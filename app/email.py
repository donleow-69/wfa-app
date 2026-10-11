"""Async email utility with graceful degradation."""

import logging
import os

import aiosmtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


def is_smtp_configured() -> bool:
    """Return True if the required SMTP environment variables are set."""
    return bool(
        os.getenv("SMTP_HOST") and os.getenv("SMTP_USER") and os.getenv("SMTP_PASSWORD")
    )


async def send_complaint_email(
    to_email: str,
    subject: str,
    html_body: str,
    reply_to: str = "",
) -> bool:
    """Send an email via SMTP. Returns True on success, False on failure or if not configured."""
    return await _send_email(to_email, subject, html_body, reply_to)


async def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    """Send a password-reset link. Returns True on success, False on failure or if not configured."""
    subject = "Reset your Workplace Fairness password"
    html_body = (
        f"<p>We received a request to reset your Workplace Fairness password.</p>"
        f'<p><a href="{reset_url}">Click here to reset your password</a></p>'
        f"<p>This link expires in 30 minutes. If you didn't request this, you can safely ignore this email.</p>"
    )
    return await _send_email(to_email, subject, html_body)


async def _send_email(
    to_email: str,
    subject: str,
    html_body: str,
    reply_to: str = "",
) -> bool:
    if not is_smtp_configured():
        logger.info("SMTP not configured — skipping email send.")
        return False

    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    from_addr = os.getenv("EMAIL_FROM", user)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(html_body, subtype="html")

    try:
        await aiosmtplib.send(
            msg,
            hostname=host,
            port=port,
            username=user,
            password=password,
            start_tls=True,
        )
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False
