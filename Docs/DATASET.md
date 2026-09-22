# Dataset Documentation — Smart Farming

This document describes the datasets used to train the Smart Farming crop identifier, disease classifiers, and pest classifier: where the raw data came from, how it was renamed/merged, and how it was split for training.

> **Note:** Section 2 lists every leaf/crop-disease dataset found in your browsing history, deduplicated by URL (and flagged where titles suggest likely-duplicate content). Where a class list or image count clearly matches your `dataset_descriptions.txt`, that's called out as the strongest candidate — but **you should confirm and delete the ones you didn't actually download** before publishing this doc, since several near-identical datasets exist per crop.

> **Chili + Bell Pepper note:** the Pepper Bell class intentionally combines Bell Pepper datasets with Chili datasets (see Section 2) — this is a deliberate scope decision, not a mislabel.

---

## 1. Pipeline Overview

```
Raw downloads (Kaggle / Mendeley, per crop, per environment)
        │
        ▼
final_combined_datasets/   (renamed to short codes, 34,552 images total)
        │
        ├──► dataset_split/     → crop identifier training (5 crop classes, train/val/test)
        ├──► disease_dataset/   → per-crop disease classifiers (pest-symptom classes removed)
        ├──► pest_dataset/      → YOLOv8 pest classifier (Aphid, Army Worm, Leaf Miner, Spider Mite)
        └──► generated_crops/   → Groundnut only: leaf crops extracted from Uncontrolled
                                  whole-plant photos before disease-class sorting
```

### How `final_combined_datasets/` was built

Multiple datasets were downloaded as `.zip` archives from Kaggle and other dataset-hosting sites (e.g. Mendeley Data). For each crop, the downloaded datasets were sorted and merged into two environment categories:

- **Closed/Controlled Environment (CE):** images with a clear/clean background, one leaf per photo.
- **Uncontrolled Environment (UE):** field-captured images, multiple leaves visible per photo (natural background — soil, hand, other leaves/branches).

Datasets that fit a crop's CE definition were merged together into that crop's CE folder; datasets fitting the UE definition were merged into the UE folder. This is why some crops have more than one CE or UE source combined into a single renamed folder (see Section 2).

---

## 2. Raw Dataset Sources (by crop)

Each CE/UE folder below may be a merge of more than one downloaded zip that fit that environment's definition (clear background + single leaf = CE, field photo + multiple leaves = UE), not necessarily a single dataset.

**Candidate list methodology:** the tables below are built from browsing history (Kaggle/Mendeley/Roboflow visits). Deduplication is done two ways: (1) exact duplicate URLs visited on different dates are merged into one entry, (2) entries with near-identical titles/near-identical class lists from different authors are flagged as **"possible duplicate content"** and only counted once — but since this can't be verified without comparing the actual image files, treat those flags as a starting point to check, not a certainty. Code notebooks (not datasets) and clearly unrelated history items (Leaflet.js docs, Overleaf, India GeoJSON, the OpenCV leaf-detection code repo) are excluded entirely.

> ⚠️ **Chili vs. Pepper Bell caveat:** several "Chili"/"Chilli" datasets appear in your history (Bangladesh chili datasets on Mendeley/Kaggle). Chili and Bell Pepper are related but visually/disease-wise distinct crops — these are listed separately below and **should only be used if you intentionally sourced Chili data for the Pepper Bell class**, otherwise exclude them.

### Cotton — 2,660 images (Closed 1,373 + Uncontrolled 1,287)

| Environment | Classes | Images | Renamed folder |
|---|---|---|---|
| Closed | Alternaria Leaf Spot, Bacterial Blight, Fusarium Wilt, Healthy, Verticillium Wilt | 1,373 | `CLCE` |
| Uncontrolled | Aphids, Army worm, Bacterial Blight, Curl Virus, Fusarium Wilt, Powdery Mildew, Target spot, Healthy | 1,287 | `CLUE` |

**All Cotton datasets found in browsing history (deduplicated):**

| Dataset | Platform | Notes |
|---|---|---|
| SAR-CLD-2024: Comprehensive Dataset for Cotton Leaf Disease Detection | Mendeley (`data.mendeley.com/datasets/b3jy2p6k8w`) | Class list matches `CLCE` exactly — best match for Closed |
| Cotton Leaf Image Dataset for Disease Classification | Mendeley | Same subject as SAR-CLD-2024, possible duplicate content — verify |
| A Comprehensive Dataset of Cotton Plant Diseases | Mendeley + mirrored on IEEE DataPort | Same title on two hosts — likely one dataset, count once |
| `seroshkarim/cotton-leaf-disease-dataset` | Kaggle | Revisited Jul 24 & Jul 26 |
| `ataher/cotton-leaf-disease-dataset` | Kaggle | Same title, different author — possible duplicate content, verify |
| `raaavan/cottonleafinfection` | Kaggle | |
| `nguynphancminh/cotton-leaf-diseases-dataset` | Kaggle | "Cotton leaf image dataset (Shamim Ripon)" |
| `dhamur/cotton-plant-disease` | Kaggle | |
| `ishratanika/cotton-leaf` | Kaggle | |
| CotLeaf-1 / CotLeaf-2 | CSIRO Data Access Portal | Leaf **surface imaging** dataset — different image type, likely not what was used |
| "cotton leaf" Roboflow project (`universe.roboflow.com`) | Roboflow | Revisited repeatedly over many weeks — looks like **your own annotation workspace**, not a downloaded dataset |

---

### Groundnut — 7,343 images (Field Closeup 1,720 + Uncontrolled 3,172 + Created 2,451)

| Environment | Classes | Images | Renamed folder |
|---|---|---|---|
| Field Closeup | Alternaria Leaf Spot, Healthy, Leaf Spot (Early+Late combined), Rosette, Rust | 1,720 | `GLFCE` |
| Uncontrolled | early_leaf_spot, healthy leaf, late leaf spot, nutrition deficiency, rust | 3,172 | `GLUE` |
| Created (leaf crops from GLUE) | early_leaf_spot_1, early_rust_1, healthy_leaf_1, late_leaf_spot_1, nutrition_deficiency_1, rust_1 | 2,451 | `GLCDfGLUE` |

The "Created" set is **not an independent download** — it's leaf images auto-cropped out of the GLUE whole-plant photos (via `generated_crops/groundnut/leaf_crops/`), then re-sorted by disease class.

**All Groundnut datasets found in browsing history (deduplicated):**

| Dataset | Platform | Notes |
|---|---|---|
| `warcoder/groundnut-plant-leaf-data` | Kaggle | Candidate for Field Closeup |
| `pandiyaraj2004/groundnut-leaf` | Kaggle | Candidate for Uncontrolled |
| `muhammadazeemabbas/groundnut-leaves-dataset` | Kaggle | Revisited multiple times (Jul 27, again during notebook work Aug 19) — strong candidate |
| `avyaya/groundnut` | Kaggle | |
| Dataset of groundnut plant leaf images for classification and detection | Mendeley (also indexed on PMC) | Mendeley + PMC listing are the same dataset — count once |

---

### Pepper Bell — 9,574 images (Closed 9,283 + Uncontrolled 291)

| Environment | Classes | Images | Renamed folder |
|---|---|---|---|
| Closed | Bacterial Spot, Cercospora Leaf Spot, Healthy, Leaf Curl, Nutrition Deficiency, Powdery Mildew | 9,283 | `PBCE` |
| Uncontrolled | Aphid, Bacterial spot, Blossom end rot, Burn, Edema, Healthy, Leaf curl, Leaf miners, Nutrient deficiency, Powdery mildew, Spider mite, Thrips | 291 | `PBUE` |

**All Pepper Bell datasets found in browsing history (deduplicated):**

| Dataset | Platform | Notes |
|---|---|---|
| `kafilatmusa11/pepper-bell-leaf-disease` | Kaggle | Large-scale, matches high counts (e.g. 4,901 Bacterial Spot) — strong candidate for Closed |
| `shuvokumarbasak2030/pepper-leaf-diseases-plant-village-augmented-data` | Kaggle | PlantVillage-augmented — possible Closed source |
| `arjuntejaswi/plant-village` | Kaggle | General PlantVillage mirror, includes a pepper bell subset |
| `mohitsingh1804/plantvillage` | Kaggle | Another PlantVillage mirror — likely duplicate content of the above, count once |
| `alexanderuzhinskiy/pepper-disease-classification-dataset-doctorp` | Kaggle | Smaller curated set — possible match for the small (291-image) Uncontrolled set |
| `ziya07/solanaceae-family-leaves-dataset` | Kaggle | Multi-crop (Solanaceae family) — may include pepper images |
| `jamijubaer/pepper-bell-disease-classification` | Kaggle (code notebook) | Reference code only, not a dataset — excluded from image counts |

**Chili datasets also in history — intentionally used as part of the Pepper Bell class:**

| Dataset | Platform |
|---|---|
| Chili Leaf Disease Dataset (Anthracnose/Cercospora/Leaf Curl, Bangladesh) | Mendeley (`data.mendeley.com/datasets/wzc6r6w5w5`) |
| Chili Plant Leaf Disease and Growth Stage Dataset (Bangladesh) | Mendeley (`data.mendeley.com/datasets/w9mr3vf56s`) |
| Chilli Leaf Disease Image Dataset for Classification and Early Diagnosis | Mendeley |
| `mahaninghubballi/chilli-leaf-dataset`, `taiburrahaman/chillileafdataset-trainvaltest`, `ahmadkurniawansyarif/chillis-leaf-white-backgroud-cropped`, `mehedi119/chilli-leaf`, `ahmadalmahsiri/chili-plant-disease` | Kaggle |

---

### Potato — 7,834 images (Uncontrolled 3,076 + Closed 4,758)

| Environment | Classes | Images | Renamed folder |
|---|---|---|---|
| Uncontrolled | Bacteria, Fungi, Healthy, Nematode, Pest, Phytopthora, Virus | 3,076 | `PLUE` |
| Closed | Early Blight, Healthy, Late Blight | 4,758 | `PLCE` |

**All Potato datasets found in browsing history (deduplicated):**

| Dataset | Platform | Notes |
|---|---|---|
| Potato Leaf Disease Dataset in Uncontrolled Environment | Mendeley (`data.mendeley.com/datasets/ptz377bwb8`) | Class names (Bacteria/Fungi/Nematode/Pest/Phytopthora/Virus) match `PLUE` exactly — strongest match for Uncontrolled |
| `muhammadardiputra/potato-leaf-disease-dataset` | Kaggle | Revisited Jul 24, 28, Aug 4 |
| `nirmalsankalana/potato-leaf-disease-dataset` | Kaggle | |
| `nirmalsankalana/plant-diseases-training-dataset` | Kaggle | General multi-crop set, same author as above |
| `rizwan123456789/potato-disease-leaf-datasetpld` | Kaggle | |
| `betulbny/potato` | Kaggle | |
| `nirmalsankalana/potato-leaf-healthy-and-late-blight` | Kaggle | Revisited repeatedly Jul 21–24 — only 2 classes, likely **not** the 3-class Closed source |
| `krishd123/potato-leaf-disease-gallery` | Kaggle | |

---

### Tomato — 7,140 images (Uncontrolled 3,090 + Closed 4,050)

| Environment | Classes | Images | Renamed folder |
|---|---|---|---|
| Uncontrolled | Bacterial Spot, Burn Leaf, Deficiency of Phosphorus/Magnesium, Early Blight, Healthy, Late Blight, Leaf Miner, Mold Leaf, Mosaic Virus, Septoria, Spider Mite, Wealth Leaf, Yellow Curl Virus | 3,090 | `TLUE` |
| Closed | Bacterial Spot, Early Blight, Healthy, Late Blight | 4,050 | `TLCE` |

**All Tomato datasets found in browsing history (deduplicated):**

| Dataset | Platform | Notes |
|---|---|---|
| Tomato Leaf Dataset: A dataset for multiclass disease detection and classification | Mendeley | Matches unusual `TLUE` class names (Wealth Leaf, Mold Leaf) — strongest match for Uncontrolled |
| `ashishmotwani/tomato` (Tomato Leaves Dataset) | Kaggle | |
| `kaustubhb999/tomatoleaf` | Kaggle | 10-class PlantVillage-style — candidate for Closed |
| `zunorain/tomato-dataset-v2` | Kaggle | |
| `muqaddasejaz/tomato-leaf-diseases-dataset` | Kaggle | |
| `ahmadzargar/tomato-leaf-disease-dataset-segmented` | Kaggle | Segmented variant |
| `sattineni/tomato-leaf` | Kaggle | |
| `syedhashirali260/tomato-leaf-disease-dataset-6-classes` | Kaggle | |
| `cookiefinder/tomato-disease-multiple-sources` | Kaggle | |
| `shylesh101/tomato-leaf-disease` | Kaggle | |
| `ayaangattuwar/tomato-leaf` | Kaggle | |
| `charuchaudhry/plantvillage-tomato-leaf-dataset` | Kaggle | PlantVillage subset — likely duplicate content of `kaustubhb999`'s / `arjuntejaswi`'s PlantVillage mirrors |
| `yusufmurtaza01/tomato-leaf-disease` | Kaggle | |
| `farukalam/tomato-leaf-diseases-detection-computer-vision` | Kaggle | |
| `vasantharank/tomato-leaf-disease-detection-yolov8-dataset` | Kaggle | YOLO-format — likely for detection experiments rather than this classifier |

**Multi-crop / general datasets also in history** (may have been used as a supplementary source across several crops — verify before listing under a specific crop):

| Dataset | Platform | Notes |
|---|---|---|
| Plant Leaf Disease MasterDataset (19 Crops) | Kaggle (`adiithape1/...`) | |
| Master Plant Disease Dataset | Kaggle (`harisri2005/plant-disease-processed`) | Similar concept/name to the above — possible duplicate content |
| PlantDoc Dataset | Kaggle (`abdulhasibuddin/plant-doc-dataset` **and** `andresmgs/plantdec`) | Both are PlantDoc mirrors — same underlying dataset, count once |
| Plant Disease Dataset | Kaggle (`rashidthihan/plant-disease-dataset`) | |
| PlantifyDr Dataset | Kaggle (`lavaman151/plantifydr-dataset`) | |
| Plant Disease Detection | Kaggle (`karagwaanntreasure/plant-disease-detection`) | |
| PEST_AI Plant Leaf Disease Recognition Dataset | Kaggle (`ibrahimagabardiop/niayes-crops-disease-v2`) | Pest-focused — may relate to `pest_dataset/` instead |
| Leaf Type Detection | Kaggle (`andrewmvd/leaf-type-detection`) | Species/leaf-type detection, not disease — likely unrelated to this project, exclude |

---

**Total raw dataset: 34,548–34,552 images across 5 crops.**

---

## 3. Folder Renaming

Full source folder names were renamed to short codes for path-length/consistency reasons. Mapping is preserved in `name_change_of_folders.txt`. Pattern: `<Crop><Environment abbreviation>` for the parent folder, `<Class abbreviation>` for each class subfolder — e.g. `Cotton Leaf Closed Environment → Alternaria Leaf Spot` became `CLCE → ALS`.

Environment folder codes:
| Code | Meaning |
|---|---|
| `CLCE` / `CLUE` | Cotton Leaf Closed / Uncontrolled Environment |
| `GLFCE` / `GLUE` / `GLCDfGLUE` | Groundnut Leaf Field Closeup / Uncontrolled / Created-from-Uncontrolled |
| `PBCE` / `PBUE` | Pepper Bell Closed / Uncontrolled Environment |
| `PLCE` / `PLUE` | Potato Leaf Closed / Uncontrolled Environment |
| `TLCE` / `TLUE` | Tomato Leaf Closed / Uncontrolled Environment |

---

## 4. Derived Training Datasets

### 4.1 Crop Identifier — `dataset_split/`
Collapses all disease/pest classes down to **crop-level labels only** (Cotton, Groundnut, Pepper Bell, Potato, Tomato), split train/val/test (~70/15/15). Used for `02_train_crop_identifier.ipynb`. Achieved 99.48% val accuracy / 99.31% test macro-F1 (per stored training results).

### 4.2 Disease Classifiers — `disease_dataset/`
Per-crop disease-class folders, pest-symptom classes (Aphids, Army Worm, Leaf Miner(s), Spider Mite, Thrips) **excluded** and routed to the pest dataset instead. Some raw classes were merged for the final label set (e.g. Potato's `Phytopthora` folded into `Late Blight`; Groundnut's `early_leaf_spot`/`late_leaf_spot` folded into a single `Leaf Spot`). Split train/val/test per crop. Used for `07_train_disease_classifier.ipynb`.

### 4.3 Pest Classifier — `pest_dataset/`
Aphid, Army Worm, Leaf Miner, Spider Mite pulled out of the Uncontrolled Environment sets across crops (mainly Tomato/Cotton/Pepper Bell), split train/val/test. Used with YOLOv8 (`11_train_pest_classifier.ipynb`, `yolov8n-cls.pt` base weights).

### 4.4 Groundnut Created Dataset — `generated_crops/groundnut/leaf_crops/`
Leaf-level crops extracted from GLUE whole-plant field photos (background: soil/hand/other leaves), then sorted into disease classes to form `GLCDfGLUE`.

---

## 5. Retraining / Production Data (separate from the above)

Per `mlops_training_guide.md`, production retraining pulls a **different** dataset — farmer/expert-labeled predictions exported live from the platform via `/admin/dataset/export`, not the original Kaggle/Mendeley sources above. Keep this distinction clear in the repo: the datasets in this document are the **original training data**; the export pipeline produces **new labeled data from real usage** for periodic retraining.

---

## 6. Class Merge / Exclusion Notes

- Pest-symptom classes (Aphids, Army Worm, Leaf Miner(s), Spider Mite, Thrips) excluded from all disease classifiers, reserved for the dedicated pest-detection model.
- Potato: `Phytopthora` merged into `Late Blight`.
- Groundnut: `early_leaf_spot` + `late_leaf_spot` merged into single `Leaf Spot` class for the Field Closeup / disease_dataset set.
- Cross-environment merges (Closed + Uncontrolled) were done per crop to reach the final `disease_dataset/` class list where classes overlapped (e.g. Cotton's `Bacterial Blight`, `Fusarium Wilt`, `Healthy` appear in both source environments and were combined).
- Pepper Bell's class set intentionally combines Bell Pepper and Chili source datasets (see Section 2) into a single `Pepper Bell` label — a deliberate scope decision for this project, not a species mislabel.
