"""
Test utility to verify SMTP email delivery settings.
Usage:
    backend\\.venv\\Scripts\\python.exe backend/scripts/test_smtp.py [recipient_email]
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add backend/src to sys.path
backend_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_root / "src"))

from app.core.config import settings
from app.services.email import send_test_email


def main():
    recipient = sys.argv[1] if len(sys.argv) > 1 else settings.SMTP_USER

    print("=" * 60)
    print("Smart Farming - SMTP Configuration Diagnostic")
    print("=" * 60)
    print(f"SMTP_HOST     : {settings.SMTP_HOST}")
    print(f"SMTP_PORT     : {settings.SMTP_PORT}")
    print(f"SMTP_USER     : {settings.SMTP_USER}")
    print(f"SMTP_PASSWORD : {'********' if settings.SMTP_PASSWORD else '[NOT SET]'}")
    print(f"SMTP_TLS      : {settings.SMTP_TLS}")
    print(f"SMTP_SSL      : {settings.SMTP_SSL}")
    print(f"FROM_EMAIL    : {settings.EMAILS_FROM_EMAIL or settings.SMTP_USER}")
    print(f"FROM_NAME     : {settings.EMAILS_FROM_NAME}")
    print(f"RECIPIENT     : {recipient}")
    print("=" * 60)

    if not recipient or recipient == "your_email@gmail.com":
        print("\n[!] Please update SMTP_USER and SMTP_PASSWORD in backend/.env with your real credentials.")
        print("Usage: python backend/scripts/test_smtp.py [recipient_email]")
        sys.exit(1)

    print(f"\nAttempting to send test email to {recipient}...")
    success, message = send_test_email(recipient)

    if success:
        print(f"[SUCCESS] {message}")
        print("Check your inbox (and spam folder) for the test email!")
    else:
        print(f"[FAILED] {message}")
        print("\nTroubleshooting tips:")
        print("1. For Gmail: Make sure you use a 16-character 'App Password', NOT your standard Gmail account password.")
        print("   Generate one at: https://myaccount.google.com/apppasswords (requires 2-Step Verification enabled)")
        print("2. Verify SMTP_PORT is 587 (with SMTP_TLS=True) or 465 (with SMTP_SSL=True).")
        print("3. Ensure your firewall or network allows outbound connections to port 587/465.")


if __name__ == "__main__":
    main()
