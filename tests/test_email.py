"""Tests for async email utility."""

from unittest.mock import AsyncMock, patch

import pytest

from app.email import is_smtp_configured, send_complaint_email


class TestIsSmtpConfigured:
    def test_not_configured_when_env_empty(self):
        with patch.dict("os.environ", {}, clear=True):
            assert is_smtp_configured() is False

    def test_not_configured_when_partial(self):
        with patch.dict("os.environ", {"SMTP_HOST": "mail.example.com"}, clear=True):
            assert is_smtp_configured() is False

    def test_configured_when_all_set(self):
        env = {
            "SMTP_HOST": "mail.example.com",
            "SMTP_USER": "user@example.com",
            "SMTP_PASSWORD": "secret",
        }
        with patch.dict("os.environ", env, clear=True):
            assert is_smtp_configured() is True


class TestSendComplaintEmail:
    @pytest.mark.asyncio
    async def test_skips_when_not_configured(self):
        with patch.dict("os.environ", {}, clear=True):
            result = await send_complaint_email(
                to_email="test@example.com",
                subject="Test",
                html_body="<p>Hello</p>",
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_send_success(self):
        env = {
            "SMTP_HOST": "mail.example.com",
            "SMTP_USER": "user@example.com",
            "SMTP_PASSWORD": "secret",
        }
        with patch.dict("os.environ", env, clear=True):
            with patch("app.email.aiosmtplib.send", new_callable=AsyncMock) as mock_send:
                result = await send_complaint_email(
                    to_email="authority@gov.example",
                    subject="Complaint",
                    html_body="<p>Details</p>",
                    reply_to="user@example.com",
                )
                assert result is True
                mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_failure(self):
        env = {
            "SMTP_HOST": "mail.example.com",
            "SMTP_USER": "user@example.com",
            "SMTP_PASSWORD": "secret",
        }
        with patch.dict("os.environ", env, clear=True):
            with patch(
                "app.email.aiosmtplib.send",
                new_callable=AsyncMock,
                side_effect=ConnectionError("SMTP down"),
            ):
                result = await send_complaint_email(
                    to_email="authority@gov.example",
                    subject="Complaint",
                    html_body="<p>Details</p>",
                )
                assert result is False
