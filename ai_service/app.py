"""
app.py — Gradio Space Entrypoint for Hugging Face Spaces.
Mounts the unified FastAPI microservice and exposes an interactive test dashboard.
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

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

import gradio as gr
from main import app as fastapi_app, root_health


@spaces.GPU
def _spaces_gpu_startup():
    """Hugging Face ZeroGPU static detection hook."""
    return True


@spaces.GPU(duration=120)
def run_advisory_gradio(crop: str, disease: str, confidence: float, language: str):
    from routers.advisory import advise, AdvisoryRequest
    req = AdvisoryRequest(crop=crop, disease=disease, confidence=confidence, language=language)
    return advise(req)


@spaces.GPU(duration=30)
def run_vision_gradio(image):
    if image is None:
        return {"error": "No image uploaded"}
    import cv2
    from vision_engine.pipeline import run_vision_pipeline
    # Gradio passes RGB numpy array
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return run_vision_pipeline(image_bgr, filename="gradio_test.jpg")


def run_health_gradio():
    return root_health()


async def run_tts_gradio(text: str, language: str):
    import base64
    from routers.tts import synthesize_speech, TTSRequest
    req = TTSRequest(text=text, language=language, speaker="female")
    res = await synthesize_speech(req)
    b64 = res.get("audioContent", "")
    raw_bytes = base64.b64decode(b64)
    out_path = Path("/tmp/sample_tts.mp3")
    out_path.write_bytes(raw_bytes)
    return str(out_path)


def build_gradio_ui():
    with gr.Blocks(title="Smart Farming AI Hub", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🌾 Smart Farming AI Microservice")
        gr.Markdown(
            "Unified AI backend for **Crop Vision**, **IndicTrans2 Translation**, **Agronomic Advisory**, and **Neural Speech**.\n\n"
            "This Space serves as the standalone AI microservice called directly by the main backend."
        )

        with gr.Tab("System & Health Diagnostics"):
            gr.Markdown("Click below to test the FastAPI backend status:")
            check_btn = gr.Button("Inspect System Health", variant="primary")
            health_output = gr.JSON(label="Health Diagnostic Response")
            check_btn.click(fn=run_health_gradio, outputs=health_output)

        with gr.Tab("Advisory Test"):
            with gr.Row():
                crop_in = gr.Dropdown(
                    ["Tomato", "Cotton", "Groundnut", "Potato", "Pepper_Bell"],
                    value="Tomato",
                    label="Crop",
                )
                disease_in = gr.Textbox(value="Early Blight", label="Disease")
                conf_in = gr.Slider(0.1, 1.0, value=0.92, label="Confidence")
                lang_in = gr.Radio(["en", "hi", "gu"], value="gu", label="Language")

            adv_btn = gr.Button("Generate Agronomic Advisory", variant="primary")
            adv_output = gr.JSON(label="Structured Advisory Output")
            adv_btn.click(
                fn=run_advisory_gradio,
                inputs=[crop_in, disease_in, conf_in, lang_in],
                outputs=adv_output,
            )

        with gr.Tab("Vision Test"):
            with gr.Row():
                vision_in = gr.Image(type="numpy", label="Upload Crop Leaf Image")
                vision_out = gr.JSON(label="Vision Inference Result")
            vision_btn = gr.Button("Run Vision Analysis", variant="primary")
            vision_btn.click(fn=run_vision_gradio, inputs=vision_in, outputs=vision_out)

        with gr.Tab("TTS Voice Synthesis Test"):
            tts_text = gr.Textbox(
                value="નમસ્તે ખેડૂત મિત્ર! સ્માર્ટ ફાર્મિંગમાં તમારું સ્વાગત છે.",
                label="Text to Synthesize",
            )
            tts_lang = gr.Radio(["gu", "hi", "en"], value="gu", label="Language")
            tts_btn = gr.Button("Synthesize Speech", variant="primary")
            tts_audio = gr.Audio(label="Synthesized Audio Output")
            tts_btn.click(fn=run_tts_gradio, inputs=[tts_text, tts_lang], outputs=tts_audio)

    return demo


demo = build_gradio_ui()

# Mount Gradio onto the FastAPI app so both UI and REST endpoints (/health, /vision, /tts, etc.) work!
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

