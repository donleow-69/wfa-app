"""Tests for the policy compliance checker feature."""

import json
from unittest.mock import AsyncMock, patch

import pytest


async def test_checker_requires_auth(client):
    resp = await client.get("/policy-checker/")
    assert resp.status_code == 401


async def test_checker_requires_subscription(auth_client):
    resp = await auth_client.get("/policy-checker/", follow_redirects=False)
    assert resp.status_code == 303
    assert "/subscribe" in resp.headers["location"]


async def test_checker_form_renders_for_subscriber(subscribed_client):
    resp = await subscribed_client.get("/policy-checker/")
    assert resp.status_code == 200
    assert b"Policy Compliance Checker" in resp.content
    assert b"Analyze Policy" in resp.content


async def test_analyze_requires_auth(client):
    resp = await client.post("/policy-checker/analyze", data={"policy_text": "test"})
    assert resp.status_code == 401


async def test_analyze_requires_subscription(auth_client):
    resp = await auth_client.post(
        "/policy-checker/analyze",
        data={"policy_text": "test", "country": "us"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/subscribe" in resp.headers["location"]


async def test_analyze_empty_input(subscribed_client):
    resp = await subscribed_client.post(
        "/policy-checker/analyze",
        data={"policy_text": "", "country": "us"},
    )
    assert resp.status_code == 400
    assert b"Please paste policy text or upload" in resp.content


async def test_analyze_with_mocked_claude(subscribed_client):
    """Full analysis with a mocked Claude response."""
    analysis = {
        "policy_type": "Anti-Discrimination Policy",
        "overall_score": 72,
        "covered": [
            {
                "requirement": "Anti-discrimination policy posted and distributed",
                "category": "Policies",
                "assessment": "Policy covers all protected classes.",
            }
        ],
        "gaps": [
            {
                "requirement": "Anti-retaliation policy in place",
                "category": "Policies",
                "severity": "high",
                "explanation": "No retaliation protections mentioned.",
            }
        ],
        "recommendations": [
            {
                "priority": 1,
                "action": "Add anti-retaliation provisions",
                "rationale": "Required by federal law.",
            }
        ],
        "summary": "Policy covers basic discrimination protections but lacks retaliation provisions.",
    }

    mock_response = AsyncMock()
    mock_response.content = [AsyncMock(text=json.dumps(analysis))]

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    with patch("app.routers.policy_checker._get_client", return_value=mock_client):
        resp = await subscribed_client.post(
            "/policy-checker/analyze",
            data={
                "policy_text": "Our company prohibits discrimination based on race, color, religion, sex, and national origin.",
                "country": "us",
            },
        )

    assert resp.status_code == 200
    assert b"Anti-Discrimination Policy" in resp.content
    assert b"72" in resp.content
    assert b"Anti-retaliation policy in place" in resp.content
    assert b"Add anti-retaliation provisions" in resp.content


async def test_analyze_handles_markdown_fenced_json(subscribed_client):
    """Claude sometimes wraps JSON in markdown fences."""
    analysis = {
        "policy_type": "Safety Policy",
        "overall_score": 55,
        "covered": [],
        "gaps": [],
        "recommendations": [],
        "summary": "Basic safety policy.",
    }

    fenced = f"```json\n{json.dumps(analysis)}\n```"

    mock_response = AsyncMock()
    mock_response.content = [AsyncMock(text=fenced)]

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    with patch("app.routers.policy_checker._get_client", return_value=mock_client):
        resp = await subscribed_client.post(
            "/policy-checker/analyze",
            data={"policy_text": "Safety first at our company.", "country": "us"},
        )

    assert resp.status_code == 200
    assert b"Safety Policy" in resp.content
    assert b"55" in resp.content
