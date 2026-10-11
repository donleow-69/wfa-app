"""Registration and login routes."""

from datetime import timedelta

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import (
    RESET_TOKEN_EXPIRE_MINUTES,
    TOKEN_EXPIRE_MINUTES,
    create_token,
    generate_reset_token,
    get_optional_user,
    hash_password,
    utcnow_naive,
    verify_password,
)
from ..database import get_db
from ..email import send_password_reset_email
from ..limiter import limiter
from ..models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse(request, "register.html", {})


@router.post("/register")
async def register(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(..., min_length=8),
    role: str = Form("employee"),
    country: str = Form("us"),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        return templates.TemplateResponse(
            request,
            "register.html",
            {"error": "An account with that email already exists."},
        )

    valid_countries = {"us", "sg", "my", "id", "ph", "th", "gb", "hk"}
    if country not in valid_countries:
        country = "us"

    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hash_password(password),
        role=role,
        country=country,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(
        "access_token",
        create_token(user.id, user.email),
        httponly=True,
        max_age=TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse(request, "login.html", {})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid email or password."},
        )

    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(
        "access_token",
        create_token(user.id, user.email),
        httponly=True,
        max_age=TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(request, "forgot_password.html", {})


@router.post("/forgot-password", response_class=HTMLResponse)
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    email: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        user.reset_token = generate_reset_token()
        user.reset_token_expires = utcnow_naive() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
        await db.commit()

        reset_url = f"{str(request.base_url).rstrip('/')}/reset-password/{user.reset_token}"
        await send_password_reset_email(user.email, reset_url)

    # Same message regardless of whether the email exists, so this can't be used to enumerate accounts.
    return templates.TemplateResponse(
        request,
        "forgot_password.html",
        {"sent": True},
    )


@router.get("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalar_one_or_none()

    if not user or not user.reset_token_expires or user.reset_token_expires < utcnow_naive():
        return templates.TemplateResponse(request, "reset_password.html", {"invalid": True})

    return templates.TemplateResponse(request, "reset_password.html", {"token": token})


@router.post("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password(
    request: Request,
    token: str,
    password: str = Form(..., min_length=8),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalar_one_or_none()

    if not user or not user.reset_token_expires or user.reset_token_expires < utcnow_naive():
        return templates.TemplateResponse(request, "reset_password.html", {"invalid": True})

    user.hashed_password = hash_password(password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()

    return templates.TemplateResponse(request, "login.html", {"reset_success": True})
