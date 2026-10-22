from __future__ import annotations

from typing import Any

import numpy as np


def evaluate_disease_prediction(
    classes: list[str],
    probs: np.ndarray,
    threshold: float = 0.7,
    near_tie_margin: float = 0.15,
) -> dict[str, Any]:
    sorted_indices = np.argsort(probs)[::-1]
    top_idx = int(sorted_indices[0])
    label = classes[top_idx]
    confidence = float(probs[top_idx])

    second_label: str | None = None
    second_confidence = 0.0
    if len(sorted_indices) > 1:
        second_idx = int(sorted_indices[1])
        second_label = classes[second_idx]
        second_confidence = float(probs[second_idx])

    margin = float(confidence - second_confidence) if second_label else 1.0
    all_probs = {cls_name: float(probability) for cls_name, probability in zip(classes, probs)}
    is_near_tie = bool(
        second_label is not None
        and margin <= near_tie_margin
        and confidence < 0.85
    )

    could_also_be = None
    if second_label and second_confidence >= 0.10:
        could_also_be = {
            "label": second_label,
            "confidence": round(second_confidence, 4),
            "margin": round(margin, 4),
        }

    notes = []
    if is_near_tie:
        confidence_rating = "near_tie"
        is_uncertain = True
        notes.append(
            f"Near-tie diagnosis: primary candidate '{label}' ({confidence*100:.1f}%) is close to '{second_label}' ({second_confidence*100:.1f}%, margin {margin*100:.1f}%). Could also be {second_label}."
        )
    elif confidence >= 0.85:
        confidence_rating = "high"
        is_uncertain = False
    elif confidence >= threshold:
        confidence_rating = "moderate"
        is_uncertain = False
    else:
        confidence_rating = "low"
        is_uncertain = True
        notes.append(
            f"Disease confidence ({confidence:.2f}) is below threshold ({threshold}). Indeterminate diagnosis."
        )

    return {
        "label": label,
        "confidence": confidence,
        "all_probs": all_probs,
        "is_near_tie": is_near_tie,
        "could_also_be": could_also_be,
        "confidence_rating": confidence_rating,
        "is_uncertain": is_uncertain,
        "uncertainty": round(float(1.0 - confidence), 3),
        "notes": notes,
    }
