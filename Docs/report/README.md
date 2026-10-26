# AI-Powered Smart Farming — Academic IEEE Report & Screenshot Suite

This directory contains the IEEE conference paper source code, the compiled PDF, and high-resolution screenshots captured directly from the live production deployment.

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
├── Smart_Farming_IEEE_Report_Updated.tex          # Original LaTeX document (copied from Downloads)
├── Smart_Farming_IEEE_Report_Updated.pdf          # Pre-compiled PDF report (copied from Downloads)
├── Smart_Farming_IEEE_Report_With_Screenshots.tex # Enriched LaTeX document with embedded figures
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

## 📄 LaTeX Documents Overview

1. **`Smart_Farming_IEEE_Report_Updated.tex`**:
   The exact baseline conference document imported from your `Downloads` directory. It uses TikZ for architecture diagrams and keeps Appendix A as a checklist table.

2. **`Smart_Farming_IEEE_Report_With_Screenshots.tex`**:
   An enriched edition pre-configured with `\graphicspath{{screenshots/}}` that integrates:
   - **Fig. 4 (`fig:crops-catalog`)** in Section IV: Supported crop registry (`02_crops_catalog.png`).
   - **Fig. 7 (`fig:prediction-advisory`)** in Section VI: Web diagnostic result & 4-field advisory (`10_demo_workbench_advisory_en.png`).
   - **Fig. 8 (`fig:saliency-and-vernacular`)** in Section VI: Two-column subfigure comparison of Grad-CAM attention (`09_demo_workbench_saliency.png`) and Gujarati regional advisory (`11_demo_workbench_advisory_gujarati.png`).
   - **Fig. 10 (`fig:platform-gallery`)** in Appendix A: Four-panel platform showcase displaying landing architecture, OpenCV segmentation, onboarding, and ICAR dosage advisory.

---

## 🛠️ How to Compile

### On Overleaf:
1. Create a new project on [Overleaf](https://www.overleaf.com/).
2. Upload `Smart_Farming_IEEE_Report_With_Screenshots.tex` and the `screenshots/` directory.
3. Select `pdfLaTeX` as the compiler and click **Recompile**.

> **Formatting Notes**:
> - **Figure 1 (TikZ Architecture)**: Formatted with clean planar orthogonal routing, wide 17.2\,cm coordinate distribution, protective `fill=white` label shields, and 0.82\,cm vertical clearance below the infrastructure tier to ensure zero box or text overlap.
> - **Table Formatting**: All tables are built with `tabularx` (`\textwidth` for two-column spanning tables and `\columnwidth` for single-column tables) with explicit `\caption{...}` and `\label{...}`.
> - **API Endpoints (Table III)**: Re-ordered with `Method` first, dedicated 6.6\,cm monospace `Endpoint / Path`, and auto-wrapping purpose descriptions to guarantee zero column collision or text overflow.
> - **Underscore Escaping**: All code identifiers and URLs outside math mode have their underscores escaped (`\_`) to prevent `Missing $ inserted` compilation errors.

### Locally (CLI):
```bash
pdflatex Smart_Farming_IEEE_Report_With_Screenshots.tex
pdflatex Smart_Farming_IEEE_Report_With_Screenshots.tex
```
*(Running twice resolves cross-references and figure numbers).*

