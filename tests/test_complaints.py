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


async def test_create_complaint_submit(auth_client, db_session, test_user):
    resp = await auth_client.post(
        "/complaints/new",
        data={
            "category": "harassment",
            "description": "Test complaint submit",
            "action": "submit",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303

    from sqlalchemy import select
    result = await db_session.execute(select(Complaint).where(Complaint.user_id == test_user.id))
    complaint = result.scalar_one()
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
