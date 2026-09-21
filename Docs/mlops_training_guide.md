# MLOps Training Guide — Smart Farming

This document explains how to reproduce a training run for either the **crop identifier** or the **disease classifier** models used by the Smart Farming backend.

---

## Prerequisites

### 1. Python environment

```bash
# Create a virtual environment (Python 3.10+)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install training dependencies
pip install torch torchvision tqdm scikit-learn matplotlib
pip install psycopg2-binary sqlalchemy python-dotenv  # for DB run logging
```

### 2. GPU (recommended)

Training works on CPU but is 10–20× slower. CUDA (NVIDIA GPU with ≥4 GB VRAM) is strongly recommended.

```bash
# Verify CUDA is available
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

---

## Step 1: Export the Dataset

Use the Admin dashboard or the API to export a labelled dataset:

```bash
# Via the API (requires admin token)
curl -X POST http://localhost:8000/admin/dataset/export \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {"expert": true, "farmer": true, "crop": null, "status": "pending_review"},
    "split": {"train": 70, "val": 15, "test": 15},
    "format": "PyTorch Folder",
    "imageTarget": "preprocessed"
  }' \
  --output dataset_export.zip

# Extract
unzip dataset_export.zip -d data/exports/latest
```

The extracted directory has this structure:

```
data/exports/latest/
├── images/
│   ├── train/
│   │   ├── Tomato_Early_Blight/
│   │   │   ├── 42_abc123.jpg
│   │   │   └── ...
│   │   └── Healthy/
│   ├── val/
│   └── test/
├── metadata.json        ← provenance block + all candidate details
├── export_config.json
└── README.md
```

---

## Step 2: Train

### Disease classifier (EfficientNet-B2)

```bash
python backend/scripts/train_eval.py disease \
    --dataset-dir data/exports/latest \
    --model-name efficientnet_b2 \
    --epochs 30 \
    --batch-size 32 \
    --lr 3e-4 \
    --warmup-epochs 3 \
    --patience 7 \
    --use-class-weights \
    --output-dir models/training_runs/disease_v2
```

### Crop identifier (EfficientNet-B0)

```bash
python backend/scripts/train_eval.py crop \
    --dataset-dir data/exports/latest \
    --model-name efficientnet_b0 \
    --epochs 20 \
    --batch-size 32 \
    --lr 2e-4 \
    --warmup-epochs 2 \
    --output-dir models/training_runs/crop_v2
```

---

## Step 3: Review Results

After training completes, the output directory contains:

```
models/training_runs/disease_v2/
├── best.pth        ← best checkpoint by val_acc
├── last.pth        ← latest epoch checkpoint
├── labels.json     ← index → class label mapping
└── metrics.json    ← full training history + test results
```

`metrics.json` includes:

| Field | Description |
|---|---|
| `best_val_acc` | Best validation accuracy during training |
| `test_acc` | Accuracy on the held-out test set |
| `epochs_trained` | Actual epochs before early stopping |
| `per_class_report` | Precision, recall, F1 per class |
| `confusion_matrix` | Class-wise confusion matrix |
| `history` | Per-epoch train/val loss and accuracy |

---

## Step 4: Evaluate an Existing Checkpoint

```bash
python backend/scripts/train_eval.py eval \
    --checkpoint models/training_runs/disease_v2/best.pth \
    --dataset-dir data/exports/latest
```

---

## Step 5: Promote a New Model

Once satisfied with evaluation metrics, promote the checkpoint to production:

```bash
# Via the model registry API (requires admin token)
curl -X POST http://localhost:8000/admin/models/promote \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_key": "tomato_disease",
    "version": "v2.0",
    "checkpoint_path": "models/training_runs/disease_v2/best.pth",
    "labels_path": "models/training_runs/disease_v2/labels.json",
    "val_acc": 0.923,
    "test_acc": 0.917,
    "notes": "Retrained on expert-corrected dataset with 120 new samples"
  }'
```

This updates `config.yaml` and `model_registry.json` atomically.

---

## Training Script Options

| Flag | Default | Description |
|---|---|---|
| `--model-name` | `efficientnet_b2` | EfficientNet variant (`b0`, `b1`, `b2`, `b3`) |
| `--epochs` | `20` | Maximum training epochs |
| `--batch-size` | `32` | Training batch size |
| `--lr` | `3e-4` | Peak learning rate (AdamW) |
| `--min-lr` | `1e-6` | Minimum LR at end of cosine schedule |
| `--warmup-epochs` | `2` | Epochs with frozen backbone (head-only training) |
| `--patience` | `7` | Early stopping patience |
| `--img-size` | `224` | Input image size (square) |
| `--use-class-weights` | enabled | Inverse-frequency class weights for imbalanced data |
| `--from-scratch` | disabled | Disable ImageNet pretrained weights |
| `--checkpoint` | — | Resume from or evaluate an existing checkpoint |

---

## Two-Phase Training Strategy

The script uses a deliberate two-phase approach to prevent catastrophic forgetting:

1. **Warmup phase** (`--warmup-epochs`): Only the classifier head is trained. The backbone (EfficientNet feature extractor) is frozen. This stabilises the head before the backbone gradients flow.
2. **Fine-tuning phase**: All layers are unfrozen. The backbone gets a 10× lower learning rate than the head. A cosine annealing schedule decays LR smoothly to `--min-lr`.

---

## Reproducibility Checklist

- [ ] Note the `exported_at` timestamp from `metadata.json` to identify the exact dataset version.
- [ ] Record `model_name`, `epochs`, `lr`, `batch_size` from `metrics.json`.
- [ ] Store `best.pth` and `labels.json` in version control or a model store.
- [ ] Register the model via the `/admin/models/promote` endpoint to update `model_registry.json`.
- [ ] Run the test evaluation (`eval` mode) before promoting to production.
