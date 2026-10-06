"""
calibration.py — Confidence Calibration & Uncertainty Quantification
Implements temperature scaling and Expected Calibration Error (ECE)
for neural network predictions across controlled and field datasets.
"""

from __future__ import annotations

from typing import Any
import numpy as np


def apply_temperature_scaling(
    logits: np.ndarray,
    temperature: float = 1.0,
) -> np.ndarray:
    """
    Applies temperature scaling to raw logits:
        scaled_probs = softmax(logits / temperature)
    
    A temperature T > 1 softens overconfident softmax distributions,
    aligning reported model confidence with empirical validation accuracy.
    """
    if temperature <= 0.0:
        raise ValueError("Temperature must be strictly positive.")
    
    scaled_logits = logits / float(temperature)
    # Numerically stable softmax
    shifted_logits = scaled_logits - np.max(scaled_logits, axis=-1, keepdims=True)
    exp_logits = np.exp(shifted_logits)
    probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
    return probs


def calibrate_probability_scalar(
    prob: float,
    temperature: float = 1.0,
    num_classes: int = 2,
) -> float:
    """
    Calibrates a single predicted probability using logit-space temperature scaling
    against an assumed uniform prior for remaining classes.
    """
    if temperature <= 0.0:
        raise ValueError("Temperature must be strictly positive.")
    if temperature == 1.0:
        return float(prob)

    clipped = float(np.clip(prob, 1e-6, 1.0 - 1e-6))
    # Approximate logit for top class assuming rest share (1 - p)/(K - 1)
    k = max(2, num_classes)
    logit_diff = np.log(clipped) - np.log((1.0 - clipped) / (k - 1))
    scaled_logit_diff = logit_diff / float(temperature)
    
    # Inverted logistic
    calibrated = 1.0 / (1.0 + (k - 1) * np.exp(-scaled_logit_diff))
    return float(np.clip(calibrated, 0.0, 1.0))


def compute_ece(
    y_true: list[int] | np.ndarray,
    y_probs: np.ndarray,
    num_bins: int = 10,
) -> dict[str, Any]:
    """
    Computes Expected Calibration Error (ECE), Maximum Calibration Error (MCE),
    and Brier score across confidence bins.
    
    Args:
        y_true: Array of ground-truth integer class labels (shape [N])
        y_probs: Predicted probability distributions (shape [N, K])
        num_bins: Number of confidence bins between 0 and 1
    
    Returns:
        dict containing 'ece', 'mce', 'brier_score', and per-bin statistics.
    """
    y_true = np.asarray(y_true)
    y_probs = np.asarray(y_probs)
    n_samples = len(y_true)
    if n_samples == 0:
        return {"ece": 0.0, "mce": 0.0, "brier_score": 0.0, "num_samples": 0, "bins": []}

    confidences = np.max(y_probs, axis=1)
    predictions = np.argmax(y_probs, axis=1)
    accuracies = (predictions == y_true).astype(float)

    bin_boundaries = np.linspace(0.0, 1.0, num_bins + 1)
    bin_stats = []
    total_ece = 0.0
    max_ce = 0.0

    for i in range(num_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        if i == num_bins - 1:
            in_bin = (confidences >= bin_lower) & (confidences <= bin_upper)
        else:
            in_bin = (confidences >= bin_lower) & (confidences < bin_upper)
        
        bin_count = int(np.sum(in_bin))
        if bin_count > 0:
            bin_acc = float(np.mean(accuracies[in_bin]))
            bin_conf = float(np.mean(confidences[in_bin]))
            ce = abs(bin_acc - bin_conf)
            total_ece += (bin_count / n_samples) * ce
            max_ce = max(max_ce, ce)
        else:
            bin_acc = 0.0
            bin_conf = 0.0
            ce = 0.0

        bin_stats.append({
            "bin": i,
            "range": [round(bin_lower, 2), round(bin_upper, 2)],
            "count": bin_count,
            "accuracy": round(bin_acc, 4),
            "confidence": round(bin_conf, 4),
            "calibration_error": round(ce, 4),
        })

    # Multiclass Brier score
    num_classes = y_probs.shape[1]
    one_hot = np.zeros((n_samples, num_classes))
    one_hot[np.arange(n_samples), y_true] = 1.0
    brier_score = float(np.mean(np.sum((y_probs - one_hot) ** 2, axis=1)))

    return {
        "ece": round(float(total_ece), 4),
        "mce": round(float(max_ce), 4),
        "brier_score": round(brier_score, 4),
        "num_samples": n_samples,
        "bins": bin_stats,
    }
