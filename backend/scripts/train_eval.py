#!/usr/bin/env python3
"""
train_eval.py — Smart Farming EfficientNet Fine-tuning Script
=============================================================

Full PyTorch training loop for fine-tuning EfficientNet-B0/B2 on the
Smart Farming disease/crop classification dataset.

Usage
-----
    # Train disease classifier for tomato (fine-tune EfficientNet-B2)
    python backend/scripts/train_eval.py disease \\
        --dataset-dir data/exports/dataset_export \\
        --model-name efficientnet_b2 \\
        --num-classes 10 \\
        --epochs 30 \\
        --batch-size 32 \\
        --lr 3e-4 \\
        --output-dir models/training_runs/tomato_disease_v2

    # Train crop identifier (fine-tune EfficientNet-B0)
    python backend/scripts/train_eval.py crop \\
        --dataset-dir data/exports/dataset_export \\
        --model-name efficientnet_b0 \\
        --num-classes 5 \\
        --epochs 20 \\
        --output-dir models/training_runs/crop_v2

    # Evaluate an existing model checkpoint
    python backend/scripts/train_eval.py eval \\
        --checkpoint models/training_runs/tomato_disease_v2/best.pth \\
        --dataset-dir data/exports/dataset_export \\
        --num-classes 10

Dataset structure expected (PyTorch ImageFolder):
    <dataset-dir>/
        images/
            train/<class_label>/<filename>.jpg
            val/<class_label>/<filename>.jpg
            test/<class_label>/<filename>.jpg

Requires
--------
    pip install torch torchvision tqdm scikit-learn matplotlib
    (optional) pip install psycopg2-binary sqlalchemy python-dotenv  # for DB logging
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from tqdm import tqdm

# ─── Optional DB logging ───────────────────────────────────────────────────────
_DB_AVAILABLE = False
try:
    import os
    from dotenv import load_dotenv

    _BACKEND_ROOT = Path(__file__).resolve().parents[1]
    load_dotenv(_BACKEND_ROOT / ".env")
    sys.path.insert(0, str(_BACKEND_ROOT / "src"))

    from app.core.session import _session_factory  # type: ignore
    from app.models.mlopsRun import MlopsRun  # type: ignore

    _DB_AVAILABLE = True
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("train_eval")

# ─── Hyperparameter defaults ────────────────────────────────────────────────────
DEFAULT_IMG_SIZE = 224
DEFAULT_LR = 3e-4
DEFAULT_WEIGHT_DECAY = 1e-4
DEFAULT_EPOCHS = 20
DEFAULT_BATCH_SIZE = 32
DEFAULT_WARMUP_EPOCHS = 2
DEFAULT_MIN_LR = 1e-6
DEFAULT_PATIENCE = 7  # early stopping patience


# ─── Transforms ─────────────────────────────────────────────────────────────────
def build_transforms(img_size: int) -> tuple[transforms.Compose, transforms.Compose]:
    """Return (train_transform, val_transform) for the given image size."""
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    train_tf = transforms.Compose([
        transforms.Resize((img_size + 32, img_size + 32)),
        transforms.RandomCrop(img_size),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.05),
        transforms.RandomRotation(degrees=20),
        transforms.RandomPerspective(distortion_scale=0.2, p=0.3),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
        transforms.RandomErasing(p=0.2, scale=(0.02, 0.15)),
    ])

    val_tf = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])

    return train_tf, val_tf


# ─── Model factory ──────────────────────────────────────────────────────────────
def build_model(model_name: str, num_classes: int, pretrained: bool = True) -> nn.Module:
    """Build an EfficientNet model with a custom classification head."""
    weights_map = {
        "efficientnet_b0": models.EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None,
        "efficientnet_b1": models.EfficientNet_B1_Weights.IMAGENET1K_V1 if pretrained else None,
        "efficientnet_b2": models.EfficientNet_B2_Weights.IMAGENET1K_V1 if pretrained else None,
        "efficientnet_b3": models.EfficientNet_B3_Weights.IMAGENET1K_V1 if pretrained else None,
    }
    if model_name not in weights_map:
        raise ValueError(f"Unsupported model '{model_name}'. Choose from: {list(weights_map)}")

    model_fn = getattr(models, model_name)
    model = model_fn(weights=weights_map[model_name])

    # Replace the classifier head
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_features, num_classes),
    )

    return model


# ─── Training helpers ────────────────────────────────────────────────────────────
def _accuracy(outputs: torch.Tensor, targets: torch.Tensor) -> float:
    _, predicted = torch.max(outputs, dim=1)
    return (predicted == targets).float().mean().item()


def _class_weights(dataset: datasets.ImageFolder, device: torch.device) -> torch.Tensor:
    """Compute inverse-frequency class weights to handle imbalanced datasets."""
    from collections import Counter
    counts = Counter(dataset.targets)
    total = sum(counts.values())
    n_classes = len(dataset.classes)
    weights = [total / (n_classes * counts.get(i, 1)) for i in range(n_classes)]
    return torch.tensor(weights, dtype=torch.float32, device=device)


def _freeze_backbone(model: nn.Module, freeze: bool = True) -> None:
    """Freeze/unfreeze all layers except the final classifier."""
    for name, param in model.named_parameters():
        if "classifier" not in name:
            param.requires_grad = not freeze


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
    scaler: torch.cuda.amp.GradScaler | None,
) -> tuple[float, float]:
    model.train()
    total_loss, total_acc = 0.0, 0.0

    for images, labels in tqdm(loader, desc="  train", leave=False):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()

        if scaler is not None:
            with torch.cuda.amp.autocast():
                outputs = model(images)
                loss = criterion(outputs, labels)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

        total_loss += loss.item()
        total_acc += _accuracy(outputs, labels)

    n = len(loader)
    return total_loss / n, total_acc / n


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float]:
    model.eval()
    total_loss, total_acc = 0.0, 0.0

    for images, labels in tqdm(loader, desc="  eval", leave=False):
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)
        total_loss += loss.item()
        total_acc += _accuracy(outputs, labels)

    n = len(loader)
    return total_loss / n, total_acc / n


# ─── DB logging helpers ──────────────────────────────────────────────────────────
def _db_create_run(model_name: str, total_epochs: int, export_config: dict | None) -> int | None:
    """Create a MlopsRun record and return its id."""
    if not _DB_AVAILABLE:
        return None
    try:
        session = _session_factory()()
        run = MlopsRun(
            model_name=model_name,
            status="running",
            total_epochs=total_epochs,
            dataset_export_config=export_config,
        )
        session.add(run)
        session.commit()
        run_id = run.id
        session.close()
        return run_id
    except Exception as exc:
        logger.warning("DB run creation failed: %s", exc)
        return None


def _db_update_run(
    run_id: int | None,
    epoch: int,
    status: str = "running",
    message: str = "",
    metrics: dict | None = None,
    finished: bool = False,
) -> None:
    if not _DB_AVAILABLE or run_id is None:
        return
    try:
        session = _session_factory()()
        run = session.get(MlopsRun, run_id)
        if run:
            run.epoch = epoch
            run.status = status
            run.message = message
            if metrics:
                run.metrics = metrics
            if finished:
                run.finished_at = datetime.now(timezone.utc)
        session.commit()
        session.close()
    except Exception as exc:
        logger.warning("DB run update failed: %s", exc)


# ─── Main training function ──────────────────────────────────────────────────────
def train(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Device: %s", device)
    if device.type == "cuda":
        logger.info("GPU: %s | VRAM: %.1f GB", torch.cuda.get_device_name(0),
                    torch.cuda.get_device_properties(0).total_memory / 1e9)

    # ── Datasets ────────────────────────────────────────────────────────────────
    data_root = Path(args.dataset_dir) / "images"
    train_tf, val_tf = build_transforms(args.img_size)

    logger.info("Loading datasets from %s", data_root)
    train_ds = datasets.ImageFolder(data_root / "train", transform=train_tf)
    val_ds   = datasets.ImageFolder(data_root / "val",   transform=val_tf)
    test_ds  = datasets.ImageFolder(data_root / "test",  transform=val_tf)

    num_classes = len(train_ds.classes)
    if args.num_classes and args.num_classes != num_classes:
        logger.warning(
            "--num-classes=%d does not match discovered class count=%d; using discovered count.",
            args.num_classes, num_classes,
        )
    args.num_classes = num_classes

    logger.info("Classes (%d): %s", num_classes, train_ds.classes)
    logger.info("Train: %d  |  Val: %d  |  Test: %d", len(train_ds), len(val_ds), len(test_ds))

    # Save class-to-index mapping
    class_to_idx = train_ds.class_to_idx
    labels_path = output_dir / "labels.json"
    labels_path.write_text(json.dumps({v: k for k, v in class_to_idx.items()}, indent=2))
    logger.info("Labels saved → %s", labels_path)

    train_loader = DataLoader(
        train_ds, batch_size=args.batch_size, shuffle=True,
        num_workers=args.num_workers, pin_memory=(device.type == "cuda"),
    )
    val_loader = DataLoader(
        val_ds, batch_size=args.batch_size * 2, shuffle=False,
        num_workers=args.num_workers, pin_memory=(device.type == "cuda"),
    )
    test_loader = DataLoader(
        test_ds, batch_size=args.batch_size * 2, shuffle=False,
        num_workers=args.num_workers, pin_memory=(device.type == "cuda"),
    )

    # ── Model ───────────────────────────────────────────────────────────────────
    logger.info("Building model: %s (num_classes=%d, pretrained=%s)",
                args.model_name, num_classes, not args.from_scratch)
    model = build_model(args.model_name, num_classes, pretrained=not args.from_scratch)

    if args.checkpoint:
        ckpt = torch.load(args.checkpoint, map_location="cpu")
        state = ckpt.get("model_state_dict", ckpt)
        model.load_state_dict(state, strict=False)
        logger.info("Loaded checkpoint: %s", args.checkpoint)

    model = model.to(device)

    # ── Loss ────────────────────────────────────────────────────────────────────
    class_weights = _class_weights(train_ds, device) if args.use_class_weights else None
    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.1)

    # ── Optimizer ───────────────────────────────────────────────────────────────
    # Two-phase: warm up with frozen backbone, then unfreeze for full fine-tuning
    _freeze_backbone(model, freeze=True)
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=args.lr, weight_decay=args.weight_decay,
    )
    # Cosine annealing with warmup
    scheduler = optim.lr_scheduler.OneCycleLR(
        optimizer,
        max_lr=args.lr,
        steps_per_epoch=len(train_loader),
        epochs=args.epochs,
        pct_start=args.warmup_epochs / args.epochs,
    )

    scaler = torch.cuda.amp.GradScaler() if device.type == "cuda" else None

    # ── DB run record ────────────────────────────────────────────────────────────
    export_config: dict | None = None
    config_path = Path(args.dataset_dir) / "metadata.json"
    if config_path.exists():
        try:
            export_config = json.loads(config_path.read_text())
        except Exception:
            pass

    run_id = _db_create_run(
        f"{args.task}:{args.model_name}",
        total_epochs=args.epochs,
        export_config=export_config,
    )

    # ── Training loop ────────────────────────────────────────────────────────────
    best_val_acc = 0.0
    best_val_loss = float("inf")
    epochs_no_improve = 0
    history: list[dict] = []
    run_start = time.time()

    logger.info("=" * 60)
    logger.info("Starting training — %d epochs", args.epochs)
    logger.info("=" * 60)

    for epoch in range(1, args.epochs + 1):
        epoch_start = time.time()

        # Unfreeze backbone after warmup
        if epoch == args.warmup_epochs + 1:
            logger.info("Epoch %d: unfreezing backbone", epoch)
            _freeze_backbone(model, freeze=False)
            # Rebuild optimizer so backbone layers get their own lower LR
            backbone_params = [p for n, p in model.named_parameters() if "classifier" not in n]
            head_params = [p for n, p in model.named_parameters() if "classifier" in n]
            optimizer = optim.AdamW([
                {"params": backbone_params, "lr": args.lr * 0.1},
                {"params": head_params, "lr": args.lr},
            ], weight_decay=args.weight_decay)
            scheduler = optim.lr_scheduler.CosineAnnealingLR(
                optimizer,
                T_max=args.epochs - args.warmup_epochs,
                eta_min=args.min_lr,
            )

        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device, scaler)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)

        if epoch > args.warmup_epochs:
            scheduler.step()

        epoch_time = time.time() - epoch_start
        current_lr = optimizer.param_groups[-1]["lr"]

        row = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(val_loss, 4),
            "val_acc": round(val_acc, 4),
            "lr": current_lr,
            "epoch_time_s": round(epoch_time, 1),
        }
        history.append(row)

        logger.info(
            "Epoch %3d/%d | train_loss=%.4f train_acc=%.4f | val_loss=%.4f val_acc=%.4f | lr=%.2e | %.1fs",
            epoch, args.epochs,
            train_loss, train_acc, val_loss, val_acc,
            current_lr, epoch_time,
        )

        # ── Save best checkpoint ────────────────────────────────────────────────
        improved = val_acc > best_val_acc or (val_acc == best_val_acc and val_loss < best_val_loss)
        if improved:
            best_val_acc = val_acc
            best_val_loss = val_loss
            epochs_no_improve = 0
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_acc": val_acc,
                "val_loss": val_loss,
                "num_classes": num_classes,
                "class_to_idx": class_to_idx,
                "model_name": args.model_name,
                "img_size": args.img_size,
            }, output_dir / "best.pth")
            logger.info("  ✓ Saved best.pth (val_acc=%.4f)", val_acc)
        else:
            epochs_no_improve += 1

        # ── Save latest checkpoint ─────────────────────────────────────────────
        torch.save({
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "val_acc": val_acc,
            "val_loss": val_loss,
        }, output_dir / "last.pth")

        # ── Update DB ─────────────────────────────────────────────────────────
        _db_update_run(run_id, epoch, status="running", message=f"Epoch {epoch}/{args.epochs}",
                       metrics={"val_acc": val_acc, "val_loss": val_loss, "train_acc": train_acc})

        # ── Early stopping ─────────────────────────────────────────────────────
        if epochs_no_improve >= args.patience:
            logger.info("Early stopping triggered (no improvement for %d epochs)", args.patience)
            break

    # ── Test evaluation ──────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("Loading best checkpoint for test evaluation")
    best_ckpt = torch.load(output_dir / "best.pth", map_location=device)
    model.load_state_dict(best_ckpt["model_state_dict"])
    test_loss, test_acc = evaluate(model, test_loader, criterion, device)
    logger.info("Test — loss=%.4f  acc=%.4f", test_loss, test_acc)

    # ── Per-class report ─────────────────────────────────────────────────────────
    logger.info("Computing per-class report…")
    all_preds, all_labels = [], []
    model.eval()
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images.to(device))
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.tolist())

    try:
        from sklearn.metrics import classification_report, confusion_matrix
        report = classification_report(all_labels, all_preds, target_names=train_ds.classes, output_dict=True)
        cm = confusion_matrix(all_labels, all_preds).tolist()
        logger.info("\n%s", classification_report(all_labels, all_preds, target_names=train_ds.classes))
    except ImportError:
        report = {}
        cm = []
        logger.warning("scikit-learn not installed; skipping classification report")

    total_time = time.time() - run_start

    # ── Save final metrics ───────────────────────────────────────────────────────
    final_metrics: dict[str, Any] = {
        "task": args.task,
        "model_name": args.model_name,
        "num_classes": num_classes,
        "classes": train_ds.classes,
        "img_size": args.img_size,
        "best_val_acc": round(best_val_acc, 4),
        "best_val_loss": round(best_val_loss, 4),
        "test_acc": round(test_acc, 4),
        "test_loss": round(test_loss, 4),
        "epochs_trained": len(history),
        "total_time_s": round(total_time, 1),
        "history": history,
        "per_class_report": report,
        "confusion_matrix": cm,
        "checkpoint": str(output_dir / "best.pth"),
        "labels_file": str(labels_path),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(json.dumps(final_metrics, indent=2))
    logger.info("Metrics saved → %s", metrics_path)

    # ── Final DB update ──────────────────────────────────────────────────────────
    _db_update_run(
        run_id,
        epoch=len(history),
        status="completed",
        message=f"Training complete. Test acc: {test_acc:.4f}",
        metrics=final_metrics,
        finished=True,
    )

    logger.info("=" * 60)
    logger.info("Training complete in %.1f minutes", total_time / 60)
    logger.info("Best val_acc=%.4f | Test acc=%.4f", best_val_acc, test_acc)
    logger.info("Checkpoint: %s", output_dir / "best.pth")
    logger.info("=" * 60)

    return final_metrics


# ─── Evaluate-only mode ──────────────────────────────────────────────────────────
def evaluate_only(args: argparse.Namespace) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Eval-only mode | device: %s", device)

    ckpt = torch.load(args.checkpoint, map_location=device)
    model_name = ckpt.get("model_name", args.model_name)
    num_classes = ckpt.get("num_classes", args.num_classes)
    img_size = ckpt.get("img_size", args.img_size)

    model = build_model(model_name, num_classes, pretrained=False)
    model.load_state_dict(ckpt["model_state_dict"])
    model = model.to(device)

    _, val_tf = build_transforms(img_size)
    data_root = Path(args.dataset_dir) / "images"
    test_ds = datasets.ImageFolder(data_root / "test", transform=val_tf)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size * 2, shuffle=False)

    criterion = nn.CrossEntropyLoss()
    test_loss, test_acc = evaluate(model, test_loader, criterion, device)
    logger.info("Test — loss=%.4f  acc=%.4f", test_loss, test_acc)

    # Per-class report
    all_preds, all_labels = [], []
    model.eval()
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images.to(device))
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.tolist())

    try:
        from sklearn.metrics import classification_report
        logger.info("\n%s", classification_report(all_labels, all_preds, target_names=test_ds.classes))
    except ImportError:
        pass


# ─── CLI ─────────────────────────────────────────────────────────────────────────
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Smart Farming — EfficientNet Training Script",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("task", choices=["disease", "crop", "eval"],
                        help="Task: 'disease' = disease classifier, 'crop' = crop identifier, 'eval' = evaluate checkpoint only")
    parser.add_argument("--dataset-dir", required=True,
                        help="Root of exported dataset (containing images/train, images/val, images/test)")
    parser.add_argument("--model-name", default="efficientnet_b2",
                        choices=["efficientnet_b0", "efficientnet_b1", "efficientnet_b2", "efficientnet_b3"],
                        help="EfficientNet variant to fine-tune")
    parser.add_argument("--num-classes", type=int, default=0,
                        help="Number of output classes (auto-detected from dataset if 0)")
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=DEFAULT_LR, help="Peak learning rate")
    parser.add_argument("--min-lr", type=float, default=DEFAULT_MIN_LR,
                        help="Minimum LR at end of cosine schedule")
    parser.add_argument("--weight-decay", type=float, default=DEFAULT_WEIGHT_DECAY)
    parser.add_argument("--warmup-epochs", type=int, default=DEFAULT_WARMUP_EPOCHS,
                        help="Epochs to train with frozen backbone before full fine-tuning")
    parser.add_argument("--patience", type=int, default=DEFAULT_PATIENCE,
                        help="Early stopping patience (epochs without val improvement)")
    parser.add_argument("--img-size", type=int, default=DEFAULT_IMG_SIZE,
                        help="Input image size (square)")
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--output-dir", default="models/training_runs/run",
                        help="Directory to save checkpoints and metrics")
    parser.add_argument("--checkpoint", default=None,
                        help="Path to an existing checkpoint to resume from or evaluate")
    parser.add_argument("--from-scratch", action="store_true",
                        help="Train from random initialization (no ImageNet weights)")
    parser.add_argument("--use-class-weights", action="store_true", default=True,
                        help="Use inverse-frequency class weights in loss function")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.task == "eval":
        if not args.checkpoint:
            parser.error("--checkpoint is required for eval mode")
        evaluate_only(args)
    else:
        metrics = train(args)
        # Print summary to stdout for CI pipelines
        print(json.dumps({
            "test_acc": metrics["test_acc"],
            "best_val_acc": metrics["best_val_acc"],
            "epochs_trained": metrics["epochs_trained"],
            "checkpoint": metrics["checkpoint"],
        }, indent=2))


if __name__ == "__main__":
    main()
