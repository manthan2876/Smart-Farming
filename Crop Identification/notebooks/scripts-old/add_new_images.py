"""
add_new_images.py
-----------------
Validates and merges newly downloaded images into processed_dataset/train.
Also updates the val split (10% of new images go to val).

Run from: d:\Crop Identification Dataset\notebooks\
Input:    d:\Crop Identification Dataset\new_images\<ClassName>\
Output:   processed_dataset/train/<ClassName>/  (and val/)
"""

import os
import sys
import shutil
import random
from PIL import Image

# ── Config ────────────────────────────────────────────────────────────────────
NEW_IMAGES_DIR   = r"d:\Crop Identification Dataset\new_images"
TRAIN_DIR        = "processed_dataset/train"
VAL_DIR          = "processed_dataset/val"
VAL_SPLIT        = 0.10     # 10% of new images → val
MIN_SIZE         = (64, 64) # reject images smaller than this
VALID_EXTS       = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

random.seed(42)

def is_valid_image(path):
    """Return True if the file is a valid, non-corrupt image above min size."""
    try:
        with Image.open(path) as img:
            img.verify()       # detect corruption
        with Image.open(path) as img:
            w, h = img.size
            if w < MIN_SIZE[0] or h < MIN_SIZE[1]:
                return False
        return True
    except Exception:
        return False

def count_existing(directory):
    """Count images already in a directory."""
    return len([f for f in os.listdir(directory)
                if os.path.splitext(f)[1].lower() in VALID_EXTS])

def get_next_index(directory, prefix):
    """Find the next available sequential index for naming."""
    existing = [f for f in os.listdir(directory)
                if f.startswith(prefix) and
                os.path.splitext(f)[1].lower() in VALID_EXTS]
    if not existing:
        return 1
    indices = []
    for f in existing:
        try:
            idx = int(os.path.splitext(f)[0].replace(prefix, ""))
            indices.append(idx)
        except ValueError:
            pass
    return max(indices) + 1 if indices else 1


def process_class(class_name):
    src_dir   = os.path.join(NEW_IMAGES_DIR, class_name)
    train_dst = os.path.join(TRAIN_DIR, class_name)
    val_dst   = os.path.join(VAL_DIR,   class_name)

    if not os.path.isdir(src_dir):
        print(f"  [{class_name}] No new_images folder found. Skipping.", flush=True)
        return 0, 0

    os.makedirs(train_dst, exist_ok=True)
    os.makedirs(val_dst,   exist_ok=True)

    # Gather all valid new images
    candidates = []
    raw_files  = [f for f in os.listdir(src_dir)
                  if os.path.splitext(f)[1].lower() in VALID_EXTS]

    print(f"\n[{class_name}] Validating {len(raw_files)} source images...", flush=True)

    for fname in raw_files:
        fpath = os.path.join(src_dir, fname)
        if is_valid_image(fpath):
            candidates.append(fpath)

    invalid = len(raw_files) - len(candidates)
    print(f"  Valid: {len(candidates)}  |  Rejected (corrupt/tiny): {invalid}", flush=True)

    if not candidates:
        print(f"  No valid images found for {class_name}.", flush=True)
        return 0, 0

    # Split into train / val
    random.shuffle(candidates)
    n_val   = max(1, int(len(candidates) * VAL_SPLIT))
    val_set = candidates[:n_val]
    trn_set = candidates[n_val:]

    prefix    = f"new_{class_name.lower()}_"
    trn_idx   = get_next_index(train_dst, prefix)
    val_idx   = get_next_index(val_dst,   prefix)

    # Copy train
    added_train = 0
    for src in trn_set:
        ext  = os.path.splitext(src)[1].lower()
        dst  = os.path.join(train_dst, f"{prefix}{trn_idx:04d}{ext}")
        shutil.copy2(src, dst)
        trn_idx   += 1
        added_train += 1

    # Copy val
    added_val = 0
    for src in val_set:
        ext = os.path.splitext(src)[1].lower()
        dst = os.path.join(val_dst, f"{prefix}{val_idx:04d}{ext}")
        shutil.copy2(src, dst)
        val_idx  += 1
        added_val += 1

    print(f"  Added to train: {added_train}  |  Added to val: {added_val}", flush=True)
    print(f"  Train total now: {count_existing(train_dst)}  |  "
          f"Val total now: {count_existing(val_dst)}", flush=True)
    return added_train, added_val


def main():
    print("=" * 60, flush=True)
    print("Add New Images to Training Dataset", flush=True)
    print("=" * 60, flush=True)

    if not os.path.isdir(NEW_IMAGES_DIR):
        print(f"ERROR: new_images directory not found at:\n  {NEW_IMAGES_DIR}", flush=True)
        print("Run download_images.py first!", flush=True)
        sys.exit(1)

    classes = [d for d in os.listdir(NEW_IMAGES_DIR)
               if os.path.isdir(os.path.join(NEW_IMAGES_DIR, d))]

    if not classes:
        print("No class folders found in new_images/. Nothing to add.", flush=True)
        sys.exit(1)

    print(f"Found classes: {classes}", flush=True)

    total_train = 0
    total_val   = 0
    for cls in sorted(classes):
        t, v = process_class(cls)
        total_train += t
        total_val   += v

    print("\n" + "=" * 60, flush=True)
    print(f"DONE! Added {total_train} images to train, {total_val} to val.", flush=True)
    print("Next step: run scripts/retrain_v2.py", flush=True)


if __name__ == "__main__":
    main()
