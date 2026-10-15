from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger("smart-farming.email")


def _get_from_email() -> str:
    """Resolve sender email address, defaulting to configured EMAILS_FROM_EMAIL or standard sender."""
    if settings.EMAILS_FROM_EMAIL and settings.EMAILS_FROM_EMAIL.strip():
        return settings.EMAILS_FROM_EMAIL.strip()
    return "mgkuvadiya28@gmail.com"


def _create_smtp_connection(timeout: int = 15) -> smtplib.SMTP | smtplib.SMTP_SSL | None:
    """Optional legacy SMTP fallback connection if explicit host credentials exist."""
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        return None
    use_ssl = getattr(settings, "SMTP_SSL", False) or settings.SMTP_PORT == 465
    if use_ssl:
        server: smtplib.SMTP | smtplib.SMTP_SSL = smtplib.SMTP_SSL(
            settings.SMTP_HOST, settings.SMTP_PORT, timeout=timeout
        )
    else:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=timeout)
        if getattr(settings, "SMTP_TLS", True):
            server.ehlo()
            server.starttls()
            server.ehlo()

    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

    return server


async def send_reset_password_email(email_to: str, token: str | None = None) -> bool:
    """
    Dispatches a password reset recovery email via Supabase Custom SMTP.
    Falls back to direct SMTP if configured, or logs to console during offline local development.
    """
    email_to = email_to.strip().lower()
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    reset_url = f"{frontend_url}/auth/reset-password" + (f"?token={token}" if token else "")

    supabase_url = getattr(settings, "SUPABASE_URL", "")
    anon_key = getattr(settings, "SUPABASE_ANON_KEY", "")
    service_key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")

    # 1. Primary Delivery: Supabase Auth Recovery API (uses Custom SMTP configured in Supabase)
    if supabase_url and (service_key or anon_key):
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(
                    f"{supabase_url.rstrip('/')}/auth/v1/recover",
                    headers={
                        "apikey": anon_key or service_key,
                        "Authorization": f"Bearer {service_key or anon_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "email": email_to,
                        "redirect_to": f"{frontend_url}/auth/reset-password",
                    },
                )
                if resp.status_code in (200, 201, 204):
                    logger.info("Password reset email successfully dispatched to %s via Supabase Custom SMTP", email_to)
                    return True
                else:
                    logger.warning("Supabase /auth/v1/recover returned status %s: %s", resp.status_code, resp.text)
        except Exception as exc:
            logger.warning("Supabase Auth recover request failed for %s: %s", email_to, exc)

    # 2. Secondary fallback: direct SMTP if credentials provided
    smtp_server = None
    try:
        smtp_server = _create_smtp_connection(timeout=10)
    except Exception as exc:
        logger.debug("Local SMTP connection not available: %s", exc)

    if smtp_server:
        try:
            from_email = _get_from_email()
            from_header = f"{settings.EMAILS_FROM_NAME} <{from_email}>"
            msg = MIMEMultipart("alternative")
            msg["From"] = from_header
            msg["To"] = email_to
            msg["Subject"] = "Reset Your Smart Farming Password"

            text_content = f"Hello,\n\nWe received a request to reset your password. Click to reset:\n{reset_url}\n"
            msg.attach(MIMEText(text_content, "plain"))
            smtp_server.sendmail(from_email, [email_to], msg.as_string())
            smtp_server.quit()
            logger.info("Password reset email sent to %s via direct SMTP fallback", email_to)
            return True
        except Exception as exc:
            logger.error("Failed sending email via direct SMTP fallback: %s", exc)

    # 3. Development / offline console logging
    logger.info(
        "\n" + "=" * 65 + "\n"
        "[EMAIL SERVICE - DEV FALLBACK]\n"
        f"To: {email_to}\n"
        f"Subject: Reset Your Smart Farming Password\n"
        f"Reset Link: {reset_url}\n"
        f"Token: {token or '[Supabase Recovery Link]'}\n"
        "(Supabase Custom SMTP or dev link logged to console)\n"
        + "=" * 65 + "\n"
    )
    return True


async def send_verification_email(
    email_to: str,
    token: str,
    token_type: str = "registration",
    user_name: str | None = None,
    user_id: str | None = None,
) -> bool:
    """
    Dispatches an email verification link via Supabase Auth Custom SMTP.
    Falls back to direct SMTP if configured, or logs link to console during local development.
    """
    email_to = email_to.strip().lower()
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    verify_url = f"{frontend_url}/auth/verify-email?token={token}"

    supabase_url = getattr(settings, "SUPABASE_URL", "")
    service_key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
    anon_key = getattr(settings, "SUPABASE_ANON_KEY", "")

    # 1. Primary Delivery: Supabase Auth APIs (triggers email through Supabase's Custom SMTP)
    if supabase_url and (service_key or anon_key):
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                clean_redirect = f"{frontend_url}/auth/verify-email"

                # A. Initial Registration: Trigger Supabase Auth signup to dispatch the "Confirm signup" template
                if token_type == "registration":
                    import secrets
                    signup_resp = await client.post(
                        f"{supabase_url.rstrip('/')}/auth/v1/signup?redirect_to={clean_redirect}",
                        headers={
                            "apikey": anon_key or service_key,
                            "Content-Type": "application/json",
                        },
                        json={
                            "email": email_to,
                            "password": secrets.token_urlsafe(16),
                            "options": {
                                "data": {"name": user_name or ""},
                                "email_redirect_to": clean_redirect,
                            },
                        },
                    )
                    if signup_resp.status_code in (200, 201):
                        logger.info("Confirm signup email dispatched to %s via Supabase Auth signup", email_to)
                        return True
                    else:
                        logger.info("Supabase signup returned status %s (%s), attempting resend fallback", signup_resp.status_code, signup_resp.text)

                # B. Email Update for existing user
                if token_type == "email_update" and user_id and service_key:
                    try:
                        link_resp = await client.post(
                            f"{supabase_url.rstrip('/')}/auth/v1/admin/generate_link",
                            headers={
                                "apikey": service_key,
                                "Authorization": f"Bearer {service_key}",
                                "Content-Type": "application/json",
                            },
                            json={
                                "type": "email_change_new",
                                "email": email_to,
                                "new_email": email_to,
                            },
                        )
                        if link_resp.status_code == 200:
                            logger.info("Generated email_change link for %s", email_to)
                    except Exception as gen_err:
                        logger.debug("generate_link note: %s", gen_err)

                # C. Resend confirmation email
                resend_type = "email_change" if token_type == "email_update" else "signup"
                resp = await client.post(
                    f"{supabase_url.rstrip('/')}/auth/v1/resend?redirect_to={clean_redirect}",
                    headers={
                        "apikey": anon_key or service_key,
                        "Authorization": f"Bearer {service_key or anon_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "type": resend_type,
                        "email": email_to,
                        "options": {
                            "email_redirect_to": clean_redirect,
                        },
                    },
                )
                if resp.status_code in (200, 201, 204):
                    logger.info("Verification email dispatched to %s via Supabase Custom SMTP (type: %s)", email_to, resend_type)
                    return True
                else:
                    logger.warning("Supabase /auth/v1/resend returned %s: %s", resp.status_code, resp.text)
        except Exception as exc:
            logger.warning("Supabase Auth email dispatch failed for %s: %s", email_to, exc)

    # 2. Secondary fallback: direct SMTP
    smtp_server = None
    try:
        smtp_server = _create_smtp_connection(timeout=10)
    except Exception as exc:
        logger.debug("Local SMTP connection not available: %s", exc)

    if smtp_server:
        try:
            from_email = _get_from_email()
            from_header = f"{settings.EMAILS_FROM_NAME} <{from_email}>"
            is_update = token_type == "email_update"
            subject = (
                "Verify Your Updated Email Address - Smart Farming"
                if is_update
                else "Verify Your Smart Farming Account"
            )
            msg = MIMEMultipart("alternative")
            msg["From"] = from_header
            msg["To"] = email_to
            msg["Subject"] = subject
            body = f"Hello,\n\nPlease verify your email by clicking the link below:\n{verify_url}\n"
            msg.attach(MIMEText(body, "plain"))
            smtp_server.sendmail(from_email, [email_to], msg.as_string())
            smtp_server.quit()
            logger.info("Verification email sent to %s via direct SMTP fallback", email_to)
            return True
        except Exception as exc:
            logger.error("Failed sending email via direct SMTP fallback: %s", exc)

    # 3. Development / offline console logging
    logger.info(
        "\n" + "=" * 65 + "\n"
        f"[EMAIL SERVICE - DEV FALLBACK: {token_type.upper()}]\n"
        f"To: {email_to}\n"
        f"Verification Link: {verify_url}\n"
        f"Token: {token}\n"
        "(Supabase Custom SMTP or link logged to console)\n"
        + "=" * 65 + "\n"
    )
    return True


async def send_test_email(email_to: str) -> tuple[bool, str]:
    """
    Diagnostic helper to test email delivery via Supabase Auth custom SMTP or direct SMTP.
    """
    supabase_url = getattr(settings, "SUPABASE_URL", "")
    anon_key = getattr(settings, "SUPABASE_ANON_KEY", "")
    service_key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")

    if supabase_url and (service_key or anon_key):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{supabase_url.rstrip('/')}/auth/v1/recover",
                    headers={
                        "apikey": anon_key or service_key,
                        "Authorization": f"Bearer {service_key or anon_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "email": email_to,
                        "redirect_to": f"{settings.FRONTEND_URL.rstrip('/')}/auth/reset-password",
                    },
                )
                if resp.status_code in (200, 201, 204):
                    return (True, f"Test email successfully dispatched to {email_to} via Supabase Custom SMTP ({supabase_url})")
                else:
                    return (False, f"Supabase email dispatch returned HTTP {resp.status_code}: {resp.text}")
        except Exception as exc:
            return (False, f"Supabase Auth error: {exc}")

    # Fallback to direct SMTP if configured
    smtp_server = None
    try:
        smtp_server = _create_smtp_connection(timeout=10)
    except Exception as exc:
        return (False, f"No Supabase or SMTP connection available: {exc}")

    if smtp_server:
        try:
            from_email = _get_from_email()
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{settings.EMAILS_FROM_NAME} <{from_email}>"
            msg["To"] = email_to
            msg["Subject"] = "🌱 Smart Farming - SMTP Connection Test"
            msg.attach(MIMEText(f"Test email to {email_to}", "plain"))
            smtp_server.sendmail(from_email, [email_to], msg.as_string())
            smtp_server.quit()
            return (True, f"Test email sent via direct SMTP to {email_to}")
        except Exception as exc:
            return (False, f"SMTP Error: {exc}")

    return (False, "Neither Supabase Auth URL nor SMTP host credentials are configured.")
