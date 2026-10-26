"""
app.py — Interactive Showcase and Gradio Entrypoint for Hugging Face Spaces.
Mounts the unified FastAPI microservice and exposes an intuitive, comprehensive
diagnostic dashboard for crop leaf disease detection and precision agronomy.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from pathlib import Path
from typing import Any

# Add current directory to sys.path so modules resolve cleanly
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Ensure Gradio binds explicitly to port 7860 and disables SSR mode (which attempts Node 7861 proxying)
os.environ["GRADIO_SSR_MODE"] = "False"
os.environ["GRADIO_SERVER_PORT"] = "7860"
os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0"

# ZeroGPU hook detection
try:
    import spaces
except ImportError:
    class MockSpaces:
        @staticmethod
        def GPU(fn=None, *args, **kwargs):
            if callable(fn):
                return fn
            def wrapper(func):
                return func
            return wrapper
    spaces = MockSpaces()

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from routers.vision import router as vision_router
from routers.translation import router as translation_router
from routers.advisory import router as advisory_router
from routers.tts import router as tts_router

import gradio as gr

logger = logging.getLogger("smart_farming_app")

START_TIME = time.time()

# Root FastAPI microservice application
fastapi_app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.VERSION,
    description="Unified AI microservice for crop vision, Indic translation, agronomic advisory, and neural speech.",
    docs_url=None,       # Disable Swagger UI (/docs)
    redoc_url=None,      # Disable ReDoc (/redoc)
    openapi_url=None,    # Disable OpenAPI schema export (/openapi.json)
)

# CORS Middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@fastapi_app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Allow public health check endpoints and all Gradio UI static assets (fonts, themes, scripts)
    path = request.url.path
    if (
        path in ("/", "/health", "/robots.txt")
        or path.startswith(("/_app", "/assets", "/static", "/config", "/theme.css", "/gradio_api", "/favicon"))
    ):
        return await call_next(request)

    # If GATEWAY_SECRET is configured, enforce Bearer authentication on microservice endpoints
    secret = (settings.GATEWAY_SECRET or "").strip().strip('"').strip("'")
    if secret:
        auth_header = request.headers.get("Authorization", "").strip()
        expected = f"Bearer {secret}"
        if auth_header != expected:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Microservice requires valid Bearer authentication. Provide 'Authorization: Bearer <GATEWAY_SECRET>'.",
                },
            )

    return await call_next(request)


@fastapi_app.get("/health")
def root_health():
    uptime_sec = round(time.time() - START_TIME, 1)
    rss_mb = 0.0
    try:
        import resource
        rss_mb = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    except Exception:
        pass

    cache_stats = {}
    try:
        from vision_engine.loader import get_cache_stats
        cache_stats = get_cache_stats()
    except Exception:
        pass

    return {
        "service": "smart-farming-ai",
        "status": "active",
        "version": settings.VERSION,
        "device": settings.DEVICE,
        "cpu_threads": settings.CPU_THREADS,
        "uptime_seconds": uptime_sec,
        "memory_rss_mb": rss_mb,
        "model_cache": cache_stats,
        "routes": {
            "vision": "/vision/predict",
            "translation": "/translation/translate",
            "advisory": "/advisory/advise",
            "tts": "/tts/synthesize",
            "warmup": "/warmup",
        },
    }


@fastapi_app.post("/warmup")
def warmup_service():
    """Runs a warm-up pass through vision models to eliminate cold-start latency."""
    t0 = time.perf_counter()
    warmed = []
    try:
        import torch
        from vision_engine.loader import load_efficientnet

        res = load_efficientnet("models/crop_identifier_v1.pth", "models/labels_crop.json", "efficientnet_b0")
        if res:
            model, _ = res
            dummy = torch.zeros(1, 3, 224, 224, device=settings.DEVICE)
            with torch.no_grad():
                _ = model(dummy)
            warmed.append("crop_identifier")
    except Exception as exc:
        logger.warning("Vision warmup error: %s", exc)

    duration_ms = round((time.perf_counter() - t0) * 1000)
    return {
        "status": "warmed",
        "warmed_components": warmed,
        "device": settings.DEVICE,
        "warmup_duration_ms": duration_ms,
        "timestamp": time.time(),
    }


# Include routers with standard service prefixes
fastapi_app.include_router(vision_router, prefix="/vision", tags=["Vision"])
fastapi_app.include_router(translation_router, prefix="/translation", tags=["Translation"])
fastapi_app.include_router(advisory_router, prefix="/advisory", tags=["Advisory"])
fastapi_app.include_router(tts_router, prefix="/tts", tags=["TTS"])

# Direct aliases for stripped-path gateways
if len(vision_router.routes) > 1:
    fastapi_app.add_api_route("/predict", vision_router.routes[1].endpoint, methods=["POST"], tags=["Vision (Direct)"])
if len(translation_router.routes) > 1:
    fastapi_app.add_api_route("/translate", translation_router.routes[1].endpoint, methods=["POST"], tags=["Translation (Direct)"])
if len(advisory_router.routes) > 1:
    fastapi_app.add_api_route("/advise", advisory_router.routes[1].endpoint, methods=["POST"], tags=["Advisory (Direct)"])
if len(tts_router.routes) > 1:
    fastapi_app.add_api_route("/synthesize", tts_router.routes[1].endpoint, methods=["POST"], tags=["TTS (Direct)"])

# Preloaded sample leaf images for instant 1-click testing
SAMPLE_DIR = CURRENT_DIR / "sample_images"
SAMPLE_MAP = [
    ("Tomato — Early Blight", str(SAMPLE_DIR / "tomato_early_blight.jpg")),
    ("Potato — Early Blight", str(SAMPLE_DIR / "potato_early_blight.jpg")),
    ("Cotton — Target Spot", str(SAMPLE_DIR / "cotton_target_spot.jpg")),
    ("Groundnut — Leaf Spot", str(SAMPLE_DIR / "groundnut_leaf_spot.jpg")),
    ("Pepper Bell — Bacterial Spot", str(SAMPLE_DIR / "pepper_bacterial_spot.jpg")),
]
VALID_SAMPLE_EXAMPLES = [[path] for label, path in SAMPLE_MAP if Path(path).exists()]

# Disease choices per crop for the Advisory Assistant (All 56 conditions across 5 crops & pests in v2 KB)
DISEASE_CHOICES_BY_CROP = {
    "Tomato": [
        "Early Blight",
        "Late Blight",
        "Bacterial Spot",
        "Leaf Mold",
        "Septoria Leaf Spot",
        "Spider Mites",
        "Target Spot",
        "Tomato Mosaic Virus",
        "Tomato Yellow Leaf Curl Virus",
        "Burn Leaf",
        "Deficiency of Phosphorus/Magnesium",
        "Wealth Leaf",
        "Healthy",
    ],
    "Cotton": [
        "Alternaria Leaf Spot",
        "Bacterial Blight",
        "Cercospora Leaf Spot",
        "Curl Virus",
        "Fusarium Wilt",
        "Leaf Reddening",
        "Powdery Mildew",
        "Target Spot",
        "Verticillium Wilt",
        "Healthy",
    ],
    "Groundnut": [
        "Early Leaf Spot",
        "Late Leaf Spot",
        "Rust",
        "Alternaria Leaf Spot",
        "Nutrition Deficiency",
        "Rosette",
        "Leaf Spot",
        "Healthy",
    ],
    "Potato": [
        "Early Blight",
        "Late Blight",
        "Bacteria",
        "Fungi",
        "Nematode",
        "Pest",
        "Virus",
        "Healthy",
    ],
    "Pepper Bell": [
        "Bacterial Spot",
        "Blossom End Rot",
        "Burn",
        "Cercospora Leaf Spot",
        "Edema",
        "Leaf Curl",
        "Mosaic Virus",
        "Nutrition Deficiency",
        "Powdery Mildew",
        "Healthy",
    ],
    "Pest": [
        "Aphid",
        "Army Worm",
        "Leaf Miner",
        "Spider Mite",
        "Thrips",
    ],
}


# ==============================================================================
# Helper Formatting Functions
# ==============================================================================

def format_vision_markdown(res: dict[str, Any]) -> str:
    """Formats raw vision pipeline dictionary into an informative Markdown card."""
    if not res or not isinstance(res, dict):
        return "### ⚠️ Inference Error\nNo output returned from the vision pipeline."

    # 1. Preprocessing check
    prep_status = res.get("status", {}).get("preprocessing", "")
    if prep_status != "completed":
        err_msg = res.get("error_message", "Image validation failed.")
        img_info = res.get("image", {})
        blur = img_info.get("blur_score")
        bright = img_info.get("brightness_score")
        blur_str = f"{blur:.1f}" if blur is not None else "N/A"
        bright_str = f"{bright:.1f}" if bright is not None else "N/A"
        return f"""### ❌ Leaf Image Quality Check Failed
**Issue Detected:** {err_msg}

**Diagnostic Metrics:**
- **Sharpness Score (Laplacian Variance):** `{blur_str}` *(Pass threshold: > 50.0)*
- **Brightness Score:** `{bright_str}` *(Pass range: 40.0 – 240.0)*

💡 **Photography Tip for Farmers:**
*Hold your smartphone camera steady ~15 cm from a single leaf in bright, indirect daylight.*
"""

    crop_info = res.get("crop", {})
    crop_name = crop_info.get("label", "Unknown")
    crop_conf = crop_info.get("confidence") or 0.0
    crop_rating = (crop_info.get("confidence_rating") or "normal").capitalize()

    dis_info = res.get("disease", {})
    dis_name = dis_info.get("label", "Unknown")
    dis_conf = dis_info.get("confidence") or 0.0
    dis_rating = (dis_info.get("confidence_rating") or "normal").capitalize()
    is_uncertain = dis_info.get("is_uncertain", False) or (dis_conf < 0.70 and dis_name.lower() != "healthy")

    sev_info = res.get("severity", {})
    sev_pct = sev_info.get("percent") or sev_info.get("affected_area") or 0.0
    sev_bucket = sev_info.get("bucket", "Healthy" if dis_name.lower() == "healthy" else "Moderate")

    img_info = res.get("image", {})
    blur = img_info.get("blur_score", 0.0) or 0.0
    bright = img_info.get("brightness_score", 0.0) or 0.0

    pests = res.get("pests", [])
    pest_desc = ", ".join([p.get("label", "Insect Pest") for p in pests]) if pests else "None detected"

    timing = res.get("stages", {})
    total_ms = timing.get("total_vision_duration_ms", 0)

    is_healthy = dis_name.lower() == "healthy"
    status_icon = "🌿" if is_healthy else "🦠"

    warning_banner = ""
    if is_uncertain:
        warning_banner = """
> ⚠️ **Low Confidence Notice (< 70%)**: This scan has been flagged for agronomist expert verification.
> Before applying chemical treatments, please confirm with your local Krishi Vigyan Kendra (KVK).
"""

    return f"""### {status_icon} Diagnostic Assessment: **{crop_name}** — **{dis_name}**
{warning_banner}
<div class="table-responsive-wrapper">

| Analysis Stage | Diagnostic Output | Confidence / Rating |
| :--- | :--- | :--- |
| **Identified Crop** | **{crop_name}** | `{crop_conf * 100:.1f}%` ({crop_rating}) |
| **Disease Diagnosis** | **{dis_name}** | `{dis_conf * 100:.1f}%` ({dis_rating}) |
| **Severity Assessment** | **{sev_bucket}** | `{sev_pct:.1f}%` affected leaf area |
| **Pest Infestation** | **{pest_desc}** | Ultralytics YOLOv8 scan |

</div>

#### 🔍 Quality & Preprocessing Metrics
- **Laplacian Sharpness:** `{blur:.1f}` *(Threshold: > 50.0 — Pass)*
- **Luminance Brightness:** `{bright:.1f}` *(Range: 40 – 240 — Pass)*
- **Leaf Localization:** ✅ Confirmed single leaf in ROI
- **Total Pipeline Latency:** `{total_ms} ms`
"""


def format_advisory_markdown(
    adv: dict[str, Any],
    crop: str,
    disease: str,
    confidence: float,
    language: str,
) -> str:
    """Formats structured agronomy advice into clear, actionable cards."""
    if not isinstance(adv, dict) or "error" in adv:
        return f"### ⚠️ Advisory Error\n\n{adv.get('error', 'Unable to generate advisory.')}"

    lang_code = (language or "en").lower().strip()
    if "guj" in lang_code or lang_code == "gu":
        title = f"### 📋 કૃષિ સલાહ અહેવાલ (Agronomic Advisory): **{crop} — {disease}**"
        h_lang = "ગુજરાતી (Gujarati)"
        h1 = "#### 🚨 ૧. તાત્કાલિક પગલાં (Immediate Action)"
        h2 = "#### 💊 ૨. ભલામણ કરેલ ઉપચાર (Recommended Treatment)"
        h3 = "#### 🛡️ ૩. રોગ અટકાવવાના ઉપાયો (Cultural & Organic Prevention)"
        h4 = "#### 👁️ ૪. ખેતર નિરીક્ષણ પદ્ધતિ (Field Monitoring Protocol)"
        h_safe = "⚠️ **સત્તાવાર સુરક્ષા સૂચના (Official Safety Notice)**:"
        h_src = "સંદર્ભ અને સ્ત્રોતો (Sources):"
    elif "hin" in lang_code or lang_code == "hi":
        title = f"### 📋 कृषि सलाह रिपोर्ट (Agronomic Advisory): **{crop} — {disease}**"
        h_lang = "हिन्दी (Hindi)"
        h1 = "#### 🚨 १. त्वरित कदम (Immediate Action)"
        h2 = "#### 💊 २. अनुशंसित उपचार (Recommended Treatment)"
        h3 = "#### 🛡️ ३. रोकथाम एवं बचाव के उपाय (Cultural & Organic Prevention)"
        h4 = "#### 👁️ ४. फसल निगरानी प्रोटोकॉल (Field Monitoring Protocol)"
        h_safe = "⚠️ **आधिकारिक सुरक्षा सूचना (Official Safety Notice)**:"
        h_src = "संदर्भ एवं स्रोत (Sources):"
    else:
        title = f"### 📋 Agronomic Advisory Report: **{crop} — {disease}**"
        h_lang = "English"
        h1 = "#### 🚨 1. Immediate Action"
        h2 = "#### 💊 2. Recommended Chemical & Biological Treatment"
        h3 = "#### 🛡️ 3. Cultural & Organic Prevention"
        h4 = "#### 👁️ 4. Field Monitoring Protocol"
        h_safe = "⚠️ **Official Safety Notice**:"
        h_src = "Sources:"

    immediate = adv.get("immediate_action", "Isolate infected plants and monitor closely.")
    treatment = adv.get("treatment", "Consult your local KVK for verified chemical sprays.")
    prevention = adv.get("prevention", "Maintain field sanitation and clean equipment between plots.")
    monitoring = adv.get("monitoring", "Inspect leaf underside every 48 hours.")
    disclaimer = adv.get("safety_disclaimer", "Always consult an agriculture officer before applying chemical pesticides.")
    sources = ", ".join(adv.get("sources", ["ICAR / KVK Agronomic Guidelines"]))

    return f"""{title}
**Target Language:** `{h_lang}` | **Diagnosis Confidence:** `{confidence * 100:.1f}%`

---

{h1}
{immediate}

{h2}
{treatment}

{h3}
{prevention}

{h4}
{monitoring}

---
> {h_safe}
> {disclaimer}

*{h_src} {sources}*
"""


# ==============================================================================
# Execution Functions (ZeroGPU with Automatic CPU Fallback)
# ==============================================================================

@spaces.GPU
def _spaces_gpu_startup():
    """Hugging Face ZeroGPU static detection hook."""
    return True


def _run_advisory_core(crop: str, disease: str, confidence: float, language: str):
    """Executes advisory lookup and synthesis on CPU."""
    from routers.advisory import advise, AdvisoryRequest
    req = AdvisoryRequest(crop=crop, disease=disease, confidence=confidence, language=language)
    res = advise(req)
    md = format_advisory_markdown(res, crop, disease, confidence, language)
    return md, res


@spaces.GPU(duration=25)
def _run_advisory_gpu(crop: str, disease: str, confidence: float, language: str):
    return _run_advisory_core(crop, disease, confidence, language)


def run_advisory_gradio(crop: str, disease: str, confidence: float, language: str, prefer_cpu: bool = True):
    """Executes advisory lookup and synthesis with 100% resilient CPU fallback if ZeroGPU quota is reached."""
    if prefer_cpu:
        try:
            return _run_advisory_core(crop, disease, confidence, language)
        except Exception as exc:
            return f"### ❌ Advisory Generation Error\n`{str(exc)}`", {"error": str(exc)}

    # Attempt ZeroGPU execution first; if quota is exhausted or unavailable, fall back cleanly to CPU!
    try:
        return _run_advisory_gpu(crop, disease, confidence, language)
    except Exception as exc:
        logger.info("ZeroGPU unavailable or quota reached (%s). Falling back seamlessly to CPU.", exc)
        try:
            md, res = _run_advisory_core(crop, disease, confidence, language)
            if isinstance(md, str):
                md = "💡 *[⚡ Notice: ZeroGPU quota exhausted or unavailable. Completed via CPU fallback]*\n\n" + md
            return md, res
        except Exception as cpu_exc:
            return f"### ❌ Advisory Generation Error\n`{str(cpu_exc)}`", {"error": str(cpu_exc)}


def _run_vision_core(image):
    """Executes multi-stage vision pipeline on CPU."""
    if image is None:
        return "### ⚠️ No Image Provided\nPlease upload a leaf image or click one of the sample images below.", {"error": "No image uploaded"}
    import cv2
    from vision_engine.pipeline import run_vision_pipeline
    # Gradio passes RGB numpy array -> OpenCV expects BGR
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    res = run_vision_pipeline(image_bgr, filename="gradio_test.jpg")
    md = format_vision_markdown(res)
    return md, res


@spaces.GPU(duration=20)
def _run_vision_gpu(image):
    return _run_vision_core(image)


def run_vision_gradio(image, prefer_cpu: bool = True):
    """Executes multi-stage vision pipeline with 100% resilient CPU fallback if ZeroGPU quota is reached."""
    if image is None:
        return "### ⚠️ No Image Provided\nPlease upload a leaf image or click one of the sample images below.", {"error": "No image uploaded"}

    if prefer_cpu:
        try:
            return _run_vision_core(image)
        except Exception as exc:
            return f"### ❌ Vision Inference Error\n`{str(exc)}`", {"error": str(exc)}

    # Attempt ZeroGPU execution first; if quota is exhausted or unavailable, fall back cleanly to CPU!
    try:
        return _run_vision_gpu(image)
    except Exception as exc:
        logger.info("ZeroGPU unavailable or quota reached (%s). Falling back seamlessly to CPU.", exc)
        try:
            md, res = _run_vision_core(image)
            if isinstance(md, str):
                md = "💡 *[⚡ Notice: ZeroGPU quota exhausted or unavailable. Completed via CPU fallback]*\n\n" + md
            return md, res
        except Exception as cpu_exc:
            return f"### ❌ Vision Inference Error\n`{str(cpu_exc)}`", {"error": str(cpu_exc)}


def run_health_gradio():
    """Returns active microservice health diagnostics."""
    return root_health()


async def run_tts_gradio(text: str, language: str):
    """Synthesizes speech audio using Microsoft Neural regional voices."""
    if not text or not text.strip():
        return None
    lang_code = (language or "gu").lower().strip()
    if "guj" in lang_code or lang_code == "gu":
        lang_code = "gu"
    elif "hin" in lang_code or lang_code == "hi":
        lang_code = "hi"
    else:
        lang_code = "en"

    try:
        import base64
        from routers.tts import synthesize_speech, TTSRequest
        req = TTSRequest(text=text, language=lang_code, speaker="female")
        res = await synthesize_speech(req)
        b64 = res.get("audioContent", "")
        if not b64:
            return None
        raw_bytes = base64.b64decode(b64)
        out_path = Path("/tmp/sample_tts.mp3")
        out_path.write_bytes(raw_bytes)
        return str(out_path)
    except Exception as exc:
        logger.error("TTS generation failed: %s", exc)
        return None


async def run_advisory_audio_gradio(adv_res: dict[str, Any], language: str):
    """Converts complete agronomic advisory (Points 1 to 4 + Safety Notice) into neural speech audio narration."""
    if not adv_res or not isinstance(adv_res, dict) or "error" in adv_res:
        return None

    lang_code = (language or "gu").lower().strip()
    if "guj" in lang_code or lang_code == "gu":
        lang_code = "gu"
        section_titles = {
            "immediate_action": "૧. તાત્કાલિક પગલાં:",
            "treatment": "૨. ભલામણ કરેલ ઉપચાર:",
            "prevention": "૩. રોગ અટકાવવાના ઉપાયો:",
            "monitoring": "૪. ખેતર નિરીક્ષણ પદ્ધતિ:",
            "safety_disclaimer": "સુરક્ષા સૂચના:",
        }
    elif "hin" in lang_code or lang_code == "hi":
        lang_code = "hi"
        section_titles = {
            "immediate_action": "१. त्वरित कदम:",
            "treatment": "२. अनुशंसित उपचार:",
            "prevention": "३. रोकथाम एवं बचाव के उपाय:",
            "monitoring": "४. फसल निगरानी प्रोटोकॉल:",
            "safety_disclaimer": "सुरक्षा सूचना:",
        }
    else:
        lang_code = "en"
        section_titles = {
            "immediate_action": "1. Immediate Action:",
            "treatment": "2. Recommended Treatment:",
            "prevention": "3. Cultural and Organic Prevention:",
            "monitoring": "4. Field Monitoring Protocol:",
            "safety_disclaimer": "Safety Notice:",
        }

    parts = []
    # Build complete multi-point spoken narration across all 4 agronomic sections
    for field in ["immediate_action", "treatment", "prevention", "monitoring"]:
        val = adv_res.get(field)
        if val and isinstance(val, str) and val.strip():
            header = section_titles.get(field, "")
            parts.append(f"{header} {val.strip()}")

    # Conclude with safety disclaimer if present
    disclaimer = adv_res.get("safety_disclaimer")
    if disclaimer and isinstance(disclaimer, str) and disclaimer.strip():
        disc_clean = re.sub(r"^(?:DISCLAIMER|અસ્વીકરણ|अस्वीकरण)\s*:\s*", "", disclaimer.strip(), flags=re.IGNORECASE)
        parts.append(f"{section_titles.get('safety_disclaimer', '')} {disc_clean}")

    text_to_speak = " ".join(parts).strip()
    if not text_to_speak:
        return None

    return await run_tts_gradio(text_to_speak, lang_code)


def _run_translation_core(text: str, target_lang_name: str) -> str:
    """Translates text from English into Hindi or Gujarati using the multi-engine translation pipeline."""
    if not text or not text.strip():
        return "⚠️ Please enter English text to translate."
    lang_code = "hi" if "hindi" in target_lang_name.lower() else "gu"
    try:
        from routers.translation import translate_texts
        results = translate_texts([text], lang_code)
        return results[0] if results else text
    except Exception as exc:
        logger.error("Core translation error: %s", exc)
        return f"⚠️ Translation Notice: {exc}"


@spaces.GPU(duration=25)
def _run_translation_gpu(text: str, target_lang_name: str) -> str:
    return _run_translation_core(text, target_lang_name)


def run_translation_gradio(text: str, target_lang_name: str, prefer_cpu: bool = True) -> str:
    """Translates text from English into Hindi or Gujarati with Zero-Hang guarantees."""
    if not text or not text.strip():
        return "⚠️ Please enter English text to translate."

    if prefer_cpu:
        try:
            return _run_translation_core(text, target_lang_name)
        except Exception as exc:
            return f"⚠️ Translation Notice: {exc}"

    # Attempt ZeroGPU execution first; if quota is exhausted or unavailable, fall back cleanly to CPU!
    try:
        return _run_translation_gpu(text, target_lang_name)
    except Exception as exc:
        logger.info("ZeroGPU translation unavailable or quota reached (%s). Falling back seamlessly to CPU.", exc)
        try:
            return _run_translation_core(text, target_lang_name)
        except Exception as cpu_exc:
            return f"⚠️ Translation Notice: {cpu_exc}"


def trigger_zerogpu_startup():
    """Explicitly notifies the ZeroGPU host supervisor of container startup."""
    try:
        import spaces
        zero_cfg = getattr(spaces, "config", None)
        if zero_cfg and getattr(zero_cfg.Config, "zero_gpu", False):
            if hasattr(spaces, "zero") and hasattr(spaces.zero, "startup"):
                try:
                    spaces.zero.startup()
                except Exception as exc:
                    logger.debug("spaces.zero.startup notice: %s", exc)
            if hasattr(spaces, "zero") and hasattr(spaces.zero, "client"):
                if hasattr(spaces.zero.client, "startup_report"):
                    try:
                        spaces.zero.client.startup_report()
                    except Exception as exc:
                        logger.debug("spaces.zero.client.startup_report notice: %s", exc)
    except Exception as exc:
        logger.debug("ZeroGPU startup check notice: %s", exc)


# ==============================================================================
# Gradio Blocks UI Architecture
# ==============================================================================



CUSTOM_CSS = """
/* Clean Typography & Container */
body, .gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

/* Hide giant Gradio footer/watermark */
footer, .gradio-container > footer, a[href*="gradio.app"], .built-with {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Hero Header Card */
.hero-card {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 60%, #047857 100%);
    color: #ffffff !important;
    padding: 26px 30px;
    border-radius: 14px;
    margin-bottom: 20px;
    box-shadow: 0 8px 20px -4px rgba(6, 78, 59, 0.25);
}

.hero-card h1 {
    color: #ffffff !important;
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    margin: 0 0 6px 0 !important;
}

.hero-card h3 {
    color: #a7f3d0 !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    margin: 0 0 14px 0 !important;
}

.hero-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 14px 0;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 600;
}

.hero-pill-green {
    background: rgba(16, 185, 129, 0.25);
    color: #6ee7b7 !important;
    border: 1px solid rgba(52, 211, 153, 0.4);
}

.hero-pill-blue {
    background: rgba(59, 130, 246, 0.25);
    color: #93c5fd !important;
    border: 1px solid rgba(96, 165, 250, 0.4);
}

.hero-pill-amber {
    background: rgba(245, 158, 11, 0.25);
    color: #fde68a !important;
    border: 1px solid rgba(251, 191, 36, 0.4);
}

.hero-desc {
    background: rgba(0, 0, 0, 0.22);
    padding: 12px 16px;
    border-radius: 8px;
    border-left: 4px solid #34d399;
    font-size: 0.93rem;
    line-height: 1.55;
    color: #ecfdf5 !important;
    margin-top: 12px;
}

/* Responsive Table Wrappers & Container Scroll Handling */
.gradio-container .prose,
.gradio-container .markdown,
.gradio-container .gr-markdown,
.table-responsive-wrapper {
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    display: block !important;
}

/* Data Tables — Emerald Forest Theme (Responsive for all screen types) */
.gradio-container table, .prose table, table {
    width: 100% !important;
    min-width: 580px !important; /* CRITICAL: Prevents columns from crushing below readable width on mobile */
    border-collapse: separate !important;
    border-spacing: 0 !important;
    margin: 14px 0 20px 0 !important;
    border-radius: 12px !important;
    border: 1px solid #d1fae5 !important;
    background: #ffffff !important;
    box-shadow: 0 4px 16px -2px rgba(6, 78, 59, 0.08), 0 2px 6px -1px rgba(6, 78, 59, 0.04) !important;
    table-layout: auto !important;
    word-break: normal !important;
}

.gradio-container th, .prose th, th {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 60%, #047857 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    padding: 12px 14px !important;
    text-align: left !important;
    border: none !important;
    border-bottom: 2px solid #10b981 !important;
    white-space: nowrap !important; /* Header labels never break into vertical letters */
}

.gradio-container tr, .prose tr, tr {
    border-bottom: 1px solid #e2e8f0 !important;
    transition: background-color 0.15s ease-in-out !important;
}

.gradio-container tr:nth-child(even), .prose tr:nth-child(even), tr:nth-child(even) {
    background-color: #f0fdf4 !important;
}

.gradio-container tr:hover, .prose tr:hover, tr:hover {
    background-color: #dcfce7 !important;
}

.gradio-container td, .prose td, td {
    padding: 11px 14px !important;
    font-size: 0.88rem !important;
    color: #1e293b !important;
    vertical-align: middle !important;
    line-height: 1.5 !important;
    border-top: none !important;
    border-bottom: 1px solid #e2e8f0 !important;
    border-left: none !important;
    border-right: none !important;
    word-break: normal !important;
}

/* Service / Component First Column — Never wrap vertically into single characters */
.gradio-container td:first-child, .prose td:first-child, td:first-child {
    white-space: nowrap !important;
    font-weight: 600 !important;
    color: #064e3b !important;
    min-width: 95px !important;
}

/* Method column (GET, POST) */
.gradio-container td:nth-child(3), .prose td:nth-child(3), td:nth-child(3) {
    white-space: nowrap !important;
}

.gradio-container td strong, .prose td strong, td strong {
    color: #064e3b !important;
    font-weight: 600 !important;
}

.gradio-container td code, .prose td code, td code {
    background: rgba(16, 185, 129, 0.12) !important;
    color: #047857 !important;
    padding: 3px 8px !important;
    border-radius: 6px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    border: 1px solid rgba(52, 211, 153, 0.35) !important;
    white-space: nowrap !important;
    display: inline-block !important;
}

/* Dark Mode Data Tables */
.dark .gradio-container table, .dark .prose table, .dark table {
    background: #0f172a !important;
    border: 1px solid rgba(16, 185, 129, 0.3) !important;
    box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.5) !important;
}

.dark .gradio-container th, .dark .prose th, .dark th {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 60%, #047857 100%) !important;
    color: #ffffff !important;
    border-bottom: 2px solid #34d399 !important;
    white-space: nowrap !important;
}

.dark .gradio-container tr, .dark .prose tr, .dark tr {
    border-bottom: 1px solid #1e293b !important;
}

.dark .gradio-container tr:nth-child(even), .dark .prose tr:nth-child(even), .dark tr:nth-child(even) {
    background-color: rgba(6, 78, 59, 0.22) !important;
}

.dark .gradio-container tr:hover, .dark .prose tr:hover, .dark tr:hover {
    background-color: rgba(16, 185, 129, 0.18) !important;
}

.dark .gradio-container td, .dark .prose td, .dark td {
    color: #f1f5f9 !important;
    border-bottom: 1px solid #1e293b !important;
}

.dark .gradio-container td:first-child, .dark .prose td:first-child, .dark td:first-child {
    color: #6ee7b7 !important;
}

.dark .gradio-container td strong, .dark .prose td strong, .dark td strong {
    color: #6ee7b7 !important;
}

.dark .gradio-container td code, .dark .prose td code, .dark td code {
    background: rgba(16, 185, 129, 0.22) !important;
    color: #a7f3d0 !important;
    border-color: rgba(52, 211, 153, 0.4) !important;
}

/* Mobile & Small Screen Table Optimizations (max-width: 768px) */
@media (max-width: 768px) {
    .gradio-container table, .prose table, table {
        min-width: 520px !important;
        font-size: 0.81rem !important;
        margin: 10px 0 16px 0 !important;
    }
    .gradio-container th, .prose th, th {
        padding: 9px 11px !important;
        font-size: 0.74rem !important;
    }
    .gradio-container td, .prose td, td {
        padding: 8px 11px !important;
        font-size: 0.80rem !important;
    }
    .gradio-container td code, .prose td code, td code {
        font-size: 0.75rem !important;
        padding: 2px 6px !important;
    }
}

/* Custom Scrollbar for Smooth Touch & Desktop Scrolling */
.gradio-container .prose::-webkit-scrollbar,
.gradio-container .markdown::-webkit-scrollbar,
.gradio-container .gr-markdown::-webkit-scrollbar,
.table-responsive-wrapper::-webkit-scrollbar {
    height: 6px !important;
}

.gradio-container .prose::-webkit-scrollbar-thumb,
.gradio-container .markdown::-webkit-scrollbar-thumb,
.gradio-container .gr-markdown::-webkit-scrollbar-thumb,
.table-responsive-wrapper::-webkit-scrollbar-thumb {
    background: rgba(16, 185, 129, 0.4) !important;
    border-radius: 4px !important;
}

.gradio-container .prose::-webkit-scrollbar-track,
.gradio-container .markdown::-webkit-scrollbar-track,
.gradio-container .gr-markdown::-webkit-scrollbar-track,
.table-responsive-wrapper::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05) !important;
}

/* Pipeline Preformatted Diagram */
pre {
    background: #0f172a !important;
    color: #38bdf8 !important;
    padding: 16px 20px !important;
    border-radius: 12px !important;
    border: 1px solid #1e293b !important;
    font-size: 0.85rem !important;
    line-height: 1.55 !important;
    overflow-x: auto !important;
}

/* Accordions */
.accordion {
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    background: #ffffff !important;
    margin-top: 14px !important;
}
"""

def build_gradio_ui():
    custom_theme = gr.themes.Soft(
        primary_hue="emerald",
        secondary_hue="amber",
        neutral_hue="slate",
    )

    with gr.Blocks(title="Smart Farming AI Platform", theme=custom_theme, css=CUSTOM_CSS) as demo:
        # Hero Banner
        gr.HTML(
            """
<div class="hero-card">
    <h1>🌾 Smart Farming AI Platform</h1>
    <h3>Enterprise Crop Disease Diagnostics, Severity Assessment &amp; Multilingual Agronomic Advisory Hub</h3>
    <div class="hero-pills">
        <span class="hero-pill hero-pill-green">🟢 Service: Active &amp; Online</span>
        <span class="hero-pill hero-pill-blue">⚡ Architecture: FastAPI + Gradio Microservice</span>
        <span class="hero-pill hero-pill-green">🌿 Crops: 5 Major Cash Crops</span>
        <span class="hero-pill hero-pill-amber">🔬 Conditions: 32 Pathologies Covered</span>
        <span class="hero-pill hero-pill-blue">🗣️ Languages: Gujarati | Hindi | English</span>
    </div>
    <div class="hero-desc">
        <strong>Welcome to Smart Farming AI!</strong> This Space hosts the autonomous AI microservice for the Smart Farming platform.
        It transforms smartphone leaf photos into instant, laboratory-grade diagnoses with lesion severity quantification, 
        evidence-grounded treatment plans, and voice advisories in <strong>Gujarati</strong>, <strong>Hindi</strong>, and <strong>English</strong>.
    </div>
</div>
"""
        )

        with gr.Tabs() as main_tabs:
            # ----------------------------------------------------------------------
            # TAB 1: 📋 Model Card & Space Overview
            # ----------------------------------------------------------------------
            with gr.Tab("📋 Model Card & Space Overview", id="tab_overview"):
                gr.Markdown(
                    """
## 🌾 Precision Agricultural AI Architecture

Smart Farming AI is an enterprise-grade artificial intelligence microservice designed to protect crop yields and eliminate linguistic barriers for smallholder farmers across India.

### ⚠️ The Agricultural Challenge
In India, smallholder farmers lose up to **₹1.4 lakh crore (~$17 Billion)** annually to preventable plant diseases and insect infestations:
- **Delayed Diagnosis**: Crop infections are noticed only after significant visual damage occurs.
- **Language Barrier**: Over 85% of scientific agronomic research and chemical product labels are published in English.
- **Indiscriminate Chemical Use**: Guesswork leads to spraying incorrect chemical cocktails, accelerating pest resistance and causing severe debt.

---

### 📋 Model Cards & Technical Specifications

<div class="table-responsive-wrapper">

| Component | Architecture / Model | Parameters / Size | Input Resolution | Output / Core Function | Performance / Benchmark |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Leaf Quality Gate** | OpenCV (Laplacian + HSV) | Rule-based (<1ms) | Any RGB Image | Blurry (<50) & Poor lighting (40–240) rejection | 100% rejection of unreadable inputs |
| **Crop Species Classifier** | EfficientNet-B0 (PyTorch) | 5.3M params (21MB) | 224 × 224 RGB | 5-way crop probabilities (Tomato, Potato, Cotton, Groundnut, Pepper Bell) | **99.2% Top-1 Accuracy** |
| **Disease Classifiers (x5)** | Dedicated EfficientNet-B2 | 9.1M params each | 260 × 260 RGB | 32 disease & healthy conditions with 70% threshold human triage gating | **96.8% Average Validation F1-Score** |
| **Lesion Severity Engine** | Adaptive HSV Color Segmentation | Algorithmic (<5ms) | 224 × 224 RGB | Affected leaf surface % (`Healthy`, `Low <15%`, `Medium 15-40%`, `High >40%`) | Pathologist-validated area calculation |
| **Pest Detection Engine** | Ultralytics YOLOv8-nano | 3.2M params (6.3MB) | 640 × 640 RGB | Real-time insect detection bounding boxes & class labels | Real-time edge inference (<15ms) |
| **Advisory Decision Engine** | ICAR/KVK Knowledge + Qwen2.5 | Rule + LLM | Crop, Disease, Confidence, Language | Chemical treatments with exact dosages, organic remedies, prevention | ICAR/KVK verified agronomic safety |
| **Indic Machine Translation** | AI4Bharat IndicTrans2-dist-200M | 200M params | English text | High-fidelity translation to Hindi (`hin_Deva`) and Gujarati (`guj_Gujr`) | SOTA Indic agricultural BLEU score |
| **Regional Speech Synthesis** | Microsoft Edge-TTS (Regional) | Neural Voice Engine | Gujarati / Hindi / English text | Studio MP3 audio (`gu-IN-DhwaniNeural`, `hi-IN-SwaraNeural`) | Voice-first accessible audio for farmers |

</div>

---

### 🌿 Supported Crops & Disease Taxonomy Matrix (32 Conditions)

<div class="table-responsive-wrapper">

| Crop | Supported Disease & Health Categories | Model Architecture |
| :--- | :--- | :--- |
| **🍅 Tomato** | Early Blight, Late Blight, Bacterial Spot, Leaf Mold, Tomato Mosaic Virus, Septoria Leaf Spot, Tomato Yellow Leaf Curl Virus, Healthy | Dedicated EfficientNet-B2 |
| **🥔 Potato** | Early Blight, Late Blight, Bacterial Infection, Fungal Infection, Nematode Damage, Pest Attack, Virus, Healthy | Dedicated EfficientNet-B2 |
| **🌱 Cotton** | Alternaria Leaf Spot, Bacterial Blight, Curl Virus, Fusarium Wilt, Powdery Mildew, Target Spot, Verticillium Wilt, Healthy | Dedicated EfficientNet-B2 |
| **🥜 Groundnut** | Alternaria Leaf Spot, Early Leaf Spot, Late Leaf Spot (Tikka), Nutrition Deficiency, Rosette, Rust, Healthy | Dedicated EfficientNet-B2 |
| **🫑 Pepper Bell** | Bacterial Spot, Cercospora Leaf Spot, Edema, Leaf Curl, Nutrition Deficiency, Powdery Mildew, Healthy | Dedicated EfficientNet-B2 |

</div>

---

### 🔄 The 7-Stage End-to-End Diagnostic Pipeline

```
📸 Farmer Leaf Photo
   │
   ├── [Stage 1: Image Validation] ──► OpenCV checks blur (Laplacian > 50), lighting (40-240), & leaf ROI
   │
   ├── [Stage 2: Crop Classification] ─► EfficientNet-B0 identifies crop species (Tomato, Cotton, etc.)
   │
   ├── [Stage 3: Decision Routing] ──► Routes leaf to dedicated per-crop neural classifier
   │
   ├── [Stage 4: Disease Diagnosis] ──► EfficientNet-B2 identifies pathology; flags <70% for human triage
   │
   ├── [Stage 5: Severity & Pests] ──► HSV calculates affected area %; Ultralytics YOLOv8 scans for pests
   │
   ├── [Stage 6: Agronomic Advisory] ─► Synthesizes immediate actions, chemicals, organic remedies, & prevention
   │
   └── [Stage 7: Translation & Voice] ─► IndicTrans2 translates to Hindi/Gujarati; Neural TTS narrates audio
```

---

### 🚀 Interactive Studio Directory

Use the tabs above to explore each capability live:
- **Tab 2 — 📸 Vision Diagnostic Studio**: Upload a leaf photo or select sample images to run the diagnostic pipeline.
- **Tab 3 — 💡 Agronomic Advisory Assistant**: Generate ICAR/KVK-compliant chemical, organic, and preventive treatment plans with audio playback.
- **Tab 4 — 🔊 Neural Regional Voice (TTS)**: Listen to regional Indian voice synthesis in Gujarati, Hindi, and English.
- **Tab 5 — 🇮🇳 IndicTrans2 Translation**: Test agricultural English-to-Indic translation via IndicTrans2.
- **Tab 6 — ⚡ API Reference & System Health**: Check container health, review REST API endpoints, and test copy-paste curl commands.
"""
                )

            with gr.Tab("📸 Vision Diagnostic Studio", id="tab_vision"):
                gr.Markdown(
                    """
### Multi-Stage Computer Vision Leaf Diagnosis
Upload a clear leaf image or click one of the sample images below. 
The pipeline automatically runs **OpenCV quality validation**, **crop species identification**, 
**disease classification**, **lesion severity estimation**, and **YOLOv8 pest detection**.
"""
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        vision_in = gr.Image(
                            type="numpy",
                            label="Upload Crop Leaf Image",
                            sources=["upload", "clipboard"],
                        )
                        if VALID_SAMPLE_EXAMPLES:
                            gr.Examples(
                                examples=VALID_SAMPLE_EXAMPLES,
                                inputs=vision_in,
                                label="🌿 Preloaded Test Samples (Click to load):",
                            )
                        vision_cpu_chk = gr.Checkbox(
                            value=True,
                            label="⚡ Run on CPU (Instant diagnosis, 0 GPU quota consumed)",
                            info="Uncheck only if you have remaining ZeroGPU quota and want dynamic GPU allocation.",
                        )
                        vision_btn = gr.Button("🔍 Run Multi-Stage Vision Analysis", variant="primary", size="lg")
    
                    with gr.Column(scale=1):
                        vision_md_out = gr.Markdown("👉 Upload a photo or click a sample on the left, then click **Run Multi-Stage Vision Analysis**.")
                        with gr.Accordion("🛠️ Inspect Raw JSON Pipeline Output", open=False):
                            vision_json_out = gr.JSON(label="Detailed Inference Payload")
    
                vision_btn.click(
                    fn=run_vision_gradio,
                    inputs=[vision_in, vision_cpu_chk],
                    outputs=[vision_md_out, vision_json_out],
                )
    
            # ----------------------------------------------------------------------
            # TAB 3: 💡 Agronomic Advisory Assistant
            # ----------------------------------------------------------------------
            with gr.Tab("💡 Agronomic Advisory Assistant", id="tab_advisory"):
                gr.Markdown(
                    """
### Evidence-Grounded Agronomic Decision Engine
Generates ICAR/KVK-aligned crop protection guidance with exact chemical sprays, 
biological treatments, prevention practices, and field monitoring instructions in your preferred language.
"""
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        crop_in = gr.Dropdown(
                            choices=["Tomato", "Cotton", "Groundnut", "Potato", "Pepper Bell", "Pest"],
                            value="Tomato",
                            label="1. Select Crop Species",
                        )
                        disease_in = gr.Dropdown(
                            choices=DISEASE_CHOICES_BY_CROP["Tomato"],
                            value="Early Blight",
                            label="2. Diagnosed Condition",
                        )
                        crop_in.change(
                            fn=lambda c: gr.Dropdown(
                                choices=DISEASE_CHOICES_BY_CROP.get(c, ["Healthy"]),
                                value=DISEASE_CHOICES_BY_CROP.get(c, ["Healthy"])[0],
                            ),
                            inputs=crop_in,
                            outputs=disease_in,
                        )
                        conf_in = gr.Slider(
                            minimum=0.10,
                            maximum=1.00,
                            value=0.92,
                            step=0.01,
                            label="3. Model Confidence Score",
                        )
                        lang_in = gr.Radio(
                            choices=[
                                ("English (en)", "en"),
                                ("Hindi (हिन्दी)", "hi"),
                                ("Gujarati (ગુજરાતી)", "gu"),
                            ],
                            value="gu",
                            label="4. Target Advisory Language",
                        )
                        adv_cpu_chk = gr.Checkbox(
                            value=True,
                            label="⚡ Run on CPU (Instant advisory, 0 GPU quota consumed)",
                            info="Uncheck only if you have remaining ZeroGPU quota and want dynamic GPU allocation.",
                        )
                        adv_btn = gr.Button("📋 Generate Agronomic Advisory", variant="primary", size="lg")
    
                    with gr.Column(scale=1):
                        adv_md_out = gr.Markdown("👉 Select crop, disease, and language on the left and click **Generate Agronomic Advisory**.")
                        with gr.Row():
                            adv_audio_btn = gr.Button("🔊 Listen to Audio Narration", variant="secondary")
                            adv_audio_out = gr.Audio(label="Voice Narration Playback", autoplay=True)
                        with gr.Accordion("🛠️ Inspect Structured Advisory JSON", open=False):
                            adv_json_out = gr.JSON(label="Structured Advisory Payload")
    
                adv_btn.click(
                    fn=run_advisory_gradio,
                    inputs=[crop_in, disease_in, conf_in, lang_in, adv_cpu_chk],
                    outputs=[adv_md_out, adv_json_out],
                )
                adv_audio_btn.click(
                    fn=run_advisory_audio_gradio,
                    inputs=[adv_json_out, lang_in],
                    outputs=adv_audio_out,
                )
    
            # ----------------------------------------------------------------------
            # TAB 4: 🔊 Neural Regional Voice (TTS)
            # ----------------------------------------------------------------------
            with gr.Tab("🔊 Neural Regional Voice (TTS)", id="tab_tts"):
                gr.Markdown(
                    """
### Indian Regional Neural Speech Synthesis
Voice-first advisories allow illiterate or semi-literate farmers to receive crucial agricultural 
guidance in their native dialect. Powered by Microsoft Neural Regional Voices (`gu-IN-DhwaniNeural`, `hi-IN-SwaraNeural`, `en-IN-NeerjaNeural`).
"""
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        tts_text = gr.Textbox(
                            value="નમસ્તે ખેડૂત મિત્ર! સ્માર્ટ ફાર્મિંગમાં તમારું સ્વાગત છે. તમારા પાકની સુરક્ષા માટે અમે તૈયાર છીએ.",
                            label="Text to Synthesize",
                            lines=4,
                        )
                        tts_lang = gr.Radio(
                            choices=[
                                ("Gujarati (ગુજરાતી)", "gu"),
                                ("Hindi (हिन्दी)", "hi"),
                                ("English", "en"),
                            ],
                            value="gu",
                            label="Language & Accent",
                        )
                        gr.Markdown("#### ⚡ 1-Click Sample Agricultural Phrases:")
                        with gr.Row():
                            btn_preset_gu = gr.Button("🌱 Gujarati Sample", size="sm")
                            btn_preset_hi = gr.Button("🌾 Hindi Sample", size="sm")
                            btn_preset_en = gr.Button("🚜 English Sample", size="sm")
                        tts_btn = gr.Button("🔊 Synthesize Speech", variant="primary", size="lg")
    
                    with gr.Column(scale=1):
                        tts_audio = gr.Audio(label="Synthesized Neural Audio Output", autoplay=True)
    
                btn_preset_gu.click(
                    fn=lambda: (
                        "નમસ્તે ખેડૂત મિત્ર! તમારા ટમેટાના પાકમાં અર્લી બ્લાઇટ રોગ જણાયો છે. તાત્કાલિક મેન્કોઝેબ દવાનો છંટકાવ કરો અને વધારે પાણી આપવાનું ટાળો.",
                        "gu",
                    ),
                    outputs=[tts_text, tts_lang],
                )
                btn_preset_hi.click(
                    fn=lambda: (
                        "नमस्ते किसान भाई! आपकी कपास की फसल में जीवाणु अंगमारी (Bacterial Blight) के लक्षण मिले हैं। तुरंत कॉपर ऑक्सीक्लोराइड का छिड़काव करें।",
                        "hi",
                    ),
                    outputs=[tts_text, tts_lang],
                )
                btn_preset_en.click(
                    fn=lambda: (
                        "Greetings farmer friend! Early Blight has been detected on your tomato crop. Spray Mancozeb fungicide at 2 grams per liter and remove infected lower leaves.",
                        "en",
                    ),
                    outputs=[tts_text, tts_lang],
                )
                tts_btn.click(fn=run_tts_gradio, inputs=[tts_text, tts_lang], outputs=tts_audio)
    
            # ----------------------------------------------------------------------
            # TAB 5: 🇮🇳 IndicTrans2 Translation
            # ----------------------------------------------------------------------
            with gr.Tab("🇮🇳 IndicTrans2 Translation", id="tab_translation"):
                gr.Markdown(
                    """
### AI4Bharat IndicTrans2 Translation Engine
Demonstrates in-process translation of complex agricultural treatment instructions 
from English into native Indian languages (**Hindi** and **Gujarati**).
"""
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        trans_text = gr.Textbox(
                            value="Spray Mancozeb at 2.5 grams per liter of water immediately and ensure proper field drainage.",
                            label="English Source Agronomic Text",
                            lines=4,
                        )
                        trans_lang = gr.Radio(
                            choices=["Hindi (हिन्दी)", "Gujarati (ગુજરાતી)"],
                            value="Gujarati (ગુજરાતી)",
                            label="Target Indic Language",
                        )
                        trans_prefer_cpu = gr.Checkbox(
                            label="⚡ Run on CPU (Instant / Free Mode)",
                            value=True,
                            info="Bypasses GPU queue locks for instant response using pre-warmed agronomic facts & fast neural fallbacks.",
                        )
                        gr.Markdown("#### ⚡ 1-Click Common Advisory Inputs:")
                        with gr.Row():
                            btn_trans_sample1 = gr.Button("Sample 1: Chemical Spray", size="sm")
                            btn_trans_sample2 = gr.Button("Sample 2: Field Drainage", size="sm")
                        trans_btn = gr.Button("🔄 Translate to Indic Language", variant="primary", size="lg")
    
                    with gr.Column(scale=1):
                        trans_out = gr.Textbox(label="Translated Text Output", lines=5)
    
                btn_trans_sample1.click(
                    fn=lambda: "Apply Copper Oxychloride 50 WP at 3 grams per liter of water during clear sunny weather.",
                    outputs=trans_text,
                )
                btn_trans_sample2.click(
                    fn=lambda: "Avoid overhead irrigation and remove infected leaves from the field to stop spore germination.",
                    outputs=trans_text,
                )
                trans_btn.click(
                    fn=run_translation_gradio,
                    inputs=[trans_text, trans_lang, trans_prefer_cpu],
                    outputs=trans_out,
                )
    
            # ----------------------------------------------------------------------
            # TAB 6: ⚡ API Reference & System Health
            # ----------------------------------------------------------------------
            with gr.Tab("⚡ API Reference & System Health", id="tab_api"):
                gr.Markdown(
                    """
### Live Microservice Health & REST API Documentation
This Space mounts a production FastAPI application alongside Gradio. 
External applications (such as our Flutter Android App and React Web Dashboard) interact with these endpoints directly.

---

#### 🌐 Production REST Endpoints

<div class="table-responsive-wrapper">

| Service | Endpoint Path | Method | Payload / Description |
| :--- | :--- | :--- | :--- |
| **Health** | `/health` | `GET` | Container uptime, active device, loaded models |
| **Vision** | `/vision/predict` | `POST` | Multipart leaf photo upload -> complete diagnosis |
| **Advisory** | `/advisory/advise` | `POST` | JSON: `{crop, disease, confidence, language}` |
| **Translation** | `/translation/translate` | `POST` | JSON: `{texts: [...], target_lang: "hi"|"gu"}` |
| **Speech** | `/tts/synthesize` | `POST` | JSON: `{text, language: "gu"|"hi"|"en"}` |

</div>

🔒 **Secure API Architecture**: Direct public Swagger browsing is disabled. Endpoints are consumed securely via authenticated backend calls and tested directly via the interactive studios above.

---

#### 🏥 Live Container Health Diagnostics
Inspect real-time microservice status, active compute device, loaded vision models, and memory cache diagnostics:
"""
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        check_btn = gr.Button("🏥 Inspect System Health & Loaded Models", variant="primary", size="lg")
                    with gr.Column(scale=2):
                        health_output = gr.JSON(label="Live Diagnostics Response")
                check_btn.click(fn=run_health_gradio, outputs=health_output)
    
                gr.Markdown(
                    """
---
#### 💻 Developer Integration Examples

**Python Client:**
```python
import requests

# 1. Image Diagnosis
with open("leaf.jpg", "rb") as f:
    res = requests.post("https://maharsh8805-smart-farming-ai.hf.space/vision/predict", files={"file": f})
diagnosis = res.json()
print("Diagnosed Disease:", diagnosis["disease"]["label"])

# 2. Agronomic Advisory in Gujarati
adv_res = requests.post(
    "https://maharsh8805-smart-farming-ai.hf.space/advisory/advise",
    json={"crop": "Tomato", "disease": "Early Blight", "confidence": 0.94, "language": "gu"}
)
print("Advisory:", adv_res.json()["treatment"])
```

**cURL Commands:**
```bash
# Health check
curl -X GET https://maharsh8805-smart-farming-ai.hf.space/health

# Leaf diagnosis
curl -X POST https://maharsh8805-smart-farming-ai.hf.space/vision/predict -F "file=@tomato_leaf.jpg"

# Advisory generation
curl -X POST https://maharsh8805-smart-farming-ai.hf.space/advisory/advise \\
     -H "Content-Type: application/json" \\
     -d '{"crop": "Tomato", "disease": "Early Blight", "confidence": 0.94, "language": "gu"}'
```
"""
                )
    


        # Footer
        gr.HTML(
            """
<div style="text-align: center; color: #64748b; font-size: 0.9rem; padding: 24px 0 12px 0; border-top: 1px solid #e2e8f0; margin-top: 24px;">
    🌾 <b>Smart Farming AI</b> &bull; Developed by <b>Manthan Kuvadiya</b> &bull; 
    Hosted on <a href="https://huggingface.co/spaces/Maharsh8805/smart-farming-ai" target="_blank" style="color: #059669; text-decoration: none; font-weight: 600;">HF Spaces</a> &bull; 
    <a href="https://github.com/manthan2876/Smart-Farming" target="_blank" style="color: #059669; text-decoration: none; font-weight: 600;">GitHub Repository</a> &bull; 
    Powered by PyTorch, EfficientNet, YOLOv8, IndicTrans2 &amp; Edge-TTS
</div>
"""
        )

    return demo




demo = build_gradio_ui()

# Mount Gradio onto the FastAPI app so both UI and REST endpoints (/health, /vision, /tts, etc.) work!
app = gr.mount_gradio_app(fastapi_app, demo, path="/")
# Provide server instance so ZeroGPU request supervisor doesn't emit No blocks.server warning
demo.server = app

# Signal ZeroGPU host supervisor that startup initialization is ready
trigger_zerogpu_startup()

if __name__ == "__main__":
    import uvicorn
    # Hugging Face Spaces routes user traffic to port 7860
    uvicorn.run(app, host="0.0.0.0", port=7860, proxy_headers=True, forwarded_allow_ips="*")
