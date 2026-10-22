# User & Administrator Operations Manual
## AI-Powered Smart Farming Platform

**Degree:** Bachelor of Technology (B.Tech) in Information Technology  
**Department:** Department of Information Technology  
**Institute:** Chandubhai S. Patel Institute of Technology (CSPIT)  
**University:** Charotar University of Science and Technology (CHARUSAT), Changa, Gujarat, India  
**Academic Year:** 2026 – 2027  

**Student Contributors:**  
- **Manthan Kuvadiya** (Full-Stack Engineering & MLOps Pipeline)  
- **Kunj Lunagariya** (Computer Vision, Deep Learning & Backend Services)  

**Project Guide:**  
- **Prof. Rajnik Katariya**, Assistant Professor, IT Department, CSPIT, CHARUSAT  

**Document Version:** 1.0 (Final Academic Baseline)  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started & Supported Platforms](#2-getting-started--supported-platforms)
3. [Farmer User Guide](#3-farmer-user-guide)
   - 3.1 [Creating an Account & Sign In](#31-creating-an-account--sign-in)
   - 3.2 [One-Tap Guest Diagnosis Mode](#32-one-tap-guest-diagnosis-mode)
   - 3.3 [Taking a High-Quality Leaf Photo](#33-taking-a-high-quality-leaf-photo)
   - 3.4 [Understanding Diagnostic Results](#34-understanding-diagnostic-results)
   - 3.5 [Vernacular Language Switching & Audio Playback](#35-vernacular-language-switching--audio-playback)
   - 3.6 [Mapping Farm & Plot Boundaries](#36-mapping-farm--plot-boundaries)
   - 3.7 [Proactive Weather Alerts](#37-proactive-weather-alerts)
   - 3.8 [Submitting Field Feedback](#38-submitting-field-feedback)
4. [Agricultural Expert User Guide](#4-agricultural-expert-user-guide)
   - 4.1 [Accessing the Agronomist Queue](#41-accessing-the-agronomist-queue)
   - 4.2 [Claiming a Scan Review (Atomic Lease Lock)](#42-claiming-a-scan-review-atomic-lease-lock)
   - 4.3 [Adjudicating Findings & Prescribing Treatment](#43-adjudicating-findings--prescribing-treatment)
5. [Administrator Operations Manual](#5-administrator-operations-manual)
   - 5.1 [Admin Telemetry & Health Dashboard](#51-admin-telemetry--health-dashboard)
   - 5.2 [Model Registry & Instant Version Rollback](#52-model-registry--instant-version-rollback)
   - 5.3 [MLOps Continuous Retraining Data Export](#53-mlops-continuous-retraining-data-export)
6. [Troubleshooting & FAQ](#6-troubleshooting--faq)

---

## 1. Introduction

The **AI-Powered Smart Farming Platform** is designed to provide immediate, actionable foliar disease diagnostics and ICAR/KVK-grounded agronomic advisory to farmers across India.

The platform is available as:
1. **Responsive Web Application**: Accessible on any mobile or desktop web browser (`https://smart-farming-dashboard.vercel.app`).
2. **Flutter Mobile Application**: Native Android and iOS app with offline queue support and camera viewfinder assistance.

---

## 2. Getting Started & Supported Platforms

### Supported Web Browsers
- Google Chrome, Mozilla Firefox, Apple Safari, Microsoft Edge.
- Camera access permission is requested when capturing leaf photos directly through the browser.

### Supported Mobile Devices
- **Android**: Version 8.0 (Oreo) and above.
- **iOS**: Version 14.0 and above.
- Minimum 2GB RAM and 50MB free internal storage.

---

## 3. Farmer User Guide

### 3.1 Creating an Account & Sign In
1. Open the application.
2. Select your preferred regional language on the splash screen: **English**, **ગુજરાતી (Gujarati)**, or **हिन्दी (Hindi)**.
3. Enter your 10-digit mobile phone number or email address.
4. If you are a new user, click **Register**, enter your farm location (e.g., *Anand, Gujarat*), and choose your primary crops.
5. Sign in securely. Your session will remain active for 30 days via secure refresh token rotation.

### 3.2 One-Tap Guest Diagnosis Mode
If you do not wish to create an account immediately:
1. Tap **Try 1 Free Diagnostic Scan (Guest)** on the login screen.
2. The diagnosis will execute with complete 7-stage AI rigor.
3. After viewing your treatment plan, you can register with one click to permanently save the result to your farm history.

### 3.3 Taking a High-Quality Leaf Photo
To ensure high classification confidence:
- **Balanced Sunlight**: Capture photos in daylight. Avoid deep shadows or night shots under artificial flashlight.
- **Fill the Frame**: Place the diseased leaf squarely inside the camera viewfinder box.
- **Hold Steady**: The OpenCV quality gate rejects blurred photos (Laplacian variance < 50.0). If you see a *"Hold phone steady"* prompt, retake the photo without camera shake.
- **Isolate Single Leaf**: Avoid photographing large clusters of mixed background weeds.

### 3.4 Understanding Diagnostic Results
Upon completing inference (average 2 to 3.5 seconds), the screen displays:
- **Crop Identified**: E.g., *Tomato* (EfficientNet-B0 prediction).
- **Disease Identified**: E.g., *Early Blight (Alternaria solani)*.
- **Confidence Rating**:
  - **High (>85%)**: Certified AI classification.
  - **Medium (70%–85%)**: Verified guidance provided.
  - **Low (<70%)**: Automatically escalated to an Agricultural Expert for human verification.
- **Infection Severity**: Visual lesion percentage (Low <25%, Moderate 25%–55%, Severe >55%).
- **Pest Detection**: Flags visible vector pests (e.g., Aphids) detected by YOLOv8.
- **4-Point Treatment Advisory**:
  1. *Immediate Action*: Urgent field hygiene tasks.
  2. *Chemical / Bio Treatment*: Exact ICAR formulation (e.g., Mancozeb @ 2.5 g/L).
  3. *Prevention*: Long-term crop spacing and crop rotation tips.
  4. *Monitoring*: Follow-up foliage inspection schedule.

### 3.5 Vernacular Language Switching & Audio Playback
- **Language Toggle**: Tap the language button in the top navigation bar at any time to switch the entire user interface and diagnostic recommendations between Gujarati, Hindi, and English.
- **Listen to Advisory (TTS)**: Tap the **Speaker Icon** on any diagnosis card to listen to the advice narrated in clear regional speech with numbers and dosages correctly pronounced.

### 3.6 Mapping Farm & Plot Boundaries
1. Navigate to the **My Farm** tab.
2. Tap **Set Farm Boundary**.
3. Use the interactive satellite map to tap the corners of your farm. The system will automatically close the polygon ring and calculate your farm acreage in real-time.
4. Tap **Add Crop Plot** inside your farm to designate individual crop zones (e.g., *Plot 1: Cotton, 2.5 Acres*).

### 3.7 Proactive Weather Alerts
The **Alerts** tab continuously monitors 5-day forecasts for your specific GPS coordinates:
- **Blight Risk**: Alerts when humidity exceeds 75% during warm weather.
- **Heat Stress**: Warns if temperatures exceed 38°C for more than 3 consecutive periods.
- **Heavy Rain**: Notifies if rainfall exceeding 20mm is forecast, prompting farmers to clear field drainage channels.

### 3.8 Submitting Field Feedback
At the bottom of every diagnostic result card:
- Tap **Thumbs Up (Correct)** if the diagnosis matches your field observation.
- Tap **Thumbs Down (Incorrect)** and enter a brief note if you suspect a different issue.
- Submissions are reviewed by agronomists and incorporated into continuous model retraining.

---

## 4. Agricultural Expert User Guide

### 4.1 Accessing the Agronomist Queue
1. Log in with your registered Expert credentials.
2. Navigate to **Expert Review Queue** (`/expert/queue`).
3. The queue displays all farmer scans that triggered low-confidence warnings (<0.70) or farmer-requested reassessments.

### 4.2 Claiming a Scan Review (Atomic Lease Lock)
- To prevent conflicting advice from multiple agronomists, tap **Claim Review**.
- The system establishes an atomic **15-minute lease lock**. Other agronomists will see the review marked as *Claimed by you*.
- If you cannot complete the review, tap **Release Review** to return it to the shared queue.

### 4.3 Adjudicating Findings & Prescribing Treatment
1. Inspect the high-resolution leaf image, automated findings, and farmer plot history.
2. Choose a review action:
   - **Confirm AI Findings**: Approves the automated classification.
   - **Override / Correct Findings**: Select the correct pathogen from the certified disease list and adjust the severity score.
   - **Request Rescan**: Instructs the farmer to take a clearer photograph.
3. Write custom guidance in the **Agronomist Guidance** box.
4. Check **Flag for Retraining** if this sample represents an informative edge case.
5. Tap **Submit Review**. The farmer immediately receives an alert notification and personalized advice in their preferred language.

---

## 5. Administrator Operations Manual

### 5.1 Admin Telemetry & Health Dashboard
Access `/admin/metrics` to monitor:
- **System Health**: Database connection pool status, Redis latency, and AI microservice response time.
- **Confidence Drift**: Distribution of high, medium, and low confidence scans over time.
- **Crop Distribution**: Relative percentage of Tomato, Potato, Cotton, Groundnut, and Pepper Bell scans.

### 5.2 Model Registry & Instant Version Rollback
Access `/admin/models`:
- View all deployed vision weights (`crop_identifier_v1.pth`, `disease_Cotton.pth`, etc.).
- Inspect validation accuracy, F1-scores, and training dataset size.
- **Rollback**: If a newly promoted model displays an anomaly in production, click **Rollback to Previous Version** to instantly switch active weights without taking the server offline.

### 5.3 MLOps Continuous Retraining Data Export
Access `/admin/mlops`:
1. View all accumulated `dataset_candidates` from verified expert corrections and farmer feedback.
2. Select target crops and date range.
3. Click **Export Training Dataset**. The system compiles an organized directory of raw images and verified JSON metadata with an 80/20 train/validation split.

---

## 6. Troubleshooting & FAQ

**Q1: The app says "Photo is too dark. Please take it in daylight." What should I do?**  
*A: The system requires clear illumination to distinguish fungal spots from leaf shadows. Move to outdoor natural sunlight and avoid casting your body shadow over the leaf.*

**Q2: Can I use the app without an internet connection?**  
*A: Yes! The Flutter mobile application includes an offline SQLite queue. You can photograph leaves while working offline in remote fields. When your phone reconnects to cellular data or Wi-Fi, the app automatically synchronizes your scans.*

**Q3: Does the system replace my local agricultural extension officer?**  
*A: No. The platform provides preliminary AI diagnosis and standard ICAR management practices. For chemical pesticide applications, farmers must always follow local product labels and verify recommendations with their local Krishi Vigyan Kendra (KVK).*

