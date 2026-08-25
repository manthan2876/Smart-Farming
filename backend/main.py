import sys
from pathlib import Path

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Support both `uvicorn main:app` from backend/ and package imports from the repo root.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.api.routes import router
from backend.api.auth_routes import router as auth_router
from backend.utils.logging import configure_logging

configure_logging()
app = FastAPI(
    title="Smart Farming API",
    version="0.1.0",
    description="HTTP delivery layer for the Smart Farming diagnostic pipeline.",
)
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(auth_router)


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Smart Farming API", "docs": "/docs"}