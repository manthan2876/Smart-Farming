"""
service.py — LLM Recommendation Service
Generates actionable farming recommendations using Gemini based on 
crop, disease, severity, pests, weather, and location.
"""

import os
import json
from typing import Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def generate_recommendation(context: dict, config: dict[str, Any] = None) -> dict:
    """
    Constructs a detailed prompt from the shared context dictionary and 
    calls the Gemini API to generate structured agricultural advice.
    """
    # 1. Check if preprocessing and core stages completed
    if context["status"]["preprocessing"] != "completed":
        context["status"]["recommendation"] = "skipped"
        context["notes"].append("Recommendation skipped because preprocessing failed.")
        return context

    # 2. Extract context data
    crop = context.get("crop", {})
    disease = context.get("disease", {})
    severity = context.get("severity", {})
    pests = context.get("pests", [])
    weather = context.get("weather", {})
    user = context.get("user", {})

    crop_label = crop.get("label", "Unknown Crop")
    crop_conf = crop.get("confidence", 0.0)
    
    disease_label = disease.get("label", "Unknown")
    disease_conf = disease.get("confidence", 0.0)
    
    severity_pct = severity.get("percent", 0.0)
    severity_bucket = severity.get("bucket", "N/A")
    
    location = user.get("location", "Unknown Location")
    
    # Format weather summary
    weather_desc = weather.get("description", "N/A")
    temp = weather.get("temperature_celsius", "N/A")
    humidity = weather.get("humidity_percent", "N/A")
    wind_speed = weather.get("wind_speed_m_s", "N/A")

    # Format pests summary
    pest_summary = ", ".join([f"{p.get('label')} ({p.get('confidence'):.2f})" for p in pests]) if pests else "None detected"

    # 3. Initialize Gemini API Client
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API")
    if not api_key:
        context["status"]["recommendation"] = "failed"
        context["notes"].append("Recommendation failed: GEMINI_API_KEY is missing in environment variables.")
        return context

    try:
        client = genai.Client(api_key=api_key)

        # 4. Construct the Prompt
        prompt = f"""
You are an expert agricultural AI assistant. Analyze the following farm diagnostic report and provide precise, actionable recommendations for the farmer.

DIAGNOSTIC REPORT:
- Location: {location}
- Detected Crop: {crop_label} (Confidence: {crop_conf})
- Disease/Condition: {disease_label} (Confidence: {disease_conf})
- Infection Severity: {severity_pct}% (Bucket: {severity_bucket})
- Detected Pests: {pest_summary}
- Current Weather: {temp}°C, Humidity: {humidity}%, Wind: {wind_speed} m/s, Condition: {weather_desc}

Provide your response strictly in the following valid JSON structure with these exact keys:
{{
  "fertilizer": "Recommended fertilizer adjustments or soil nutrients",
  "pesticide": "Recommended treatment, chemical or organic, considering severity and weather",
  "irrigation": "Specific watering advice based on current weather and humidity",
  "prevention_tips": "Long-term disease and pest prevention practices for future cycles"
}}
"""

        # 5. Call Gemini Model (using standard structured response generation)
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        # 6. Parse and store response
        recommendation_data = json.loads(response.text)
        context["recommendation"] = recommendation_data
        context["status"]["recommendation"] = "completed"

    except Exception as exc:
        context["status"]["recommendation"] = "failed"
        context["notes"].append(f"Recommendation generation error: {exc}")
        context["recommendation"] = {
            "error": str(exc),
            "fertilizer": "N/A",
            "pesticide": "N/A",
            "irrigation": "N/A",
            "prevention_tips": "N/A"
        }

    return context