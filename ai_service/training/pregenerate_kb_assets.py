#!/usr/bin/env python3
"""
pregenerate_kb_assets.py — Pre-generate Audio & Translations for the 56 ICAR Conditions
========================================================================================

Reads the 56 ICAR/KVK conditions from advisory_kb.json, extracts their summary advisories,
and pre-generates neural speech audio clips (en, hi, gu) using Edge-TTS Indian voices.
Saves pre-cached audio to data/audio/{hash}.mp3 and syncs to Supabase Storage.

Usage:
    python ai_service/training/pregenerate_kb_assets.py [--dry-run] [--upload-storage]
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pregenerate_kb")

ROOT = Path(__file__).resolve().parents[2]
KB_PATH = Path(__file__).resolve().parents[1] / "advisory_kb.json"
AUDIO_DIR = ROOT / "backend" / "data" / "audio"

VOICES = {
    "en": "en-IN-NeerjaNeural",
    "hi": "hi-IN-SwaraNeural",
    "gu": "gu-IN-DhwaniNeural",
}


def load_conditions() -> list[dict]:
    if not KB_PATH.exists():
        logger.error("Knowledge base not found at %s", KB_PATH)
        return []
    with open(KB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("conditions", [])


async def synthesize_audio(text: str, voice: str, output_path: Path) -> bool:
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))
        return True
    except Exception as exc:
        logger.warning("Edge-TTS synthesis error for voice %s: %s", voice, exc)
        return False


def get_text_hash(lang: str, text: str) -> str:
    cleaned = text.strip()
    return hashlib.sha256(f"{lang}:{cleaned}".encode("utf-8")).hexdigest()


async def pregenerate_all(dry_run: bool = False, upload_storage: bool = False):
    conditions = load_conditions()
    logger.info("Loaded %d conditions from %s", len(conditions), KB_PATH.name)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    storage = None
    if upload_storage:
        sys.path.insert(0, str(ROOT / "backend" / "src"))
        try:
            from app.core.storage import get_storage
            storage = get_storage()
            logger.info("Connected to Supabase/Object storage backend.")
        except Exception as exc:
            logger.warning("Storage initialization failed: %s", exc)

    total_tasks = 0
    synthesized = 0

    for cond in conditions:
        cond_id = cond.get("id", "unknown")
        crop = cond.get("crop", "")
        disease = cond.get("condition", "")

        # Extract multilingual summaries
        summaries = {
            "en": cond.get("immediate_action") or f"Inspection and diagnosis for {crop} {disease}.",
            "hi": cond.get("translations", {}).get("hi", {}).get("immediate_action") or f"{crop} {disease} के लिए कृषि सलाह।",
            "gu": cond.get("translations", {}).get("gu", {}).get("immediate_action") or f"{crop} {disease} માટે કૃષિ સલાહ.",
        }

        for lang, text in summaries.items():
            if not text:
                continue
            total_tasks += 1
            thash = get_text_hash(lang, text)
            out_file = AUDIO_DIR / f"{thash}.mp3"
            cond_named_file = AUDIO_DIR / f"{cond_id}_{lang}.mp3"

            if out_file.exists() and not dry_run:
                # Also link named file for direct reference
                if not cond_named_file.exists():
                    try:
                        cond_named_file.write_bytes(out_file.read_bytes())
                    except Exception:
                        pass
                continue

            if dry_run:
                logger.info("[Dry Run] Would synthesize %s (%s): %s", cond_id, lang, text[:40])
                continue

            voice = VOICES.get(lang, "en-IN-NeerjaNeural")
            success = await synthesize_audio(text, voice, out_file)
            if success:
                synthesized += 1
                try:
                    cond_named_file.write_bytes(out_file.read_bytes())
                except Exception:
                    pass

                if storage:
                    try:
                        data = out_file.read_bytes()
                        storage.save(data, f"audio/{thash}.mp3", content_type="audio/mpeg")
                        storage.save(data, f"audio/{cond_id}_{lang}.mp3", content_type="audio/mpeg")
                    except Exception as exc:
                        logger.warning("Upload failed for %s: %s", thash, exc)

    logger.info("Pre-generation complete. Total items: %d | Newly synthesized: %d", total_tasks, synthesized)


def main():
    parser = argparse.ArgumentParser(description="Pre-generate KB audio assets")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without synthesis")
    parser.add_argument("--upload-storage", action="store_true", help="Upload to active storage backend")
    args = parser.parse_args()

    asyncio.run(pregenerate_all(dry_run=args.dry_run, upload_storage=args.upload_storage))


if __name__ == "__main__":
    main()

