"""Tests for subscription and Stripe webhook routes."""


async def test_subscribe_page_renders(client):
    resp = await client.get("/subscribe")
    assert resp.status_code == 200


async def test_subscribe_redirects_if_subscribed(subscribed_client):
    resp = await subscribed_client.get("/subscribe", follow_redirects=False)
    assert resp.status_code == 303


async def test_checkout_requires_auth(client):
    resp = await client.post("/subscribe/checkout")
    assert resp.status_code == 401


async def test_checkout_no_stripe_key(auth_client):
    """With empty STRIPE_SECRET_KEY, checkout should redirect with error."""
    resp = await auth_client.post("/subscribe/checkout", follow_redirects=False)
    assert resp.status_code == 303
    assert "error" in resp.headers["location"]


async def test_webhook_invalid_signature(client):
    resp = await client.post(
        "/webhook/stripe",
        content=b'{"type": "checkout.session.completed"}',
        headers={
            "content-type": "application/json",
            "stripe-signature": "bad_sig",
        },
    )
    data = resp.json()
    # With no webhook secret configured, it returns webhook_secret_not_configured
    # With a secret configured but bad sig, it returns invalid_signature
    assert data["status"] in ("invalid_signature", "webhook_secret_not_configured")
