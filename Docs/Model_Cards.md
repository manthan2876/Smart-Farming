# Model Cards — AI-Powered Smart Farming

> **Project**: AI-Powered Smart Farming System
> **Document Version**: 1.0
> **Last Updated**: 2026-09-22

---

## Table of Contents

1. [Model 1 — Crop Identifier](#1-crop-identifier)
2. [Model 2 — Disease Classifiers (Per-Crop)](#2-disease-classifiers-per-crop)
   - [2a. Cotton Disease Classifier](#2a-cotton-disease-classifier)
   - [2b. Groundnut Disease Classifier](#2b-groundnut-disease-classifier)
   - [2c. Pepper Bell Disease Classifier](#2c-pepper-bell-disease-classifier)
   - [2d. Potato Disease Classifier](#2d-potato-disease-classifier)
   - [2e. Tomato Disease Classifier](#2e-tomato-disease-classifier)
3. [Model 3 — Pest Classifier](#3-pest-classifier)
4. [Model 4 — Severity Estimator (CV Heuristic)](#4-severity-estimator-cv-heuristic)
5. [Model 5 — Recommendation Engine (LLM)](#5-recommendation-engine-llm)
6. [Pipeline Architecture Overview](#pipeline-architecture-overview)
7. [Common Preprocessing Specification](#common-preprocessing-specification)

---

## 1. Crop Identifier

| Field | Details |
|---|---|
| **Model ID** | `crop_identifier_v1` |
| **Model Files** | `models/crop_identifier_v1.pth`, `models/crop_identifier_labels.json` |
| **Architecture** | EfficientNet-B0 (via `timm`, pretrained on ImageNet, fine-tuned) |
| **Task** | Multi-class image classification — identifies crop from leaf image |
| **Number of Classes** | 5 |
| **Device** | CUDA (if available), else CPU — detected at startup |
| **Inference Mode** | Single-image; no batch inference in production |
| **Framework** | PyTorch (`torch.no_grad()` + `torch.softmax`) |

### Classes

| Index | Label |
|---|---|
| 0 | Cotton |
| 1 | Groundnut |
| 2 | Pepper Bell |
| 3 | Potato |
| 4 | Tomato |

### Training Data

| Property | Details |
|---|---|
| **Total Images** | ~34,552 |
| **Label Strategy** | Disease-level classes collapsed → crop-level labels |
| **Split** | 70% train / 15% validation / 15% test |
| **Augmentation** | Albumentations pipeline (normalization: mean `(0.485, 0.456, 0.406)`, std `(0.229, 0.224, 0.225)`) |

### Input Specification

| Property | Value |
|---|---|
| **Image Size** | 224 × 224 px |
| **Color Space** | RGB |
| **Normalization Mean** | `(0.485, 0.456, 0.406)` |
| **Normalization Std** | `(0.229, 0.224, 0.225)` |

### Performance Metrics

| Metric | Value |
|---|---|
| **Validation Accuracy** | ~99.48% |
| **Test Macro F1-Score** | ~99.31% |

### Confidence & Uncertainty Handling

| Confidence Level | Threshold | Behavior |
|---|---|---|
| **High** | ≥ 0.85 | Passed directly to disease router |
| **Moderate** | ≥ 0.70 (configurable) | Passed with a low-confidence note |
| **Low** | < 0.70 | Flagged as `unsupported_crop`; `is_uncertain=true` set; escalated to expert queue |

> **Configuration**: The confidence threshold (default `0.7`) is configurable via `config.yaml`.

### Known Limitations

- Supports only **5 crops**; out-of-scope crops will be misclassified or trigger low-confidence flags.
- Images significantly outside the training distribution (very dark, non-leaf objects, heavily occluded leaves) may cause incorrect or uncertain predictions.
- Accuracy in **uncontrolled field environments** is lower than in controlled lab/studio conditions.
- Model is not designed for batch inference in production; single-image pipeline only.

### Usage Notes

```python
# Conceptual usage
model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=5)
model.load_state_dict(torch.load("models/crop_identifier_v1.pth"))
model.eval()
with torch.no_grad():
    logits = model(input_tensor)
    probs = torch.softmax(logits, dim=1)
```

---

## 2. Disease Classifiers (Per-Crop)

### Overview

| Property | Details |
|---|---|
| **Architecture** | EfficientNet-B2 (via `timm`, pretrained on ImageNet, fine-tuned per crop) |
| **Task** | Multi-class disease classification, one model per crop |
| **Input Spec** | Identical to Crop Identifier: 224 × 224 RGB, same normalization |
| **Routing Logic** | Decision Engine (`router.py`) reads `config.yaml[models.disease_models]` and selects the per-crop model based on Crop Identifier output |

> **Note**: EfficientNet-B2 is used for disease classifiers (vs. B0 for the crop identifier) to capture finer-grained visual features required to distinguish between disease subtypes within a single crop.

---

### 2a. Cotton Disease Classifier

| Field | Details |
|---|---|
| **Model File** | `models/disease_Cotton.pth` |
| **Labels File** | `models/disease_Cotton_labels.json` |
| **Number of Classes** | 6 |

#### Classes

| Index | Label |
|---|---|
| 0 | Alternaria Leaf Spot |
| 1 | Bacterial Blight |
| 2 | Fusarium Wilt |
| 3 | Healthy |
| 4 | Powdery Mildew |
| 5 | Verticillium Wilt |

#### Training Data

| Property | Details |
|---|---|
| **Total Images** | ~2,660 |
| **Source Environments** | Closed Environment (CE) + Uncontrolled Environment (UE) merged |

#### Performance

| Metric | Value |
|---|---|
| **Validation Accuracy** | ~94.6% |

#### Known Limitations

- **Smallest dataset** across all disease classifiers (~2,660 images). Higher risk of overfitting or poor generalization on rare disease presentations.
- Lower recall on classes that appear exclusively in CE or exclusively in UE data.
- Uncontrolled background images tend to reduce prediction confidence.
- Verticillium Wilt and Fusarium Wilt have similar visual symptoms at early stages — potential for inter-class confusion.

---

### 2b. Groundnut Disease Classifier

| Field | Details |
|---|---|
| **Model File** | `models/disease_Groundnut.pth` |
| **Labels File** | `models/disease_Groundnut_labels.json` |
| **Number of Classes** | 7 |

#### Classes

| Index | Label |
|---|---|
| 0 | Alternaria Leaf Spot |
| 1 | Early Leaf Spot |
| 2 | Healthy |
| 3 | Late Leaf Spot |
| 4 | Nutrition Deficiency |
| 5 | Rosette |
| 6 | Rust |

> **Note**: Late Leaf Spot label was merged from "Early" and "Late" leaf spot classes present in some source datasets to ensure label consistency.

#### Training Data

| Property | Details |
|---|---|
| **Total Images** | ~7,343 |
| **Source Environments** | Field Closeup (FCU), Uncontrolled Environment (UE), Created-from-Uncontrolled (`GLCDfGLUE` — auto-cropped leaf images extracted from whole-plant photos) |

#### Known Limitations

- `GLCDfGLUE` auto-cropped images may carry **label noise** introduced during automated cropping from whole-plant photographs.
- **Early Leaf Spot vs. Late Leaf Spot** have very similar visual appearances — inter-class confusion expected on borderline cases, even for human experts.
- Nutrition Deficiency class may overlap visually with early-stage disease symptoms.

---

### 2c. Pepper Bell Disease Classifier

| Field | Details |
|---|---|
| **Model File** | `models/disease_Pepper_Bell.pth` |
| **Labels File** | `models/disease_Pepper_Bell_labels.json` |
| **Number of Classes** | 6 |

#### Classes

| Index | Label |
|---|---|
| 0 | Bacterial Spot |
| 1 | Cercospora Leaf Spot |
| 2 | Healthy |
| 3 | Leaf Curl |
| 4 | Nutrition Deficiency |
| 5 | Powdery Mildew |

> **Scope Note**: Chili (*Capsicum annuum* var.) leaf images are intentionally included under the Pepper Bell class. This is a deliberate project scope decision due to high visual and botanical similarity.

#### Training Data

| Property | Details |
|---|---|
| **Total Images** | ~9,574 |
| **Closed Environment (CE)** | ~9,283 images |
| **Uncontrolled Environment (UE)** | ~291 images |
| **CE/UE Imbalance Ratio** | ~32:1 |

#### Known Limitations

- **Severe CE/UE imbalance** (9,283 vs. 291 images). The model is heavily biased toward clean-background single-leaf imagery.
- Performance on field shots with cluttered backgrounds is significantly lower than on CE images.
- Leaf Curl symptom can co-occur with multiple causes (viral, nutrient, physical damage) — the model predicts the class, not the causal agent.

---

### 2d. Potato Disease Classifier

| Field | Details |
|---|---|
| **Model File** | `models/disease_Potato.pth` |
| **Labels File** | `models/disease_Potato_labels.json` |
| **Number of Classes** | 7 |

#### Classes

| Index | Label |
|---|---|
| 0 | Bacteria |
| 1 | Early Blight |
| 2 | Fungi |
| 3 | Healthy |
| 4 | Late Blight |
| 5 | Nematode |
| 6 | Virus |

> **Label Note**: The `Phytophthora` source class was merged into **Late Blight** during preprocessing, as *Phytophthora infestans* is the primary causal agent of Late Blight and the two labels were used interchangeably across source datasets.

#### Training Data

| Property | Details |
|---|---|
| **Total Images** | ~7,834 |

#### Known Limitations

- **Early Blight vs. Late Blight** distinction can be difficult even for trained agricultural experts at early symptom stages — the model may exhibit confusion between these two classes.
- Broad pathogen-category classes (`Bacteria`, `Fungi`, `Virus`, `Nematode`) aggregate multiple distinct diseases — the model identifies the pathogen category, not the specific pathogen species.
- Nematode damage typically manifests on roots rather than leaves; leaf-based visual signals may be weak.

---

### 2e. Tomato Disease Classifier

| Field | Details |
|---|---|
| **Model File** | `models/disease_Tomato.pth` |
| **Labels File** | `models/disease_Tomato_labels.json` |
| **Number of Classes** | 11 |

#### Classes

| Index | Label |
|---|---|
| 0 | Bacterial Spot |
| 1 | Burn Leaf |
| 2 | Early Blight |
| 3 | Healthy |
| 4 | Late Blight |
| 5 | Leaf Miner |
| 6 | Mold Leaf |
| 7 | Mosaic Virus |
| 8 | Septoria |
| 9 | Spider Mite |
| 10 | Yellow Curl Virus |

#### Training Data

| Property | Details |
|---|---|
| **Total Images** | ~7,140 |
| **Closed Environment (CE)** | ~4,050 images |
| **Uncontrolled Environment (UE)** | ~3,090 images |

#### Performance

| Metric | Value |
|---|---|
| **Validation Accuracy** | ~90.8% |

#### Known Limitations

- **Highest class count** (11 classes) across all disease classifiers — greatest inter-class confusion risk.
- `Burn Leaf` class images appear **exclusively in UE data** — generalization to CE images is untested.
- **Spider Mite** and **Leaf Miner** symptom images visually overlap with pest-category images in the Pest Classifier (Model 3), potentially causing ambiguity between the two pipeline stages.
- Lower recall on minority/long-tail classes due to unequal class representation.
- Lower overall accuracy (~90.8%) compared to other per-crop classifiers, attributed to higher class count and domain diversity.

---

## 3. Pest Classifier

| Field | Details |
|---|---|
| **Model File** | `models/pest_classifier/pest_classifier.pt` |
| **Architecture** | YOLOv8-cls (Ultralytics YOLOv8 Classification, based on `yolov8n-cls.pt` pretrained weights) |
| **Task** | Multi-class classification for pest identification |
| **Framework** | Ultralytics (`ultralytics` Python package) |
| **Number of Classes** | 4 |

### Classes

| Index | Label |
|---|---|
| 0 | Aphid |
| 1 | Army Worm |
| 2 | Leaf Miner |
| 3 | Spider Mite |

### Input Specification

| Property | Value |
|---|---|
| **Image Format** | Leaf image (read as BGR via OpenCV, converted to RGB for YOLO inference) |
| **Inference Type** | Classification only (no bounding box, no instance count) |

### Confidence Thresholds

| Level | Threshold | Interpretation |
|---|---|---|
| **Detection threshold** | 0.40 | Minimum confidence to report any pest |
| **Confident prediction** | ≥ 0.60 | High-confidence pest identification |
| **Uncertain / No pest** | < 0.40 | Result suppressed; no pest reported |

### Source Data

Pest-symptom images were pulled from Uncontrolled Environment sets (primarily Tomato, Cotton, and Pepper Bell crops) during dataset preprocessing. These images depict visible pest damage on leaves rather than isolated pest specimens.

### Output Schema

```json
{
  "pests": [
    { "label": "Aphid", "confidence": 0.82 }
  ],
  "pest_classification": {
    "Aphid": 0.82,
    "Army Worm": 0.07,
    "Leaf Miner": 0.06,
    "Spider Mite": 0.05
  }
}
```

Pipeline context keys: `context["pests"]` (filtered list), `context["pest_classification"]` (full probability dict).

### Known Limitations

- **Classification only** — no bounding box localization, no individual pest count. The model predicts pest category from the entire leaf image.
- The model will output a probability distribution even when **no pest is actually present**. Confidence thresholds are critical to suppress false positives.
- Model availability is **not guaranteed** — if the weight file (`pest_classifier.pt`) is missing, the pest classification step is gracefully skipped in the pipeline.
- Training data is limited to symptom images from 3 crop types (Tomato, Cotton, Pepper Bell) — generalization to other crops is unknown.
- Leaf Miner and Spider Mite may cause confusion with similarly-named disease classes in the Tomato Disease Classifier.

### Graceful Degradation

If `models/pest_classifier/pest_classifier.pt` is not found at startup, the pipeline will log a warning and skip the pest classification step without raising an exception. The rest of the inference pipeline continues normally.

---

## 4. Severity Estimator (CV Heuristic)

| Field | Details |
|---|---|
| **Type** | Computer Vision Heuristic (rule-based, not a learned model) |
| **Library** | OpenCV |
| **Task** | Estimate percentage of leaf tissue showing disease symptoms |
| **Color Spaces** | HSV + LAB |

### Algorithm

The severity estimator is a deterministic, hand-engineered image processing pipeline. It is **not trained on data**.

| Step | Operation |
|---|---|
| **1. Leaf Mask** | HSV thresholding over the vegetation color range to isolate the leaf area from the background |
| **2. Disease Mask** | Detect yellow, brown, dark necrotic, and pale/bleached regions using HSV range masks |
| **3. LAB Corroboration** | Filter weak disease candidates using LAB color space to reduce false positives from lighting artifacts |
| **4. Connected Components** | Remove noise components smaller than 30 pixels using connected component analysis |
| **5. Morphological Cleanup** | Apply morphological open + close operations with a 5×5 elliptical structuring kernel |
| **6. Severity Score** | `severity_percent = (diseased_pixels / leaf_pixels) × 100` |
| **7. Heatmap Overlay** | Generate JET colormap heatmap overlay saved as a processed image for visualization |

### Severity Buckets

| Severity Level | Threshold | Interpretation |
|---|---|---|
| **Mild** | < 20% | Early-stage or minor infection |
| **Moderate** | 20% – 50% | Significant infection; treatment recommended |
| **Severe** | > 50% | Advanced infection; immediate intervention required |

### Known Limitations

- HSV thresholds were **hand-tuned**, not learned from labelled segmentation data. Performance is sensitive to the initial calibration.
- Accuracy **degrades** on images with unusual lighting conditions, heavy shadows, or non-standard backgrounds.
- The severity score is an **approximation** — it is not a laboratory-grade or agronomist-validated measurement.
- Cannot distinguish between multiple co-occurring diseases on the same leaf.
- A **dedicated semantic segmentation model** (e.g., a fine-tuned U-Net or SegFormer) is the recommended next step to replace this heuristic for production-level accuracy.

### Output

| Key | Type | Description |
|---|---|---|
| `severity_percent` | `float` | Estimated percentage of leaf area showing disease |
| `severity_label` | `str` | One of: `"Mild"`, `"Moderate"`, `"Severe"` |
| `processed_image_path` | `str` | Path to saved JET heatmap overlay image |

---

## 5. Recommendation Engine (LLM)

| Field | Details |
|---|---|
| **Model** | `Qwen/Qwen3-4B-Instruct-2507` |
| **Provider** | HuggingFace Inference Providers |
| **Backend** | nscale |
| **Task** | Generate structured, actionable agricultural recommendations |
| **Prompt Version** | v1.0 |

### Inference Parameters

| Parameter | Value |
|---|---|
| **Temperature** | 0.2 (near-deterministic) |
| **Max New Tokens** | 350 |
| **Output Validation** | Pydantic schema validation |

### Input

The LLM receives a structured prompt containing the following context, assembled by the pipeline after all upstream models have completed:

| Input Field | Source |
|---|---|
| Crop name | Crop Identifier output |
| Detected disease | Disease Classifier output |
| Disease severity (%) and label | Severity Estimator output |
| Detected pests | Pest Classifier output |
| Weather data | External weather API |
| Location | User-provided or GPS |

### Output Schema (Pydantic-validated)

```json
{
  "immediate_action": "string — actions to take within 24–48 hours",
  "treatment": "string — recommended chemical/biological/organic treatment",
  "prevention": "string — long-term preventive measures",
  "monitoring": "string — what to watch for in follow-up inspections"
}
```

### Fallback Mechanism

If the LLM inference call fails (network error, timeout) **or** the response fails Pydantic schema validation, the pipeline switches to a **rule-based fallback** response:

- Fallback text is returned in the same output schema format.
- `is_fallback: true` is set in the pipeline context.
- The user-facing response is structurally identical; the fallback is transparent to end users unless explicitly exposed in the UI.

### Safety & Disclaimer

Every recommendation response (both LLM-generated and fallback) appends the following disclaimer:

> **DISCLAIMER**: Always follow local agricultural guidelines, product labels, and environmental regulations when applying chemical treatments.

### Known Limitations

- **Cloud inference dependency**: The model runs on HuggingFace's nscale backend. Latency and availability are subject to network conditions and third-party SLA.
- The LLM may occasionally produce **imprecise measurements** (e.g., dilution ratios, dosage) that should be cross-referenced with product labels.
- Output quality is influenced by the quality of upstream model predictions — a misclassified disease will yield recommendations for the wrong condition.
- The model does not have real-time access to local pest outbreak databases or region-specific chemical registration status.
- Prompt version v1.0 — subject to revision as the system matures.

---

## Pipeline Architecture Overview

The five models/components above operate as a sequential inference pipeline triggered by a single leaf image upload:

```
User Image
    │
    ▼
┌─────────────────────────────┐
│  Model 1: Crop Identifier   │  EfficientNet-B0
│  → Crop label + confidence  │  224×224 RGB
└────────────┬────────────────┘
             │ Confidence ≥ threshold?
             │ Yes → route to disease model
             │ No  → flag unsupported_crop, escalate
             ▼
┌─────────────────────────────┐
│  Model 2: Disease Classifier│  EfficientNet-B2 (per-crop)
│  → Disease label + prob.    │  Routed by router.py + config.yaml
└────────────┬────────────────┘
             │
             ├──────────────────────────────────┐
             ▼                                  ▼
┌─────────────────────────┐      ┌────────────────────────────┐
│ Model 3: Pest Classifier│      │ Model 4: Severity Estimator│
│ YOLOv8-cls              │      │ OpenCV HSV+LAB heuristic   │
│ → pests list + probs    │      │ → severity_percent + label │
└────────────┬────────────┘      └──────────────┬─────────────┘
             │                                  │
             └──────────────┬───────────────────┘
                            ▼
             ┌──────────────────────────────┐
             │ Model 5: Recommendation LLM  │  Qwen3-4B-Instruct
             │ Qwen/Qwen3-4B-Instruct-2507  │  + Weather + Location
             │ → {immediate_action,         │
             │     treatment, prevention,   │
             │     monitoring}              │
             └──────────────────────────────┘
```

---

## Common Preprocessing Specification

All image-based ML models (Crop Identifier, Disease Classifiers, Pest Classifier) share a common preprocessing pipeline for input normalization:

| Step | Details |
|---|---|
| **Resize** | 224 × 224 pixels |
| **Color Space** | RGB (OpenCV BGR images converted to RGB before model input) |
| **Library** | Albumentations |
| **Normalization Mean** | `(0.485, 0.456, 0.406)` — ImageNet standard |
| **Normalization Std** | `(0.229, 0.224, 0.225)` — ImageNet standard |
| **Tensor Type** | `torch.float32` |

> The same normalization statistics (ImageNet mean/std) are used across all models because all models are initialized from ImageNet-pretrained weights and fine-tuned on domain data.

---

*Document maintained by the smart farming development team. For queries, refer to the project README or contact the team lead.*
