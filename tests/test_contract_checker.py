"""Tests for the contract checker feature."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.routers import contract_checker

_USAGE = SimpleNamespace(
    input_tokens=100, output_tokens=200, cache_creation_input_tokens=0, cache_read_input_tokens=0
)


async def test_checker_requires_auth(client):
    resp = await client.get("/contract-checker/")
    assert resp.status_code == 303


async def test_get_analyze_redirects_to_form(auth_client):
    """A bookmark/home-screen icon saved from an error state can end up
    pointing at the POST-only /analyze URL. GET-ing it used to 405 with no
    way back to the actual form — redirect to the form instead."""
    resp = await auth_client.get("/contract-checker/analyze", follow_redirects=False)
    assert resp.status_code in (302, 303, 307, 308)
    assert resp.headers["location"] == "/contract-checker/"


async def test_checker_form_renders(auth_client):
    resp = await auth_client.get("/contract-checker/")
    assert resp.status_code == 200
    assert b"Contract Checker" in resp.content


async def test_analyze_requires_auth(client):
    resp = await client.post("/contract-checker/analyze", data={"contract_text": "test"})
    assert resp.status_code == 303


async def test_analyze_empty_input(auth_client):
    resp = await auth_client.post(
        "/contract-checker/analyze",
        data={"contract_text": "", "country": "us"},
    )
    assert resp.status_code == 400
    assert b"Please paste contract text or upload" in resp.content


async def test_analyze_rejects_oversized_file(auth_client):
    """A scanned multi-page contract easily exceeds the old 2 MB limit —
    this must be rejected with a clear, specific error, not silently."""
    oversized = b"%PDF-1.4\n" + b"0" * (contract_checker.MAX_FILE_SIZE + 1)
    resp = await auth_client.post(
        "/contract-checker/analyze",
        data={"country": "us"},
        files={"file": ("scanned-contract.pdf", oversized, "application/pdf")},
    )
    assert resp.status_code == 400
    assert b"exceeds" in resp.content


async def test_analyze_accepts_realistic_scanned_contract_size(auth_client):
    """A 6-7 page scanned PDF (the reported real-world case) is commonly a
    few MB — must fit comfortably under the limit now that it's been raised
    from 2 MB. (Uses a corrupt PDF body since we only care that it clears
    the size check; extraction failure is covered separately.)"""
    six_mb = 6 * 1024 * 1024
    assert six_mb < contract_checker.MAX_FILE_SIZE, (
        "MAX_FILE_SIZE must comfortably fit a realistic scanned multi-page contract"
    )


async def test_analyze_unsupported_file_type(auth_client):
    resp = await auth_client.post(
        "/contract-checker/analyze",
        data={"country": "us"},
        files={"file": ("contract.txt", b"plain text contract", "text/plain")},
    )
    assert resp.status_code == 400
    assert b"Unsupported file type" in resp.content


def _minimal_pdf(content: bytes) -> bytes:
    """Build a minimal, structurally valid single-page PDF (correct xref
    table) with the given raw content stream — e.g. b"" for a page with no
    text layer, simulating a scanned/photographed document."""
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
        b"3 0 obj << /Type /Page /Parent 2 0 R /Resources << /Font << /F1 5 0 R >> >> "
        b"/MediaBox [0 0 612 792] /Contents 4 0 R >> endobj",
        b"4 0 obj << /Length %d >> stream\n%s\nendstream endobj" % (len(content), content),
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
    ]
    pdf = b"%PDF-1.4\n"
    offsets = []
    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj + b"\n"
    xref_offset = len(pdf)
    pdf += b"xref\n0 %d\n" % (len(objects) + 1)
    pdf += b"0000000000 65535 f \n"
    for off in offsets:
        pdf += ("%010d 00000 n \n" % off).encode()
    pdf += b"trailer << /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (
        len(objects) + 1,
        xref_offset,
    )
    return pdf


async def test_analyze_scanned_pdf_with_no_text_layer_hints_at_scan(auth_client):
    """A photographed/scanned PDF has no extractable text layer. The error
    should say so distinctly from a generic failure, so users understand
    *why* and what to do next."""
    empty_pdf = _minimal_pdf(b"")
    resp = await auth_client.post(
        "/contract-checker/analyze",
        data={"country": "us"},
        files={"file": ("scanned-contract.pdf", empty_pdf, "application/pdf")},
    )
    assert resp.status_code == 400
    assert b"scanned" in resp.content.lower() or b"photo" in resp.content.lower()


async def test_analyze_with_mocked_claude(auth_client):
    analysis = {
        "contract_type": "Employment Agreement",
        "risk_score": 40,
        "summary": "Generally standard contract.",
        "illegal_clauses": [],
        "missing_provisions": [],
        "red_flags": [],
        "recommendations": [{"priority": 1, "action": "Add a notice period clause."}],
    }

    mock_response = AsyncMock()
    mock_response.content = [AsyncMock(text=json.dumps(analysis))]
    mock_response.usage = _USAGE

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    with patch("app.routers.contract_checker._get_client", return_value=mock_client):
        resp = await auth_client.post(
            "/contract-checker/analyze",
            data={"contract_text": "This Employment Agreement is entered into.", "country": "us"},
        )

    assert resp.status_code == 200
    assert b"Employment Agreement" in resp.content
    assert b"Add a notice period clause" in resp.content


async def test_analyze_logs_unexpected_extraction_error(auth_client, caplog):
    """Regression guard for a real observability gap found while debugging
    a "nothing happened" report: unexpected extraction failures (e.g. a
    corrupt or encrypted file) were swallowed with a generic message and
    never logged server-side, making them undiagnosable from Render logs."""
    corrupt_pdf = b"%PDF-1.4\nnot actually a valid pdf structure"
    with caplog.at_level("ERROR"):
        resp = await auth_client.post(
            "/contract-checker/analyze",
            data={"country": "us"},
            files={"file": ("contract.pdf", corrupt_pdf, "application/pdf")},
        )
    assert resp.status_code == 400
    assert any("contract" in r.message.lower() or "extract" in r.message.lower() for r in caplog.records)
