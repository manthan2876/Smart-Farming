import sys
from pathlib import Path

from fastapi import FastAPI

# Support both `uvicorn main:app` from backend/ and package imports from the repo root.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.api.routes import router

app = FastAPI(
    title="Smart Farming API",
    version="0.1.0",
    description="HTTP delivery layer for the Smart Farming diagnostic pipeline.",
)
app.include_router(router)


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Smart Farming API", "docs": "/docs"}