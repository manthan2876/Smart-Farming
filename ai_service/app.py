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

import gradio as gr
from main import app as fastapi_app, root_health


def build_gradio_ui():
    with gr.Blocks(title="Smart Farming AI Hub", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🌾 Smart Farming AI Microservice")
        gr.Markdown(
            "Unified AI backend for **Crop Vision**, **IndicTrans2 Translation**, **Agronomic Advisory**, and **Neural Speech**.\n\n"
            "This Space serves as the backend microservice behind the Cloudflare Edge Gateway."
        )

        with gr.Tab("System & Health Diagnostics"):
            gr.Markdown("Click below to test the FastAPI backend status:")
            check_btn = gr.Button("Inspect System Health", variant="primary")
            health_output = gr.JSON(label="Health Diagnostic Response")
            check_btn.click(fn=root_health, outputs=health_output)

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

            def _test_adv(c, d, conf, l):
                from routers.advisory import advise, AdvisoryRequest
                req = AdvisoryRequest(crop=c, disease=d, confidence=conf, language=l)
                return advise(req)

            adv_btn.click(fn=_test_adv, inputs=[crop_in, disease_in, conf_in, lang_in], outputs=adv_output)

        with gr.Tab("TTS Voice Synthesis Test"):
            tts_text = gr.Textbox(
                value="નમસ્તે ખેડૂત મિત્ર! સ્માર્ટ ફાર્મિંગમાં તમારું સ્વાગત છે.",
                label="Text to Synthesize",
            )
            tts_lang = gr.Radio(["gu", "hi", "en"], value="gu", label="Language")
            tts_btn = gr.Button("Synthesize Speech", variant="primary")
            tts_audio = gr.Audio(label="Synthesized Audio Output")

            async def _test_tts(txt, l):
                import base64
                from routers.tts import synthesize_speech, TTSRequest
                req = TTSRequest(text=txt, language=l, speaker="female")
                res = await synthesize_speech(req)
                b64 = res.get("audioContent", "")
                raw_bytes = base64.b64decode(b64)
                out_path = Path("/tmp/sample_tts.mp3")
                out_path.write_bytes(raw_bytes)
                return str(out_path)

            tts_btn.click(fn=_test_tts, inputs=[tts_text, tts_lang], outputs=tts_audio)

    return demo


demo = build_gradio_ui()

# Mount Gradio onto the FastAPI app so both UI and REST endpoints (/health, /vision, /tts, etc.) work!
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    demo.launch(server_port=7860)

