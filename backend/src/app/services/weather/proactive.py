"""
Proactive Microclimate Alert Engine (Phase 2)
Fetches 5-day / 3-hour forecast for every plot, evaluates disease risk rules,
and writes deduplicated Alert rows so the dashboard can show actionable warnings.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.core.database import SessionLocal
from app.models.alert import Alert
from app.models.plot import Plot
from app.models.farm import Farm

logger = logging.getLogger("smart-farming.proactive-weather")

OPENWEATHER_API = os.getenv("OPENWEATHER_API")

# ──────────────────────────────────────────────────────────────
# Risk Rules
# Each rule: (kind, title_template, body_template, condition_fn)
#   condition_fn(forecast_periods: list[dict]) -> bool
# ──────────────────────────────────────────────────────────────
def _high_humidity_warm(periods: list[dict]) -> bool:
    """High humidity (>75%) + warm temps (20-30°C) → Early Blight / Leaf Spot risk."""
    for p in periods:
        humidity = p.get("main", {}).get("humidity", 0)
        temp = p.get("main", {}).get("temp", 0)
        if humidity > 75 and 20 <= temp <= 30:
            return True
    return False

def _extreme_heat(periods: list[dict]) -> bool:
    """Sustained heat > 38°C → Heat Stress risk."""
    hot_count = sum(1 for p in periods if p.get("main", {}).get("temp", 0) > 38)
    return hot_count >= 3

def _heavy_rain(periods: list[dict]) -> bool:
    """Forecast rainfall > 20mm cumulative → Root Rot / Waterlogging risk."""
    total_rain = sum(p.get("rain", {}).get("3h", 0) for p in periods[:8])  # next 24h
    return total_rain > 20

RISK_RULES: list[tuple[str, str, str, Any]] = [
    (
        "weather_blight_risk",
        "🍃 Early Blight / Leaf Spot Risk Detected",
        "Forecast shows high humidity (>75%) with warm temperatures — ideal conditions for fungal diseases. Consider applying preventative copper-based fungicide.",
        _high_humidity_warm,
    ),
    (
        "weather_heat_stress",
        "🌡️ Extreme Heat Stress Warning",
        "Temperatures exceeding 38°C are forecast. Ensure crops receive adequate irrigation; consider mulching to retain soil moisture.",
        _extreme_heat,
    ),
    (
        "weather_flood_risk",
        "🌧️ Heavy Rain / Waterlogging Alert",
        "Over 20mm of rainfall is forecast in the next 24 hours. Ensure drainage channels are clear to prevent root rot.",
        _heavy_rain,
    ),
]


async def _fetch_forecast(lat: float, lon: float, client: httpx.AsyncClient) -> list[dict]:
    """Fetch 5-day / 3-hour forecast list from OpenWeatherMap."""
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API}&units=metric&cnt=40"
    )
    resp = await client.get(url, timeout=10)
    if resp.status_code != 200:
        logger.warning(f"Forecast API error: {resp.status_code}")
        return []
    return resp.json().get("list", [])


def _alert_exists(db, user_id: str, plot_id: int | None, kind: str) -> bool:
    """Return True if an unread alert of this kind was already created in the last 24h."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    q = db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.kind == kind,
        Alert.is_read == False,
        Alert.created_at >= cutoff,
    )
    if plot_id is not None:
        q = q.filter(Alert.plot_id == plot_id)
    return q.first() is not None


async def evaluate_weather_risks(ctx: dict | None = None) -> None:
    """
    ARQ-compatible cron task. Iterates every plot, fetches forecast,
    and writes alerts for any triggered risk rules.
    """
    if not OPENWEATHER_API:
        logger.warning("OPENWEATHER_API env var not set — skipping proactive weather checks.")
        return

    logger.info("Running proactive weather risk evaluation for all plots...")
    db = SessionLocal()
    created_count = 0

    try:
        plots = db.query(Plot).join(Farm, Plot.farm_id == Farm.id).all()

        new_alerts = []
        async with httpx.AsyncClient() as client:
            for plot in plots:
                farm = plot.farm
                if not farm or not farm.latitude or not farm.longitude:
                    continue

                lat, lon = farm.latitude, farm.longitude
                user_id = farm.user_id

                forecast_periods = await _fetch_forecast(lat, lon, client)
                if not forecast_periods:
                    continue

                for kind, title, body, condition_fn in RISK_RULES:
                    if condition_fn(forecast_periods) and not _alert_exists(db, user_id, plot.id, kind):
                        alert = Alert(
                            user_id=user_id,
                            plot_id=plot.id,
                            kind=kind,
                            severity="high" if "heat" in kind or "flood" in kind else "medium",
                            title=f"{title} — {plot.name}",
                            body=body,
                        )
                        db.add(alert)
                        new_alerts.append(alert)
                        created_count += 1

        db.commit()

        # Enqueue background translation for all created alerts
        from app.core.arq import enqueue_translation
        for a in new_alerts:
            try:
                await enqueue_translation("alert", a.id, {"title": a.title, "body": a.body})
            except Exception:
                pass

        logger.info(f"Proactive weather evaluation complete. {created_count} new alert(s) created.")
    except Exception as exc:
        logger.error(f"Proactive weather cron error: {exc}")
        db.rollback()
    finally:
        db.close()

