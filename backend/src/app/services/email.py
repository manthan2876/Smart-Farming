from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger("smart-farming.email")


def _get_from_email() -> str:
    """Resolve the sender email address from settings, falling back to SMTP_USER."""
    if settings.EMAILS_FROM_EMAIL and settings.EMAILS_FROM_EMAIL.strip():
        return settings.EMAILS_FROM_EMAIL.strip()
    if settings.SMTP_USER and "@" in settings.SMTP_USER:
        return settings.SMTP_USER.strip()
    return "noreply@smartfarming.com"


def _create_smtp_connection(timeout: int = 15) -> smtplib.SMTP | smtplib.SMTP_SSL:
    """Create and authenticate an SMTP or SMTP_SSL connection based on settings."""
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


def send_reset_password_email(email_to: str, token: str) -> None:
    """
    Send a password reset email via SMTP with fallback to console logging in development.
    """
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    reset_url = f"{frontend_url}/auth/reset-password?token={token}"

    # Dev fallback when SMTP host or user is not configured
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.info(
            "\n" + "=" * 65 + "\n"
            "[EMAIL SERVICE - DEV FALLBACK]\n"
            f"To: {email_to}\n"
            f"Subject: Reset Your Smart Farming Password\n"
            f"Reset Link: {reset_url}\n"
            f"Token: {token}\n"
            "(No SMTP credentials configured in .env; link logged to console)\n"
            + "=" * 65 + "\n"
        )
        return

    from_email = _get_from_email()
    from_header = (
        f"{settings.EMAILS_FROM_NAME} <{from_email}>"
        if settings.EMAILS_FROM_NAME
        else from_email
    )

    msg = MIMEMultipart("alternative")
    msg["From"] = from_header
    msg["To"] = email_to
    msg["Subject"] = "Reset Your Smart Farming Password"

    text_content = f"""Hello,

We received a request to reset the password for your Smart Farming account.
To choose a new password, click the link below (valid for 15 minutes):

{reset_url}

If you did not request a password reset, you can safely ignore this email.

Best regards,
{settings.EMAILS_FROM_NAME}
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f7f4; margin: 0; padding: 20px; }}
    .container {{ max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
    .header {{ background: #166534; padding: 28px 24px; text-align: center; color: #ffffff; }}
    .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; }}
    .content {{ padding: 32px 24px; color: #1e293b; line-height: 1.6; font-size: 15px; }}
    .btn {{ display: inline-block; background: #166534; color: #ffffff !important; text-decoration: none; padding: 12px 28px; border-radius: 6px; font-weight: 600; margin: 24px 0; }}
    .footer {{ background: #f8fafc; padding: 16px 24px; font-size: 12px; color: #64748b; text-align: center; border-top: 1px solid #e2e8f0; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🌱 Smart Farming</h1>
    </div>
    <div class="content">
      <p>Hello,</p>
      <p>We received a request to reset the password for your Smart Farming account.</p>
      <p style="text-align: center;">
        <a href="{reset_url}" class="btn">Reset Password</a>
      </p>
      <p>This password reset link is valid for <strong>15 minutes</strong>. If you did not request this change, you can safely ignore this message.</p>
      <p style="font-size: 13px; color: #64748b; word-break: break-all;">
        If the button above does not work, copy and paste this link into your browser:<br>
        <a href="{reset_url}">{reset_url}</a>
      </p>
    </div>
    <div class="footer">
      &copy; {settings.EMAILS_FROM_NAME}. All rights reserved.
    </div>
  </div>
</body>
</html>
"""

    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        with _create_smtp_connection(timeout=15) as server:
            server.sendmail(from_email, [email_to], msg.as_string())
        logger.info("Password reset email successfully sent to %s via SMTP (%s)", email_to, settings.SMTP_HOST)
    except Exception as exc:
        logger.error(
            "Failed to send password reset email to %s via SMTP (%s:%s): %s",
            email_to,
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            exc,
            exc_info=True,
        )


def send_test_email(email_to: str) -> tuple[bool, str]:
    """
    Direct test helper to verify SMTP credentials and network connectivity.
    Returns (success: bool, message: str).
    """
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return (
            False,
            f"SMTP configuration incomplete. HOST={settings.SMTP_HOST}, USER={settings.SMTP_USER}, PASSWORD={'[SET]' if settings.SMTP_PASSWORD else '[NOT SET]'}"
        )

    from_email = _get_from_email()
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{from_email}>"
    msg["To"] = email_to
    msg["Subject"] = "🌱 Smart Farming - SMTP Connection Test"

    body = f"Hello,\n\nYour SMTP email service on Smart Farming is configured and working successfully!\n\nHost: {settings.SMTP_HOST}:{settings.SMTP_PORT}\nFrom: {from_email}\n"
    msg.attach(MIMEText(body, "plain"))

    try:
        with _create_smtp_connection(timeout=15) as server:
            server.sendmail(from_email, [email_to], msg.as_string())
        return (True, f"Test email successfully sent to {email_to}")
    except Exception as exc:
        return (False, f"SMTP Error: {exc}")
