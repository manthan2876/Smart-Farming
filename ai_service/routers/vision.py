"""
ai_service/routers/vision.py — Vision API router (Crop, Disease & Pest Inference).
"""

from __future__ import annotations

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from vision_engine.pipeline import run_vision_pipeline

router = APIRouter()


@router.get("/health")
def vision_health():
    return {
        "status": "healthy",
        "service": "vision_inference",
        "version": "2.0.0",
    }


@router.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        nparr = np.frombuffer(content, np.uint8)
        image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image_bgr is None or image_bgr.size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file could not be decoded as an image."
            )

        result = run_vision_pipeline(image_bgr, filename=file.filename or "upload.jpg")

        prep_status = result.get("status", {}).get("preprocessing")
        if prep_status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error_message", "Image validation failed.")
            )

        return result
    except HTTPException:
        raise
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("Vision pipeline internal error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vision pipeline encountered an internal error processing the image."
        )

