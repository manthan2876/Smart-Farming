# Smart Farming — Landing Page UI/UX Specification

For your project, the **Landing Page should be a public-facing product introduction**, not the farmer dashboard.

One important distinction from your roadmap: the roadmap explicitly specifies `/login`, `/register`, `/upload`, `/result/:id`, `/history`, `/profile`, and `/admin`, but it **does not explicitly define a landing-page design or route**. 

So below, I’ll separate what is **roadmap-supported** from my **UX recommendation**.

---

# 1. Screen Overview

### Screen name

**Landing Page**

### Recommended route

```text
/
```

### Access

```text
Public
```

No authentication required.

### Primary objective

The landing page should answer these questions within a few seconds:

1. **What is Smart Farming?**
2. **Who is it for?**
3. **What problem does it solve?**
4. **How does it work?**
5. **Why should I trust it?**
6. **How do I try it?**

Your project is fundamentally an AI pipeline where a farmer uploads a leaf photo, preprocessing validates it, AI identifies crop/disease/severity/pests, and the recommendation layer produces farmer-readable advice. 

Therefore, the landing page should revolve around exactly that journey.

---

# 2. Main Design Concept

I recommend this positioning:

> **AI-powered crop health diagnosis and actionable farming guidance.**

The visual story should be:

```text
                    FARMER
                       ↓
                  📷 LEAF PHOTO
                       ↓
                 🤖 AI ANALYSIS
                       ↓
            ┌──────────┼──────────┐
            ↓          ↓          ↓
          CROP       DISEASE    SEVERITY
            │          │          │
            └──────────┼──────────┘
                       ↓
                  🐛 PEST CHECK
                       ↓
                  🌦 FARM CONTEXT
                       ↓
                🌱 ACTIONABLE ADVICE
```

This is much stronger than a generic hero saying:

> "Welcome to Smart Farming."

---

# 3. Complete Landing Page Structure

I recommend:

```text
/
│
├── Navbar
│
├── Hero
│
├── Trust / Capability Strip
│
├── How It Works
│
├── AI Diagnosis Features
│
├── Explainable AI
│
├── Actionable Recommendations
│
├── Farm Context
│
├── Responsible AI / Expert Review
│
├── Languages
│
├── CTA
│
└── Footer
```

The landing page should be approximately **7–9 sections**, not 15+ sections.

You don't want it to feel like a marketing website disconnected from your actual product.

---

# 4. Navbar

## Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming        Features  How It Works  About       │
│                                                              │
│                         ગુજરાતી  हिन्दी  English             │
│                                                              │
│                         [ Login ] [ Get Started ]             │
└──────────────────────────────────────────────────────────────┘
```

### Left

Logo:

```text
🌱 Smart Farming
```

You can later replace the emoji with your actual SVG logo.

### Center

Navigation:

```text
Features
How It Works
Why Smart Farming
```

I would **not** add too many links.

Don't put:

```text
Dashboard
History
Admin
Models
MLOps
```

in the public navbar.

Those are authenticated/application features.

---

# 5. Navbar Behavior

### Desktop

Full navbar.

### Tablet

Reduce:

```text
Features
How It Works
Login
Get Started
```

### Mobile

```text
🌱 Smart Farming                       ☰
```

Clicking the hamburger opens:

```text
Features
How It Works
Why Smart Farming

English
ગુજરાતી
हिन्दी

Login
Get Started
```

---

# 6. Hero Section

This is the **most important section**.

## Recommended layout

Two-column design:

```text
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  AI-POWERED CROP HEALTH                     ┌─────────────┐ │
│                                              │             │ │
│  Know what's wrong.                         │   FARMER    │ │
│  Know what to do.                           │   + LEAF    │ │
│                                              │             │ │
│  Detect crop diseases, assess severity,      │    IMAGE    │ │
│  identify pests and receive actionable      │             │ │
│  farming guidance from one image.            │  AI overlay │ │
│                                              │             │ │
│  [ Scan Your Crop ] [ Explore How It Works ]│             │ │
│                                              └─────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

# 7. Hero Copy

I recommend:

### Eyebrow

```text
AI-POWERED CROP HEALTH
```

### Main heading

> **Know what's wrong. Know what to do.**

This is stronger than:

> "Revolutionizing Agriculture with AI"

because it communicates the actual user value.

### Supporting text

> Upload a crop leaf photo and let Smart Farming analyze crop type, disease, severity and pests — then turn the results into practical farming recommendations.

This is directly aligned with your actual pipeline. 

---

# 8. Hero Buttons

### Primary

```text
[ 📷 Scan Your Crop ]
```

Click:

```text
/
 ↓
/login
```

if authentication is required before `/predict`.

Your roadmap defines `/predict` as authenticated, so the frontend should not imply that an unauthenticated visitor can directly execute a diagnosis. 

### Secondary

```text
[ How It Works ↓ ]
```

Scrolls to the How It Works section.

---

# 9. Hero Visual

Don't use a generic farm landscape as the main visual.

The visual should communicate **AI diagnosis**.

I recommend a composition like:

```text
               ┌─────────────────────────┐
               │                         │
               │      Tomato Leaf        │
               │                         │
               │   🔴 affected region    │
               │                         │
               └─────────────────────────┘
                         │
                 AI ANALYSIS
                         │
          ┌──────────────┼──────────────┐
          │              │              │
       Tomato       Early Blight      32%
        98%             96%          Moderate
```

The heatmap/attention concept is appropriate because your project uses Grad-CAM to explain predictions. 

---

# 10. Hero Floating Result Card

Overlay a small diagnosis card on the image:

```text
┌─────────────────────────────┐
│ ✓ AI Diagnosis              │
│                             │
│ 🍅 Tomato                   │
│ 🦠 Early Blight             │
│                             │
│ Confidence        96%       │
│ Severity          Moderate  │
│                             │
│ ✓ Recommendation ready      │
└─────────────────────────────┘
```

This instantly tells the visitor what the product actually does.

---

# 11. Trust / Capability Strip

Immediately below the hero:

```text
┌────────────┬────────────┬────────────┬────────────┐
│ 🌱 Crop    │ 🦠 Disease │ 📊 Severity │ 🐛 Pest    │
│ Detection  │ Detection   │ Analysis   │ Detection  │
└────────────┴────────────┴────────────┴────────────┘
```

These correspond to the actual AI pipeline rather than invented marketing features. 

---

# 12. Section: "One Photo. Complete Crop Analysis."

### Heading

> **One photo. Complete crop analysis.**

### Description

> Smart Farming combines image preprocessing, crop identification, disease classification, severity estimation and pest analysis into a single workflow.

Your roadmap describes exactly this sequence. 

---

## Four cards

### Card 1

```text
🌱

Crop Identification

Identify the crop from
the uploaded leaf image.
```

### Card 2

```text
🦠

Disease Detection

Identify potential crop
diseases with AI.
```

### Card 3

```text
📊

Severity Analysis

Estimate how seriously
the plant is affected.
```

### Card 4

```text
🐛

Pest Detection

Check for potential
pest presence.
```

---

# 13. Card Interaction

On hover:

```text
Card moves slightly upward
+
icon animation
+
subtle shadow
```

Don't make cards excessively animated.

Your product is a diagnostic system, so the visual language should remain professional.

---

# 14. How It Works Section

## Heading

> **From leaf photo to farming action.**

### Subtitle

> A simple workflow powered by AI.

Then show:

```text
01
📷
Upload

        ↓

02
🔍
Validate & Prepare

        ↓

03
🤖
Analyze

        ↓

04
📊
Assess Severity

        ↓

05
🌱
Get Recommendations
```

---

# 15. Step 1 — Upload

```text
01

📷 Upload a Leaf Photo

Provide a clear photo of the
affected crop leaf.
```

Your project starts with a farmer uploading a leaf photo. 

---

# 16. Step 2 — Image Quality

```text
02

🔍 Validate the Image

The system checks whether the
image is suitable for analysis.
```

You can mention:

```text
✓ Blur detection
✓ Brightness validation
✓ Leaf detection
✓ Background handling
```

These are actually part of your OpenCV preprocessing stage. 

---

# 17. Step 3 — AI Analysis

```text
03

🤖 Analyze the Crop

AI models identify crop type,
disease and potential pests.
```

Don't expose model names on the landing page.

Don't say:

> EfficientNet-B0 + EfficientNet-B2 + YOLOv8

That's useful for your technical presentation, not the farmer-facing landing page.

---

# 18. Step 4 — Severity

```text
04

📊 Understand the Severity

See how seriously the leaf
appears to be affected.
```

Visual:

```text
Healthy ─── Mild ─── Moderate ─── Severe
                         ▲
                        32%
```

---

# 19. Step 5 — Recommendation

```text
05

🌱 Take Action

Receive farmer-readable guidance
for treatment, irrigation,
fertilizer and prevention.
```

Your project explicitly turns raw predictions into farmer-readable recommendations. 

---

# 20. Explainable AI Section

This should be one of your **signature sections**.

## Heading

> **Don't just trust the AI. See why.**

### Supporting text

> Smart Farming can visualize the regions of the leaf that contributed to the model's prediction, helping make the diagnosis easier to understand.

Your roadmap specifically identifies Grad-CAM heatmap overlays as the explainability mechanism. 

---

## Visual

Use a before/after slider:

```text
┌────────────────────┬────────────────────┐
│                    │                    │
│   Original Leaf    │   AI Attention     │
│                    │                    │
│       🍃           │      🔴🍃          │
│                    │                    │
└────────────────────┴────────────────────┘

          ← Drag to compare →
```

---

# 21. Explainability Result Card

Beside the image:

```text
AI Diagnosis

Early Blight

96% confidence

Why?

• Relevant affected regions highlighted
• Visual patterns used by the model
• Diagnosis shown with confidence
```

Important: don't promise specific "evidence" such as brown lesions unless your backend actually produces those evidence statements. Your roadmap supports the heatmap; a generated evidence list is an additional UI/backend capability. 

---

# 22. Recommendation Section

## Heading

> **From diagnosis to action.**

### Subtitle

> Understanding the problem is only the first step. Smart Farming turns AI results into practical next steps.

Then show four cards:

```text
┌──────────────┐ ┌──────────────┐
│ 🌿           │ │ 🧪           │
│ Fertilizer   │ │ Treatment    │
└──────────────┘ └──────────────┘

┌──────────────┐ ┌──────────────┐
│ 💧           │ │ 🛡           │
│ Irrigation   │ │ Prevention   │
└──────────────┘ └──────────────┘
```

These categories are supported by the project's recommendation design. 

---

# 23. Context-Aware Recommendation Section

This is where you can differentiate your project.

Heading:

> **Advice that considers your farm.**

Show:

```text
Crop
  +
Disease
  +
Severity
  +
Weather
  +
Location
  +
Farm History
       ↓
Personalized Recommendation
```

Your later roadmap explicitly introduces a **Farm Context Engine** that includes zone, farm history, weather and growth stage in the recommendation prompt. 

This is a very good feature to showcase on the landing page.

---

# 24. Weather Visual

For example:

```text
Current Conditions

29°C
74% Humidity
20% Rain

        ↓

AI Recommendation
"Consider current weather conditions
when planning treatment and irrigation."
```

Don't claim that every recommendation dynamically uses weather unless that integration is actually active in your deployed version.

---

# 25. Responsible AI Section

This should be another major differentiator.

## Heading

> **When AI isn't confident, it doesn't pretend.**

Visual:

```text
             AI Confidence

                 58%

              ⚠ LOW

                ↓

        Expert Review Required

                ↓

          Verified Diagnosis
```

Your roadmap specifically defines low-confidence predictions as `pending_expert_review` rather than immediately showing an answer. 

---

# 26. Responsible AI Copy

> **Confidence matters.**

> When the system cannot confidently identify a disease, the result can be sent for expert review instead of presenting uncertain advice as fact.

This is a much stronger message than claiming:

> "Our AI is 99% accurate."

Never put exaggerated accuracy claims on the landing page unless you have a defensible evaluation result for the deployed model.

---

# 27. Farmer-Friendly / Regional Language Section

Your roadmap explicitly supports English, Gujarati and Hindi. 

### Heading

> **Built for farmers, in their language.**

Show:

```text
English
"Your tomato crop shows signs
of Early Blight."

ગુજરાતી
"તમારા ટામેટાના પાકમાં
અર્લી બ્લાઇટના લક્ષણો જોવા મળે છે."

हिन्दी
"आपकी टमाटर की फसल में
अर्ली ब्लाइट के लक्षण दिखाई देते हैं।"
```

Add language switcher:

```text
[ English ] [ ગુજરાતી ] [ हिन्दी ]
```

---

# 28. Final CTA Section

This should be visually strong.

```text
┌──────────────────────────────────────────────────────┐
│                                                      │
│        Ready to understand your crop better?        │
│                                                      │
│       Upload a leaf photo and start your             │
│                  AI diagnosis.                       │
│                                                      │
│              [ Scan Your Crop → ]                    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

This should send the user into:

```text
/ → /login → /upload
```

depending on authentication state.

---

# 29. Footer

Keep it clean.

```text
┌──────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                                     │
│                                                      │
│ AI-powered crop health diagnosis and guidance.      │
│                                                      │
│ Product              Resources          Account      │
│ Features             How It Works       Login        │
│ How It Works         Documentation      Register     │
│                                                      │
│ ──────────────────────────────────────────────────── │
│                                                      │
│ Smart Farming • SIH 25099                            │
│                                                      │
│ © 2026 Smart Farming                                 │
└──────────────────────────────────────────────────────┘
```

Don't add a large list of fake social media links or unrelated sections.

---

# 30. Full Landing Page Wireframe

Putting everything together:

```text
┌─────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming        Features  How It Works  About       │
│                         English  ગુજરાતી  हिन्दी            │
│                                      [Login] [Get Started]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│              AI-POWERED CROP HEALTH                         │
│                                                             │
│        KNOW WHAT'S WRONG.                                   │
│        KNOW WHAT TO DO.                    ┌─────────────┐  │
│                                             │             │  │
│        Upload a leaf photo and let          │   LEAF      │  │
│        AI analyze your crop health.         │   IMAGE     │  │
│                                             │             │  │
│        [ Scan Your Crop ]                   │ 🔴 Heatmap  │  │
│        [ How It Works ]                     │             │  │
│                                             └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   🌱 Crop       🦠 Disease       📊 Severity       🐛 Pest │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│              ONE PHOTO. COMPLETE ANALYSIS.                  │
│                                                             │
│      [Crop]       [Disease]       [Severity]      [Pest]    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│              FROM LEAF PHOTO TO ACTION                      │
│                                                             │
│   01 Upload → 02 Validate → 03 Analyze → 04 Assess → 05 Act│
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│              DON'T JUST TRUST THE AI.                       │
│                       SEE WHY.                              │
│                                                             │
│        Original Leaf       AI Heatmap                       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                  FROM DIAGNOSIS TO ACTION                    │
│                                                             │
│       🌿 Fertilizer   🧪 Treatment                         │
│       💧 Irrigation   🛡 Prevention                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│               ADVICE THAT CONSIDERS YOUR FARM               │
│                                                             │
│     Crop + Disease + Severity + Weather + Farm History      │
│                           ↓                                 │
│                    Recommendation                           │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│           WHEN AI ISN'T CONFIDENT, IT DOESN'T PRETEND.       │
│                                                             │
│                  58% → Expert Review                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                 BUILT FOR FARMERS                           │
│                                                             │
│        English     ગુજરાતી     हिन्दी                       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│             READY TO UNDERSTAND YOUR CROP?                  │
│                                                             │
│                  [ Scan Your Crop → ]                       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ 🌱 Smart Farming                                            │
│ Features | How It Works | Login | Register                 │
│ SIH 25099                                                   │
└─────────────────────────────────────────────────────────────┘
```

---

# 31. Landing Page Component Structure

For your React/Vite implementation:

```text
src/
└── components/
    └── landing/
        ├── LandingNavbar.tsx
        ├── HeroSection.tsx
        ├── CapabilityStrip.tsx
        ├── FeatureSection.tsx
        ├── HowItWorks.tsx
        ├── ExplainableAI.tsx
        ├── RecommendationSection.tsx
        ├── FarmContextSection.tsx
        ├── ResponsibleAI.tsx
        ├── LanguageSection.tsx
        ├── FinalCTA.tsx
        └── LandingFooter.tsx
```

Page:

```text
src/pages/
└── LandingPage.tsx
```

---

# 32. Landing Page Data

You don't need API calls for most of this page.

This is important.

The landing page should be **fast and mostly static**.

```text
Landing Page
│
├── Static product information
├── Static illustrations
├── Feature descriptions
├── How-it-works
├── Explainability demo
├── Responsible AI explanation
└── CTA
```

Don't call:

```text
GET /history
GET /weather
GET /admin/metrics
```

just to populate the landing page.

Your roadmap describes the web dashboard as a thin API consumer, while the landing page itself isn't part of the specified authenticated dashboard routes. 

---

# 33. One Important UX Decision

I recommend **not putting the actual image upload widget directly in the hero**.

Instead:

```text
Hero
  ↓
[ Scan Your Crop ]
  ↓
Login/Register if required
  ↓
Upload Page
```

Why?

Because the landing page's job is:

> **Explain → Build trust → Convert**

while `/upload`'s job is:

> **Perform diagnosis**

Keeping those responsibilities separate will make your application cleaner.

---

# 34. What Makes Your Landing Page Different

Don't market Smart Farming as:

> "An AI platform for modern agriculture."

That's too generic.

Your strongest story is:

### **Image → Diagnosis → Explanation → Action**

And your differentiators are:

```text
✓ Image quality validation
✓ Crop identification
✓ Disease diagnosis
✓ Severity estimation
✓ Pest analysis
✓ Explainable AI
✓ Context-aware recommendations
✓ Low-confidence expert escalation
✓ Farmer-friendly language
✓ Feedback → monitoring → improvement
```

The first five are core to your existing pipeline; explainability, farm context and expert escalation are specifically identified as roadmap depth additions. 

---

# 35. Priority for Implementation

### P0 — Must have

```text
✓ Navbar
✓ Hero
✓ CTA
✓ Core capabilities
✓ How It Works
✓ Footer
```

### P1 — Strongly recommended

```text
✓ Explainable AI section
✓ Recommendation section
✓ Farm Context section
✓ Responsible AI section
✓ Language section
```

### P2 — Optional polish

```text
✓ Animated pipeline
✓ Before/after Grad-CAM slider
✓ Animated statistics
✓ Scroll animations
✓ Interactive diagnosis demo
```

---

# Smart Farming — Login Screen UI/UX Specification

The Login screen is the **entry point into the authenticated Smart Farming application**. According to your roadmap, `/login` is an authentication screen using the same authentication API as the mobile app, and `POST /auth/login` issues JWT access + refresh tokens. 

The roadmap also places authentication before the React dashboard, with protected routes gated through `AuthContext`. 

---

# 1. Screen Overview

### Screen name

**Login**

### Route

```text
/login
```

### Access

```text
Public
```

### Purpose

Allow an existing farmer to securely authenticate and enter the Smart Farming application.

### Primary action

```text
Login
```

### Secondary action

```text
Create an account
```

### Authentication flow

```text
Landing Page
      ↓
   Login
      ↓
POST /auth/login
      ↓
JWT access + refresh token
      ↓
AuthContext
      ↓
Authenticated application
```

The backend contract explicitly defines `POST /auth/login` for issuing the JWT access and refresh token. 

---

# 2. Recommended Overall Layout

I recommend **not** making the login page look like a generic corporate login form.

Instead, use a two-panel agricultural/AI design:

```text
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌────────────────────────┐  ┌────────────────────────────┐ │
│  │                        │  │                            │ │
│  │      🌱                │  │       Welcome back         │ │
│  │   Smart Farming        │  │                            │ │
│  │                        │  │   Sign in to your farm     │ │
│  │  AI-powered crop       │  │   intelligence dashboard.  │ │
│  │  health diagnosis      │  │                            │ │
│  │                        │  │   Phone / Email             │ │
│  │   [Leaf visual]        │  │   ┌──────────────────────┐ │ │
│  │                        │  │   │                      │ │ │
│  │  Crop • Disease •      │  │   └──────────────────────┘ │ │
│  │  Severity • Pest       │  │                            │ │
│  │                        │  │   Password                 │ │
│  │                        │  │   ┌──────────────────────┐ │ │
│  │                        │  │   │                 👁  │ │ │
│  │                        │  │   └──────────────────────┘ │ │
│  │                        │  │                            │ │
│  │                        │  │   [        Login        ] │ │
│  │                        │  │                            │ │
│  │                        │  │   Don't have an account?   │ │
│  │                        │  │   Create one               │ │
│  │                        │  │                            │ │
│  └────────────────────────┘  └────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

# 3. Left Panel — Product Identity

The left panel should communicate **what the farmer is logging into**.

### Logo

```text
🌱 Smart Farming
```

### Heading

> **Smarter decisions for healthier crops.**

### Supporting text

> AI-powered crop health analysis that helps you understand your crops and take informed action.

---

# 4. Left Panel Visual

Use a crop leaf image/illustration.

The visual should contain a subtle AI-analysis overlay:

```text
              🍃
         ╱          ╲
       ╱              ╲
      │   AI ANALYSIS  │
       ╲              ╱
         ╲          ╱

       Crop       98%
       Disease   96%
       Severity  32%
```

This reinforces your actual pipeline:

```text
Crop
 ↓
Disease
 ↓
Severity
 ↓
Pest
 ↓
Recommendation
```

Your roadmap describes these as the core AI stages. 

---

# 5. Left Panel Feature Indicators

At the bottom:

```text
✓ Crop identification
✓ Disease detection
✓ Severity analysis
✓ Farmer-readable recommendations
```

Keep this to **four items maximum**.

Don't turn the login page into another landing page.

---

# 6. Right Panel — Login Form

This is the functional portion.

### Heading

> **Welcome back**

### Subtitle

> Sign in to continue managing your crop health.

---

# 7. Login Identifier

Your roadmap specifies the registration data as:

```text
name
phone
location
language
```

and the database's `users` table includes `phone`, `name`, and `language`.  

Therefore, I recommend using:

### Label

```text
Phone Number
```

### Placeholder

```text
Enter your phone number
```

### Example

```text
+91 98765 43210
```

If your implemented `/auth/login` contract instead accepts email, change this to **Email Address**. Don't build both unless the backend explicitly supports both.

---

# 8. Password Field

### Label

```text
Password
```

### Placeholder

```text
Enter your password
```

Right-side control:

```text
👁
```

### Behavior

Default:

```text
••••••••••
```

Click eye:

```text
password123
```

Click again:

```text
••••••••••
```

---

# 9. Remember Me

I recommend **not adding a "Remember me" checkbox initially**.

Your roadmap specifies JWT access + refresh tokens and recommends keeping the access token in memory with an HTTP-only refresh cookie if supported. 

A generic:

```text
☐ Remember me
```

can encourage an implementation that conflicts with your intended token strategy.

---

# 10. Forgot Password

Your current roadmap **does not define a forgot-password endpoint**.

Therefore:

### Do NOT implement

```text
Forgot Password?
```

yet.

If you later add:

```text
POST /auth/forgot-password
POST /auth/reset-password
```

then add it to this screen.

For now, don't create a fake flow.

---

# 11. Login Button

### Button

```text
[ Login ]
```

Full width.

### Loading state

After clicking:

```text
[ ⟳ Signing in... ]
```

Disable the form while the request is in progress.

---

# 12. Login API

Frontend calls:

```http
POST /auth/login
```

The roadmap explicitly defines this endpoint. 

Conceptually:

```text
Login Form
    ↓
auth.login()
    ↓
POST /auth/login
    ↓
Backend validates credentials
    ↓
JWT access + refresh token
    ↓
AuthContext
    ↓
Navigate to application
```

---

# 13. Successful Login

On successful authentication:

```text
POST /auth/login
        ↓
200 OK
        ↓
Store authentication state
        ↓
AuthContext updated
        ↓
Navigate to dashboard
```

The roadmap says `AuthContext` should hold the JWT/current user and gate protected routes. 

### Recommended destination

```text
/dashboard
```

If your actual dashboard route is different, use that route consistently throughout the application.

---

# 14. Authentication Storage

Based on the roadmap:

### Preferred

```text
Access token
    ↓
Memory

Refresh token
    ↓
httpOnly cookie
```

if the backend supports the HTTP-only refresh-cookie mechanism. 

Avoid designing the frontend around:

```javascript
localStorage.setItem("password", ...)
```

or storing sensitive credentials.

---

# 15. Error States

This is extremely important.

Don't simply display:

```text
Login failed
```

Instead, use appropriate user-facing messages.

---

## Invalid credentials

```text
⚠ Incorrect phone number or password.
```

Don't reveal whether the phone number exists.

---

## Network error

```text
⚠ Unable to connect to Smart Farming.

Please check your internet connection and try again.
```

Button:

```text
[ Try Again ]
```

---

## Server error

```text
⚠ Something went wrong on our side.

Please try again in a moment.
```

---

## Empty phone

```text
Please enter your phone number.
```

---

## Invalid phone

```text
Please enter a valid phone number.
```

---

## Empty password

```text
Please enter your password.
```

---

# 16. Form Validation

Validation should happen **before API submission**.

### Phone

```text
Required
Valid phone format
```

### Password

```text
Required
```

Don't enforce arbitrary frontend password rules during login.

The backend should remain authoritative for credential validation.

---

# 17. Register CTA

Below the login button:

```text
Don't have an account?

[ Create an account ]
```

Click:

```text
/login
   ↓
/register
```

Your roadmap explicitly defines `/register` as the second authentication screen. 

---

# 18. Registration Screen Relationship

The Login screen and Register screen should visually belong to the same authentication system.

```text
┌─────────────────────┐
│                     │
│   Login             │
│                     │
│   Phone             │
│   Password          │
│                     │
│   [ Login ]         │
│                     │
│   Create account →  │
│                     │
└─────────────────────┘
```

Then:

```text
┌─────────────────────┐
│                     │
│   Create Account    │
│                     │
│   Name              │
│   Phone             │
│   Location          │
│   Language          │
│   Password          │
│                     │
│   [ Register ]      │
│                     │
│   ← Back to Login   │
│                     │
└─────────────────────┘
```

The registration fields should align with the roadmap's farmer-account data: name, phone, location and language. 

---

# 19. Language Selector

Because your system supports farmer language preferences, I recommend a small selector in the top-right:

```text
English ▾
```

Options:

```text
English
ગુજરાતી
हिन्दी
```

The roadmap specifically calls for English/Gujarati/Hindi UI copy and says the farmer's language should be carried through the recommendation flow. 

---

# 20. Mobile Layout

On mobile, don't keep the two-column design.

Use:

```text
┌──────────────────────────────┐
│                              │
│       🌱 Smart Farming       │
│                              │
│       Welcome back           │
│                              │
│  Sign in to continue.        │
│                              │
│  Phone Number                │
│  ┌────────────────────────┐  │
│  │                        │  │
│  └────────────────────────┘  │
│                              │
│  Password                 👁 │
│  ┌────────────────────────┐  │
│  │                        │  │
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │         Login          │  │
│  └────────────────────────┘  │
│                              │
│  Don't have an account?      │
│  Create an account           │
│                              │
└──────────────────────────────┘
```

Hide the large marketing panel.

---

# 21. Desktop Dimensions

Recommended:

```text
Page max width:      1200–1280px
Authentication card: 440–480px
Left panel:          ~50%
Right panel:         ~50%
Form width:          380–420px
```

Don't make the form extremely wide.

---

# 22. Visual Design

Use the same design language established for your landing page.

### Background

Very light neutral/green-tinted background.

### Primary color

Use your project's agricultural green as the primary action color.

### Cards

```text
border-radius: 16–20px
```

### Inputs

```text
height: 48–52px
border-radius: 10–12px
```

### Primary button

```text
height: 50–52px
border-radius: 10–12px
```

The login screen should feel **clean and trustworthy**, not overly decorative.

---

# 23. Input States

Every input should support:

### Default

```text
┌──────────────────────────┐
│ Enter your phone number  │
└──────────────────────────┘
```

### Focus

```text
┌──────────────────────────┐
│ +91 98765 43210          │
└──────────────────────────┘
        ↑
   focused border
```

### Error

```text
┌──────────────────────────┐
│ 9876                      │
└──────────────────────────┘
⚠ Please enter a valid phone number.
```

### Disabled

During login:

```text
┌──────────────────────────┐
│     Signing in...        │
└──────────────────────────┘
```

---

# 24. Security UX

Do not display sensitive information in error messages.

Bad:

```text
User with phone +91XXXXXXXXXX does not exist.
```

Better:

```text
Incorrect phone number or password.
```

Also:

* Don't expose JWTs in UI.
* Don't show backend exception messages directly.
* Don't log passwords.
* Don't put credentials in URLs.
* Clear sensitive form state when appropriate.

---

# 25. Accessibility

### Every input needs a real label

Not only:

```text
placeholder="Phone number"
```

Use:

```text
<label>Phone Number</label>
```

### Keyboard

Tab order:

```text
Phone
↓
Password
↓
Show password
↓
Login
↓
Create account
```

### Screen readers

Errors should be associated with the relevant input.

### Password visibility

The eye button should have an accessible label:

```text
Show password
```

and:

```text
Hide password
```

---

# 26. React Component Structure

For your Vite + React frontend:

```text
frontend/
└── src/
    ├── pages/
    │   └── LoginPage.tsx
    │
    ├── components/
    │   └── auth/
    │       ├── AuthLayout.tsx
    │       ├── AuthBrandPanel.tsx
    │       ├── LoginForm.tsx
    │       ├── PhoneInput.tsx
    │       ├── PasswordInput.tsx
    │       └── AuthError.tsx
    │
    ├── api/
    │   └── auth.ts
    │
    ├── context/
    │   └── AuthContext.tsx
    │
    └── hooks/
        └── useAuth.ts
```

This aligns with the roadmap's proposed `api/`, `components/`, `pages/`, and `context/AuthContext.tsx` structure. 

---

# 27. Component Hierarchy

```text
LoginPage
│
└── AuthLayout
    │
    ├── AuthBrandPanel
    │   ├── Logo
    │   ├── BrandHeading
    │   ├── BrandDescription
    │   └── CapabilityList
    │
    └── LoginCard
        ├── LanguageSelector
        ├── LoginHeader
        ├── LoginForm
        │   ├── PhoneInput
        │   ├── PasswordInput
        │   └── LoginButton
        │
        ├── AuthError
        │
        └── RegisterLink
```

---

# 28. API Layer

Don't call `fetch()` directly inside `LoginPage.tsx`.

Use:

```text
LoginPage
    ↓
useAuth()
    ↓
AuthContext
    ↓
auth.login()
    ↓
POST /auth/login
```

The roadmap specifically recommends thin API wrappers and `AuthContext` for authentication state. 

---

# 29. Login State Machine

Think of the screen as:

```text
              ┌─────────────┐
              │   INITIAL   │
              └──────┬──────┘
                     │
                  Submit
                     ↓
              ┌─────────────┐
              │   LOADING   │
              └──────┬──────┘
                     │
             ┌───────┴────────┐
             ↓                ↓
          SUCCESS           ERROR
             │                │
             ↓                ↓
        Dashboard          Show error
```

This will make your implementation much cleaner.

---

# 30. Complete Screen Blueprint

```text
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│ ┌────────────────────────────┐ ┌─────────────────────────┐ │
│ │                            │ │ English ▾               │ │
│ │       🌱                   │ │                         │ │
│ │    Smart Farming           │ │     Welcome back        │ │
│ │                            │ │                         │ │
│ │  Smarter decisions for     │ │  Sign in to continue    │ │
│ │  healthier crops.          │ │  managing your crops.   │ │
│ │                            │ │                         │ │
│ │      ┌─────────────┐       │ │  Phone Number           │ │
│ │      │    🍃       │       │ │  ┌────────────────────┐ │ │
│ │      │  AI Scan    │       │ │  │ Enter phone number │ │ │
│ │      └─────────────┘       │ │  └────────────────────┘ │ │
│ │                            │ │                         │ │
│ │  ✓ Crop identification    │ │  Password                │ │
│ │  ✓ Disease detection      │ │  ┌────────────────────┐ │ │
│ │  ✓ Severity analysis      │ │  │••••••••••••••  👁│ │ │
│ │  ✓ AI recommendations     │ │  └────────────────────┘ │ │
│ │                            │ │                         │ │
│ │                            │ │  ┌────────────────────┐ │ │
│ │                            │ │  │       Login        │ │ │
│ │                            │ │  └────────────────────┘ │ │
│ │                            │ │                         │ │
│ │                            │ │  Don't have an account? │ │
│ │                            │ │  Create an account →    │ │
│ │                            │ │                         │ │
│ └────────────────────────────┘ └─────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# 31. Final UX Flow

Your complete authentication flow should be:

```text
Landing Page
     │
     ├──────────────→ Login
     │                  │
     │                  ├── Successful
     │                  │       ↓
     │                  │   Dashboard
     │                  │
     │                  └── Failed
     │                          ↓
     │                     Error message
     │
     └──────────────→ Register
                        │
                        ↓
                  Create account
                        │
                        ↓
                      Login
```

And once authenticated:

```text
Login
 ↓
AuthContext
 ↓
Dashboard
 ├── Upload
 ├── Result
 ├── History
 └── Profile
```

Those application routes are explicitly defined in your roadmap. 

### Most important implementation decision

**Keep Login visually simple.** Your actual product complexity belongs after authentication—in the upload, result, history, farm context, recommendation, and explainability screens. The roadmap explicitly identifies the **Result screen as the centerpiece** of the web dashboard. 

So the Login screen should create trust and get the farmer into the application quickly, rather than trying to showcase every feature.

# Smart Farming — Register Screen UI/UX Specification

The Register screen is the **farmer onboarding screen**. Your roadmap defines `/register` as the second authentication screen and specifies that registration should collect **name, phone, location, language, and password**, followed by a `POST /auth/register` request. 

The database design also supports `phone`, `name`, `language`, and user role information. 

---

# 1. Screen Overview

### Screen name

**Create Your Farm Account**

### Route

```text
/register
```

### Access

```text
Public
```

### Primary objective

Allow a new farmer to create an account with the minimum information required to personalize the Smart Farming experience.

### Primary CTA

```text
Create Account
```

### Secondary CTA

```text
Already have an account? Login
```

---

# 2. Recommended UX Concept

Unlike the Login page, registration needs to communicate:

> **"Tell us a little about yourself so Smart Farming can give you more relevant guidance."**

The screen should therefore collect the farmer's basic identity and preferences without becoming a long profile form.

Recommended structure:

```text
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌────────────────────────┐  ┌────────────────────────────┐ │
│  │                        │  │                            │ │
│  │       🌱               │  │    Create your account     │ │
│  │   Smart Farming        │  │                            │ │
│  │                        │  │    Start smarter crop      │ │
│  │  Your crops.           │  │    health monitoring.      │ │
│  │  Your data.            │  │                            │ │
│  │  Smarter decisions.    │  │    Full Name               │ │
│  │                        │  │    ┌────────────────────┐  │ │
│  │      🍃                │  │    └────────────────────┘  │ │
│  │   AI crop health      │  │                            │ │
│  │                        │  │    Phone Number            │ │
│  │                        │  │    ┌────────────────────┐  │ │
│  │                        │  │    └────────────────────┘  │ │
│  │                        │  │                            │ │
│  │                        │  │    Location                │ │
│  │                        │  │    ┌────────────────────┐  │ │
│  │                        │  │    └────────────────────┘  │ │
│  │                        │  │                            │ │
│  └────────────────────────┘  │    Language               │ │
│                              │    ┌────────────────────┐  │ │
│                              │    └────────────────────┘  │ │
│                              │                            │ │
│                              │    Password                │ │
│                              │    ┌────────────────────┐  │ │
│                              │    └────────────────────┘  │ │
│                              │                            │ │
│                              │    [ Create Account ]     │ │
│                              │                            │ │
│                              │    Already registered?     │ │
│                              │    Login                   │ │
│                              └────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

# 3. Left Brand Panel

Keep this consistent with your Login screen.

### Logo

```text
🌱 Smart Farming
```

### Heading

> **Grow smarter with AI-powered crop insights.**

### Description

> Create your Smart Farming account to analyze crop health, understand disease severity, detect potential pests, and receive actionable farming guidance.

The feature list is based on the project's documented AI pipeline. 

---

# 4. Brand Panel Feature List

Show four concise benefits:

```text
✓ AI-powered crop analysis
✓ Disease and pest identification
✓ Crop severity assessment
✓ Actionable farming recommendations
```

Avoid putting technical model names such as:

```text
EfficientNet-B0
YOLOv8
PyTorch
FastAPI
```

on this screen.

Those belong in your technical documentation/project presentation, not farmer onboarding.

---

# 5. Right Panel Header

### Heading

> **Create your account**

### Subtitle

> Start using Smart Farming to understand your crops and make informed decisions.

---

# 6. Form Fields

Your roadmap supports these registration fields:

```text
Name
Phone
Location
Language
Password
```

The `/auth/register` API is also defined around these values. 

So I recommend exactly these fields.

---

# 7. Field 1 — Full Name

### Label

```text
Full Name
```

### Placeholder

```text
Enter your full name
```

### Example

```text
Manthan Kuvadiya
```

### Validation

```text
Required
Minimum reasonable length
Trim leading/trailing whitespace
```

### Error

```text
Please enter your name.
```

---

# 8. Field 2 — Phone Number

This should be the primary account identifier because the roadmap's user model centers on `phone`. 

### Label

```text
Phone Number
```

### Placeholder

```text
Enter your phone number
```

### Recommended UI

```text
┌───────┬───────────────────────────┐
│ +91 ▾ │ Enter phone number        │
└───────┴───────────────────────────┘
```

For your Indian-focused project, defaulting to:

```text
+91
```

is sensible.

### Validation

```text
Required
Valid Indian phone number
```

### Error

```text
Please enter a valid phone number.
```

---

# 9. Field 3 — Location

This field is important because your project is designed around **context-aware farming guidance**.

### Label

```text
Farm Location
```

I prefer **Farm Location** rather than simply `Location`, because it makes the purpose clearer.

### Placeholder

```text
Enter your village, city or district
```

Example:

```text
Anand, Gujarat
```

---

# 10. Location UI

Initially, keep this simple:

```text
┌────────────────────────────────────┐
│ 📍 Enter your village, city or     │
│    district                        │
└────────────────────────────────────┘
```

Don't immediately ask the farmer for:

```text
Latitude
Longitude
PIN code
Taluka
District
State
Country
```

unless your backend actually requires those fields.

The roadmap only explicitly specifies `location` during registration. 

---

# 11. Future Location Enhancement

You can later add:

```text
📍 Use my current location
```

which could produce:

```text
Village
District
State
Latitude
Longitude
```

But this should be a **future enhancement**, not something you need to force into the initial registration flow.

---

# 12. Field 4 — Preferred Language

This is an important field for your project.

### Label

```text
Preferred Language
```

### Dropdown

```text
┌────────────────────────────────────┐
│ English                         ▾  │
└────────────────────────────────────┘
```

Options:

```text
English
ગુજરાતી
हिन्दी
```

Your roadmap explicitly calls for English, Gujarati and Hindi support. 

---

# 13. Language Explanation

Under the dropdown, add small helper text:

> Recommendations and important farming information will be shown in your preferred language.

This makes the field's purpose immediately obvious.

---

# 14. Field 5 — Password

### Label

```text
Password
```

### Placeholder

```text
Create a password
```

Right-side:

```text
👁
```

---

# 15. Password Requirements

During registration, show requirements below the input.

For example:

```text
Password should contain:
✓ At least 8 characters
✓ At least one number
```

However, **only enforce requirements that your backend actually implements**.

The supplied roadmap does not specify a detailed password policy. Therefore, don't invent a complex policy such as:

```text
uppercase + lowercase + number + special character
```

unless you implement that policy consistently on the backend.

---

# 16. Password Strength Indicator

Optional but recommended:

```text
Password strength

████████░░  Strong
```

States:

```text
Weak
Medium
Strong
```

This is a UX enhancement; it is not specified in your roadmap.

---

# 17. Terms / Consent

I would **not invent a legal Terms & Conditions system** unless you plan to implement it.

If your project requires it, use:

```text
☐ I agree to the Terms of Service and Privacy Policy.
```

But don't make the checkbox decorative.

It must actually affect registration.

---

# 18. Create Account Button

### Default

```text
[ Create Account ]
```

Full width.

### Loading

```text
[ ⟳ Creating account... ]
```

During loading:

```text
Name        disabled
Phone       disabled
Location    disabled
Language    disabled
Password    disabled
Button      disabled
```

This prevents duplicate registrations.

---

# 19. Registration API

Your frontend should call:

```http
POST /auth/register
```

The documented registration flow accepts:

```text
name
phone
location
language
password
```

and returns an authentication token/session result. 

Conceptually:

```text
Register Form
     ↓
Validation
     ↓
auth.register()
     ↓
POST /auth/register
     ↓
Account created
     ↓
Authentication state
     ↓
Dashboard
```

---

# 20. Successful Registration

I recommend **automatically signing the farmer in** if your backend returns the required authentication token/session.

Flow:

```text
Create Account
      ↓
POST /auth/register
      ↓
201 / 200
      ↓
AuthContext updated
      ↓
Dashboard
```

Otherwise:

```text
Create Account
      ↓
Account created
      ↓
/login
```

Use whichever behavior your backend actually supports.

Don't make the frontend assume automatic authentication if `/auth/register` only creates the account.

---

# 21. Existing Account CTA

At the bottom:

```text
Already have an account?

[ Login ]
```

Click:

```text
/register
     ↓
 /login
```

---

# 22. Error States

You need proper handling for registration errors.

---

## Phone already registered

```text
⚠ An account with this phone number already exists.
```

CTA:

```text
[ Go to Login ]
```

This is much better than:

```text
Registration failed.
```

---

## Invalid phone

```text
Please enter a valid phone number.
```

---

## Missing name

```text
Please enter your name.
```

---

## Missing location

```text
Please enter your farm location.
```

---

## Missing language

```text
Please select your preferred language.
```

---

## Weak password

Only show this if the backend enforces a password requirement:

```text
Your password does not meet the required security rules.
```

---

## Network failure

```text
⚠ Unable to connect to Smart Farming.

Please check your internet connection and try again.
```

---

## Server error

```text
⚠ We couldn't create your account right now.

Please try again in a moment.
```

---

# 23. Form Validation Behavior

Don't wait until the user clicks Create Account to show every error.

Recommended:

```text
User focuses field
      ↓
User enters value
      ↓
User leaves field
      ↓
Validate field
```

Then on submit:

```text
Validate entire form
      ↓
If invalid → show errors
      ↓
If valid → API request
```

---

# 24. Registration Progress

Because this form has five fields, I recommend **not using a multi-step wizard** initially.

Avoid:

```text
Step 1/3
Personal details
       ↓
Step 2/3
Farm details
       ↓
Step 3/3
Security
```

That's unnecessary for five fields.

Keep everything on one screen.

---

# 25. Mobile Layout

On mobile, remove the large left marketing panel.

```text
┌──────────────────────────────┐
│      🌱 Smart Farming        │
│                              │
│     Create your account      │
│                              │
│  Start using Smart Farming   │
│  for smarter crop insights.  │
│                              │
│  Full Name                   │
│  ┌────────────────────────┐  │
│  │                        │  │
│  └────────────────────────┘  │
│                              │
│  Phone Number                │
│  ┌────────────────────────┐  │
│  │                        │  │
│  └────────────────────────┘  │
│                              │
│  Farm Location               │
│  ┌────────────────────────┐  │
│  │                        │  │
│  └────────────────────────┘  │
│                              │
│  Preferred Language          │
│  ┌────────────────────────┐  │
│  │ English             ▾  │  │
│  └────────────────────────┘  │
│                              │
│  Password                 👁 │
│  ┌────────────────────────┐  │
│  │                        │  │
│  └────────────────────────┘  │
│                              │
│  [    Create Account     ]  │
│                              │
│  Already have an account?    │
│  Login                       │
│                              │
└──────────────────────────────┘
```

---

# 26. Desktop Form Dimensions

Recommended:

```text
Page max-width:       1200–1280px

Left panel:           ~50%
Right panel:          ~50%

Form width:           400–440px

Input height:         48–52px

Button height:        50–52px

Card radius:          16–20px
```

---

# 27. Visual Relationship With Login

The two screens should look like **one authentication experience**.

```text
                    AUTH SYSTEM

            ┌──────────────┐
            │ Smart Farming│
            └───────┬──────┘
                    │
             ┌──────┴──────┐
             ↓             ↓
          /login        /register
             │             │
       Welcome back    Create account
             │             │
             └──────┬──────┘
                    ↓
                Dashboard
```

Keep the following identical between the two:

* Logo
* Typography
* Background
* Input style
* Button style
* Border radius
* Error style
* Language selector
* Left brand panel
* Mobile behavior

Only the form content changes.

---

# 28. React Component Structure

For your React/Vite frontend:

```text
src/
├── pages/
│   ├── LoginPage.tsx
│   └── RegisterPage.tsx
│
├── components/
│   └── auth/
│       ├── AuthLayout.tsx
│       ├── AuthBrandPanel.tsx
│       ├── RegisterForm.tsx
│       ├── NameInput.tsx
│       ├── PhoneInput.tsx
│       ├── LocationInput.tsx
│       ├── LanguageSelect.tsx
│       ├── PasswordInput.tsx
│       ├── PasswordStrength.tsx
│       └── AuthError.tsx
│
├── api/
│   └── auth.ts
│
├── context/
│   └── AuthContext.tsx
│
└── hooks/
    └── useAuth.ts
```

The overall structure follows the roadmap's suggested React organization and `AuthContext` approach. 

---

# 29. Component Hierarchy

```text
RegisterPage
│
└── AuthLayout
    │
    ├── AuthBrandPanel
    │   ├── Logo
    │   ├── BrandHeading
    │   ├── BrandDescription
    │   └── CapabilityList
    │
    └── RegisterCard
        ├── LanguageSelector
        ├── RegisterHeader
        │
        ├── RegisterForm
        │   ├── NameInput
        │   ├── PhoneInput
        │   ├── LocationInput
        │   ├── LanguageSelect
        │   ├── PasswordInput
        │   ├── PasswordStrength
        │   └── CreateAccountButton
        │
        ├── AuthError
        │
        └── LoginLink
```

---

# 30. Registration State Machine

```text
                    INITIAL
                       │
                       │ Submit
                       ↓
                 VALIDATING
                  /       \
             invalid       valid
               ↓             ↓
         SHOW ERRORS      LOADING
                             │
                    ┌────────┴────────┐
                    ↓                 ↓
                 SUCCESS            ERROR
                    │                 │
                    ↓                 ↓
               AUTH/DASHBOARD     SHOW ERROR
```

This gives you predictable UI behavior.

---

# 31. Complete Register Wireframe

```text
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│ ┌────────────────────────────┐ ┌─────────────────────────┐ │
│ │                            │ │ English ▾               │ │
│ │       🌱                   │ │                         │ │
│ │    Smart Farming           │ │  Create your account    │ │
│ │                            │ │                         │ │
│ │  Grow smarter with        │ │  Start smarter crop     │ │
│ │  AI-powered crop insights.│ │  health monitoring.     │ │
│ │                            │ │                         │ │
│ │       🍃                   │ │  Full Name              │ │
│ │      AI crop               │ │  ┌────────────────────┐ │ │
│ │      analysis              │ │  │                    │ │ │
│ │                            │ │  └────────────────────┘ │ │
│ │  ✓ Crop identification    │ │                         │ │
│ │  ✓ Disease detection      │ │  Phone Number            │ │
│ │  ✓ Severity analysis      │ │  ┌────────────────────┐ │ │
│ │  ✓ AI recommendations     │ │  │ +91                │ │ │
│ │                            │ │  └────────────────────┘ │ │
│ │                            │ │                         │ │
│ │                            │ │  Farm Location          │ │
│ │                            │ │  ┌────────────────────┐ │ │
│ │                            │ │  │ Village / City     │ │ │
│ │                            │ │  └────────────────────┘ │ │
│ │                            │ │                         │ │
│ │                            │ │  Preferred Language     │ │
│ │                            │ │  ┌────────────────────┐ │ │
│ │                            │ │  │ English          ▾ │ │ │
│ │                            │ │  └────────────────────┘ │ │
│ │                            │ │                         │ │
│ │                            │ │  Password             👁│ │
│ │                            │ │  ┌────────────────────┐ │ │
│ │                            │ │  │                    │ │ │
│ │                            │ │  └────────────────────┘ │ │
│ │                            │ │                         │ │
│ │                            │ │  [ Create Account ]    │ │
│ │                            │ │                         │ │
│ │                            │ │  Already registered?    │ │
│ │                            │ │  Login →                │ │
│ └────────────────────────────┘ └─────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# 32. Complete User Flow

Your first three screens should now connect like this:

```text
                 LANDING PAGE
                       │
             [ Get Started / Scan ]
                       ↓
                    /login
                 ↙           ↘
        Existing user       New user
             │                  │
             ↓                  ↓
          Login             Register
             │                  │
             │          Name / Phone
             │          Location / Language
             │          Password
             │                  │
             └────────┬─────────┘
                      ↓
                  AUTHENTICATED
                      ↓
                  /dashboard
```

This is the correct place to end registration. **Don't send the user directly to `/upload`** after registration. The roadmap establishes the dashboard as the authenticated application entry point, with upload and result as subsequent workflows. 

---

## Recommended final form

For your current project, I would keep the initial registration form to exactly:

| Field              | Required | Source/Reason                  |
| ------------------ | -------: | ------------------------------ |
| Full Name          |      Yes | Roadmap registration data      |
| Phone Number       |      Yes | Authentication/user identity   |
| Farm Location      |      Yes | Context-aware farming          |
| Preferred Language |      Yes | English/Gujarati/Hindi support |
| Password           |      Yes | Authentication                 |

Then after registration, **collect additional farm details inside the application**, rather than making onboarding unnecessarily long. This will give you a much better farmer UX while still preserving the information your backend currently expects.


# Smart Farming — Dashboard Screen UI/UX Specification

The **Dashboard** should be the farmer's main authenticated home screen. One important point from your roadmap: the documented React routes explicitly include `/login`, `/register`, `/upload`, `/result/:id`, `/history`, `/profile`, and `/admin`, but **a `/dashboard` route is not explicitly listed**. 

So I recommend adding:

```text
/dashboard
```

as the authenticated home route. This is a **UX recommendation**, not a route currently specified by the roadmap.

The dashboard should be a **summary and action center**, while the detailed diagnosis belongs on `/result/:id`, which the roadmap explicitly calls the centerpiece of the web dashboard. 

---

# 1. Dashboard's Main Purpose

The farmer should understand the state of their farm in **5–10 seconds**.

The dashboard should answer:

> **How is my farm doing?**

> **What did I analyze recently?**

> **Is anything concerning?**

> **What should I do next?**

> **Can I scan another crop?**

It should **not** attempt to reproduce the entire result screen.

---

# 2. Recommended Route

```text
/dashboard
```

### Access

```text
Authenticated farmer
```

Unauthenticated user:

```text
/dashboard
     ↓
/login
```

This follows the roadmap's JWT/AuthContext protected-route architecture. 

---

# 3. Dashboard Layout

I recommend a **sidebar + top header + responsive content** layout.

```text
┌────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                         🔔     👤 Manthan ▾       │
├───────────────┬────────────────────────────────────────────────────┤
│               │                                                    │
│ 🏠 Dashboard  │  Good morning, Manthan 👋                         │
│               │  Here's your farm health overview.                │
│ 📷 Scan Crop  │                                                    │
│               │  ┌──────────────────┐ ┌─────────────────────────┐ │
│ 📋 History    │  │ Farm Overview    │ │ 🌦 Weather              │ │
│               │  │                  │ │                         │ │
│ 🌱 My Farm    │  │ 24 Analyses      │ │ 29°C                    │ │
│               │  │ 18 Healthy       │ │ Humidity 74%            │ │
│ 🔔 Alerts     │  │ 4 Moderate       │ │                         │ │
│               │  │ 2 Severe         │ │ Anand, Gujarat          │ │
│ ⚙ Settings   │  └──────────────────┘ └─────────────────────────┘ │
│               │                                                    │
│               │  ┌─────────────────────────────────────────────┐ │
│               │  │          📷 Analyze Your Crop               │ │
│               │  │                                             │ │
│               │  │ Upload a leaf photo to check crop health.   │ │
│               │  │                                             │ │
│               │  │            [ Scan New Crop ]                 │ │
│               │  └─────────────────────────────────────────────┘ │
│               │                                                    │
│               │  Recent Diagnoses                                 │
│               │  ┌────────┬──────────┬──────────┬─────────────┐ │
│               │  │ Crop   │ Disease  │ Severity │ Date        │ │
│               │  ├────────┼──────────┼──────────┼─────────────┤ │
│               │  │ Tomato │ Blight   │ Moderate │ Today       │ │
│               │  │ Cotton │ Healthy  │ Healthy  │ Yesterday   │ │
│               │  └────────┴──────────┴──────────┴─────────────┘ │
│               │                                                    │
└───────────────┴────────────────────────────────────────────────────┘
```

---

# 4. Sidebar

The sidebar is the main navigation system.

## Navigation

```text
🌱 Smart Farming

🏠 Dashboard
📷 Scan Crop
📋 History
🌱 My Farm
🔔 Alerts
⚙ Settings
```

At bottom:

```text
👤 Manthan
Farmer

Logout
```

---

# 5. Why These Navigation Items?

### Dashboard

```text
/dashboard
```

Summary and overview.

### Scan Crop

```text
/upload
```

The roadmap explicitly defines `/upload` as the drag-and-drop leaf upload screen that calls `POST /predict`. 

### History

```text
/history
```

The roadmap specifies a paginated prediction history with crop, disease and date filters. 

### My Farm

```text
/profile
```

The roadmap defines the profile page for farmer/farm details, crop history and language preference. 

### Alerts

This is a **recommended addition**, not a currently specified frontend route.

It becomes especially useful if you implement the roadmap's weather-triggered proactive alerts. 

### Settings

Also a UX recommendation. Your roadmap mentions language, notification preferences and data-usage settings in the broader application design. 

---

# 6. Sidebar Active State

If the farmer is on Dashboard:

```text
┌──────────────────────┐
│ 🏠 Dashboard         │ ← active
├──────────────────────┤
│ 📷 Scan Crop         │
│ 📋 History           │
│ 🌱 My Farm           │
│ 🔔 Alerts            │
│ ⚙ Settings           │
└──────────────────────┘
```

Use a subtle background + left indicator rather than an extremely bright color.

---

# 7. Top Header

Desktop:

```text
┌──────────────────────────────────────────────────────────┐
│                                      🔔     👤 Manthan ▾ │
└──────────────────────────────────────────────────────────┘
```

### Notification icon

```text
🔔
```

If there are alerts:

```text
🔔
 ●
```

Clicking it opens a notification panel.

---

# 8. User Profile Menu

Click:

```text
👤 Manthan ▾
```

Dropdown:

```text
┌────────────────────────┐
│ 👤 Manthan Kuvadiya    │
│ Farmer                 │
├────────────────────────┤
│ My Profile             │
│ Settings               │
│                        │
│ 🚪 Logout              │
└────────────────────────┘
```

---

# 9. Dashboard Greeting

Main content begins with:

### Heading

> **Good morning, Manthan 👋**

Use dynamic greeting:

```text
05:00–11:59 → Good morning
12:00–16:59 → Good afternoon
17:00–04:59 → Good evening
```

### Subtitle

> Here's your farm health overview.

Don't make the greeting overly large. The dashboard is a utility screen.

---

# 10. Farm Context Header

Below the greeting:

```text
📍 Anand, Gujarat
🌱 Main Crop: Tomato
```

If the user has multiple plots:

```text
📍 Anand, Gujarat       Farm Zone: Zone A ▾
```

This is particularly useful if you implement the roadmap's **Farm Context Engine**, which includes zone, farm history, growth stage, weather and recent actions. 

---

# 11. Farm Health Overview Card

This is the first major card.

### Heading

> **Farm Health Overview**

Example:

```text
┌──────────────────────────────────────────────┐
│ Farm Health Overview                         │
│                                              │
│      24                 18                   │
│   Analyses            Healthy                │
│                                              │
│       4                 2                    │
│   Moderate             Severe                 │
│                                              │
│        Last analysis: Today                  │
└──────────────────────────────────────────────┘
```

---

# 12. Don't Call It "Farm Health Score"

I recommend **not** showing:

```text
Farm Health Score: 87/100
```

unless you actually implement a defensible farm-health scoring algorithm.

Your current system produces crop, disease, severity and pest outputs—not a documented aggregate "farm health score." The dashboard should display the actual available information instead of inventing a metric.

---

# 13. Analysis Summary

A better visualization:

```text
Total Analyses
24

Healthy
18  ███████████████

Moderate
4   ████

Severe
2   ██
```

The underlying prediction history can support these aggregates because the system logs the prediction chain. 

---

# 14. Weather Card

Your backend roadmap explicitly includes:

```http
GET /weather
```

for current weather for the farmer's saved location. 

So the dashboard should have a weather card.

```text
┌─────────────────────────────────┐
│ 🌦 Current Weather               │
│                                 │
│             ☀                  │
│            29°C                 │
│                                 │
│ Humidity        74%             │
│ Rain            20%             │
│                                 │
│ 📍 Anand, Gujarat               │
│ Updated 10 min ago              │
└─────────────────────────────────┘
```

---

# 15. Weather Card Should Be Actionable

Don't make it just:

```text
29°C
Sunny
```

If your recommendation system actually uses weather context, show:

```text
🌱 Farm insight

Current conditions may affect
irrigation and disease risk.
```

The roadmap explicitly describes weather as part of the recommendation context. 

---

# 16. Quick Scan Card

This should be one of the **largest and most visually prominent elements**.

```text
┌────────────────────────────────────────────────────┐
│                                                    │
│                 📷                                 │
│                                                    │
│          Analyze Your Crop                         │
│                                                    │
│  Upload a clear leaf photo to check crop health,   │
│  disease, severity and potential pests.            │
│                                                    │
│              [ Scan New Crop → ]                   │
│                                                    │
└────────────────────────────────────────────────────┘
```

Click:

```text
/dashboard
     ↓
/upload
```

The roadmap defines `/upload` as the frontend upload interface that triggers the full prediction pipeline. 

---

# 17. Quick Scan Secondary Action

Optionally:

```text
[ View Scan History ]
```

which navigates to:

```text
/history
```

---

# 18. Recent Diagnoses

This should be directly below the scan card.

### Heading

> **Recent Diagnoses**

### Right side

```text
[ View All → ]
```

---

# 19. Recent Diagnosis Card

Desktop table:

```text
┌────────────┬────────────────┬────────────┬──────────────┬─────────┐
│ Crop       │ Disease        │ Severity   │ Confidence   │ Date    │
├────────────┼────────────────┼────────────┼──────────────┼─────────┤
│ 🍅 Tomato  │ Early Blight   │ Moderate   │ 96%          │ Today   │
│ 🌱 Cotton  │ Healthy        │ Healthy    │ 98%          │ Aug 25  │
│ 🥔 Potato  │ Late Blight    │ Severe     │ 91%          │ Aug 24  │
└────────────┴────────────────┴────────────┴──────────────┴─────────┘
```

The roadmap specifically defines crop, disease, severity and confidence as key result information. 

---

# 20. Diagnosis Row Interaction

Clicking a row:

```text
/history
   ↓
/result/:id
```

The result page should show the complete diagnosis.

Remember: **don't put the entire Grad-CAM/recommendation result inside the dashboard.**

The roadmap specifically designates the result screen as the centerpiece. 

---

# 21. Status Badges

Use semantic badges.

### Healthy

```text
✓ Healthy
```

### Mild

```text
● Mild
```

### Moderate

```text
● Moderate
```

### Severe

```text
⚠ Severe
```

### Expert review

If low confidence:

```text
⏳ Expert Review
```

The roadmap specifies that low-confidence predictions should become `pending_expert_review` rather than displaying unverified advice. 

---

# 22. Important Alert Card

If you implement proactive alerts, put a compact alert section above recent history.

Example:

```text
┌────────────────────────────────────────────────────┐
│ ⚠ Attention Required                              │
│                                                    │
│ Tomato — Early Blight                             │
│ Severe severity detected in Zone A.               │
│                                                    │
│ [ View Diagnosis → ]                               │
└────────────────────────────────────────────────────┘
```

If you don't have the alert engine implemented yet, **don't show fake alerts**.

---

# 23. Farm Zones

This is a strong enhancement for your project.

If multiple farm zones are implemented:

```text
┌───────────────────────────────────────────────────┐
│ 🌱 My Farm Zones                                  │
│                                                   │
│ Zone A        Tomato       ⚠ 2 issues             │
│ Zone B        Cotton       ✓ Healthy              │
│ Zone C        Groundnut    ● 1 moderate           │
│                                                   │
│                    [ Manage Zones → ]             │
└───────────────────────────────────────────────────┘
```

This is supported as a roadmap depth addition: predictions can be grouped by farmer-defined plot, with trends over time. 

But make it **P1**, not mandatory for the first version.

---

# 24. Crop Health Trend

Another good dashboard feature:

```text
Health / Severity Trend

Severity
100% ┤
 80% ┤
 60% ┤         ╭─╮
 40% ┤    ╭────╯ ╰──╮
 20% ┤────╯         ╰──
  0% ┼────────────────────
      Aug 20  Aug 23  Aug 26
```

But this should be based on actual prediction history.

Don't create a generic "AI health trend" if the data isn't available.

The roadmap's multi-plot/history addition explicitly allows trend views over logged predictions. 

---

# 25. Recommended Dashboard Layout

I would actually structure the desktop content in this order:

```text
┌────────────────────────────────────────────────────────────┐
│ Greeting + Farm Location                                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌──────────────────────┐ ┌───────────────────────────────┐ │
│ │ Farm Health Overview │ │ Weather                       │ │
│ └──────────────────────┘ └───────────────────────────────┘ │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │                                                        │ │
│ │                 📷 Scan Your Crop                      │ │
│ │                                                        │ │
│ │             [ Scan New Crop → ]                        │ │
│ │                                                        │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Recent Diagnoses                           View All →       │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Crop | Disease | Severity | Confidence | Date          │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌────────────────────────┐ ┌────────────────────────────┐ │
│ │ Crop Health Trend      │ │ Farm Zones                  │ │
│ └────────────────────────┘ └────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

# 26. Desktop Sidebar + Content Dimensions

Recommended:

```text
Sidebar:
240–260px

Top header:
64–72px

Main content:
max-width 1400px

Page padding:
24–32px

Card gap:
16–24px
```

Don't make the dashboard full-width with huge empty areas.

---

# 27. Mobile Dashboard

The desktop sidebar becomes a bottom navigation.

```text
┌───────────────────────────────┐
│ 🌱 Smart Farming       🔔 👤 │
├───────────────────────────────┤
│                               │
│ Good morning 👋               │
│ Anand, Gujarat                │
│                               │
│ ┌───────────────────────────┐ │
│ │ Farm Health               │ │
│ │                           │ │
│ │ 24 analyses               │ │
│ │ 18 Healthy                │ │
│ │ 4 Moderate   2 Severe     │ │
│ └───────────────────────────┘ │
│                               │
│ ┌───────────────────────────┐ │
│ │ 🌦 29°C                   │ │
│ │ Humidity 74%              │ │
│ └───────────────────────────┘ │
│                               │
│ ┌───────────────────────────┐ │
│ │ 📷 Analyze Your Crop      │ │
│ │                           │ │
│ │ [ Scan New Crop ]         │ │
│ └───────────────────────────┘ │
│                               │
│ Recent Diagnoses              │
│ ┌───────────────────────────┐ │
│ │ 🍅 Tomato                 │ │
│ │ Early Blight              │ │
│ │ Moderate       Today      │ │
│ └───────────────────────────┘ │
│                               │
├───────────────────────────────┤
│ 🏠       📷       📋      👤 │
│ Home     Scan    History   Me │
└───────────────────────────────┘
```

---

# 28. Mobile Navigation

I recommend only four primary items:

```text
🏠 Home
📷 Scan
📋 History
👤 Profile
```

Put:

```text
Alerts
Settings
```

inside Profile/More.

This keeps the mobile interface simple.

---

# 29. Loading State

When dashboard data is loading:

Don't show an empty page.

Use skeletons:

```text
┌───────────────────────────┐
│ █████████████             │
│ ███████                   │
└───────────────────────────┘

┌──────────────┐ ┌───────────┐
│ ███████      │ │ ███████   │
│ █████        │ │ █████     │
│ ███████      │ │ ██████    │
└──────────────┘ └───────────┘

┌──────────────────────────────┐
│ █████████████████████        │
│ █████████████                │
└──────────────────────────────┘
```

---

# 30. Empty Dashboard

For a newly registered farmer, there may be no predictions.

Don't show:

```text
No data.
```

Instead:

```text
┌───────────────────────────────────────────┐
│                                           │
│              📷                           │
│                                           │
│       No crop analyses yet                │
│                                           │
│  Upload your first leaf photo to start   │
│  monitoring your crop health.             │
│                                           │
│       [ Scan Your First Crop ]            │
│                                           │
└───────────────────────────────────────────┘
```

This is especially important for your demo because a newly created account should still look complete.

---

# 31. API Integration

The dashboard can consume several backend APIs.

### History

```http
GET /history
```

Used for:

* recent diagnoses
* analysis count
* severity summary
* trends

The endpoint is explicitly defined as a paginated farmer prediction history. 

### Weather

```http
GET /weather
```

Used for:

* temperature
* humidity
* rain/current conditions



### Profile

Your profile data can provide:

```text
name
location
language
farm information
```

The profile route is explicitly part of the frontend plan. 

---

# 32. Dashboard API Architecture

Don't put API calls directly inside the page.

Use:

```text
DashboardPage
      ↓
React Query hooks
      ↓
API wrappers
      ↓
FastAPI
```

Example architecture:

```text
src/
├── api/
│   ├── history.ts
│   ├── weather.ts
│   └── profile.ts
│
├── hooks/
│   ├── useHistory.ts
│   ├── useWeather.ts
│   └── useProfile.ts
│
└── pages/
    └── DashboardPage.tsx
```

The roadmap explicitly recommends React Query for caching, retries and loading/error states. 

---

# 33. Recommended React Component Structure

```text
src/
└── components/
    └── dashboard/
        ├── DashboardLayout.tsx
        ├── Sidebar.tsx
        ├── Topbar.tsx
        ├── WelcomeHeader.tsx
        ├── FarmContextHeader.tsx
        ├── FarmHealthOverview.tsx
        ├── WeatherCard.tsx
        ├── ScanCropCard.tsx
        ├── RecentDiagnoses.tsx
        ├── DiagnosisRow.tsx
        ├── HealthTrendChart.tsx
        ├── FarmZonesCard.tsx
        ├── AlertCard.tsx
        ├── NotificationPanel.tsx
        └── UserMenu.tsx
```

---

# 34. Dashboard Page Structure

```text
DashboardPage
│
├── DashboardLayout
│   │
│   ├── Sidebar
│   │
│   └── MainContent
│       │
│       ├── Topbar
│       │
│       ├── WelcomeHeader
│       │
│       ├── FarmContextHeader
│       │
│       ├── OverviewGrid
│       │   ├── FarmHealthOverview
│       │   └── WeatherCard
│       │
│       ├── ScanCropCard
│       │
│       ├── RecentDiagnoses
│       │
│       └── InsightsGrid
│           ├── HealthTrendChart
│           └── FarmZonesCard
```

---

# 35. Dashboard State Architecture

You need at least:

```text
loading
success
empty
error
```

for each major data section.

For example:

```text
Weather
├── loading
├── loaded
└── error

History
├── loading
├── loaded
├── empty
└── error

Farm Profile
├── loading
├── loaded
└── error
```

React Query is particularly suitable here because your roadmap explicitly recommends it. 

---

# 36. Important: Don't Overload the Dashboard

I would **not** put these directly on the dashboard:

```text
❌ Full Grad-CAM heatmap
❌ Full recommendation text
❌ Raw JSON
❌ Model architecture
❌ Model accuracy charts
❌ Training metrics
❌ Dataset information
❌ Admin/MLOps metrics
```

Those belong elsewhere.

The roadmap clearly separates:

```text
Farmer dashboard
        ↓
Predictions / history / profile

Admin
        ↓
Accuracy / confidence / drift / retraining
```

The `/admin` page is specifically reserved for aggregate metrics and MLOps information. 

---

# 37. What the Dashboard Should Emphasize

Use this hierarchy:

```text
1. 📷 SCAN CROP
       ↓
2. ⚠ IMPORTANT FARM ISSUES
       ↓
3. 🌦 FARM CONTEXT / WEATHER
       ↓
4. 📋 RECENT DIAGNOSES
       ↓
5. 📈 TRENDS
```

The primary goal is to encourage the farmer to **perform the next useful action**, not to stare at statistics.

---

# 38. Dashboard's Most Important Card

If I had to choose one component that visually dominates the dashboard, it would be:

> **Analyze Your Crop**

Because your entire product begins with:

```text
Leaf Photo
   ↓
OpenCV validation
   ↓
Crop identification
   ↓
Disease classification
   ↓
Severity
   ↓
Pest analysis
   ↓
Recommendation
```

That four-stage core is explicitly how the roadmap defines the product. 

---

# 39. Final Dashboard Wireframe

```text
┌─────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                         🔔        👤 Manthan ▾     │
├───────────────┬─────────────────────────────────────────────────────┤
│               │                                                     │
│ 🏠 Dashboard  │  Good morning, Manthan 👋                           │
│               │  Here's your farm health overview.                 │
│ 📷 Scan Crop  │                                                     │
│               │  📍 Anand, Gujarat                                 │
│ 📋 History    │                                                     │
│               │  ┌──────────────────────┐ ┌──────────────────────┐ │
│ 🌱 My Farm    │  │ 🌱 Farm Health       │ │ 🌦 Weather           │ │
│               │  │                      │ │                      │ │
│ 🔔 Alerts     │  │ 24 Analyses          │ │ 29°C                 │ │
│               │  │ 18 Healthy           │ │ Humidity 74%         │ │
│ ⚙ Settings    │  │ 4 Moderate           │ │                      │ │
│               │  │ 2 Severe             │ │ 📍 Anand, Gujarat    │ │
│               │  └──────────────────────┘ └──────────────────────┘ │
│               │                                                     │
│               │  ┌───────────────────────────────────────────────┐ │
│               │  │                                                 │ │
│               │  │             📷 Analyze Your Crop               │ │
│               │  │                                                 │ │
│               │  │   Upload a leaf photo to check crop health.   │ │
│               │  │                                                 │ │
│               │  │                [ Scan New Crop → ]             │ │
│               │  │                                                 │ │
│               │  └───────────────────────────────────────────────┘ │
│               │                                                     │
│               │  Recent Diagnoses                   View All →      │
│               │  ┌───────────────────────────────────────────────┐ │
│               │  │ Crop   Disease      Severity   Confidence     │ │
│               │  ├───────────────────────────────────────────────┤ │
│               │  │ 🍅     Early Blight Moderate    96%           │ │
│               │  │ 🌱     Healthy      Healthy     98%           │ │
│               │  │ 🥔     Late Blight  Severe      91%           │ │
│               │  └───────────────────────────────────────────────┘ │
│               │                                                     │
│               │  ┌──────────────────────┐ ┌──────────────────────┐ │
│               │  │ 📈 Health Trend      │ │ 🌱 Farm Zones        │ │
│               │  │                      │ │                      │ │
│               │  │       ╭──╮           │ │ Zone A  ⚠ 2 issues   │ │
│               │  │   ╭───╯  ╰───        │ │ Zone B  ✓ Healthy    │ │
│               │  │                      │ │ Zone C  ● Moderate   │ │
│               │  └──────────────────────┘ └──────────────────────┘ │
│               │                                                     │
└───────────────┴─────────────────────────────────────────────────────┘
```

---

## Priority breakdown

### P0 — Build first

```text
✓ Sidebar
✓ Topbar
✓ Welcome/farm context
✓ Farm analysis summary
✓ Weather
✓ Scan New Crop CTA
✓ Recent Diagnoses
✓ Loading/error/empty states
```

### P1 — Add after core flow works

```text
✓ Health trend
✓ Farm zones
✓ Alerts
✓ Notification panel
✓ Context-aware farm insights
```

### P2 — Future enhancement

```text
✓ Proactive weather alerts
✓ Advanced multi-zone analytics
✓ More detailed farm trends
✓ Voice-oriented assistance
```

The P1/P2 features should be added only when the corresponding backend capabilities exist; the roadmap specifically describes farm context, multi-plot history and weather-triggered alerts as depth additions rather than mandatory baseline dashboard functionality. 

**Most importantly:** keep this screen as the **farmer's command center**, not the diagnosis screen. The next screen, `/upload`, should be extremely focused on getting a good leaf image into your pipeline; `/result/:id` should then contain the detailed AI diagnosis, Grad-CAM explanation, severity and recommendation. That separation matches the architecture in your roadmap. 


# Smart Farming — Scan / Upload Screen UI/UX Specification

This is one of the **most important screens in your project** because it is the entry point to your AI diagnosis pipeline.

Your roadmap defines `/upload` as the leaf-image upload interface. It should support **drag-and-drop, file selection, image preview, validation, and submission to `POST /predict`**. 

Your backend pipeline then processes the image through:

```text
Image
  ↓
OpenCV preprocessing
  ↓
Crop identification
  ↓
Decision routing
  ↓
Disease classification
  ↓
Severity estimation
  ↓
Pest detection
  ↓
AI recommendation
  ↓
Result
```

The roadmap describes crop identification, disease classification, severity estimation and pest analysis as the core prediction flow. 

---

# 1. Screen Overview

### Route

```text
/upload
```

### Screen name

**Analyze Your Crop**

### Primary objective

Allow the farmer to upload a **clear leaf/crop image** and start the AI analysis.

### Primary CTA

```text
Analyze Crop →
```

### Secondary action

```text
← Back to Dashboard
```

---

# 2. Core UX Principle

The farmer should immediately understand:

> **"Upload a clear photo of a crop leaf, and Smart Farming will analyze it."**

Do **not** make this page look like a generic file-upload form.

Avoid:

```text
Upload File
Choose File
Submit
```

Instead, make it feel like a **crop diagnosis workflow**.

---

# 3. Recommended Layout

Desktop:

```text
┌────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                       🔔        👤 Manthan ▾      │
├───────────────┬────────────────────────────────────────────────────┤
│               │                                                    │
│ 🏠 Dashboard  │  Analyze Your Crop                                │
│               │  Upload a clear leaf image for AI-powered         │
│ 📷 Scan Crop  │  crop health analysis.                            │
│               │                                                    │
│ 📋 History    │                                                    │
│               │  ┌────────────────────────────────────────────┐  │
│ 🌱 My Farm    │  │                                            │  │
│               │  │                  📷                        │  │
│ 🔔 Alerts     │  │                                            │  │
│               │  │       Upload your crop image              │  │
│ ⚙ Settings    │  │                                            │  │
│               │  │  Drag & drop your image here              │  │
│               │  │  or                                        │  │
│               │  │  [ Choose Image ]                          │  │
│               │  │                                            │  │
│               │  │  JPG / JPEG / PNG                          │  │
│               │  │  Maximum size: X MB                        │  │
│               │  │                                            │  │
│               │  └────────────────────────────────────────────┘  │
│               │                                                    │
│               │  💡 Tips for a better diagnosis                   │
│               │  ✓ Use a clear image                              │
│               │  ✓ Keep the leaf in focus                         │
│               │  ✓ Avoid extreme darkness or brightness           │
│               │                                                    │
│               │                       [ Analyze Crop → ]          │
│               │                                                    │
└───────────────┴────────────────────────────────────────────────────┘
```

---

# 4. Page Header

### Heading

> **Analyze Your Crop**

### Subtitle

> Upload a clear image of a crop leaf and let Smart Farming analyze its health.

Keep the language farmer-friendly.

Do **not** say:

> Run the multi-stage computer vision inference pipeline.

That's technically accurate but terrible UX.

---

# 5. Upload Card

The upload area should be the visual center of the page.

```text
┌──────────────────────────────────────────────┐
│                                              │
│                    📷                        │
│                                              │
│             Upload crop image                │
│                                              │
│       Drag & drop your image here            │
│                   or                         │
│             [ Choose Image ]                 │
│                                              │
│          JPG • JPEG • PNG                    │
│                                              │
└──────────────────────────────────────────────┘
```

---

# 6. Drag-and-Drop Interaction

The roadmap explicitly specifies drag-and-drop support. 

### Normal state

```text
Upload your crop image

Drag & drop here
or

[ Choose Image ]
```

### When dragging over

Change the card:

```text
┌──────────────────────────────────────────────┐
│                                              │
│                    📥                        │
│                                              │
│             Drop image here                  │
│                                              │
│       Release to start image upload          │
│                                              │
└──────────────────────────────────────────────┘
```

Use a visible border/outline change so the farmer knows where to drop.

---

# 7. Supported Image Formats

Display:

```text
JPG • JPEG • PNG
```

The exact maximum size should be whatever your backend actually enforces.

If you have not implemented a size limit yet, **don't put an arbitrary number such as "Maximum 10 MB" in the UI.**

---

# 8. Image Selection Flow

After selecting an image:

```text
Choose Image
     ↓
Validate file
     ↓
Show preview
     ↓
User confirms
     ↓
Analyze Crop
```

Do **not automatically start the expensive AI pipeline immediately after file selection**.

Let the user inspect the image first.

---

# 9. Image Preview State

Once an image is selected:

```text
┌──────────────────────────────────────────────┐
│                                              │
│              ┌────────────────┐              │
│              │                │              │
│              │                │              │
│              │   LEAF IMAGE   │              │
│              │                │              │
│              │                │              │
│              └────────────────┘              │
│                                              │
│  tomato_leaf_01.jpg                          │
│  2.4 MB                                      │
│                                              │
│  [ Change Image ]                            │
│                                              │
└──────────────────────────────────────────────┘
```

---

# 10. Image Preview Controls

Under the preview:

```text
[ Change Image ]
```

Optional:

```text
[ Remove ]
```

If removed:

```text
Preview
   ↓
Upload state
```

---

# 11. Image Quality Guidance

This is particularly important for your project because your preprocessing layer performs image-quality checks.

Your configured preprocessing thresholds include blur and brightness checks, and the backend preprocessing service performs validation before continuing through the pipeline.

Therefore, the frontend should **educate the user before they submit** rather than simply returning an error afterward.

---

# 12. "Tips for Better Results" Card

Place this below or beside the uploader:

```text
┌────────────────────────────────────────────┐
│ 💡 Tips for a better diagnosis             │
│                                            │
│ ✓ Capture the leaf clearly                 │
│ ✓ Keep the leaf in focus                   │
│ ✓ Use good lighting                        │
│ ✓ Avoid heavily blurred images             │
│ ✓ Keep the leaf visible in the frame       │
└────────────────────────────────────────────┘
```

This directly supports your preprocessing workflow.

---

# 13. Don't Overcomplicate the Instructions

Don't give the farmer technical requirements such as:

```text
HSV range
CLAHE
224 × 224
Gaussian blur
variance threshold
RGB normalization
```

Those are implementation details.

The user only needs:

> **Clear + focused + visible leaf + reasonable lighting.**

---

# 14. Analyze Button

When no image exists:

```text
[ Analyze Crop ]
```

should be **disabled**.

After a valid image is selected:

```text
[ Analyze Crop → ]
```

becomes active.

This prevents accidental API requests.

---

# 15. Button State

### Disabled

```text
[ Analyze Crop ]
```

### Ready

```text
[ Analyze Crop → ]
```

### Uploading

```text
[ Uploading image... ]
```

### Processing

```text
[ Analyzing crop... ]
```

### Success

Navigate to:

```text
/result/:id
```

The roadmap explicitly defines `/result/:id` as the detailed prediction result screen. 

---

# 16. Processing Experience

This is **very important for your project**.

Your prediction is not an instantaneous single-model operation. The pipeline performs multiple stages.

Therefore, don't simply show:

```text
Loading...
```

Instead show meaningful progress.

For example:

```text
┌────────────────────────────────────────────┐
│                                            │
│             🌱 Analyzing your crop        │
│                                            │
│        ███████████████░░░░░               │
│                                            │
│  ✓ Image quality checked                   │
│  ✓ Crop identified                         │
│  ● Checking for disease                    │
│  ○ Estimating severity                     │
│  ○ Checking for pests                      │
│  ○ Preparing recommendation                 │
│                                            │
│       Please don't close this page.        │
│                                            │
└────────────────────────────────────────────┘
```

This is much better UX.

---

# 17. Processing Stages

I recommend these frontend labels:

```text
1. Checking image
2. Identifying crop
3. Checking crop health
4. Estimating severity
5. Checking for pests
6. Preparing recommendations
```

Do **not** expose internal service names like:

```text
crop_identification_service
decision_routing
pest_classifier
severity_estimator
```

---

# 18. Important Backend Reality

Your frontend should **not fake progress percentages** such as:

```text
10%
20%
30%
40%
```

unless your backend actually provides stage/progress information.

Otherwise, a better UI is:

```text
✓ Completed
● Currently analyzing
○ Waiting
```

This avoids misleading the farmer.

---

# 19. Image Validation Errors

You need dedicated error states.

---

## No image

```text
Please upload a crop image before continuing.
```

---

## Unsupported format

```text
This image format isn't supported.

Please upload a JPG, JPEG, or PNG image.
```

---

## Image too large

Only if your backend has a defined size limit:

```text
This image is too large.

Please choose a smaller image.
```

---

# 20. Blurry Image

Because your preprocessing pipeline checks blur, the backend may reject a low-quality image.

Frontend result:

```text
┌────────────────────────────────────────────┐
│ ⚠ Image may be too blurry                  │
│                                            │
│ Please take another photo with the leaf    │
│ clearly in focus.                          │
│                                            │
│ [ Choose Another Image ]                   │
└────────────────────────────────────────────┘
```

Don't show:

```text
Blur variance = 72.43
```

---

# 21. Too Dark / Too Bright

Your preprocessing includes brightness validation.

User-friendly errors:

### Too dark

> **The image is too dark.**
> Try taking the photo in better lighting.

### Too bright

> **The image is too bright.**
> Avoid direct glare and try again.

---

# 22. Leaf Not Detected

Your preprocessing pipeline attempts to isolate the leaf.

If no suitable leaf is found:

```text
⚠ We couldn't identify a clear leaf in this image.

Please upload a photo where the crop leaf is clearly visible.

[ Choose Another Image ]
```

This is much more useful than:

```text
Leaf detection failed.
```

---

# 23. API Error

If `/predict` fails:

```text
┌────────────────────────────────────────────┐
│ ⚠ Analysis couldn't be completed           │
│                                            │
│ Something went wrong while analyzing       │
│ your image. Please try again.              │
│                                            │
│ [ Try Again ]   [ Choose Another Image ]   │
└────────────────────────────────────────────┘
```

---

# 24. Low Confidence Result

Your backend architecture includes confidence-aware behavior and recommends sending low-confidence results for expert review rather than presenting unverified advice. 

Therefore, if the backend returns something like:

```text
status: pending_expert_review
```

the frontend should **not** treat it as a normal diagnosis.

Show:

```text
┌────────────────────────────────────────────┐
│ ⏳ Review Required                         │
│                                            │
│ Smart Farming couldn't confidently        │
│ determine the crop condition.              │
│                                            │
│ Your result has been marked for review.    │
│                                            │
│ [ View Status ]                             │
└────────────────────────────────────────────┘
```

---

# 25. Upload Screen — Recommended Two-State Design

I recommend treating this screen as two primary states.

### State A — Upload

```text
┌─────────────────────────────────────────────┐
│ Analyze Your Crop                           │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │                                         │ │
│ │                📷                       │ │
│ │                                         │ │
│ │       Upload your crop image            │ │
│ │                                         │ │
│ │       Drag & drop here                  │ │
│ │                 or                      │ │
│ │       [ Choose Image ]                  │ │
│ │                                         │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ 💡 Tips for a better diagnosis              │
│ ✓ Clear image                               │
│ ✓ Good lighting                             │
│ ✓ Leaf clearly visible                      │
│                                             │
│                  [ Analyze Crop ]            │
└─────────────────────────────────────────────┘
```

### State B — Preview

```text
┌─────────────────────────────────────────────┐
│ Analyze Your Crop                           │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │                                         │ │
│ │             LEAF PREVIEW                │ │
│ │                                         │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ tomato_leaf.jpg                             │
│ 2.4 MB                                      │
│                                             │
│ [ Change Image ]                            │
│                                             │
│ ✓ Image format supported                    │
│ ✓ Image ready for analysis                  │
│                                             │
│              [ Analyze Crop → ]             │
└─────────────────────────────────────────────┘
```

---

# 26. Desktop Layout — Better Version

I would actually use a **two-column layout** once an image is selected.

```text
┌───────────────────────────────────────────────────────────────┐
│ Analyze Your Crop                                             │
│ Upload a clear leaf image for AI-powered analysis.            │
│                                                               │
│ ┌───────────────────────────────┐ ┌─────────────────────────┐ │
│ │                               │ │ 💡 Photo Tips           │ │
│ │                               │ │                         │ │
│ │        IMAGE PREVIEW          │ │ ✓ Clear leaf            │ │
│ │                               │ │ ✓ Good lighting         │ │
│ │                               │ │ ✓ In focus              │ │
│ │                               │ │ ✓ Leaf visible          │ │
│ │                               │ │                         │ │
│ │                               │ │ Supported:              │ │
│ │                               │ │ JPG / JPEG / PNG        │ │
│ └───────────────────────────────┘ └─────────────────────────┘ │
│                                                               │
│ tomato_leaf.jpg                           [ Change Image ]    │
│                                                               │
│                           [ Analyze Crop → ]                   │
└───────────────────────────────────────────────────────────────┘
```

This makes the screen feel like an actual **AI crop scanner**, rather than a file-management interface.

---

# 27. Mobile Layout

On mobile:

```text
┌──────────────────────────────┐
│ ← Analyze Your Crop     ⋮   │
├──────────────────────────────┤
│                              │
│ Upload a clear leaf image    │
│ for AI-powered analysis.     │
│                              │
│ ┌──────────────────────────┐ │
│ │                          │ │
│ │          📷              │ │
│ │                          │ │
│ │   Upload crop image      │ │
│ │                          │ │
│ │ [ Choose Image ]         │ │
│ │                          │ │
│ │ JPG • JPEG • PNG        │ │
│ └──────────────────────────┘ │
│                              │
│ 💡 Photo tips                │
│ ✓ Clear                     │
│ ✓ Good lighting             │
│ ✓ In focus                  │
│                              │
│                              │
│ [     Analyze Crop →     ]   │
│                              │
└──────────────────────────────┘
```

On mobile, I would **not** use the permanent desktop sidebar.

---

# 28. Optional Camera Capture

For your Indian farming use case, this is a **very valuable enhancement**.

Instead of only:

```text
[ Choose Image ]
```

offer:

```text
[ 📷 Take Photo ]
[ 🖼 Choose From Gallery ]
```

Mobile:

```text
┌──────────────────────────────┐
│ Upload crop image            │
│                              │
│ [ 📷 Take Photo ]            │
│                              │
│ [ 🖼 Choose From Gallery ]   │
│                              │
└──────────────────────────────┘
```

This is particularly appropriate because the user will often diagnose a crop **directly from the field**.

However, this is a frontend enhancement; your roadmap specifically guarantees drag-and-drop/file selection, not camera capture. 

---

# 29. Camera Flow

If you implement it:

```text
Take Photo
    ↓
Camera
    ↓
Capture
    ↓
Preview
    ↓
Retake / Use Photo
    ↓
Analyze Crop
```

Don't automatically analyze immediately after taking the picture.

Give the farmer a chance to inspect it.

---

# 30. Optional Image Cropper

I recommend **not adding an aggressive crop editor** initially.

Your backend already performs preprocessing and leaf isolation.

You don't want the user to accidentally crop away important visual information.

If you later add it:

```text
[ Crop Image ]
```

should be optional.

---

# 31. Upload Component Architecture

For your React/Vite project:

```text
src/
├── pages/
│   └── UploadPage.tsx
│
├── components/
│   └── upload/
│       ├── UploadHeader.tsx
│       ├── DropZone.tsx
│       ├── FilePicker.tsx
│       ├── CameraCapture.tsx
│       ├── ImagePreview.tsx
│       ├── ImageMetadata.tsx
│       ├── UploadTips.tsx
│       ├── UploadValidation.tsx
│       ├── AnalysisProgress.tsx
│       └── UploadError.tsx
│
├── api/
│   └── prediction.ts
│
└── hooks/
    └── usePrediction.ts
```

---

# 32. Component Hierarchy

```text
UploadPage
│
├── DashboardLayout
│   ├── Sidebar
│   └── Topbar
│
└── UploadContent
    │
    ├── UploadHeader
    │
    ├── UploadWorkspace
    │   │
    │   ├── DropZone
    │   │   └── FilePicker
    │   │
    │   └── UploadTips
    │
    ├── ImagePreview
    │
    ├── ImageValidation
    │
    ├── AnalyzeButton
    │
    └── AnalysisProgress
```

---

# 33. State Machine

This screen should have an explicit state model.

```text
EMPTY
  │
  │ select/drop image
  ↓
SELECTED
  │
  │ validation
  ├───────────────┐
  ↓               ↓
VALID           INVALID
  │               │
  │               └──→ ERROR
  │
  │ Analyze
  ↓
UPLOADING
  │
  ↓
PROCESSING
  │
  ├──────────────→ SUCCESS
  │                    │
  │                    ↓
  │              /result/:id
  │
  └──────────────→ ERROR
```

This will make your frontend implementation considerably cleaner.

---

# 34. API Integration

The roadmap specifies:

```http
POST /predict
```

for the upload/prediction workflow. 

Your frontend abstraction should therefore look conceptually like:

```text
UploadPage
     ↓
usePrediction()
     ↓
predictionApi.predict(file)
     ↓
POST /predict
     ↓
prediction response
     ↓
navigate(`/result/${id}`)
```

Don't let the UI component directly contain all of your `fetch`/Axios logic.

---

# 35. Recommended API Response Handling

The frontend should be prepared for:

```text
success
validation_error
low_confidence
server_error
network_error
```

For example:

```text
if success
    → /result/:id

if invalid image
    → show image error

if low confidence
    → show review state

if server error
    → retry

if network error
    → retry
```

---

# 36. Important UX Detail — Don't Leave the User on a Blank Screen

During inference, use:

```text
✓ Checking image
✓ Identifying crop
● Analyzing crop health
○ Estimating severity
○ Checking pests
○ Preparing recommendations
```

Your pipeline has enough meaningful stages to make this feel purposeful.

---

# 37. What NOT to Show

Avoid putting these on the upload screen:

```text
❌ Model accuracy
❌ EfficientNet-B0
❌ YOLOv8
❌ PyTorch
❌ Confidence thresholds
❌ API endpoint
❌ Dataset information
❌ Grad-CAM
❌ Disease treatment
❌ Fertilizer recommendations
```

The upload page's job is:

```text
GET GOOD IMAGE
       ↓
START ANALYSIS
```

The result page's job is:

```text
EXPLAIN RESULT
       ↓
SHOW EVIDENCE
       ↓
GIVE RECOMMENDATION
```

---

# 38. Navigation Flow

Your first major application flow should now be:

```text
Landing
   ↓
Login / Register
   ↓
Dashboard
   ↓
┌─────────────────┐
│   Scan Crop     │
└────────┬────────┘
         ↓
     /upload
         ↓
   Select Image
         ↓
      Preview
         ↓
  Analyze Crop
         ↓
     /predict
         ↓
    AI Pipeline
         ↓
   /result/:id
         ↓
Detailed Diagnosis
```

The `/result/:id` endpoint is explicitly part of your frontend roadmap and is intended to present the full prediction result. 

---

# 39. Final Recommended Screen

If you're building the first production-quality version, I recommend this exact composition:

```text
┌─────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                         🔔        👤 Manthan ▾ │
├───────────────┬─────────────────────────────────────────────────┤
│               │                                                 │
│ 🏠 Dashboard  │  Analyze Your Crop                              │
│               │  Upload a clear leaf image for AI analysis.    │
│ 📷 Scan Crop  │                                                 │
│               │  ┌───────────────────────────────────────────┐ │
│ 📋 History    │  │                                           │ │
│               │  │                  📷                       │ │
│ 🌱 My Farm    │  │                                           │ │
│               │  │       Upload your crop image             │ │
│ 🔔 Alerts     │  │                                           │ │
│               │  │       Drag & drop here                   │ │
│ ⚙ Settings    │  │                  or                       │ │
│               │  │          [ Choose Image ]                │ │
│               │  │                                           │ │
│               │  │       JPG • JPEG • PNG                   │ │
│               │  │                                           │ │
│               │  └───────────────────────────────────────────┘ │
│               │                                                 │
│               │  💡 Tips for a better diagnosis                │
│               │  ✓ Keep leaf clearly visible                   │
│               │  ✓ Use good lighting                            │
│               │  ✓ Keep image in focus                          │
│               │                                                 │
│               │                     [ Analyze Crop → ]          │
│               │                                                 │
└───────────────┴─────────────────────────────────────────────────┘
```

After image selection:

```text
┌─────────────────────────────────────────────────────────────────┐
│ Analyze Your Crop                                               │
│                                                                 │
│ ┌──────────────────────────────┐ ┌────────────────────────────┐ │
│ │                              │ │ 💡 Better diagnosis        │ │
│ │                              │ │                            │ │
│ │       LEAF IMAGE             │ │ ✓ Clear image             │ │
│ │                              │ │ ✓ Good lighting            │ │
│ │                              │ │ ✓ Leaf in focus            │ │
│ │                              │ │                            │ │
│ │                              │ │ JPG / JPEG / PNG           │ │
│ └──────────────────────────────┘ └────────────────────────────┘ │
│                                                                 │
│ tomato_leaf.jpg                              2.4 MB             │
│                                                                 │
│ [ Change Image ]                                                │
│                                                                 │
│                              [ Analyze Crop → ]                  │
└─────────────────────────────────────────────────────────────────┘
```

And during inference:

```text
┌─────────────────────────────────────────────┐
│                                             │
│             🌱 Analyzing Your Crop          │
│                                             │
│  ✓ Checking image                          │
│  ✓ Identifying crop                        │
│  ● Checking crop health                    │
│  ○ Estimating severity                     │
│  ○ Checking for pests                      │
│  ○ Preparing recommendation                 │
│                                             │
│       Please wait while we analyze         │
│       your crop.                            │
│                                             │
└─────────────────────────────────────────────┘
```

### The key design decision

Make `/upload` **simple and reassuring**. The farmer should never need to understand the AI pipeline to use it. Your sophisticated computer-vision pipeline should be **behind the scenes**, while the UI communicates only the actions the farmer needs to take: **choose a clear leaf image → review it → analyze → receive the diagnosis.**


# Smart Farming — Processing Screen UI/UX Specification

The **Processing Screen** appears immediately after the farmer clicks **“Analyze Crop”** on `/upload`.

Its job is to make the AI pipeline feel **transparent, trustworthy, and alive** while the backend processes the image.

Your system has multiple stages—preprocessing, crop identification, disease classification, severity estimation, pest analysis, and recommendation—so this screen is a particularly good place to communicate progress without exposing technical implementation details.

---

# 1. Screen Purpose

The farmer should understand three things:

1. **My image was received successfully.**
2. **The system is actively analyzing it.**
3. **The analysis is progressing through meaningful stages.**

The screen should answer:

> **“What is happening to my crop image right now?”**

---

# 2. Route / Navigation

I recommend **not creating a separate browser route** for this screen unless you specifically need refresh/recovery support.

Instead:

```text
/upload
   ↓
User clicks "Analyze Crop"
   ↓
Processing state
   ↓
/result/:id
```

So technically:

```text
UploadPage
   ├── upload state
   ├── preview state
   └── processing state
```

This is cleaner than:

```text
/upload
   ↓
/processing
   ↓
/result/:id
```

However, if you want a dedicated route for your project architecture, you can use:

```text
/processing/:jobId
```

I would consider that a **future enhancement**, not necessary for V1.

---

# 3. Overall Design

The processing screen should be much simpler than the dashboard.

No sidebar-heavy information.

No large navigation menu.

The focus should be:

```text
        Crop Image
            ↓
      AI Analysis
            ↓
       Progress
            ↓
        Result
```

Recommended layout:

```text
┌─────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                              👤 Manthan    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                                                             │
│                    🌱                                       │
│                                                             │
│              Analyzing Your Crop                            │
│                                                             │
│       We're checking your crop image...                     │
│                                                             │
│          ┌────────────────────────────┐                     │
│          │                            │                     │
│          │       CROP IMAGE           │                     │
│          │                            │                     │
│          └────────────────────────────┘                     │
│                                                             │
│          ━━━━━━━━━━━━━━━━━━━░░░░░                           │
│                                                             │
│                 3 of 6 stages                               │
│                                                             │
│                                                             │
│          ✓ Image quality checked                            │
│          ✓ Crop identified                                  │
│          ● Checking crop health                             │
│          ○ Estimating severity                              │
│          ○ Checking for pests                               │
│          ○ Preparing recommendation                         │
│                                                             │
│                                                             │
│             Please don't close this page.                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# 4. Header

Keep the header minimal.

```text
🌱 Smart Farming
```

Right:

```text
👤 Manthan
```

You don't need the full dashboard navigation because the user is currently in an active analysis process.

---

# 5. Main Heading

Use:

> **Analyzing Your Crop**

Not:

> Running Prediction Pipeline

Not:

> AI Inference in Progress

Not:

> Processing Request #1234

The user should understand it immediately.

---

# 6. Subtitle

Recommended:

> **We're checking your crop image for signs of disease, severity, and pests.**

This communicates what the system is doing without exposing implementation details.

---

# 7. Crop Image Preview

Show the image the farmer submitted.

Example:

```text
┌──────────────────────────────┐
│                              │
│                              │
│         LEAF IMAGE           │
│                              │
│                              │
└──────────────────────────────┘

tomato_leaf.jpg
```

Recommended image dimensions:

```text
Desktop:
280–360px

Mobile:
220–280px
```

Keep the image reasonably sized.

The purpose isn't image inspection—it is to reassure the user that **the correct image is being analyzed**.

---

# 8. Image Status

Under the image:

```text
✓ Image uploaded successfully
```

or:

```text
✓ Image received
```

This immediately distinguishes upload success from processing.

---

# 9. Main Progress Indicator

You have two good choices.

## Option A — Stage Progress

I recommend this.

```text
3 of 6 stages completed
```

and:

```text
━━━━━━━━━━━━━━━━━━░░░░░
```

This is better than pretending that the backend can accurately report:

```text
37%
```

unless your API actually provides numerical progress.

---

# 10. Pipeline Stages

Your frontend should present **six farmer-friendly stages**:

```text
1. Checking image
2. Identifying crop
3. Checking crop health
4. Estimating severity
5. Checking for pests
6. Preparing recommendation
```

These correspond conceptually to your existing pipeline without exposing internal service names.

---

# 11. Stage List

Recommended design:

```text
✓  Checking image
✓  Identifying crop
●  Checking crop health
○  Estimating severity
○  Checking for pests
○  Preparing recommendation
```

Where:

```text
✓ = completed
● = currently running
○ = pending
```

---

# 12. Stage Colors

Use semantic colors carefully.

### Completed

```text
✓
```

Use your success color.

### Active

```text
●
```

Use your primary brand color.

### Pending

```text
○
```

Use muted gray.

### Failed

```text
!
```

Use your error color.

---

# 13. Active Stage Animation

The currently running stage can have a subtle animation.

For example:

```text
● Checking crop health
```

with a small pulsing indicator.

Avoid excessive animations.

Don't make every stage spin.

---

# 14. Recommended Progress Animation

Example:

```text
Checking image       ●
Identifying crop     ●
Checking health      ●
```

The active indicator can gently pulse:

```text
● → ◉ → ● → ◉
```

Keep it subtle.

---

# 15. Don't Fake Backend Progress

This is **very important**.

Don't do:

```text
0%
10%
20%
30%
40%
50%
...
100%
```

with a timer.

If your backend finishes in 3 seconds but your animation takes 15 seconds, the UI becomes misleading.

Likewise, if the backend takes 30 seconds but your UI reaches 100% in 5 seconds, the user thinks the application is stuck.

Instead, tie stages to actual backend events whenever possible.

---

# 16. Best Architecture for Your Project

If `/predict` currently behaves as a single synchronous API call:

```text
POST /predict
        ↓
Backend pipeline
        ↓
Complete response
```

then the frontend can show a **controlled stage animation** but should treat it as an approximate visual representation.

For a future production architecture:

```text
POST /predict
       ↓
job_id
       ↓
processing
       ↓
GET /prediction/{job_id}/status
       ↓
stage updates
       ↓
completed
       ↓
result
```

Then your UI can show genuinely accurate stages.

---

# 17. Ideal Future API

For example:

```text
POST /predict
```

Response:

```json
{
  "job_id": "abc123",
  "status": "processing"
}
```

Then:

```text
GET /predict/abc123/status
```

could return:

```json
{
  "status": "processing",
  "stage": "disease_classification",
  "progress": 50
}
```

Then the frontend can accurately render:

```text
✓ Checking image
✓ Identifying crop
● Checking crop health
○ Estimating severity
○ Checking for pests
○ Preparing recommendation
```

You don't need this architecture for your current MVP, but it is the cleanest long-term solution.

---

# 18. Processing Messages

You can rotate small messages beneath the progress indicator.

For example:

### Stage 1

> Checking image quality...

### Stage 2

> Identifying your crop...

### Stage 3

> Checking the crop for disease...

### Stage 4

> Estimating disease severity...

### Stage 5

> Checking for possible pests...

### Stage 6

> Preparing your farming recommendations...

This makes the system feel intelligent without making unsupported claims.

---

# 19. Important — Don't Say "Disease Detected" During Processing

Avoid:

```text
Detecting disease...
```

That's okay.

But don't show:

```text
Disease detected!
```

before the pipeline has actually completed.

Likewise:

```text
Tomato confirmed!
```

should only appear after crop identification has actually returned that result.

The processing screen should not prematurely reveal diagnosis information.

---

# 20. Optional Crop Identification Reveal

You can make the transition slightly more engaging.

Once crop identification finishes:

```text
✓ Crop identified

Tomato
```

Then continue:

```text
● Checking crop health
```

For example:

```text
✓ Image quality checked

✓ Crop identified
  Tomato

● Checking crop health
```

This is useful because it reassures the farmer that the system is actually understanding the image.

---

# 21. Processing Card

I recommend placing everything inside one centered card.

```text
┌────────────────────────────────────────────────────┐
│                                                    │
│                   🌱                               │
│                                                    │
│             Analyzing Your Crop                   │
│                                                    │
│       We're checking your crop image...            │
│                                                    │
│          ┌──────────────────────────┐              │
│          │                          │              │
│          │       LEAF IMAGE         │              │
│          │                          │              │
│          └──────────────────────────┘              │
│                                                    │
│        ━━━━━━━━━━━━━━━░░░░░░                       │
│                                                    │
│             3 of 6 stages                          │
│                                                    │
│        ✓ Checking image                             │
│        ✓ Identifying crop                           │
│        ● Checking crop health                       │
│        ○ Estimating severity                        │
│        ○ Checking for pests                         │
│        ○ Preparing recommendation                    │
│                                                    │
│        Please don't close this page.               │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

# 22. Estimated Time

If you have measured your actual average inference time, you can show:

> Usually takes less than 30 seconds.

But **don't invent a number**.

If you haven't measured it:

```text
This may take a few moments.
```

is safer.

---

# 23. Cancel Button

I recommend **not** having:

```text
[ Cancel Analysis ]
```

for your first version unless your backend supports cancellation.

If the user leaves the page while `/predict` is running, the backend may continue processing.

So don't give the impression that clicking Cancel actually terminates inference if it doesn't.

---

# 24. Browser Navigation

You should also consider:

```text
← Back
```

During processing.

I recommend disabling the normal navigation or showing:

> **Your crop is still being analyzed. Are you sure you want to leave?**

If your request is synchronous, leaving the page could also lose the ability to show the result.

---

# 25. Leave Confirmation

If the user attempts to navigate away:

```text
┌─────────────────────────────────────────────┐
│ Leave analysis?                             │
│                                             │
│ Your crop is still being analyzed.         │
│ Leaving may interrupt your analysis view.   │
│                                             │
│ [ Continue Analysis ]   [ Leave ]           │
└─────────────────────────────────────────────┘
```

This is optional but good UX.

---

# 26. Error State

If the pipeline fails:

```text
┌─────────────────────────────────────────────┐
│                                             │
│                    ⚠                        │
│                                             │
│          Analysis Couldn't Complete         │
│                                             │
│  We couldn't finish analyzing your image.  │
│                                             │
│  Please try again or upload another image. │
│                                             │
│      [ Try Again ]   [ Choose Image ]      │
│                                             │
└─────────────────────────────────────────────┘
```

---

# 27. Don't Show Technical Errors

Never show:

```text
RuntimeError: CUDA out of memory
```

or:

```text
HTTP 500
```

or:

```text
Model inference failed
```

to the farmer.

Log these internally.

Frontend:

> **We couldn't complete the analysis. Please try again.**

---

# 28. Low Confidence Handling

If your backend determines that the result requires expert review, don't present the normal success transition.

Instead:

```text
┌─────────────────────────────────────────────┐
│                    ⏳                       │
│                                             │
│         Additional Review Required          │
│                                             │
│  The image could not be analyzed with       │
│  enough confidence for a reliable result.   │
│                                             │
│  We've marked this analysis for review.     │
│                                             │
│              [ View Status ]                │
└─────────────────────────────────────────────┘
```

Your roadmap explicitly describes low-confidence predictions being marked for expert review rather than showing potentially unsafe advice. 

---

# 29. Success Transition

When processing completes:

```text
✓ Analysis complete
```

Then:

```text
Navigating to your results...
```

After a short transition:

```text
/result/:id
```

The roadmap defines the result screen as the detailed diagnosis page. 

---

# 30. Success Animation

Keep it simple:

```text
✓
Analysis Complete
```

A subtle checkmark animation is enough.

Don't use a huge celebratory animation because the result could actually be:

```text
Severe disease
```

The user isn't necessarily receiving good news.

So don't use:

```text
🎉 Congratulations!
```

That's inappropriate for agricultural disease detection.

---

# 31. Mobile Processing Screen

Mobile should be extremely focused:

```text
┌──────────────────────────────┐
│ 🌱 Smart Farming             │
├──────────────────────────────┤
│                              │
│                              │
│          🌱                  │
│                              │
│    Analyzing Your Crop       │
│                              │
│ We're checking your crop     │
│ image for possible issues.   │
│                              │
│    ┌────────────────────┐    │
│    │                    │    │
│    │    LEAF IMAGE      │    │
│    │                    │    │
│    └────────────────────┘    │
│                              │
│ ━━━━━━━━━━━━━░░░░            │
│                              │
│       3 of 6 stages          │
│                              │
│ ✓ Checking image             │
│ ✓ Identifying crop           │
│ ● Checking crop health       │
│ ○ Estimating severity        │
│ ○ Checking for pests         │
│ ○ Preparing recommendation   │
│                              │
│                              │
│ Please wait...               │
│                              │
└──────────────────────────────┘
```

---

# 32. Mobile Don'ts

Don't put:

```text
Sidebar
Dashboard cards
Weather
Farm statistics
Recent diagnoses
```

on this screen.

The farmer is already waiting for an operation to finish.

**Reduce cognitive load.**

---

# 33. Visual Hierarchy

Use this hierarchy:

```text
        1
Analyzing Your Crop
        ↓
        2
     Crop Image
        ↓
        3
      Progress
        ↓
        4
    Stage Details
        ↓
        5
     Status Message
```

The progress should be visually dominant.

---

# 34. Component Architecture

For your React/Vite frontend:

```text
src/
├── pages/
│   └── UploadPage.tsx
│
├── components/
│   └── processing/
│       ├── ProcessingView.tsx
│       ├── ProcessingHeader.tsx
│       ├── ProcessingImage.tsx
│       ├── ProgressBar.tsx
│       ├── ProcessingStages.tsx
│       ├── ProcessingStage.tsx
│       ├── ProcessingMessage.tsx
│       ├── ProcessingError.tsx
│       └── ProcessingComplete.tsx
│
└── hooks/
    └── usePrediction.ts
```

---

# 35. Processing Component Hierarchy

```text
ProcessingView
│
├── ProcessingHeader
│
├── ProcessingImage
│
├── ProgressBar
│
├── ProcessingStages
│   ├── ProcessingStage
│   ├── ProcessingStage
│   ├── ProcessingStage
│   ├── ProcessingStage
│   ├── ProcessingStage
│   └── ProcessingStage
│
└── ProcessingMessage
```

---

# 36. State Model

Use an explicit state machine:

```text
UPLOADING
     ↓
PROCESSING
     ↓
COMPLETED
     │
     └────────→ /result/:id

PROCESSING
     │
     ├────────→ ERROR
     │
     └────────→ REVIEW_REQUIRED
```

And stage state:

```text
Stage
├── pending
├── active
├── completed
└── failed
```

---

# 37. Example Frontend Data Model

Conceptually:

```text
processingState = {
    status: "processing",
    currentStage: "disease",
    completedStages: [
        "image",
        "crop"
    ]
}
```

Then your UI derives:

```text
image       → completed
crop        → completed
disease     → active
severity    → pending
pest        → pending
recommendation → pending
```

This keeps the UI logic clean.

---

# 38. Important Backend/Frontend Separation

Your frontend should **not know how EfficientNet, YOLO, OpenCV or your recommendation model works**.

Frontend sees:

```text
Checking image
Identifying crop
Checking health
Estimating severity
Checking pests
Preparing recommendation
```

Backend handles:

```text
OpenCV
EfficientNet
Disease model
Severity estimator
YOLO
LLM recommendation
```

This is an important architectural boundary.

---

# 39. Recommended Processing Screen Text

### Initial

> **Analyzing Your Crop**

> We're checking your crop image for signs of disease, severity, and pests.

### Stage 1

> **Checking image quality...**

### Stage 2

> **Identifying your crop...**

### Stage 3

> **Checking crop health...**

### Stage 4

> **Estimating severity...**

### Stage 5

> **Checking for possible pests...**

### Stage 6

> **Preparing your farming recommendations...**

### Complete

> **Analysis complete**

> Your crop analysis is ready.

---

# 40. One Important Change From the Upload Screen

The upload screen is about:

```text
USER ACTION
```

The processing screen is about:

```text
SYSTEM ACTIVITY
```

So remove:

```text
Choose Image
Change Image
Upload Image
```

once processing starts.

The farmer should have **one clear mental model**:

> "My image is being analyzed. I need to wait."

---

# 41. Final Recommended Processing Screen

This is the version I would implement for your project:

```text
┌──────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                              👤 Manthan     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                                                              │
│                         🌱                                   │
│                                                              │
│                  Analyzing Your Crop                         │
│                                                              │
│       We're checking your crop image for signs of             │
│       disease, severity, and pests.                           │
│                                                              │
│              ┌────────────────────────┐                      │
│              │                        │                      │
│              │                        │                      │
│              │       LEAF IMAGE       │                      │
│              │                        │                      │
│              │                        │                      │
│              └────────────────────────┘                      │
│                                                              │
│              ━━━━━━━━━━━━━━━━━░░░░░                           │
│                                                              │
│                     3 of 6 stages                             │
│                                                              │
│              ✓  Checking image quality                       │
│              ✓  Identifying crop                             │
│              ●  Checking crop health                         │
│              ○  Estimating severity                          │
│              ○  Checking for pests                           │
│              ○  Preparing recommendation                     │
│                                                              │
│              This may take a few moments.                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### The key implementation decision for your current project

Because your existing `/predict` pipeline is a **multi-stage synchronous inference flow**, I would initially implement the processing UI as a **state inside the upload page**, rather than adding a new `/processing` route. Once you introduce a `job_id` + status endpoint, you can upgrade it to a real-time processing page with backend-driven stage progress.

That gives you a clean first version without pretending that the frontend knows the exact progress of the AI pipeline.

# Smart Farming — Diagnosis Result Screen UI/UX Specification

The **Diagnosis Result Screen** is the most important screen after `/upload`. This is where your Smart Farming project should demonstrate the actual value of your AI pipeline.

Your roadmap explicitly identifies `/result/:id` as the detailed prediction result page and describes it as the **centerpiece of the web dashboard**. It should present the crop, disease, severity, pest analysis, confidence, explanations, and recommendations. 

The screen should answer:

> **What is wrong with my crop?**

> **How serious is it?**

> **Why did the AI reach this conclusion?**

> **What should I do now?**

---

# 1. Route

```text
/result/:id
```

Example:

```text
/result/65f82c91
```

The `id` identifies the saved prediction.

---

# 2. Overall Result Flow

Your complete farmer journey becomes:

```text
Dashboard
    ↓
Scan Crop
    ↓
Upload
    ↓
Processing
    ↓
┌──────────────────────────────┐
│      DIAGNOSIS RESULT        │
└──────────────────────────────┘
    ↓
Crop Identification
    ↓
Disease Diagnosis
    ↓
Severity
    ↓
Pest Analysis
    ↓
Visual Explanation
    ↓
AI Recommendation
    ↓
Next Action
```

---

# 3. Most Important Design Principle

Do **not** make the result page look like an ML model output.

Bad:

```text
Prediction:
class_3

confidence:
0.93482

model:
efficientnet_b2
```

Instead:

```text
🍅 Tomato

⚠ Early Blight

Moderate severity

AI Confidence
94%

Recommended Action
...
```

The farmer needs a **decision**, not model internals.

---

# 4. Recommended Desktop Layout

```text
┌─────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                         🔔        👤 Manthan ▾     │
├───────────────┬─────────────────────────────────────────────────────┤
│               │                                                     │
│ 🏠 Dashboard  │  ← Back to Dashboard                               │
│               │                                                     │
│ 📷 Scan Crop  │  Crop Diagnosis                                    │
│               │  Analysis completed • Aug 26, 2026                 │
│ 📋 History    │                                                     │
│               │  ┌───────────────────────────────────────────────┐ │
│ 🌱 My Farm    │  │ 🍅 Tomato                                     │ │
│               │  │                                               │ │
│ 🔔 Alerts     │  │ ⚠ Early Blight                               │ │
│               │  │                                               │ │
│ ⚙ Settings    │  │ Moderate Severity                            │ │
│               │  │                                               │ │
│               │  │ AI Confidence: 94%                            │ │
│               │  └───────────────────────────────────────────────┘ │
│               │                                                     │
│               │  ┌──────────────────┐ ┌──────────────────────────┐ │
│               │  │ Original Image   │ │ AI Analysis              │ │
│               │  │                  │ │                          │ │
│               │  │    🌿 IMAGE      │ │ Disease affected areas   │ │
│               │  │                  │ │ highlighted              │ │
│               │  └──────────────────┘ └──────────────────────────┘ │
│               │                                                     │
│               │  Disease Details                                   │
│               │                                                     │
│               │  Severity                                            │
│               │  ███████████░░░  Moderate                           │
│               │                                                     │
│               │  Pest Analysis                                      │
│               │  🐛 Aphid        Low risk                           │
│               │                                                     │
│               │  ┌───────────────────────────────────────────────┐ │
│               │  │ 🌱 Recommended Actions                       │ │
│               │  │                                               │ │
│               │  │ Immediate actions...                          │ │
│               │  │ Prevention...                                 │ │
│               │  │ Monitoring...                                 │ │
│               │  └───────────────────────────────────────────────┘ │
│               │                                                     │
│               │       [ Save Result ] [ Scan Another Crop ]        │
│               │                                                     │
└───────────────┴─────────────────────────────────────────────────────┘
```

---

# 5. Result Page Header

At the top:

```text
← Back to Dashboard
```

Then:

> **Crop Diagnosis**

Subtitle:

> Analysis completed on Aug 26, 2026 at 4:18 PM

This helps the farmer understand that this is a historical diagnosis, not live sensor data.

---

# 6. Main Diagnosis Card

This should be the **hero card**.

Example:

```text
┌──────────────────────────────────────────────────────┐
│                                                      │
│ 🍅  TOMATO                                           │
│                                                      │
│ ⚠ EARLY BLIGHT                                      │
│                                                      │
│ Moderate Severity                                   │
│                                                      │
│ AI Confidence                          94%           │
│ ███████████████████░░                              │
│                                                      │
└──────────────────────────────────────────────────────┘
```

This should be visible **without scrolling**.

---

# 7. Crop Identification

Show:

```text
Crop
Tomato
```

If your model returns confidence:

```text
Crop confidence
98%
```

But don't make the farmer focus on two different confidence numbers.

Better:

```text
🍅 Tomato
Identified with high confidence
```

Then detailed confidence can be available in an expandable section.

---

# 8. Disease Diagnosis

The disease name should be visually dominant after the crop.

Example:

```text
⚠ Early Blight
```

For a healthy crop:

```text
✓ Healthy
```

For unknown:

```text
? Unable to determine
```

---

# 9. Disease Status Variants

You should design for at least these states.

### Healthy

```text
┌──────────────────────────────────────────────┐
│ ✓ Crop appears healthy                       │
│                                              │
│ No significant disease signs were detected. │
└──────────────────────────────────────────────┘
```

### Disease detected

```text
┌──────────────────────────────────────────────┐
│ ⚠ Early Blight detected                     │
│                                              │
│ Moderate severity                            │
└──────────────────────────────────────────────┘
```

### Low confidence

```text
┌──────────────────────────────────────────────┐
│ ⏳ Review Required                           │
│                                              │
│ The system could not confidently determine   │
│ the crop condition.                          │
└──────────────────────────────────────────────┘
```

The last case is consistent with your roadmap's confidence-aware design. 

---

# 10. Severity Card

Your backend already estimates severity using the affected-area concept.

The frontend should convert that into a very understandable visualization.

```text
┌──────────────────────────────────────────────┐
│ Severity                                     │
│                                              │
│              MODERATE                        │
│                                              │
│ █████████████░░░░░░░                         │
│                                              │
│ The affected area indicates a moderate      │
│ level of crop damage.                        │
└──────────────────────────────────────────────┘
```

---

# 11. Severity Levels

Use three primary levels:

```text
Healthy
Mild
Moderate
Severe
```

Visual:

```text
Healthy    ✓
Mild       ●
Moderate   ●
Severe     ⚠
```

Don't rely solely on color.

Always display the text.

---

# 12. Severity Explanation

Don't just say:

```text
Moderate
```

Give a short explanation:

> **Moderate:** Visible affected areas are present and should be monitored and treated according to the recommended action.

Keep this concise.

The exact thresholds should remain backend logic rather than being hard-coded into the UI.

---

# 13. Original Image + AI Explanation

This is one of the most important parts of your project.

Your roadmap specifically describes visual explainability using **Grad-CAM** and wants explanations such as showing where the model focused. 

Use a two-panel layout:

```text
┌────────────────────────┐  ┌────────────────────────┐
│ Original Image         │  │ AI Focus                │
│                        │  │                        │
│                        │  │                        │
│      LEAF IMAGE        │  │   HEATMAP OVERLAY      │
│                        │  │                        │
│                        │  │                        │
└────────────────────────┘  └────────────────────────┘
```

---

# 14. Explainability Section

Heading:

> **Why the AI Made This Diagnosis**

Subtitle:

> The highlighted areas show regions that influenced the model's prediction.

Then:

```text
Original Image          AI Focus
┌──────────────┐       ┌──────────────┐
│              │       │   🔥🔥        │
│     LEAF     │       │  🔥 LEAF      │
│              │       │    🔥         │
└──────────────┘       └──────────────┘
```

This is much more valuable for a hackathon demonstration than simply displaying:

```text
Confidence: 94%
```

---

# 15. Add a Toggle

For the Grad-CAM area:

```text
[ Original ] [ AI Focus ]
```

Or:

```text
Original Image
      ↕
AI Focus
```

A useful implementation is a slider:

```text
Original ─────────●──────── AI Focus
```

This allows the user to compare the original and heatmap.

---

# 16. Explainability Disclaimer

Because Grad-CAM is an **explanation of model attention**, not proof of causation, use wording like:

> **AI Focus:** Highlighted areas show regions that influenced the model's prediction. They are provided to help explain the result.

Do not say:

> "These pixels prove the disease."

---

# 17. Disease Information

After the visual explanation:

```text
## About the Diagnosis

Early blight is a fungal disease that can affect tomato leaves
and may progress under favorable conditions.
```

Keep this concise.

If your recommendation model generates disease-specific information, you can populate this dynamically.

---

# 18. Pest Analysis

Your pipeline also performs pest classification/detection.

Therefore, this should have its own section.

```text
┌──────────────────────────────────────────────────┐
│ 🐛 Pest Analysis                                 │
│                                                  │
│ Possible Pest                                    │
│ Aphid                                            │
│                                                  │
│ Confidence                        91%             │
│                                                  │
│ Status                                            │
│ Low Risk                                          │
└──────────────────────────────────────────────────┘
```

If no pest is detected:

```text
┌──────────────────────────────────────────────────┐
│ 🐛 Pest Analysis                                 │
│                                                  │
│ ✓ No significant pest detected                  │
└──────────────────────────────────────────────────┘
```

---

# 19. Multiple Pest Results

If your backend eventually supports multiple detections:

```text
Pest Analysis

┌────────────────────────────────────────────┐
│ Aphid                 91%                  │
│ Army Worm             72%                  │
│ Spider Mite           41%                  │
└────────────────────────────────────────────┘
```

But don't display low-confidence predictions as confirmed pests.

---

# 20. Recommendation Section

This should be the **second-most important section after the diagnosis**.

Your roadmap explicitly defines AI-powered recommendations using the diagnosis, severity, weather, soil, crop stage and farmer context. 

Use:

```text
┌─────────────────────────────────────────────────────┐
│ 🌱 What You Should Do                               │
│                                                     │
│ Based on your crop diagnosis and farm context:      │
│                                                     │
│ 1. Immediate Action                                 │
│    ...                                               │
│                                                     │
│ 2. Treatment / Management                           │
│    ...                                               │
│                                                     │
│ 3. Prevention                                       │
│    ...                                               │
│                                                     │
│ 4. Monitor                                          │
│    ...                                               │
└─────────────────────────────────────────────────────┘
```

---

# 21. Recommendation Categories

I strongly recommend structuring the LLM output into categories rather than displaying one giant paragraph.

### Immediate Action

```text
What should I do now?
```

### Treatment

```text
What should I use/do to manage the problem?
```

### Prevention

```text
How can I prevent it from spreading?
```

### Monitoring

```text
What should I watch over the next few days?
```

This makes the AI recommendation much more useful.

---

# 22. Example Recommendation

For example:

```text
🌱 Recommended Actions

1. Immediate Action
Inspect nearby tomato leaves for similar symptoms and remove
severely affected leaves where appropriate.

2. Management
Follow locally approved disease-management practices and
product-label instructions.

3. Prevention
Maintain suitable spacing and avoid prolonged leaf wetness.

4. Monitor
Recheck the crop regularly for increasing affected areas.
```

Avoid giving exact pesticide dosages unless your recommendation system is specifically designed and validated to provide them.

---

# 23. Farm Context

This is where your project can become significantly more unique.

Instead of:

```text
AI Recommendation
...
```

show:

```text
Recommendation based on:

📍 Anand, Gujarat
🌱 Tomato
🌤 Current weather
🌾 Growth stage
📋 Previous diagnosis
```

Your roadmap explicitly describes the Farm Context Engine as combining location, plot, crop history, growth stage, weather, soil and recent actions. 

---

# 24. Context Card

Example:

```text
┌────────────────────────────────────────────────┐
│ 🌾 Recommendation Context                     │
│                                                │
│ Location       Anand, Gujarat                  │
│ Crop           Tomato                          │
│ Growth Stage  Flowering                        │
│ Weather        29°C • 74% humidity             │
│ Last Analysis  2 days ago                     │
└────────────────────────────────────────────────┘
```

Only show fields that actually exist.

**Do not invent soil/growth-stage data** if the farmer hasn't provided them.

---

# 25. Confidence Information

The result should show confidence, but not make it the center of the page.

Good:

```text
AI Confidence
94%
```

Better:

```text
AI Confidence
94%
High confidence
```

You can add an information icon:

```text
94%   ⓘ
```

Tooltip:

> Confidence indicates how strongly the model supports this prediction. It does not guarantee that the diagnosis is correct.

---

# 26. Technical Details — Optional

For a normal farmer, hide technical details.

For your **hackathon/demo version**, add an expandable section:

```text
▸ Technical Details
```

Inside:

```text
Crop model
Disease model
Pest model
Prediction confidence
Processing time
Prediction ID
```

This is useful when judges want to see the engineering behind the product.

But it shouldn't dominate the farmer UI.

---

# 27. Recommended Technical Details

```text
┌────────────────────────────────────────────┐
│ Technical Details                          │
│                                            │
│ Prediction ID    #SF-2026-0826-00123      │
│ Crop confidence  98%                       │
│ Disease confidence 94%                     │
│ Processing time  8.4 sec                   │
└────────────────────────────────────────────┘
```

Don't expose model file paths or internal backend architecture.

---

# 28. Result Actions

At the bottom:

```text
[ 📷 Scan Another Crop ]
[ 📋 View History ]
```

Optional:

```text
[ Download Report ]
```

The primary action should be:

> **Scan Another Crop**

because it drives continued use.

---

# 29. Download Report

This would be a good enhancement for your project.

Button:

```text
↓ Download Diagnosis Report
```

Generate something like:

```text
SMART FARMING
Crop Diagnosis Report

Crop:
Tomato

Disease:
Early Blight

Severity:
Moderate

Confidence:
94%

Pest:
Aphid

Recommendations:
...

Date:
26 August 2026
```

This is especially useful for farmers who want to share the result with an agriculture officer or expert.

---

# 30. Save Result

If every prediction is already stored by your backend, don't use:

```text
[ Save Result ]
```

because the result is already saved.

Instead use:

```text
[ Add Note ]
```

or:

```text
[ Download Report ]
```

Your roadmap already describes prediction history as persistent data. 

---

# 31. Farmer Notes — Good Enhancement

Add:

```text
📝 Add Farmer Note
```

Example:

```text
"First noticed spots 3 days ago."
```

This can become extremely useful later for historical analysis.

---

# 32. Diagnosis Timeline

For your more advanced version:

```text
Crop History

Aug 26
⚠ Moderate Early Blight

Aug 23
● Mild Early Blight

Aug 18
✓ Healthy
```

This helps the farmer understand:

> **Is my crop getting better or worse?**

This is a strong feature because your prediction history already provides the underlying records.

---

# 33. Result Page — Recommended Information Hierarchy

Use this exact order:

```text
1. Diagnosis Summary
       ↓
2. Crop + Disease + Severity
       ↓
3. Confidence
       ↓
4. Original Image + AI Focus
       ↓
5. Disease Explanation
       ↓
6. Pest Analysis
       ↓
7. Farm Context
       ↓
8. Recommended Actions
       ↓
9. Technical Details
       ↓
10. Next Actions
```

---

# 34. Full Desktop Wireframe

```text
┌──────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                              🔔       👤 Manthan ▾ │
├───────────────┬──────────────────────────────────────────────────────┤
│               │                                                      │
│ 🏠 Dashboard  │  ← Back to Dashboard                                │
│               │                                                      │
│ 📷 Scan Crop  │  Crop Diagnosis                                     │
│               │  Analysis completed • Aug 26, 2026                  │
│ 📋 History    │                                                      │
│               │  ┌────────────────────────────────────────────────┐ │
│ 🌱 My Farm    │  │ 🍅 TOMATO                                      │ │
│               │  │                                                │ │
│ 🔔 Alerts     │  │ ⚠ EARLY BLIGHT                                │ │
│               │  │                                                │ │
│ ⚠ Moderate    │  │ AI Confidence: 94%                             │ │
│ ⚙ Settings    │  │                                                │ │
│               │  └────────────────────────────────────────────────┘ │
│               │                                                      │
│               │  ┌─────────────────────┐ ┌────────────────────────┐ │
│               │  │ Original Image      │ │ AI Focus               │ │
│               │  │                     │ │                        │ │
│               │  │      🌿             │ │       🔥🌿             │ │
│               │  │                     │ │                        │ │
│               │  └─────────────────────┘ └────────────────────────┘ │
│               │                                                      │
│               │  ┌────────────────────────────────────────────────┐ │
│               │  │ Severity                                         │ │
│               │  │                                                │ │
│               │  │ MODERATE                                       │ │
│               │  │ █████████████░░░░                             │ │
│               │  └────────────────────────────────────────────────┘ │
│               │                                                      │
│               │  ┌────────────────────────────────────────────────┐ │
│               │  │ 🐛 Pest Analysis                               │ │
│               │  │                                                │ │
│               │  │ Aphid                         91%              │ │
│               │  └────────────────────────────────────────────────┘ │
│               │                                                      │
│               │  ┌────────────────────────────────────────────────┐ │
│               │  │ 🌱 Recommended Actions                         │ │
│               │  │                                                │ │
│               │  │ Immediate Action                                │ │
│               │  │ ...                                            │ │
│               │  │                                                │ │
│               │  │ Management                                      │ │
│               │  │ ...                                            │ │
│               │  │                                                │ │
│               │  │ Prevention                                      │ │
│               │  │ ...                                            │ │
│               │  └────────────────────────────────────────────────┘ │
│               │                                                      │
│               │      [ Scan Another Crop ] [ View History ]         │
│               │                                                      │
└───────────────┴──────────────────────────────────────────────────────┘
```

---

# 35. Mobile Result Screen

The mobile version should be **vertical**.

```text
┌───────────────────────────────┐
│ ← Diagnosis             ⋮     │
├───────────────────────────────┤
│                               │
│ 🍅 Tomato                     │
│                               │
│ ⚠ Early Blight                │
│                               │
│ Moderate Severity             │
│                               │
│ AI Confidence                 │
│ 94%                           │
│                               │
├───────────────────────────────┤
│ Original Image                │
│                               │
│       🌿 IMAGE                │
│                               │
├───────────────────────────────┤
│ AI Focus                      │
│                               │
│       🔥🌿 HEATMAP            │
│                               │
│ Why this diagnosis?           │
│ Highlighted regions show      │
│ areas that influenced the     │
│ prediction.                   │
├───────────────────────────────┤
│ Severity                      │
│                               │
│ MODERATE                      │
│ ███████████░░                 │
├───────────────────────────────┤
│ 🐛 Pest Analysis              │
│                               │
│ Aphid                 91%     │
├───────────────────────────────┤
│ 🌱 What You Should Do         │
│                               │
│ 1. Immediate Action           │
│ ...                           │
│                               │
│ 2. Management                 │
│ ...                           │
│                               │
│ 3. Prevention                 │
│ ...                           │
├───────────────────────────────┤
│                               │
│ [ 📷 Scan Another Crop ]      │
│ [ 📋 View History ]           │
│                               │
└───────────────────────────────┘
```

---

# 36. Healthy Result

You need a completely different visual state.

```text
┌────────────────────────────────────────────────┐
│                                                │
│                ✓                               │
│                                                │
│             Tomato                             │
│                                                │
│       Crop appears healthy                     │
│                                                │
│      No significant disease signs              │
│      were detected.                            │
│                                                │
│      AI Confidence: 98%                        │
│                                                │
└────────────────────────────────────────────────┘
```

Then:

```text
🌱 Recommended Monitoring

Continue regular crop monitoring and inspect
new growth for changes.
```

Don't show a scary red severity card for a healthy crop.

---

# 37. Severe Result

For severe:

```text
┌────────────────────────────────────────────────┐
│ ⚠ Attention Required                           │
│                                                │
│ Tomato                                         │
│ Late Blight                                    │
│                                                │
│ SEVERE                                         │
│                                                │
│ The detected condition requires prompt         │
│ attention.                                     │
└────────────────────────────────────────────────┘
```

Then immediately:

```text
🌱 Recommended Actions
```

Don't make the farmer scroll through technical details before reaching the action.

---

# 38. Low Confidence Result

This is an important safety state:

```text
┌────────────────────────────────────────────────┐
│ ⏳ Additional Review Required                  │
│                                                │
│ The system could not confidently identify      │
│ the crop condition.                            │
│                                                │
│ Avoid relying on this result for treatment     │
│ decisions until it has been reviewed.         │
│                                                │
│ [ View Status ]                                │
│ [ Scan Another Image ]                         │
└────────────────────────────────────────────────┘
```

This aligns with the roadmap's expert-review mechanism. 

---

# 39. Error / Failed Result

```text
┌────────────────────────────────────────────────┐
│ ⚠ Analysis Unavailable                        │
│                                                │
│ We couldn't generate a reliable diagnosis      │
│ from this image.                               │
│                                                │
│ Please try a clearer image.                    │
│                                                │
│ [ Scan Another Crop ]                          │
└────────────────────────────────────────────────┘
```

---

# 40. API Data Needed

Your frontend result screen should conceptually consume a prediction object containing:

```text id="w5zv6q"
predictionId

crop
cropConfidence

disease
diseaseConfidence

severity
severityPercentage

pest
pestConfidence

originalImageUrl
processedImageUrl
gradcamImageUrl

recommendation

status

createdAt
```

The exact field names should follow your **actual backend response schema** rather than being invented in the frontend.

---

# 41. React Component Architecture

I recommend:

```text
src/
├── pages/
│   └── DiagnosisResultPage.tsx
│
├── components/
│   └── diagnosis/
│       ├── DiagnosisHeader.tsx
│       ├── DiagnosisSummary.tsx
│       ├── CropResultCard.tsx
│       ├── DiseaseResultCard.tsx
│       ├── ConfidenceBadge.tsx
│       ├── SeverityCard.tsx
│       ├── ImageComparison.tsx
│       ├── GradCAMViewer.tsx
│       ├── DiseaseExplanation.tsx
│       ├── PestAnalysisCard.tsx
│       ├── FarmContextCard.tsx
│       ├── RecommendationCard.tsx
│       ├── TechnicalDetails.tsx
│       ├── DiagnosisTimeline.tsx
│       └── ResultActions.tsx
│
├── api/
│   └── predictions.ts
│
└── hooks/
    └── usePrediction.ts
```

---

# 42. Component Hierarchy

```text
DiagnosisResultPage
│
├── PageHeader
│
├── DiagnosisSummary
│   ├── CropResult
│   ├── DiseaseResult
│   ├── Severity
│   └── Confidence
│
├── ExplainabilitySection
│   ├── OriginalImage
│   └── GradCAMViewer
│
├── DiseaseDetails
│
├── PestAnalysis
│
├── FarmContext
│
├── RecommendationCard
│   ├── ImmediateAction
│   ├── Management
│   ├── Prevention
│   └── Monitoring
│
├── TechnicalDetails
│
└── ResultActions
```

---

# 43. Recommended Screen Priority

For your actual project, I would prioritize the implementation like this:

### P0 — Must Have

```text
✓ Crop
✓ Disease
✓ Confidence
✓ Severity
✓ Original image
✓ AI/Grad-CAM image
✓ Pest result
✓ Recommendation
✓ Scan another crop
✓ History navigation
```

### P1 — Strongly Recommended

```text
✓ Farm context
✓ Disease explanation
✓ Recommendation categories
✓ Download report
✓ Technical details
```

### P2 — Advanced

```text
✓ Diagnosis timeline
✓ Farmer notes
✓ Multi-plot comparison
✓ Historical severity trend
✓ Follow-up reminders
```

The P1/P2 features should only display information that your backend actually provides.

---

# 44. The Most Important UX Decision

Your result screen should have **three visual layers**:

```text
┌──────────────────────────────────────────────┐
│ 1. WHAT IS WRONG?                            │
│                                              │
│ Tomato → Early Blight → Moderate             │
├──────────────────────────────────────────────┤
│ 2. WHY DOES THE AI THINK SO?                 │
│                                              │
│ Original Image + Grad-CAM                    │
├──────────────────────────────────────────────┤
│ 3. WHAT SHOULD I DO?                         │
│                                              │
│ AI/Farm-context recommendations              │
└──────────────────────────────────────────────┘
```

That structure is excellent for both **real farmer usability and your hackathon demonstration**.

---

# 45. Final Result Screen

If I were implementing your Smart Farming frontend, the final hierarchy would be:

```text
                    CROP DIAGNOSIS
                           │
             ┌─────────────┴─────────────┐
             │                           │
          TOMATO                    EARLY BLIGHT
             │                           │
             └─────────────┬─────────────┘
                           │
                    MODERATE SEVERITY
                           │
                       94% CONFIDENCE
                           │
             ┌─────────────┴─────────────┐
             │                           │
       ORIGINAL IMAGE               AI FOCUS
             │                       GRAD-CAM
             └─────────────┬─────────────┘
                           │
                    DISEASE DETAILS
                           │
                     PEST ANALYSIS
                           │
                    FARM CONTEXT
                           │
                ┌──────────┴──────────┐
                │                     │
          IMMEDIATE ACTION        PREVENTION
                │                     │
                └──────────┬──────────┘
                           │
                    MONITORING PLAN
                           │
             ┌─────────────┴─────────────┐
             │                           │
      SCAN ANOTHER CROP             VIEW HISTORY
```

**This should be the strongest screen in your entire frontend.** Your dashboard gets the farmer into the system, the upload screen gets the image into the pipeline, but **this screen is where you prove that your Smart Farming project actually provides useful intelligence rather than merely running an image classifier.**


# Smart Farming — History Screen UI/UX Specification

The **History Screen** should allow the farmer to answer:

> **“What happened to my crops in the past?”**

and more importantly:

> **“Is my crop condition improving or getting worse?”**

For your project, I recommend making History more than a simple list of previous predictions. It should combine **diagnosis history, filtering, trend visualization, and quick access to previous reports**.

---

# 1. Route

```text
/history
```

From:

```text
Dashboard
   ↓
History
```

And from the Diagnosis Result screen:

```text
Diagnosis Result
      ↓
 View History
      ↓
 /history
```

---

# 2. Main Purpose

The screen should allow users to:

* View previous crop scans
* Search previous diagnoses
* Filter by crop
* Filter by disease
* Filter by severity
* Filter by date
* See whether the condition is improving/worsening
* Open an old diagnosis
* Download an old report
* Delete an old record if your backend supports deletion

Your roadmap describes prediction history as persistent records containing the image, crop, disease, confidence, severity, recommendations, and timestamp, so these are the core data points the history UI should expose. 

---

# 3. Overall Desktop Layout

```text
┌─────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                         🔔        👤 Manthan ▾     │
├───────────────┬─────────────────────────────────────────────────────┤
│               │                                                     │
│ 🏠 Dashboard  │  Diagnosis History                                │
│               │                                                     │
│ 📷 Scan Crop  │  Track your previous crop analyses                │
│               │                                                     │
│ 📋 History ●  │  ┌───────────────────────────────────────────────┐ │
│               │  │ Total Scans     Diseases     Healthy     ... │ │
│ 🌱 My Farm    │  │      24            8           16            │ │
│               │  └───────────────────────────────────────────────┘ │
│ 🔔 Alerts     │                                                     │
│               │  Search & Filters                                  │
│ ⚙ Settings    │  [🔍 Search] [Crop ▾] [Disease ▾] [Severity ▾]     │
│               │                                                     │
│               │  Recent Diagnoses                                  │
│               │                                                     │
│               │  ┌───────────────────────────────────────────────┐ │
│               │  │ IMG │ Tomato │ Early Blight │ Moderate │ ...│ │
│               │  ├───────────────────────────────────────────────┤ │
│               │  │ IMG │ Cotton │ Healthy      │ Healthy  │ ...│ │
│               │  ├───────────────────────────────────────────────┤ │
│               │  │ IMG │ Potato │ Late Blight  │ Severe   │ ...│ │
│               │  └───────────────────────────────────────────────┘ │
│               │                                                     │
│               │              [1] [2] [3] →                         │
│               │                                                     │
└───────────────┴─────────────────────────────────────────────────────┘
```

---

# 4. Page Header

Use:

> **Diagnosis History**

Subtitle:

> **Track and review your previous crop analyses.**

Avoid technical wording such as:

> Prediction Database

or:

> Model Inference History.

---

# 5. Summary Cards

At the top, show a small overview.

Recommended:

```text
┌──────────────────┐
│ Total Scans      │
│                  │
│ 24               │
└──────────────────┘

┌──────────────────┐
│ Healthy          │
│                  │
│ 16               │
└──────────────────┘

┌──────────────────┐
│ Issues Detected  │
│                  │
│ 8                │
└──────────────────┘

┌──────────────────┐
│ Severe Cases     │
│                  │
│ 2                │
└──────────────────┘
```

These values should come from actual stored records.

---

# 6. Better Summary Cards

Because this is a farming application, I would slightly change the wording:

```text
Total Analyses
24

Healthy Crops
16

Issues Detected
8

Needs Attention
2
```

This is more farmer-friendly than:

```text
Disease Count
```

---

# 7. Add a Trend Card

This is where your History screen can become much more interesting.

Below the summary cards:

```text
┌──────────────────────────────────────────────────────────┐
│ Crop Health Trend                                        │
│                                                          │
│ Severity                                                 │
│                                                          │
│  Severe │                         ●                      │
│         │                    ●                           │
│ Moderate│             ●────●                            │
│         │        ●────                                    │
│ Mild    │   ●                                             │
│         └────────────────────────────────────────────     │
│           Aug 1   Aug 8   Aug 15   Aug 22                │
└──────────────────────────────────────────────────────────┘
```

This lets the farmer see whether a particular crop is getting better or worse.

**Important:** don't display a trend unless you have enough historical observations for it to be meaningful.

---

# 8. Crop Filter

Use:

```text
Crop
[ All Crops ▾ ]
```

Example options:

```text
All Crops
Tomato
Potato
Cotton
Groundnut
Pepper Bell
```

These should match the crops supported by your actual crop-identification model.

---

# 9. Disease Filter

```text
Disease
[ All Diseases ▾ ]
```

Example:

```text
All Diseases
Healthy
Early Blight
Late Blight
...
```

Populate this dynamically from your backend rather than hard-coding disease names wherever possible.

---

# 10. Severity Filter

```text
Severity
[ All Levels ▾ ]
```

Options:

```text
All Levels
Healthy
Mild
Moderate
Severe
```

---

# 11. Date Filter

Use:

```text
Date
[ Last 7 days ▾ ]
```

Options:

```text
Today
Last 7 days
Last 30 days
Last 3 months
This year
Custom range
```

---

# 12. Search

Search should support things like:

```text
🔍 Search crop or disease...
```

Examples:

```text
Tomato
Early Blight
Cotton
Healthy
```

Don't require the user to search by prediction ID.

---

# 13. History Table — Desktop

I recommend a table rather than large cards on desktop.

```text
┌─────┬─────────┬──────────────┬──────────┬──────────┬──────────────┐
│ Img │ Crop    │ Diagnosis    │ Severity │ Conf.    │ Date         │
├─────┼─────────┼──────────────┼──────────┼──────────┼──────────────┤
│ 🌿  │ Tomato  │ Early Blight │ Moderate │ 94%      │ Aug 26, 2026 │
│ 🌿  │ Cotton  │ Healthy      │ Healthy  │ 98%      │ Aug 24, 2026 │
│ 🌿  │ Potato  │ Late Blight  │ Severe   │ 91%      │ Aug 21, 2026 │
│ 🌿  │ Tomato  │ Healthy      │ Healthy  │ 97%      │ Aug 18, 2026 │
└─────┴─────────┴──────────────┴──────────┴──────────┴──────────────┘
```

---

# 14. Table Columns

Recommended:

```text
Image
Crop
Diagnosis
Severity
Confidence
Date
Action
```

Don't add too many columns.

Avoid:

```text
Model
Framework
Inference Time
Device
Tensor Shape
```

Those belong in technical details, not history.

---

# 15. History Row

Example:

```text
┌─────────────────────────────────────────────────────────────────┐
│ 🌿  Tomato                                                       │
│     Early Blight                                                 │
│                                                                  │
│     Moderate        94%        Aug 26, 2026        View →       │
└─────────────────────────────────────────────────────────────────┘
```

---

# 16. Severity Badge

Use text + icon.

### Healthy

```text
✓ Healthy
```

### Mild

```text
● Mild
```

### Moderate

```text
● Moderate
```

### Severe

```text
⚠ Severe
```

Don't depend only on red/green colors because color alone isn't sufficiently accessible.

---

# 17. Confidence Display

Use:

```text
94%
```

rather than:

```text
0.9417823
```

If needed:

```text
94% High
```

Keep it compact.

---

# 18. Date Display

Instead of:

```text
2026-08-26T16:18:42.431Z
```

show:

```text
Aug 26, 2026
4:18 PM
```

For recent entries:

```text
Today
4:18 PM
```

or:

```text
Yesterday
11:42 AM
```

This is much easier for farmers.

---

# 19. Actions

Each row should have:

```text
[ View ]
```

Clicking it:

```text
/history
     ↓
/result/:id
```

Optional menu:

```text
⋮
├── View Diagnosis
├── Download Report
└── Delete
```

Only provide Delete if your backend supports it.

---

# 20. "View Diagnosis" Interaction

When the user clicks:

```text
View →
```

open:

```text
/result/:id
```

The result screen should show exactly the same diagnosis associated with that history record.

Don't rerun the AI model.

This is an important architecture point:

```text
History
   ↓
Stored Prediction
   ↓
Result
```

not:

```text
History
   ↓
Run Model Again
   ↓
Result
```

---

# 21. Mobile History Screen

Don't try to squeeze the desktop table into a phone.

Use cards.

```text
┌───────────────────────────────┐
│ ← Diagnosis History       ⋮   │
├───────────────────────────────┤
│                               │
│ Diagnosis History             │
│ Track your previous analyses  │
│                               │
├───────────────────────────────┤
│ Total       Healthy   Issues  │
│ 24          16        8       │
├───────────────────────────────┤
│ 🔍 Search...                  │
│                               │
│ [Crop ▾] [Severity ▾]         │
├───────────────────────────────┤
│                               │
│ 🌿  Tomato                    │
│     Early Blight              │
│                               │
│     Moderate       94%        │
│     Aug 26, 2026              │
│                               │
│                  View →       │
├───────────────────────────────┤
│ 🌿  Cotton                    │
│     ✓ Healthy                 │
│                               │
│     98%            Aug 24     │
│                               │
│                  View →       │
├───────────────────────────────┤
│ 🌿  Potato                    │
│     Late Blight               │
│                               │
│     ⚠ Severe       91%       │
│     Aug 21, 2026              │
│                               │
│                  View →       │
└───────────────────────────────┘
```

---

# 22. Mobile Filters

Don't show five large dropdowns simultaneously.

Use:

```text
🔍 Search

[ Filters ▾ ]
```

Clicking Filters opens:

```text
┌───────────────────────────────┐
│ Filters                    ×  │
├───────────────────────────────┤
│ Crop                          │
│ [ All Crops ▾ ]               │
│                               │
│ Severity                      │
│ [ All Levels ▾ ]              │
│                               │
│ Date                          │
│ [ Last 30 Days ▾ ]            │
│                               │
│ [ Clear ]       [ Apply ]     │
└───────────────────────────────┘
```

---

# 23. Empty State

This is important for a new account.

Don't show:

```text
No data found.
```

Use:

```text
┌──────────────────────────────────────────┐
│                                          │
│                  🌱                      │
│                                          │
│           No Diagnoses Yet               │
│                                          │
│  Your crop analysis history will appear  │
│  here after you scan your first crop.    │
│                                          │
│        [ 📷 Scan Your First Crop ]       │
│                                          │
└──────────────────────────────────────────┘
```

---

# 24. Filtered Empty State

Different from a completely empty account.

Example:

```text
No Tomato diagnoses found.

Try changing your filters.

[ Clear Filters ]
```

Don't show the "Scan Your First Crop" message if the user already has history.

---

# 25. Loading State

Use skeletons rather than a giant spinner.

```text
┌────────────────────────────────────────────┐
│ ████████████                               │
│                                            │
│ ████████    ███████████    ██████          │
│ ████████    ███████████    ██████          │
│                                            │
│ ████████    ███████████    ██████          │
│ ████████    ███████████    ██████          │
└────────────────────────────────────────────┘
```

This makes the page feel faster.

---

# 26. Error State

If history cannot load:

```text
┌──────────────────────────────────────────┐
│                  ⚠                       │
│                                          │
│       Couldn't Load History              │
│                                          │
│ We couldn't retrieve your previous       │
│ crop analyses.                           │
│                                          │
│              [ Try Again ]               │
└──────────────────────────────────────────┘
```

Don't expose:

```text
MongoServerSelectionError
```

or:

```text
HTTP 500
```

---

# 27. Pagination

If you have many predictions, don't load everything at once.

Use:

```text
← Previous     1  2  3  4     Next →
```

For mobile:

```text
[ Load More ]
```

For your MVP, **Load More** is arguably simpler than traditional pagination.

---

# 28. Recommended API

Your backend could expose something conceptually like:

```text
GET /predictions
```

With:

```text
?page=1
&limit=20
&crop=Tomato
&severity=Moderate
&search=blight
```

Response:

```json
{
  "items": [],
  "total": 24,
  "page": 1,
  "limit": 20
}
```

Again, use your actual backend naming conventions rather than forcing these exact endpoint names.

---

# 29. History Data Model

A history item should conceptually contain:

```text
{
    id,
    crop,
    cropConfidence,
    disease,
    diseaseConfidence,
    severity,
    pest,
    pestConfidence,
    imageUrl,
    createdAt
}
```

And optionally:

```text
{
    recommendation,
    location,
    growthStage,
    weather,
    notes
}
```

The first group is directly aligned with the prediction-history information described in your roadmap. 

---

# 30. Important Feature: "Needs Attention"

This can make your History screen much more useful.

Add a filter:

```text
[ Needs Attention ]
```

It could show:

```text
Moderate
Severe
Low confidence / review required
```

Example:

```text
┌──────────────────────────────────────────┐
│ ⚠ Needs Attention                        │
│                                          │
│ 3 previous diagnoses require attention. │
│                                          │
│ Tomato — Early Blight — Moderate        │
│ Potato — Late Blight — Severe           │
│ Cotton — Pest Risk — Moderate           │
└──────────────────────────────────────────┘
```

This turns History into a **farm-management tool**, not just an archive.

---

# 31. Strong Feature: Crop-Specific History

When the farmer clicks a crop:

```text
Tomato
```

you could show:

```text
Tomato History

Aug 26   ⚠ Early Blight   Moderate
Aug 23   ● Early Blight   Mild
Aug 18   ✓ Healthy
Aug 10   ✓ Healthy
```

Then:

```text
Health Trend
```

This lets the user visually understand disease progression.

---

# 32. Disease Progression

This is one of the most valuable additions I'd recommend.

Example:

```text
Tomato — Plot A

Aug 18       Aug 23       Aug 26
  ✓            ●             ⚠
Healthy      Mild        Moderate
```

Then:

> **Condition appears to be worsening.**

Only show this type of conclusion when it is supported by actual historical data and consistent records. Don't infer it from a single scan.

---

# 33. History Detail Drawer — Optional

Instead of immediately navigating to the result page, you could optionally have:

```text
Click row
    ↓
Right-side drawer
```

```text
┌───────────────────────────────────────────┐
│ Diagnosis Preview                     ×   │
├───────────────────────────────────────────┤
│                                           │
│ 🌿 Tomato                                 │
│                                           │
│ ⚠ Early Blight                            │
│ Moderate                                  │
│                                           │
│ Confidence 94%                            │
│                                           │
│ Aug 26, 2026                               │
│                                           │
│ [ View Full Diagnosis ]                   │
└───────────────────────────────────────────┘
```

I would make this a **P2 feature**, not necessary for your first implementation.

---

# 34. Download Report

Each history item can have:

```text
⋮ → Download Report
```

This is useful because a farmer can retrieve an old diagnosis without reopening the entire result page.

---

# 35. Delete History

If you support deletion:

```text
⋮
   Delete
```

Confirmation:

```text
┌──────────────────────────────────────────┐
│ Delete this diagnosis?                   │
│                                          │
│ This record will be permanently removed. │
│                                          │
│ [ Cancel ]       [ Delete ]              │
└──────────────────────────────────────────┘
```

Don't make Delete the primary action.

---

# 36. Search + Filter Layout

Desktop:

```text
┌────────────────────────────────────────────────────────────┐
│ 🔍 Search crop or disease...                               │
│                                                            │
│ [ Crop ▾ ] [ Severity ▾ ] [ Disease ▾ ] [ Date ▾ ]        │
│                                                            │
│                         [ Clear Filters ]                   │
└────────────────────────────────────────────────────────────┘
```

Mobile:

```text
┌──────────────────────────────┐
│ 🔍 Search...                 │
│                              │
│ [ Filters ▾ ]                │
└──────────────────────────────┘
```

---

# 37. Recommended Color Semantics

Use your application's primary brand color for normal UI.

For diagnosis states:

```text
Healthy       → success semantic
Mild          → warning semantic
Moderate      → warning/attention semantic
Severe        → danger semantic
Review        → neutral/info semantic
```

But don't make the entire history card red just because the diagnosis is severe.

Only the relevant badge should communicate severity.

---

# 38. What NOT to Put on History

Avoid turning it into another dashboard.

Don't put:

```text
Weather
Soil analytics
Market prices
AI chatbot
Huge statistics
IoT sensor charts
```

unless they're directly connected to historical diagnoses.

The screen's purpose is:

> **Review previous crop analyses.**

---

# 39. React Component Architecture

I recommend:

```text
src/
├── pages/
│   └── HistoryPage.tsx
│
├── components/
│   └── history/
│       ├── HistoryHeader.tsx
│       ├── HistorySummary.tsx
│       ├── HistoryFilters.tsx
│       ├── HistorySearch.tsx
│       ├── HistoryTable.tsx
│       ├── HistoryRow.tsx
│       ├── HistoryCard.tsx
│       ├── SeverityBadge.tsx
│       ├── HistoryTrend.tsx
│       ├── AttentionSummary.tsx
│       ├── HistoryEmptyState.tsx
│       ├── HistorySkeleton.tsx
│       └── HistoryError.tsx
│
├── api/
│   └── history.ts
│
└── hooks/
    └── useHistory.ts
```

---

# 40. Component Hierarchy

```text
HistoryPage
│
├── HistoryHeader
│
├── HistorySummary
│   ├── TotalAnalyses
│   ├── HealthyCrops
│   ├── IssuesDetected
│   └── NeedsAttention
│
├── HistoryTrend
│
├── HistoryFilters
│   ├── Search
│   ├── CropFilter
│   ├── DiseaseFilter
│   ├── SeverityFilter
│   └── DateFilter
│
├── HistoryTable
│   └── HistoryRow
│
└── Pagination
```

---

# 41. Mobile Component Hierarchy

```text
HistoryPage
│
├── HistoryHeader
├── HistorySummary
├── HistorySearch
├── MobileFilters
│
└── HistoryList
    ├── HistoryCard
    ├── HistoryCard
    └── HistoryCard
```

---

# 42. State Management

You should have explicit states:

```text
loading
success
empty
filteredEmpty
error
```

For filtering:

```text
filters = {
    search: "",
    crop: "all",
    disease: "all",
    severity: "all",
    dateRange: "30d"
}
```

---

# 43. URL Query Parameters

A nice improvement is making filters shareable/bookmarkable:

```text
/history?crop=Tomato&severity=Moderate
```

Then refreshing the page doesn't lose the selected filters.

This is not essential for V1, but it is good frontend architecture.

---

# 44. Final Recommended Desktop Screen

```text
┌──────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                               🔔       👤 Manthan   │
├───────────────┬──────────────────────────────────────────────────────┤
│               │                                                      │
│ 🏠 Dashboard  │  Diagnosis History                                 │
│               │  Track and review your previous crop analyses      │
│ 📷 Scan Crop  │                                                      │
│               │  ┌────────────┐ ┌────────────┐ ┌────────────┐      │
│ 📋 History ●  │  │24          │ │16          │ │8           │      │
│               │  │Total       │ │Healthy     │ │Issues      │      │
│ 🌱 My Farm    │  └────────────┘ └────────────┘ └────────────┘      │
│               │                                                      │
│ 🔔 Alerts     │  ┌───────────────────────────────────────────────┐ │
│               │  │ Crop Health Trend                             │ │
│ ⚙ Settings    │  │                                               │ │
│               │  │        ●                                      │ │
│               │  │     ●     ●                                   │ │
│               │  │  ●                                             │ │
│               │  └───────────────────────────────────────────────┘ │
│               │                                                      │
│               │  🔍 Search crop or disease...                       │
│               │                                                      │
│               │  [Crop ▾] [Disease ▾] [Severity ▾] [Date ▾]       │
│               │                                                      │
│               │  Recent Diagnoses                                   │
│               │                                                      │
│               │  ┌────┬────────┬──────────────┬─────────┬───────┐ │
│               │  │Img │ Crop   │ Diagnosis    │Severity │ Date  │ │
│               │  ├────┼────────┼──────────────┼─────────┼───────┤ │
│               │  │ 🌿 │ Tomato │ Early Blight │Moderate │ Aug26 │ │
│               │  │ 🌿 │ Cotton │ Healthy      │Healthy  │ Aug24 │ │
│               │  │ 🌿 │ Potato │ Late Blight  │Severe   │ Aug21 │ │
│               │  └────┴────────┴──────────────┴─────────┴───────┘ │
│               │                                                      │
│               │                    ← 1  2  3 →                     │
│               │                                                      │
└───────────────┴──────────────────────────────────────────────────────┘
```

---

# 45. My Recommended V1 vs Advanced Version

### V1 — Implement Now

```text
✓ History header
✓ Total/Healthy/Issues summary
✓ Search
✓ Crop filter
✓ Severity filter
✓ Date filter
✓ Diagnosis table
✓ Severity badges
✓ Confidence
✓ Date/time
✓ View result
✓ Pagination / Load More
✓ Loading state
✓ Empty state
✓ Error state
```

### V2 — Add After Core Frontend Works

```text
⭐ Crop-specific health trend
⭐ Needs Attention filter
⭐ Disease progression timeline
⭐ Download PDF report
⭐ Farmer notes
⭐ Advanced disease filtering
⭐ History detail drawer
```

### V3 — Differentiating Feature

```text
🔥 "Is my crop getting better or worse?"

Select:
Tomato / Plot A

        Healthy
           ↓
          Mild
           ↓
       Moderate
           ↓
        Severe

AI summarizes the historical trend and
shows the farmer what changed between scans.
```

That last feature is where I would differentiate your History screen from a generic CRUD-style "prediction history" page. It turns the screen from **an archive of AI predictions into a crop-health monitoring timeline**, which fits your Smart Farming concept much better.


# Smart Farming — Farms / Plots Screen UI/UX Specification

For your project, I would make **Farms / Plots** a proper farm-management screen rather than just a CRUD page.

The core concept should be:

> **Farm → Plot → Crop → Diagnoses → Health History**

This is important because your diagnosis system becomes much more useful when a prediction is associated with a **specific physical plot** instead of existing as an isolated image scan.

---

# 1. Route

```text
/farms
```

Optional detailed route:

```text
/farms/:farmId
```

and plot detail:

```text
/farms/:farmId/plots/:plotId
```

Recommended navigation:

```text
Dashboard
   ↓
Farms & Plots
   ↓
Farm
   ↓
Plot
   ↓
Crop Health
   ↓
Diagnosis History
```

---

# 2. Main Purpose

The screen should allow the farmer to:

* Create a farm
* Add multiple plots
* View plot locations
* Assign crops to plots
* See current crop status
* See the latest diagnosis
* See the number of previous scans
* Open a specific plot
* Edit farm/plot information
* Manage multiple farms

---

# 3. Important Concept

Don't structure the UI as:

```text
Farm
 ├── Image
 ├── Disease
 └── Prediction
```

Instead:

```text
                    FARM
                     │
        ┌────────────┼────────────┐
        │            │            │
      Plot A       Plot B       Plot C
        │            │            │
     Tomato       Cotton       Potato
        │            │            │
   Diagnoses     Diagnoses     Diagnoses
        │            │            │
     History       History      History
```

This gives your application a proper **farm-management data model**.

---

# 4. Desktop Layout

```text
┌─────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                         🔔        👤 Manthan ▾     │
├───────────────┬─────────────────────────────────────────────────────┤
│               │                                                     │
│ 🏠 Dashboard  │  Farms & Plots                         [+ Add Farm] │
│               │                                                     │
│ 📷 Scan Crop  │  Manage your farms, plots and crops                │
│               │                                                     │
│ 📋 History    │  ┌───────────────────────────────────────────────┐ │
│               │  │ 🌾 My Farms                                   │ │
│ 🌾 Farms ●   │  │                                               │ │
│               │  │ 2 Farms • 6 Plots                            │ │
│ 🔔 Alerts     │  └───────────────────────────────────────────────┘ │
│               │                                                     │
│ ⚙ Settings    │  [ All Farms ▾ ] [ Crop ▾ ] [ Status ▾ ]          │
│               │                                                     │
│               │  ┌──────────────────────┐ ┌──────────────────────┐│
│               │  │ 🌾 Main Farm         │ │ 🌾 Village Farm      ││
│               │  │ Anand, Gujarat       │ │ Kheda, Gujarat       ││
│               │  │                      │ │                      ││
│               │  │ 4 Plots              │ │ 2 Plots              ││
│               │  │ 3 Healthy            │ │ 1 Needs Attention    ││
│               │  │                      │ │                      ││
│               │  │ [ View Farm → ]      │ │ [ View Farm → ]      ││
│               └──────────────────────┘ └──────────────────────┘│
│               │                                                     │
│               │  Recent Plot Status                                │
│               │                                                     │
│               │  ┌───────────────────────────────────────────────┐ │
│               │  │ Plot │ Crop   │ Status    │ Last Scan │ ...  │ │
│               │  │ A-01 │ Tomato │ Moderate  │ Aug 26    │      │ │
│               │  │ A-02 │ Cotton │ Healthy   │ Aug 24    │      │ │
│               │  │ B-01 │ Potato │ Severe    │ Aug 21    │      │ │
│               │  └───────────────────────────────────────────────┘ │
└───────────────┴─────────────────────────────────────────────────────┘
```

---

# 5. Page Header

Use:

> **Farms & Plots**

Subtitle:

> Manage your farms, plots and crop health.

Primary button:

```text
+ Add Farm
```

Don't use:

```text
Create New Farm Entity
```

Keep the terminology farmer-friendly.

---

# 6. Farm Summary

At the top:

```text
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Farms        │ │ Plots        │ │ Healthy      │ │ Attention    │
│              │ │              │ │              │ │              │
│ 2            │ │ 6            │ │ 4            │ │ 2            │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

Recommended terminology:

```text
Farms
Plots
Healthy
Needs Attention
```

This gives the user an immediate understanding of the state of their farm.

---

# 7. Farm Card

Each farm should have a card.

```text
┌──────────────────────────────────────────────┐
│ 🌾 Main Farm                         ⋮       │
│                                              │
│ 📍 Anand, Gujarat                            │
│                                              │
│ 4 Plots                                      │
│                                              │
│ ┌──────────┐ ┌──────────┐                   │
│ │ 3        │ │ 1        │                   │
│ │ Healthy  │ │ Attention│                   │
│ └──────────┘ └──────────┘                   │
│                                              │
│ Last activity: Today                        │
│                                              │
│             [ View Farm → ]                 │
└──────────────────────────────────────────────┘
```

---

# 8. Farm Card Menu

The `⋮` menu:

```text
⋮
├── View Farm
├── Edit Farm
├── Add Plot
└── Delete Farm
```

For Delete:

> Deleting a farm may also remove its associated plot records.

Show a confirmation dialog before deletion.

---

# 9. Add Farm

When clicking:

```text
+ Add Farm
```

Open a modal or dedicated page.

I recommend a modal for the initial version.

```text
┌────────────────────────────────────────────┐
│ Add New Farm                          ×    │
├────────────────────────────────────────────┤
│                                            │
│ Farm Name                                  │
│ [ Main Farm                         ]      │
│                                            │
│ Location                                   │
│ [ Search location...               ]      │
│                                            │
│ Village / Area                             │
│ [                              ]            │
│                                            │
│ Farm Description                           │
│ [                              ]            │
│                                            │
│              [ Cancel ] [ Create Farm ]    │
└────────────────────────────────────────────┘
```

---

# 10. Farm Location

Location is particularly valuable for your project because later features can use it for:

* Weather
* Local recommendations
* Farm context
* Location-aware alerts

Use:

```text
📍 Location
[ Search location ]
```

If you later implement maps:

```text
┌──────────────────────────────────────┐
│                                      │
│              📍                      │
│                                      │
│        Map / Farm Location           │
│                                      │
└──────────────────────────────────────┘
```

Do not require exact GPS coordinates in your first version if the farmer only needs to provide a general location.

---

# 11. Farm Detail Screen

When the farmer clicks:

```text
View Farm →
```

navigate to:

```text
/farms/:farmId
```

Example:

```text
← Farms

Main Farm
📍 Anand, Gujarat

[ + Add Plot ]

4 Plots
```

Then show the farm's plots.

---

# 12. Farm Detail Layout

```text
┌──────────────────────────────────────────────────────────────────┐
│ ← Farms                                                          │
│                                                                  │
│ 🌾 Main Farm                                    [ + Add Plot ]   │
│ 📍 Anand, Gujarat                                                │
│                                                                  │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│ │ 4        │ │ 3        │ │ 1        │ │ 18       │             │
│ │ Plots    │ │ Healthy  │ │ Attention│ │ Scans   │             │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘             │
│                                                                  │
│ Plots                                                            │
│                                                                  │
│ ┌──────────────────────┐ ┌──────────────────────┐                │
│ │ Plot A-01             │ │ Plot A-02            │               │
│ │ Tomato                │ │ Cotton               │               │
│ │                       │ │                      │               │
│ │ ✓ Healthy             │ │ ⚠ Moderate           │               │
│ │ Last scan: Aug 26     │ │ Last scan: Aug 24    │               │
│ │                       │ │                      │               │
│ │ [ View Plot → ]       │ │ [ View Plot → ]      │               │
│ └──────────────────────┘ └──────────────────────┘                │
└──────────────────────────────────────────────────────────────────┘
```

---

# 13. Plot Card

The plot is the most important entity inside the farm.

Example:

```text
┌──────────────────────────────────────┐
│ Plot A-01                         ⋮  │
│                                      │
│ 🍅 Tomato                            │
│                                      │
│ ✓ Healthy                            │
│                                      │
│ Last diagnosis                       │
│ Aug 26, 2026                         │
│                                      │
│ 6 Analyses                           │
│                                      │
│ [ View Plot → ]                      │
└──────────────────────────────────────┘
```

---

# 14. Plot Status

Use:

```text
✓ Healthy
● Mild
● Moderate
⚠ Severe
⏳ Review Required
— Not Scanned
```

The last one is important.

A new plot might not have any diagnosis yet:

```text
Plot B-03

🍅 Tomato

— Not Scanned

[ Scan This Plot ]
```

---

# 15. Add Plot

Click:

```text
+ Add Plot
```

Modal:

```text
┌────────────────────────────────────────────┐
│ Add Plot                              ×    │
├────────────────────────────────────────────┤
│                                            │
│ Plot Name / Number                         │
│ [ Plot A-03                       ]       │
│                                            │
│ Crop                                       │
│ [ Select Crop ▾ ]                           │
│                                            │
│ Area                                       │
│ [           ] hectares                     │
│                                            │
│ Location                                   │
│ [ Use Farm Location ]                      │
│                                            │
│ Crop Stage                                 │
│ [ Select Stage ▾ ]                         │
│                                            │
│              [ Cancel ] [ Add Plot ]       │
└────────────────────────────────────────────┘
```

---

# 16. Crop Assignment

This is important.

A plot should be associated with the current crop.

Example:

```text
Plot A-01

Crop
🍅 Tomato
```

When a crop changes:

```text
Plot A-01

Previous crop:
Tomato

Current crop:
Cotton
```

This becomes useful for historical records.

However, don't automatically overwrite old diagnoses. Historical diagnoses should retain the crop associated with the original analysis.

---

# 17. Plot Area

Optional field:

```text
Area
2.5 hectares
```

or:

```text
Area
6.2 acres
```

For India, supporting both:

```text
Hectares
Acres
```

is useful.

You can let the user select:

```text
[ Hectares ▾ ]
```

---

# 18. Plot Detail Screen

Route:

```text
/farms/:farmId/plots/:plotId
```

This should be one of your strongest screens after Diagnosis Result.

Layout:

```text
← Main Farm

Plot A-01
🍅 Tomato
📍 Main Farm

Status
⚠ Moderate

[ Scan This Plot ]

────────────────────────────

Crop Health Overview

Current Status
Moderate

Last Scan
Aug 26, 2026

Total Analyses
6

────────────────────────────

Health History

Aug 26  ⚠ Moderate
Aug 23  ● Mild
Aug 18  ✓ Healthy

────────────────────────────

Latest Diagnosis

Early Blight
94% confidence

[ View Diagnosis ]

────────────────────────────

Recommendations

...

[ View Full Recommendations ]
```

---

# 19. Plot Health Timeline

This is where the Farms/Plots feature connects directly with your History screen.

Example:

```text
Plot A-01 — Tomato

Aug 18
   │
   ✓ Healthy
   │
Aug 23
   │
   ● Mild
   │
Aug 26
   │
   ⚠ Moderate
```

This gives a clear progression.

---

# 20. "Scan This Plot"

This should be one of the most useful buttons.

```text
[ 📷 Scan This Plot ]
```

Clicking it should open your existing scan/upload screen with the plot context already selected.

Instead of:

```text
Upload
→ Select Crop
→ Select Farm
→ Select Plot
```

the user gets:

```text
Plot A-01
     ↓
Scan This Plot
     ↓
Upload Image
     ↓
Diagnosis
```

This is significantly better UX.

---

# 21. Scan Context

When launching the scan from a plot:

```text
Scan Crop

Farm
Main Farm

Plot
A-01

Crop
Tomato
```

These should ideally be pre-filled.

---

# 22. Map View

A map can be a strong enhancement, but I would not make it mandatory for V1.

Desktop:

```text
┌──────────────────────────────────────────────────────┐
│ Farm Map                                             │
│                                                      │
│        ┌───────────────┐                             │
│        │ Plot A-01     │                             │
│        │ 🍅 Moderate   │                             │
│        └───────────────┘                             │
│                                                      │
│   ┌─────────────┐                                    │
│   │ Plot A-02   │                                    │
│   │ ✓ Healthy   │                                    │
│   └─────────────┘                                    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

Each plot can be represented by a marker.

---

# 23. Plot Health Map

This could become a very impressive hackathon feature.

Concept:

```text
                 FARM
                  │
       ┌──────────┼──────────┐
       │          │          │
    Plot A      Plot B      Plot C
      🟢          🟡          🔴
    Healthy    Moderate     Severe
```

The map visually communicates:

> **Where is the problem in my farm?**

This is much more meaningful than simply showing a list of predictions.

---

# 24. Map Legend

If implemented:

```text
● Healthy
● Mild
● Moderate
● Severe
● Not Scanned
```

Again, combine color with text/status so the map isn't dependent solely on color.

---

# 25. Farm Health Summary

Inside a farm detail screen:

```text
Farm Health

Healthy        3
Mild           0
Moderate       1
Severe         0
Not Scanned    0
```

You can also display:

> **3 of 4 plots are currently healthy.**

This is a very farmer-friendly summary.

---

# 26. Farm-Level Alert

If one plot has severe disease:

```text
┌─────────────────────────────────────────────┐
│ ⚠ Attention Required                       │
│                                             │
│ Plot A-03 has a severe diagnosis.           │
│                                             │
│ Review the latest diagnosis and recommended │
│ actions.                                    │
│                                             │
│ [ View Plot ]                               │
└─────────────────────────────────────────────┘
```

This connects your plot management with your notification/alert system.

---

# 27. Crop Rotation / Previous Crops

This is a good **advanced** feature.

Inside plot:

```text
Crop History

2026
Tomato

2025
Cotton

2024
Groundnut
```

This becomes useful for future recommendation logic.

Don't implement this as a complicated agricultural model initially. Just allow the farmer to record previous crops.

---

# 28. Plot Metadata

A plot detail section could contain:

```text
Plot Information

Plot ID
A-01

Area
2.5 hectares

Current Crop
Tomato

Growth Stage
Flowering

Created
Aug 1, 2026

Last Scan
Aug 26, 2026
```

Use an expandable card:

```text
▾ Plot Information
```

to avoid clutter.

---

# 29. Farm vs Plot Responsibility

Keep the distinction very clear.

### Farm

Represents:

```text
Physical farm/property
```

Example:

```text
Main Farm
📍 Anand
```

### Plot

Represents:

```text
A specific cultivated area inside the farm
```

Example:

```text
Plot A-01
🍅 Tomato
2.5 hectares
```

---

# 30. Recommended Data Relationship

Your frontend should conceptually follow:

```text
User
 │
 ├── Farm 1
 │    │
 │    ├── Plot 1
 │    │     ├── Crop
 │    │     └── Diagnoses
 │    │
 │    ├── Plot 2
 │    │     ├── Crop
 │    │     └── Diagnoses
 │    │
 │    └── Plot 3
 │
 └── Farm 2
      │
      ├── Plot 4
      └── Plot 5
```

This will make your backend/frontend integration much cleaner.

---

# 31. Recommended Plot Object

Conceptually:

```javascript
{
  id,
  farmId,
  name,
  crop,
  area,
  areaUnit,
  location,
  growthStage,
  status,
  lastDiagnosisId,
  lastScannedAt,
  diagnosisCount
}
```

And Farm:

```javascript
{
  id,
  name,
  location,
  description,
  plotCount,
  createdAt
}
```

Use your actual backend schema when implementing.

---

# 32. Navigation

Sidebar:

```text
🏠 Dashboard

📷 Scan Crop

📋 History

🌾 Farms & Plots

🔔 Alerts

⚙ Settings
```

I recommend calling the sidebar item:

> **Farms & Plots**

rather than simply:

> Farms

because the plot concept is important to your product.

---

# 33. Empty State — No Farms

For a new user:

```text
┌─────────────────────────────────────────────┐
│                                             │
│                 🌾                          │
│                                             │
│          Set Up Your First Farm             │
│                                             │
│ Add your farm and plots to organize crop    │
│ health and diagnosis history.               │
│                                             │
│              [ + Add Farm ]                 │
│                                             │
└─────────────────────────────────────────────┘
```

---

# 34. Empty State — Farm Has No Plots

```text
┌─────────────────────────────────────────────┐
│                                             │
│              🌱                             │
│                                             │
│           No Plots Yet                      │
│                                             │
│ Add your first plot to start tracking       │
│ crop health.                                │
│                                             │
│              [ + Add Plot ]                 │
│                                             │
└─────────────────────────────────────────────┘
```

---

# 35. Loading State

Use skeletons:

```text
┌───────────────────────┐
│ █████████████         │
│ ███████               │
│                       │
│ ██████   ██████       │
│                       │
│ █████████████████     │
└───────────────────────┘
```

Don't show an empty state while data is still loading.

---

# 36. Delete Farm Confirmation

```text
┌────────────────────────────────────────────┐
│ Delete Main Farm?                      ×   │
├────────────────────────────────────────────┤
│                                            │
│ This will remove the farm from your        │
│ farm list.                                 │
│                                            │
│ Its associated plots and records may also  │
│ be affected.                               │
│                                            │
│ [ Cancel ]          [ Delete Farm ]        │
└────────────────────────────────────────────┘
```

The exact deletion behavior must match your backend's data-retention rules.

---

# 37. Mobile Farms Screen

```text
┌───────────────────────────────┐
│ 🌱 Farms & Plots          +   │
├───────────────────────────────┤
│                               │
│ 2 Farms      6 Plots          │
│ 4 Healthy    2 Attention      │
│                               │
├───────────────────────────────┤
│                               │
│ 🌾 Main Farm              ⋮   │
│ 📍 Anand, Gujarat             │
│                               │
│ 4 Plots                       │
│                               │
│ ✓ 3 Healthy                   │
│ ⚠ 1 Attention                 │
│                               │
│ [ View Farm → ]               │
├───────────────────────────────┤
│                               │
│ 🌾 Village Farm           ⋮   │
│ 📍 Kheda, Gujarat             │
│                               │
│ 2 Plots                       │
│                               │
│ ✓ 1 Healthy                   │
│ ⚠ 1 Attention                 │
│                               │
│ [ View Farm → ]               │
└───────────────────────────────┘
```

---

# 38. Mobile Farm Detail

```text
┌───────────────────────────────┐
│ ← Farms              ⋮        │
├───────────────────────────────┤
│ 🌾 Main Farm                  │
│ 📍 Anand, Gujarat             │
│                               │
│ [ + Add Plot ]                │
├───────────────────────────────┤
│                               │
│ Farm Overview                 │
│                               │
│ 4 Plots   3 Healthy   1 Alert │
│                               │
├───────────────────────────────┤
│ Plots                         │
│                               │
│ ┌───────────────────────────┐ │
│ │ Plot A-01                 │ │
│ │ 🍅 Tomato                 │ │
│ │                           │ │
│ │ ⚠ Moderate                │ │
│ │ Last scan: Aug 26         │ │
│ │                           │ │
│ │ [ View Plot → ]           │ │
│ └───────────────────────────┘ │
│                               │
│ ┌───────────────────────────┐ │
│ │ Plot A-02                 │ │
│ │ 🌿 Cotton                 │ │
│ │                           │ │
│ │ ✓ Healthy                 │ │
│ │ Last scan: Aug 24         │ │
│ │                           │ │
│ │ [ View Plot → ]           │ │
│ └───────────────────────────┘ │
└───────────────────────────────┘
```

---

# 39. Recommended Plot Detail Mobile

```text
┌───────────────────────────────┐
│ ← Main Farm              ⋮    │
├───────────────────────────────┤
│                               │
│ Plot A-01                     │
│ 🍅 Tomato                     │
│                               │
│ ⚠ Moderate                    │
│                               │
│ [ 📷 Scan This Plot ]         │
├───────────────────────────────┤
│                               │
│ Crop Health                   │
│                               │
│ Current       Moderate        │
│ Last Scan     Aug 26          │
│ Analyses      6               │
├───────────────────────────────┤
│                               │
│ Health History                │
│                               │
│ Aug 26  ⚠ Moderate            │
│   │                           │
│ Aug 23  ● Mild                │
│   │                           │
│ Aug 18  ✓ Healthy             │
├───────────────────────────────┤
│                               │
│ Latest Diagnosis              │
│ Early Blight                  │
│ 94% confidence                │
│                               │
│ [ View Diagnosis ]            │
├───────────────────────────────┤
│                               │
│ Plot Information          ▾   │
└───────────────────────────────┘
```

---

# 40. The Most Important UX Connection

Your **Farms/Plots → Scan → Diagnosis → History** flow should be tightly connected.

The ideal flow is:

```text
             🌾 Main Farm
                  │
             🍅 Plot A-01
                  │
          [ Scan This Plot ]
                  │
                  ▼
             Upload Image
                  │
                  ▼
             AI Processing
                  │
                  ▼
           Diagnosis Result
                  │
                  ├──────→ Saved to History
                  │
                  ▼
          Plot Health Updated
                  │
                  ▼
          Farm Health Updated
```

So after a diagnosis:

```text
Plot A-01
Before:
✓ Healthy

After:
⚠ Moderate
```

and automatically:

```text
Main Farm
Healthy: 3
Attention: 1
```

This is the kind of integration that will make your frontend feel like **one coherent Smart Farming platform**, rather than a collection of independent pages.

---

# 41. Recommended V1

For your current project, I would implement these first:

### Farms

```text
✓ Farms list
✓ Add farm
✓ Edit farm
✓ Delete farm
✓ Farm location
✓ Farm summary
✓ View farm
```

### Plots

```text
✓ Plot list
✓ Add plot
✓ Edit plot
✓ Delete plot
✓ Crop assignment
✓ Plot area
✓ Plot status
✓ Last diagnosis
✓ Diagnosis count
✓ View plot
```

### Integration

```text
✓ Scan This Plot
✓ Plot → Diagnosis
✓ Diagnosis → Plot history
✓ Plot → History
✓ Farm health summary
```

---

# 42. Advanced Version

After the basic system works:

```text
⭐ Farm map
⭐ Plot boundaries
⭐ Plot health map
⭐ Crop history
⭐ Crop rotation records
⭐ Plot health timeline
⭐ Needs Attention plots
⭐ Farm-level alerts
⭐ Weather per farm
⭐ Soil information per plot
⭐ Plot-specific recommendations
```

The most valuable advanced feature is:

> **Farm Health Map**

where each plot visually shows:

```text
🟢 Healthy
🟡 Mild
🟠 Moderate
🔴 Severe
⚪ Not Scanned
```

Then a farmer can immediately understand **where the problems are**, rather than reading through individual diagnoses.

---

# 43. Final Screen Architecture

Your frontend navigation can now become:

```text
                         SMART FARMING
                              │
       ┌──────────────────────┼────────────────────────┐
       │                      │                        │
   DASHBOARD              FARMS & PLOTS             HISTORY
       │                      │                        │
       │                 ┌────┴────┐                   │
       │                 │         │                   │
       │               FARM 1    FARM 2                │
       │                 │                              │
       │             ┌───┼───┐                          │
       │             │   │   │                          │
       │           PLOT PLOT PLOT                       │
       │             │   │   │                          │
       └─────────────┼───┼───┼──────────────────────────┘
                     │   │   │
                     ▼   ▼   ▼
                  SCAN CROP
                     │
                     ▼
                  PROCESSING
                     │
                     ▼
              DIAGNOSIS RESULT
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Disease      Pest      Severity
          │
          ▼
    AI Recommendation
          │
          ▼
      Plot History
```

**This is the architecture I would use for your Smart Farming frontend.** The key distinction is that **History records what happened, while Farms/Plots establishes where it happened**. Once those two are connected to your existing diagnosis pipeline, your application becomes much closer to a real farm-management product rather than simply an AI crop-disease classifier.


# Smart Farming — Alerts Screen UI/UX Specification

The **Alerts Screen** should not be just a notification inbox.

For your Smart Farming project, its purpose should be:

> **Tell the farmer what needs attention, why it matters, where the problem is, and what action they should take.**

This makes Alerts directly connected to your **Farms → Plots → Scan → Diagnosis → Recommendation** workflow.

---

# 1. Route

```text
/alerts
```

Individual alert:

```text
/alerts/:alertId
```

The notification bell should also link here:

```text
🔔 → /alerts
```

---

# 2. What Should Generate an Alert?

Your alert system can receive events from different parts of your application.

### Crop/Disease Alerts

```text
⚠ Disease detected
⚠ Disease severity increased
⚠ Severe crop condition
```

### Pest Alerts

```text
🐛 Pest detected
🐛 High pest risk
```

### Crop Health Alerts

```text
🌱 Crop condition worsening
🌱 Repeated disease detection
🌱 Plot hasn't been scanned recently
```

### Recommendation Alerts

```text
💡 Recommended action available
💡 Follow-up scan recommended
```

### System Alerts

```text
ℹ Scan completed
ℹ Diagnosis ready
⚠ Scan failed
```

For your MVP, prioritize **actionable agricultural alerts** over generic system notifications.

---

# 3. Main Desktop Layout

```text
┌─────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                         🔔        👤 Manthan ▾     │
├───────────────┬─────────────────────────────────────────────────────┤
│               │                                                     │
│ 🏠 Dashboard  │  Alerts                                             │
│               │  Stay informed about important crop conditions     │
│ 📷 Scan Crop  │                                                     │
│               │  ┌────────────┐ ┌────────────┐ ┌────────────┐      │
│ 📋 History    │  │ 5          │ │ 2          │ │ 3          │      │
│               │  │ Total      │ │ Critical   │ │ Unread     │      │
│ 🌾 Farms      │  └────────────┘ └────────────┘ └────────────┘      │
│               │                                                     │
│ 🔔 Alerts ●  │  [All] [Unread] [Critical] [Disease] [Pest]       │
│               │                                                     │
│ ⚙ Settings    │  Today                                             │
│               │                                                     │
│               │  ┌───────────────────────────────────────────────┐ │
│               │  │ ⚠  Disease severity increased                │ │
│               │  │    Tomato • Plot A-01                        │ │
│               │  │    Early Blight changed from Mild → Moderate │ │
│               │  │    2 hours ago                    [View →]   │ │
│               │  ├───────────────────────────────────────────────┤ │
│               │  │ 🐛 Pest detected                             │ │
│               │  │    Cotton • Plot A-02                        │ │
│               │  │    Aphid detected with 92% confidence       │ │
│               │  │    5 hours ago                    [View →]   │ │
│               │  └───────────────────────────────────────────────┘ │
│               │                                                     │
│               │  Yesterday                                         │
│               │                                                     │
│               │  ┌───────────────────────────────────────────────┐ │
│               │  │ ✓ Scan completed                              │ │
│               │  │    Potato • Plot B-01                         │ │
│               │  │    Healthy                                    │ │
│               │  └───────────────────────────────────────────────┘ │
└───────────────┴─────────────────────────────────────────────────────┘
```

---

# 4. Page Header

Use:

> **Alerts**

Subtitle:

> **Stay informed about important crop conditions and recommended actions.**

On the right:

```text
[ Mark all as read ]
```

Optional:

```text
[ Alert Settings ]
```

---

# 5. Summary Cards

At the top:

```text
┌────────────────┐
│ Total Alerts   │
│                │
│ 12             │
└────────────────┘

┌────────────────┐
│ Critical       │
│                │
│ 2              │
└────────────────┘

┌────────────────┐
│ Unread         │
│                │
│ 3              │
└────────────────┘

┌────────────────┐
│ Needs Action   │
│                │
│ 4              │
└────────────────┘
```

I recommend **Needs Action** instead of simply "Warnings" because it tells the farmer what matters.

---

# 6. Alert Priority

Use four levels.

### Critical

```text
⚠ Critical
```

Examples:

* Severe disease
* Rapid deterioration
* Severe pest issue

### High

```text
⚠ High
```

Examples:

* Moderate → Severe
* Significant pest detection

### Medium

```text
● Medium
```

Examples:

* Healthy → Mild
* Follow-up scan recommended

### Info

```text
ℹ Information
```

Examples:

* Scan completed
* Recommendation updated

---

# 7. Alert Card

Each alert should answer four questions:

```text
WHAT happened?
WHERE did it happen?
WHEN did it happen?
WHAT should I do?
```

Example:

```text
┌────────────────────────────────────────────────────────────┐
│ ⚠  Disease severity increased                    HIGH     │
│                                                            │
│ Tomato • Plot A-01                                         │
│                                                            │
│ Early Blight severity increased from Mild to Moderate.     │
│                                                            │
│ 2 hours ago                                                │
│                                                            │
│ [ View Diagnosis ]       [ Mark as Read ]                 │
└────────────────────────────────────────────────────────────┘
```

---

# 8. Alert Types

Use a recognizable icon.

| Type           | Icon | Example                  |
| -------------- | ---- | ------------------------ |
| Disease        | 🦠   | Early Blight detected    |
| Pest           | 🐛   | Aphid detected           |
| Severity       | ⚠    | Severity increased       |
| Crop Health    | 🌱   | Crop condition worsening |
| Recommendation | 💡   | Action recommended       |
| Scan           | 📷   | Scan completed           |
| System         | ℹ    | Processing failed        |

The icon should supplement the text, not replace it.

---

# 9. Disease Alert

Example:

```text
┌──────────────────────────────────────────────────────────┐
│ 🦠 Disease Detected                             HIGH     │
│                                                          │
│ Tomato • Plot A-01                                       │
│                                                          │
│ Early Blight detected                                    │
│ Confidence: 94%                                         │
│ Severity: Moderate                                       │
│                                                          │
│ Detected today at 10:42 AM                               │
│                                                          │
│ [ View Diagnosis ]                                       │
└──────────────────────────────────────────────────────────┘
```

---

# 10. Severity Increase Alert

This is one of the **most valuable alerts** for your project.

```text
┌──────────────────────────────────────────────────────────┐
│ ⚠ Crop condition worsening                     CRITICAL  │
│                                                          │
│ 🍅 Tomato • Plot A-01                                    │
│                                                          │
│ Early Blight                                             │
│                                                          │
│ Previous:  Mild                                          │
│ Current:   Severe                                        │
│                                                          │
│ Your latest scan indicates increased disease severity.   │
│                                                          │
│ [ View Plot ]        [ View Recommendation ]             │
└──────────────────────────────────────────────────────────┘
```

This alert should only be generated when your application has enough historical information to establish that severity actually increased.

---

# 11. Pest Alert

```text
┌──────────────────────────────────────────────────────────┐
│ 🐛 Pest Detected                               HIGH       │
│                                                          │
│ Cotton • Plot A-02                                       │
│                                                          │
│ Aphid detected                                           │
│ Confidence: 92%                                         │
│                                                          │
│ Recommended: Review the pest-control recommendation.    │
│                                                          │
│ [ View Diagnosis ]                                       │
└──────────────────────────────────────────────────────────┘
```

---

# 12. Recommendation Alert

```text
┌──────────────────────────────────────────────────────────┐
│ 💡 Recommended Action                         MEDIUM     │
│                                                          │
│ Tomato • Plot A-01                                       │
│                                                          │
│ A new recommendation is available for your latest       │
│ diagnosis.                                               │
│                                                          │
│ [ View Recommendation ]                                  │
└──────────────────────────────────────────────────────────┘
```

---

# 13. Follow-Up Scan Alert

This is a particularly useful feature.

Example:

```text
┌──────────────────────────────────────────────────────────┐
│ 📷 Follow-up Scan Recommended                  MEDIUM     │
│                                                          │
│ Tomato • Plot A-01                                       │
│                                                          │
│ Your previous diagnosis showed moderate severity.        │
│ Consider scanning this plot again to monitor changes.    │
│                                                          │
│ [ Scan This Plot ]                                       │
└──────────────────────────────────────────────────────────┘
```

This directly connects:

```text
Alert
 ↓
Scan
 ↓
Diagnosis
 ↓
History
```

---

# 14. Alert Filters

At the top:

```text
[ All ] [ Unread ] [ Critical ] [ Disease ] [ Pest ]
```

Additional filters:

```text
[ Farm ▾ ]
[ Plot ▾ ]
[ Date ▾ ]
```

Desktop:

```text
┌──────────────────────────────────────────────────────────┐
│ [ All ] [ Unread ] [ Critical ] [ Disease ] [ Pest ]     │
│                                                          │
│ Farm: [ All Farms ▾ ]    Plot: [ All Plots ▾ ]           │
└──────────────────────────────────────────────────────────┘
```

---

# 15. Search

Add:

```text
🔍 Search alerts...
```

Search should support:

```text
Tomato
Cotton
Early Blight
Aphid
Plot A-01
```

---

# 16. Group Alerts by Date

Instead of displaying a flat list:

```text
Today
Yesterday
Aug 23
Aug 22
```

Example:

```text
TODAY

⚠ Disease severity increased
🐛 Pest detected

YESTERDAY

💡 Recommendation available
📷 Follow-up scan recommended

AUGUST 23

✓ Scan completed
```

This makes the screen easier to scan.

---

# 17. Unread State

Unread alerts should be visually distinct.

Example:

```text
┌──────────────────────────────────────────────────────┐
│ ● ⚠ Disease severity increased                       │
│                                                      │
│ Tomato • Plot A-01                                   │
│ 2 hours ago                                           │
└──────────────────────────────────────────────────────┘
```

Read:

```text
┌──────────────────────────────────────────────────────┐
│   ⚠ Disease severity increased                       │
│                                                      │
│ Tomato • Plot A-01                                   │
│ 2 hours ago                                           │
└──────────────────────────────────────────────────────┘
```

Use a small dot, weight, or subtle background—not only color.

---

# 18. Mark as Read

Each alert can have:

```text
Mark as read
```

or a menu:

```text
⋮
├── Mark as read
├── View diagnosis
└── Delete
```

At the top:

```text
[ Mark all as read ]
```

---

# 19. Alert Detail

When the user clicks an alert:

```text
/alerts/:alertId
```

show a detailed screen.

```text
┌─────────────────────────────────────────────────────────────┐
│ ← Alerts                                                     │
│                                                             │
│ ⚠ Crop Condition Worsening                                  │
│                                                             │
│ Tomato • Plot A-01                                          │
│ Main Farm • Anand, Gujarat                                  │
│                                                             │
│ ──────────────────────────────────────────────────────────  │
│                                                             │
│ What happened?                                              │
│                                                             │
│ Early Blight was detected in the latest crop scan.          │
│                                                             │
│ Previous Severity       Mild                                │
│ Current Severity        Moderate                            │
│ Confidence              94%                                 │
│                                                             │
│ Detected                 Aug 26, 2026 • 10:42 AM            │
│                                                             │
│ ──────────────────────────────────────────────────────────  │
│                                                             │
│ Recommended Action                                          │
│                                                             │
│ Review the diagnosis and follow the recommended treatment   │
│ guidance.                                                   │
│                                                             │
│ [ View Full Diagnosis ]   [ View Plot ]                     │
└─────────────────────────────────────────────────────────────┘
```

---

# 20. Alert → Diagnosis

If the alert was generated from a diagnosis:

```text
[ View Full Diagnosis ]
```

should navigate to:

```text
/result/:predictionId
```

Do **not** run the model again.

The alert should reference the stored prediction.

---

# 21. Alert → Plot

If it concerns a specific plot:

```text
[ View Plot ]
```

goes to:

```text
/farms/:farmId/plots/:plotId
```

This is important because the farmer may want to see the broader history of that plot.

---

# 22. Alert → Scan

For follow-up alerts:

```text
[ Scan This Plot ]
```

should launch:

```text
/scan?farmId=...&plotId=...
```

with farm and plot already selected.

---

# 23. Empty State

For a new user:

```text
┌──────────────────────────────────────────────┐
│                                              │
│                    🔔                        │
│                                              │
│              You're All Caught Up            │
│                                              │
│  Important crop alerts and recommendations   │
│  will appear here.                           │
│                                              │
│              🌱 Keep farming                 │
│                                              │
└──────────────────────────────────────────────┘
```

This is much better than:

> No alerts found.

---

# 24. Filtered Empty State

If the user searches:

```text
Severe + Cotton
```

and nothing matches:

```text
No alerts found

There are no severe alerts for Cotton
matching your current filters.

[ Clear Filters ]
```

---

# 25. Error State

```text
┌──────────────────────────────────────────────┐
│                  ⚠                           │
│                                              │
│          Couldn't Load Alerts                │
│                                              │
│ We couldn't retrieve your latest alerts.     │
│                                              │
│                [ Try Again ]                 │
└──────────────────────────────────────────────┘
```

Never expose backend errors to the farmer.

---

# 26. Loading State

Use alert skeletons:

```text
┌──────────────────────────────────────────────┐
│ ████  ███████████████████                    │
│       █████████████████                     │
│       ███████                               │
│                                              │
│ ████  ███████████████████                    │
│       █████████████████                     │
│       ███████                               │
└──────────────────────────────────────────────┘
```

---

# 27. Mobile Alerts Screen

```text
┌───────────────────────────────┐
│ 🔔 Alerts          ✓ Read All │
├───────────────────────────────┤
│                               │
│ 3 Unread   2 Critical         │
│                               │
│ [All] [Unread] [Critical]     │
│                               │
│ TODAY                         │
│                               │
│ ┌───────────────────────────┐ │
│ │ ● ⚠ Disease worsening    │ │
│ │                           │ │
│ │ Tomato • Plot A-01       │ │
│ │ Mild → Moderate          │ │
│ │                           │ │
│ │ 2 hours ago              │ │
│ │                           │ │
│ │ View →                   │ │
│ └───────────────────────────┘ │
│                               │
│ ┌───────────────────────────┐ │
│ │ 🐛 Pest detected          │ │
│ │                           │ │
│ │ Cotton • Plot A-02       │ │
│ │ Aphid • 92%              │ │
│ │                           │ │
│ │ 5 hours ago              │ │
│ │                           │ │
│ │ View →                   │ │
│ └───────────────────────────┘ │
│                               │
│ YESTERDAY                     │
│                               │
│ ┌───────────────────────────┐ │
│ │ 💡 Recommendation         │ │
│ │ Tomato • Plot A-01       │ │
│ │ Yesterday                │ │
│ └───────────────────────────┘ │
└───────────────────────────────┘
```

---

# 28. Notification Bell

The Alerts screen should connect to the global navbar.

Example:

```text
🔔³
```

The number means:

```text
3 unread alerts
```

Click:

```text
🔔
```

opens a small notification preview.

---

# 29. Notification Preview

```text
┌───────────────────────────────────────────┐
│ Notifications                  View All   │
├───────────────────────────────────────────┤
│                                           │
│ ● ⚠ Disease severity increased            │
│   Tomato • Plot A-01                      │
│   2h ago                                  │
│                                           │
│ ● 🐛 Pest detected                        │
│   Cotton • Plot A-02                      │
│   5h ago                                  │
│                                           │
│ ✓ Scan completed                           │
│   Potato • Plot B-01                     │
│   Yesterday                               │
│                                           │
│             [ View All Alerts ]           │
└───────────────────────────────────────────┘
```

Only show the latest 3–5 notifications here.

---

# 30. Critical Alert on Dashboard

Your Dashboard can show a small alert section:

```text
┌─────────────────────────────────────────────┐
│ ⚠ Needs Attention                           │
│                                             │
│ Plot A-01 — Tomato                          │
│ Early Blight — Moderate                     │
│                                             │
│ [ View Diagnosis ]                          │
└─────────────────────────────────────────────┘
```

Then:

```text
View All Alerts →
```

opens `/alerts`.

This makes the Alerts screen discoverable.

---

# 31. Alert Severity UX

I recommend:

```text
CRITICAL
├── Severe disease
├── Severe pest issue
└── Significant deterioration

HIGH
├── Moderate → Severe
├── High pest risk
└── Important recommendation

MEDIUM
├── Disease detected
├── Mild condition
└── Follow-up scan

INFO
├── Scan completed
├── Diagnosis available
└── Recommendation updated
```

Don't generate alerts for every tiny event. Otherwise the farmer gets **alert fatigue**.

---

# 32. Alert Deduplication

This is an important backend/frontend consideration.

Suppose the farmer scans the same plot three times:

```text
Scan 1 → Early Blight
Scan 2 → Early Blight
Scan 3 → Early Blight
```

Don't generate:

```text
⚠ Early Blight detected
⚠ Early Blight detected
⚠ Early Blight detected
```

Instead, generate a meaningful alert only when there is a change:

```text
Healthy → Mild
Mild → Moderate
Moderate → Severe
```

or when a new significant condition appears.

---

# 33. Recommended Alert Object

Your frontend can conceptually consume:

```javascript
{
    id,
    type,
    priority,
    title,
    message,

    farmId,
    plotId,
    predictionId,

    crop,
    disease,
    severity,

    isRead,
    createdAt,

    actionType,
    actionUrl
}
```

For example:

```javascript
{
    type: "severity_increase",
    priority: "high",

    title: "Crop condition worsening",

    message:
      "Tomato severity increased from Mild to Moderate.",

    farmId: "...",
    plotId: "...",
    predictionId: "...",

    isRead: false
}
```

---

# 34. Suggested API Structure

Conceptually:

```text
GET    /alerts
GET    /alerts/:id
PATCH  /alerts/:id/read
PATCH  /alerts/read-all
DELETE /alerts/:id
```

With filtering:

```text
GET /alerts?
    type=disease
    &priority=high
    &isRead=false
    &farmId=...
    &plotId=...
```

Use your actual backend conventions when implementing.

---

# 35. React Component Architecture

I recommend:

```text
src/
├── pages/
│   └── AlertsPage.tsx
│
├── components/
│   └── alerts/
│       ├── AlertsHeader.tsx
│       ├── AlertSummary.tsx
│       ├── AlertFilters.tsx
│       ├── AlertList.tsx
│       ├── AlertCard.tsx
│       ├── AlertPriorityBadge.tsx
│       ├── AlertTypeIcon.tsx
│       ├── AlertDetail.tsx
│       ├── NotificationBell.tsx
│       ├── NotificationDropdown.tsx
│       ├── AlertsEmptyState.tsx
│       ├── AlertsSkeleton.tsx
│       └── AlertsError.tsx
│
├── api/
│   └── alerts.ts
│
└── hooks/
    └── useAlerts.ts
```

---

# 36. Component Hierarchy

```text
AlertsPage
│
├── AlertsHeader
│   └── MarkAllRead
│
├── AlertSummary
│   ├── TotalAlerts
│   ├── CriticalAlerts
│   ├── UnreadAlerts
│   └── NeedsAction
│
├── AlertFilters
│   ├── TypeFilter
│   ├── PriorityFilter
│   ├── FarmFilter
│   └── PlotFilter
│
├── AlertList
│   └── AlertCard
│       ├── AlertTypeIcon
│       ├── AlertPriorityBadge
│       └── AlertActions
│
└── Pagination
```

---

# 37. Most Important Feature for Your Project

I would make **"Crop Health Change Alerts"** the signature feature.

Instead of generic:

> Disease detected.

Your application should intelligently communicate:

```text
┌─────────────────────────────────────────────┐
│ ⚠ CROP CONDITION WORSENING                  │
│                                             │
│ 🍅 Tomato — Plot A-01                       │
│                                             │
│ Aug 23                                      │
│ Mild Early Blight                           │
│          ↓                                  │
│ Aug 26                                      │
│ Moderate Early Blight                       │
│                                             │
│ The condition has become more severe since  │
│ the previous scan.                          │
│                                             │
│ [ View Diagnosis ] [ Scan Again ]            │
└─────────────────────────────────────────────┘
```

This connects your existing **severity estimation + diagnosis history + farms/plots + recommendations** into a single useful feature.

---

# 38. Final Alerts Architecture

Your complete flow should look like:

```text
                 ┌──────────────┐
                 │    SCAN      │
                 └──────┬───────┘
                        ↓
                 ┌──────────────┐
                 │  DIAGNOSIS   │
                 └──────┬───────┘
                        ↓
                ┌────────────────┐
                │ Compare with   │
                │ previous scan  │
                └───────┬────────┘
                        ↓
                ┌────────────────┐
                │ Significant    │
                │ change?        │
                └───────┬────────┘
                        ↓ YES
                ┌────────────────┐
                │ CREATE ALERT   │
                └───────┬────────┘
                        ↓
                 🔔 ALERTS
                        │
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
       Diagnosis       Plot        Recommendation
          │             │             │
          └─────────────┼─────────────┘
                        ↓
                  Farmer Action
                        ↓
                    Re-scan
```

That gives the Alerts screen a **real functional purpose** in your application rather than making it another notification list.

### Recommended V1

Implement:

* Alert list
* Unread/read state
* Critical/high/medium/info priority
* Disease alerts
* Pest alerts
* Severity-change alerts
* Follow-up scan alerts
* Farm/plot association
* Alert → Diagnosis
* Alert → Plot
* Alert → Scan
* Filters
* Mark as read
* Mark all as read
* Notification bell
* Empty/loading/error states

### V2

Add:

* Alert grouping/deduplication
* Crop-health trend alerts
* Farm-level alerts
* Personalized alert preferences
* Push/browser notifications
* Scheduled follow-up reminders
* Weather-triggered agricultural alerts

The **V1 version is enough to make the screen feel complete**, while the severity-change and plot-specific alerts give it a strong connection to the rest of your Smart Farming system.


# Smart Farming — Profile Screen UI/UX Specification

For your Smart Farming project, the **Profile screen** should be more than a basic name/email page. It should act as the farmer's **personal account + farming preferences + application settings** hub.

The key principle is:

> **Keep personal information separate from farm/plot information.**

Farms and plots belong in **Farms & Plots**. The Profile screen should contain the **user identity, preferences, language, notification settings, security, and account controls**.

---

# 1. Route

```text
/profile
```

From the navbar:

```text
👤 Manthan ▾
      ↓
   Profile
```

Recommended sidebar:

```text
🏠 Dashboard
📷 Scan Crop
📋 History
🌾 Farms & Plots
🔔 Alerts
👤 Profile
⚙ Settings
```

You can also combine Profile and Settings later, but for your project I recommend keeping **Profile** as the identity/account page and **Settings** for application configuration.

---

# 2. Main Purpose

The profile screen should allow the user to:

* View profile information
* Edit personal information
* Add/change profile photo
* Set preferred language
* Set preferred measurement unit
* Manage notification preferences
* Change password
* View account information
* Logout
* Delete account

---

# 3. Desktop Layout

```text
┌─────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                         🔔        👤 Manthan ▾     │
├───────────────┬─────────────────────────────────────────────────────┤
│               │                                                     │
│ 🏠 Dashboard  │  Profile                                            │
│               │  Manage your personal information and preferences   │
│ 📷 Scan Crop  │                                                     │
│               │  ┌───────────────────────────────────────────────┐ │
│ 📋 History    │  │                                               │ │
│               │  │              👤                               │ │
│ 🌾 Farms      │  │           Manthan                             │ │
│               │  │        manthan@email.com                      │ │
│ 🔔 Alerts     │  │                                               │ │
│               │  │             [ Edit Profile ]                  │ │
│ 👤 Profile ● │  │                                               │ │
│               │  └───────────────────────────────────────────────┘ │
│ ⚙ Settings    │                                                     │
│               │  Personal Information                               │
│               │  ┌──────────────────────┐ ┌──────────────────────┐│
│               │  │ Full Name            │ │ Email                ││
│               │  │ Manthan Kuvadiya     │ │ manthan@email.com    ││
│               │  └──────────────────────┘ └──────────────────────┘│
│               │                                                     │
│               │  ┌──────────────────────┐ ┌──────────────────────┐│
│               │  │ Phone                │ │ Location             ││
│               │  │ +91 XXXXX XXXXX      │ │ Gujarat, India       ││
│               │  └──────────────────────┘ └──────────────────────┘│
│               │                                                     │
│               │  Preferences                                        │
│               │  Language       English ▾                           │
│               │  Area Unit      Hectares ▾                         │
│               │                                                     │
│               │  Notifications                                     │
│               │  Crop alerts                       [ ON ]           │
│               │  Recommendations                  [ ON ]           │
│               │                                                     │
│               │  Security                                           │
│               │  Password                         [ Change ]        │
│               │                                                     │
│               │  Account                                            │
│               │  [ Logout ]                    [ Delete Account ]   │
└───────────────┴─────────────────────────────────────────────────────┘
```

---

# 4. Profile Header

The top section should be visually stronger than the rest.

```text
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                       ┌─────────┐                           │
│                       │         │                           │
│                       │   👤    │                           │
│                       │         │                           │
│                       └─────────┘                           │
│                                                             │
│                   Manthan Kuvadiya                          │
│                   manthan@email.com                         │
│                                                             │
│                    [ Edit Profile ]                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

If the user hasn't uploaded a photo, use initials:

```text
MK
```

instead of a generic avatar.

---

# 5. Profile Photo

Clicking the photo:

```text
[ Change Photo ]
```

opens:

```text
┌─────────────────────────────────────┐
│ Change Profile Photo            ×  │
├─────────────────────────────────────┤
│                                     │
│             ┌─────────┐             │
│             │   MK    │             │
│             └─────────┘             │
│                                     │
│       [ Upload New Photo ]           │
│                                     │
│       JPG / PNG • Max 5 MB           │
│                                     │
│ [ Cancel ]            [ Save ]      │
└─────────────────────────────────────┘
```

For V1, you can simply use an avatar generated from the user's initials and skip image uploads.

---

# 6. Personal Information

Section:

> **Personal Information**

Fields:

```text
Full Name
Email
Phone Number
Location
```

Example:

```text
┌────────────────────────────────────────────────────┐
│ Personal Information                                │
│                                                    │
│ Full Name                 Email                    │
│ Manthan Kuvadiya          manthan@email.com        │
│                                                    │
│ Phone Number              Location                 │
│ +91 XXXXX XXXXX           Gujarat, India           │
└────────────────────────────────────────────────────┘
```

---

# 7. Edit Profile

Click:

```text
[ Edit Profile ]
```

Change the fields into inputs:

```text
┌────────────────────────────────────────────────────┐
│ Edit Profile                                       │
│                                                    │
│ Full Name                                          │
│ [ Manthan Kuvadiya                         ]       │
│                                                    │
│ Email                                              │
│ [ manthan@email.com                        ]       │
│                                                    │
│ Phone Number                                       │
│ [ +91 XXXXX XXXXX                         ]       │
│                                                    │
│ Location                                           │
│ [ Gujarat, India                           ]       │
│                                                    │
│             [ Cancel ] [ Save Changes ]            │
└────────────────────────────────────────────────────┘
```

---

# 8. Email Handling

Email should generally be treated as an account identifier.

Display:

```text
Email
manthan@email.com
✓ Verified
```

If you implement email verification:

```text
✓ Verified
```

If not:

```text
Email
manthan@email.com
```

Don't show a fake verification status.

---

# 9. Farming Preferences

This is where your profile becomes more relevant to Smart Farming.

Section:

> **Farming Preferences**

Recommended fields:

```text
Preferred Language
Area Unit
Temperature Unit
```

Example:

```text
Farming Preferences

Language
[ English ▾ ]

Area Unit
[ Hectares ▾ ]

Temperature
[ Celsius °C ▾ ]
```

For an Indian-focused project, default to:

```text
Language: English
Area: Hectares
Temperature: Celsius
```

But allow changing them.

---

# 10. Language

This is an especially useful feature for your Indian farming context.

Initial options:

```text
English
Hindi
Gujarati
```

Later you could add:

```text
Marathi
Punjabi
Bengali
Tamil
Telugu
Kannada
Malayalam
```

For your current prototype, **English + Hindi + Gujarati** is enough.

The setting should affect:

* Dashboard
* Diagnosis
* Recommendations
* Alerts
* Buttons
* Navigation

---

# 11. Notification Preferences

Section:

> **Notification Preferences**

Example:

```text
Notification Preferences

Crop Health Alerts                     [ ON ]

Disease & Pest Alerts                  [ ON ]

New Recommendations                    [ ON ]

Follow-up Scan Reminders                [ ON ]

System Notifications                    [ ON ]
```

You can later add:

```text
Email Notifications                    [ OFF ]

Browser Notifications                  [ ON ]
```

---

# 12. Smart Alert Preferences

This is particularly useful because your Alerts screen is important.

Allow:

```text
Alert me when:

☑ Disease is detected
☑ Disease severity increases
☑ Pest is detected
☑ Severe crop condition occurs
☑ Follow-up scan is recommended
☑ New recommendation is available
```

This gives the user control over alert noise.

---

# 13. Security Section

```text
Security

Password
Last changed: 30 days ago

                         [ Change Password ]
```

Clicking it:

```text
┌────────────────────────────────────────────┐
│ Change Password                        ×   │
├────────────────────────────────────────────┤
│                                            │
│ Current Password                           │
│ [ ••••••••••••• ]                          │
│                                            │
│ New Password                               │
│ [ ••••••••••••• ]                          │
│                                            │
│ Confirm New Password                       │
│ [ ••••••••••••• ]                          │
│                                            │
│ [ Cancel ]             [ Update Password ] │
└────────────────────────────────────────────┘
```

Include password validation:

```text
✓ At least 8 characters
✓ Contains a number
✓ Passwords match
```

Use whatever requirements your backend actually enforces.

---

# 14. Account Section

At the bottom:

```text
Account

Account created
August 2026

Account ID
••••••••

[ Log Out ]
```

Don't expose internal database IDs unless there's a real reason to do so.

---

# 15. Logout

Use a secondary/destructive action:

```text
[ Log Out ]
```

Confirmation:

```text
┌────────────────────────────────────────────┐
│ Log out of Smart Farming?              ×   │
├────────────────────────────────────────────┤
│                                            │
│ You'll need to sign in again to access     │
│ your farms and crop records.               │
│                                            │
│ [ Cancel ]                 [ Log Out ]     │
└────────────────────────────────────────────┘
```

---

# 16. Delete Account

Keep this visually separated from normal settings.

```text
Danger Zone

Delete Account

Permanently delete your Smart Farming account
and associated account data.

[ Delete Account ]
```

Confirmation should be much stronger:

```text
┌────────────────────────────────────────────┐
│ Delete Account                         ×   │
├────────────────────────────────────────────┤
│                                            │
│ This action cannot be undone.              │
│                                            │
│ Your account and associated data may be    │
│ permanently deleted.                       │
│                                            │
│ Type DELETE to confirm:                    │
│ [                                  ]       │
│                                            │
│ [ Cancel ]          [ Delete Account ]     │
└────────────────────────────────────────────┘
```

Only implement the exact deletion behavior that your backend supports.

---

# 17. Profile Stats

You can optionally add a small statistics row.

This is a good way to connect Profile with the rest of your application:

```text
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Farms        │ │ Plots        │ │ Scans        │
│              │ │              │ │              │
│ 2            │ │ 6            │ │ 28           │
└──────────────┘ └──────────────┘ └──────────────┘
```

I would include this in your project because it makes the profile feel more useful.

Clicking:

```text
Farms → /farms
Plots → /farms
Scans → /history
```

---

# 18. Profile Header + Stats

A better overall design:

```text
┌────────────────────────────────────────────────────────────┐
│                                                            │
│                         ┌────────┐                         │
│                         │   MK   │                         │
│                         └────────┘                         │
│                                                            │
│                    Manthan Kuvadiya                        │
│                    manthan@email.com                       │
│                                                            │
│                    [ Edit Profile ]                        │
│                                                            │
│       2 Farms          6 Plots          28 Scans           │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

This should be your main profile hero section.

---

# 19. Recommended Profile Sections

I recommend exactly these sections:

```text
Profile
│
├── Profile Header
│
├── Activity Overview
│   ├── Farms
│   ├── Plots
│   └── Scans
│
├── Personal Information
│   ├── Name
│   ├── Email
│   ├── Phone
│   └── Location
│
├── Farming Preferences
│   ├── Language
│   ├── Area Unit
│   └── Temperature Unit
│
├── Notification Preferences
│   ├── Crop Alerts
│   ├── Disease/Pest Alerts
│   ├── Recommendations
│   └── Scan Reminders
│
├── Security
│   └── Change Password
│
└── Danger Zone
    └── Delete Account
```

---

# 20. Mobile Layout

```text
┌───────────────────────────────┐
│ ← Profile                     │
├───────────────────────────────┤
│                               │
│             ┌─────┐           │
│             │ MK  │           │
│             └─────┘           │
│                               │
│       Manthan Kuvadiya        │
│       manthan@email.com       │
│                               │
│       [ Edit Profile ]        │
│                               │
├───────────────────────────────┤
│                               │
│  2          6          28     │
│ Farms      Plots      Scans   │
│                               │
├───────────────────────────────┤
│ Personal Information      ›  │
├───────────────────────────────┤
│ Farming Preferences        ›  │
├───────────────────────────────┤
│ Notifications              ›  │
├───────────────────────────────┤
│ Security                   ›  │
├───────────────────────────────┤
│                               │
│ Account                       │
│                               │
│ [ Log Out ]                   │
│                               │
│ Danger Zone                   │
│ [ Delete Account ]            │
└───────────────────────────────┘
```

On mobile, I recommend making each section **collapsible** rather than displaying every field at once.

---

# 21. Mobile Edit Profile

```text
┌───────────────────────────────┐
│ ← Edit Profile                │
├───────────────────────────────┤
│                               │
│             ┌─────┐           │
│             │ MK  │           │
│             └─────┘           │
│          Change Photo          │
│                               │
│ Full Name                     │
│ [ Manthan Kuvadiya ]          │
│                               │
│ Email                         │
│ [ manthan@email.com ]         │
│                               │
│ Phone                         │
│ [ +91 XXXXX XXXXX ]           │
│                               │
│ Location                      │
│ [ Gujarat, India ]            │
│                               │
│ [ Save Changes ]              │
└───────────────────────────────┘
```

---

# 22. Profile vs Settings

I recommend this distinction:

### Profile

```text
Who am I?
```

Contains:

* Name
* Email
* Phone
* Location
* Photo
* Language
* Farming preferences

### Settings

```text
How does the application behave?
```

Contains:

* Theme
* Notifications
* Privacy
* Application preferences
* Data management
* About

If you want a simpler MVP, you can combine them into one page.

---

# 23. React Component Structure

For your React/Vite frontend:

```text
src/
├── pages/
│   └── ProfilePage.jsx
│
├── components/
│   └── profile/
│       ├── ProfileHeader.jsx
│       ├── ProfileStats.jsx
│       ├── PersonalInfo.jsx
│       ├── EditProfileForm.jsx
│       ├── FarmingPreferences.jsx
│       ├── NotificationPreferences.jsx
│       ├── SecuritySection.jsx
│       ├── AccountSection.jsx
│       ├── DangerZone.jsx
│       ├── ChangePasswordModal.jsx
│       └── DeleteAccountModal.jsx
│
├── api/
│   └── profile.js
│
└── hooks/
    └── useProfile.js
```

---

# 24. Suggested API Structure

Conceptually:

```text
GET    /profile
PATCH  /profile
PATCH  /profile/preferences

PATCH  /profile/notifications

PATCH  /profile/password

POST   /profile/avatar

DELETE /profile
```

Your authentication system may instead expose these under `/users/me`, `/auth`, etc. The frontend should follow your actual backend API conventions.

---

# 25. Profile Data Model

Conceptually:

```javascript
{
    id,
    name,
    email,
    phone,
    location,
    avatar,

    preferences: {
        language,
        areaUnit,
        temperatureUnit
    },

    notifications: {
        cropHealth,
        diseaseAlerts,
        pestAlerts,
        recommendations,
        scanReminders
    },

    stats: {
        farms,
        plots,
        scans
    },

    createdAt
}
```

---

# 26. Important UX Connection

Your Profile should connect to the rest of the application:

```text
                     PROFILE
                        │
       ┌────────────────┼─────────────────┐
       │                │                 │
       ▼                ▼                 ▼
   Preferences      Farms/Plots       Alerts
       │                │                 │
       │                ▼                 │
       │             Diagnosis            │
       │                │                 │
       └────────────────┼─────────────────┘
                        ▼
                   Recommendations
```

For example, if the user changes:

```text
Language → Gujarati
```

then eventually the UI and AI recommendations can be presented in Gujarati.

---

# 27. Strong Feature for Your Indian-Farming Focus

I would add:

### Preferred Advisory Language

Instead of only:

```text
Language: English
```

use:

```text
Advisory Language

[ Gujarati ▾ ]

AI recommendations and farming guidance
will be presented in your preferred language.
```

This is particularly valuable for your project's Indian-farming focus.

You could support:

```text
English
ગુજરાતી
हिन्दी
```

in the UI itself.

---

# 28. Recommended V1

For your current Smart Farming implementation, I would build:

### Profile

* Profile avatar/initials
* Name
* Email
* Phone
* Location
* Edit profile
* Farm count
* Plot count
* Scan count

### Preferences

* Language
* Area unit
* Temperature unit

### Notifications

* Disease alerts
* Pest alerts
* Severity alerts
* Recommendations
* Follow-up scan reminders

### Security

* Change password
* Logout

### Account

* Account creation date
* Delete account

---

# 29. Final Profile Screen Architecture

Your complete frontend structure is now becoming:

```text
SMART FARMING
│
├── 🏠 Dashboard
│
├── 📷 Scan Crop
│    ├── Upload
│    ├── Processing
│    └── Diagnosis Result
│
├── 📋 History
│
├── 🌾 Farms & Plots
│    ├── Farms
│    ├── Farm Detail
│    └── Plot Detail
│
├── 🔔 Alerts
│
├── 👤 Profile
│    ├── Personal Information
│    ├── Farming Preferences
│    ├── Notification Preferences
│    ├── Security
│    └── Account
│
└── ⚙ Settings
```

The **Profile screen should therefore stay relatively clean**. Don't put farm management, diagnosis history, or crop information directly into Profile—those already have dedicated screens. The Profile's job is to answer **"Who is this farmer and how does this farmer want Smart Farming to work?"**.


# Smart Farming — Settings Screen UI/UX Specification

For your project, I recommend keeping **Settings separate from Profile**.

A simple distinction:

> **Profile = Who is the farmer?**
> **Settings = How should Smart Farming behave?**

The Settings screen should control application behavior, privacy, notifications, appearance, data, and other system preferences.

---

# 1. Route

```text
/settings
```

Sidebar:

```text
🏠 Dashboard
📷 Scan Crop
📋 History
🌾 Farms & Plots
🔔 Alerts
👤 Profile
⚙ Settings ●
```

---

# 2. Main Settings Categories

I recommend these sections:

```text
Settings
│
├── Appearance
│
├── Language & Region
│
├── Notifications
│
├── Scan & Diagnosis
│
├── Privacy & Data
│
├── Accessibility
│
├── Help & Support
│
└── About
```

For your current project, **Appearance, Language, Notifications, Scan & Diagnosis, Privacy, and About** are the most relevant.

---

# 3. Desktop Layout

```text
┌─────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming                         🔔        👤 Manthan ▾     │
├───────────────┬─────────────────────────────────────────────────────┤
│               │                                                     │
│ 🏠 Dashboard  │  Settings                                           │
│               │  Customize your Smart Farming experience            │
│ 📷 Scan Crop  │                                                     │
│               │  ┌───────────────────────────────────────────────┐ │
│ 📋 History    │  │ Appearance                                    │ │
│               │  │                                               │ │
│ 🌾 Farms      │  │ Theme                         Light ▾          │ │
│               │  │                                               │ │
│ 🔔 Alerts     │  │ Dashboard density             Comfortable     │ │
│               │  └───────────────────────────────────────────────┘ │
│ 👤 Profile    │                                                     │
│               │  ┌───────────────────────────────────────────────┐ │
│ ⚙ Settings ● │  │ Language & Region                             │ │
│               │  │                                               │ │
│               │  │ Interface Language             English ▾       │ │
│               │  │ Advisory Language              Gujarati ▾      │ │
│               │  │ Area Unit                      Hectares ▾      │ │
│               │  │ Temperature                    Celsius ▾       │ │
│               │  └───────────────────────────────────────────────┘ │
│               │                                                     │
│               │  ┌───────────────────────────────────────────────┐ │
│               │  │ Notifications                                │ │
│               │  │                                               │ │
│               │  │ Crop Health Alerts             [ ON ]         │ │
│               │  │ Disease & Pest Alerts          [ ON ]         │ │
│               │  │ Recommendations                [ ON ]         │ │
│               │  │ Follow-up Reminders             [ ON ]         │ │
│               │  └───────────────────────────────────────────────┘ │
└───────────────┴─────────────────────────────────────────────────────┘
```

---

# 4. Settings Header

Use:

> **Settings**

Subtitle:

> Customize your Smart Farming experience.

Don't overload the header with controls.

---

# 5. Appearance

Section:

> **Appearance**

### Theme

```text
Theme

○ Light
○ Dark
○ System
```

For your React application, I recommend:

```text
System
```

as the default.

If you want a simpler UI:

```text
Theme
[ System ▾ ]
```

---

# 6. Dark Mode

Your application should support:

```text
Light
Dark
System
```

Example:

```text
┌──────────────────────────────────────────┐
│ Appearance                               │
│                                          │
│ Theme                                    │
│                                          │
│ [ ☀ Light ] [ ◐ Dark ] [ System ]       │
└──────────────────────────────────────────┘
```

Since you are using plain CSS, implement this using CSS variables rather than maintaining separate stylesheets.

Conceptually:

```css
:root {
    --background: ...;
    --surface: ...;
    --text: ...;
    --border: ...;
}
```

Then a dark theme overrides the variables.

---

# 7. Language & Region

This section is especially important for your **Indian farming** focus.

```text
Language & Region

Interface Language
[ English ▾ ]

Advisory Language
[ Gujarati ▾ ]

Area Unit
[ Hectares ▾ ]

Temperature Unit
[ Celsius °C ▾ ]
```

---

# 8. Interface Language vs Advisory Language

I strongly recommend keeping these separate.

### Interface Language

Controls:

```text
Dashboard
Buttons
Navigation
Settings
Forms
Labels
```

### Advisory Language

Controls:

```text
AI recommendations
Disease explanation
Pest guidance
Treatment suggestions
Farming advice
```

Example:

```text
Interface Language:
English

Advisory Language:
Gujarati
```

The UI can remain English while agricultural recommendations appear in Gujarati.

This is a useful distinction for your project.

---

# 9. Indian Language Options

Initial implementation:

```text
English
ગુજરાતી
हिन्दी
```

Later:

```text
मराठी
ਪੰਜਾਬੀ
বাংলা
தமிழ்
తెలుగు
ಕನ್ನಡ
മലയാളം
```

Don't implement languages you cannot actually support throughout the interface/recommendation pipeline.

---

# 10. Notification Settings

This section controls **how** alerts behave.

Remember:

**Alerts screen = see alerts**

**Settings = configure alerts**

Example:

```text
Notifications

Crop Health Alerts                    [ ON ]

Disease Alerts                       [ ON ]

Pest Alerts                          [ ON ]

Severity Change Alerts               [ ON ]

New Recommendations                 [ ON ]

Follow-up Scan Reminders             [ ON ]
```

---

# 11. Notification Channels

Later you can support:

```text
Notification Channels

In-App Notifications                 [ ON ]

Browser Notifications                [ OFF ]

Email Notifications                  [ OFF ]
```

For your MVP, **In-App Notifications** are sufficient.

Don't create UI for channels your backend doesn't support.

---

# 12. Quiet Hours

This can be a useful advanced feature.

```text
Quiet Hours

[ ON ]

From
[ 10:00 PM ]

To
[ 06:00 AM ]
```

Then:

> Non-critical alerts will be delivered after quiet hours.

Important: **critical agricultural alerts should have a separate policy** if you implement this. Don't silently suppress severe crop alerts.

---

# 13. Scan & Diagnosis Settings

This section is directly related to your existing AI pipeline.

```text
Scan & Diagnosis

Save Scan History                     [ ON ]

Save Original Images                 [ ON ]

Automatic Diagnosis                  [ ON ]

Show Confidence Score                [ ON ]

Show Disease Severity                [ ON ]

Show AI Recommendations              [ ON ]
```

---

# 14. Image Storage Setting

Since your application processes crop images:

```text
Save Original Images

[ ON ]

Original images are stored with your
diagnosis history.
```

If the user disables this:

```text
Save Original Images
[ OFF ]

Only diagnosis information will be retained.
```

Your actual behavior must match your backend storage implementation.

---

# 15. Confidence Score

Your diagnosis screen can display:

```text
Disease:
Early Blight

Confidence:
94%
```

Settings:

```text
Show AI Confidence Scores
[ ON ]
```

This is useful for transparency.

However, don't imply that a confidence score is equivalent to medical/agricultural certainty.

---

# 16. Diagnosis Detail Preference

Allow:

```text
Diagnosis Detail

○ Simple
○ Detailed
```

### Simple

```text
Disease:
Early Blight

Severity:
Moderate

Recommended Action:
...
```

### Detailed

```text
Disease
Confidence
Severity
Observed symptoms
Possible causes
Recommended actions
Prevention
```

This is a good UX enhancement if your recommendation system supports both levels.

---

# 17. Automatic Follow-Up Scan

This fits your Alerts functionality.

```text
Follow-up Scan Reminders

[ ON ]

Remind me when a previous diagnosis
should be monitored again.
```

This can generate:

```text
📷 Follow-up scan recommended
```

on the Alerts screen.

---

# 18. Privacy & Data

Section:

> **Privacy & Data**

Example:

```text
Privacy & Data

Data Sharing
Allow anonymous usage analytics       [ OFF ]

AI Processing
Allow image processing for diagnosis  [ ON ]

Diagnosis History
Store diagnosis history               [ ON ]

Download My Data                      [ Export ]
```

Be precise about what your system actually does.

Don't include "anonymous analytics" unless your application really collects analytics.

---

# 19. Export Data

A useful feature:

```text
Your Data

Download a copy of your Smart Farming
data.

[ Export My Data ]
```

Possible exported information:

```text
Profile
Farms
Plots
Diagnosis history
Alert history
Recommendations
```

For your MVP, this can remain a future feature.

---

# 20. Delete All Scan History

This should be separate from deleting the entire account.

```text
Scan History

Delete all scan history

[ Delete History ]
```

Confirmation:

```text
Delete Scan History?

This will permanently remove your saved
diagnosis history.

[ Cancel ]       [ Delete History ]
```

This is useful because a user may want to clear historical images without deleting their account.

---

# 21. Accessibility

Add:

> **Accessibility**

Potential settings:

```text
Text Size

○ Small
● Medium
○ Large
```

and:

```text
Reduce Motion
[ OFF ]
```

Also ensure the application itself follows accessibility basics:

* Keyboard navigation
* Visible focus states
* Semantic buttons
* Proper labels
* Sufficient contrast
* Non-color-only status indicators

---

# 22. Help & Support

Section:

```text
Help & Support

How Smart Farming Works                 →

Scan Guidelines                         →

Understanding Diagnosis                 →

Contact Support                         →
```

For your project, **Scan Guidelines** is particularly useful.

---

# 23. Scan Guidelines

This could open:

```text
How to Capture a Good Crop Image

✓ Use good lighting
✓ Keep the leaf in focus
✓ Capture the affected area clearly
✓ Avoid excessive background
✓ Keep the camera steady
✓ Avoid heavily blurred images
```

This directly supports your preprocessing pipeline because your system already performs checks such as image quality/brightness/blur and leaf isolation.

---

# 24. About

Section:

```text
About Smart Farming

Version
1.0.0

AI-powered crop health and disease
assistance platform.

[ About the Project ]

[ Privacy Policy ]

[ Terms of Service ]
```

For your hackathon/project demo:

```text
Developed as part of Smart Farming
SIH25099
```

only if you want the project identifier displayed in the product.

---

# 25. Model Information

Since this is an AI project, you can optionally add:

```text
AI System

Crop Identification
EfficientNet

Disease Analysis
AI Vision Model

Pest Analysis
YOLO-based Classifier

Recommendation Engine
AI Recommendation Model
```

However, I would **not expose internal model filenames, checkpoints, or technical implementation details to normal farmers**.

If you want this information, put it under:

```text
About → AI Information
```

rather than the main Settings page.

---

# 26. Advanced "AI Transparency" Section

This could be a strong hackathon feature.

```text
AI Transparency

Smart Farming uses AI to assist with crop
health assessment.

AI results should be treated as guidance
and not as a guaranteed diagnosis.

[ Learn More ]
```

This establishes appropriate expectations.

---

# 27. Reset Settings

At the bottom:

```text
Settings

[ Reset All Settings ]
```

Confirmation:

```text
Reset Settings?

Your application preferences will be
restored to their default values.

Your farms, plots, diagnoses and history
will not be deleted.

[ Cancel ]       [ Reset Settings ]
```

This distinction is important.

**Reset Settings ≠ Delete Account.**

---

# 28. Mobile Layout

I recommend a list-based settings UI on mobile.

```text
┌───────────────────────────────┐
│ ← Settings                    │
├───────────────────────────────┤
│                               │
│ Appearance                 ›  │
│                               │
│ Language & Region          ›  │
│                               │
│ Notifications              › │
│                               │
│ Scan & Diagnosis            › │
│                               │
│ Privacy & Data              › │
│                               │
│ Accessibility               › │
│                               │
│ Help & Support              › │
│                               │
│ About                       › │
│                               │
├───────────────────────────────┤
│                               │
│ Reset Settings                │
│                               │
│ [ Reset All Settings ]        │
└───────────────────────────────┘
```

Clicking a category opens its own sub-page.

---

# 29. Mobile — Notifications

```text
┌───────────────────────────────┐
│ ← Notifications               │
├───────────────────────────────┤
│                               │
│ Crop Health Alerts       ON   │
│                               │
│ Disease Alerts           ON   │
│                               │
│ Pest Alerts              ON   │
│                               │
│ Severity Alerts          ON   │
│                               │
│ Recommendations          ON   │
│                               │
│ Follow-up Reminders      ON   │
│                               │
│ Quiet Hours              OFF  │
└───────────────────────────────┘
```

---

# 30. Mobile — Language

```text
┌───────────────────────────────┐
│ ← Language & Region           │
├───────────────────────────────┤
│                               │
│ Interface Language            │
│                               │
│ ● English                     │
│ ○ ગુજરાતી                    │
│ ○ हिन्दी                     │
│                               │
├───────────────────────────────┤
│                               │
│ Advisory Language             │
│                               │
│ ○ English                     │
│ ● ગુજરાતી                    │
│ ○ हिन्दी                     │
│                               │
├───────────────────────────────┤
│                               │
│ Area Unit                     │
│ ○ Hectares                    │
│ ○ Acres                       │
│                               │
│ Temperature                   │
│ ● Celsius                     │
│ ○ Fahrenheit                  │
└───────────────────────────────┘
```

---

# 31. Settings UX Principle

Don't make every setting a toggle.

Use the appropriate control:

| Setting        | UI                 |
| -------------- | ------------------ |
| Notifications  | Toggle             |
| Dark mode      | Segmented control  |
| Language       | Select/radio       |
| Area unit      | Select/radio       |
| Temperature    | Select/radio       |
| Text size      | Segmented control  |
| Password       | Button             |
| Export data    | Button             |
| Delete history | Destructive button |
| Delete account | Destructive button |
| Help           | Navigation link    |

This makes the interface feel more professional.

---

# 32. Profile vs Settings — Final Separation

This is the structure I recommend for your project:

### 👤 Profile

```text
Profile
│
├── Photo
├── Name
├── Email
├── Phone
├── Location
│
├── Farms: 2
├── Plots: 6
└── Scans: 28
```

### ⚙ Settings

```text
Settings
│
├── Appearance
│   └── Theme
│
├── Language & Region
│   ├── Interface Language
│   ├── Advisory Language
│   ├── Area Unit
│   └── Temperature
│
├── Notifications
│   ├── Disease
│   ├── Pest
│   ├── Severity
│   ├── Recommendations
│   └── Reminders
│
├── Scan & Diagnosis
│   ├── Save Images
│   ├── Save History
│   ├── Confidence
│   └── Diagnosis Detail
│
├── Privacy & Data
│   ├── Export Data
│   └── Delete History
│
├── Accessibility
│
├── Help & Support
│
└── About
```

---

# 33. Recommended V1 for Your Project

Don't implement every setting immediately.

### Must Have

```text
✓ Theme
✓ Interface language
✓ Advisory language
✓ Area unit
✓ Temperature unit
✓ Disease alerts toggle
✓ Pest alerts toggle
✓ Severity alerts toggle
✓ Recommendation alerts toggle
✓ Follow-up reminders
✓ Save diagnosis history
✓ Scan guidelines
✓ About
```

### Good V2 Features

```text
⭐ Browser notifications
⭐ Quiet hours
⭐ Export data
⭐ Delete scan history
⭐ Accessibility controls
⭐ AI transparency
⭐ Detailed/simple diagnosis preference
```

### Avoid Until Backend Support Exists

```text
✗ Fake email notifications
✗ Fake analytics controls
✗ Fake data export
✗ Fake cloud backup
✗ Fake privacy controls
```

The frontend should never present a setting that doesn't actually change system behavior.

---

# 34. Final Settings Architecture

Your overall application now has a clean separation:

```text
                         SMART FARMING
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
    PROFILE                SETTINGS              FARMS
       │                      │                      │
       │                ┌─────┼─────┐                │
       │                │     │     │                │
    Identity        Language Alerts Diagnosis      Plots
    Account         Theme    Privacy  Scan            │
       │                │     │       │               │
       └────────────────┼─────┼───────┼───────────────┘
                        │     │       │
                        ▼     ▼       ▼
                    SMART FARMING EXPERIENCE
```

The most important design decision is to make **Settings actually control the behavior of the features you've already designed**. For example, enabling "Severity Alerts" should affect the Alerts system, changing "Advisory Language" should affect AI recommendations, and changing "Area Unit" should update farm/plot measurements. That will make your frontend feel like a real integrated product rather than a collection of static screens.


# Smart Farming — Expert Dashboard / Review Queue UI/UX Specification

The **Expert Dashboard / Review Queue** should be a separate interface from the farmer dashboard.

Its purpose is to let an **agricultural expert, agronomist, or authorized reviewer** review AI-generated crop diagnoses, prioritize risky cases, validate AI results, and provide expert feedback.

The key concept is:

> **AI detects → Expert reviews → Expert validates/corrects → Farmer receives improved guidance.**

This can become one of the strongest features of your Smart Farming project because it introduces a **Human-in-the-Loop (HITL)** workflow rather than treating the AI prediction as the final authority.

---

# 1. Route Structure

I recommend:

```text
/expert
```

Main expert dashboard.

```text
/expert/review-queue
```

Review queue.

```text
/expert/reviews/:reviewId
```

Individual case review.

```text
/expert/farms
```

Optional expert farm overview.

---

# 2. Expert Dashboard vs Farmer Dashboard

Do **not** simply reuse your farmer dashboard.

### Farmer

```text
My Farms
My Plots
My Scans
My Alerts
My Recommendations
```

### Expert

```text
Cases
Review Queue
High-Risk Cases
AI Performance
Pending Reviews
Expert Decisions
```

The expert is managing **cases**, not managing their own farm.

---

# 3. Main Expert Dashboard

Desktop:

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming Expert Portal                  🔔      👨‍🌾 Expert ▾     │
├───────────────┬──────────────────────────────────────────────────────────┤
│               │                                                          │
│ 📊 Dashboard  │  Expert Dashboard                                       │
│               │  Review AI-assisted crop health cases                    │
│ 📋 Review     │                                                          │
│    Queue      │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│               │  │ 24       │ │ 8        │ │ 5        │ │ 11       │   │
│ 🚨 High Risk  │  │ Pending  │ │ High Risk│ │ Critical │ │ Today    │   │
│               │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│ ✓ Reviewed    │                                                          │
│               │  Priority Review Queue                                  │
│ 📈 Analytics  │                                                          │
│               │  ┌──────────────────────────────────────────────────┐  │
│ ⚙ Settings   │  │ Case       Crop    Issue       Severity  Action │  │
│               │  ├──────────────────────────────────────────────────┤  │
│               │  │ #1042      Tomato  Early Blight Severe   Review │  │
│               │  │ #1041      Cotton  Aphid       High      Review │  │
│               │  │ #1040      Potato  Healthy     Low       Review │  │
│               │  └──────────────────────────────────────────────────┘  │
│               │                                                          │
│               │  Recent Activity                                        │
│               │  ┌──────────────────────────────────────────────────┐  │
│               │  │ ✓ Case #1039 reviewed by Expert A       12m ago │  │
│               │  │ ✓ Case #1038 marked AI-correct           25m ago │  │
│               │  └──────────────────────────────────────────────────┘  │
└───────────────┴──────────────────────────────────────────────────────────┘
```

---

# 4. Expert Sidebar

Keep it compact:

```text
📊 Dashboard

📋 Review Queue
🚨 High Risk
✓ Reviewed

📈 Analytics

⚙ Settings
```

Optional:

```text
💬 Expert Notes
```

---

# 5. Dashboard Summary Cards

Use four primary cards.

### Pending Reviews

```text
24
Pending Reviews
```

### High Risk

```text
8
High-Risk Cases
```

### Critical

```text
5
Critical Cases
```

### Reviewed Today

```text
11
Reviewed Today
```

These numbers should be calculated from actual review/case data.

---

# 6. Priority Review Queue

This is the most important component.

Heading:

> **Priority Review Queue**

Subtitle:

> Cases requiring expert attention.

Example:

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Priority Review Queue                                               │
│                                                                     │
│ [ All ] [ Critical ] [ High ] [ Medium ] [ Unassigned ]            │
│                                                                     │
│ Search cases...                   Crop ▾    Issue ▾    Date ▾       │
│                                                                     │
│ Case     Crop       Issue          Severity    Confidence   Status │
│ ────────────────────────────────────────────────────────────────── │
│ #1042    Tomato     Early Blight   Severe      61%          🔴     │
│ #1041    Cotton     Aphid          High        72%          🟠     │
│ #1040    Potato     Disease        Medium      78%          🟡     │
│ #1039    Tomato     Healthy        Low         96%          🟢     │
└─────────────────────────────────────────────────────────────────────┘
```

---

# 7. Why Confidence Should Be Visible

Your expert shouldn't only see:

```text
Early Blight
```

They should see:

```text
Early Blight
Confidence: 61%
```

This helps prioritize uncertain AI predictions.

For example:

```text
High severity + low confidence
```

should have a higher review priority than:

```text
Healthy + 98% confidence
```

This creates a useful **AI-assisted triage system**.

---

# 8. Review Priority

I recommend three priority levels:

### 🔴 Critical

Examples:

```text
Severe disease
Severe pest condition
Very low AI confidence
Rapid deterioration
Conflicting model outputs
```

### 🟠 High

```text
Moderate → Severe
Important disease detection
Low confidence
Repeated deterioration
```

### 🟡 Medium

```text
New disease detection
Moderate severity
Moderate confidence
```

### 🟢 Low

```text
Healthy crop
High confidence
No significant change
```

Don't make priority depend only on confidence.

---

# 9. Review Queue Filters

Experts need strong filtering.

Use:

```text
[ All ]
[ Critical ]
[ High ]
[ Medium ]
[ Low ]
```

Then:

```text
Crop:       [ All Crops ▾ ]
Issue:      [ All Issues ▾ ]
Severity:   [ All ▾ ]
Confidence: [ All ▾ ]
Status:     [ Pending ▾ ]
Date:       [ Date ▾ ]
```

Optional:

```text
Location: [ Gujarat ▾ ]
```

if your platform eventually operates across multiple regions.

---

# 10. Search

Search should support:

```text
Case ID
Crop
Disease
Pest
Farm
Plot
Farmer
```

Example:

```text
🔍 Search case, crop, disease, farmer...
```

---

# 11. Review Queue Card Alternative

For mobile or a more visual desktop UI, use cards.

```text
┌──────────────────────────────────────────────┐
│ 🔴 CRITICAL                                  │
│                                              │
│ Case #1042                                   │
│ Tomato • Early Blight                        │
│                                              │
│ AI Prediction                                │
│ Early Blight                                 │
│ Confidence: 61%                              │
│ Severity: Severe                             │
│                                              │
│ ⚠ Requires Expert Review                    │
│                                              │
│ [ Review Case ]                              │
└──────────────────────────────────────────────┘
```

---

# 12. Individual Expert Review Screen

This is the **most important expert screen**.

Route:

```text
/expert/reviews/:reviewId
```

It should display all evidence in one place.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ ← Review Queue                                      Case #1042           │
├───────────────────────┬──────────────────────────────────────────────────┤
│                       │                                                  │
│                       │ AI Diagnosis                                     │
│    Crop Image         │                                                  │
│                       │ Crop: Tomato                                     │
│   ┌───────────────┐   │ Disease: Early Blight                            │
│   │               │   │ Confidence: 61%                                  │
│   │    LEAF       │   │ Severity: Severe                                 │
│   │     IMAGE     │   │                                                  │
│   │               │   │ ─────────────────────────────────────────────── │
│   └───────────────┘   │ Previous Diagnosis                               │
│                       │ Mild → Moderate → Severe                         │
│ [ View Original ]     │                                                  │
│ [ View Processed ]    │ ─────────────────────────────────────────────── │
│                       │ AI Recommendation                                │
│                       │                                                  │
│                       │ [ recommendation content ]                       │
│                       │                                                  │
│                       │ ─────────────────────────────────────────────── │
│                       │ Expert Decision                                  │
│                       │                                                  │
│                       │ ○ AI Result Correct                              │
│                       │ ○ AI Result Incorrect                            │
│                       │ ○ Needs More Information                         │
│                       │                                                  │
│                       │ Expert Diagnosis                                 │
│                       │ [ Select diagnosis ▾ ]                           │
│                       │                                                  │
│                       │ Severity                                         │
│                       │ [ Moderate ▾ ]                                   │
│                       │                                                  │
│                       │ Notes                                            │
│                       │ [                              ]                 │
│                       │                                                  │
│                       │ [ Save Review ]                                  │
└───────────────────────┴──────────────────────────────────────────────────┘
```

---

# 13. Image Viewer

The expert needs better image inspection than the farmer.

Provide:

```text
[ Original ]
[ Processed ]
[ Leaf Isolation ]
```

Potentially:

```text
[ Original ] [ Leaf Mask ] [ Enhanced ]
```

If your preprocessing pipeline produces these intermediate artifacts, exposing them here is highly valuable.

---

# 14. Image Zoom

Add:

```text
🔍+
🔍−
↻
⛶
```

The expert should be able to inspect:

* Lesions
* Spots
* Discoloration
* Pest evidence
* Leaf boundaries

Don't force experts to review a 224×224 image only.

Use the highest-quality stored image available.

---

# 15. AI Diagnosis Panel

Example:

```text
AI Diagnosis

Crop
Tomato

Disease
Early Blight

Confidence
61%

Severity
Severe
```

If multiple models are involved, you can optionally show:

```text
Crop Identification
Tomato — 97%

Disease Classification
Early Blight — 61%

Severity Estimation
Severe
```

This matches your existing pipeline architecture.

---

# 16. AI Recommendation Panel

Show the recommendation separately.

```text
AI Recommendation

The system recommends reviewing the affected
area and following the appropriate disease
management procedure.

[ View Full Recommendation ]
```

Do not mix AI diagnosis and expert diagnosis into the same visual block.

The expert needs to clearly distinguish:

```text
AI says:
Early Blight

Expert says:
__________
```

---

# 17. Historical Context

This is extremely important.

The expert should see previous cases from the same plot.

```text
Previous Crop Health

Aug 20
Healthy

Aug 23
Early Blight — Mild

Aug 25
Early Blight — Moderate

Aug 26
Early Blight — Severe
```

Visually:

```text
Healthy
   ↓
Mild
   ↓
Moderate
   ↓
🔴 Severe
```

This gives the expert context that a single image cannot provide.

---

# 18. Expert Decision

The expert must explicitly classify the AI result.

Recommended options:

```text
○ AI Result Correct

○ AI Result Incorrect

○ Uncertain / Needs More Information
```

This is better than simply:

```text
[ Approve ]
```

because the purpose is to capture **expert validation of AI output**.

---

# 19. If AI Result Is Correct

Show:

```text
AI Result Correct ✓

Confirmed Diagnosis
Early Blight

Confirmed Severity
Severe

Expert Notes
[                                  ]

[ Confirm Review ]
```

---

# 20. If AI Result Is Incorrect

Dynamic form:

```text
AI Result Incorrect

AI predicted:
Early Blight

Expert Diagnosis:
[ Select Disease ▾ ]

Expert Severity:
[ Moderate ▾ ]

Reason:
[                              ]

[ Submit Correction ]
```

This is important because your system can potentially use this feedback for future model improvement.

---

# 21. If Expert Is Uncertain

```text
Needs More Information

Reason:
[ Select reason ▾ ]

○ Image quality insufficient
○ Symptoms unclear
○ Multiple possible diseases
○ Additional field inspection required
○ Other

Notes:
[                              ]

Recommended Action:
[                              ]

[ Request More Information ]
```

---

# 22. Expert Notes

Use a proper text area:

```text
Expert Notes

┌──────────────────────────────────────────┐
│                                          │
│                                          │
│                                          │
└──────────────────────────────────────────┘

0 / 1000 characters
```

Don't make this a tiny single-line input.

---

# 23. Farmer-Facing vs Internal Notes

I strongly recommend separating these.

```text
Expert Notes
```

and:

```text
Message for Farmer
```

Example:

```text
Internal Expert Note
Only authorized experts can see this.

[ ... ]

Message for Farmer
This may be shown to the farmer.

[ ... ]
```

This prevents internal comments from accidentally becoming farmer-facing advice.

---

# 24. Final Review Actions

At the bottom:

```text
[ Save Draft ]

[ Confirm AI Result ]

[ Submit Correction ]

[ Request More Information ]
```

The exact buttons should change based on the selected decision.

---

# 25. Review Status

Each case should have a status:

```text
Pending
In Review
Reviewed
Needs More Information
Escalated
```

Example:

```text
Case #1042
Status: In Review
Assigned to: Dr. Patel
```

---

# 26. Assignment

For multiple experts:

```text
Assigned Expert

[ Dr. Patel ▾ ]
```

Or:

```text
[ Assign to Me ]
```

This prevents two experts from unknowingly reviewing the same case.

---

# 27. Expert Dashboard — Assignment Section

Add:

```text
My Queue
```

Example:

```text
My Queue

12 cases assigned to you

5  Critical
4  High
3  Medium
```

And:

```text
Unassigned
7 cases
```

---

# 28. Case Table

A more professional expert queue:

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Case │ Crop   │ Issue       │ Severity │ Confidence │ Age │ Status        │
├──────┼────────┼─────────────┼──────────┼────────────┼─────┼───────────────┤
│1042  │ Tomato │ Early Blight│ Severe   │ 61%        │ 2h  │ 🔴 Pending    │
│1041  │ Cotton │ Aphid       │ High     │ 72%        │ 3h  │ 🟠 Pending    │
│1040  │ Potato │ Disease     │ Medium   │ 78%        │ 5h  │ 🟡 In Review  │
│1039  │ Tomato │ Healthy     │ Low      │ 96%        │ 7h  │ ✓ Reviewed    │
└────────────────────────────────────────────────────────────────────────────┘
```

Clicking a row:

```text
→ /expert/reviews/1042
```

---

# 29. Queue Sorting

Experts should be able to sort by:

```text
Priority ↓
Confidence ↑
Severity ↓
Newest
Oldest
```

Default:

> **Highest priority first**

This is important. An expert should not have to manually find the critical cases.

---

# 30. Smart Priority Score

You can eventually calculate a review priority score using factors such as:

```text
Severity
+
Model confidence
+
Change from previous diagnosis
+
Pest/disease type
+
Time waiting
```

Conceptually:

```text
Review Priority
      │
      ├── Severity
      ├── Confidence uncertainty
      ├── Historical deterioration
      ├── Case age
      └── Issue type
```

This is a **decision-support mechanism**, not a replacement for expert judgment.

---

# 31. "Why This Case Is Prioritized"

This would be a very strong UX feature.

For example:

```text
Why prioritized?

🔴 Severe crop condition
⚠ Confidence below 70%
📈 Severity increased since last scan
⏱ Waiting for 3 hours
```

The expert immediately understands why the case is at the top.

---

# 32. Expert Dashboard Analytics

You can include a small section:

```text
Review Performance

Cases Reviewed
42

AI Confirmed
34

AI Corrected
6

Needs More Info
2
```

And:

```text
AI Agreement Rate

81%
```

However, be careful with the term **accuracy**.

If experts validate only a subset of cases, don't call this the overall model accuracy.

Use:

> **Expert-AI Agreement Rate**

instead.

---

# 33. Review Activity

Example:

```text
Recent Activity

✓ Case #1040 confirmed
  10 minutes ago

✎ Case #1039 corrected
  32 minutes ago

! Case #1038 requested more information
  1 hour ago
```

---

# 34. Expert Review History

Route:

```text
/expert/reviewed
```

Display:

```text
Reviewed Cases

Case       Decision              Expert       Date
#1039      AI Confirmed          You          Today
#1038      Diagnosis Corrected   You          Today
#1037      More Info Required    You          Yesterday
```

Filters:

```text
[ Confirmed ]
[ Corrected ]
[ More Info ]
```

---

# 35. High-Risk Screen

Route:

```text
/expert/high-risk
```

This should be a focused queue.

```text
🚨 High-Risk Cases

8 cases require immediate attention

┌──────────────────────────────────────────────┐
│ #1042                                       │
│ Tomato • Severe Early Blight                │
│ Confidence: 61%                             │
│                                             │
│ Severity increased rapidly                  │
│                                             │
│ [ Review ]                                  │
└──────────────────────────────────────────────┘
```

---

# 36. Mobile Expert Dashboard

```text
┌───────────────────────────────┐
│ 🌱 Expert Portal       🔔     │
├───────────────────────────────┤
│                               │
│ Expert Dashboard              │
│                               │
│ ┌────────┐ ┌────────┐        │
│ │ 24     │ │ 8      │        │
│ │Pending │ │High    │        │
│ └────────┘ └────────┘        │
│                               │
│ ┌────────┐ ┌────────┐        │
│ │ 5      │ │ 11     │        │
│ │Critical│ │Today   │        │
│ └────────┘ └────────┘        │
│                               │
│ Priority Cases                │
│                               │
│ ┌───────────────────────────┐ │
│ │ 🔴 #1042                  │ │
│ │ Tomato                    │ │
│ │ Early Blight              │ │
│ │ Severe • 61%              │ │
│ │                           │ │
│ │ [ Review Case ]           │ │
│ └───────────────────────────┘ │
│                               │
│ ┌───────────────────────────┐ │
│ │ 🟠 #1041                  │ │
│ │ Cotton                    │ │
│ │ Aphid • 72%               │ │
│ │                           │ │
│ │ [ Review Case ]           │ │
│ └───────────────────────────┘ │
└───────────────────────────────┘
```

---

# 37. Mobile Review Screen

```text
┌───────────────────────────────┐
│ ← Case #1042                  │
├───────────────────────────────┤
│                               │
│        [ Crop Image ]         │
│                               │
│ [Original] [Processed]       │
│                               │
├───────────────────────────────┤
│ AI Diagnosis                  │
│                               │
│ Crop                          │
│ Tomato                        │
│                               │
│ Disease                       │
│ Early Blight                  │
│                               │
│ Confidence                    │
│ 61%                           │
│                               │
│ Severity                      │
│ 🔴 Severe                     │
│                               │
├───────────────────────────────┤
│ Previous History              │
│                               │
│ Mild → Moderate → Severe      │
│                               │
├───────────────────────────────┤
│ Expert Decision               │
│                               │
│ ○ AI Correct                  │
│ ○ AI Incorrect                │
│ ○ Need More Information       │
│                               │
│ Expert Diagnosis              │
│ [ Select ▾ ]                  │
│                               │
│ Notes                         │
│ [                         ]   │
│                               │
│ [ Submit Review ]             │
└───────────────────────────────┘
```

---

# 38. Important Security Requirement

The Expert Portal must **not** simply rely on hiding the page from normal users.

Frontend:

```text
/user → Farmer UI
/expert → Expert UI
```

But backend must enforce authorization:

```text
role = expert
```

before allowing:

```text
GET /expert/reviews
POST /expert/reviews
PATCH /expert/reviews/:id
```

A farmer should never be able to access expert review data by manually entering the URL.

---

# 39. Suggested Roles

You can eventually have:

```text
Farmer
Expert
Admin
```

### Farmer

```text
Scan
Diagnosis
Recommendations
History
Alerts
Farms
```

### Expert

```text
Review Queue
Case Review
Validation
Correction
Expert Notes
```

### Admin

```text
User Management
Expert Management
System Monitoring
Model Performance
```

This gives you a clean RBAC architecture.

---

# 40. Recommended React Structure

```text
src/
├── pages/
│   └── expert/
│       ├── ExpertDashboard.jsx
│       ├── ReviewQueue.jsx
│       ├── ReviewCase.jsx
│       ├── HighRiskCases.jsx
│       └── ReviewedCases.jsx
│
├── components/
│   └── expert/
│       ├── ExpertSidebar.jsx
│       ├── ExpertHeader.jsx
│       ├── ExpertStatCards.jsx
│       ├── ReviewQueueTable.jsx
│       ├── ReviewCaseCard.jsx
│       ├── PriorityBadge.jsx
│       ├── CaseStatusBadge.jsx
│       ├── CropImageViewer.jsx
│       ├── AIDiagnosisPanel.jsx
│       ├── DiagnosisHistory.jsx
│       ├── ExpertDecisionForm.jsx
│       ├── ExpertNotes.jsx
│       └── ReviewActivity.jsx
│
├── api/
│   └── expert.js
│
└── hooks/
    └── useExpertReviews.js
```

---

# 41. Suggested Review Data Model

Your frontend should conceptually receive something like:

```javascript
{
    id: "1042",

    farmer: {
        id: "...",
        name: "..."
    },

    farm: {
        id: "...",
        name: "..."
    },

    plot: {
        id: "...",
        name: "..."
    },

    image: {
        originalUrl: "...",
        processedUrl: "...",
        isolatedLeafUrl: "..."
    },

    aiResult: {
        crop: "Tomato",
        disease: "Early Blight",
        confidence: 0.61,
        severity: "Severe"
    },

    history: [],

    priority: "critical",

    status: "pending",

    assignedExpert: null,

    expertReview: null,

    createdAt: "..."
}
```

---

# 42. Expert Review Object

After review:

```javascript
{
    decision: "ai_incorrect",

    diagnosis: "Late Blight",

    severity: "Moderate",

    notes: "Symptoms are more consistent with late blight.",

    farmerMessage:
        "Please monitor the affected leaves and follow the recommended treatment.",

    reviewedBy: "...",

    reviewedAt: "..."
}
```

---

# 43. Complete Expert Workflow

Your Smart Farming system can now have a very strong workflow:

```text
                  FARMER
                     │
                     ▼
               Upload Image
                     │
                     ▼
              AI PROCESSING
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      Crop         Disease       Pest
      Model         Model        Model
        │            │            │
        └────────────┼────────────┘
                     ▼
                AI Diagnosis
                     │
                     ▼
             Confidence / Risk
                     │
                     ▼
              ┌─────────────┐
              │ Needs Expert│
              │   Review?   │
              └──────┬──────┘
                     │
                    YES
                     ▼
             EXPERT REVIEW QUEUE
                     │
                     ▼
              Expert Reviews
                     │
          ┌──────────┼───────────┐
          ▼          ▼           ▼
       Correct    Incorrect    Uncertain
          │          │           │
          │          ▼           ▼
          │       Correction   More Info
          │          │           │
          └──────────┼───────────┘
                     ▼
              Final Diagnosis
                     │
                     ▼
              Recommendation
                     │
                     ▼
                  FARMER
```

---

# 44. The Most Valuable Feature

For your project, I would make **AI–Expert Disagreement Detection** the standout feature.

Example:

```text
┌──────────────────────────────────────────────────────────┐
│ 🚨 EXPERT REVIEW REQUIRED                                │
│                                                          │
│ AI Prediction                                            │
│ Early Blight                                             │
│ Confidence: 61%                                          │
│                                                          │
│ Why this case needs review                               │
│                                                          │
│ • Low model confidence                                   │
│ • Severity classified as Severe                          │
│ • Severity increased since previous scan                 │
│ • New disease detected                                   │
│                                                          │
│              [ Review Case ]                             │
└──────────────────────────────────────────────────────────┘
```

That makes the expert dashboard **AI-assisted rather than just a CRUD admin panel**.

---

# 45. Recommended V1

For your current project, I would implement these first:

### Expert Dashboard

* Pending review count
* Critical count
* High-risk count
* Reviewed today
* Priority queue
* Search
* Filters
* Sorting
* Recent activity

### Review Queue

* Case ID
* Crop
* Disease/pest
* Severity
* Confidence
* Priority
* Status
* Assigned expert

### Review Case

* Original image
* Processed image
* Leaf-isolated image if available
* AI crop result
* AI disease result
* Confidence
* Severity
* Previous diagnosis history
* AI recommendation
* Expert decision
* Expert diagnosis
* Expert severity
* Expert notes
* Farmer-facing message
* Submit review

### Security

* Expert-only routes
* Backend role authorization
* Audit trail

---

## The overall role architecture becomes

```text
                         SMART FARMING
                              │
                ┌─────────────┴─────────────┐
                │                           │
             FARMER                       EXPERT
                │                           │
       ┌────────┼────────┐          ┌───────┼────────┐
       ▼        ▼        ▼          ▼       ▼        ▼
     Scan     Farms    Alerts     Queue   Review   History
       │        │        │          │       │
       ▼        ▼        ▼          └───────┤
   Diagnosis  Plots   Actions              │
       │                                     ▼
       └──────────────► AI ◄────────── Expert Validation
                         │
                         ▼
                  Final Recommendation
                         │
                         ▼
                       Farmer
```

This **Expert Dashboard / Review Queue** is worth adding to your Smart Farming frontend because it gives your project a genuine **human-in-the-loop agricultural decision-support architecture** rather than presenting the AI prediction as unquestionable.


# Smart Farming — Expert Review Case Screen

This is the **most important screen in the Expert Portal**. It should give the agricultural expert enough context to make a decision without navigating through multiple pages.

The core UX should be:

> **Inspect evidence → Understand AI decision → Compare history → Make expert decision → Provide farmer-safe guidance → Submit review**

---

# 1. Route

```text
/expert/reviews/:reviewId
```

Example:

```text
/expert/reviews/1042
```

---

# 2. Screen Objective

The expert should be able to answer five questions immediately:

1. **What crop is this?**
2. **What did the AI detect?**
3. **How confident is the AI?**
4. **What has happened to this plot previously?**
5. **Do I agree with the AI, and what should the farmer be told?**

---

# 3. Overall Desktop Layout

I recommend a **three-zone layout** rather than one long page.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ ← Review Queue       Case #1042      🔴 CRITICAL       Pending Review        │
├───────────────────────────────┬──────────────────────────────────────────────┤
│                               │                                              │
│        IMAGE EVIDENCE         │             CASE INFORMATION                 │
│                               │                                              │
│   ┌───────────────────────┐   │  Farmer: Manthan                            │
│   │                       │   │  Farm: Patel Farm                            │
│   │                       │   │  Plot: Tomato Plot A                         │
│   │       CROP IMAGE      │   │                                              │
│   │                       │   │  Crop: Tomato                                │
│   │                       │   │  Scan Date: 26 Aug 2026                      │
│   └───────────────────────┘   │                                              │
│                               │                                              │
│ [Original] [Processed]        │  AI DIAGNOSIS                               │
│ [Leaf Isolation]              │  Early Blight                                │
│                               │  Confidence: 61%                             │
│ 🔍 Zoom  ⛶ Fullscreen         │  Severity: 🔴 Severe                         │
│                               │                                              │
├───────────────────────────────┼──────────────────────────────────────────────┤
│                               │                                              │
│       DIAGNOSIS HISTORY       │        EXPERT DECISION                      │
│                               │                                              │
│ Healthy → Mild → Moderate     │  ○ AI Result Correct                        │
│              → Severe         │  ○ AI Result Incorrect                      │
│                               │  ○ Needs More Information                   │
│                               │                                              │
│       AI RECOMMENDATION       │  Diagnosis                                   │
│                               │  [ Select diagnosis ▾ ]                     │
│ [View recommendation]         │                                              │
│                               │  Severity                                    │
│                               │  [ Select severity ▾ ]                      │
│                               │                                              │
│                               │  Expert Notes                                │
│                               │  [.......................................]   │
│                               │                                              │
│                               │  Farmer Message                              │
│                               │  [.......................................]   │
│                               │                                              │
│                               │  [ Save Draft ] [ Submit Review ]            │
└───────────────────────────────┴──────────────────────────────────────────────┘
```

---

# 4. Top Header

The header should always show the case identity.

```text
← Back to Review Queue

Case #1042

🔴 Critical

Pending Review
```

Example:

```text
┌─────────────────────────────────────────────────────────────────┐
│ ← Review Queue   Case #1042   🔴 Critical   Pending Review      │
└─────────────────────────────────────────────────────────────────┘
```

### Important

Do not make the expert wonder which case they're reviewing.

Always show:

* Case ID
* Priority
* Status

---

# 5. Case Metadata

Place this near the top:

```text
Case Information

Farmer
Manthan Kuvadiya

Farm
Patel Farm

Plot
Tomato Plot A

Crop
Tomato

Scan Date
26 Aug 2026, 10:42 AM
```

If your system has GPS/location:

```text
Location
Gujarat, India
```

Only display information your backend actually stores.

---

# 6. Image Evidence — Left Side

This should be the visual focus.

```text
┌─────────────────────────────────────┐
│                                     │
│                                     │
│             LEAF IMAGE              │
│                                     │
│                                     │
└─────────────────────────────────────┘
```

Under it:

```text
[ Original ] [ Processed ] [ Leaf ]
```

I recommend **tabs** rather than three images simultaneously.

---

# 7. Image Tabs

### Original

The actual image uploaded by the farmer.

```text
Original
```

### Processed

The image after your preprocessing pipeline.

```text
Processed
```

### Leaf Isolation

If your pipeline successfully isolates the leaf:

```text
Leaf Isolation
```

This is particularly useful for the expert because they can compare:

```text
Original → Processed → Isolated Leaf
```

---

# 8. Image Controls

Under the image:

```text
🔍−    100%    🔍+       ⛶
```

Functions:

* Zoom out
* Current zoom
* Zoom in
* Fullscreen

Optional:

```text
↻ Rotate
```

---

# 9. Image Quality Information

Because your preprocessing pipeline checks image quality, show the relevant results.

Example:

```text
Image Quality

✓ Sharpness        Good
✓ Brightness       Good
✓ Leaf Detected    Yes
✓ Image Quality    Acceptable
```

If something is questionable:

```text
⚠ Sharpness        Low
✓ Brightness       Good
✓ Leaf Detected    Yes
```

This helps the expert understand whether the AI's uncertainty may be related to image quality.

---

# 10. AI Diagnosis Panel

This should be one of the strongest visual sections.

```text
┌──────────────────────────────────────────────┐
│ AI DIAGNOSIS                                 │
│                                              │
│ Crop                                         │
│ Tomato                                       │
│                                              │
│ Disease                                      │
│ Early Blight                                 │
│                                              │
│ Confidence                                   │
│ 61%                                          │
│                                              │
│ Severity                                     │
│ 🔴 Severe                                    │
└──────────────────────────────────────────────┘
```

---

# 11. Confidence Visualization

Don't show only:

```text
61%
```

Use a progress indicator:

```text
AI Confidence

61%

████████████░░░░░░░░
```

And optionally:

```text
Moderate confidence
```

Do not label confidence as "accuracy."

---

# 12. Model Results

Because your pipeline contains multiple stages, the expert can optionally see the individual outputs.

```text
AI Pipeline Results

Crop Identification
Tomato                         97%

Disease Classification
Early Blight                  61%

Severity Estimation
Severe
```

For pest-related cases:

```text
Pest Classification
Aphid                          72%
```

This is useful for expert review without exposing technical model internals.

---

# 13. AI Recommendation

Place this below the diagnosis.

```text
┌──────────────────────────────────────────────┐
│ AI RECOMMENDATION                            │
│                                              │
│ The AI recommends monitoring the affected   │
│ leaves and following the appropriate crop    │
│ disease management procedure.                │
│                                              │
│ [ View Full Recommendation ]                 │
└──────────────────────────────────────────────┘
```

The expert should be able to inspect the recommendation **before approving it**.

---

# 14. Recommendation Warning

If your system generates recommendations using an LLM, make the distinction clear:

```text
ℹ AI-generated recommendation
```

The expert should be able to override it.

---

# 15. Historical Diagnosis

This is one of the most valuable sections.

```text
Diagnosis History

Aug 20
Healthy
        ↓
Aug 23
Early Blight — Mild
        ↓
Aug 25
Early Blight — Moderate
        ↓
Aug 26
Early Blight — Severe
```

Visually:

```text
Healthy ──→ Mild ──→ Moderate ──→ 🔴 Severe
```

This gives the expert temporal context.

---

# 16. Previous Scan Images

If you store historical images, provide:

```text
Previous Scans

[ Aug 20 ] [ Aug 23 ] [ Aug 25 ]

        [ View Scan History ]
```

Clicking a previous scan should ideally open a lightweight comparison view.

---

# 17. Expert Decision Panel

This is where the expert takes action.

```text
Expert Decision

○ AI Result Correct

○ AI Result Incorrect

○ Needs More Information
```

I recommend **radio buttons**, not a dropdown.

The three choices should be immediately visible.

---

# 18. Decision: AI Result Correct

After selecting:

```text
● AI Result Correct

Confirmed Diagnosis

Early Blight

Confirmed Severity

Severe
```

Then:

```text
Expert Notes
[........................................]
```

And:

```text
Farmer Message
[........................................]
```

Button:

```text
[ Confirm Review ]
```

---

# 19. Decision: AI Result Incorrect

When selected, dynamically expand:

```text
● AI Result Incorrect

AI Diagnosis
Early Blight

Expert Diagnosis
[ Select Disease ▾ ]

Expert Severity
[ Select Severity ▾ ]

Reason for Correction
[........................................]

Expert Notes
[........................................]

Farmer Message
[........................................]

[ Submit Correction ]
```

---

# 20. Expert Diagnosis Dropdown

For your current project, populate it from the diseases your models actually support.

Don't create a huge generic list if your model doesn't support those diseases.

For example:

```text
Select Disease

[ Select ]

Early Blight
Late Blight
Healthy
...
```

The exact list should come from your backend/model configuration.

---

# 21. Expert Severity

Use:

```text
Healthy
Mild
Moderate
Severe
```

Potentially:

```text
[ Healthy ▾ ]
```

The expert should not be forced to accept the AI's severity.

---

# 22. Decision: Needs More Information

This option is very important.

```text
● Needs More Information
```

Then:

```text
Why?

☐ Image quality insufficient
☐ Symptoms unclear
☐ Multiple possible conditions
☐ Additional image required
☐ Field inspection required
☐ Other
```

Then:

```text
Additional Request

[ Please upload a clearer image of the affected
  leaf from both sides.                    ]
```

Button:

```text
[ Request More Information ]
```

---

# 23. Expert Notes vs Farmer Message

Keep these **strictly separate**.

### Expert Notes

```text
Internal note
Only authorized experts can see this.
```

### Farmer Message

```text
Farmer-facing message
May be shown to the farmer.
```

Example:

```text
Expert Notes:
Symptoms appear consistent with early blight,
but image quality limits certainty.

Farmer Message:
Please upload another clear image of the affected
leaf so we can provide a more reliable assessment.
```

This is an important safety and UX distinction.

---

# 24. Submit Review Confirmation

Before submitting:

```text
┌───────────────────────────────────────────────┐
│ Confirm Expert Review                         │
├───────────────────────────────────────────────┤
│                                               │
│ Decision                                      │
│ AI Result Incorrect                           │
│                                               │
│ Diagnosis                                     │
│ Late Blight                                   │
│                                               │
│ Severity                                      │
│ Moderate                                      │
│                                               │
│ This review will be saved and the final       │
│ result may be shown to the farmer.             │
│                                               │
│ [ Cancel ]              [ Confirm & Submit ]  │
└───────────────────────────────────────────────┘
```

This prevents accidental submissions.

---

# 25. Save Draft

Experts may need to leave a case temporarily.

Provide:

```text
[ Save Draft ]
```

Status becomes:

```text
🟡 Draft
```

When returning:

```text
Continue Review
```

This is especially useful for long cases.

---

# 26. Case Status Lifecycle

Use:

```text
Pending
   ↓
In Review
   ↓
Draft
   ↓
Reviewed
```

Alternative path:

```text
Pending
   ↓
In Review
   ↓
Needs More Information
   ↓
Additional Information
   ↓
Reviewed
```

---

# 27. Assignment Information

At the top-right:

```text
Assigned To

Dr. Patel

[ Reassign ]
```

For the current expert:

```text
Assigned to you
```

If unassigned:

```text
⚠ Unassigned

[ Assign to Me ]
```

---

# 28. Expert Activity / Audit Trail

At the bottom or side panel:

```text
Case Activity

10:42 AM
Farmer uploaded image

10:43 AM
AI diagnosis completed

10:44 AM
Case marked High Priority

11:02 AM
Assigned to Dr. Patel

11:15 AM
Review started
```

After submission:

```text
11:27 AM
Expert review submitted
```

This creates an audit trail.

---

# 29. Right-Side Sticky Action Panel

On desktop, I recommend making the **Expert Decision** panel sticky.

As the expert scrolls through:

```text
Image
↓
AI diagnosis
↓
History
↓
Recommendation
```

the decision panel remains accessible.

```text
┌───────────────────────────┐
│ EXPERT DECISION           │
│                           │
│ ○ AI Correct              │
│ ○ AI Incorrect            │
│ ○ Need More Information   │
│                           │
│ [ Save Draft ]            │
│ [ Submit Review ]         │
└───────────────────────────┘
```

This is excellent for usability.

---

# 30. Recommended Screen Sections

The final order should be:

```text
Review Case
│
├── Header
│   ├── Case ID
│   ├── Priority
│   └── Status
│
├── Case Information
│   ├── Farmer
│   ├── Farm
│   ├── Plot
│   ├── Crop
│   └── Date
│
├── Image Evidence
│   ├── Original
│   ├── Processed
│   └── Leaf Isolation
│
├── Image Quality
│
├── AI Diagnosis
│   ├── Crop
│   ├── Disease
│   ├── Confidence
│   └── Severity
│
├── AI Recommendation
│
├── Diagnosis History
│
├── Expert Decision
│   ├── Correct
│   ├── Incorrect
│   └── Need More Information
│
├── Expert Diagnosis
│
├── Expert Severity
│
├── Expert Notes
│
├── Farmer Message
│
└── Submit
```

---

# 31. Color/Status System

Use colors consistently throughout the Expert Portal.

```text
🔴 Critical
🟠 High
🟡 Medium
🟢 Low
🔵 Informational
```

For diagnosis:

```text
Healthy       🟢
Mild          🟡
Moderate      🟠
Severe        🔴
```

Don't rely on color alone. Always include text.

For example:

```text
🔴 Severe
```

not simply a red circle.

---

# 32. Responsive Mobile Layout

On mobile, change from two/three columns to a vertical workflow:

```text
┌───────────────────────────────┐
│ ← Review Case      #1042      │
│ 🔴 Critical                   │
├───────────────────────────────┤
│                               │
│ Image                         │
│                               │
│      ┌──────────────┐         │
│      │              │         │
│      │    IMAGE     │         │
│      │              │         │
│      └──────────────┘         │
│                               │
│ [Original] [Processed]       │
│                               │
├───────────────────────────────┤
│ Case Information              │
│ Farmer: Manthan               │
│ Farm: Patel Farm              │
│ Plot: Tomato A                │
│                               │
├───────────────────────────────┤
│ AI Diagnosis                  │
│                               │
│ Tomato                        │
│ Early Blight                  │
│ 61% confidence                │
│ 🔴 Severe                     │
│                               │
├───────────────────────────────┤
│ Diagnosis History             │
│ Healthy → Mild → Severe       │
│                               │
├───────────────────────────────┤
│ AI Recommendation             │
│                               │
│ [ View Recommendation ]       │
│                               │
├───────────────────────────────┤
│ Expert Decision               │
│                               │
│ ○ AI Correct                  │
│ ○ AI Incorrect                │
│ ○ Need More Information       │
│                               │
│ Diagnosis                     │
│ [ Select ▾ ]                  │
│                               │
│ Severity                      │
│ [ Select ▾ ]                  │
│                               │
│ Notes                         │
│ [                         ]   │
│                               │
│ Farmer Message                │
│ [                         ]   │
│                               │
│ [ Save Draft ]                │
│ [ Submit Review ]             │
└───────────────────────────────┘
```

---

# 33. Strong UX Feature — AI vs Expert Comparison

I highly recommend adding this.

When the expert selects **AI Result Incorrect**, show:

```text
┌───────────────────────────────────────────────┐
│ AI vs Expert                                  │
├───────────────────────┬───────────────────────┤
│ AI                    │ Expert                │
├───────────────────────┼───────────────────────┤
│ Early Blight          │ Late Blight            │
│ Confidence: 61%       │ Confidence: —         │
│ Severity: Severe      │ Severity: Moderate    │
└───────────────────────┴───────────────────────┘
```

This makes the human-in-the-loop process extremely clear.

---

# 34. Strong UX Feature — "Why Review?"

At the top of the case:

```text
⚠ Why this case needs review

• AI confidence is 61%
• Disease severity is Severe
• Severity increased from Moderate
• Case requires expert validation
```

This is much better than simply saying:

```text
Critical
```

The expert immediately knows **why** the case is important.

---

# 35. Strong UX Feature — Evidence Summary

Add:

```text
Evidence Summary

✓ Crop identified
✓ Leaf detected
✓ Image quality acceptable
⚠ Disease confidence moderate
🔴 Severe severity
📈 Condition worsening
```

This gives the expert a 5-second overview before detailed inspection.

---

# 36. Final Recommended Screen

For your Smart Farming project, I would make the final desktop design roughly:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ ← Queue   Case #1042   🔴 CRITICAL   Pending      Assigned: You             │
├──────────────────────────────┬───────────────────────────────────────────────┤
│                              │ CASE INFORMATION                              │
│                              │ Farmer: Manthan                               │
│       CROP IMAGE             │ Farm: Patel Farm                              │
│                              │ Plot: Tomato A                                │
│     ┌──────────────────┐     │ Scan: 26 Aug 2026                             │
│     │                  │     │                                               │
│     │      IMAGE       │     │ AI DIAGNOSIS                                  │
│     │                  │     │ Tomato                                         │
│     │                  │     │ Early Blight                                  │
│     └──────────────────┘     │ Confidence: 61%                               │
│                              │ 🔴 Severe                                      │
│ [Original][Processed][Leaf] │                                               │
│                              │ WHY REVIEW?                                   │
│ 🔍 Zoom        ⛶ Fullscreen │ ⚠ Low confidence                              │
│                              │ 🔴 Severe condition                            │
│ IMAGE QUALITY                │ 📈 Condition worsening                         │
│ ✓ Sharp ✓ Bright ✓ Leaf     │                                               │
│                              ├───────────────────────────────────────────────┤
│ DIAGNOSIS HISTORY            │ EXPERT DECISION                               │
│                              │                                               │
│ Healthy → Mild → Moderate   │ ○ AI Result Correct                           │
│              → 🔴 Severe     │ ○ AI Result Incorrect                         │
│                              │ ○ Needs More Information                      │
│ AI RECOMMENDATION             │                                               │
│                              │ Diagnosis                                      │
│ [ View Recommendation ]      │ [ Select Diagnosis ▾ ]                       │
│                              │                                               │
│                              │ Severity                                       │
│                              │ [ Select Severity ▾ ]                        │
│                              │                                               │
│                              │ Expert Notes                                   │
│                              │ [                                           ] │
│                              │                                               │
│                              │ Farmer Message                                │
│                              │ [                                           ] │
│                              │                                               │
│                              │ [ Save Draft ] [ Submit Review ]              │
└──────────────────────────────┴───────────────────────────────────────────────┘
```

---

# 37. Most Important Design Principle

The expert should **never lose sight of what is AI-generated versus what is expert-verified**.

Use explicit labels everywhere:

```text
AI RESULT
Early Blight
61%

EXPERT RESULT
Not yet reviewed
```

After review:

```text
AI RESULT
Early Blight
61%

EXPERT VERIFIED RESULT ✓
Late Blight
Moderate
```

That distinction will make your Smart Farming system feel substantially more credible and professionally designed.

It also fits your existing pipeline well: **preprocessing → crop identification → disease classification → severity → pest analysis → recommendation → expert validation → final farmer-facing result**.


# Smart Farming — Admin Overview Screen UI/UX Specification

The **Admin Overview** should be different from both the Farmer Dashboard and Expert Dashboard.

Its purpose is to answer:

> **"What is happening across the entire Smart Farming platform, and is the system operating correctly?"**

The admin should primarily monitor **users, farms, scans, diagnoses, expert reviews, alerts, system health, and platform activity**.

---

# 1. Route

```text
/admin
```

Related admin routes:

```text
/admin/users
/admin/experts
/admin/farms
/admin/cases
/admin/alerts
/admin/analytics
/admin/system
```

The Overview is the admin's starting point.

---

# 2. Admin vs Expert vs Farmer

Keep these three interfaces clearly separated.

### Farmer

```text
My farm
My crops
My scans
My alerts
My recommendations
```

### Expert

```text
Review cases
Validate AI
Correct diagnoses
Expert feedback
```

### Admin

```text
Platform users
Platform activity
System health
Experts
Cases
AI pipeline
Platform-wide analytics
```

The admin should **not** be reviewing every diagnosis manually unless specifically assigned to an administrative workflow.

---

# 3. Desktop Layout

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming Admin                  🔔        👤 Admin ▾                 │
├────────────────┬────────────────────────────────────────────────────────────┤
│                │                                                            │
│ 📊 Overview    │  Platform Overview                                        │
│                │  Monitor platform activity and system health               │
│ 👥 Users       │                                                            │
│                │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│ 👨‍🌾 Experts    │  │ 1,284    │ │ 3,842    │ │ 9,641    │ │ 247      │     │
│                │  │ Users    │ │ Farms    │ │ Scans    │ │ Reviews  │     │
│ 🌾 Farms       │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│                │                                                            │
│ 📋 Cases       │  ┌──────────────────────────┐ ┌────────────────────────┐ │
│                │  │ Platform Activity        │ │ System Health          │ │
│ 🚨 Alerts      │  │                          │ │                        │ │
│                │  │        📈                │ │ API          ● Healthy │ │
│ 📈 Analytics   │  │     activity chart       │ │ AI Pipeline  ● Healthy │ │
│                │  │                          │ │ Database    ● Healthy │ │
│ ⚙ System      │  └──────────────────────────┘ └────────────────────────┘ │
│                │                                                            │
│                │  Review & Risk Overview                                   │
│                │  ┌────────────────────┐ ┌──────────────────────────────┐ │
│                │  │ Pending Reviews    │ │ Diagnosis Distribution        │ │
│                │  │                    │ │                              │ │
│                │  │ 24                 │ │ Healthy       42%            │ │
│                │  │ 8 High Risk        │ │ Disease       38%            │ │
│                │  │ 5 Critical         │ │ Pest          20%            │ │
│                │  └────────────────────┘ └──────────────────────────────┘ │
│                │                                                            │
│                │  Recent Platform Activity                                │
│                │  ┌────────────────────────────────────────────────────┐  │
│                │  │ User registered                         2 min ago   │  │
│                │  │ Expert completed review                  8 min ago   │  │
│                │  │ New farm created                        12 min ago   │  │
│                │  └────────────────────────────────────────────────────┘  │
└────────────────┴────────────────────────────────────────────────────────────┘
```

---

# 4. Admin Sidebar

Use:

```text
📊 Overview
👥 Users
👨‍🌾 Experts
🌾 Farms
📋 Cases
🚨 Alerts
📈 Analytics
⚙ System
```

Optional:

```text
📝 Audit Logs
```

I recommend adding Audit Logs eventually because an administrative platform should be able to answer:

> Who changed what, and when?

---

# 5. Header

Header:

```text
Platform Overview
```

Subtitle:

> Monitor platform activity, AI-assisted diagnoses, expert reviews, and system health.

Right side:

```text
🔔
Admin ▾
```

Optional:

```text
Last updated: 2 minutes ago
```

---

# 6. Global Date Filter

The admin overview should support:

```text
Today
7 Days
30 Days
90 Days
Custom
```

Example:

```text
Period: [ Last 30 Days ▾ ]
```

This filter should affect the dashboard metrics and charts.

---

# 7. KPI Cards

I recommend four primary cards.

## Total Users

```text
┌────────────────────┐
│ 👥 Total Users     │
│                    │
│ 1,284              │
│ ↑ 8.4%             │
│ vs previous period │
└────────────────────┘
```

---

## Total Farms

```text
┌────────────────────┐
│ 🌾 Total Farms     │
│                    │
│ 3,842              │
│ ↑ 5.2%             │
└────────────────────┘
```

---

## Total Scans

```text
┌────────────────────┐
│ 📷 Total Scans     │
│                    │
│ 9,641              │
│ ↑ 12.7%            │
└────────────────────┘
```

---

## Expert Reviews

```text
┌────────────────────┐
│ ✓ Expert Reviews   │
│                    │
│ 247                │
│ 24 Pending         │
└────────────────────┘
```

These numbers are examples for the UI only; your implementation should use actual backend data.

---

# 8. Secondary KPI Row

Below the main cards:

```text
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Active Users │ │ Active       │ │ High Risk    │ │ Critical     │
│              │ │ Experts      │ │ Cases        │ │ Cases        │
│ 842          │ │ 24           │ │ 8            │ │ 5            │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

---

# 9. Platform Activity Chart

This should be the main chart.

Title:

> **Platform Activity**

Display:

```text
Scans
Users
Reviews
```

Example:

```text
Activity
│
│                  ╭──╮
│              ╭───╯  ╰─╮
│         ╭────╯         ╰──
│     ╭───╯
│─────╯
└──────────────────────────────
 Mon Tue Wed Thu Fri Sat Sun
```

You could have tabs:

```text
[ Scans ] [ Users ] [ Reviews ]
```

Don't put too many lines on one chart.

---

# 10. Scan Activity

For your project, scan volume is an important metric.

```text
Scan Activity

Today
328 scans

This Week
2,184 scans

This Month
9,641 scans
```

Chart:

```text
Daily Scans
Mon   █████████
Tue   ███████████
Wed   ███████
Thu   █████████████
Fri   ██████████
Sat   ██████
Sun   ████████
```

---

# 11. Diagnosis Distribution

This is useful for understanding what the platform is seeing.

```text
Diagnosis Distribution

Healthy             42%
Disease Detected    38%
Pest Detected       20%
```

Visual:

```text
             ┌───────────────┐
             │               │
             │   DONUT       │
             │    CHART      │
             │               │
             └───────────────┘
```

You can then show:

```text
Healthy        4,049
Disease        3,662
Pest           1,930
```

Use actual database values.

---

# 12. Disease Distribution

Another useful admin metric:

```text
Top Detected Diseases

Early Blight       28%
Late Blight        19%
Leaf Spot          16%
Other              37%
```

This helps identify which conditions are appearing most frequently.

---

# 13. Crop Distribution

Show:

```text
Most Scanned Crops

Tomato
██████████████

Cotton
██████████

Potato
████████

Groundnut
██████
```

This connects directly to your current supported crop models.

---

# 14. Expert Review Overview

This should be prominent.

```text
Expert Review Status

Pending              24
In Review             7
Reviewed            216
Needs Information     5
```

Visual:

```text
Pending       ████
In Review     ██
Reviewed      █████████████████████
More Info     █
```

---

# 15. High-Risk Cases

Add a dedicated card:

```text
┌─────────────────────────────────────────┐
│ 🚨 High-Risk Cases                      │
│                                         │
│ 8 cases require attention               │
│                                         │
│ 🔴 5 Critical                           │
│ 🟠 3 High                               │
│                                         │
│ [ View High-Risk Cases ]                │
└─────────────────────────────────────────┘
```

Click:

```text
→ /admin/cases?priority=high
```

---

# 16. System Health

This is where the Admin Dashboard differs significantly from the Expert Dashboard.

```text
System Health

API
● Operational

Database
● Operational

AI Pipeline
● Operational

Recommendation Service
● Operational

Authentication
● Operational
```

Example:

```text
┌──────────────────────────────────────────┐
│ System Health                             │
├──────────────────────────────────────────┤
│ API                       ● Operational   │
│ Database                  ● Operational   │
│ Crop Model                ● Operational   │
│ Disease Model             ● Operational  │
│ Pest Model                ● Operational   │
│ Recommendation Engine     ● Operational   │
└──────────────────────────────────────────┘
```

---

# 17. AI Pipeline Health

Since your Smart Farming system has multiple stages, you can make this especially useful.

```text
AI Pipeline

Image Preprocessing       ● Healthy
Crop Identification       ● Healthy
Disease Classification    ● Healthy
Severity Estimation       ● Healthy
Pest Classification       ● Healthy
Recommendation Engine     ● Healthy
```

If something fails:

```text
Disease Classification    ⚠ Degraded
```

Clicking it:

```text
→ /admin/system
```

---

# 18. Recent Platform Activity

Use an activity feed:

```text
Recent Activity

● New farmer registered
  2 minutes ago

● Expert completed Case #1042
  8 minutes ago

● New farm created
  12 minutes ago

● 17 crop scans processed
  18 minutes ago

⚠ Recommendation service response delayed
  24 minutes ago
```

This makes the dashboard feel live.

---

# 19. User Overview

Small summary:

```text
Users

Total Users       1,284
Active Today        184
New This Week       62
New This Month     218
```

Potential chart:

```text
User Growth
│
│                       ╭──
│                  ╭────╯
│            ╭─────╯
│      ╭─────╯
│──────╯
└──────────────────────────
```

---

# 20. User Role Distribution

Useful for RBAC monitoring:

```text
User Roles

Farmers       1,240
Experts          38
Admins            6
```

Don't expose individual sensitive information on the overview.

---

# 21. Expert Overview

```text
Expert Activity

Total Experts          38
Active Experts         24
Pending Assignments     7
Reviews Today          31
```

And:

```text
Average Review Time
18 min
```

Only show this if your backend actually tracks review timestamps.

---

# 22. Expert Workload

This is a good operational feature.

```text
Expert Workload

Dr. Patel
████████████  12 cases

Dr. Shah
███████        7 cases

Dr. Mehta
████            4 cases
```

This lets an admin redistribute cases.

---

# 23. Geographic Overview

Since this is an India-focused farming platform, eventually you can include:

```text
Farm Distribution

Gujarat       1,240
Maharashtra     842
Rajasthan       431
Madhya Pradesh  382
Other           947
```

A map could later show:

```text
India
   ● Gujarat
        ● Maharashtra
   ● Rajasthan
```

For your initial frontend, I would use a **state distribution chart rather than a complex map**.

---

# 24. Alerts Overview

Admin should see platform-level alert statistics:

```text
Alerts

Critical       12
High           38
Medium         94
Low           212
```

And:

```text
Unresolved Alerts
47
```

Click:

```text
[ View Alerts ]
```

---

# 25. System Alerts

Separate agricultural alerts from technical system alerts.

### Agricultural

```text
🚨 Severe crop condition
```

### System

```text
⚠ Recommendation service degraded
```

The admin should be able to distinguish these immediately.

---

# 26. Quick Actions

At the top-right:

```text
[ + Add Expert ]
[ View Users ]
[ Review Cases ]
```

Maybe:

```text
More ▾
```

Don't put too many actions on the Overview screen.

---

# 27. Recommended Quick Actions

```text
Add Expert
Manage Users
Review High-Risk Cases
View System Health
View Audit Logs
```

---

# 28. Admin Dashboard Layout

My recommended final arrangement:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Platform Overview                                  [Last 30 Days ▾]         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│ │ Users    │ │ Farms    │ │ Scans    │ │ Reviews  │                       │
│ │ 1,284    │ │ 3,842    │ │ 9,641    │ │ 247      │                       │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘                       │
│                                                                              │
│ ┌──────────────────────────────────┐ ┌─────────────────────────────────┐  │
│ │ Platform Activity                │ │ System Health                   │  │
│ │                                  │ │                                 │  │
│ │           📈                     │ │ API                 ● Healthy   │  │
│ │                                  │ │ Database            ● Healthy   │  │
│ │                                  │ │ AI Pipeline         ● Healthy   │  │
│ │                                  │ │ Recommendation      ● Healthy   │  │
│ └──────────────────────────────────┘ └─────────────────────────────────┘  │
│                                                                              │
│ ┌──────────────────────────────────┐ ┌─────────────────────────────────┐  │
│ │ Diagnosis Distribution           │ │ Expert Review Status            │  │
│ │                                  │ │                                 │  │
│ │          ◯                       │ │ Pending          24             │  │
│ │       donut chart                │ │ In Review         7             │  │
│ │                                  │ │ Reviewed        216             │  │
│ └──────────────────────────────────┘ └─────────────────────────────────┘  │
│                                                                              │
│ ┌──────────────────────────────────┐ ┌─────────────────────────────────┐  │
│ │ 🚨 High-Risk Cases              │ │ Recent Activity                  │  │
│ │                                  │ │                                 │  │
│ │ Critical              5         │ │ User registered        2m ago   │  │
│ │ High                  3         │ │ Case reviewed           8m ago   │  │
│ │                                  │ │ Farm created           12m ago  │  │
│ │ [ View Cases ]                  │ │ Scan completed         18m ago  │  │
│ └──────────────────────────────────┘ └─────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

# 29. Mobile Admin Overview

Don't attempt to squeeze the desktop dashboard onto mobile.

Use:

```text
┌───────────────────────────────┐
│ 🌱 Admin              🔔      │
├───────────────────────────────┤
│ Platform Overview             │
│                               │
│ [ Last 30 Days ▾ ]            │
│                               │
│ ┌──────────┐ ┌──────────┐    │
│ │ Users    │ │ Farms    │    │
│ │ 1,284    │ │ 3,842    │    │
│ └──────────┘ └──────────┘    │
│                               │
│ ┌──────────┐ ┌──────────┐    │
│ │ Scans    │ │ Reviews  │    │
│ │ 9,641    │ │ 247      │    │
│ └──────────┘ └──────────┘    │
│                               │
│ System Health                │
│                               │
│ API                 ●        │
│ Database            ●        │
│ AI Pipeline         ●        │
│                               │
│ 🚨 High-Risk Cases            │
│                               │
│ Critical       5              │
│ High           3              │
│                               │
│ [ View Cases ]                │
│                               │
│ Recent Activity               │
│ ─────────────────────────     │
│ User registered      2m       │
│ Case reviewed        8m       │
│ Farm created        12m       │
└───────────────────────────────┘
```

Charts can become horizontally scrollable cards or be moved to `/admin/analytics`.

---

# 30. What NOT to Put on Overview

Keep the admin Overview focused.

Don't put:

```text
❌ Full user table
❌ Full farm table
❌ Full diagnosis table
❌ Full expert queue
❌ Detailed model metrics
❌ Individual farmer medical/personal information
❌ Huge audit log
```

Those belong in dedicated screens.

The Overview should answer:

```text
What is happening?
What needs attention?
Is the system healthy?
```

---

# 31. Admin Navigation Architecture

Your final admin portal can become:

```text
ADMIN PORTAL
│
├── 📊 Overview
│
├── 👥 Users
│   ├── All Users
│   └── User Detail
│
├── 👨‍🌾 Experts
│   ├── Expert List
│   ├── Expert Detail
│   └── Workload
│
├── 🌾 Farms
│   └── Farm Overview
│
├── 📋 Cases
│   ├── All Cases
│   ├── High Risk
│   └── Case Detail
│
├── 🚨 Alerts
│
├── 📈 Analytics
│
├── 📝 Audit Logs
│
└── ⚙ System
    ├── System Health
    ├── AI Services
    └── Configuration
```

---

# 32. Most Valuable Admin Feature for Your Project

I would make **System Health + AI Pipeline Monitoring** one of the defining features.

Your admin can see:

```text
AI PIPELINE HEALTH

Preprocessing             ✓
Crop Identification       ✓
Disease Classification    ✓
Severity Estimation       ✓
Pest Classification       ✓
Recommendation Engine     ⚠
```

Clicking Recommendation Engine:

```text
Recommendation Service

Status:
Degraded

Requests Today:
1,284

Successful:
1,247

Failed:
37

Average Response:
2.8 sec

Last Error:
26 Aug 2026, 15:42
```

This is particularly appropriate for your architecture because your application has multiple independent AI/service stages.

---

# 33. Recommended V1

For your current Smart Farming project, don't overbuild the admin dashboard.

### Must Have

```text
✓ Total users
✓ Total farms
✓ Total scans
✓ Expert reviews
✓ Pending reviews
✓ High-risk cases
✓ Platform activity
✓ Diagnosis distribution
✓ Recent activity
✓ System health
✓ AI pipeline health
```

### V2

```text
⭐ Geographic distribution
⭐ Expert workload
⭐ User growth analytics
⭐ Crop distribution
⭐ Disease distribution
⭐ Alert analytics
⭐ Audit logs
⭐ AI–Expert agreement metrics
```

### V3

```text
⭐ Advanced analytics
⭐ Model monitoring
⭐ Drift monitoring
⭐ Service latency monitoring
⭐ Automated incident alerts
⭐ Geographic heatmaps
```

---

# 34. Important Architecture Decision

Your three dashboards should now form a very clear hierarchy:

```text
                         SMART FARMING
                              │
              ┌───────────────┼───────────────┐
              │               │               │
           FARMER           EXPERT           ADMIN
              │               │               │
              ▼               ▼               ▼
        Personal Farm     Review Cases     Platform
        Management        AI Validation    Management
              │               │               │
              ▼               ▼               ▼
         Diagnosis        Expert Result    System Health
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                     FINAL FARMING GUIDANCE
```

So the **Admin Overview should not be another diagnosis dashboard**. It should be the **control tower of your entire Smart Farming platform**—showing platform usage, operational risk, expert workload, AI pipeline health, and anything requiring administrative attention.


# Smart Farming — Admin Prediction Monitoring Screen

The **Prediction Monitoring** screen should be the admin's dedicated control center for monitoring how the AI prediction pipeline is behaving across the platform.

For your project, this screen should focus on:

> **What is the AI predicting? How confident is it? How often is it wrong/uncertain? Which models are being used? Which predictions need expert attention?**

It should **not** become a data-science dashboard with dozens of model-training metrics. The admin is monitoring the deployed system, not training the models.

---

# 1. Route

```text
/admin/predictions
```

Optional detail route:

```text
/admin/predictions/:predictionId
```

---

# 2. Main Purpose

The admin should be able to monitor:

```text
Prediction Volume
        ↓
Prediction Results
        ↓
Confidence
        ↓
High-Risk / Low-Confidence Predictions
        ↓
Expert Validation
        ↓
AI vs Expert Agreement
        ↓
Model / Pipeline Health
```

---

# 3. Overall Desktop Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming Admin                         🔔        Admin ▾              │
├────────────────┬─────────────────────────────────────────────────────────────┤
│                │                                                             │
│ 📊 Overview    │ Prediction Monitoring                                      │
│                │ Monitor AI predictions across the platform                 │
│ 👥 Users       │                                                             │
│ 👨‍🌾 Experts    │ [Last 30 Days ▾] [All Crops ▾] [All Models ▾] [Filter ▾]  │
│                │                                                             │
│ 🌾 Farms       │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│                │ │ 9,641    │ │ 8,923    │ │ 718      │ │ 247      │       │
│ 📋 Cases       │ │Predictions│ │High Conf│ │Low Conf  │ │Reviewed  │       │
│                │ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│ 🚨 Alerts      │                                                             │
│                │ ┌──────────────────────────┐ ┌──────────────────────────┐ │
│ 📈 Analytics   │ │ Prediction Volume        │ │ Confidence Distribution  │ │
│                │ │                          │ │                          │ │
│ ⚙ System      │ │        📈                │ │       ███████             │ │
│                │ │                          │ │       █████████           │ │
│                │ └──────────────────────────┘ └──────────────────────────┘ │
│                │                                                             │
│                │ ┌──────────────────────────┐ ┌──────────────────────────┐ │
│                │ │ Model Performance        │ │ Review & Risk             │ │
│                │ │                          │ │                          │ │
│                │ │ Crop Identifier    ✓     │ │ Low Confidence     718   │ │
│                │ │ Disease Model      ✓     │ │ High Risk          86    │ │
│                │ │ Pest Model         ✓     │ │ Pending Review     24    │ │
│                │ └──────────────────────────┘ └──────────────────────────┘ │
│                │                                                             │
│                │ Recent Predictions                                          │
│                │ ┌────────────────────────────────────────────────────────┐ │
│                │ │ ID │ Crop │ Prediction │ Confidence │ Severity │ Status│ │
│                │ └────────────────────────────────────────────────────────┘ │
└────────────────┴─────────────────────────────────────────────────────────────┘
```

---

# 4. Header

Use:

```text
Prediction Monitoring
```

Subtitle:

> Monitor AI-generated crop, disease, pest, severity, and recommendation predictions.

Right side:

```text
[ Last 30 Days ▾ ]
```

Optional:

```text
Last updated: 2 min ago
```

---

# 5. Global Filters

Filters are extremely important on this screen.

Use:

```text
[ Date Range ▾ ]
[ Crop ▾ ]
[ Prediction Type ▾ ]
[ Confidence ▾ ]
[ Severity ▾ ]
[ Status ▾ ]
```

### Prediction Type

```text
All

Crop Identification
Disease Classification
Severity Estimation
Pest Classification
Recommendation
```

These correspond directly to your pipeline.

---

# 6. Primary KPI Cards

I recommend **four main cards**.

---

## Card 1 — Total Predictions

```text
┌─────────────────────────┐
│ 🧠 Total Predictions    │
│                         │
│ 9,641                   │
│ ↑ 12.7%                 │
│ vs previous period      │
└─────────────────────────┘
```

This counts prediction requests/results over the selected period.

---

## Card 2 — High Confidence

```text
┌─────────────────────────┐
│ ✓ High Confidence       │
│                         │
│ 8,923                   │
│ 92.5% of predictions    │
└─────────────────────────┘
```

Define the threshold consistently in your backend.

For example, if your system uses:

```text
≥ 75%
```

then the frontend should use the backend's classification rather than independently calculating it.

---

## Card 3 — Low Confidence

```text
┌─────────────────────────┐
│ ⚠ Low Confidence        │
│                         │
│ 718                     │
│ 7.5% of predictions     │
└─────────────────────────┘
```

Clicking this should take the admin to:

```text
/admin/predictions?confidence=low
```

---

## Card 4 — Expert Reviewed

```text
┌─────────────────────────┐
│ 👨‍🌾 Expert Reviewed      │
│                         │
│ 247                     │
│ 24 pending              │
└─────────────────────────┘
```

This is particularly valuable for your **human-in-the-loop architecture**.

---

# 7. Prediction Volume Chart

Main chart:

```text
Prediction Volume
```

Example:

```text
Predictions
│
│                         ╭──╮
│                    ╭────╯  ╰──╮
│             ╭──────╯           ╰─
│        ╭────╯
│   ╭────╯
│───╯
└──────────────────────────────────
  Mon Tue Wed Thu Fri Sat Sun
```

Tabs:

```text
[ All ] [ Crop ] [ Disease ] [ Pest ] [ Severity ]
```

Don't display every prediction type simultaneously if it makes the graph unreadable.

---

# 8. Prediction Type Distribution

Show how your AI pipeline is being used.

```text
Prediction Types

Crop Identification       32%
Disease Classification    38%
Pest Classification       18%
Severity Estimation       12%
```

Use a donut chart or horizontal bars.

---

# 9. Confidence Distribution

This is one of the **most important charts**.

```text
Confidence Distribution

90–100%   █████████████████████
80–90%    █████████████████
70–80%    ███████████
60–70%    █████
<60%      ██
```

Add labels:

```text
High confidence
Moderate confidence
Low confidence
```

This helps the admin quickly identify whether the AI is frequently uncertain.

---

# 10. Confidence Trend

Don't only show the current distribution.

Show whether confidence is changing over time.

```text
Average AI Confidence

100% ┤
 90% ┤          ╭───╮
 80% ┤────╮─────╯   ╰────
 70% ┤    ╰──
 60% ┤
     └────────────────────
       Week 1  Week 2  Week 3  Week 4
```

Potential metric:

```text
Current Average
84.6%

Previous Period
82.1%

↑ 2.5%
```

---

# 11. Model Monitoring

This should reflect **your actual AI architecture**.

```text
AI Models

┌──────────────────────────────────────────────┐
│ Crop Identifier                             │
│ EfficientNet-B0                             │
│ Status: ● Healthy                           │
│ Predictions: 3,184                          │
│ Avg Confidence: 94.2%                       │
│                                              │
│ [ View Details ]                             │
├──────────────────────────────────────────────┤
│ Disease Classifier                          │
│ EfficientNet                                │
│ Status: ● Healthy                           │
│ Predictions: 3,842                          │
│ Avg Confidence: 81.4%                       │
│                                              │
│ [ View Details ]                             │
├──────────────────────────────────────────────┤
│ Pest Classifier                              │
│ YOLO                                        │
│ Status: ● Healthy                           │
│ Predictions: 1,930                          │
│ Avg Confidence: 88.7%                       │
│                                              │
│ [ View Details ]                             │
└──────────────────────────────────────────────┘
```

Don't hardcode these model names in the frontend if your backend configuration may change.

---

# 12. Model Status

Use:

```text
● Healthy
⚠ Degraded
● Offline
```

But use different visual treatment for positive/negative states so accessibility isn't dependent on color.

Example:

```text
✓ Healthy
⚠ Degraded
✕ Offline
```

---

# 13. Pipeline Monitoring

Your project has a multi-stage pipeline, so show it explicitly.

```text
Prediction Pipeline

Upload
  ↓
Preprocessing
  ✓
  ↓
Crop Identification
  ✓
  ↓
Decision Routing
  ✓
  ↓
Disease Classification
  ✓
  ↓
Severity Estimation
  ✓
  ↓
Pest Classification
  ✓
  ↓
Recommendation
  ✓
```

At the top:

```text
Pipeline Status: ✓ Operational
```

---

# 14. Pipeline Failure Indicator

If one stage is failing:

```text
Prediction Pipeline

Upload                  ✓
Preprocessing            ✓
Crop Identification      ✓
Disease Classification   ⚠
Severity Estimation      —
Pest Classification      —
Recommendation           —
```

Then:

```text
⚠ Disease Classification is experiencing errors.

[ View System Health ]
```

This should link to:

```text
/admin/system
```

---

# 15. High-Risk Prediction Panel

This should be highly visible.

```text
┌─────────────────────────────────────────┐
│ 🚨 High-Risk Predictions                │
│                                         │
│ 86 predictions require attention        │
│                                         │
│ 🔴 Critical       18                    │
│ 🟠 High           68                    │
│                                         │
│ [ View High-Risk ]                      │
└─────────────────────────────────────────┘
```

---

# 16. Low-Confidence Predictions

Separate this from severity.

A prediction can be:

```text
High severity + low confidence
```

which deserves special attention.

Example:

```text
⚠ Low Confidence Predictions

Disease Classification
142

Pest Classification
83

Crop Identification
21

[ Review Predictions ]
```

---

# 17. AI vs Expert Agreement

This is one of the **best unique features** you can add to the admin dashboard.

Once experts review enough cases:

```text
AI vs Expert Agreement

Overall
87.4%

Crop Identification
94%

Disease Classification
82%

Severity
79%

Pest Classification
91%
```

Visual:

```text
Agreement

Crop        ███████████████████ 94%
Disease     ████████████████    82%
Severity    ███████████████     79%
Pest        ██████████████████  91%
```

This is much more useful to an admin than simply displaying model accuracy from training.

---

# 18. Expert Correction Rate

Add:

```text
Expert Correction Rate

12.6%
```

Meaning:

> Percentage of expert-reviewed predictions that were changed by experts.

Then:

```text
AI Accepted
87.4%

AI Corrected
12.6%
```

This should be based on your actual review records.

---

# 19. Prediction Outcome

Another useful metric:

```text
Prediction Outcome

AI Accepted          216
Expert Corrected      31
Needs More Info        8
```

This directly connects prediction monitoring to your Expert Review screen.

---

# 20. Recent Predictions Table

This should be the main detailed component near the bottom.

```text
Recent Predictions
```

Table:

| ID    | Crop   | Prediction   | Confidence | Severity | Review   | Status |
| ----- | ------ | ------------ | ---------: | -------- | -------- | ------ |
| #1042 | Tomato | Early Blight |        61% | Severe   | Pending  | ⚠      |
| #1041 | Cotton | Healthy      |        94% | —        | —        | ✓      |
| #1040 | Potato | Late Blight  |        82% | Moderate | Reviewed | ✓      |
| #1039 | Tomato | Aphid        |        73% | Moderate | Pending  | ⚠      |

---

# 21. Table Row Behavior

Clicking a prediction should open:

```text
/admin/predictions/1042
```

or a side drawer.

I recommend a **side drawer** for quick inspection.

---

# 22. Prediction Detail Drawer

When admin clicks:

```text
#1042
```

open:

```text
┌─────────────────────────────────────────┐
│ Prediction #1042                    ✕   │
├─────────────────────────────────────────┤
│                                         │
│ Crop                                     │
│ Tomato                                   │
│                                         │
│ Disease                                  │
│ Early Blight                             │
│                                         │
│ Confidence                               │
│ 61%                                      │
│                                         │
│ Severity                                 │
│ Severe                                   │
│                                         │
│ Model                                    │
│ Disease Classifier                       │
│                                         │
│ Created                                  │
│ 26 Aug 2026, 10:42 AM                    │
│                                         │
│ Review Status                            │
│ Pending Expert Review                    │
│                                         │
│ [ Open Full Case ]                       │
└─────────────────────────────────────────┘
```

---

# 23. Image Preview

For image-based predictions, show a small image.

```text
┌─────────────────────────┐
│                         │
│       Leaf Image        │
│                         │
└─────────────────────────┘

[ View Full Image ]
```

Admin shouldn't need to leave the prediction screen just to understand what prediction was generated.

---

# 24. AI Evidence

The admin can optionally see:

```text
Prediction Evidence

Image Quality
✓ Acceptable

Leaf Detection
✓ Detected

Crop
Tomato — 97%

Disease
Early Blight — 61%

Severity
Severe
```

This aligns directly with your existing pipeline.

---

# 25. Recommendation Monitoring

Because your pipeline includes an AI recommendation stage, monitor it separately.

```text
Recommendation Service

Requests
1,284

Successful
1,247

Failed
37

Success Rate
97.1%

Avg Response
2.8 sec
```

Status:

```text
✓ Operational
```

If recommendation generation fails:

```text
⚠ 37 recommendation failures

[ View Errors ]
```

---

# 26. Recommendation Quality — Important Distinction

Don't call this:

```text
Recommendation Accuracy
```

unless you have a valid ground-truth evaluation methodology.

Instead use:

```text
Recommendation Generation Status
Expert Acceptance Rate
Expert Edited Rate
```

For example:

```text
Expert Recommendation Feedback

Accepted        81%
Edited          14%
Rejected         5%
```

Only show this once you actually collect that feedback.

---

# 27. Filters + Search

At the top of the table:

```text
🔍 Search prediction ID, crop, disease...

[ Crop ▾ ]
[ Prediction Type ▾ ]
[ Confidence ▾ ]
[ Severity ▾ ]
[ Review Status ▾ ]
```

Useful confidence filter:

```text
All
<50%
50–70%
70–90%
>90%
```

---

# 28. Export

For an admin:

```text
[ Export CSV ]
```

Useful for:

* operational reports
* hackathon demonstrations
* audit
* analysis

But export should respect authorization and privacy rules.

---

# 29. Prediction Status

Use clear statuses:

```text
✓ Processed
⚠ Low Confidence
🔍 Pending Review
✓ Expert Verified
✎ Expert Corrected
⚠ Failed
```

Example:

```text
#1042
⚠ Low Confidence
🔍 Pending Review
```

---

# 30. Empty State

If no predictions exist:

```text
┌─────────────────────────────────────┐
│                                     │
│             🧠                      │
│                                     │
│      No predictions found           │
│                                     │
│ Try changing your filters or        │
│ date range.                         │
│                                     │
│ [ Clear Filters ]                   │
└─────────────────────────────────────┘
```

---

# 31. Loading State

Use skeletons instead of a blank screen.

```text
┌──────────────┐
│ ▓▓▓▓▓▓▓▓▓▓   │
│ ▓▓▓▓▓▓       │
│ ▓▓▓▓▓▓▓▓     │
└──────────────┘
```

For charts:

```text
████████████████████
████████████
████████████████
```

---

# 32. Error State

If monitoring data cannot be loaded:

```text
⚠ Unable to load prediction monitoring data.

The prediction service may be temporarily
unavailable.

[ Retry ]
```

Don't show fake `0` values when an API failed.

---

# 33. Recommended Desktop Screen Structure

Your final screen should roughly be:

```text
PREDICTION MONITORING
│
├── Global Filters
│
├── KPI Cards
│   ├── Total Predictions
│   ├── High Confidence
│   ├── Low Confidence
│   └── Expert Reviewed
│
├── Prediction Volume
│
├── Confidence Distribution
│
├── Prediction Type Distribution
│
├── Model Monitoring
│
├── Pipeline Health
│
├── Risk & Review
│   ├── High Risk
│   ├── Low Confidence
│   └── Pending Review
│
├── AI vs Expert Agreement
│
├── Recent Predictions
│
└── Prediction Detail Drawer
```

---

# 34. The Most Important Part for Your Project

Because your architecture already has:

```text
Preprocessing
      ↓
Crop Identification
      ↓
Decision Routing
      ↓
Disease Classification
      ↓
Severity
      ↓
Pest Classification
      ↓
Recommendation
      ↓
Expert Review
```

I would make **Prediction Monitoring** visually revolve around this pipeline.

A strong centerpiece would be:

```text
                 PREDICTION PIPELINE

       ┌──────────────┐
       │ Image Upload │
       └──────┬───────┘
              ↓
       ┌──────────────┐
       │ Preprocessing│ ✓
       └──────┬───────┘
              ↓
       ┌──────────────┐
       │ Crop ID      │ ✓ 94.2%
       └──────┬───────┘
              ↓
       ┌──────────────┐
       │ Disease      │ ✓ 81.4%
       └──────┬───────┘
              ↓
       ┌──────────────┐
       │ Severity     │ ✓
       └──────┬───────┘
              ↓
       ┌──────────────┐
       │ Pest         │ ✓ 88.7%
       └──────┬───────┘
              ↓
       ┌──────────────┐
       │ Recommendation│ ✓
       └──────┬───────┘
              ↓
       ┌──────────────┐
       │ Expert Review │
       └──────────────┘
```

This makes it immediately obvious to an admin **where a prediction came from, where it is currently sitting, and whether human validation is required**.

---

# 35. V1 vs V2

### V1 — Build these now

```text
✓ Total predictions
✓ Prediction volume
✓ Prediction type
✓ Confidence distribution
✓ Low-confidence predictions
✓ High-risk predictions
✓ Model status
✓ Pipeline status
✓ Recent prediction table
✓ Prediction detail drawer
✓ Expert review status
```

### V2 — Add after the core system works

```text
⭐ AI vs Expert agreement
⭐ Expert correction rate
⭐ Confidence trend
⭐ Model-specific monitoring
⭐ Recommendation acceptance/edit rate
⭐ Prediction failure rate
⭐ Geographic prediction distribution
```

### V3 — Advanced

```text
⭐ Model drift detection
⭐ Confidence calibration
⭐ Per-class performance
⭐ False-positive/false-negative monitoring
⭐ Data distribution monitoring
⭐ Automated model alerts
```

For your current hackathon project, **V1 + AI-vs-Expert agreement** would give the screen a strong balance between being technically impressive and actually useful to an administrator.


# Smart Farming — Admin Feedback Screen UI/UX Specification

The **Feedback screen** should be the admin's central place for understanding what farmers and experts think about the Smart Farming platform and, more importantly, **which parts of the system need improvement**.

For your project, I would design it around:

> **Feedback → Categorization → Sentiment → Issue Detection → AI/Expert Improvement → Resolution**

This screen should not just be a list of comments. It should turn feedback into **actionable product and system insights**.

---

# 1. Route

```text
/admin/feedback
```

Feedback detail:

```text
/admin/feedback/:feedbackId
```

---

# 2. Main Objectives

Admin should be able to answer:

```text
How much feedback are we receiving?
        ↓
Who is giving it?
        ↓
What are they complaining about?
        ↓
Are they satisfied?
        ↓
Are problems related to AI, UI, recommendations, or experts?
        ↓
Which issues are most important?
        ↓
Have those issues been resolved?
```

---

# 3. Desktop Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming Admin                         🔔        Admin ▾              │
├────────────────┬─────────────────────────────────────────────────────────────┤
│                │                                                             │
│ 📊 Overview    │ Feedback                                                   │
│                │ Monitor farmer and expert feedback                         │
│ 👥 Users       │                                                             │
│ 👨‍🌾 Experts    │ [Last 30 Days ▾] [All Users ▾] [Category ▾] [Status ▾]   │
│                │                                                             │
│ 🌾 Farms       │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│                │ │ 428      │ │ 82%      │ │ 37       │ │ 14       │       │
│ 📋 Cases       │ │ Feedback │ │ Positive │ │ Issues   │ │ Unresolved│      │
│                │ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│ 🚨 Alerts      │                                                             │
│                │ ┌──────────────────────────┐ ┌──────────────────────────┐ │
│ 📈 Analytics   │ │ Feedback Trend           │ │ Sentiment Distribution   │ │
│                │ │                          │ │                          │ │
│ ⚙ System      │ │        📈                │ │ Positive       82%       │ │
│                │ │                          │ │ Neutral        11%       │ │
│ 💬 Feedback    │ │                          │ │ Negative        7%       │ │
│                │ └──────────────────────────┘ └──────────────────────────┘ │
│                │                                                             │
│                │ ┌──────────────────────────────────────────────────────┐ │
│                │ │ Feedback Categories                                  │ │
│                │ │                                                      │ │
│                │ │ AI Diagnosis        ███████████████  124             │ │
│                │ │ Recommendation      ███████████      96              │ │
│                │ │ UI / UX             █████████         78              │ │
│                │ │ Expert Review       ██████            52              │ │
│                │ │ Other               █████             41              │ │
│                │ └──────────────────────────────────────────────────────┘ │
│                                                                              │
│                │ Recent Feedback                                            │
│                │ ┌────────────────────────────────────────────────────────┐ │
│                │ │ User │ Category │ Feedback │ Sentiment │ Status       │ │
│                │ └────────────────────────────────────────────────────────┘ │
└────────────────┴─────────────────────────────────────────────────────────────┘
```

---

# 4. Header

Use:

```text
Feedback
```

Subtitle:

> Review farmer and expert feedback, identify recurring problems, and track resolution.

Right side:

```text
[ Last 30 Days ▾ ]
[ Export ▾ ]
```

---

# 5. Primary KPI Cards

I recommend four.

## Total Feedback

```text
┌─────────────────────────┐
│ 💬 Total Feedback       │
│                         │
│ 428                     │
│ ↑ 14.2%                 │
│ vs previous period      │
└─────────────────────────┘
```

---

## Positive Feedback

```text
┌─────────────────────────┐
│ 😊 Positive             │
│                         │
│ 82%                     │
│ 351 responses           │
└─────────────────────────┘
```

---

## Issues Reported

```text
┌─────────────────────────┐
│ ⚠ Issues Reported       │
│                         │
│ 37                      │
│ 8.6% of feedback        │
└─────────────────────────┘
```

---

## Unresolved

```text
┌─────────────────────────┐
│ 🔴 Unresolved           │
│                         │
│ 14                      │
│ 5 high priority         │
└─────────────────────────┘
```

---

# 6. Feedback Trend

Show how much feedback is being received over time.

```text
Feedback Volume
│
│                         ╭──╮
│                  ╭──────╯  ╰─
│            ╭─────╯
│       ╭────╯
│  ╭────╯
│──╯
└──────────────────────────────
 Mon Tue Wed Thu Fri Sat Sun
```

Tabs:

```text
[ Feedback ] [ Issues ] [ Complaints ]
```

---

# 7. Sentiment Distribution

If you implement sentiment classification, show:

```text
Sentiment

Positive       82%
Neutral        11%
Negative        7%
```

A donut chart works well here.

However, if sentiment analysis is **not yet implemented in your backend**, don't fake this metric. In that case, use manually assigned feedback types/statuses instead.

---

# 8. Feedback Categories

This is one of the most useful sections for your project.

Recommended categories:

```text
AI Diagnosis
Recommendation
Crop Identification
Pest Detection
Severity Assessment
Expert Review
Image Upload
Dashboard
Mobile / UI
Performance
Other
```

Example:

```text
Feedback Categories

AI Diagnosis
████████████████ 124

Recommendation
████████████     96

UI / UX
██████████       78

Expert Review
██████           52

Image Upload
████             37

Other
████             41
```

---

# 9. Smart Farming-Specific Feedback Categories

Since your application is agriculture-focused, I would add specific categories instead of using only generic categories.

```text
🌱 Crop Detection
🦠 Disease Detection
🐛 Pest Detection
📊 Severity
💡 Recommendation
👨‍🌾 Expert Review
📷 Image Upload
🌾 Farm Management
🚨 Alerts
🌐 General Platform
```

This makes the feedback analytics much more useful.

---

# 10. Feedback Source

Show who submitted the feedback.

```text
Feedback Source

Farmers       364
Experts        52
Admins          8
```

Or:

```text
Farmers       ███████████████████
Experts       ███
Admins        █
```

---

# 11. Feedback Type

Separate sentiment from issue type.

```text
Feedback Type

Suggestion
██████████████

Bug Report
████████

Complaint
██████

Praise
██████████

Question
████
```

This is much more actionable than sentiment alone.

---

# 12. Priority Distribution

Use:

```text
Priority

🔴 Critical      3
🟠 High          11
🟡 Medium        19
🟢 Low           52
```

This allows admins to prioritize actual issues.

---

# 13. Recent Feedback Table

This is the main detailed component.

```text
Recent Feedback
```

Recommended columns:

| ID    | User   | Type       | Category       | Feedback                   | Sentiment | Priority | Status    |
| ----- | ------ | ---------- | -------------- | -------------------------- | --------- | -------- | --------- |
| #F428 | Farmer | Complaint  | Recommendation | Recommendation was unclear | Negative  | High     | Open      |
| #F427 | Farmer | Suggestion | Dashboard      | Add Gujarati language      | Neutral   | Medium   | Reviewing |
| #F426 | Expert | Issue      | Disease AI     | Low confidence on cases    | Negative  | High     | Open      |
| #F425 | Farmer | Praise     | Diagnosis      | Very useful diagnosis      | Positive  | Low      | Resolved  |

---

# 14. Table Actions

At the end of each row:

```text
⋮
```

Menu:

```text
View Feedback
Mark as Reviewing
Change Priority
Assign
Resolve
Delete
```

Don't immediately delete feedback; consider retaining it for audit/history.

---

# 15. Search

At the top of the table:

```text
🔍 Search feedback...
```

Search should support:

```text
Feedback ID
User
Crop
Disease
Category
Feedback text
```

Example:

```text
🔍 "recommendation"
```

---

# 16. Filters

Use:

```text
[ Date ▾ ]
[ Source ▾ ]
[ Category ▾ ]
[ Type ▾ ]
[ Sentiment ▾ ]
[ Priority ▾ ]
[ Status ▾ ]
```

Example status:

```text
All
Open
Reviewing
Resolved
Rejected
```

---

# 17. Feedback Detail Drawer

Clicking a feedback row should open a right-side drawer.

```text
┌──────────────────────────────────────────────┐
│ Feedback #F428                         ✕    │
├──────────────────────────────────────────────┤
│                                              │
│ Farmer Feedback                              │
│                                              │
│ User                                         │
│ Farmer #284                                  │
│                                              │
│ Submitted                                    │
│ 26 Aug 2026, 10:42 AM                        │
│                                              │
│ Category                                     │
│ Recommendation                              │
│                                              │
│ Type                                         │
│ Complaint                                    │
│                                              │
│ Priority                                     │
│ 🔴 High                                      │
│                                              │
│ Feedback                                     │
│ "The recommendation was difficult to         │
│ understand and did not explain what           │
│ I should do next."                            │
│                                              │
│ Sentiment                                    │
│ Negative                                     │
│                                              │
│ Related Case                                 │
│ #1042                                        │
│                                              │
│ Status                                       │
│ Open                                         │
│                                              │
│ [ Assign ] [ Mark Reviewing ]                │
│ [ Resolve ]                                  │
└──────────────────────────────────────────────┘
```

---

# 18. Related Case

This is especially important for your system.

If the farmer gives feedback after a diagnosis:

```text
Related Case

Case #1042
Tomato
Early Blight
61% confidence
Severe

[ Open Case ]
```

This lets the admin understand the context behind the feedback.

---

# 19. Related Prediction

For AI-related feedback:

```text
Related Prediction

Prediction #1042

AI:
Early Blight

Confidence:
61%

Expert:
Pending

[ View Prediction ]
```

This creates a strong connection:

```text
Feedback
   ↓
Prediction
   ↓
Expert Review
```

---

# 20. Admin Response

For feedback that requires communication, provide:

```text
Admin Response

[ Write response.................................... ]

☐ Send notification to user

[ Send Response ]
```

Example:

> Thank you for your feedback. We have forwarded this issue to our agricultural expert team.

Don't automatically send responses without explicit admin action.

---

# 21. Internal Notes

Separate internal notes from the user-visible response.

```text
Internal Notes

[................................................]

Only admins can see this.

[ Add Note ]
```

This is similar to the distinction between **Expert Notes** and **Farmer Message** in your expert review screen.

---

# 22. Feedback Status Lifecycle

Use:

```text
Open
  ↓
Reviewing
  ↓
Action Required
  ↓
Resolved
```

Alternative:

```text
Open
  ↓
Rejected
```

For example:

```text
🔴 Open
🟡 Reviewing
🟠 Action Required
🟢 Resolved
⚪ Rejected
```

---

# 23. Feedback Resolution

When admin clicks **Resolve**:

```text
┌───────────────────────────────────────────┐
│ Resolve Feedback                          │
├───────────────────────────────────────────┤
│                                           │
│ Resolution Type                           │
│ [ Select ▾ ]                              │
│                                           │
│ Bug Fixed                                  │
│ Feature Added                              │
│ Model Issue Investigated                   │
│ User Educated                              │
│ Duplicate                                  │
│ No Action Required                         │
│                                           │
│ Resolution Notes                           │
│ [.......................................] │
│                                           │
│ [ Cancel ]          [ Mark Resolved ]     │
└───────────────────────────────────────────┘
```

---

# 24. Recurring Issues

This would make your admin screen significantly more intelligent.

Add:

```text
Recurring Issues
```

Example:

```text
Top Recurring Issues

1. Recommendation unclear
   24 reports

2. Disease prediction uncertain
   18 reports

3. Image upload problems
   13 reports

4. Gujarati language requested
   11 reports

5. Slow prediction processing
    9 reports
```

This helps the admin identify **systemic problems rather than individual complaints**.

---

# 25. Feedback → Product Improvement

A particularly strong feature for your project:

```text
Feedback Insights

💡 11 farmers requested Gujarati support

⚠ 18 users reported uncertain disease predictions

📷 13 users experienced image upload issues

💬 24 users found recommendations unclear
```

Then:

```text
[ Create Improvement Task ]
```

This turns feedback into an actual development workflow.

---

# 26. AI-Related Feedback

Because your project is AI-heavy, create a dedicated section:

```text
AI Feedback

Diagnosis
     124 feedback

Recommendation
      96 feedback

Pest Detection
      42 feedback

Severity
      31 feedback
```

Then:

```text
AI Feedback Outcome

Accepted AI result       78%
Questioned result        14%
Reported incorrect        8%
```

Only calculate these if you actually have the corresponding data.

---

# 27. Expert Feedback

Your experts can also submit feedback about the AI.

Example:

```text
Expert Feedback

AI diagnosis frequently uncertain
        ↓
Disease Classifier
        ↓
Cases affected: 18
        ↓
Priority: High
```

This is extremely useful because experts are effectively providing **human-in-the-loop system feedback**.

---

# 28. Farmer Satisfaction

If you add a simple rating after a diagnosis:

```text
Was this diagnosis helpful?

⭐ ⭐ ⭐ ⭐ ☆
```

Then admin can see:

```text
Farmer Satisfaction

Average Rating

4.3 / 5

★★★★★
```

And:

```text
5★    48%
4★    31%
3★    12%
2★     6%
1★     3%
```

This would be a strong addition to your project.

---

# 29. Post-Diagnosis Feedback

I recommend collecting feedback immediately after the farmer sees a result.

Example on the Farmer side:

```text
Was this diagnosis helpful?

        👍 Yes     👎 No

[ Tell us more ]
```

If they choose No:

```text
What was the problem?

○ Diagnosis seems incorrect
○ Recommendation was unclear
○ Image processing failed
○ Result took too long
○ Something else
```

That structured information will make your Admin Feedback screen much more useful.

---

# 30. Feedback Analytics

At the bottom:

```text
Feedback Analytics
```

Potential metrics:

```text
Average Satisfaction
4.3 / 5

Resolution Rate
86%

Average Resolution Time
18 hours

Negative Feedback
7%

Repeat Issue Rate
12%
```

Again, only display metrics that your backend actually tracks.

---

# 31. Mobile Layout

On mobile, prioritize:

```text
┌───────────────────────────────┐
│ 💬 Feedback             🔔    │
├───────────────────────────────┤
│                               │
│ [ Last 30 Days ▾ ]            │
│                               │
│ ┌──────────┐ ┌──────────┐    │
│ │ Feedback │ │ Positive │    │
│ │ 428      │ │ 82%      │    │
│ └──────────┘ └──────────┘    │
│                               │
│ ┌──────────┐ ┌──────────┐    │
│ │ Issues   │ │ Unresolved│   │
│ │ 37       │ │ 14       │    │
│ └──────────┘ └──────────┘    │
│                               │
│ Sentiment                     │
│                               │
│ Positive       ████████       │
│ Neutral        ██             │
│ Negative       █              │
│                               │
│ Categories                    │
│                               │
│ AI Diagnosis     124          │
│ Recommendation    96          │
│ UI / UX           78          │
│                               │
│ Recent Feedback               │
│ ─────────────────────────     │
│ Recommendation Issue         │
│ Negative • High              │
│ 2 min ago                    │
│                               │
│ AI Diagnosis Issue           │
│ Negative • Medium            │
│ 8 min ago                    │
└───────────────────────────────┘
```

---

# 32. Recommended Screen Structure

Your final implementation should be:

```text
ADMIN FEEDBACK
│
├── Header
│
├── Global Filters
│
├── KPI Cards
│   ├── Total Feedback
│   ├── Positive
│   ├── Issues
│   └── Unresolved
│
├── Feedback Trend
│
├── Sentiment Distribution
│
├── Feedback Categories
│
├── Feedback Sources
│
├── Priority Distribution
│
├── Recurring Issues
│
├── AI Feedback
│
├── Recent Feedback Table
│
└── Feedback Detail Drawer
    ├── Feedback
    ├── User
    ├── Related Case
    ├── Related Prediction
    ├── Admin Response
    ├── Internal Notes
    └── Resolution
```

---

# 33. What I Recommend for Your V1

Don't implement every feature immediately.

### Must Have

```text
✓ Feedback list
✓ Search
✓ Filters
✓ Feedback categories
✓ Feedback type
✓ Priority
✓ Status
✓ Related case
✓ Feedback detail
✓ Resolve feedback
✓ Admin notes
✓ Recent feedback
```

### Strong additions

```text
⭐ Sentiment
⭐ Feedback trend
⭐ Recurring issues
⭐ Farmer satisfaction rating
⭐ AI-related feedback analytics
⭐ Expert feedback
```

### Advanced

```text
⭐ Automatic issue clustering
⭐ AI-generated feedback summaries
⭐ Feedback → development task
⭐ Resolution-time analytics
⭐ Repeat-user issue detection
```

---

# 34. One Feature I Strongly Recommend for Your Smart Farming Project

Make **AI Feedback → Prediction → Expert Review** traceable.

For example:

```text
Farmer Feedback
      │
      │
      ▼
┌──────────────────────┐
│ Feedback #F428       │
│ "Diagnosis seems    │
│ incorrect."          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Prediction #1042     │
│ Tomato               │
│ Early Blight         │
│ Confidence: 61%      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Expert Review        │
│ Pending              │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Final Result         │
│ Expert corrected     │
│ diagnosis            │
└──────────────────────┘
```

That gives your admin a complete **feedback-to-AI-quality loop**, which is much more impressive and useful than a conventional "customer feedback" page.

It also complements the **Prediction Monitoring** screen you just defined: Prediction Monitoring tells the admin **what the AI is doing**, while Feedback tells them **how users and experts perceive those results and where the system needs improvement**.


# Smart Farming — Admin Model Performance Screen UI/UX Specification

For your Smart Farming project, the **Model Performance** screen should answer a different question from the Prediction Monitoring screen:

> **Prediction Monitoring:** What is the AI doing in production?
> **Model Performance:** How well are the individual AI models performing, based on available evaluation/validation data?

This screen should focus on your actual AI components:

```text
Crop Identifier
      ↓
Disease Classifiers
      ↓
Severity Estimator
      ↓
Pest Classifier
      ↓
Recommendation Model
```

I would make this one of the most technically impressive admin screens in your project.

---

# 1. Route

```text
/admin/model-performance
```

Optional model detail:

```text
/admin/model-performance/:modelId
```

---

# 2. Main Screen

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming Admin                                      Admin ▾          │
├────────────────┬─────────────────────────────────────────────────────────────┤
│                │                                                             │
│ 📊 Overview    │ Model Performance                                          │
│ 👥 Users       │ Monitor deployed AI model performance and reliability      │
│ 👨‍🌾 Experts    │                                                             │
│ 🌾 Farms       │ [All Models ▾] [Model Type ▾] [Version ▾] [Period ▾]       │
│ 📋 Cases       │                                                             │
│ 🚨 Alerts      │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│ 📈 Analytics   │ │ 94.2%    │ │ 91.8%    │ │ 96.6%    │ │ 87.4%    │       │
│ 🧠 Predictions │ │ Crop     │ │ Disease  │ │ Pest     │ │ Expert   │       │
│ 💬 Feedback    │ │ Accuracy │ │ Accuracy │ │ F1       │ │ Agreement│       │
│ ⚙ System       │ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                │                                                             │
│                │ ┌──────────────────────────┐ ┌──────────────────────────┐ │
│                │ │ Model Comparison         │ │ Performance Trend        │ │
│                │ │                          │ │                          │ │
│                │ │ Crop       █████████ 94% │ │          📈              │ │
│                │ │ Disease    ████████  91% │ │                          │ │
│                │ │ Pest       █████████ 97% │ │                          │ │
│                │ └──────────────────────────┘ └──────────────────────────┘ │
│                │                                                             │
│                │ Model Registry                                             │
│                │ ┌────────────────────────────────────────────────────────┐ │
│                │ │ Model │ Version │ Metric │ Status │ Updated │ Action   │ │
│                │ └────────────────────────────────────────────────────────┘ │
└────────────────┴─────────────────────────────────────────────────────────────┘
```

---

# 3. Header

### Title

```text
Model Performance
```

### Subtitle

> Monitor the performance, reliability, and validation status of deployed Smart Farming AI models.

Right side:

```text
[ Export Report ]
```

and:

```text
Last updated: 2 min ago
```

---

# 4. Important Design Principle

Do **not** mix these three concepts:

### Training Performance

```text
Accuracy
Precision
Recall
F1
Loss
```

### Production Performance

```text
Prediction volume
Confidence
Latency
Failures
```

### Human Validation

```text
Expert agreement
Expert correction
Farmer feedback
```

Your frontend should visually separate them.

---

# 5. Model Selector

At the top:

```text
Model:

[ All Models ▾ ]
```

Options:

```text
All Models

Crop Identifier
Disease Classifier
Pest Classifier
Severity Estimator
Recommendation Model
```

For disease classification, because your architecture uses crop-specific models, you can further show:

```text
Disease Models
├── Tomato
├── Potato
└── Cotton
```

This is particularly relevant to your current project structure.

---

# 6. Primary KPI Cards

I recommend four cards.

---

## 6.1 Crop Model

```text
┌──────────────────────────┐
│ 🌱 Crop Identifier       │
│                          │
│ 94.2%                    │
│ Accuracy                 │
│                          │
│ ✓ Healthy                │
└──────────────────────────┘
```

Your actual backend evaluation result should populate this.

---

## 6.2 Disease Model

```text
┌──────────────────────────┐
│ 🦠 Disease Classifier    │
│                          │
│ 91.8%                    │
│ F1 Score                 │
│                          │
│ ✓ Healthy                │
└──────────────────────────┘
```

For your crop-specific disease models, this could become:

```text
Tomato       91.8%
Potato       89.7%
Cotton       93.1%
```

---

## 6.3 Pest Model

```text
┌──────────────────────────┐
│ 🐛 Pest Classifier       │
│                          │
│ 96.59%                   │
│ Macro F1                 │
│                          │
│ ✓ Healthy                │
└──────────────────────────┘
```

This is particularly appropriate for your existing pest classifier because its evaluation was based on macro-F1.

---

## 6.4 Human Agreement

```text
┌──────────────────────────┐
│ 👨‍🌾 Expert Agreement     │
│                          │
│ 87.4%                    │
│ AI / Expert Agreement    │
│                          │
│ ↑ 3.2%                   │
└──────────────────────────┘
```

Only show this once your system has enough expert-review data.

---

# 7. Model Comparison

This should be the main visual component.

```text
Model Performance

Crop Identifier
███████████████████ 94.2%

Disease Classifier
██████████████████  91.8%

Pest Classifier
████████████████████ 96.6%

Severity Estimator
████████████████     88.4%
```

But don't compare incompatible metrics directly.

For example, don't put:

```text
Crop Accuracy = 94%
Pest F1 = 96%
Severity MAE = 8%
```

into one "performance" ranking.

Instead, display the **metric name beside every value**.

---

# 8. Model Performance Table

This should be the core component.

| Model           | Type           | Version | Primary Metric |  Value | Status    | Last Evaluated |
| --------------- | -------------- | ------- | -------------- | -----: | --------- | -------------- |
| Crop Identifier | Classification | v1      | Accuracy       |  94.2% | ✓ Healthy | 26 Aug         |
| Tomato Disease  | Classification | v1      | Macro F1       |  91.8% | ✓ Healthy | 25 Aug         |
| Potato Disease  | Classification | v1      | Macro F1       |  89.7% | ✓ Healthy | 25 Aug         |
| Cotton Disease  | Classification | v1      | Macro F1       |  93.1% | ✓ Healthy | 25 Aug         |
| Pest Classifier | Classification | v1      | Macro F1       | 96.59% | ✓ Healthy | 26 Aug         |
| Severity        | Estimation     | v1      | MAE            |   8.4% | ✓ Healthy | 24 Aug         |

The exact numbers above are illustrative except where they correspond to your existing recorded evaluation.

---

# 9. Model Status

Use:

```text
✓ Healthy
⚠ Needs Attention
✕ Failed
○ Not Evaluated
```

Example:

```text
Pest Classifier
✓ Healthy

Disease Model — Potato
⚠ Needs Attention

Recommendation Model
○ Not Evaluated
```

This is important because not every model necessarily has the same evaluation methodology.

---

# 10. Model Detail Drawer

Clicking a model should open a drawer.

Example:

```text
┌──────────────────────────────────────────────┐
│ Pest Classifier                         ✕   │
├──────────────────────────────────────────────┤
│                                              │
│ Model                                         │
│ YOLO Pest Classifier                         │
│                                              │
│ Version                                       │
│ v1                                            │
│                                              │
│ Classes                                       │
│ 4                                             │
│                                              │
│ Primary Metric                                │
│ Macro F1                                      │
│                                              │
│ Score                                         │
│ 96.59%                                        │
│                                              │
│ Status                                        │
│ ✓ Healthy                                     │
│                                              │
│ [ View Detailed Metrics ]                    │
└──────────────────────────────────────────────┘
```

---

# 11. Detailed Metrics

When opening a model:

```text
Performance Metrics

Accuracy
94.2%

Precision
92.8%

Recall
91.4%

F1 Score
92.1%
```

But show only metrics actually calculated for that model.

For example, if your evaluation pipeline only produces macro-F1 for the pest classifier, don't invent precision/recall values.

---

# 12. Confusion Matrix

This is one of the most valuable components for classification models.

For example, Pest Classifier:

```text
Confusion Matrix

              Predicted
              Aphid  Army  Miner  Mite

Aphid          98      1      0     1
Army            2     96      1     1
Miner           0      1     97     2
Mite            1      0      2    97
```

Visual heatmap:

```text
              Predicted
           A    AW    LM    SM

Actual A   ███   ░     ░     ░
       AW  ░    ███    ░     ░
       LM  ░     ░    ███    ░
       SM  ░     ░     ░    ███
```

For your admin, this reveals **which classes the model confuses**.

---

# 13. Per-Class Performance

For your pest model:

```text
Per-Class Performance

Aphid
Precision  97%
Recall     96%
F1         96.5%

Army Worm
Precision  96%
Recall     95%
F1         95.5%

Leaf Miner
Precision  97%
Recall     98%
F1         97.5%

Spider Mite
Precision  96%
Recall     97%
F1         96.5%
```

Again, use actual evaluation results from your backend.

---

# 14. Disease Model Comparison

Because you have crop-specific disease models, give them their own section.

```text
Disease Model Performance

Tomato
██████████████████  91.8%

Potato
████████████████    89.7%

Cotton
███████████████████ 93.1%
```

Then:

```text
[ Tomato ] [ Potato ] [ Cotton ]
```

Selecting a crop updates the detailed metrics.

---

# 15. Crop Identifier Performance

Your crop identifier has:

```text
Cotton
Groundnut
Pepper Bell
Potato
Tomato
```

Show per-class performance:

```text
Crop Identification

Cotton        95%
Groundnut     93%
Pepper Bell   91%
Potato        96%
Tomato        95%
```

This is more informative than displaying only:

```text
Overall Accuracy: 94%
```

because an admin can immediately see if one crop is problematic.

---

# 16. Model Performance Trend

Show performance across evaluation runs.

```text
Model Performance Trend

Score
100% ┤
 95% ┤          ╭──────
 90% ┤────╮─────╯
 85% ┤    ╰──
 80% ┤
     └────────────────────
       v1   v2   v3   v4
```

Use:

```text
[ Accuracy ]
[ F1 ]
[ Precision ]
[ Recall ]
```

depending on the selected model.

---

# 17. Model Version History

This is important if you eventually deploy improved versions.

```text
Version History

v3
● Current
F1: 96.59%
Deployed: 20 Aug 2026

v2
F1: 94.12%
Deployed: 12 Aug 2026

v1
F1: 91.80%
Deployed: 03 Aug 2026
```

Admin should be able to compare:

```text
v2 vs v3
```

before promoting a model.

---

# 18. Model Registry

Add a model registry table.

```text
Model Registry
```

Columns:

```text
Model
Version
Framework
Task
Dataset
Metric
Status
Deployed
Updated
```

Example:

| Model             | Version | Task    | Metric   | Status |
| ----------------- | ------- | ------- | -------- | ------ |
| EfficientNet Crop | v1      | Crop ID | Accuracy | ✓      |
| Tomato Disease    | v1      | Disease | F1       | ✓      |
| Potato Disease    | v1      | Disease | F1       | ✓      |
| Cotton Disease    | v1      | Disease | F1       | ✓      |
| YOLO Pest         | v1      | Pest    | Macro F1 | ✓      |

---

# 19. Deployment Status

Add:

```text
Deployment

✓ Production
○ Staging
○ Archived
```

Example:

```text
YOLO Pest Classifier
v1

Production ✓
```

This is useful if you eventually have multiple versions.

---

# 20. Model Health

Separate **performance** from **operational health**.

For example:

```text
Model Health

Crop Identifier
Performance     ✓
Availability    ✓
Latency         ✓

Disease Model
Performance     ✓
Availability    ✓
Latency         ⚠

Pest Model
Performance     ✓
Availability    ✓
Latency         ✓
```

---

# 21. Inference Latency

Although this isn't a model-quality metric, it is important operationally.

Show:

```text
Average Inference Time

Crop Identifier
182 ms

Disease Classifier
245 ms

Pest Classifier
210 ms

Recommendation
2.8 sec
```

Also:

```text
P95 Latency
```

if your backend tracks it.

---

# 22. Prediction Error Rate

For production monitoring:

```text
Prediction Errors

Crop Identifier
2.1%

Disease Classifier
4.8%

Pest Classifier
1.7%
```

But define exactly what "error" means.

If you don't have ground truth, use:

```text
Expert Correction Rate
```

instead of pretending these are actual errors.

---

# 23. AI vs Expert Performance

This is the strongest connection between your Model Performance and Expert Review systems.

```text
AI vs Expert

                 AI Accepted   Corrected

Crop               94%            6%
Disease             82%           18%
Severity            79%           21%
Pest                91%            9%
```

This lets you identify:

> "The disease model is the area where experts disagree with AI most frequently."

That is actionable.

---

# 24. Model Confidence vs Expert Correction

A very useful visualization:

```text
Confidence vs Expert Correction

Correction %
│
│ █
│ █
│  █
│   █
│     █
│       █
└────────────────────────
  50   60   70   80   90  100
       Confidence %
```

The goal is to determine whether:

```text
Low confidence → More corrections
```

If that relationship is visible in your real data, it can help justify your **expert-review routing threshold**.

---

# 25. Model Alerts

Add:

```text
Model Alerts
```

Example:

```text
⚠ Potato Disease model F1 dropped below threshold

⚠ Pest model latency increased 18%

⚠ 12% increase in expert corrections

✓ Crop Identifier operating normally
```

---

# 26. Threshold Configuration

Since your project already uses confidence thresholds, show them.

For example:

```text
Prediction Thresholds

Crop Confidence
0.75

Disease Confidence
0.70

```

Your frontend should fetch these from backend configuration rather than hardcoding them.

Admin can potentially view:

```text
Current Threshold
0.70

Predictions below threshold
→ Expert Review
```

If you allow editing thresholds, make that a controlled configuration screen rather than a casual dashboard action.

---

# 27. Model Evaluation Dataset

For transparency:

```text
Evaluation

Dataset
Smart Farming Test Set

Samples
2,400

Classes
5

Last Evaluated
26 Aug 2026

Evaluation Status
✓ Complete
```

For each model, show only metadata your backend actually stores.

---

# 28. Dataset Version

If your evaluation pipeline tracks dataset versions:

```text
Dataset

test_v2
2,400 images

Evaluated:
26 Aug 2026
```

This becomes extremely useful when comparing model versions.

---

# 29. Model Detail Page

If you want a dedicated page rather than drawer:

```text
/admin/model-performance/pest-classifier
```

Layout:

```text
Pest Classifier
────────────────────────────────────────────

Model Information
├── Version
├── Framework
├── Classes
├── Dataset
└── Deployment

Performance
├── Accuracy
├── Precision
├── Recall
└── Macro F1

Class Performance
├── Aphid
├── Army Worm
├── Leaf Miner
└── Spider Mite

Confusion Matrix

Performance Trend

AI vs Expert

Operational Metrics
├── Latency
├── Error Rate
└── Prediction Volume
```

---

# 30. Recommendation Model

Your recommendation model is different.

Don't force classification metrics onto an LLM.

Instead show:

```text
Recommendation Model

Model
Qwen2.5-1.5B-Instruct

Status
✓ Operational

Requests
1,284

Successful
1,247

Failed
37

Average Response
2.8 sec

Expert Acceptance
81%

Expert Edited
14%

Rejected
5%
```

This is a much more appropriate evaluation framework for an LLM recommendation service.

---

# 31. Severity Estimator

Your severity system is also different from classification.

Instead of:

```text
Accuracy
```

consider:

```text
Mean Absolute Error
```

and:

```text
Mean Error
```

if your backend evaluates it numerically.

For the UI:

```text
Severity Estimator

MAE
8.4%

Healthy Classification
✓

Mild
✓

Moderate
✓

Severe
✓
```

If you only use severity buckets based on image segmentation and don't have ground-truth evaluation, show:

```text
Operational Status
✓

Predictions
1,842

Expert Reviewed
142

Expert Correction
11.2%
```

rather than inventing a statistical metric.

---

# 32. Mobile Layout

Mobile should prioritize model cards and alerts.

```text
┌──────────────────────────────┐
│ 🧠 Model Performance    🔔  │
├──────────────────────────────┤
│                              │
│ [ All Models ▾ ]             │
│                              │
│ Crop Identifier              │
│                              │
│ 94.2%                        │
│ Accuracy                     │
│ ✓ Healthy                    │
│                              │
│ Disease Classifier           │
│                              │
│ 91.8%                        │
│ Macro F1                     │
│ ✓ Healthy                    │
│                              │
│ Pest Classifier              │
│                              │
│ 96.59%                       │
│ Macro F1                     │
│ ✓ Healthy                    │
│                              │
│ Model Alerts                 │
│                              │
│ ⚠ Potato model needs review │
│                              │
│ Model Registry               │
│                              │
│ Crop Identifier       ✓     │
│ Disease Model         ✓     │
│ Pest Model            ✓     │
└──────────────────────────────┘
```

Detailed charts can be moved below or opened from each model card.

---

# 33. Recommended Screen Architecture

```text
MODEL PERFORMANCE
│
├── Global Filters
│
├── KPI Summary
│   ├── Crop Performance
│   ├── Disease Performance
│   ├── Pest Performance
│   └── Expert Agreement
│
├── Model Comparison
│
├── Performance Trend
│
├── Model Registry
│
├── Model Alerts
│
├── Disease Model Comparison
│
├── Class-Level Performance
│
├── Confusion Matrix
│
├── AI vs Expert Agreement
│
├── Operational Metrics
│   ├── Latency
│   ├── Availability
│   └── Failure Rate
│
└── Model Detail
```

---

# 34. What to Build for Your V1

For your current Smart Farming project, I would **not** build the entire ML monitoring platform yet.

### V1

```text
✓ Model cards
✓ Model registry
✓ Accuracy / F1 / appropriate metric
✓ Per-class performance
✓ Disease model comparison
✓ Confusion matrix
✓ Model status
✓ Version
✓ Last evaluation
✓ Prediction volume
✓ Expert correction/agreement
✓ Model alerts
```

### V2

```text
⭐ Model version comparison
⭐ Performance trend
⭐ Latency monitoring
⭐ Prediction error monitoring
⭐ Confidence vs correction
⭐ Dataset version tracking
```

### V3

```text
⭐ Model drift
⭐ Data drift
⭐ Calibration curves
⭐ Automated performance alerts
⭐ Champion/challenger models
⭐ Model deployment approval workflow
```

---

# 35. How This Fits Your Admin Portal

Your admin screens now form a coherent monitoring system:

```text
                    ADMIN
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
   Predictions     Feedback       Models
   Monitoring      Monitoring     Performance
       │              │              │
       │              │              │
       ▼              ▼              ▼
"What is AI       "What do       "How well
doing?"            users think?"  does AI work?"
       │              │              │
       └──────────────┼──────────────┘
                      ▼
                Expert Reviews
                      │
                      ▼
              Human Validation
                      │
                      ▼
              System Improvement
```

The key distinction is:

**Prediction Monitoring** = real-time/production behavior
**Feedback** = user and expert experience
**Model Performance** = validated model quality

That separation will make your admin frontend feel like a **real AI-powered agricultural platform**, rather than a collection of generic CRUD dashboards.


# Smart Farming — Admin Drift Monitoring Screen UI/UX Specification

For your Smart Farming project, **Drift Monitoring** should be an advanced admin screen that detects whether the data reaching your AI models is starting to differ from the data the models were originally evaluated on.

The core idea is:

> **"Is the real-world farming data still similar enough to the data our AI models were built and evaluated on?"**

This is different from your **Model Performance** screen.

```text
Model Performance
→ How well did the model perform?

Prediction Monitoring
→ What is the model doing in production?

Drift Monitoring
→ Is the production data changing in a way that could make
  the model less reliable?
```

---

# 1. Route

```text
/admin/drift-monitoring
```

Optional detail:

```text
/admin/drift-monitoring/:modelId
```

---

# 2. Main Screen

I recommend this overall structure:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming Admin                                      Admin ▾          │
├────────────────┬─────────────────────────────────────────────────────────────┤
│                │                                                             │
│ 📊 Overview    │ Drift Monitoring                                           │
│ 👥 Users       │ Monitor changes in production data and model behavior      │
│ 👨‍🌾 Experts    │                                                             │
│ 🌾 Farms       │ [Last 30 Days ▾] [All Models ▾] [All Crops ▾]              │
│ 📋 Cases       │                                                             │
│ 🚨 Alerts      │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│ 📈 Analytics   │ │ Healthy  │ │ Warning  │ │ Critical │ │ Features │       │
│ 🧠 Predictions │ │ 4        │ │ 2        │ │ 1        │ │ 18       │       │
│ 💬 Feedback    │ │ Models   │ │ Models   │ │ Model    │ │ Monitored │       │
│ ⚙ System       │ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                │                                                             │
│ 🔄 Drift       │ ┌──────────────────────────┐ ┌──────────────────────────┐ │
│                │ │ Overall Drift Status     │ │ Drift Trend              │ │
│                │ │                          │ │                          │ │
│                │ │        ● WARNING         │ │       📈                 │ │
│                │ │                          │ │                          │ │
│                │ │ Score: 0.18              │ │                          │ │
│                │ └──────────────────────────┘ └──────────────────────────┘ │
│                │                                                             │
│                │ Model Drift                                                  │
│                │ ┌────────────────────────────────────────────────────────┐ │
│                │ │ Model │ Data Drift │ Prediction │ Confidence │ Status │ │
│                │ └────────────────────────────────────────────────────────┘ │
│                                                                              │
│                │ Feature Drift                                               │
│                │ ┌────────────────────────────────────────────────────────┐ │
│                │ │ Feature │ Baseline │ Current │ Drift │ Status          │ │
│                │ └────────────────────────────────────────────────────────┘ │
│                                                                              │
│                │ 🚨 Drift Alerts                                             │
└────────────────┴─────────────────────────────────────────────────────────────┘
```

---

# 3. Header

### Title

```text
Drift Monitoring
```

### Subtitle

> Monitor changes in production data, prediction distributions, and model behavior.

Right side:

```text
[ Last 30 Days ▾ ]
[ Refresh ]
```

And:

```text
Last checked: 2 min ago
```

---

# 4. Global Filters

Use:

```text
[ Date Range ▾ ]
[ Model ▾ ]
[ Crop ▾ ]
[ Drift Type ▾ ]
[ Severity ▾ ]
```

### Model

```text
All Models

Crop Identifier
Disease Classifier
Pest Classifier
Severity Estimator
Recommendation Model
```

### Drift Type

```text
All

Data Drift
Prediction Drift
Confidence Drift
Image Quality Drift
```

---

# 5. Top KPI Cards

I recommend four.

## Card 1 — Healthy Models

```text
┌──────────────────────────┐
│ ✓ Healthy Models         │
│                          │
│ 4                        │
│ No significant drift     │
└──────────────────────────┘
```

---

## Card 2 — Warning

```text
┌──────────────────────────┐
│ ⚠ Warning                │
│                          │
│ 2                        │
│ Models affected          │
└──────────────────────────┘
```

---

## Card 3 — Critical

```text
┌──────────────────────────┐
│ 🔴 Critical Drift        │
│                          │
│ 1                        │
│ Immediate investigation  │
└──────────────────────────┘
```

---

## Card 4 — Features Monitored

```text
┌──────────────────────────┐
│ 📊 Features Monitored    │
│                          │
│ 18                       │
│ Across all models        │
└──────────────────────────┘
```

These numbers are examples. Your frontend should receive them from the backend.

---

# 6. Overall Drift Status

This should be the most prominent component.

```text
┌─────────────────────────────────────┐
│ Overall Drift Status                │
│                                     │
│              ⚠                      │
│           WARNING                   │
│                                     │
│ Drift Score                         │
│                                     │
│ 0.18                                │
│                                     │
│ ↑ 0.06 from previous period         │
└─────────────────────────────────────┘
```

Use a simple status system:

```text
✓ Stable
⚠ Warning
🔴 Critical
```

---

# 7. Important: Explain the Drift Score

Do **not** simply show:

```text
Drift = 0.18
```

The admin needs context.

Add:

```text
What does this mean?

The current production data differs from the
baseline distribution. Further investigation
may be required.

[ Learn More ]
```

You can also provide a tooltip:

```text
ⓘ Drift score represents the measured difference
between baseline and current production data.
```

---

# 8. Drift Trend

Show drift over time:

```text
Drift Score

0.30 ┤
0.25 ┤
0.20 ┤                    ╭──
0.15 ┤              ╭─────╯
0.10 ┤──────╮───────╯
0.05 ┤      ╰────
     └────────────────────────
       Week 1  2  3  4  5
```

Tabs:

```text
[ Overall ]
[ Data Drift ]
[ Prediction Drift ]
[ Confidence Drift ]
```

---

# 9. Model Drift Table

This is one of the most important components.

```text
Model Drift
```

| Model           | Data Drift | Prediction Drift | Confidence | Status      |
| --------------- | ---------: | ---------------: | ---------: | ----------- |
| Crop Identifier |       0.08 |             0.05 |      93.2% | ✓ Stable    |
| Tomato Disease  |       0.21 |             0.18 |      76.4% | ⚠ Warning   |
| Potato Disease  |       0.12 |             0.09 |      81.3% | ✓ Stable    |
| Cotton Disease  |       0.07 |             0.06 |      89.1% | ✓ Stable    |
| Pest Classifier |       0.28 |             0.24 |      71.2% | 🔴 Critical |

Again, these values are illustrative.

The frontend should display whatever drift methodology your backend implements.

---

# 10. Data Drift

For your project, data drift could represent changes in the characteristics of incoming inputs.

For image-based models, potential monitored properties include:

```text
Image brightness
Image sharpness
Image resolution
Leaf area
Background proportion
Color distribution
Image size
```

For other data:

```text
Crop
Season
Location
Weather conditions
Soil properties
```

Only display features that your backend actually measures.

---

# 11. Feature Drift Table

Example:

```text
Feature Drift
```

| Feature          | Baseline | Current | Drift Score | Status |
| ---------------- | -------: | ------: | ----------: | ------ |
| Brightness       |      142 |     121 |        0.18 | ⚠      |
| Sharpness        |     0.73 |    0.69 |        0.07 | ✓      |
| Leaf Area        |      42% |     35% |        0.21 | ⚠      |
| Image Resolution |  224×224 | 224×224 |        0.00 | ✓      |
| Background Ratio |      31% |     47% |        0.28 | 🔴     |

This is particularly relevant to your existing preprocessing pipeline.

---

# 12. Image Quality Drift

This could be a **unique feature for your project**.

Your pipeline already performs image-quality preprocessing such as:

```text
Blur detection
Brightness validation
Leaf detection
Leaf isolation
Background removal
```

Therefore, monitor whether incoming farmer images are changing.

Example:

```text
Image Quality Drift

Blurred Images
Baseline       8%
Current       14%
             ↑ 6%

Low Brightness
Baseline       5%
Current         9%
             ↑ 4%

Poor Leaf Detection
Baseline       4%
Current         8%
             ↑ 4%
```

Then:

```text
⚠ Incoming image quality is deteriorating.
This may affect disease and pest predictions.
```

This is much more domain-specific than a generic ML monitoring dashboard.

---

# 13. Prediction Drift

Prediction drift means the **distribution of predictions** is changing.

Example:

Baseline:

```text
Disease Predictions

Healthy       42%
Early Blight  21%
Late Blight   18%
Other         19%
```

Current:

```text
Disease Predictions

Healthy       27% ↓
Early Blight  35% ↑
Late Blight   24% ↑
Other         14% ↓
```

Then:

```text
⚠ Significant prediction distribution change
```

---

# 14. Prediction Distribution Chart

Use a grouped bar chart:

```text
Disease Distribution

             Baseline     Current

Healthy       ████████     █████
Early Blight  ████         ███████
Late Blight   ███          █████
Other         ████         ███
```

This is much easier for admins to understand than just a drift score.

---

# 15. Confidence Drift

This is highly relevant to your system.

Show:

```text
Average Confidence

Baseline
89.4%

Current
81.7%

↓ 7.7%
```

Then:

```text
⚠ Model confidence is declining.
```

---

# 16. Confidence Distribution

Show:

```text
Confidence

90–100%  █████████████
80–90%   █████████
70–80%   ██████
60–70%   ███
<60%     ██
```

Compare:

```text
Baseline vs Current
```

This lets the admin see whether the AI is becoming increasingly uncertain.

---

# 17. Drift + Expert Corrections

This is an especially powerful feature for your project.

Show:

```text
Drift vs Expert Correction Rate
```

Example:

```text
Drift ↑
       │
0.30   │              ●
       │           ●
0.20   │        ●
       │     ●
0.10   │ ●
       └────────────────────
          Expert Correction ↑
```

Then:

```text
Current Drift
0.24

Expert Correction
18.2%
```

This helps determine whether drift is actually affecting model reliability.

---

# 18. Model-Specific Detail

Clicking:

```text
Tomato Disease Classifier
```

opens:

```text
┌──────────────────────────────────────────────┐
│ Tomato Disease Model                    ✕   │
├──────────────────────────────────────────────┤
│                                              │
│ Overall Status                               │
│ ⚠ WARNING                                    │
│                                              │
│ Data Drift                                   │
│ 0.21                                         │
│                                              │
│ Prediction Drift                             │
│ 0.18                                         │
│                                              │
│ Confidence Change                            │
│ -8.4%                                        │
│                                              │
│ Expert Correction                            │
│ 15.2%                                        │
│                                              │
│ Last Checked                                 │
│ 26 Aug 2026                                  │
│                                              │
│ [ View Detailed Drift ]                     │
└──────────────────────────────────────────────┘
```

---

# 19. Detailed Drift Screen

If you create:

```text
/admin/drift-monitoring/tomato-disease
```

show:

```text
Tomato Disease Classifier
────────────────────────────────────

Status
⚠ Warning

Drift Overview

Data Drift             0.21
Prediction Drift       0.18
Confidence Drift       0.16

────────────────────────────────────

Feature Drift

Brightness             0.18
Sharpness              0.07
Leaf Area              0.21
Background Ratio       0.28

────────────────────────────────────

Prediction Distribution

Baseline vs Current

────────────────────────────────────

Confidence Distribution

Baseline vs Current

────────────────────────────────────

Expert Validation

Agreement              84.8%
Correction             15.2%

────────────────────────────────────

Recommended Action

⚠ Investigate image quality
  and recent prediction changes.

[ Create Investigation ]
```

---

# 20. Drift Alerts

At the bottom or right side:

```text
🚨 Drift Alerts
```

Example:

```text
🔴 Critical
Pest Classifier

Prediction distribution changed significantly.

2 hours ago
[ Investigate ]
```

```text
⚠ Warning
Tomato Disease

Average confidence dropped 8%.

5 hours ago
[ Investigate ]
```

```text
⚠ Warning
Image Quality

Blurred image rate increased 6%.

Yesterday
[ Investigate ]
```

---

# 21. Alert Lifecycle

Use:

```text
Detected
   ↓
Investigating
   ↓
Action Required
   ↓
Resolved
```

Example:

```text
⚠ Drift Detected
      ↓
Admin Investigation
      ↓
Check Data Quality
      ↓
Check Model Performance
      ↓
Expert Validation
      ↓
Resolve / Retrain
```

---

# 22. Recommended Action

Don't just tell the admin that drift exists.

Tell them what they can investigate.

Example:

```text
Recommended Actions

⚠ Image quality deterioration detected.

Suggested investigation:

1. Review recent uploaded images.
2. Check image preprocessing failures.
3. Compare prediction confidence.
4. Review expert corrections.
5. Evaluate the model on recent samples.

[ Review Images ]
[ View Predictions ]
[ View Expert Reviews ]
```

This creates a proper operational workflow.

---

# 23. Data Drift vs Model Drift

Use clear terminology in the UI.

### Data Drift

```text
Input data changed.
```

Example:

```text
Farmer images are darker than baseline images.
```

### Prediction Drift

```text
Model outputs changed.
```

Example:

```text
Early Blight predictions increased significantly.
```

### Confidence Drift

```text
Model certainty changed.
```

Example:

```text
Average prediction confidence dropped from 89% to 78%.
```

This distinction should appear in tooltips.

---

# 24. Drift Threshold Configuration

Since your admin system already has configuration concepts, you can show:

```text
Drift Thresholds

Stable
< 0.10

Warning
0.10 – 0.20

Critical
> 0.20
```

However, **do not hardcode these values unless your backend actually defines them**.

Better:

```text
Threshold Configuration
ⓘ Values provided by monitoring service
```

---

# 25. Baseline Information

The admin should always know:

> **"Compared against what?"**

Add:

```text
Baseline

Dataset:
Smart Farming Evaluation Dataset

Version:
v2

Samples:
2,400

Reference Period:
01 Aug – 15 Aug 2026
```

For production drift:

```text
Current Window

16 Aug – 26 Aug 2026

Samples:
1,284
```

This makes the drift measurement interpretable.

---

# 26. Baseline vs Current

Create a reusable comparison component:

```text
┌─────────────────────────────────────────┐
│ Baseline vs Current                     │
├─────────────────────────────────────────┤
│                                         │
│ Metric          Baseline    Current     │
│                                         │
│ Brightness      142         121         │
│ Sharpness       0.73        0.69        │
│ Leaf Area       42%         35%         │
│ Confidence      89.4%       81.7%       │
│                                         │
└─────────────────────────────────────────┘
```

This should be available when inspecting any model.

---

# 27. Crop-Specific Drift

Because Indian farming has strong crop and seasonal variation, allow:

```text
[ All Crops ▾ ]
```

Options:

```text
Cotton
Groundnut
Pepper Bell
Potato
Tomato
```

Then show:

```text
Crop Drift

Cotton
✓ Stable

Groundnut
✓ Stable

Potato
⚠ Warning

Tomato
🔴 Critical
```

This can help identify whether drift is localized to a particular crop.

---

# 28. Seasonal Drift

This can become a very useful Smart Farming-specific feature.

Instead of assuming every distribution change means model failure, show:

```text
Seasonal Context

Current Season:
Monsoon

Baseline:
Pre-Monsoon

⚠ Distribution differences may be
season-related.
```

This prevents admins from treating every legitimate agricultural change as a model problem.

---

# 29. Geographic Drift

If your application stores farm location:

```text
Geographic Drift
```

Map:

```text
             Gujarat

      ●●●
   ●●●●●●
      ●●
```

Example:

```text
Region             Drift

Surat               0.08 ✓
Ahmedabad           0.12 ⚠
Rajkot              0.09 ✓
Vadodara            0.24 🔴
```

This is particularly interesting for an Indian farming application because model input characteristics can vary geographically.

Only implement this if your application actually stores sufficiently reliable location data.

---

# 30. Mobile Layout

On mobile:

```text
┌──────────────────────────────┐
│ 🔄 Drift Monitoring     🔔  │
├──────────────────────────────┤
│                              │
│ [ Last 30 Days ▾ ]           │
│                              │
│ Overall Status               │
│                              │
│ ⚠ WARNING                    │
│ Drift Score: 0.18            │
│                              │
│ ┌──────────┐ ┌──────────┐   │
│ │ Healthy  │ │ Warning  │   │
│ │ 4        │ │ 2        │   │
│ └──────────┘ └──────────┘   │
│                              │
│ 🔴 Critical: 1              │
│                              │
│ Model Drift                  │
│                              │
│ Crop Identifier      ✓      │
│ Tomato Disease       ⚠      │
│ Potato Disease       ✓      │
│ Pest Classifier      🔴     │
│                              │
│ Confidence Drift             │
│                              │
│ Baseline     89.4%           │
│ Current      81.7%           │
│                              │
│ 🚨 Alerts                    │
│                              │
│ Pest model critical drift   │
│                              │
│ [ Investigate ]              │
└──────────────────────────────┘
```

---

# 31. Empty State

If monitoring hasn't been configured:

```text
┌──────────────────────────────────────┐
│                                      │
│              📊                     │
│                                      │
│       No drift data available        │
│                                      │
│ Drift monitoring has not received     │
│ enough production data yet.          │
│                                      │
│ Baseline comparison will appear      │
│ when sufficient data is available.   │
│                                      │
└──────────────────────────────────────┘
```

This is important.

**Do not display "0% drift" when you simply don't have enough data.**

---

# 32. Insufficient Data State

This is even better:

```text
⚠ Insufficient Data

Only 24 production samples are available.
At least 100 samples are required before
calculating reliable drift statistics.

Samples:
24 / 100
```

This makes your system look much more professionally engineered.

---

# 33. Error State

If the monitoring service fails:

```text
⚠ Unable to calculate drift

The monitoring service could not retrieve
the current production distribution.

Last successful check:
26 Aug 2026, 10:42 AM

[ Retry ]
```

---

# 34. Recommended Screen Structure

Your complete screen should be:

```text
DRIFT MONITORING
│
├── Global Filters
│
├── KPI Cards
│   ├── Healthy
│   ├── Warning
│   ├── Critical
│   └── Features Monitored
│
├── Overall Drift Status
│
├── Drift Trend
│
├── Model Drift
│
├── Feature Drift
│
├── Image Quality Drift
│
├── Prediction Drift
│
├── Confidence Drift
│
├── Baseline vs Current
│
├── AI vs Expert Correction
│
├── Crop-Specific Drift
│
├── Drift Alerts
│
└── Model Drift Detail
```

---

# 35. What I Recommend for Your Smart Farming V1

Because your project is currently a prototype/hackathon system, **don't try to build a full enterprise MLOps platform**.

Build:

### V1

```text
✓ Overall drift status
✓ Baseline vs current
✓ Model drift table
✓ Confidence drift
✓ Prediction distribution
✓ Image-quality drift
✓ Drift alerts
✓ Crop filter
✓ Model filter
✓ Insufficient-data state
```

### V2

```text
⭐ Expert correction vs drift
⭐ Per-feature drift
⭐ Drift trends
⭐ Crop-specific drift
⭐ Seasonal context
⭐ Geographic drift
```

### V3

```text
⭐ Automated drift detection
⭐ Automated investigation
⭐ Retraining recommendations
⭐ Model version comparison
⭐ Automatic retraining pipeline
⭐ Champion/challenger deployment
```

---

# 36. The Most Important Feature for Your Project

I would make **Image Quality Drift → Prediction Confidence → Expert Correction** your signature monitoring flow.

For example:

```text
                 DRIFT DETECTED
                       │
                       ▼
             Image Brightness ↓
                       │
                       ▼
             Image Quality ↓
                       │
                       ▼
            AI Confidence ↓
                       │
                       ▼
          Expert Corrections ↑
                       │
                       ▼
             Model Investigation
                       │
              ┌────────┴────────┐
              ▼                 ▼
          No Issue          Model Issue
              │                 │
              ▼                 ▼
           Resolve          Evaluate/
                             Retrain
```

This is much more relevant to your Smart Farming system than simply displaying generic **PSI/KL-divergence** charts.

And it connects your admin modules into a complete operational loop:

```text
Prediction Monitoring
        │
        ▼
Drift Monitoring
        │
        ▼
Model Performance
        │
        ▼
Expert Review
        │
        ▼
Feedback
        │
        ▼
Model/System Improvement
```

That overall architecture will make your admin panel feel like a **real production AI platform**, rather than just a collection of dashboard pages.


# Smart Farming — Admin MLOps / Retraining Screen UI/UX Specification

For your Smart Farming project, **MLOps / Retraining** should be the admin screen that closes the loop: it's where drift, low confidence, and expert corrections actually turn into a new, better-trained, and safely deployed model.

The core idea is:

> **"Do we need to retrain a model, and if so, can we do it safely — without breaking what's already working in the field?"**

This is different from your other admin screens.

```text
Drift Monitoring
→ Is something wrong?

Model Performance
→ How good is the current model?

Feedback / Predictions
→ What raw signals are coming in?

MLOps / Retraining
→ What do we do about it — and how do we do it safely?
```

---

# 1. Route

```text
/admin/mlops
```

Optional detail:

```text
/admin/mlops/runs/:runId
/admin/mlops/models/:modelId/versions
```

---

# 2. Main Screen

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🌱 Smart Farming Admin                                      Admin ▾          │
├────────────────┬─────────────────────────────────────────────────────────────┤
│                │                                                             │
│ 📊 Overview    │ MLOps / Retraining                                         │
│ 👥 Users       │ Trigger, monitor, and deploy model retraining safely       │
│ 👨‍🌾 Experts    │                                                             │
│ 🌾 Farms       │ [All Models ▾] [All Crops ▾]        [ + New Retraining Run ]│
│ 📋 Cases       │                                                             │
│ 🚨 Alerts      │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│ 📈 Analytics   │ │ Needs    │ │ Running  │ │ Awaiting │ │ Deployed │       │
│ 🧠 Predictions │ │ Retrain  │ │ Now      │ │ Approval │ │ This Wk  │       │
│ 💬 Feedback    │ │ 2 Models │ │ 1 Run    │ │ 1 Model  │ │ 1 Model  │       │
│ 🔄 Drift       │ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│ ⚙ System       │                                                             │
│ 🧪 MLOps       │ Retraining Triggers                                        │
│                │ ┌────────────────────────────────────────────────────────┐ │
│                │ │ Model │ Trigger Reason │ Detected │ Priority │ Action  │ │
│                │ └────────────────────────────────────────────────────────┘ │
│                │                                                             │
│                │ Active & Recent Training Runs                              │
│                │ ┌────────────────────────────────────────────────────────┐ │
│                │ │ Run │ Model │ Status │ Progress │ Started │ Duration   │ │
│                │ └────────────────────────────────────────────────────────┘ │
│                │                                                             │
│                │ Champion vs Challenger Comparison                          │
│                │                                                             │
│                │ Deployment Pipeline                                        │
└────────────────┴─────────────────────────────────────────────────────────────┘
```

---

# 3. Header

### Title
```text
MLOps / Retraining
```

### Subtitle
> Trigger, monitor, evaluate, and safely deploy retrained models.

Right side:
```text
[ All Models ▾ ]
[ + New Retraining Run ]
```

And:
```text
Last pipeline run: 3 hours ago
```

---

# 4. Global Filters

```text
[ Model ▾ ]
[ Crop ▾ ]
[ Run Status ▾ ]
[ Time Range ▾ ]
```

### Model
```text
All Models

Crop Identifier
Tomato Disease Classifier
Potato Disease Classifier
Cotton Disease Classifier
Groundnut Disease Classifier
Pepper Bell Disease Classifier
Severity Estimator
```

### Run Status
```text
All

Queued
Preprocessing Data
Training
Evaluating
Awaiting Approval
Deployed
Rejected
Failed
```

---

# 5. Top KPI Cards

## Card 1 — Needs Retrain
```text
┌──────────────────────────┐
│ ⚠ Needs Retraining       │
│                          │
│ 2                        │
│ Models flagged by drift  │
└──────────────────────────┘
```

## Card 2 — Running Now
```text
┌──────────────────────────┐
│ ⏳ Running Now            │
│                          │
│ 1                        │
│ Active training run      │
└──────────────────────────┘
```

## Card 3 — Awaiting Approval
```text
┌──────────────────────────┐
│ 🕓 Awaiting Approval      │
│                          │
│ 1                        │
│ Ready for admin review   │
└──────────────────────────┘
```

## Card 4 — Deployed This Week
```text
┌──────────────────────────┐
│ ✅ Deployed This Week     │
│                          │
│ 1                        │
│ Model version live       │
└──────────────────────────┘
```

These numbers are examples — the frontend should receive them from the backend.

---

# 6. Retraining Triggers

This section answers: **"Why would we retrain right now?"** It should pull directly from your Drift Monitoring, Feedback, and Prediction Monitoring modules — this is where those three modules actually connect to action.

```text
Retraining Triggers
```

| Model | Trigger Reason | Detected | Priority | Action |
|---|---|---|---|---|
| Pest Classifier | Critical data drift (0.28) | 2 hrs ago | 🔴 High | [ Start Retraining ] |
| Tomato Disease | Confidence dropped 8%, expert correction 15.2% | 5 hrs ago | ⚠ Medium | [ Start Retraining ] |
| Potato Disease | 340 new labeled feedback samples available | Yesterday | Low | [ Review Data ] |

Each trigger row should be traceable back to its source:

```text
ⓘ Trigger source: Drift Monitoring → Pest Classifier → Critical
ⓘ Trigger source: Feedback → 340 expert-corrected cases since last training
```

**Do not auto-trigger retraining silently.** Every automatic trigger should surface here for an admin to review and confirm — this keeps a human in the loop before compute and deployment risk are spent.

---

# 7. Starting a New Retraining Run

Clicking **"+ New Retraining Run"** or **"Start Retraining"** on a trigger opens a config panel:

```text
┌──────────────────────────────────────────────┐
│ New Retraining Run                      ✕   │
├──────────────────────────────────────────────┤
│                                              │
│ Model                                        │
│ [ Tomato Disease Classifier ▾ ]              │
│                                              │
│ Base Checkpoint                              │
│ [ Current Production (v2.3) ▾ ]              │
│                                              │
│ Training Data                                │
│ ☑ Original training set (12,400 images)      │
│ ☑ New expert-corrected feedback (340 images) │
│ ☐ Synthetic/augmented additions              │
│                                              │
│ Data Split                                   │
│ Train 80% / Val 10% / Test 10%               │
│                                              │
│ Hyperparameters                              │
│ Epochs        [ 20      ]                    │
│ Learning Rate [ 1e-4    ]                    │
│ Batch Size    [ 32      ]                    │
│                                              │
│ Evaluation Gate                              │
│ Must beat current production on:             │
│ ☑ Macro F1     ☑ Per-class recall            │
│ ☑ Uncontrolled-env accuracy                  │
│                                              │
│ [ Cancel ]              [ Start Training ]   │
└──────────────────────────────────────────────┘
```

Prefilling this from a trigger (e.g. pre-checking "new feedback" data, pre-selecting the flagged model) turns a vague "retrain" click into a reviewable, specific plan.

---

# 8. Active & Recent Training Runs

```text
Active & Recent Training Runs
```

| Run | Model | Status | Progress | Started | Duration |
|---|---|---|---|---|---|
| #128 | Tomato Disease | ⏳ Training | Epoch 14/20 (70%) | 40 min ago | 40 min |
| #127 | Pest Classifier | 🕓 Awaiting Approval | Complete | Yesterday | 2h 10m |
| #126 | Crop Identifier | ✅ Deployed | Complete | 3 days ago | 1h 45m |
| #125 | Potato Disease | ❌ Failed | Stopped at epoch 6 | 4 days ago | 22 min |

Clicking a run opens the **Run Detail** view.

### Run Detail Screen — `/admin/mlops/runs/:runId`

```text
Run #128 — Tomato Disease Classifier
────────────────────────────────────

Status
⏳ Training — Epoch 14 / 20

Live Metrics
Train Loss        0.142  ↓
Val Loss          0.181  ↓
Val Accuracy      94.2%  ↑
Val Macro F1      0.931  ↑

────────────────────────────────────

Training Curve
[ Loss / Accuracy chart, train vs val ]

────────────────────────────────────

Configuration
Base checkpoint    v2.3
Dataset            12,740 images (12,400 base + 340 feedback)
Epochs             20
Learning rate      1e-4
Batch size         32

────────────────────────────────────

Logs
[ Streaming training log, tail -f style ]

[ Stop Run ]
```

For a **failed** run, replace Live Metrics with:

```text
⚠ Run Failed

Stopped at epoch 6
Reason: Validation loss diverged (NaN detected)

[ View Full Logs ]
[ Retry with Adjusted Config ]
```

---

# 9. Champion vs Challenger Comparison

This is the most important gate in the whole screen — it's what prevents a worse model from silently reaching farmers.

```text
Champion vs Challenger Comparison
```

```text
┌─────────────────────────────────────────────────────────┐
│ Tomato Disease Classifier                                │
├───────────────────────┬──────────────┬───────────────────┤
│ Metric                │ Champion (v2.3) │ Challenger (v2.4) │
├───────────────────────┼──────────────┼───────────────────┤
│ Macro F1               │ 0.912          │ 0.931  ↑          │
│ Overall Accuracy       │ 91.4%          │ 93.8%  ↑          │
│ Uncontrolled-env Acc   │ 87.1%          │ 90.2%  ↑          │
│ Lowest Class Recall    │ 0.79 (Mold)    │ 0.84 (Mold)  ↑    │
│ Avg Inference Time     │ 84ms           │ 89ms   ↓          │
│ Confidence (avg)       │ 88.9%          │ 90.1%  ↑          │
└───────────────────────┴──────────────┴───────────────────┘

Verdict: ✅ Challenger outperforms champion on all evaluation-gate metrics.
```

If the challenger loses on any gated metric, show a clear warning instead of a plain verdict:

```text
Verdict: ⚠ Challenger regresses on Lowest Class Recall (0.76 vs 0.79).
Review before approving.
```

Include a **per-class breakdown** (expandable), since an average improvement can hide a single disease class getting worse — which matters most for rarer, more damaging diseases.

```text
Per-Class Comparison ▾

Class              Champion   Challenger
Bacterial Spot     0.91       0.93  ↑
Early Blight       0.88       0.90  ↑
Mold Leaf          0.79       0.84  ↑
Mosaic Virus       0.85       0.82  ↓  ⚠
```

---

# 10. Approval Decision

Below the comparison:

```text
┌──────────────────────────────────────────────┐
│ Deployment Decision                          │
├──────────────────────────────────────────────┤
│                                              │
│ Reviewed by: (admin name)                    │
│ Notes: [                                  ]  │
│                                              │
│ [ Reject Challenger ]   [ Approve & Deploy ]  │
└──────────────────────────────────────────────┘
```

Rejecting should require a short reason (kept for audit history):

```text
Reason for rejection
[ Regression on Mosaic Virus recall — retry with class-weighted loss ]
[ Confirm Rejection ]
```

---

# 11. Deployment Pipeline

Once approved, show the rollout stage — retraining a good model is only half the job; how it reaches production matters just as much.

```text
Deployment Pipeline

Approved
   ↓
Staging Deployment
   ↓
Shadow Testing (predicts alongside champion, not shown to farmers)
   ↓
Canary Rollout (5% of traffic)
   ↓
Full Production Rollout
   ↓
Champion Updated
```

```text
┌──────────────────────────────────────────────┐
│ Tomato Disease Classifier — v2.4              │
├──────────────────────────────────────────────┤
│ ✅ Approved            26 Aug, 10:20 AM       │
│ ✅ Staging              26 Aug, 10:25 AM       │
│ ⏳ Shadow Testing        In progress (18h left)│
│ ⬜ Canary Rollout                              │
│ ⬜ Full Rollout                                │
└──────────────────────────────────────────────┘

[ View Shadow Test Results ]
[ Pause Rollout ]
```

### Shadow test results (expandable)
```text
Shadow Testing — Agreement with Champion

Predictions matched champion    91.2%
Predictions differed            8.8%
  Challenger more confident      6.1%
  Champion more confident        2.7%

No safety-relevant disagreements detected.
```

### Rollback control
Always show this — it's the safety net for the whole pipeline:
```text
[ ⏮ Rollback to Champion (v2.3) ]
```

---

# 12. Model Version History

```text
Model Version History — Tomato Disease Classifier
```

| Version | Deployed | Macro F1 | Status | Notes |
|---|---|---|---|---|
| v2.4 | 26 Aug 2026 | 0.931 | 🟢 Live (Canary 5%) | Retrained on feedback data |
| v2.3 | 02 Aug 2026 | 0.912 | Champion (rolling back if needed) | — |
| v2.2 | 14 Jul 2026 | 0.897 | Archived | — |
| v2.1 | 28 Jun 2026 | 0.884 | Archived | Initial disease taxonomy revision |

Clicking any version opens a read-only snapshot of its training config, dataset version, and evaluation report — for audit and reproducibility.

---

# 13. Dataset Versioning

Retraining runs should always be traceable to *which data* trained them.

```text
Dataset Versions — Tomato

Version   Images   Source                          Used In
v3        12,740   base + 340 feedback (26 Aug)     Run #128
v2        12,400   base dataset                      Run #126, #124
v1        9,800     original Kaggle/Mendeley import   Run #101
```

```text
[ View Dataset Diff v2 → v3 ]
```

---

# 14. Empty State

```text
┌──────────────────────────────────────┐
│                                      │
│              🧪                     │
│                                      │
│      No retraining runs yet          │
│                                      │
│ When a model needs retraining, it    │
│ will appear here — or start one      │
│ manually.                            │
│                                      │
│        [ + New Retraining Run ]      │
│                                      │
└──────────────────────────────────────┘
```

---

# 15. Error State

```text
⚠ Training run failed to start

The training service could not allocate
compute resources.

Last attempt:
26 Aug 2026, 2:14 PM

[ Retry ]
[ View Logs ]
```

---

# 16. Mobile Layout

```text
┌──────────────────────────────┐
│ 🧪 MLOps / Retraining    🔔  │
├──────────────────────────────┤
│                              │
│ ┌──────────┐ ┌──────────┐   │
│ │ Needs    │ │ Running  │   │
│ │ Retrain 2│ │ Now: 1   │   │
│ └──────────┘ └──────────┘   │
│                              │
│ Triggers                     │
│ 🔴 Pest Classifier — drift   │
│ ⚠ Tomato — confidence ↓      │
│                              │
│ Active Runs                  │
│ #128 Tomato — 70% (Epoch 14) │
│ #127 Pest — Awaiting Approval│
│                              │
│ [ View Run #127 ]            │
│                              │
│ Champion vs Challenger        │
│ Macro F1: 0.912 → 0.931 ↑    │
│                              │
│ [ Approve & Deploy ]         │
│ [ Reject ]                   │
└──────────────────────────────┘
```

Keep the config form (Section 7) and comparison table (Section 9) as full-screen modals on mobile rather than inline, since they carry the most decision-critical detail.

---

# 17. Recommended Screen Structure

```text
MLOps / RETRAINING
│
├── Global Filters
│
├── KPI Cards
│   ├── Needs Retrain
│   ├── Running Now
│   ├── Awaiting Approval
│   └── Deployed This Week
│
├── Retraining Triggers
│
├── New Retraining Run (config modal)
│
├── Active & Recent Training Runs
│   └── Run Detail (live metrics, logs, curve)
│
├── Champion vs Challenger Comparison
│   └── Per-Class Breakdown
│
├── Approval Decision
│
├── Deployment Pipeline
│   └── Shadow Testing Results
│
├── Model Version History
│
├── Dataset Versioning
│
└── Rollback Control
```

---

# 18. What I Recommend for Your Smart Farming V1

This is a hackathon/prototype-stage system, so avoid building a full enterprise CI/CD-for-ML platform.

### V1
```text
✓ Retraining triggers (fed by Drift Monitoring + Feedback)
✓ New retraining run config form
✓ Active/recent runs list with live progress
✓ Champion vs Challenger comparison table
✓ Manual approve/reject deployment decision
✓ Simple deploy (no canary — direct swap after approval)
✓ Model version history
✓ Empty/error states
```

### V2
```text
⭐ Per-class comparison breakdown
⭐ Dataset versioning + diff view
⭐ Shadow testing before rollout
⭐ Canary rollout (% traffic)
⭐ One-click rollback
```

### V3
```text
⭐ Fully automated trigger → retrain → shadow → canary pipeline
⭐ Automatic rollback on production metric regression
⭐ Multi-model orchestration (retrain dependent models together)
⭐ Scheduled/periodic retraining policies
```

---

# 19. The Most Important Feature for Your Project

Make **Trigger → Champion vs Challenger → Approval → Rollback** your signature flow — it's what turns your drift and feedback monitoring from passive dashboards into an actual closed-loop system:

```text
          RETRAINING TRIGGERED
        (drift / feedback / manual)
                    │
                    ▼
            Training Run Started
                    │
                    ▼
         Challenger Model Produced
                    │
                    ▼
      Champion vs Challenger Comparison
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Regression           Improvement
          │                   │
          ▼                   ▼
      Reject Run          Admin Approves
                              │
                              ▼
                     Deploy (staged/canary)
                              │
                              ▼
                    Monitor via Drift/Predictions
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                Stable              Regression Found
                    │                   │
                    ▼                   ▼
            New Champion          Rollback to
                                  Previous Champion
```

This closes the loop across your whole admin panel:

```text
Prediction Monitoring → Drift Monitoring → MLOps/Retraining →
Model Version Deployed → Prediction Monitoring (again)
```

That full cycle — not any single screen — is what makes the admin panel read as a real production ML system rather than a set of disconnected dashboards.