# Model Cards — AI-Powered Smart Farming

**Project:** AI-Powered Smart Farming  
**Version:** 2.0  
**Date:** 19 October 2026  
**Status:** Active / Production Reference  
**Last Verified Against Codebase:** 19 October 2026  

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
4. [Model 4 — Severity Estimator (CV Heuristic & DeepLabV3+)](#4-severity-estimator-cv-heuristic--deeplabv3)
5. [Model 5 — Recommendation Engine (LLM + ICAR/KVK Knowledge Base)](#5-recommendation-engine-llm--icarkvk-knowledge-base)
6. [Model 6 — Regional Translation Engine (AI4Bharat IndicTrans2)](#6-regional-translation-engine-ai4bharat-indictrans2)
7. [Model 7 — Neural Speech Synthesis (Microsoft Edge-TTS)](#7-neural-speech-synthesis-microsoft-edge-tts)
8. [Pipeline Architecture & 7-Stage Vision Engine](#8-pipeline-architecture--7-stage-vision-engine)
9. [Common Preprocessing Specification](#9-common-preprocessing-specification)

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

| Metric | Overall Value |
|---|---|
| **Validation Accuracy** | ~99.48% |
| **Held-Out Test Accuracy** | 99.53% (4,240 / 4,260 correct) |
| **Test Macro F1-Score** | 99.45% |
| **Weighted F1-Score** | 99.50% |

#### Per-Class Metrics (Held-Out Test Set, N = 4,260)

| Crop Class | Precision | Recall | F1-Score | Support (Images) |
|---|---|---|---|---|
| **Cotton** | 0.993 | 0.986 | 0.990 | 288 |
| **Groundnut** | 0.999 | 0.997 | 0.998 | 695 |
| **Pepper Bell** | 0.996 | 0.995 | 0.995 | 1,128 |
| **Potato** | 0.997 | 1.000 | 0.999 | 1,152 |
| **Tomato** | 0.991 | 0.992 | 0.991 | 997 |
| **Macro Average** | **0.995** | **0.994** | **0.995** | **4,260** |
| **Weighted Average** | **0.995** | **0.995** | **0.995** | **4,260** |

#### In-Situ Field Set vs. Controlled Environment Breakdown

| Evaluation Split | Test Accuracy | Correct / Total | Description |
|---|---|---|---|
| **Closed Environment (Lab)** | **99.65%** | 2,855 / 2,865 | Studio/bench lighting with isolated leaf background |
| **Uncontrolled Environment (Field)** | **99.35%** | 1,385 / 1,395 | In-situ farm photography under natural sunlight, shadows, and soil background |

#### Confidence Calibration & Reliability

* **Post-Hoc Temperature Scaling:** Optimal temperature $T = 1.08$ configured in `config.yaml`.
* **Expected Calibration Error (ECE):**
  * Uncalibrated raw softmax: `0.0210`
  * Temperature-calibrated ($T = 1.08$): `0.0072` (65.7% reduction in miscalibration)
* **Maximum Calibration Error (MCE):** `0.0185` across 10 confidence bins.
* **Brier Score:** `0.0076`.

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

#### Performance & Empirical Metrics

| Metric | Overall Value |
|---|---|
| **Validation Accuracy** | ~94.6% |
| **Held-Out Test Accuracy** | 95.7% (265 / 277 correct) |
| **Test Macro F1-Score** | 93.33% |
| **Weighted F1-Score** | 95.70% |

##### Per-Class Metrics (Held-Out Test Set, N = 277)

| Disease Class | Precision | Recall | F1-Score | Support (Images) |
|---|---|---|---|---|
| **Alternaria Leaf Spot** | 1.000 | 0.962 | 0.980 | 26 |
| **Bacterial Blight** | 0.949 | 0.860 | 0.902 | 43 |
| **Curl Virus** | 1.000 | 0.923 | 0.960 | 13 |
| **Fusarium Wilt** | 0.967 | 0.989 | 0.978 | 88 |
| **Healthy** | 0.982 | 0.982 | 0.982 | 56 |
| **Powdery Mildew** | 1.000 | 1.000 | 1.000 | 6 |
| **Target Spot** | 0.625 | 0.833 | 0.714 | 6 |
| **Verticillium Wilt** | 0.927 | 0.974 | 0.950 | 39 |
| **Macro Average** | **0.931** | **0.940** | **0.933** | **277** |
| **Weighted Average** | **0.959** | **0.957** | **0.957** | **277** |

##### In-Situ Field Set vs. Controlled Environment Breakdown

| Evaluation Split | Test Accuracy | Description |
|---|---|---|
| **Closed Environment (Lab)** | **96.8%** | Controlled indoor canopy scans |
| **Uncontrolled Environment (Field)** | **94.2%** | Real farm canopy scans with complex natural backgrounds |

##### Confidence Calibration & Reliability

* **Temperature Scaling:** Calibrated with $T = 1.12$ in `config.yaml`.
* **Expected Calibration Error (ECE):** Reduced from `0.0460` to `0.0162`.
* **Brier Score:** `0.0541`.

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

#### Training Data

| Property | Details |
|---|---|
| **Total Images** | ~7,343 |
| **Source Environments** | Field Closeup (FCU), Uncontrolled Environment (UE), Created-from-Uncontrolled (`GLCDfGLUE` — auto-cropped leaf images extracted from whole-plant photos) |

#### Performance & Empirical Metrics

| Metric | Overall Value |
|---|---|
| **Validation Accuracy** | ~93.4% |
| **Held-Out Test Accuracy** | 93.8% (652 / 695 correct) |
| **Test Macro F1-Score** | 94.61% |
| **Weighted F1-Score** | 93.80% |

##### Per-Class Metrics (Held-Out Test Set, N = 695)

| Disease Class | Precision | Recall | F1-Score | Support (Images) |
|---|---|---|---|---|
| **Alternaria Leaf Spot** | 0.983 | 0.983 | 0.983 | 58 |
| **Healthy** | 0.915 | 0.947 | 0.931 | 228 |
| **Leaf Spot** | 0.930 | 0.942 | 0.936 | 294 |
| **Nutrition Deficiency** | 0.978 | 0.918 | 0.947 | 49 |
| **Rosette** | 1.000 | 0.929 | 0.963 | 14 |
| **Rust** | 1.000 | 0.846 | 0.917 | 52 |
| **Macro Average** | **0.968** | **0.928** | **0.946** | **695** |
| **Weighted Average** | **0.939** | **0.938** | **0.938** | **695** |

##### In-Situ Field Set vs. Controlled Environment Breakdown

| Evaluation Split | Test Accuracy | Description |
|---|---|---|
| **Closed Environment (Lab)** | **95.1%** | Benchmark scans with clean backgrounds |
| **Field Closeup & GLCDfGLUE (Field)** | **92.9%** | In-situ groundnut canopy photos with soil & weeds |

##### Confidence Calibration & Reliability

* **Temperature Scaling:** Calibrated with $T = 1.15$ in `config.yaml`.
* **Expected Calibration Error (ECE):** Reduced from `0.0510` to `0.0178`.
* **Brier Score:** `0.0612`.

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

#### Performance & Empirical Metrics

| Metric | Overall Value |
|---|---|
| **Validation Accuracy** | ~98.2% |
| **Held-Out Test Accuracy** | 98.5% (1,098 / 1,115 correct) |
| **Test Macro F1-Score** | 93.60% |
| **Weighted F1-Score** | 98.50% |

##### Per-Class Metrics (Held-Out Test Set, N = 1,115)

| Disease Class | Precision | Recall | F1-Score | Support (Images) |
|---|---|---|---|---|
| **Bacterial Spot** | 0.998 | 0.981 | 0.990 | 536 |
| **Cercospora Leaf Spot** | 0.977 | 0.990 | 0.983 | 210 |
| **Edema** | 0.750 | 0.600 | 0.667 | 5 |
| **Healthy** | 0.974 | 0.996 | 0.985 | 227 |
| **Leaf Curl** | 0.980 | 0.980 | 0.980 | 51 |
| **Nutrition Deficiency** | 0.967 | 1.000 | 0.983 | 58 |
| **Powdery Mildew** | 0.964 | 0.964 | 0.964 | 28 |
| **Macro Average** | **0.944** | **0.930** | **0.936** | **1,115** |
| **Weighted Average** | **0.985** | **0.985** | **0.985** | **1,115** |

##### In-Situ Field Set vs. Controlled Environment Breakdown

| Evaluation Split | Test Accuracy | Description |
|---|---|---|
| **Closed Environment (Lab)** | **98.7%** | Controlled lab/studio dataset scans |
| **Uncontrolled Environment (Field)** | **91.4%** | Real-world in-situ field leaf images |

##### Confidence Calibration & Reliability

* **Temperature Scaling:** Calibrated with $T = 1.10$ in `config.yaml`.
* **Expected Calibration Error (ECE):** Reduced from `0.0240` to `0.0084`.
* **Brier Score:** `0.0248`.

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

#### Performance & Empirical Metrics

| Metric | Overall Value |
|---|---|
| **Validation Accuracy** | ~94.1% |
| **Held-Out Test Accuracy** | 94.5% (1,089 / 1,152 correct) |
| **Test Macro F1-Score** | 87.77% |
| **Weighted F1-Score** | 94.40% |

##### Per-Class Metrics (Held-Out Test Set, N = 1,152)

| Disease Class | Precision | Recall | F1-Score | Support (Images) |
|---|---|---|---|---|
| **Bacteria** | 0.902 | 0.988 | 0.943 | 84 |
| **Early Blight** | 1.000 | 1.000 | 1.000 | 266 |
| **Fungi** | 0.832 | 0.900 | 0.865 | 110 |
| **Healthy** | 0.960 | 0.973 | 0.967 | 224 |
| **Late Blight** | 0.993 | 0.959 | 0.975 | 290 |
| **Nematode** | 1.000 | 0.400 | 0.571 | 10 |
| **Pest (Damage)** | 0.859 | 0.744 | 0.798 | 90 |
| **Virus** | 0.860 | 0.949 | 0.902 | 78 |
| **Macro Average** | **0.926** | **0.864** | **0.878** | **1,152** |
| **Weighted Average** | **0.947** | **0.945** | **0.944** | **1,152** |

##### In-Situ Field Set vs. Controlled Environment Breakdown

| Evaluation Split | Test Accuracy | Description |
|---|---|---|
| **Closed Environment (Lab)** | **96.2%** | Standard high-resolution controlled leaf captures |
| **Uncontrolled Environment (Field)** | **92.1%** | In-situ agricultural field shots under varied illumination |

##### Confidence Calibration & Reliability

* **Temperature Scaling:** Calibrated with $T = 1.14$ in `config.yaml`.
* **Expected Calibration Error (ECE):** Reduced from `0.0350` to `0.0121`.
* **Brier Score:** `0.0435`.

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

#### Performance & Empirical Metrics

| Metric | Overall Value |
|---|---|
| **Validation Accuracy** | ~90.8% |
| **Held-Out Test Accuracy** | 89.5% (831 / 929 correct) |
| **Test Macro F1-Score** | 78.42% |
| **Weighted F1-Score** | 89.80% |

##### Per-Class Metrics (Held-Out Test Set, N = 929)

| Disease Class | Precision | Recall | F1-Score | Support (Images) |
|---|---|---|---|---|
| **Bacterial Spot** | 0.970 | 0.896 | 0.931 | 182 |
| **Early Blight** | 0.908 | 0.945 | 0.927 | 220 |
| **Healthy** | 0.975 | 0.956 | 0.966 | 206 |
| **Late Blight** | 0.931 | 0.892 | 0.911 | 166 |
| **Mold Leaf** | 0.824 | 0.813 | 0.819 | 75 |
| **Mosaic Virus** | 0.368 | 0.500 | 0.424 | 14 |
| **Septoria** | 0.600 | 0.733 | 0.660 | 45 |
| **Yellow Curl Virus** | 0.609 | 0.667 | 0.636 | 21 |
| **Macro Average** | **0.773** | **0.800** | **0.784** | **929** |
| **Weighted Average** | **0.903** | **0.895** | **0.898** | **929** |

##### In-Situ Field Set vs. Controlled Environment Breakdown

| Evaluation Split | Test Accuracy | Description |
|---|---|---|
| **Closed Environment (Lab)** | **92.4%** | Bench scans under uniform diffused LED illumination |
| **Uncontrolled Environment (Field)** | **87.2%** | Real farm canopy scans under high-contrast solar shadows |

##### Confidence Calibration & Reliability

* **Temperature Scaling:** Calibrated with $T = 1.18$ in `config.yaml`.
* **Expected Calibration Error (ECE):** Reduced from `0.0520` to `0.0195`.
* **Brier Score:** `0.0782`.

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

### Performance & Empirical Metrics

| Metric | Overall Value |
|---|---|
| **Validation Top-1 Accuracy** | 100.0% (at epoch 14/19) |
| **Held-Out Test Accuracy** | 97.6% (80 / 82 correct) |
| **Test Macro F1-Score** | 96.59% |
| **Weighted F1-Score** | 97.60% |

#### Per-Class Metrics (Held-Out Test Set, N = 82)

| Pest Class | Precision | Recall | F1-Score | Support (Images) |
|---|---|---|---|---|
| **Aphid** | 1.000 | 0.900 | 0.947 | 10 |
| **Army Worm** | 1.000 | 1.000 | 1.000 | 6 |
| **Leaf Miner** | 0.983 | 0.983 | 0.983 | 59 |
| **Spider Mite** | 0.875 | 1.000 | 0.933 | 7 |
| **Macro Average** | **0.965** | **0.971** | **0.966** | **82** |
| **Weighted Average** | **0.977** | **0.976** | **0.976** | **82** |

#### In-Situ Field Set vs. Controlled Environment Breakdown

| Evaluation Split | Test Accuracy | Description |
|---|---|---|
| **In-Situ Field Leaf Damage Set** | **97.6%** | Real leaf symptom images extracted from uncontrolled field environments |

#### Confidence Calibration & Reliability

* **Threshold-Based Gating:** Detection floor `0.40` suppresses false alarms when no pest is present; confident predictions require $\ge 0.60$.
* **Expected Calibration Error (ECE):** `0.0182`.
* **Brier Score:** `0.0215`.

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
| **Healthy** | 0% | No visible foliar lesions detected; healthy plant tissue |
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
| `severity_label` | `str` | One of: `"Healthy"`, `"Mild"`, `"Moderate"`, `"Severe"` |
| `processed_image_path` | `str` | Path to saved JET heatmap overlay image |

---

## 5. Recommendation Engine (LLM + ICAR/KVK Knowledge Base)

| Field | Details |
|---|---|
| **Primary Local Engine** | `Qwen/Qwen2.5-1.5B-Instruct` (in-memory Hugging Face PyTorch CPU) |
| **High-Speed Cloud Engine**| `Groq Llama-3.3-70B-Versatile` (via Groq Cloud API, ~300 tokens/sec) |
| **Multimodal Advisory Fallback** | Google Gemini 2.5 Flash (`google-genai` / `GEMINI_API_KEY`) |
| **Agronomic Knowledge Base** | `advisory_kb.json` (ICAR & Krishi Vigyan Kendra validated packages of practices) |
| **Task** | Generate structured, actionable agricultural recommendations with safety guidelines |
| **Prompt Version** | v2.1 |

### Inference Parameters

| Parameter | Value |
|---|---|
| **Temperature** | 0.2 (near-deterministic) |
| **Max New Tokens** | 450 |
| **Output Validation** | Pydantic schema validation |

### Input Context Assembly

The LLM receives a structured prompt containing the following assembled pipeline context:

| Input Field | Source |
|---|---|
| Crop name | Crop Identifier output (Cotton, Groundnut, Pepper Bell, Potato, Tomato) |
| Detected disease | Disease Classifier output |
| Disease severity (%) and label | Severity Estimator output |
| Detected pests | Pest Classifier output |
| Weather data | OpenWeatherMap API (temperature, humidity, rainfall forecast) |
| Location | User GPS or Indian Agricultural Default (`Gujarat, India`) |
| Relevant Agronomic KB Entry | Ground-truth pesticide recommendations, organic alternatives, and safety limits from `advisory_kb.json` |

### Output Schema (Pydantic-validated)

```json
{
  "immediate_action": "string — actions to take within 24–48 hours",
  "treatment": "string — recommended chemical/biological/organic treatment with dilution dosage",
  "prevention": "string — long-term preventive measures and crop hygiene",
  "monitoring": "string — symptoms to watch for in follow-up inspections"
}
```

### Safety & Disclaimer

Every recommendation response appends the standardized statutory disclaimer:

> **DISCLAIMER**: Always follow local agricultural guidelines, product labels, and environmental regulations when applying chemical treatments.

---

## 6. Regional Translation Engine (AI4Bharat IndicTrans2)

| Field | Details |
|---|---|
| **Model ID** | `ai4bharat/indictrans2-en-indic-dist-200M` |
| **Architecture** | Distilled Sequence-to-Sequence Transformer |
| **Parameters** | 200 Million |
| **Hosting** | In-memory on Hugging Face Spaces AI Microservice (`ai_service/routers/translation.py`) |
| **Task** | Neural Machine Translation from English into Indian regional languages |
| **Supported Pairs** | English $\to$ Hindi (`en` $\to$ `hi`), English $\to$ Gujarati (`en` $\to$ `gu`) |
| **Inference Latency** | ~400–600ms on CPU for typical advisory paragraphs |
| **Tokenizer** | IndicTransTokenizer with language indicators (`<2hi>`, `<2gu>`) |

### Agricultural Domain Evaluation

| Language Pair | IndicBENCH BLEU | Agronomic Terminology Accuracy |
|---|---|---|
| **English $\to$ Hindi** | 38.4 | 96.8% (Verified against ICAR Hindi glossary) |
| **English $\to$ Gujarati**| 35.1 | 95.4% (Verified against GAU agricultural terms) |

### Caching Architecture

- **Sub-20ms Repeat Response:** All translated phrases are hashed (`sf:trans:{lang}:{hash}`) and cached in Upstash Redis REST.
- **Relational Persistence:** Translated recommendations and expert guidance notes are committed to the `entity_translations` table in Supabase PostgreSQL for persistent retrieval.

---

## 7. Neural Speech Synthesis (Microsoft Edge-TTS)

| Field | Details |
|---|---|
| **Engine** | Microsoft Edge-TTS Neural Voice Architecture |
| **Hosting** | Asynchronous service on Hugging Face Spaces AI Microservice (`ai_service/routers/tts.py`) |
| **Task** | High-fidelity audio narration of diagnostic reports and weather advisories |
| **Output Format** | MP3 / 24kHz Mono WAV |

### Voice Allocation Matrix

| Language | Primary Voice | Style / Gender | Sample Rate |
|---|---|---|---|
| **Gujarati (`gu`)** | `gu-IN-DhwaniNeural` | Female / Clear Regional Intonation | 24,000 Hz |
| **Hindi (`hi`)** | `hi-IN-SwaraNeural` | Female / Standard Modern Hindi | 24,000 Hz |
| **Indian English (`en`)** | `en-IN-NeerjaNeural` | Female / Indian Accent English | 24,000 Hz |

### Phonetic & Numeric Preprocessing

The TTS pipeline includes `tts_normalizer.py`:
- Expands numbers, percentages, and decimals into spoken regional words (e.g. `10%` $\to$ `દસ ટકા` in Gujarati or `दस प्रतिशत` in Hindi).
- If English text is submitted for Gujarati or Hindi voice synthesis, the service automatically invokes IndicTrans2 to pre-translate the text, guaranteeing authentic regional speech delivery.

---

## 8. Pipeline Architecture & 7-Stage Vision Engine

The AI microservice integrates computer vision, deep learning, rule-based heuristics, and generative LLMs into an automated sequential pipeline:

```
📷 User Image Upload
       │
       ▼
┌───────────────────────────────┐
│ Stage 1: Preprocessing        │  OpenCV: Aspect ratio preservation,
│                               │  RGB normalization, lighting pre-checks
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ Stage 2: Crop Identification  │  ResNet-50 / MobileNetV3 (5 crops)
│                               │  Confidence ≥ 0.70 threshold check
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ Stage 3: Leaf Isolation       │  DeepLabV3+ Semantic Segmentation
│                               │  Removes background clutter (soil, hands)
└──────────────┬────────────────┘
               │
               ├─────────────────────────────────────────┐
               ▼                                         ▼
┌───────────────────────────────┐         ┌───────────────────────────────┐
│ Stage 4: Disease Classifier   │         │ Stage 5: Severity Masking     │
│ DenseNet-121 (Per-Crop)       │         │ HSV Contour & LAB masking     │
│ Probability distribution      │         │ Infected leaf area percentage │
└──────────────┬────────────────┘         └──────────────┬────────────────┘
               │                                         │
               ├─────────────────────────────────────────┘
               ▼
┌───────────────────────────────┐
│ Stage 6: Pest Detection       │  YOLOv8-nano (Aphid, Army Worm,
│                               │  Leaf Miner, Spider Mite)
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ Stage 7: Decision Router      │  Evaluates confidence scores; flags
│                               │  escalation_required if confidence < 0.70
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ Stage 8: Advisory & LLM       │  Qwen2.5-1.5B / Groq Llama-3.3-70B
│                               │  + OpenWeatherMap + ICAR/KVK KB
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ Regional Translation & TTS    │  IndicTrans2 (EN → HI, GU)
│                               │  Edge-TTS (Dhwani, Swara, Neerja)
└───────────────────────────────┘
```

---

## 9. Common Preprocessing Specification

All image-based vision models (Crop Identifier, Disease Classifiers, Pest Detector) share a common input transformation pipeline:

| Step | Details |
|---|---|
| **Resize** | 224 × 224 pixels (Crop & Disease), 640 × 640 pixels (YOLO Pest) |
| **Color Space** | RGB (OpenCV BGR images converted to RGB before tensor creation) |
| **Library** | Albumentations / Torchvision |
| **Normalization Mean** | `(0.485, 0.456, 0.406)` — ImageNet standard |
| **Normalization Std** | `(0.229, 0.224, 0.225)` — ImageNet standard |
| **Tensor Type** | `torch.float32` |

---

*AI-Powered Smart Farming — Model Cards Reference*  
*Last Updated: 19 October 2026*  
*Maintained by the Smart Farming ML & Agronomy Team*
