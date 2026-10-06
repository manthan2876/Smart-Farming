from pydantic import BaseModel, Field, ValidationError
"""
Smart Farming - Remote AI Recommendation Service

Uses Hugging Face Inference Providers instead of loading
a large LLM locally.

Model:
    Qwen/Qwen2.5-1.5B-Instruct

Provider:
    Hugging Face Inference Providers

Required environment variable:
    HF_TOKEN
"""

import json
import os
from typing import Any
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

MODEL_ID = "Qwen/Qwen3-4B-Instruct-2507"
HF_TOKEN = os.getenv("HF_TOKEN")
class LLMRecommendation(BaseModel):
    immediate_action: str = Field(description="Immediate actions to take")
    treatment: str = Field(description="Long term treatment plan")
    prevention: str = Field(description="How to prevent this in the future")
    monitoring: str = Field(description="How to monitor the situation")

_CLIENT_CACHE: InferenceClient | None = None



def _get_hf_client() -> InferenceClient:
    """Create and cache the Hugging Face InferenceClient."""
    global _CLIENT_CACHE
    if _CLIENT_CACHE is not None:
        return _CLIENT_CACHE
    if not HF_TOKEN:
        raise RuntimeError(
            "HF_TOKEN environment variable is not set. "
            "Create a Hugging Face token with "
            "'Make calls to Inference Providers' permission "
            "and store it in backend/.env."
        )
    print("[INFO] Initializing Hugging Face Inference Client...")
    print(f"[INFO] Recommendation model: {MODEL_ID}")
    print("[INFO] Provider: nscale")
    _CLIENT_CACHE = InferenceClient(api_key=HF_TOKEN, provider="nscale")
    return _CLIENT_CACHE


def _extract_json(text: str) -> dict:
    if not text:
        raise ValueError("Hugging Face returned an empty response.")
    response_text = text.strip()
    if "```json" in response_text:
        response_text = response_text.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```", 1)[1].split("```", 1)[0].strip()
    start_idx = response_text.find("{")
    end_idx = response_text.rfind("}")
    if start_idx == -1 or end_idx == -1:
        raise ValueError(
            f"No JSON object found in Hugging Face response: {response_text[:500]}"
        )
    json_text = response_text[start_idx : end_idx + 1]
    data = json.loads(json_text)
    if not isinstance(data, dict):
        raise ValueError("Model response JSON is not an object.")
    return data


def _build_prompt(context: dict) -> str:
    crop = context.get("crop", {})
    disease = context.get("disease", {})
    severity = context.get("severity", {})
    pests = context.get("pests", [])
    weather = context.get("weather", {})
    user = context.get("user", {})

    crop_label = crop if isinstance(crop, str) else (crop.get("label", "Unknown Crop") if isinstance(crop, dict) else "Unknown Crop")
    crop_confidence = crop.get("confidence", 0.0) if isinstance(crop, dict) else 0.0
    disease_label = disease if isinstance(disease, str) else (disease.get("label", "Unknown") if isinstance(disease, dict) else "Unknown")
    disease_confidence = disease.get("confidence", 0.0) if isinstance(disease, dict) else 0.0

    severity_percent = severity if isinstance(severity, (int, float)) else (severity.get("percent", 0.0) if isinstance(severity, dict) else 0.0)
    severity_bucket = severity if isinstance(severity, str) else (severity.get("bucket", "Unknown") if isinstance(severity, dict) else "Unknown")
    location = user.get("location", "Unknown Location")
    temperature = weather.get("temperature_celsius", "N/A")
    humidity = weather.get("humidity_percent", "N/A")
    wind_speed = weather.get("wind_speed_m_s", "N/A")
    weather_condition = weather.get("condition", "N/A")
    weather_description = weather.get("description", "N/A")

    pest_items = []
    for pest in pests:
        label = pest.get("label", "Unknown")
        confidence = pest.get("confidence", 0.0)
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0
        pest_items.append(f"{label} ({confidence:.3f})")
    pest_summary = ", ".join(pest_items) if pest_items else "No pest detected"

    could_also_be = disease.get("could_also_be") if isinstance(disease, dict) else None
    could_also_be_info = ""
    if could_also_be and isinstance(could_also_be, dict):
        c_lbl = could_also_be.get("label", "")
        c_cnf = could_also_be.get("confidence", 0.0)
        could_also_be_info = f"\nAlternative condition (Near-tie): Could also be {c_lbl} ({c_cnf*100:.1f}% confidence)"

    farm = context.get("farm", {})
    plot = context.get("plot", {})
    farm_info_lines = []
    if farm.get("name") or farm.get("area_acres"):
        farm_info_lines.append(f"Farm: {farm.get('name') or 'Farm'}" + (f" ({farm.get('area_acres')} acres total)" if farm.get("area_acres") else ""))
    if plot.get("name") or plot.get("area_acres"):
        farm_info_lines.append(f"Target Plot: {plot.get('name') or 'Plot'}" + (f" ({plot.get('area_acres')} acres)" if plot.get("area_acres") else ""))
    if farm.get("crop_history"):
        crops_str = ", ".join(farm.get("crop_history")[:4])
        farm_info_lines.append(f"Farm Historical Crops: {crops_str}")
    farm_context_block = ("\n" + "\n".join(farm_info_lines)) if farm_info_lines else ""

    prompt = f"""
You are an agricultural advisory AI for a Smart Farming system.
Analyze the following crop diagnostic information.

IMPORTANT:
- Generate all recommendation text in English by default.
- Give practical and concise agricultural recommendations.
- Do not invent measurements that are not provided.
- Consider crop, disease, severity, pests, weather, location, target plot area, and historical crops.
- If target plot acreage is provided, calibrate chemical dilution, spray tank volumes, and rotation precautions to the plot scale.
- Do not provide dangerous or excessive chemical instructions.
- Recommend following the pesticide/fungicide label and local agricultural guidance.
- If an alternative condition is indicated (Could also be), advise careful foliar inspection before applying narrow-spectrum chemicals.
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not add explanations outside the JSON.

FARM DIAGNOSTIC DATA
Location: {location}{farm_context_block}
Crop: {crop_label}
Crop confidence: {crop_confidence}
Disease / Condition: {disease_label}
Disease confidence: {disease_confidence}{could_also_be_info}
Disease severity: {severity_percent}%
Severity category: {severity_bucket}
Detected pests: {pest_summary}
Weather condition: {weather_condition}
Weather description: {weather_description}
Temperature: {temperature} °C
Humidity: {humidity} %
Wind speed: {wind_speed} m/s

RETURN EXACTLY THIS JSON STRUCTURE:
{{
    "immediate_action": "Immediate actions to take based on disease and weather",
    "treatment": "Long term treatment plan or pesticide recommendation",
    "prevention": "How to prevent this in the future",
    "monitoring": "How to monitor the situation or manage irrigation"
}}
"""
    return prompt.strip()


def generate_recommendation(context: dict, config: dict[str, Any] | None = None) -> dict:
    if config is None:
        config = {}

    status_map = context.setdefault("status", {})
    if status_map.get("preprocessing", "completed") != "completed":
        status_map["recommendation"] = "skipped"
        context.setdefault("notes", []).append("Recommendation skipped because preprocessing failed.")
        return context

    crop = context.get("crop", {})
    disease = context.get("disease", {})
    crop_label = crop.get("label", "Unknown Crop") if isinstance(crop, dict) else (crop or "Unknown Crop")
    crop_confidence = crop.get("confidence", 0.0) if isinstance(crop, dict) else 0.0
    crop_status = crop.get("status") if isinstance(crop, dict) else None
    disease_label = disease.get("label", "Unknown") if isinstance(disease, dict) else (disease or "Unknown")

    # Unsupported Crop Gate — suppress chemical recommendation and enforce safety
    if (
        crop_status == "unsupported_crop"
        or context.get("status", {}).get("decision_routing") == "unsupported_crop"
        or "unsupported crop" in str(disease_label).lower()
        or (crop_confidence > 0.0 and crop_confidence < 0.70)
    ):
        context["recommendation"] = {
            "provider": "safety_gate",
            "model": "unsupported_crop_guardrail",
            "prompt_version": "v1.0",
            "is_fallback": True,
            "is_masked": True,
            "fallback_reason": "Unsupported crop species or indeterminate crop identification.",
            "immediate_action": f"Automated disease diagnosis is not supported for '{crop_label}'. Please consult a local agricultural extension officer or Krishi Vigyan Kendra (KVK).",
            "treatment": "No automated chemical treatment is recommended for unverified crops to avoid pesticide misuse.",
            "prevention": "Ensure proper field drainage, isolate suspicious plants, and seek agronomist guidance before applying fungicides.",
            "monitoring": "Take high-resolution, centered photos in balanced daylight and have a specialist review the plant.",
            "pesticide": "None (Consult specialist)",
            "safety_disclaimer": "DISCLAIMER: Automated diagnosis currently supports Cotton, Groundnut, Pepper Bell, Potato, and Tomato. Do not apply synthetic pesticides without professional verification.",
        }
        context["status"]["recommendation"] = "completed"
        context["status"]["mask_advisory"] = True
        return context

    try:
        print("[INFO] Generating recommendation using Hugging Face...")
        client = _get_hf_client()
        prompt = _build_prompt(context)
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert agricultural advisory assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=350,
            temperature=0.2,
        )
        if not completion.choices:
            raise RuntimeError("Hugging Face returned no completion choices.")
        message = completion.choices[0].message
        response_text = message.content
        if not response_text:
            raise RuntimeError("Hugging Face returned empty model content.")
        print("[INFO] Hugging Face response received.")

        recommendation_data = _extract_json(response_text)
        
        # Legacy mapping for stubborn LLMs
        if "fertilizer" in recommendation_data and "immediate_action" not in recommendation_data:
            recommendation_data["immediate_action"] = recommendation_data.pop("fertilizer")
        if "pesticide" in recommendation_data and "treatment" not in recommendation_data:
            recommendation_data["treatment"] = recommendation_data.pop("pesticide")
        if "prevention_tips" in recommendation_data and "prevention" not in recommendation_data:
            recommendation_data["prevention"] = recommendation_data.pop("prevention_tips")
        if "irrigation" in recommendation_data and "monitoring" not in recommendation_data:
            recommendation_data["monitoring"] = recommendation_data.pop("irrigation")

        # Deterministic Guardrails
        dis = context.get("disease", {})
        could_be = dis.get("could_also_be") if isinstance(dis, dict) else None
        dis_label = dis.get("label", str(dis)) if isinstance(dis, dict) else str(dis)
        is_near_tie = dis.get("is_near_tie", False) if isinstance(dis, dict) else False

        try:
            validated = LLMRecommendation(**recommendation_data)
            rec_dict = validated.model_dump()
            farm = context.get("farm", {})
            plot = context.get("plot", {})
            rec_dict.update({
                "provider": "HuggingFace / nscale",
                "model": MODEL_ID,
                "prompt_version": "v1.0",
                "is_fallback": False,
                "fallback_reason": None,
                "could_also_be": could_be,
                "farm_aware": bool(farm.get("name") or plot.get("name") or plot.get("area_acres")),
                "plot_name": plot.get("name"),
                "plot_area_acres": plot.get("area_acres"),
                "safety_disclaimer": "DISCLAIMER: Always follow local agricultural guidelines, product labels, and environmental regulations when applying chemical treatments."
            })
            context["recommendation"] = rec_dict
            context["status"]["recommendation"] = "completed"
            print("[OK] Hugging Face recommendation generated successfully.")
            return context
        except ValidationError as ve:
            print(f"[ERROR] LLM Validation Error: {ve}")
            farm = context.get("farm", {})
            plot = context.get("plot", {})
            imm_act = (
                f"Visual symptoms are close between {dis_label} and {could_be.get('label') if isinstance(could_be, dict) else could_be}. Isolate affected plants and verify symptoms before chemical spraying."
                if is_near_tie
                else "Isolate affected plants if possible."
            )
            if plot.get("area_acres"):
                imm_act += f" Calibrate spray application for {plot.get('area_acres')} acre(s)."
            context["recommendation"] = {
                "provider": "rule_based_fallback",
                "model": "internal_safety_rules",
                "prompt_version": "v1.0",
                "is_fallback": True,
                "fallback_reason": f"LLM output failed safety validation: {ve}",
                "error": "LLM output failed safety validation",
                "details": str(ve),
                "could_also_be": could_be,
                "farm_aware": bool(farm.get("name") or plot.get("name") or plot.get("area_acres")),
                "plot_name": plot.get("name"),
                "plot_area_acres": plot.get("area_acres"),
                "immediate_action": imm_act,
                "treatment": "Use an appropriate registered treatment for the diagnosed disease and follow product label strictly.",
                "prevention": "Maintain proper plant spacing and field sanitation.",
                "monitoring": "Monitor the crop daily for spread.",
                "safety_disclaimer": "DISCLAIMER: Always follow local agricultural guidelines, product labels, and environmental regulations when applying chemical treatments."
            }
            context["status"]["recommendation"] = "completed"
            return context

    except Exception as exc:
        error_message = (
            f"Hugging Face recommendation error: {type(exc).__name__}: {exc}"
        )
        print(f"[ERROR] {error_message}")
        context.setdefault("status", {})["recommendation"] = "failed"
        context.setdefault("notes", []).append(error_message)
        farm = context.get("farm", {})
        plot = context.get("plot", {})
        dis = context.get("disease", {})
        could_be = dis.get("could_also_be") if isinstance(dis, dict) else None
        dis_label = dis.get("label", str(dis)) if isinstance(dis, dict) else str(dis)
        is_near_tie = dis.get("is_near_tie", False) if isinstance(dis, dict) else False
        imm_act = (
            f"Visual symptoms are close between {dis_label} and {could_be.get('label') if isinstance(could_be, dict) else could_be}. Isolate affected plants and verify symptoms before chemical spraying."
            if is_near_tie
            else "Isolate affected plants if possible."
        )
        if plot.get("area_acres"):
            imm_act += f" Calibrate spray application for {plot.get('area_acres')} acre(s)."
        context["recommendation"] = {
            "provider": "rule_based_fallback",
            "model": "internal_safety_rules",
            "prompt_version": "v1.0",
            "is_fallback": True,
            "fallback_reason": str(exc),
            "error": str(exc),
            "could_also_be": could_be,
            "farm_aware": bool(farm.get("name") or plot.get("name") or plot.get("area_acres")),
            "plot_name": plot.get("name"),
            "plot_area_acres": plot.get("area_acres"),
            "immediate_action": imm_act,
            "treatment": "Use an appropriate registered treatment for the diagnosed disease and follow product label strictly.",
            "prevention": "Maintain proper plant spacing and field sanitation.",
            "monitoring": "Monitor the crop daily for spread.",
            "safety_disclaimer": "DISCLAIMER: Always follow local agricultural guidelines, product labels, and environmental regulations when applying chemical treatments."
        }

    return context

def generate_weather_advisory(user_profile: dict, weather_data: dict) -> str:
    """Generates an agronomic advisory string based on weather and field history."""
    try:
        client = _get_hf_client()
        
        crops = user_profile.get("crop_history", [])
        location = user_profile.get("location", "Unknown")
        farm_name = user_profile.get("farm_name", "Unknown Farm")
        area = user_profile.get("farm_area_acres", "Unknown")
        
        temp = weather_data.get("temperature_celsius", weather_data.get("temperature", "N/A"))
        humidity = weather_data.get("humidity_percent", weather_data.get("humidity", "N/A"))
        condition = weather_data.get("condition", weather_data.get("description", "N/A"))
        
        prompt = f"""You are an expert agronomist AI.
Analyze the following farm data and current weather conditions.
Write a single, practical paragraph advising the farmer on what actions to take today.

FARM DATA
Location: {location}
Farm Name: {farm_name}
Area: {area} acres
Current/Historical Crops: {', '.join(crops) if crops else 'Unknown'}

WEATHER CONDITIONS
Temperature: {temp}C
Humidity: {humidity}%
Condition: {condition}

Provide only the advisory paragraph. No markdown, no conversational filler."""
        
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_ID,
            max_tokens=200,
            temperature=0.3,
        )
        text = response.choices[0].message.content.strip()
        return text
    except Exception as e:
        print(f"[ERROR] Weather advisory generation failed: {e}")
        return ""
