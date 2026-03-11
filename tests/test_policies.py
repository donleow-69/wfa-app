"""Tests for policy drafting routes."""


async def test_policies_list_requires_auth(client):
    resp = await client.get("/policies/")
    assert resp.status_code == 303


async def test_policies_list_renders(auth_client):
    resp = await auth_client.get("/policies/")
    assert resp.status_code == 200


async def test_policy_form_requires_subscription(auth_client):
    resp = await auth_client.get("/policies/anti_discrimination", follow_redirects=False)
    assert resp.status_code == 303
    assert "/subscribe" in resp.headers["location"]


async def test_generate_policy_subscribed(subscribed_client):
    resp = await subscribed_client.post(
        "/policies/anti_discrimination/generate",
        data={
            "company_name": "Test Corp",
            "effective_date": "2025-01-01",
            "contact_person": "HR Manager",
            "hr_contact": "hr@test.com",
            "country": "us",
        },
    )
    assert resp.status_code == 200
    assert b"Test Corp" in resp.content


async def test_custom_policy_requires_subscription(auth_client):
    resp = await auth_client.get("/policies/custom", follow_redirects=False)
    assert resp.status_code == 303
    assert "/subscribe" in resp.headers["location"]
