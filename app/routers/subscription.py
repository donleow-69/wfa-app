"""Stripe subscription routes."""

import os

import stripe
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user, get_optional_user
from ..database import get_db
from ..models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


@router.get("/subscribe", response_class=HTMLResponse)
async def subscribe_page(
    request: Request,
    next: str | None = None,
    user: User | None = Depends(get_optional_user),
):
    if user and user.is_subscribed:
        return RedirectResponse(next or "/dashboard", status_code=303)
    return templates.TemplateResponse(
        "subscribe.html",
        {"request": request, "user": user, "next_url": next or "/policies"},
    )


@router.post("/subscribe/checkout")
async def create_checkout_session(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not stripe.api_key or not STRIPE_PRICE_ID:
        return RedirectResponse("/subscribe?error=stripe_not_configured", status_code=303)

    # Create or reuse Stripe customer
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name,
            metadata={"user_id": str(user.id)},
        )
        user.stripe_customer_id = customer.id
        await db.commit()
    else:
        customer_id = user.stripe_customer_id

    base_url = str(request.base_url).rstrip("/")
    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
        mode="subscription",
        success_url=f"{base_url}/subscribe/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{base_url}/subscribe?cancelled=1",
    )

    return RedirectResponse(session.url, status_code=303)


@router.get("/subscribe/success", response_class=HTMLResponse)
async def subscribe_success(
    request: Request,
    session_id: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if session_id and stripe.api_key:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                user.is_subscribed = True
                if not user.stripe_customer_id:
                    user.stripe_customer_id = session.customer
                await db.commit()
        except stripe.StripeError:
            pass

    return templates.TemplateResponse(
        "subscribe_success.html",
        {"request": request, "user": user},
    )


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not STRIPE_WEBHOOK_SECRET:
        return {"status": "webhook_secret_not_configured"}

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.SignatureVerificationError):
        return {"status": "invalid_signature"}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        if customer_id:
            from sqlalchemy import select

            result = await db.execute(
                select(User).where(User.stripe_customer_id == customer_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.is_subscribed = True
                await db.commit()

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        if customer_id:
            from sqlalchemy import select

            result = await db.execute(
                select(User).where(User.stripe_customer_id == customer_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.is_subscribed = False
                await db.commit()

    return {"status": "ok"}
