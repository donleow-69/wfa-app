"""Tests for the home and dashboard routes."""


async def test_home_page_anonymous(client):
    resp = await client.get("/")
    assert resp.status_code == 200


async def test_home_page_authenticated(auth_client):
    resp = await auth_client.get("/")
    assert resp.status_code == 200


async def test_dashboard_redirects_anonymous(client):
    resp = await client.get("/dashboard", follow_redirects=False)
    assert resp.status_code == 303
    assert "/login" in resp.headers["location"]


async def test_dashboard_authenticated(auth_client):
    resp = await auth_client.get("/dashboard")
    assert resp.status_code == 200
