"""
test_pipeline.py — Standalone smoke test for the full Smart Farming pipeline.
"""

import pprint
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from context import create_context
from pipeline import run_pipeline

DEFAULT_TEST_IMAGE = PROJECT_ROOT / "Datasets" / "testing_images" / "aphids_tomato.jpeg"


def safe_confidence(value):
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return str(value)


def print_stage_status(stage, status):
    if status == "completed":
        icon = "[OK]"
    elif status in ("skipped", "not_run", "no_model_available", "skipped_low_confidence"):
        icon = "[--]"
    elif str(status).startswith("failed"):
        icon = "[FAIL]"
    else:
        icon = "[!!]"
    print(f"  {icon} {stage:<30} -> {status}")


def print_result_section(result):
    crop = result.get("crop", {})
    disease = result.get("disease", {})
    severity = result.get("severity", {})
    pests = result.get("pests", [])
    pest_classification = result.get("pest_classification", {})
    weather = result.get("weather", {})
    recommendation = result.get("recommendation", {})

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    # CROP
    crop_label = crop.get("label")
    crop_confidence = crop.get("confidence")
    print(f"\nCrop       : {crop_label if crop_label is not None else 'N/A'}  (confidence={safe_confidence(crop_confidence)})")

    # DISEASE
    disease_label = disease.get("label")
    disease_confidence = disease.get("confidence")
    disease_model = disease.get("model_used")
    print(f"Disease    : {disease_label if disease_label is not None else 'N/A'}  (confidence={safe_confidence(disease_confidence)}, model={disease_model if disease_model is not None else 'N/A'})")

    # SEVERITY
    severity_percent = severity.get("percent")
    severity_bucket = severity.get("bucket")
    affected_area = severity.get("affected_area")

    if severity_percent is not None:
        print(f"Severity   : {severity_percent}%  ({severity_bucket if severity_bucket else 'N/A'})")
    else:
        print("Severity   : N/A")

    if affected_area is not None:
        print(f"Affected   : {affected_area * 100:.2f}%")

    # WEATHER
    print("\nWeather Data")
    print("-" * 70)
    if weather.get("status") == "success":
        print(f"Condition   : {weather.get('condition')} ({weather.get('description')})")
        print(f"Temperature : {weather.get('temperature_celsius')}°C (Feels like: {weather.get('feels_like_celsius')}°C)")
        print(f"Humidity    : {weather.get('humidity_percent')}%")
        print(f"Wind Speed  : {weather.get('wind_speed_m_s')} m/s")
    else:
        print(f"Status      : {weather.get('status', 'N/A')}")

    # RECOMMENDATIONS (NEW)
    print("\nAI Recommendations")
    print("-" * 70)
    if recommendation and "error" not in recommendation:
        print(f"Fertilizer  : {recommendation.get('fertilizer', 'N/A')}")
        print(f"Pesticide   : {recommendation.get('pesticide', 'N/A')}")
        print(f"Irrigation  : {recommendation.get('irrigation', 'N/A')}")
        print(f"Prevention  : {recommendation.get('prevention_tips', 'N/A')}")
    else:
        print("Recommendations: Not available or failed.")

    # PEST CLASSIFICATION
    print("\nPest Classification")
    print("-" * 70)
    model_type = pest_classification.get("model_type", "classification")
    model_used = pest_classification.get("model_used")
    top_k = pest_classification.get("top_k", len(pests))

    print(f"Model type : {model_type}")
    print(f"Model      : {model_used if model_used else 'N/A'}")
    print(f"Top-K      : {top_k}")

    if pests:
        print("\nPredicted pest classes:")
        for index, pest in enumerate(pests, start=1):
            print(f"  {index}. {pest.get('label', 'Unknown')} (confidence={safe_confidence(pest.get('confidence'))})")
    else:
        print("Pests      : No pest classification result")


def main():
    print("=" * 70)
    print("SMART FARMING - PIPELINE SMOKE TEST")
    print("=" * 70)

    image_path = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else DEFAULT_TEST_IMAGE
    image_path = image_path.resolve()

    if not image_path.exists() or not image_path.is_file():
        print(f"[ERROR] Test image not found at: {image_path}")
        sys.exit(1)

    print("[1/2] Creating pipeline context...")
    context = create_context(
        image_path=str(image_path),
        user_id="test_user",
        location="Warsaw, Poland",
        lat=52.2297,
        lon=21.0122,
        language="English",
    )
    print("[OK] Context created.\n")

    print("[2/2] Running complete AI pipeline...\n")
    try:
        result = run_pipeline(context)
    except Exception as exc:
        print(f"[PIPELINE ERROR] {type(exc).__name__}: {exc}")
        sys.exit(1)

    print("=" * 70)
    print("PIPELINE STATUS")
    print("=" * 70)
    for stage, status in result.get("status", {}).items():
        print_stage_status(stage, status)

    print_result_section(result)

    notes = result.get("notes", [])
    if notes:
        print("\n" + "=" * 70)
        print("NOTES")
        print("=" * 70)
        for note in notes:
            print(f"  - {note}")

    print("\n[DONE] Smoke test finished successfully.")


if __name__ == "__main__":
    main()