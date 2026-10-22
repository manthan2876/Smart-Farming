# Privacy Policy

**Project:** Smart Farming Platform  
**Effective Date:** 22 October 2026  
**Regulatory Compliance:** Digital Personal Data Protection (DPDP) Act, 2023 (India) & General Data Protection Regulation (GDPR)  
**Institution:** Department of Information Technology, CSPIT, CHARUSAT, Gujarat, India  

---

## 1. Introduction

The Smart Farming Platform ("we", "us", or "our") respects the privacy rights of farmers, agronomic experts, and administrators. This Privacy Policy explains what personal and agricultural data we collect, how it is processed and protected, and your statutory rights regarding your personal data.

---

## 2. Information We Collect

### A. Information You Directly Provide
- **Account Identity**: Name, email address, phone number, hashed password, and preferred regional language (English, Gujarati, or Hindi).
- **Farm Profile**: Farm name, geographic location description, acreage, crop cultivation history, and GeoJSON boundary coordinates.

### B. Information Collected Automatically
- **Field Imagery**: Leaf photographs uploaded via camera or gallery for foliar disease diagnosis.
- **Geospatial Location Data**: GPS latitude and longitude (captured with user device permission) to retrieve ambient temperature, humidity, and precipitation risk forecasts.
- **System Telemetry**: Request IDs, device OS version, and diagnostic logs (used strictly for error resolution and performance optimization).

---

## 3. Lawful Purpose of Data Processing

We process your data strictly for legitimate agricultural and academic research purposes:
1. **Executing Leaf Diagnosis**: Processing images via our computer vision pipeline to detect crop species, foliar diseases, and pests.
2. **Localizing Advisory**: Delivering audio narration (Edge-TTS) and text recommendations in your chosen regional language (Gujarati, Hindi, or English).
3. **Proactive Disaster Alerts**: Matching GPS coordinates with OpenWeatherMap data to alert farmers to imminent frost, heatwave, or unseasonal rainfall risks.
4. **Continuous Model Improvement**: Adding verified expert-adjudicated images to the training corpus to improve accuracy for Indian agricultural conditions.

---

## 4. Data Storage, Security & Sharing

- **Zero Commercial Monetization**: We do not sell, rent, monetize, or trade farmer personal data or field boundary coordinates to third-party advertisers or commercial brokers.
- **Encryption**: All network communication is encrypted using TLS 1.3. Database records are stored within Supabase PostgreSQL with role-based row-level permissions.
- **Storage Backend**: Raw and processed foliar images are stored with time-bounded, cryptographically signed URLs (default 900 seconds expiry).

---

## 5. Your Rights Under DPDP Act 2023

You have the following rights regarding your personal data:
1. **Right to Access & Summary**: You may view your complete scan history and personal profile at any time through the dashboard.
2. **Right to Correction**: You may update inaccurate farm boundaries, crop histories, or contact numbers via the settings interface.
3. **Right to Erasure / Account Deletion**: You have the right to request deletion of your account and associated personal data by contacting platform administrators or invoking the profile deletion endpoint.

---

## 6. Grievance Redressal & Contact

For questions regarding this policy or to exercise your privacy rights, contact:

**Data Protection & Grievance Officer**  
Department of Information Technology, CSPIT  
Charotar University of Science and Technology (CHARUSAT)  
Changa, Anand, Gujarat - 388421, India  
Email: `smartfarming.project@charusat.ac.in`

