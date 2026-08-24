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
_CLIENT_CACHE = InferenceClient(
    api_key=HF_TOKEN,
    provider="nscale",
)

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
        raise ValueError(f"No JSON object found in Hugging Face response: {response_text[:500]}")
    json_text = response_text[start_idx:end_idx + 1]
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

    crop_label = crop.get("label", "Unknown Crop")
    crop_confidence = crop.get("confidence", 0.0)
    disease_label = disease.get("label", "Unknown")
    disease_confidence = disease.get("confidence", 0.0)
    severity_percent = severity.get("percent", 0.0)
    severity_bucket = severity.get("bucket", "Unknown")
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

    prompt = f"""
You are an agricultural advisory AI for a Smart Farming system.
Analyze the following crop diagnostic information.

IMPORTANT:
- Give practical and concise agricultural recommendations.
- Do not invent measurements that are not provided.
- Consider crop, disease, severity, pests, weather and location.
- Do not provide dangerous or excessive chemical instructions.
- Recommend following the pesticide/fungicide label and local agricultural guidance.
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not add explanations outside the JSON.

FARM DIAGNOSTIC DATA
Location: {location}
Crop: {crop_label}
Crop confidence: {crop_confidence}
Disease / Condition: {disease_label}
Disease confidence: {disease_confidence}
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
    "fertilizer": "Specific fertilizer or nutrient-management recommendation",
    "pesticide": "Disease and pest management recommendation",
    "irrigation": "Irrigation recommendation considering weather and disease severity",
    "prevention_tips": "Disease and pest prevention recommendations"
}}
"""
    return prompt.strip()

def generate_recommendation(context: dict, config: dict[str, Any] = None) -> dict:
    if context["status"]["preprocessing"] != "completed":
        context["status"]["recommendation"] = "skipped"
        context["notes"].append("Recommendation skipped because preprocessing failed.")
        return context

    try:
        print("[INFO] Generating recommendation using Hugging Face...")
        client = _get_hf_client()
        prompt = _build_prompt(context)
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": "You are an expert agricultural advisory assistant."},
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
        recommendation = {
            "fertilizer": recommendation_data.get("fertilizer", "N/A"),
            "pesticide": recommendation_data.get("pesticide", "N/A"),
            "irrigation": recommendation_data.get("irrigation", "N/A"),
            "prevention_tips": recommendation_data.get("prevention_tips", "N/A"),
        }
        context["recommendation"] = recommendation
        context["status"]["recommendation"] = "completed"
        print("[OK] Hugging Face recommendation generated successfully.")

    except Exception as exc:
        error_message = f"Hugging Face recommendation error: {type(exc).__name__}: {exc}"
        print(f"[ERROR] {error_message}")
        context["status"]["recommendation"] = "failed"
        context["notes"].append(error_message)
        context["recommendation"] = {
            "error": str(exc),
            "fertilizer": "Use fertilizer according to crop requirements and soil-test results.",
            "pesticide": "Use an appropriate registered treatment for the diagnosed disease or pest and follow the product label.",
            "irrigation": "Maintain consistent soil moisture while avoiding waterlogging and excess leaf wetness.",
            "prevention_tips": "Maintain proper plant spacing, field sanitation, ventilation and regular crop monitoring.",
        }

    return context