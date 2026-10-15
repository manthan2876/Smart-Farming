"""
Diagnostic utility to verify email delivery via Supabase Custom SMTP.
Usage:
    python backend/scripts/test_smtp.py [recipient_email]
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Locate backend root and .env file
backend_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_root / "src"))

# Load config: try app settings, fallback to direct .env reading
env_vars: dict[str, str] = {}
env_file = backend_root / ".env"
if not env_file.exists():
    env_file = backend_root / ".env.production"

if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                env_vars[k] = v

supabase_url = env_vars.get("SUPABASE_URL", "")
service_key = env_vars.get("SUPABASE_SERVICE_ROLE_KEY", "")
anon_key = env_vars.get("SUPABASE_ANON_KEY", "")
from_name = env_vars.get("EMAILS_FROM_NAME", "Smart Farming Support")
from_email = env_vars.get("EMAILS_FROM_EMAIL", "mgkuvadiya28@gmail.com")
frontend_url = env_vars.get("FRONTEND_URL", "http://localhost:5173")


def send_test_via_urllib(target_email: str) -> tuple[bool, str]:
    if not supabase_url:
        return (False, "SUPABASE_URL is missing in .env")

    api_key = service_key or anon_key
    if not api_key:
        return (False, "Neither SUPABASE_SERVICE_ROLE_KEY nor SUPABASE_ANON_KEY found in .env")

    url = f"{supabase_url.rstrip('/')}/auth/v1/recover"
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "SmartFarming-Diagnostic/1.0",
    }
    payload = json.dumps({
        "email": target_email,
        "redirect_to": f"{frontend_url.rstrip('/')}/auth/reset-password",
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            status = response.getcode()
            if status in (200, 201, 204):
                return (True, f"Email successfully dispatched to {target_email} via Supabase Custom SMTP ({supabase_url})")
            return (False, f"Supabase responded with HTTP {status}")
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="ignore")
        return (False, f"Supabase HTTP Error {err.code}: {body}")
    except Exception as exc:
        return (False, f"Network/Connection error: {exc}")


def main():
    recipient = sys.argv[1] if len(sys.argv) > 1 else from_email

    print("=" * 65)
    print("Smart Farming - Email Delivery Diagnostic (Supabase Custom SMTP)")
    print("=" * 65)
    print(f"SUPABASE_URL  : {supabase_url}")
    print(f"SERVICE_KEY   : {'[CONFIGURED]' if service_key else '[NOT SET]'}")
    print(f"ANON_KEY      : {'[CONFIGURED]' if anon_key else '[NOT SET]'}")
    print(f"FROM_NAME     : {from_name}")
    print(f"FROM_EMAIL    : {from_email}")
    print(f"FRONTEND_URL  : {frontend_url}")
    print(f"RECIPIENT     : {recipient}")
    print("=" * 65)
    print("Email delivery is dispatched via Supabase Auth using the Custom SMTP")
    print("configured in your Supabase Dashboard (Auth > Configuration > Emails).")
    print("=" * 65)

    print(f"\nAttempting to dispatch test recovery email to {recipient} via Supabase...")
    success, message = send_test_via_urllib(recipient)

    if success:
        print(f"\n[SUCCESS] {message}")
        print("\n--> Check your Gmail inbox (and Spam/Promotions folder) for the email!")
        print(f"--> Sender will be: {from_name} <{from_email}>")
    else:
        print(f"\n[FAILED] {message}")
        print("\nTroubleshooting tips:")
        print("1. Ensure 'Enable custom SMTP' is toggled ON in Supabase Dashboard:")
        print("   Authentication -> Emails -> SMTP provider settings.")
        print("2. Verify your Gmail App Password and username in Supabase SMTP settings.")
        print("3. Check Supabase Auth Rate Limits (under Auth -> Configuration -> Rate Limits).")


if __name__ == "__main__":
    main()
