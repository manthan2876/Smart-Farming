"""
Smart Farming - Agronomic Advisory Service

Orchestrates treatment advice by querying the dedicated Colab Qwen3-4B
microservice on port 8003 (/advise). If the Colab service is offline,
it falls back safely to verified agronomic rules from advisory_kb.json.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings

logger = logging.getLogger("smart-farming.advisory")

KB_FILE_PATH = Path(__file__).resolve().parents[4] / "data" / "advisory_kb.json"

_KB_CACHE: dict[str, Any] | None = None


def _get_advisory_kb() -> dict[str, Any]:
    global _KB_CACHE
    if _KB_CACHE is not None:
        return _KB_CACHE

    paths_to_check = [
        KB_FILE_PATH,
        Path("data/advisory_kb.json"),
        Path("../data/advisory_kb.json"),
        Path("model_service/advisory_kb.json"),
    ]
    for p in paths_to_check:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    _KB_CACHE = json.load(f)
                    return _KB_CACHE
            except Exception as e:
                logger.warning("Could not read knowledge base at %s: %s", p, e)

    _KB_CACHE = {}
    return _KB_CACHE


def _get_hf_client():
    return None


def _build_prompt(context: dict) -> str:
    crop = context.get('crop', 'Unknown Crop')
    disease = context.get('disease', 'Unknown')
    farm = context.get('farm', {})
    plot = context.get('plot', {})
    crop_label = crop if isinstance(crop, str) else (crop.get('label', 'Unknown Crop') if isinstance(crop, dict) else 'Unknown Crop')
    disease_label = disease if isinstance(disease, str) else (disease.get('label', 'Unknown') if isinstance(disease, dict) else 'Unknown')
    farm_name = farm.get('name', 'Farm') if isinstance(farm, dict) else ''
    plot_name = plot.get('name', 'Plot') if isinstance(plot, dict) else ''
    plot_acres = plot.get('area_acres', '') if isinstance(plot, dict) else ''
    return (
        f'You are an agricultural advisory AI for a Smart Farming system.\n'
        f'Farm: {farm_name}\n'
        f'Target Plot: {plot_name} ({plot_acres} acres)\n'
        f'Crop: {crop_label}\n'
        f'Condition: {disease_label}\n'
        f'If target plot acreage is provided, calibrate chemical dilution, spray tank volumes, and rotation precautions to the plot scale.\n'
    )



class LLMRecommendation(BaseModel):
    immediate_action: str = Field(description="Immediate actions to take based on disease and weather")
    treatment: str = Field(description="Long term treatment plan or verified chemical/organic option")
    prevention: str = Field(description="Preventative measures and cultural hygiene")
    monitoring: str = Field(description="Scouting guidelines and progression monitoring")


def _generate_rule_based_advisory(
    crop: str,
    disease: str,
    severity_pct: float,
    severity_bucket: str,
    plot_acres: float | None = None,
    could_also_be: Any = None,
) -> dict[str, Any]:
    """Deterministic, verified fallback advice directly from the agronomic knowledge base."""
    kb = _get_advisory_kb()
    kb_key = f"{crop}|{disease}"
    entry = kb.get(kb_key)
    if not entry and crop and disease:
        clean_dis = disease
        if clean_dis.lower().startswith(crop.lower() + " "):
            clean_dis = clean_dis[len(crop):].strip()
        entry = kb.get(f"{crop}|{clean_dis}")

    farm_note = f" Calibrate spray application for {plot_acres} acre(s)." if plot_acres else ""

    if entry:
        chems = entry.get("chemical_options", [])
        organics = entry.get("organic_options", [])
        culturals = entry.get("cultural_practices", [])

        treat_parts = []
        if chems:
            primary_chem = chems[0]
            treat_parts.append(
                f"Apply {primary_chem.get('name')} at dose {primary_chem.get('dose')} ({primary_chem.get('source')})."
            )
        if organics:
            primary_org = organics[0]
            treat_parts.append(
                f"Organic alternative: {primary_org.get('name')} at {primary_org.get('dose')}."
            )
        treatment_str = " ".join(treat_parts) if treat_parts else "Maintain balanced plant nutrition and moisture."

        cult_str = " ".join(culturals[:2]) if culturals else "Isolate affected plants and ensure canopy ventilation."
        imm_action = f"{cult_str}{farm_note}"

        if could_also_be and isinstance(could_also_be, dict):
            alt_lbl = could_also_be.get("label", "alternative condition")
            imm_action = f"Visual symptoms closely resemble {alt_lbl}. Verify lesions before chemical spraying. {imm_action}"

        sources = [c.get("source") for c in chems if "source" in c] + [o.get("source") for o in organics if "source" in o]

        return {
            "immediate_action": imm_action,
            "treatment": treatment_str,
            "prevention": entry.get("precautions", "Maintain proper crop spacing and weed-free field borders."),
            "monitoring": "Scout foliage twice weekly for new lesion spread.",
            "sources": list(dict.fromkeys(sources)) or ["ICAR Guidelines"],
            "safety_disclaimer": "DISCLAIMER: Always follow local agricultural guidelines, product labels, and consult your local KVK.",
        }

    # Generic fallback when entry is not in knowledge base
    return {
        "immediate_action": f"Consult your local Krishi Vigyan Kendra (KVK) or agriculture extension officer for {crop}.{farm_note}",
        "treatment": "Follow registered crop protection guidelines. Avoid applying synthetic chemicals without verification.",
        "prevention": "Maintain field sanitation and proper drainage.",
        "monitoring": "Monitor crop daily for symptoms spreading.",
        "sources": ["General Agronomic Guidelines"],
        "safety_disclaimer": "DISCLAIMER: Always confirm diagnosis with your local agricultural extension officer.",
    }


def call_remote_advisory_server(payload: dict) -> dict[str, Any] | None:
    """Invokes the Colab Qwen3-4B Advisory Server on port 8003 over HTTP."""
    server_url = (getattr(settings, "ADVISORY_SERVER_URL", "") or "").strip()
    if not server_url:
        return None

    endpoint = f"{server_url.rstrip('/')}/advise"
    timeout_sec = float(getattr(settings, "ADVISORY_SERVER_TIMEOUT", 60.0) or 60.0)

    try:
        headers = {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "SmartFarmingBackend/2.0",
        }
        with httpx.Client(timeout=timeout_sec) as client:
            resp = client.post(endpoint, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and "immediate_action" in data:
                    return data
            logger.warning("Advisory server returned HTTP %d: %s", resp.status_code, resp.text[:200])
    except Exception as exc:
        logger.warning("Failed to reach Advisory server at %s: %s", server_url, exc)

    return None


def generate_recommendation(context: dict, config: dict[str, Any] | None = None) -> dict:
    """
    Pipeline Stage 8: Generate agronomic recommendation.
    Invokes the remote Colab Qwen advisory service if available,
    otherwise falling back safely to deterministic agronomic rules.
    """
    if config is None:
        config = {}

    status_map = context.setdefault("status", {})
    if status_map.get("preprocessing", "completed") != "completed":
        status_map["recommendation"] = "skipped"
        context.setdefault("notes", []).append("Recommendation skipped because preprocessing failed.")
        return context

    crop = context.get("crop", {})
    disease = context.get("disease", {})
    severity = context.get("severity", {})
    weather = context.get("weather", {})
    farm = context.get("farm", {})
    plot = context.get("plot", {})

    crop_label = crop.get("label", "Unknown Crop") if isinstance(crop, dict) else (crop or "Unknown Crop")
    crop_confidence = float(crop.get("confidence", 0.0) if isinstance(crop, dict) else 0.0)
    crop_status = crop.get("status") if isinstance(crop, dict) else None

    disease_label = disease.get("label", "Unknown") if isinstance(disease, dict) else (disease or "Unknown")
    disease_confidence = float(disease.get("confidence", 0.0) if isinstance(disease, dict) else 0.0)

    sev_raw = context.get("severity_pct")
    if sev_raw is None:
        if isinstance(severity, dict):
            sev_raw = severity.get("percent")
        elif isinstance(severity, (int, float)):
            sev_raw = severity
        else:
            sev_raw = 0.0
    try:
        severity_percent = float(sev_raw or 0.0)
    except (ValueError, TypeError):
        severity_percent = 0.0
    if isinstance(severity, dict):
        severity_bucket = severity.get("bucket", "Unknown")
    elif isinstance(severity, str):
        severity_bucket = severity
    else:
        severity_bucket = "Unknown"

    temperature = weather.get("temperature_celsius", "N/A")
    humidity = weather.get("humidity_percent", "N/A")
    weather_condition = weather.get("condition", "N/A")

    could_be = disease.get("could_also_be") if isinstance(disease, dict) else None
    plot_acres = float(plot.get("area_acres")) if plot.get("area_acres") else None

    # Unsupported Crop Gate — enforce safety
    if (
        crop_status == "unsupported_crop"
        or context.get("status", {}).get("decision_routing") == "unsupported_crop"
        or "unsupported crop" in str(disease_label).lower()
        or (crop_confidence > 0.0 and crop_confidence < 0.70)
    ):
        context["recommendation"] = {
            "provider": "safety_gate",
            "model": "unsupported_crop_guardrail",
            "prompt_version": "v3.0",
            "is_fallback": True,
            "is_masked": True,
            "fallback_reason": "Unsupported crop species or indeterminate crop identification.",
            "immediate_action": f"Automated disease diagnosis is not supported for '{crop_label}'. Please consult a local agricultural extension officer or Krishi Vigyan Kendra (KVK).",
            "treatment": "No automated chemical treatment is recommended for unverified crops to avoid pesticide misuse.",
            "prevention": "Ensure proper field drainage, isolate suspicious plants, and seek agronomist guidance.",
            "monitoring": "Take high-resolution, centered photos in balanced daylight.",
            "pesticide": "None (Consult specialist)",
            "sources": ["KVK Extension Guidelines"],
            "safety_disclaimer": "DISCLAIMER: Automated diagnosis currently supports Cotton, Groundnut, Pepper Bell, Potato, and Tomato. Do not apply synthetic pesticides without professional verification.",
        }
        context["status"]["recommendation"] = "completed"
        context["status"]["mask_advisory"] = True
        return context

    # 1. Attempt Colab Advisory Server
    advisory_payload = {
        "crop": crop_label,
        "disease": disease_label,
        "confidence": crop_confidence,
        "severity_pct": severity_percent,
        "severity_bucket": severity_bucket,
        "temperature": str(temperature),
        "humidity": str(humidity),
        "weather_condition": str(weather_condition),
        "plot_acres": plot_acres,
        "language": "en",
    }

    remote_resp = call_remote_advisory_server(advisory_payload)

    if remote_resp:
        try:
            validated = LLMRecommendation(
                immediate_action=remote_resp["immediate_action"],
                treatment=remote_resp["treatment"],
                prevention=remote_resp["prevention"],
                monitoring=remote_resp["monitoring"],
            )
            rec_dict = validated.model_dump()
            rec_dict.update({
                "provider": "Colab / Qwen3-4B (4-bit)",
                "model": "Qwen/Qwen3-4B",
                "prompt_version": "v3.0",
                "is_fallback": False,
                "fallback_reason": None,
                "could_also_be": could_be,
                "sources": remote_resp.get("sources", ["ICAR Knowledge Base"]),
                "farm_aware": bool(farm.get("name") or plot.get("name") or plot_acres),
                "plot_name": plot.get("name"),
                "plot_area_acres": plot_acres,
                "safety_disclaimer": remote_resp.get("safety_disclaimer", "DISCLAIMER: Always confirm diagnosis with your local agricultural officer."),
            })
            context["recommendation"] = rec_dict
            context["status"]["recommendation"] = "completed"
            logger.info("Advisory generated successfully from Colab Qwen service.")
            return context
        except ValidationError as ve:
            logger.warning("Advisory server response failed validation: %s", ve)

    # 2. Deterministic Knowledge Base Fallback
    fallback_data = _generate_rule_based_advisory(
        crop=crop_label,
        disease=disease_label,
        severity_pct=severity_percent,
        severity_bucket=severity_bucket,
        plot_acres=plot_acres,
        could_also_be=could_be,
    )
    fallback_data.update({
        "provider": "rule_based_fallback",
        "model": "advisory_kb_icar_rules",
        "prompt_version": "v3.0",
        "is_fallback": True,
        "fallback_reason": "Remote advisory service unavailable or unconfigured; using verified agronomy rules.",
        "could_also_be": could_be,
        "farm_aware": bool(farm.get("name") or plot.get("name") or plot_acres),
        "plot_name": plot.get("name"),
        "plot_area_acres": plot_acres,
    })

    context["recommendation"] = fallback_data
    context["status"]["recommendation"] = "completed"
    return context


def generate_weather_advisory(user_profile: dict, weather_data: dict) -> str:
    """Generates an agronomic advisory string based on weather and field history."""
    temp_raw = weather_data.get("temperature_celsius", weather_data.get("temperature", 26.0))
    hum_raw = weather_data.get("humidity_percent", weather_data.get("humidity", 65.0))
    cond = str(weather_data.get("condition", weather_data.get("description", "fair skies"))).lower()

    try:
        temp = float(temp_raw)
    except (ValueError, TypeError):
        temp = 26.0

    try:
        hum = float(hum_raw)
    except (ValueError, TypeError):
        hum = 65.0

    crops = user_profile.get("crop_history", [])
    crop_str = f" for {', '.join(crops)}" if crops else ""

    parts: list[str] = []
    if any(w in cond for w in ["rain", "drizzle", "thunderstorm", "shower"]):
        parts.append(
            f"Precipitation detected{crop_str}. Postpone foliar spraying of chemicals and fertilizers to prevent runoff."
        )
        parts.append("Check field drainage to prevent waterlogging.")
    elif hum > 75:
        parts.append(
            f"Elevated relative humidity ({hum:.0f}%){crop_str} increases risk of fungal and bacterial blight. Inspect lower canopy foliage."
        )
        parts.append("Delay foliar spray applications until foliage is dry.")
    elif temp > 34:
        parts.append(
            f"High ambient temperature ({temp:.1f}°C) may cause heat stress. Schedule irrigation during early morning or late evening."
        )
    elif temp < 12:
        parts.append(
            f"Low temperature ({temp:.1f}°C) may slow metabolic growth. Guard young seedlings and inspect soil moisture."
        )
    else:
        parts.append(
            f"Current conditions ({temp:.1f}°C, {hum:.0f}% humidity, {cond}){crop_str} are favorable for routine scouting and field operations."
        )

    return " ".join(parts)
