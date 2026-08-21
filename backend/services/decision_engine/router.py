"""
router.py — Decision Engine

The Decision Engine's single job: crop label → the right disease model.

This is pure business logic — a lookup from the config, NOT another AI model.
It also enforces the crop confidence threshold so that a low-confidence crop
prediction never drives a disease prediction.

Key behaviours:
  • If crop confidence < threshold → marks decision_routing as "skipped_low_confidence"
  • If no disease model is trained yet for the identified crop →
        marks decision_routing as "no_model_available" (does NOT crash)
  • Stores the resolved model config in context["_disease_model_cfg"] for the
        disease classifier to pick up (this key is internal and not returned in
        the final API response).

Contract:
    Input:  context["crop"]["label"]      — e.g. "Tomato"
            context["crop"]["confidence"] — float 0-1
    Output: context["_disease_model_cfg"] — internal dict with path/labels/arch
            context["status"]["decision_routing"] — "completed" | skipped states
"""

from typing import Any


def route_to_disease_model(context: dict, config: dict[str, Any]) -> dict:
    """
    Resolve which disease model to use based on the identified crop.

    Args:
        context: Shared pipeline context.
        config:  Parsed config.yaml dict.

    Returns:
        Mutated context.
    """
    # ── Guard: crop identification must have succeeded ─────────────────
    if context["status"]["crop_identification"] != "completed":
        context["status"]["decision_routing"] = "skipped"
        return context

    crop_label = context["crop"]["label"]
    crop_confidence = context["crop"]["confidence"]
    threshold = config["thresholds"].get("crop_confidence", 0.75)

    # ── Confidence floor ───────────────────────────────────────────────
    if crop_confidence < threshold:
        context["notes"].append(
            f"Crop confidence ({crop_confidence:.2f}) is below threshold ({threshold}). "
            "Skipping disease classification — ask the farmer for a clearer photo."
        )
        context["status"]["decision_routing"] = "skipped_low_confidence"
        return context

    # ── Look up the disease model config ──────────────────────────────
    # The config.yaml uses the crop label as the key (e.g. "Tomato").
    # Spaces are replaced with underscores in the model filename convention,
    # but the config key should match the crop label exactly.
    disease_models: dict = config["models"].get("disease_models", {})

    # Try the label as-is first, then try with spaces → underscores
    model_cfg = disease_models.get(crop_label) or disease_models.get(
        crop_label.replace(" ", "_")
    )

    if model_cfg is None:
        context["notes"].append(
            f"No disease model configured for crop '{crop_label}'. "
            "Skipping disease classification."
        )
        context["status"]["decision_routing"] = "no_model_available"
        return context

    # ── Store resolved config for disease classifier ───────────────────
    # Prefix with "_" to mark as internal — strip before returning to API.
    context["_disease_model_cfg"] = model_cfg
    context["disease"]["model_used"] = (
        f"disease_{crop_label.replace(' ', '_')}"
    )
    context["status"]["decision_routing"] = "completed"

    return context
