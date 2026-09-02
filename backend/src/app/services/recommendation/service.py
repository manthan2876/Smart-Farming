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
Temperature: {temperature} Â°C
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
        try:
            validated = LLMRecommendation(**recommendation_data)
            context["recommendation"] = validated.model_dump()
        except ValidationError as ve:
            print(f"[ERROR] LLM Validation Error: {ve}")
            context["recommendation"] = {
                "error": "LLM output failed safety validation",
                "details": str(ve),
                "immediate_action": "Isolate affected plants if possible.",
                "treatment": "Use an appropriate registered treatment for the diagnosed disease and follow product label strictly.",
                "prevention": "Maintain proper plant spacing and field sanitation.",
                "monitoring": "Monitor the crop daily for spread.",
                "safety_disclaimer": "DISCLAIMER: Always follow local agricultural guidelines, product labels, and environmental regulations when applying chemical treatments."
            }
            context["status"]["recommendation"] = "completed"
            return context

        disclaimer = "DISCLAIMER: Always follow local agricultural guidelines, product labels, and environmental regulations when applying chemical treatments."
        
        recommendation = {
            "immediate_action": validated.immediate_action,
            "treatment": validated.treatment,
            "prevention": validated.prevention,
            "monitoring": validated.monitoring,
            "safety_disclaimer": disclaimer
        }
        context["recommendation"] = recommendation
        context["status"]["recommendation"] = "completed"
        print("[OK] Hugging Face recommendation generated successfully.")

    except Exception as exc:
        error_message = (
            f"Hugging Face recommendation error: {type(exc).__name__}: {exc}"
        )
        print(f"[ERROR] {error_message}")
        context["status"]["recommendation"] = "failed"
        context["notes"].append(error_message)
        context["recommendation"] = {
            "error": str(exc),
            "immediate_action": "Isolate affected plants if possible.",
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
