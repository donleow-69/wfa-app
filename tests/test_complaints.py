"""Tests for complaint filing routes."""

from app.models.complaint import Complaint
from tests.conftest import create_test_user


async def test_complaints_list_requires_auth(client):
    resp = await client.get("/complaints/")
    assert resp.status_code == 401


async def test_complaints_list_empty(auth_client):
    resp = await auth_client.get("/complaints/")
    assert resp.status_code == 200


async def test_create_complaint_draft(auth_client, db_session, test_user):
    resp = await auth_client.post(
        "/complaints/new",
        data={
            "category": "discrimination",
            "description": "Test complaint draft",
            "employer_name": "Acme Corp",
            "incident_date": "2025-01-01",
            "desired_outcome": "Investigate",
            "supporting_details": "Details here",
            "action": "save",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303

    from sqlalchemy import select
    result = await db_session.execute(select(Complaint).where(Complaint.user_id == test_user.id))
    complaint = result.scalar_one()
    assert complaint.status == "draft"
    assert complaint.category == "discrimination"


async def test_create_complaint_review(auth_client, db_session, test_user):
    """action=review saves as draft and redirects to preview."""
    resp = await auth_client.post(
        "/complaints/new",
        data={
            "category": "harassment",
            "description": "Test complaint review",
            "action": "review",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/preview" in resp.headers["location"]

    from sqlalchemy import select
    result = await db_session.execute(select(Complaint).where(Complaint.user_id == test_user.id))
    complaint = result.scalar_one()
    assert complaint.status == "draft"


async def test_preview_shows_authority(auth_client, db_session, test_user):
    """Preview page shows authority info for user's country."""
    complaint = Complaint(
        user_id=test_user.id,
        category="discrimination",
        description="Discrimination complaint",
        status="draft",
    )
    db_session.add(complaint)
    await db_session.commit()
    await db_session.refresh(complaint)

    resp = await auth_client.get(f"/complaints/{complaint.id}/preview")
    assert resp.status_code == 200
    assert "EEOC" in resp.text
    assert "Confirm" in resp.text


async def test_preview_non_draft_redirects(auth_client, db_session, test_user):
    """Preview should redirect if complaint is already submitted."""
    complaint = Complaint(
        user_id=test_user.id,
        category="safety",
        description="Safety issue",
        status="submitted",
    )
    db_session.add(complaint)
    await db_session.commit()
    await db_session.refresh(complaint)

    resp = await auth_client.get(f"/complaints/{complaint.id}/preview", follow_redirects=False)
    assert resp.status_code == 303


async def test_submit_sets_authority_fields(auth_client, db_session, test_user):
    """POST submit sets authority fields and changes status to submitted."""
    complaint = Complaint(
        user_id=test_user.id,
        category="discrimination",
        description="Discrimination complaint",
        status="draft",
    )
    db_session.add(complaint)
    await db_session.commit()
    await db_session.refresh(complaint)

    resp = await auth_client.post(
        f"/complaints/{complaint.id}/submit", follow_redirects=False
    )
    assert resp.status_code == 303

    await db_session.refresh(complaint)
    assert complaint.status == "submitted"
    assert "EEOC" in complaint.authority_name
    assert complaint.authority_email == "info@eeoc.gov"
    assert complaint.authority_portal_url != ""


async def test_submit_already_submitted_redirects(auth_client, db_session, test_user):
    """Submit should redirect if complaint is already submitted."""
    complaint = Complaint(
        user_id=test_user.id,
        category="wage_theft",
        description="Unpaid wages",
        status="submitted",
    )
    db_session.add(complaint)
    await db_session.commit()
    await db_session.refresh(complaint)

    resp = await auth_client.post(
        f"/complaints/{complaint.id}/submit", follow_redirects=False
    )
    assert resp.status_code == 303

    await db_session.refresh(complaint)
    # Status should still be submitted, not changed again
    assert complaint.status == "submitted"


async def test_view_own_complaint(auth_client, db_session, test_user):
    complaint = Complaint(
        user_id=test_user.id,
        category="wage_theft",
        description="Unpaid overtime",
        status="draft",
    )
    db_session.add(complaint)
    await db_session.commit()
    await db_session.refresh(complaint)

    resp = await auth_client.get(f"/complaints/{complaint.id}")
    assert resp.status_code == 200


async def test_view_other_users_complaint(auth_client, db_session):
    other = await create_test_user(db_session, email="other@example.com")
    complaint = Complaint(
        user_id=other.id,
        category="safety",
        description="Unsafe conditions",
        status="draft",
    )
    db_session.add(complaint)
    await db_session.commit()
    await db_session.refresh(complaint)

    # Should redirect because the complaint doesn't belong to test_user
    resp = await auth_client.get(f"/complaints/{complaint.id}", follow_redirects=False)
    assert resp.status_code == 303


async def test_edit_draft_complaint(auth_client, db_session, test_user):
    complaint = Complaint(
        user_id=test_user.id,
        category="leave",
        description="Original",
        status="draft",
    )
    db_session.add(complaint)
    await db_session.commit()
    await db_session.refresh(complaint)

    resp = await auth_client.post(
        f"/complaints/{complaint.id}/edit",
        data={
            "category": "leave",
            "description": "Updated description",
            "action": "save",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303

    await db_session.refresh(complaint)
    assert complaint.description == "Updated description"


async def test_edit_submitted_complaint_rejected(auth_client, db_session, test_user):
    complaint = Complaint(
        user_id=test_user.id,
        category="retaliation",
        description="Original",
        status="submitted",
    )
    db_session.add(complaint)
    await db_session.commit()
    await db_session.refresh(complaint)

    resp = await auth_client.post(
        f"/complaints/{complaint.id}/edit",
        data={
            "category": "retaliation",
            "description": "Should not change",
            "action": "save",
        },
        follow_redirects=False,
    )
    # Redirects without changing because status != draft
    assert resp.status_code == 303

    await db_session.refresh(complaint)
    assert complaint.description == "Original"
