"""
main.py — FastAPI entrypoint for Model Inference Server (Server 2, Port 8001)
"""

from __future__ import annotations

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from src.pipeline import run_vision_pipeline

app = FastAPI(
    title="Smart Farming Model Inference Server",
    version="1.0.0",
    description="Dedicated microservice for crop identification, disease classification, severity estimation, and pest detection."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "model_inference",
        "port": 8001,
    }


@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
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
