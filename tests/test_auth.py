"""Tests for registration, login, and logout."""

from unittest.mock import AsyncMock, patch

from tests.conftest import _auth_cookies, create_test_user


async def test_register_page_renders(client):
    resp = await client.get("/register")
    assert resp.status_code == 200


async def test_register_success(client):
    resp = await client.post(
        "/register",
        data={
            "full_name": "New User",
            "email": "new@example.com",
            "password": "securepass1",
            "role": "employee",
            "country": "us",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "access_token" in resp.cookies


async def test_register_duplicate_email(client, db_session):
    await create_test_user(db_session, email="dup@example.com")
    resp = await client.post(
        "/register",
        data={
            "full_name": "Dup",
            "email": "dup@example.com",
            "password": "securepass1",
        },
        follow_redirects=False,
    )
    # Should render the form again with an error, not redirect
    assert resp.status_code == 200
    assert b"already exists" in resp.content


async def test_register_short_password(client):
    resp = await client.post(
        "/register",
        data={
            "full_name": "Short",
            "email": "short@example.com",
            "password": "abc",
        },
        follow_redirects=False,
    )
    # FastAPI will reject due to min_length=8 on the Form field (422)
    assert resp.status_code == 422


async def test_register_redirects_when_logged_in(auth_client):
    resp = await auth_client.get("/register", follow_redirects=False)
    assert resp.status_code == 303
    assert "/dashboard" in resp.headers["location"]


async def test_login_page_renders(client):
    resp = await client.get("/login")
    assert resp.status_code == 200


async def test_login_success(client, db_session):
    await create_test_user(db_session, email="login@example.com", password="mypassword1")
    resp = await client.post(
        "/login",
        data={"email": "login@example.com", "password": "mypassword1"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "access_token" in resp.cookies


async def test_login_cookie_persists_past_the_browser_session(client, db_session):
    """Without an explicit lifetime, browsers treat a cookie as a *session*
    cookie — discarded when the browser/app closes, regardless of how long
    the JWT inside it claims to be valid for. This is what broke "staying
    logged in after a break": the token was good for 24h, but the cookie
    carrying it wasn't told to outlive the browser session."""
    await create_test_user(db_session, email="persist@example.com", password="mypassword1")
    resp = await client.post(
        "/login",
        data={"email": "persist@example.com", "password": "mypassword1"},
        follow_redirects=False,
    )
    set_cookie = resp.headers["set-cookie"].lower()
    assert "max-age=" in set_cookie or "expires=" in set_cookie


async def test_register_cookie_persists_past_the_browser_session(client):
    resp = await client.post(
        "/register",
        data={
            "full_name": "Persist User",
            "email": "persist-register@example.com",
            "password": "securepass1",
        },
        follow_redirects=False,
    )
    set_cookie = resp.headers["set-cookie"].lower()
    assert "max-age=" in set_cookie or "expires=" in set_cookie


async def test_login_wrong_password(client, db_session):
    await create_test_user(db_session, email="wrong@example.com", password="rightpass1")
    resp = await client.post(
        "/login",
        data={"email": "wrong@example.com", "password": "wrongpass1"},
        follow_redirects=False,
    )
    assert resp.status_code == 200
    assert b"Invalid email or password" in resp.content


async def test_login_nonexistent_email(client):
    resp = await client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "whatever1"},
        follow_redirects=False,
    )
    assert resp.status_code == 200
    assert b"Invalid email or password" in resp.content


async def test_logout_clears_cookie(auth_client):
    resp = await auth_client.get("/logout", follow_redirects=False)
    assert resp.status_code == 303
    # The Set-Cookie header should delete the access_token
    set_cookie = resp.headers.get("set-cookie", "")
    assert "access_token" in set_cookie


async def test_forgot_password_page_renders(client):
    resp = await client.get("/forgot-password")
    assert resp.status_code == 200


async def test_forgot_password_known_email_sets_token_and_sends_email(client, db_session):
    user = await create_test_user(db_session, email="forgot@example.com")
    with patch("app.routers.auth_routes.send_password_reset_email", new_callable=AsyncMock) as mock_send:
        resp = await client.post("/forgot-password", data={"email": "forgot@example.com"})
    assert resp.status_code == 200
    assert b"we've sent a password reset link" in resp.content.lower() or b"sent a password reset link" in resp.content

    mock_send.assert_called_once()
    sent_email, reset_url = mock_send.call_args.args
    assert sent_email == "forgot@example.com"

    await db_session.refresh(user)
    assert user.reset_token is not None
    assert reset_url.endswith(f"/reset-password/{user.reset_token}")


async def test_forgot_password_unknown_email_gives_same_response(client):
    with patch("app.routers.auth_routes.send_password_reset_email", new_callable=AsyncMock) as mock_send:
        resp = await client.post("/forgot-password", data={"email": "nobody@example.com"})
    assert resp.status_code == 200
    assert b"sent a password reset link" in resp.content
    mock_send.assert_not_called()


async def test_reset_password_page_valid_token(client, db_session):
    user = await create_test_user(db_session, email="valid-token@example.com")
    with patch("app.routers.auth_routes.send_password_reset_email", new_callable=AsyncMock):
        await client.post("/forgot-password", data={"email": "valid-token@example.com"})
    await db_session.refresh(user)

    resp = await client.get(f"/reset-password/{user.reset_token}")
    assert resp.status_code == 200
    assert b"expired" not in resp.content


async def test_reset_password_page_invalid_token(client):
    resp = await client.get("/reset-password/not-a-real-token")
    assert resp.status_code == 200
    assert b"invalid or has expired" in resp.content


async def test_reset_password_submit_updates_password_and_clears_token(client, db_session):
    user = await create_test_user(db_session, email="reset-me@example.com", password="oldpassword1")
    with patch("app.routers.auth_routes.send_password_reset_email", new_callable=AsyncMock):
        await client.post("/forgot-password", data={"email": "reset-me@example.com"})
    await db_session.refresh(user)
    token = user.reset_token

    resp = await client.post(f"/reset-password/{token}", data={"password": "newpassword1"})
    assert resp.status_code == 200
    assert b"Your password has been reset" in resp.content

    await db_session.refresh(user)
    assert user.reset_token is None
    assert user.reset_token_expires is None

    # Old password no longer works, new one does.
    bad = await client.post(
        "/login", data={"email": "reset-me@example.com", "password": "oldpassword1"}, follow_redirects=False
    )
    assert b"Invalid email or password" in bad.content

    good = await client.post(
        "/login", data={"email": "reset-me@example.com", "password": "newpassword1"}, follow_redirects=False
    )
    assert good.status_code == 303


async def test_reset_password_submit_invalid_token(client):
    resp = await client.post("/reset-password/not-a-real-token", data={"password": "newpassword1"})
    assert resp.status_code == 200
    assert b"invalid or has expired" in resp.content
