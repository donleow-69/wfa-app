"""Tests for registration, login, and logout."""

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
