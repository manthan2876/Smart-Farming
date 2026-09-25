# MLOps & Retraining Guide — AI-Powered Smart Farming

**Project:** AI-Powered Smart Farming  
**Version:** 1.0  
**Date:** September 2026  
**Status:** Active / Production Reference  

---

## Table of Contents

1. [Overview — The Closed Feedback Loop](#1-overview--the-closed-feedback-loop)
2. [The DatasetCandidate Table](#2-the-datasetcandidate-table)
3. [Drift Monitoring via Admin Metrics](#3-drift-monitoring-via-admin-metrics)
4. [Prerequisites](#4-prerequisites)
5. [Step 1 — Export the Dataset](#5-step-1--export-the-dataset)
6. [Step 2 — Train](#6-step-2--train)
7. [Two-Phase Training Strategy](#7-two-phase-training-strategy)
8. [Training Script Reference](#8-training-script-reference)
9. [Step 3 — Review Training Output](#9-step-3--review-training-output)
10. [Step 4 — Evaluate](#10-step-4--evaluate)
11. [Step 5 — Promote to Production](#11-step-5--promote-to-production)
12. [Reproducibility Checklist](#12-reproducibility-checklist)
13. [Migration to S3 (Production Model Storage)](#13-migration-to-s3-production-model-storage)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Overview — The Closed Feedback Loop

The MLOps pipeline for Smart Farming is a **continuous, closed feedback loop** that converts real-world prediction errors into improved models — automatically and with full audit trails.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SMART FARMING MLOps LOOP                        │
│                                                                     │
│  ┌──────────┐   diagnosis    ┌──────────────┐                       │
│  │  Farmer  │ ──────────────►│  Prediction  │                       │
│  │  App     │                │  Engine      │                       │
│  │          │◄──────────────  (EfficientNet)│                       │
│  └────┬─────┘  thumbs up/dn  └──────┬───────┘                       │
│       │                             │ low-confidence                │
│       │ feedback logged             │ or flagged                    │
│       ▼                             ▼                               │
│  ┌──────────────┐         ┌──────────────────┐                      │
│  │   Farmer     │         │  Expert Review   │                      │
│  │   Feedback   │         │  Queue           │                      │
│  │   Records    │         │                  │                      │
│  └──────┬───────┘         └────────┬─────────┘                      │
│         │ approved by expert       │ expert corrects label          │
│         ▼                          ▼                                │
│  ┌──────────────────────────────────────────────────────┐           │
│  │              DatasetCandidate Table                  │           │
│  │  (source: farmer_feedback_review | expert_correction)│           │
│  └──────────────────────┬───────────────────────────────┘           │
│                          │ admin exports                            │
│                          ▼                                          │
│  ┌──────────────┐   ┌─────────────┐   ┌──────────────┐              │
│  │  train_eval  │   │  Model      │   │  Redis       │              │
│  │  .py         │──►│  Registry   │──►│  Hot-Reload  │              │
│  │  (training)  │   │  API        │   │  (workers)   │              │
│  └──────────────┘   └─────────────┘   └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

### Pipeline Stages at a Glance

| Stage | Actor | Output |
|---|---|---|
| **1. Farmer submits feedback** | Farmer | `thumbs_up` / `thumbs_down` on diagnosis |
| **2. Expert review** | Domain expert | Corrected disease label |
| **3. Candidate logging** | System | `DatasetCandidate` record created |
| **4. Admin export** | Admin | Labelled dataset ZIP |
| **5. Training** | ML engineer | `best.pth` checkpoint |
| **6. Evaluation & promotion** | ML engineer + Admin | `model_registry.json` updated |
| **7. Hot-reload** | System (Redis) | Workers pick up new model, no restart |

---

## 2. The DatasetCandidate Table

Every expert correction — or expert-approved farmer feedback — creates a `DatasetCandidate` record. These records are the **ground-truth audit trail** that feeds the retraining pipeline.

### Schema

| Column | Type | Description |
|---|---|---|
| `prediction_id` | UUID | The prediction being corrected |
| `source` | enum | `expert_correction` \| `farmer_feedback_review` |
| `original_label` | string | What the current model predicted |
| `corrected_label` | string | The expert's verified label |
| `image_path` | string | Path to the raw image file |
| `status` | enum | `pending_review` \| `approved` \| `rejected` |
| `provenance_note` | string | Free-text audit trail (e.g., "Confirmed Early Blight by visual inspection") |
| `created_at` | timestamp | When the candidate was created |
| `reviewed_by` | UUID | Expert user ID (if applicable) |

### Candidate Sources

- **`expert_correction`** — An expert directly overrides a model prediction in the review queue (highest trust, always approved by default).
- **`farmer_feedback_review`** — A farmer marked a diagnosis as wrong; an expert then reviews and approves or rejects that feedback before it enters the candidate pool.

### Monitoring Candidate Growth

```bash
# Quick count via the admin metrics endpoint
curl -s http://localhost:8000/admin/metrics \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  | python -m json.tool | grep retraining_candidates
```

A growing `retraining_candidates` count (e.g., > 100 new records since the last training run) is a strong signal that retraining is warranted.

---

## 3. Drift Monitoring via Admin Metrics

The `GET /admin/metrics` endpoint exposes real-time drift signals that help you decide **when** to retrain.

```bash
curl http://localhost:8000/admin/metrics \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  | python -m json.tool
```

### Key Drift Indicators

| Metric | Description | Retrain if… |
|---|---|---|
| `avg_disease_confidence_7d` | 7-day rolling average model confidence for disease predictions | drops below **0.75** consistently |
| `avg_disease_confidence_30d` | 30-day rolling average | meaningful gap vs. 7-day avg |
| `low_confidence_rate_7d` | % of disease predictions below the confidence threshold in last 7 days | rises above **15 %** |
| `expert_correction_rate` | % of expert reviews that resulted in a label change | rises above **20 %** |
| `retraining_candidates` | Count of `DatasetCandidate` records in `pending_review` | exceeds **100** new records |

### Interpreting Drift

```
Confidence drops + high correction rate  →  The model is systematically wrong
                                            on a class (new disease variant? new crop season?)

Confidence drops + low correction rate   →  Image quality issue or new camera / input
                                            distribution shift — investigate preprocessing

Correction rate high + confidence OK     →  Label noise in historical data or a rare
                                            class appearing for the first time
```

> **Tip:** Review the 7-day vs. 30-day confidence gap weekly. A sudden drop in `avg_disease_confidence_7d` against a stable `avg_disease_confidence_30d` often indicates a seasonal distribution shift (e.g., monsoon-season disease patterns).

---

## 4. Prerequisites

### 4.1 Python Environment

```bash
# Create a virtual environment (Python 3.10+)
python -m venv .venv

# Activate
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows PowerShell

# Install training dependencies
pip install torch torchvision tqdm scikit-learn matplotlib
pip install psycopg2-binary sqlalchemy python-dotenv  # for DB run logging
```

### 4.2 GPU (Strongly Recommended)

Training on CPU is possible but **10–20× slower**. An NVIDIA GPU with ≥ 4 GB VRAM is recommended for development; ≥ 8 GB for production runs.

```bash
# Verify CUDA availability
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

### 4.3 Environment Variables

Ensure the following are set in your `.env` (or shell session) before running any admin API calls:

```bash
export ADMIN_TOKEN="<your-admin-jwt>"
export STORAGE_BACKEND="local"          # or "s3" after migration
export DATABASE_URL="postgresql://..."
```

---

## 5. Step 1 — Export the Dataset

Export approved `DatasetCandidate` records as a labelled image dataset using the Admin API.

```bash
curl -X POST http://localhost:8000/admin/dataset/export \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "expert": true,
      "farmer": true,
      "crop": null,
      "status": "pending_review"
    },
    "split": {"train": 70, "val": 15, "test": 15},
    "format": "PyTorch Folder",
    "imageTarget": "preprocessed"
  }' \
  --output dataset_export.zip

# Extract to a versioned directory
unzip dataset_export.zip -d data/exports/latest
```

### Export Filter Options

| Filter Key | Values | Notes |
|---|---|---|
| `expert` | `true` / `false` | Include expert-correction candidates |
| `farmer` | `true` / `false` | Include farmer-feedback-reviewed candidates |
| `crop` | `null` \| `"tomato"` \| `"wheat"` … | Filter by crop type (null = all) |
| `status` | `"pending_review"` \| `"approved"` | `pending_review` includes unprocessed candidates |
| `imageTarget` | `"raw"` \| `"preprocessed"` | Use `preprocessed` for consistency with production pipeline |

### Exported Directory Structure

```
data/exports/latest/
├── images/
│   ├── train/
│   │   ├── Tomato_Early_Blight/
│   │   │   ├── 42_abc123.jpg
│   │   │   └── ...
│   │   ├── Tomato_Late_Blight/
│   │   └── Healthy/
│   ├── val/
│   │   └── {class_name}/{image}.jpg
│   └── test/
│       └── {class_name}/{image}.jpg
├── metadata.json        ← provenance block + all candidate details
├── export_config.json   ← filters and split config used
└── README.md            ← auto-generated data card
```

> **Important:** Record the `exported_at` timestamp from `metadata.json` immediately. This is your dataset version identifier and is required for the [Reproducibility Checklist](#12-reproducibility-checklist).

---

## 6. Step 2 — Train

### 6.1 Disease Classifier (EfficientNet-B2)

The disease classifier is the primary model. EfficientNet-B2 balances accuracy and inference speed well for the 38-class disease taxonomy used in this project.

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

### 6.2 Crop Identifier (EfficientNet-B0)

The crop identifier is a lighter model (EfficientNet-B0) since crop classification is a simpler, lower-cardinality task.

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

### 6.3 Training Progress

The script logs per-epoch metrics to stdout in a structured format and writes running history to `metrics.json`. Monitor progress:

```bash
# Tail live training output (if running in background)
tail -f models/training_runs/disease_v2/metrics.json | python -m json.tool
```

---

## 7. Two-Phase Training Strategy

The training script implements a deliberate **two-phase warm-up + fine-tune** approach to prevent catastrophic forgetting of ImageNet-pretrained features.

```
Epoch 0 ──────── Epoch N (warmup) ──────── Epoch N+1 ───────────── Epoch MAX
│                                 │                                        │
│  Phase 1: WARMUP                │  Phase 2: FINE-TUNING                  │
│  • Backbone FROZEN              │  • All layers UNFROZEN                 │
│  • Only classifier head trains  │  • Backbone LR = head LR ÷ 10          │
│  • Stabilises head weights      │  • Cosine annealing: LR → --min-lr     │
│  • Prevents large gradient      │  • Early stopping on val_acc           │
│    spikes into backbone         │    (patience = --patience)             │
└─────────────────────────────────┴────────────────────────────────────────┘
```

**Why this matters:** Without the warmup phase, the randomly-initialised classifier head produces large gradients that corrupt the pretrained backbone in the first few epochs. The warm-up lets the head converge before the backbone gradients are allowed to flow.

**Backbone LR ratio:** During fine-tuning, the backbone uses `lr / 10` (e.g., if `--lr 3e-4`, backbone gets `3e-5`). This preserves low-level features while allowing task-specific adaptation.

---

## 8. Training Script Reference

Full flag reference for `backend/scripts/train_eval.py`:

| Flag | Default | Description |
|---|---|---|
| `--model-name` | `efficientnet_b2` | EfficientNet variant (`b0`, `b1`, `b2`, `b3`). `b2` recommended for disease; `b0` for crop. |
| `--epochs` | `20` | Maximum training epochs (subject to early stopping) |
| `--batch-size` | `32` | Training batch size. Reduce to `16` if GPU VRAM is limited. |
| `--lr` | `3e-4` | Peak learning rate for the classifier head (AdamW optimiser) |
| `--min-lr` | `1e-6` | Minimum LR at the end of cosine annealing schedule |
| `--warmup-epochs` | `2` | Epochs with frozen backbone (head-only training) |
| `--patience` | `7` | Early stopping patience (epochs without val_acc improvement) |
| `--img-size` | `224` | Input image size (square). Must match production preprocessing. |
| `--use-class-weights` | enabled | Compute inverse-frequency class weights to handle imbalanced classes |
| `--from-scratch` | disabled | Disable ImageNet pretrained weights (not recommended) |
| `--checkpoint` | — | Path to `.pth` file — resumes training or runs evaluation only |
| `--output-dir` | required | Directory where `best.pth`, `last.pth`, `labels.json`, `metrics.json` are saved |

### Subcommands

```
train_eval.py disease   Train the disease classifier
train_eval.py crop      Train the crop identifier
train_eval.py eval      Evaluate an existing checkpoint (no training)
```

---

## 9. Step 3 — Review Training Output

After training completes, the output directory contains:

```
models/training_runs/disease_v2/
├── best.pth         ← Checkpoint with highest val_acc (use for production)
├── last.pth         ← Checkpoint from the final epoch (useful for debugging)
├── labels.json      ← index → class name mapping (required at inference time)
└── metrics.json     ← Full training history + held-out test results
```

### `metrics.json` Fields

| Field | Description |
|---|---|
| `best_val_acc` | Best validation accuracy achieved during training |
| `test_acc` | Accuracy on the held-out test split (unseen during training) |
| `epochs_trained` | Actual epochs run before early stopping triggered |
| `per_class_report` | Per-class precision, recall, F1-score, and support |
| `confusion_matrix` | Class × class confusion matrix (use to spot systematic confusions) |
| `history` | List of `{epoch, train_loss, val_loss, train_acc, val_acc}` per epoch |

### What to Check

1. **`test_acc` ≥ `val_acc` × 0.97** — A large drop (> 3 %) suggests overfitting. Try reducing `--epochs` or adding more data.
2. **`per_class_report`** — Flag any class where **recall < 0.70**. These are the classes the new model is systematically missing.
3. **`confusion_matrix`** — Look for off-diagonal clusters between visually similar diseases (e.g., Early Blight vs. Late Blight).
4. **`epochs_trained`** — If training stopped very early (< 5 epochs), the dataset may be too small or the LR too high.

---

## 10. Step 4 — Evaluate

Run standalone evaluation on the held-out test set before committing to a promotion decision:

```bash
python backend/scripts/train_eval.py eval \
    --checkpoint models/training_runs/disease_v2/best.pth \
    --dataset-dir data/exports/latest
```

This re-computes test accuracy, per-class report, and confusion matrix from the checkpoint without any retraining. Use this to:

- **Compare candidates:** evaluate both `best.pth` and `last.pth`, or compare two training runs.
- **Validate on a fresh export:** run eval on a newer export to see if the model generalises.
- **Cross-version comparison:** eval the current production checkpoint on the new dataset to quantify the improvement.

```bash
# Compare old vs. new checkpoint on the same dataset
python backend/scripts/train_eval.py eval \
    --checkpoint models/current_production/disease_v1.pth \
    --dataset-dir data/exports/latest

python backend/scripts/train_eval.py eval \
    --checkpoint models/training_runs/disease_v2/best.pth \
    --dataset-dir data/exports/latest
```

---

## 11. Step 5 — Promote to Production

Once satisfied with evaluation metrics, register the checkpoint via the model registry API. This operation:

1. Writes the new model entry to `model_registry.json`
2. Updates `config.yaml` with the new checkpoint and labels paths (atomic file swap)
3. Publishes a Redis hot-reload event so all inference workers pick up the new model **without restart**

```bash
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

### Promotion Fields

| Field | Required | Description |
|---|---|---|
| `model_key` | ✅ | Registry key (e.g., `tomato_disease`, `crop_identifier`) |
| `version` | ✅ | Semantic version string (e.g., `v2.0`, `v2.1`) |
| `checkpoint_path` | ✅ | Relative path to `best.pth` |
| `labels_path` | ✅ | Relative path to `labels.json` |
| `val_acc` | ✅ | Validation accuracy from `metrics.json` |
| `test_acc` | ✅ | Test accuracy from `metrics.json` |
| `notes` | ✅ | Human-readable summary of what changed |

### Hot-Reload Behaviour

After a successful `promote` call:

```
Admin API
  └─► Writes config.yaml (atomic rename swap)
  └─► Publishes "model_reloaded:{model_key}" to Redis pub/sub
        └─► Worker 1: receives event → loads new checkpoint → ready
        └─► Worker 2: receives event → loads new checkpoint → ready
        └─► Worker N: ...
```

Workers do not need to be restarted. Zero-downtime model swap is guaranteed as long as Redis pub/sub is available.

---

## 12. Reproducibility Checklist

Use this checklist every time you run a training cycle. Store it alongside the run artefacts.

- [ ] Note `exported_at` timestamp from `metadata.json` (dataset version identifier)
- [ ] Record `model_name`, `epochs`, `lr`, `warmup_epochs`, `batch_size` from `metrics.json`
- [ ] Store `best.pth` and `labels.json` in version control or a model artifact store
- [ ] Run `eval` mode on `best.pth` before promoting — compare against production checkpoint
- [ ] Review `per_class_report` — flag any class with **recall < 0.70**
- [ ] Inspect `confusion_matrix` — identify and document systematic class confusions
- [ ] Register via `POST /admin/models/promote` with full `notes` describing changes
- [ ] After promotion, monitor `expert_correction_rate` over the following 7 days — it should decrease
- [ ] Monitor `avg_disease_confidence_7d` — it should rise or stabilise after promotion
- [ ] Archive training run directory: `models/training_runs/disease_vX/` to long-term storage

---

## 13. Migration to S3 (Production Model Storage)

When moving to a production environment, migrate local image and model files to S3:

```bash
python backend/scripts/migrate_to_s3.py
```

After migration, update `.env`:

```bash
STORAGE_BACKEND=s3
AWS_S3_BUCKET=smart-farming-models
AWS_REGION=ap-south-1
```

The `migrate_to_s3.py` script handles:
- Uploading all local model checkpoints and label files
- Re-writing paths in `model_registry.json` to S3 URIs
- Uploading exported datasets and raw image files
- Verifying upload integrity via MD5 checksums

> **Important:** Test inference end-to-end in staging with `STORAGE_BACKEND=s3` before rolling to production. S3 latency on first load is higher than local disk — consider pre-loading models into memory on worker startup.

---

## 14. Troubleshooting

### Training Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| `CUDA out of memory` | Batch size too large for GPU VRAM | Reduce `--batch-size` to `16` or `8` |
| `val_acc` plateaus immediately | LR too high or dataset too small | Try `--lr 1e-4`; verify dataset size |
| Early stopping in < 5 epochs | LR too high; unstable gradients | Increase `--warmup-epochs` to 5 |
| `test_acc` >> `val_acc` | Val/test split imbalance | Re-export with stratified split |
| `test_acc` << `val_acc` | Overfitting | Reduce `--epochs`; add more training data |
| All predictions → one class | Class imbalance | Ensure `--use-class-weights` is set |

### API / Promotion Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| `401 Unauthorized` | Expired admin token | Refresh `$ADMIN_TOKEN` |
| `404` on `/admin/models/promote` | Backend not running | Start backend: `uvicorn backend.main:app` |
| Workers not picking up new model | Redis not running | Start Redis: `redis-server` |
| `config.yaml` not updated | Disk permission issue | Check write permissions on project root |

### Drift Monitoring Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| `avg_disease_confidence_7d` stays at `0.0` | No predictions in last 7 days | Check farmer app connectivity |
| `retraining_candidates` never grows | Expert review queue not being processed | Alert experts; check review workflow |
| `expert_correction_rate` = 100% | Model is severely outdated | Prioritise retraining immediately |

---

*AI-Powered Smart Farming — Documentation*  
*Last Updated: September 2026*
