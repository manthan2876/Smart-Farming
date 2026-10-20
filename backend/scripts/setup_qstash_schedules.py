from __future__ import annotations

import argparse
import os
import sys
import httpx

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app.core.config import settings


def get_qstash_headers() -> dict[str, str]:
    token = settings.primary_qstash_token
    if not token:
        print("[ERROR] No QStash token found in environment or .env file.")
        print("Please ensure QSTASH_TOKEN or EU_CENTRAL_1_QSTASH_TOKEN is set.")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {token}",
    }


def list_schedules() -> list[dict]:
    url = f"{settings.primary_qstash_url}/schedules"
    headers = get_qstash_headers()
    print(f"\n[INFO] Querying QStash schedules from {settings.primary_qstash_url}...")
    try:
        resp = httpx.get(url, headers=headers, timeout=10.0)
        if resp.status_code == 200:
            schedules = resp.json()
            print(f"[SUCCESS] Found {len(schedules)} active schedule(s):")
            for idx, s in enumerate(schedules, 1):
                cron = s.get("cron")
                destination = s.get("destination")
                schedule_id = s.get("scheduleId") or s.get("id")
                print(f"  {idx}. ID: {schedule_id} | Cron: '{cron}' -> {destination}")
            return schedules
        else:
            print(f"[ERROR] Failed to list schedules: HTTP {resp.status_code} - {resp.text}")
            return []
    except Exception as exc:
        print(f"[ERROR] Connection error: {exc}")
        return []


def delete_schedule(schedule_id: str) -> bool:
    url = f"{settings.primary_qstash_url}/schedules/{schedule_id}"
    headers = get_qstash_headers()
    print(f"\n[INFO] Deleting schedule '{schedule_id}'...")
    try:
        resp = httpx.delete(url, headers=headers, timeout=10.0)
        if resp.status_code in (200, 204):
            print(f"[SUCCESS] Schedule '{schedule_id}' deleted.")
            return True
        else:
            print(f"[ERROR] Delete failed: HTTP {resp.status_code} - {resp.text}")
            return False
    except Exception as exc:
        print(f"[ERROR] Connection error: {exc}")
        return False


def create_or_update_schedule(
    destination_url: str,
    cron_expression: str,
    schedule_id: str | None = None,
    retries: int = 3,
    failure_callback: str | None = None,
) -> bool:
    endpoint = f"{settings.primary_qstash_url}/schedules/{destination_url}"
    headers = get_qstash_headers()
    headers.update({
        "Upstash-Cron": cron_expression,
        "Upstash-Retries": str(retries),
        "Content-Type": "application/json",
    })
    if schedule_id:
        headers["Upstash-Schedule-Id"] = schedule_id
    if failure_callback:
        headers["Upstash-Failure-Callback"] = failure_callback

    print(f"\n[INFO] Registering Schedule:")
    if schedule_id:
        print(f"       Schedule ID : {schedule_id}")
    print(f"       Destination : {destination_url}")
    print(f"       Expression  : {cron_expression}")
    if failure_callback:
        print(f"       DLQ / Alert : {failure_callback}")

    try:
        resp = httpx.post(endpoint, headers=headers, timeout=10.0)
        if resp.status_code in (200, 201):
            data = resp.json() if resp.text else {}
            assigned_id = data.get("scheduleId") or data.get("id") or schedule_id or "OK"
            print(f"[SUCCESS] Schedule created/updated successfully! (ID: {assigned_id})")
            return True
        else:
            print(f"[ERROR] Failed to register schedule: HTTP {resp.status_code} - {resp.text}")
            return False
    except Exception as exc:
        print(f"[ERROR] Connection error: {exc}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Smart Farming - Upstash QStash Schedule Management CLI"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=os.getenv("BACKEND_URL", "https://smart-farming-backend-kkty.onrender.com"),
        help="Base URL of your deployed FastAPI server (defaults to Render deployment)",
    )
    parser.add_argument(
        "--failure-callback",
        type=str,
        help="Optional custom DLQ failure callback URL (defaults to <base-url>/api/v1/internal/cron/failure-callback)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all active schedules in QStash",
    )
    parser.add_argument(
        "--delete",
        type=str,
        help="Schedule ID to delete",
    )

    args = parser.parse_args()

    print("=" * 65)
    print("  SMART FARMING: UPSTASH QSTASH SCHEDULE MANAGEMENT")
    print(f"  Target Region: {settings.QSTASH_REGION}")
    print(f"  QStash API   : {settings.primary_qstash_url}")
    print("=" * 65)

    if args.list:
        list_schedules()
        return

    if args.delete:
        delete_schedule(args.delete)
        return

    base = args.base_url.rstrip("/")
    dlq_url = args.failure_callback or f"{base}/api/v1/internal/cron/failure-callback"

    # Schedule 1: Weather Risks (06:00, 12:00, 18:00 UTC)
    weather_url = f"{base}/api/v1/internal/cron/weather-risks"
    weather_cron = "0 6,12,18 * * *"
    create_or_update_schedule(
        destination_url=weather_url,
        cron_expression=weather_cron,
        schedule_id="sf-weather-risks",
        failure_callback=dlq_url,
    )

    # Schedule 2: Orphaned Blob Purge (Sundays at 03:00 UTC)
    blob_url = f"{base}/api/v1/internal/cron/purge-blobs"
    blob_cron = "0 3 * * 0"
    create_or_update_schedule(
        destination_url=blob_url,
        cron_expression=blob_cron,
        schedule_id="sf-purge-blobs",
        failure_callback=dlq_url,
    )

    print("\n" + "=" * 65)
    print("  QSTASH SCHEDULE SYNC COMPLETE!")
    print("=" * 65)
    list_schedules()


if __name__ == "__main__":
    main()
