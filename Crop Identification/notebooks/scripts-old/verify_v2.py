"""
verify_v2.py
------------
Tests the v2 model (EfficientNet-B2) on:
  1. All images in test_images/
  2. The newly downloaded iNaturalist images (a sample)

Uses Test-Time Augmentation (TTA) for more reliable predictions.

Run from: d:\Crop Identification Dataset\notebooks\
"""

import os
import sys
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import timm

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_PATH   = "models/crop_identifier_v2.pth"
TEST_DIR     = "test_images"
INAT_DIR     = r"d:\Crop Identification Dataset\new_images"
IMG_SIZE     = 260
DEVICE       = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Transforms ────────────────────────────────────────────────────────────────
base_transform = transforms.Compose([
    transforms.Resize((300, 300)),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# TTA: 5 crops (center + 4 corners) + horizontal flip
tta_transforms = [
    transforms.Compose([
        transforms.Resize((300, 300)),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    transforms.Compose([
        transforms.Resize((300, 300)),
        transforms.CenterCrop(IMG_SIZE),
        transforms.RandomHorizontalFlip(p=1.0),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    transforms.Compose([
        transforms.Resize((320, 320)),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    transforms.Compose([
        transforms.Resize((290, 290)),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
]

# ── Load model ────────────────────────────────────────────────────────────────
def load_model():
    print(f"Loading model: {MODEL_PATH}", flush=True)
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model not found at {MODEL_PATH}", flush=True)
        print("Run scripts/retrain_v2.py first!", flush=True)
        sys.exit(1)

    checkpoint  = torch.load(MODEL_PATH, map_location=DEVICE)
    class_names = checkpoint.get("classes", [])
    arch        = checkpoint.get("arch", "efficientnet_b2")

    print(f"  Architecture: {arch}", flush=True)
    print(f"  Classes: {class_names}", flush=True)

    model = timm.create_model(arch, pretrained=False, num_classes=len(class_names))
    model.load_state_dict(checkpoint["model"])
    model.to(DEVICE)
    model.eval()
    return model, class_names

# ── Predict with TTA ──────────────────────────────────────────────────────────
def predict_tta(model, class_names, img_path):
    try:
        img = Image.open(img_path).convert("RGB")
    except Exception as e:
        return None, 0.0, [], str(e)

    # Average predictions across all TTA transforms
    all_probs = []
    for tfm in tta_transforms:
        tensor = tfm(img).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            logits = model(tensor)
            probs  = F.softmax(logits, dim=1)[0]
        all_probs.append(probs)

    avg_probs    = torch.stack(all_probs).mean(0)
    top_prob, top_idx = avg_probs.topk(3)
    top3       = [(class_names[i], f"{p*100:.1f}%")
                  for i, p in zip(top_idx.tolist(), top_prob.tolist())]
    pred_class = class_names[top_idx[0]]
    confidence = top_prob[0].item() * 100
    return pred_class, confidence, top3, None


# ── Test a folder of images ────────────────────────────────────────────────────
def test_folder(model, class_names, folder, expected_label=None, max_images=10):
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    files = sorted([
        os.path.join(folder, f) for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in exts
    ])[:max_images]

    correct = 0
    for img_path in files:
        pred, conf, top3, err = predict_tta(model, class_names, img_path)
        fname = os.path.basename(img_path)
        if err:
            print(f"  {fname:<40} ERROR: {err}", flush=True)
            continue
        top3_str = " | ".join(f"{c}:{p}" for c, p in top3)
        if expected_label:
            status = "OK" if pred == expected_label else "WRONG"
            if pred == expected_label:
                correct += 1
            print(f"  [{status}] {fname:<35} => {pred:<15} ({conf:.1f}%)  [{top3_str}]", flush=True)
        else:
            print(f"  {fname:<40} => {pred:<15} ({conf:.1f}%)", flush=True)

    return correct, len(files)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    model, class_names = load_model()

    # 1. Test local test_images/
    print("\n" + "=" * 65, flush=True)
    print("1. TESTING test_images/ FOLDER (with TTA)", flush=True)
    print("=" * 65, flush=True)

    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    local_files = sorted([
        os.path.join(TEST_DIR, f) for f in os.listdir(TEST_DIR)
        if os.path.splitext(f)[1].lower() in exts
    ])

    total_correct = 0
    for img_path in local_files:
        fname      = os.path.basename(img_path)
        # Infer expected class from filename (e.g. "bellpepper.jpg" -> "BellPepper")
        stem       = os.path.splitext(fname)[0].lower().replace("_", "").replace(" ", "")
        expected   = None
        for cls in class_names:
            if cls.lower() in stem:
                expected = cls
                break

        pred, conf, top3, err = predict_tta(model, class_names, img_path)
        if err:
            print(f"  {fname:<35}  ERROR: {err}", flush=True)
            continue

        top3_str = " | ".join(f"{c}:{p}" for c, p in top3)
        if expected:
            status = "CORRECT" if pred == expected else "WRONG  "
            if pred == expected:
                total_correct += 1
            print(f"  [{status}] {fname:<30} => {pred:<15} ({conf:.1f}%)", flush=True)
            print(f"    Top-3: {top3_str}", flush=True)
        else:
            print(f"  [?????] {fname:<30} => {pred:<15} ({conf:.1f}%)", flush=True)
            print(f"    Top-3: {top3_str}", flush=True)

    labeled = sum(1 for f in local_files
                  if any(cls.lower() in os.path.splitext(os.path.basename(f))[0].lower()
                         for cls in class_names))
    if labeled > 0:
        print(f"\nAccuracy on test_images/: {total_correct}/{labeled} = "
              f"{100*total_correct/labeled:.1f}%", flush=True)

    # 2. Test 5 sample iNaturalist images per class
    print("\n" + "=" * 65, flush=True)
    print("2. TESTING INATURALIST DOWNLOADED IMAGES (5 per class)", flush=True)
    print("=" * 65, flush=True)

    if not os.path.isdir(INAT_DIR):
        print(f"  iNaturalist directory not found: {INAT_DIR}", flush=True)
        print("  Run scripts/download_images.py first.", flush=True)
    else:
        total_c = 0
        total_t = 0
        for cls in sorted(class_names):
            cls_dir = os.path.join(INAT_DIR, cls)
            if not os.path.isdir(cls_dir):
                print(f"\n  [{cls}] No directory found.", flush=True)
                continue
            print(f"\n  [{cls}]", flush=True)
            c, t = test_folder(model, class_names, cls_dir,
                               expected_label=cls, max_images=5)
            total_c += c
            total_t += t

        if total_t > 0:
            print(f"\nOverall iNaturalist accuracy: {total_c}/{total_t} = "
                  f"{100*total_c/total_t:.1f}%", flush=True)

    print("\nDone!", flush=True)


if __name__ == "__main__":
    main()
