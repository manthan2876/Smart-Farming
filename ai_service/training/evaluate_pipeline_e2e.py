#!/usr/bin/env python3
"""
evaluate_pipeline_e2e.py — Joint End-to-End Pipeline Evaluation
================================================================

Simulates realistic multi-stage deployment conditions to evaluate compounding pipeline accuracy:
    Accuracy_joint = P(Correct Disease | Correct Crop) * P(Correct Crop)

Also measures:
    - Preprocessing quality gate pass rate
    - Out-Of-Distribution (OOD) rejection fidelity
    - Uncertain-crop dual-run resolution rate
    - End-to-end inference latency percentiles (p50, p95)

Dataset directory format:
    <dataset_dir>/
        <Crop>/
            <Disease>/
                <filename>.jpg
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("eval_e2e")


def run_e2e_evaluation(dataset_dir: Path, report_path: Path | None = None) -> dict[str, Any]:
    from vision_engine.pipeline import run_vision_pipeline

    logger.info("Discovering evaluation images from %s...", dataset_dir)
    image_entries = []
    for img_path in dataset_dir.glob("*/*/*.*"):
        if img_path.suffix.lower() in (".jpg", ".jpeg", ".png"):
            crop_gt = img_path.parent.parent.name
            disease_gt = img_path.parent.name
            image_entries.append((img_path, crop_gt, disease_gt))

    total_images = len(image_entries)
    logger.info("Found %d annotated images across crop and disease folders.", total_images)
    if total_images == 0:
        logger.warning("No images found. Please provide a valid dataset directory.")
        return {"total_images": 0}

    prep_passed = 0
    crop_correct = 0
    disease_correct_given_crop = 0
    joint_correct = 0
    dual_run_invocations = 0
    ood_rejections = 0
    latencies_ms = []

    for img_path, crop_gt, disease_gt in image_entries:
        im_bgr = cv2.imread(str(img_path))
        if im_bgr is None:
            continue

        t0 = time.perf_counter()
        res = run_vision_pipeline(im_bgr, filename=img_path.name)
        latencies_ms.append((time.perf_counter() - t0) * 1000)

        # 1. Preprocessing Gate
        if res.get("status", {}).get("preprocessing") != "completed":
            continue
        prep_passed += 1

        # 2. Crop Accuracy
        pred_crop = res.get("crop", {}).get("label") or ""
        crop_match = (pred_crop.strip().lower() == crop_gt.strip().lower())
        if crop_match:
            crop_correct += 1

        if res.get("crop", {}).get("is_uncertain_band"):
            dual_run_invocations += 1

        if res.get("crop", {}).get("status") == "out_of_distribution":
            ood_rejections += 1

        # 3. Disease Accuracy
        pred_disease = res.get("disease", {}).get("label") or ""
        # Check normalized match
        clean_gt = disease_gt.replace("_", " ").strip().lower()
        clean_pred = pred_disease.replace("_", " ").strip().lower()
        disease_match = (clean_gt in clean_pred or clean_pred in clean_gt)

        if crop_match and disease_match:
            disease_correct_given_crop += 1
            joint_correct += 1

    prep_rate = prep_passed / total_images if total_images else 0.0
    crop_acc = crop_correct / prep_passed if prep_passed else 0.0
    disease_cond_acc = disease_correct_given_crop / crop_correct if crop_correct else 0.0
    joint_acc = joint_correct / total_images if total_images else 0.0

    p50_lat = np.percentile(latencies_ms, 50) if latencies_ms else 0.0
    p95_lat = np.percentile(latencies_ms, 95) if latencies_ms else 0.0

    report = {
        "dataset_dir": str(dataset_dir),
        "total_images": total_images,
        "preprocessing_pass_rate": round(prep_rate, 4),
        "crop_identification_accuracy": round(crop_acc, 4),
        "disease_accuracy_given_correct_crop": round(disease_cond_acc, 4),
        "joint_pipeline_accuracy": round(joint_acc, 4),
        "dual_run_uncertain_crop_invocations": dual_run_invocations,
        "out_of_distribution_rejections": ood_rejections,
        "latency_p50_ms": round(float(p50_lat), 1),
        "latency_p95_ms": round(float(p95_lat), 1),
    }

    logger.info("=" * 60)
    logger.info("End-to-End Joint Pipeline Evaluation Results:")
    logger.info("  Total Images:                  %d", total_images)
    logger.info("  Quality Gate Pass Rate:        %.2f%%", prep_rate * 100)
    logger.info("  Crop Accuracy P(Crop):         %.2f%%", crop_acc * 100)
    logger.info("  Disease Accuracy P(Dis|Crop):  %.2f%%", disease_cond_acc * 100)
    logger.info("  Joint End-to-End Accuracy:     %.2f%%", joint_acc * 100)
    logger.info("  Latency (p50 / p95):           %.1f ms / %.1f ms", p50_lat, p95_lat)
    logger.info("=" * 60)

    if report_path:
        report_path.write_text(json.dumps(report, indent=2))
        logger.info("E2E Report saved -> %s", report_path)

    return report


def main():
    parser = argparse.ArgumentParser(description="End-to-End Vision Pipeline Evaluation")
    parser.add_argument("--dataset-dir", required=True, type=Path, help="Annotated multi-crop dataset folder")
    parser.add_argument("--report", default="pipeline_e2e_report.json", type=Path, help="Output report JSON")
    args = parser.parse_args()

    run_e2e_evaluation(args.dataset_dir, args.report)


if __name__ == "__main__":
    main()

