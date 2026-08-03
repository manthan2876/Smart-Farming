"""
retrain_v2.py
-------------
Retrains with EfficientNet-B2 + aggressive augmentation on the expanded dataset.
Reads from: processed_dataset/train  and  processed_dataset/val
Saves to:   models/crop_identifier_v2.pth

Run from: d:\Crop Identification Dataset\notebooks\
"""

import os
import sys
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import datasets, transforms
import timm
import numpy as np
from collections import Counter

# ── Config ────────────────────────────────────────────────────────────────────
DATASET_PATH   = "processed_dataset"
BATCH_SIZE     = 32
NUM_WORKERS    = 0           # Windows safe
LR             = 5e-5        # Lower LR for pretrained B2
EPOCHS         = 20
MODEL_PATH     = "models/crop_identifier_fine_tuned.pth"   # Start from fine-tuned B0
NEW_MODEL_PATH = "models/crop_identifier_v2.pth"
LOG_FILE       = "models/retrain_v2_log.txt"
IMG_SIZE       = 260         # EfficientNet-B2 native resolution

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Transforms — AGGRESSIVE augmentation for real-world robustness ─────────────
train_transform = transforms.Compose([
    transforms.Resize((300, 300)),
    transforms.RandomResizedCrop(IMG_SIZE, scale=(0.5, 1.0)),  # vary zoom level
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(p=0.1),
    transforms.ColorJitter(
        brightness=0.4, contrast=0.4,
        saturation=0.4, hue=0.15),            # strong color variation
    transforms.RandomGrayscale(p=0.08),       # occasional grayscale
    transforms.RandomPerspective(
        distortion_scale=0.3, p=0.4),         # simulate camera angle
    transforms.RandomAffine(
        degrees=20, translate=(0.15, 0.15),
        scale=(0.85, 1.15), shear=10),        # zoom, shift, shear
    transforms.GaussianBlur(
        kernel_size=5, sigma=(0.1, 2.0)),     # simulate depth-of-field blur
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    transforms.RandomErasing(
        p=0.2, scale=(0.02, 0.15)),           # randomly hide small patches
])

val_transform = transforms.Compose([
    transforms.Resize((300, 300)),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# ── Logging ───────────────────────────────────────────────────────────────────
def log(msg, fh=None):
    print(msg, flush=True)
    if fh:
        fh.write(msg + "\n")
        fh.flush()

# ── Weighted sampler (handle class imbalance) ─────────────────────────────────
def make_weighted_sampler(dataset):
    targets = [s[1] for s in dataset.samples]
    counts  = Counter(targets)
    weights = [1.0 / counts[t] for t in targets]
    return WeightedRandomSampler(weights, len(weights), replacement=True)

# ── Training / Validation ─────────────────────────────────────────────────────
def train_one_epoch(model, loader, criterion, optimizer, scaler, log_fh):
    model.train()
    running_loss = 0.0
    correct = 0
    total   = 0
    for idx, (images, labels) in enumerate(loader):
        images = images.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        with torch.amp.autocast('cuda'):
            outputs = model(images)
            loss    = criterion(outputs, labels)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        running_loss += loss.item()
        _, pred  = outputs.max(1)
        total   += labels.size(0)
        correct += pred.eq(labels).sum().item()
        if (idx + 1) % 50 == 0:
            log(f"  [batch {idx+1}/{len(loader)}] loss={running_loss/(idx+1):.4f}", log_fh)
    return running_loss / len(loader), 100.0 * correct / total


def validate(model, loader, criterion):
    model.eval()
    running_loss = 0.0
    correct = 0
    total   = 0
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            loss    = criterion(outputs, labels)
            running_loss += loss.item()
            _, pred  = outputs.max(1)
            total   += labels.size(0)
            correct += pred.eq(labels).sum().item()
    return running_loss / len(loader), 100.0 * correct / total


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    os.makedirs("models", exist_ok=True)
    log_fh = open(LOG_FILE, "w", buffering=1)

    log(f"Using device: {device}", log_fh)
    log("Loading datasets...", log_fh)

    train_dataset = datasets.ImageFolder(
        os.path.join(DATASET_PATH, "train"), transform=train_transform)
    val_dataset   = datasets.ImageFolder(
        os.path.join(DATASET_PATH, "val"),   transform=val_transform)

    class_names = train_dataset.classes
    log(f"Train: {len(train_dataset)} images | Val: {len(val_dataset)} images", log_fh)
    log(f"Classes ({len(class_names)}): {class_names}", log_fh)

    # Log per-class counts
    counts = Counter([s[1] for s in train_dataset.samples])
    for i, name in enumerate(class_names):
        log(f"  {name}: {counts[i]} train images", log_fh)

    sampler     = make_weighted_sampler(train_dataset)
    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE,
        sampler=sampler, num_workers=NUM_WORKERS, pin_memory=True)
    val_loader   = DataLoader(
        val_dataset,   batch_size=BATCH_SIZE,
        shuffle=False, num_workers=NUM_WORKERS, pin_memory=True)

    # ── Build EfficientNet-B2 with pretrained ImageNet weights ──────────────
    log("\nBuilding EfficientNet-B2 (pretrained=True)...", log_fh)
    model = timm.create_model(
        "efficientnet_b2", pretrained=True, num_classes=len(class_names))
    model.to(device)

    log(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}", log_fh)

    # ── Two-phase training ────────────────────────────────────────────────────
    # Phase 1 (epochs 1-5): Only train the classifier head (freeze backbone)
    log("\n--- Phase 1: Train head only (5 epochs, LR=1e-3) ---", log_fh)
    for param in model.parameters():
        param.requires_grad = False
    for param in model.get_classifier().parameters():
        param.requires_grad = True

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=1e-3, weight_decay=1e-4)
    scaler = torch.amp.GradScaler('cuda')

    best_loss = float('inf')

    for epoch in range(1, 6):
        start = time.time()
        log(f"\nEpoch {epoch}/5 (Phase 1) - training head...", log_fh)
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, scaler, log_fh)
        val_loss, val_acc     = validate(model, val_loader, criterion)
        elapsed = time.time() - start
        log(f"Epoch {epoch}/5 ({elapsed:.1f}s) | "
            f"Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | "
            f"Val Loss: {val_loss:.4f} Acc: {val_acc:.2f}%", log_fh)
        if val_loss < best_loss:
            best_loss = val_loss
            log(f"--> New best! Saving {NEW_MODEL_PATH} (val_loss={val_loss:.4f})", log_fh)
            torch.save({
                "model":     model.state_dict(),
                "best_loss": best_loss,
                "epoch":     epoch,
                "classes":   class_names,
                "arch":      "efficientnet_b2",
            }, NEW_MODEL_PATH)

    # Phase 2 (epochs 6-20): Unfreeze all, fine-tune with low LR
    log("\n--- Phase 2: Full fine-tuning (15 epochs, LR=5e-5) ---", log_fh)
    for param in model.parameters():
        param.requires_grad = True

    optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=15)

    for epoch in range(6, EPOCHS + 1):
        start = time.time()
        log(f"\nEpoch {epoch}/{EPOCHS} (Phase 2) - full fine-tune...", log_fh)
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, scaler, log_fh)
        val_loss, val_acc     = validate(model, val_loader, criterion)
        scheduler.step()
        elapsed = time.time() - start

        msg = (f"Epoch {epoch}/{EPOCHS} ({elapsed:.1f}s) | "
               f"Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | "
               f"Val Loss: {val_loss:.4f} Acc: {val_acc:.2f}%")
        log(msg, log_fh)

        if val_loss < best_loss:
            best_loss = val_loss
            log(f"--> New best! Saving {NEW_MODEL_PATH} (val_loss={val_loss:.4f})", log_fh)
            torch.save({
                "model":     model.state_dict(),
                "best_loss": best_loss,
                "epoch":     epoch,
                "classes":   class_names,
                "arch":      "efficientnet_b2",
            }, NEW_MODEL_PATH)
        else:
            log(f"    No improvement (best: {best_loss:.4f})", log_fh)

    log("\nTraining complete!", log_fh)
    log(f"Best val_loss: {best_loss:.4f}", log_fh)
    log(f"Model saved: {NEW_MODEL_PATH}", log_fh)
    log_fh.close()


if __name__ == "__main__":
    main()
