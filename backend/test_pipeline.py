"""
test_pipeline.py — Standalone smoke test for the full Smart Farming pipeline.

Run from the backend/ directory:

    python test_pipeline.py

Or provide a specific image:

    python test_pipeline.py "Z:\\Projects\\Smart-Farming\\Datasets\\testing_images\\sample.jpg"

This script:

1. Creates the shared pipeline context.
2. Runs the complete AI pipeline.
3. Prints status for every stage.
4. Prints crop, disease, severity, and pest-classification results.
5. Clearly distinguishes pest CLASSIFICATION from pest DETECTION.
6. Uses ASCII-only output for Windows compatibility.
"""

import pprint
import sys
from pathlib import Path


# ============================================================================
# PATH CONFIGURATION
# ============================================================================

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ============================================================================
# IMPORTS
# ============================================================================

from context import create_context
from pipeline import run_pipeline


# ============================================================================
# DEFAULT TEST IMAGE
# ============================================================================

DEFAULT_TEST_IMAGE = (
    PROJECT_ROOT
    / "Datasets"
    / "testing_images"
    / "sample.jpg"
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def safe_confidence(value):
    """
    Safely format a confidence value.
    """

    if value is None:
        return "N/A"

    try:
        return f"{float(value):.3f}"

    except (TypeError, ValueError):
        return str(value)


def print_stage_status(stage, status):
    """
    Print pipeline stage status using ASCII-only characters.
    """

    if status == "completed":
        icon = "[OK]"

    elif status in (
        "skipped",
        "not_run",
        "no_model_available",
        "skipped_low_confidence",
    ):
        icon = "[--]"

    elif str(status).startswith("failed"):
        icon = "[FAIL]"

    else:
        icon = "[!!]"

    print(
        f"  {icon} "
        f"{stage:<30} -> {status}"
    )


# ============================================================================
# RESULT DISPLAY
# ============================================================================

def print_result_section(result):
    """
    Print model results safely even if some stages failed or were skipped.
    """

    crop = result.get("crop", {})
    disease = result.get("disease", {})
    severity = result.get("severity", {})
    pests = result.get("pests", [])

    pest_classification = result.get(
        "pest_classification",
        {},
    )

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    # ========================================================================
    # CROP
    # ========================================================================

    crop_label = crop.get("label")
    crop_confidence = crop.get("confidence")

    print(
        f"\nCrop       : "
        f"{crop_label if crop_label is not None else 'N/A'}"
        f"  (confidence={safe_confidence(crop_confidence)})"
    )

    # ========================================================================
    # DISEASE
    # ========================================================================

    disease_label = disease.get("label")
    disease_confidence = disease.get("confidence")
    disease_model = disease.get("model_used")

    print(
        f"Disease    : "
        f"{disease_label if disease_label is not None else 'N/A'}"
        f"  (confidence={safe_confidence(disease_confidence)}, "
        f"model={disease_model if disease_model is not None else 'N/A'})"
    )

    # ========================================================================
    # SEVERITY
    # ========================================================================

    severity_percent = severity.get("percent")
    severity_bucket = severity.get("bucket")
    affected_area = severity.get("affected_area")

    if severity_percent is not None:

        print(
            f"Severity   : "
            f"{severity_percent}%"
            f"  ({severity_bucket if severity_bucket else 'N/A'})"
        )

    else:
        print("Severity   : N/A")

    if affected_area is not None:

        print(
            f"Affected   : "
            f"{affected_area * 100:.2f}%"
        )

    # ========================================================================
    # PEST CLASSIFICATION
    # ========================================================================

    print("\nPest Classification")
    print("-" * 70)

    model_type = pest_classification.get(
        "model_type",
        "classification",
    )

    model_used = pest_classification.get(
        "model_used",
    )

    top_k = pest_classification.get(
        "top_k",
        len(pests),
    )

    print(
        f"Model type : {model_type}"
    )

    print(
        f"Model      : "
        f"{model_used if model_used else 'N/A'}"
    )

    print(
        f"Top-K      : {top_k}"
    )

    if pests:

        print(
            "\nPredicted pest classes:"
        )

        for index, pest in enumerate(
            pests,
            start=1,
        ):

            pest_label = pest.get(
                "label",
                "Unknown",
            )

            pest_confidence = pest.get(
                "confidence",
            )

            print(
                f"  {index}. "
                f"{pest_label} "
                f"(confidence={safe_confidence(pest_confidence)})"
            )

        print(
            "\nNOTE: The current YOLO model is a "
            "classification model."
        )

        print(
            "      These are class probabilities, "
            "NOT individual pest detections."
        )

        print(
            "      No bounding boxes or pest counts "
            "are produced."
        )

    else:

        print(
            "Pests      : "
            "No pest classification result / "
            "pest model not loaded"
        )


# ============================================================================
# MAIN
# ============================================================================

def main():

    print("=" * 70)
    print("SMART FARMING - PIPELINE SMOKE TEST")
    print("=" * 70)

    # ========================================================================
    # IMAGE PATH
    # ========================================================================

    if len(sys.argv) > 1:
        image_path = Path(
            sys.argv[1]
        ).expanduser()

    else:
        image_path = DEFAULT_TEST_IMAGE

    image_path = image_path.resolve()

    print(
        f"Project root : {PROJECT_ROOT}"
    )

    print(
        f"Backend      : {BACKEND_DIR}"
    )

    print(
        f"Test image   : {image_path}"
    )

    print()

    # ========================================================================
    # VALIDATE IMAGE
    # ========================================================================

    if not image_path.exists():

        print(
            "[ERROR] Test image was not found.\n"
        )

        print(
            f"Expected path:\n  {image_path}\n"
        )

        print("Usage:")

        print(
            '  python test_pipeline.py '
            '"Z:\\Projects\\Smart-Farming\\Datasets\\testing_images\\sample.jpg"'
        )

        sys.exit(1)

    if not image_path.is_file():

        print(
            f"[ERROR] Path is not a file: "
            f"{image_path}"
        )

        sys.exit(1)

    # ========================================================================
    # CREATE CONTEXT
    # ========================================================================

    print(
        "[1/2] Creating pipeline context..."
    )

    try:

        context = create_context(
            image_path=str(image_path),
            user_id="test_user",
            location="Gujarat, India",
            language="English",
        )

    except Exception as exc:

        print(
            "[ERROR] Failed to create pipeline context."
        )

        print(
            f"        {type(exc).__name__}: {exc}"
        )

        sys.exit(1)

    print(
        "[OK] Context created.\n"
    )

    # ========================================================================
    # RUN PIPELINE
    # ========================================================================

    print(
        "[2/2] Running complete AI pipeline...\n"
    )

    try:

        result = run_pipeline(
            context
        )

    except Exception as exc:

        print("=" * 70)
        print("PIPELINE ERROR")
        print("=" * 70)

        print(
            f"\nError type : "
            f"{type(exc).__name__}"
        )

        print(
            f"Error      : {exc}"
        )

        print(
            "\nThe pipeline raised an exception "
            "before completion."
        )

        sys.exit(1)

    # ========================================================================
    # PIPELINE STATUS
    # ========================================================================

    print("=" * 70)
    print("PIPELINE STATUS")
    print("=" * 70)

    statuses = result.get(
        "status",
        {},
    )

    if not statuses:

        print(
            "  [!!] No pipeline status information returned."
        )

    else:

        for stage, status in statuses.items():

            print_stage_status(
                stage,
                status,
            )

    # ========================================================================
    # RESULTS
    # ========================================================================

    print_result_section(
        result
    )

    # ========================================================================
    # NOTES
    # ========================================================================

    notes = result.get(
        "notes",
        [],
    )

    if notes:

        print(
            "\n" + "=" * 70
        )

        print(
            "NOTES"
        )

        print(
            "=" * 70
        )

        for note in notes:

            print(
                f"  - {note}"
            )

    # ========================================================================
    # IMAGE METADATA
    # ========================================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "IMAGE METADATA"
    )

    print(
        "=" * 70
    )

    image_info = result.get(
        "image",
        {},
    ).copy()

    # Don't print the large numpy image array.
    image_info.pop(
        "leaf_crop",
        None,
    )

    pprint.pprint(
        image_info,
        width=90,
        sort_dicts=False,
    )

    # ========================================================================
    # FAILED STAGES
    # ========================================================================

    failed_stages = [
        stage
        for stage, status in statuses.items()
        if str(status).startswith("failed")
    ]

    print(
        "\n" + "=" * 70
    )

    if failed_stages:

        print(
            "PIPELINE FINISHED WITH FAILURES"
        )

        print(
            "=" * 70
        )

        print(
            "\nFailed stages:"
        )

        for stage in failed_stages:

            print(
                f"  - {stage}"
            )

        sys.exit(2)

    print(
        "PIPELINE COMPLETED"
    )

    print(
        "=" * 70
    )

    print(
        "\n[DONE] Smoke test finished successfully."
    )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()