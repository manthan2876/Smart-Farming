# AI-Powered Smart Farming — University Project Report & Screenshot Suite

This directory contains the university-format project report source, a compiled PDF artifact, and screenshots captured from the Smart Farming application. The report source of record is `main.tex`; compile it to regenerate the PDF.

* **Live Web Application**: [smart-farming-dashboard-green.vercel.app](https://smart-farming-dashboard-green.vercel.app/)
* **Official GitHub Repository**: [github.com/manthan2876/Smart-Farming](https://github.com/manthan2876/Smart-Farming)
* **Authors**:
  * Manthan Kuvadiya (`23it050@charusat.edu.in`)
  * Kunj Lunagariya (`23it053@charusat.edu.in`)
  * Department of Information Technology, CSPIT, CHARUSAT (Academic Year 2026–2027)
  * Project Guide: Prof. Rajnik Katariya

---

## 📁 Directory Structure

```text
Docs/report/
├── README.md                                      # This reference guide
├── main.tex                                       # University project report source with TikZ diagrams
├── main.pdf                                       # Existing compiled PDF; regenerate from main.tex
└── screenshots/                                   # High-resolution 2x Retina screenshots & AI matrices
    ├── 01_landing_page_hero.png                   # Landing page hero & inference architecture
    ├── 01_landing_page_full.png                   # Full landing page overview
    ├── 02_crops_catalog.png                       # Five-way supported crops registry
    ├── 03_services_page.png                       # Pathology detection specifications
    ├── 04_about_page.png                          # About page and academic mission
    ├── 05_login_page.png                          # Farmer & agronomist authentication portal
    ├── 06_register_page.png                       # Farmer onboarding with language selection
    ├── 07_landing_page_gujarati.png               # Gujarati vernacular navigation
    ├── 08_demo_workbench_analysis.png             # OpenCV vegetation segmentation telemetry
    ├── 09_demo_workbench_saliency.png             # Transparent AI saliency (Grad-CAM focus)
    ├── 10_demo_workbench_advisory_en.png          # Diagnostic result & 4-field advisory (EN)
    ├── 11_demo_workbench_advisory_gujarati.png    # Regional weather & spray advisory (GU)
    ├── 12_demo_workbench_potato_late_blight.png   # Severe pathology & ICAR dosage advisory
    ├── 13_about_methodology.png                   # Agricultural engineering methodology
    ├── gradcam_samples.png                        # Multi-class Grad-CAM attention heatmaps
    ├── confusion_matrix.png                       # Five-way crop identification confusion matrix
    ├── confusion_matrix_Cotton.png                # Cotton disease classifier matrix
    ├── confusion_matrix_Groundnut.png             # Groundnut disease classifier matrix
    ├── confusion_matrix_Pepper_Bell.png           # Pepper Bell disease classifier matrix
    ├── confusion_matrix_Potato.png                # Potato disease classifier matrix
    ├── confusion_matrix_Tomato.png                # Tomato disease classifier matrix
    └── confusion_matrix_pest.png                  # YOLOv8 pest classifier confusion matrix
```

---

## 📄 LaTeX Document Overview

**`main.tex`** is the university-format report. In addition to the application screenshots, TikZ figures illustrate the role hierarchy, system architecture, conceptual data model, prediction sequence and lifecycle, AI pipeline, advisory flow, and MLOps process.

---

## 🛠️ How to Compile

### On Overleaf:
1. Create a new project on [Overleaf](https://www.overleaf.com/).
2. Upload `main.tex`, the `logos/` directory, and the `screenshots/` directory.
3. Select `pdfLaTeX` as the compiler and click **Recompile**.

### Locally (CLI):
```bash
latexmk -pdf main.tex
```
