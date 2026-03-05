"""Tests for compliance checklist routes."""

from app.models.compliance import ComplianceChecklist, ComplianceItem
from tests.conftest import create_test_user


async def test_compliance_requires_auth(client):
    resp = await client.get("/compliance/")
    assert resp.status_code == 401


async def test_create_checklist_with_defaults(auth_client, db_session, test_user):
    resp = await auth_client.post(
        "/compliance/create",
        data={"company_name": "Test Corp"},
        follow_redirects=False,
    )
    assert resp.status_code == 303

    from sqlalchemy import select
    result = await db_session.execute(
        select(ComplianceChecklist).where(ComplianceChecklist.user_id == test_user.id)
    )
    checklist = result.scalar_one()
    assert checklist.company_name == "Test Corp"

    items_result = await db_session.execute(
        select(ComplianceItem).where(ComplianceItem.checklist_id == checklist.id)
    )
    items = items_result.scalars().all()
    # US default items should be seeded
    assert len(items) > 0


async def test_view_checklist(auth_client, db_session, test_user):
    checklist = ComplianceChecklist(user_id=test_user.id, company_name="View Corp")
    db_session.add(checklist)
    await db_session.commit()
    await db_session.refresh(checklist)

    item = ComplianceItem(
        checklist_id=checklist.id,
        requirement="Test requirement",
        description="Test desc",
        category="Policies",
    )
    db_session.add(item)
    await db_session.commit()

    resp = await auth_client.get(f"/compliance/{checklist.id}")
    assert resp.status_code == 200


async def test_toggle_item(auth_client, db_session, test_user):
    checklist = ComplianceChecklist(user_id=test_user.id, company_name="Toggle Corp")
    db_session.add(checklist)
    await db_session.commit()
    await db_session.refresh(checklist)

    item = ComplianceItem(
        checklist_id=checklist.id,
        requirement="Toggle me",
        description="Toggleable item",
        category="Safety",
        completed=False,
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)

    resp = await auth_client.post(
        f"/compliance/{checklist.id}/toggle/{item.id}",
        follow_redirects=False,
    )
    assert resp.status_code == 303

    await db_session.refresh(item)
    assert item.completed is True


async def test_cannot_access_other_users_checklist(auth_client, db_session):
    other = await create_test_user(db_session, email="other@example.com")
    checklist = ComplianceChecklist(user_id=other.id, company_name="Other Corp")
    db_session.add(checklist)
    await db_session.commit()
    await db_session.refresh(checklist)

    # Should redirect because checklist belongs to another user
    resp = await auth_client.get(f"/compliance/{checklist.id}", follow_redirects=False)
    assert resp.status_code == 303
