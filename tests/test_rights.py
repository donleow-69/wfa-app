"""Tests for employee rights pages."""


async def test_rights_overview_defaults_to_us(client):
    resp = await client.get("/rights/")
    assert resp.status_code == 200


async def test_rights_overview_with_country_param(client):
    resp = await client.get("/rights/?country=sg")
    assert resp.status_code == 200
    assert b"Singapore" in resp.content


async def test_rights_overview_uses_user_country(auth_client, db_session, test_user):
    # Update user's country
    test_user.country = "sg"
    await db_session.commit()

    resp = await auth_client.get("/rights/")
    assert resp.status_code == 200
    assert b"Singapore" in resp.content


async def test_rights_detail_valid_category(client):
    resp = await client.get("/rights/discrimination")
    assert resp.status_code == 200


async def test_rights_detail_invalid_category(client):
    resp = await client.get("/rights/nonexistent")
    assert resp.status_code == 404
