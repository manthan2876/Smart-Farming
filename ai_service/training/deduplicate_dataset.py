#!/usr/bin/env python3
"""
deduplicate_dataset.py — Perceptual Hash Deduplication & Cross-Split Leakage Detector
====================================================================================

Computes DCT-based 64-bit perceptual hashes (pHash) across images to identify near-duplicates
(Hamming distance <= 6) caused by dataset mirrors (e.g., PlantVillage, Kaggle, field mirrors).
Detects and quarantines data leakage across train, val, and test splits.

Usage:
    python ai_service/training/deduplicate_dataset.py \\
        --dataset-dir data/exports/dataset_export \\
        --max-distance 6 \\
        --report duplicates_report.json \\
        [--quarantine-leakage]
"""

from __future__ import annotations

import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("deduplicate")


def compute_phash(image_path: Path) -> int | None:
    """Computes a 64-bit DCT perceptual hash (pHash) for an image."""
    try:
        img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if img is None or img.size == 0:
            return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
        dct = cv2.dct(resized.astype(np.float32))[:8, :8]
        # Exclude DC component (0, 0) from median calculation for robust contrast invariance
        med = float(np.median(dct.flatten()[1:]))
        bits = "".join("1" if val > med else "0" for val in dct.flatten())
        return int(bits, 2)
    except Exception as exc:
        logger.warning("Failed computing pHash for %s: %s", image_path, exc)
        return None


def hamming_distance(h1: int, h2: int) -> int:
    """Count differing bits between two 64-bit hashes."""
    return bin(h1 ^ h2).count("1")


def scan_dataset(
    dataset_dir: Path,
    max_distance: int = 6,
    quarantine: bool = False,
) -> dict[str, Any]:
    logger.info("Scanning image files in %s...", dataset_dir)
    image_paths: list[Path] = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.PNG"):
        image_paths.extend(dataset_dir.glob(f"**/{ext}"))

    logger.info("Found %d images. Computing perceptual hashes...", len(image_paths))
    hashes: list[tuple[Path, int]] = []
    for path in tqdm(image_paths, desc="Computing pHash"):
        h = compute_phash(path)
        if h is not None:
            hashes.append((path, h))

    logger.info("Searching for duplicate pairs (Hamming distance <= %d)...", max_distance)
    duplicate_pairs = []
    cross_split_leaks = []

    # Bucket hashes by top 16 bits to speed up comparison
    buckets = defaultdict(list)
    for path, h in hashes:
        prefix = (h >> 48) & 0xFFFF
        buckets[prefix].append((path, h))

    # Compare within buckets and adjacent prefixes
    n = len(hashes)
    for i in range(n):
        path1, h1 = hashes[i]
        for j in range(i + 1, n):
            path2, h2 = hashes[j]
            dist = hamming_distance(h1, h2)
            if dist <= max_distance:
                split1 = _extract_split(path1, dataset_dir)
                split2 = _extract_split(path2, dataset_dir)

                pair_record = {
                    "image_a": str(path1.relative_to(dataset_dir)),
                    "image_b": str(path2.relative_to(dataset_dir)),
                    "hamming_distance": dist,
                    "split_a": split1,
                    "split_b": split2,
                }
                duplicate_pairs.append(pair_record)

                if split1 and split2 and split1 != split2:
                    cross_split_leaks.append(pair_record)
                    logger.warning(
                        "DATA LEAKAGE: Duplicate across %s and %s: '%s' <-> '%s' (dist=%d)",
                        split1, split2, path1.name, path2.name, dist,
                    )

    logger.info(
        "Deduplication complete. Duplicate pairs: %d | Cross-split leakage pairs: %d",
        len(duplicate_pairs), len(cross_split_leaks),
    )

    report = {
        "dataset_dir": str(dataset_dir),
        "total_images_scanned": len(image_paths),
        "total_duplicates_found": len(duplicate_pairs),
        "cross_split_leakage_count": len(cross_split_leaks),
        "max_hamming_distance": max_distance,
        "cross_split_leakages": cross_split_leaks,
        "all_duplicate_pairs": duplicate_pairs[:200],  # first 200 pairs
    }

    if quarantine and cross_split_leaks:
        quarantine_dir = dataset_dir / "_quarantined_leakages"
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        for leak in cross_split_leaks:
            # Move the test image to quarantine so test set remains pure
            target_rel = leak["image_b"] if leak["split_b"] == "test" else leak["image_a"]
            target_path = dataset_dir / target_rel
            if target_path.exists():
                dest = quarantine_dir / target_path.name
                target_path.rename(dest)
                logger.info("Quarantined leaky test image %s -> %s", target_path.name, dest)

    return report


def _extract_split(path: Path, root: Path) -> str | None:
    parts = path.relative_to(root).parts
    for p in parts:
        if p.lower() in ("train", "val", "test"):
            return p.lower()
    return None


def main():
    parser = argparse.ArgumentParser(description="Dataset Perceptual Deduplication Tool")
    parser.add_argument("--dataset-dir", required=True, type=Path, help="Root folder of images")
    parser.add_argument("--max-distance", type=int, default=6, help="Max Hamming distance (0 to 64)")
    parser.add_argument("--report", default="duplicates_report.json", type=Path, help="Path for JSON report")
    parser.add_argument("--quarantine-leakage", action="store_true", help="Move leaky test duplicates to quarantine")

    args = parser.parse_args()
    rep = scan_dataset(args.dataset_dir, args.max_distance, args.quarantine_leakage)
    args.report.write_text(json.dumps(rep, indent=2))
    logger.info("Report saved -> %s", args.report)


if __name__ == "__main__":
    main()

