from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.api.deps import require_admin_role
from app.core import get_session
from app.core.paths import resolve_storage_path
from app.models import DatasetCandidate


class DatasetExportFilters(BaseModel):
    expert: bool = True
    farmer: bool = True
    crop: str | None = None
    status: str | None = None


class DatasetExportSplit(BaseModel):
    train: int = Field(ge=0, le=100)
    val: int = Field(ge=0, le=100)
    test: int = Field(ge=0, le=100)

    @model_validator(mode="after")
    def validate_total(self) -> "DatasetExportSplit":
        if self.train + self.val + self.test != 100:
            raise ValueError("Dataset split percentages must total 100")
        return self


class DatasetExportRequest(BaseModel):
    filters: DatasetExportFilters = DatasetExportFilters()
    split: DatasetExportSplit
    format: str = "PyTorch Folder"
    imageTarget: str = "preprocessed"


router = APIRouter(prefix="/admin/dataset", tags=["mlops", "dataset"])


def _source_filter(filters: DatasetExportFilters) -> set[str]:
    sources: set[str] = set()
    if filters.expert:
        sources.add("expert_correction")
    if filters.farmer:
        sources.update({"farmer_confirmation", "farmer_feedback_review"})
    return sources


def _split_for(candidate_id: int, split: DatasetExportSplit) -> str:
    bucket = int(hashlib.sha256(str(candidate_id).encode()).hexdigest()[:8], 16) % 100
    if bucket < split.train:
        return "train"
    if bucket < split.train + split.val:
        return "val"
    return "test"


@router.get("/summary")
async def get_dataset_summary(
    is_admin: str = Depends(require_admin_role),
    session: Session = Depends(get_session),
):
    return {
        "total": session.query(DatasetCandidate).count(),
        "expert_overridden": session.query(DatasetCandidate).filter(DatasetCandidate.source == "expert_correction").count(),
        "farmer_confirmed": session.query(DatasetCandidate).filter(
            DatasetCandidate.source.in_(["farmer_confirmation", "farmer_feedback_review"])
        ).count(),
    }


@router.post("/export")
async def export_dataset_post(
    payload: DatasetExportRequest,
    is_admin: str = Depends(require_admin_role),
    session: Session = Depends(get_session),
):
    if payload.format not in {"PyTorch Folder", "JSON Manifest"}:
        raise HTTPException(status_code=422, detail="Only PyTorch Folder and JSON Manifest exports are supported")
    if payload.imageTarget not in {"raw", "preprocessed"}:
        raise HTTPException(status_code=422, detail="imageTarget must be raw or preprocessed")

    sources = _source_filter(payload.filters)
    if not sources:
        raise HTTPException(status_code=422, detail="Select at least one dataset source")

    candidates = session.query(DatasetCandidate).all()
    selected = []
    for candidate in candidates:
        if candidate.source not in sources:
            continue
        if payload.filters.status and candidate.status != payload.filters.status:
            continue
        crop_filter = (payload.filters.crop or "").lower()
        if crop_filter and not crop_filter.startswith("all crops"):
            if not candidate.prediction or (candidate.prediction.crop or "").lower() != crop_filter:
                continue
        selected.append(candidate)

    if not selected:
        raise HTTPException(status_code=404, detail="No dataset candidates match the selected filters")

    tmp_dir = Path(tempfile.mkdtemp(prefix="smartfarming-mlops-"))
    zip_path = tmp_dir / "dataset_export.zip"
    metadata = []

    try:
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for candidate in selected:
                prediction = candidate.prediction
                image_path_value = candidate.image_path
                if payload.imageTarget == "preprocessed" and prediction and prediction.processed_path:
                    image_path_value = prediction.processed_path
                try:
                    image_path = resolve_storage_path(image_path_value)
                except ValueError as exc:
                    raise HTTPException(status_code=422, detail="Candidate image path is outside configured storage") from exc

                split = _split_for(candidate.id, payload.split)
                image_file = None
                if image_path.is_file():
                    image_file = f"images/{split}/{candidate.id}_{image_path.name}"
                    archive.write(image_path, arcname=image_file)

                metadata.append({
                    "id": candidate.id,
                    "prediction_id": candidate.prediction_id,
                    "source": candidate.source,
                    "image_file": image_file,
                    "image_target": payload.imageTarget,
                    "split": split,
                    "original_label": candidate.original_label,
                    "corrected_label": candidate.corrected_label,
                    "status": candidate.status,
                    "model_used": prediction.model_used if prediction else None,
                    "created_at": candidate.created_at.isoformat(),
                })

            metadata_path = tmp_dir / "metadata.json"
            metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            archive.write(metadata_path, arcname="metadata.json")

            config_path = tmp_dir / "export_config.json"
            config_path.write_text(json.dumps(payload.model_dump(), indent=2), encoding="utf-8")
            archive.write(config_path, arcname="export_config.json")
    except HTTPException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    return FileResponse(path=zip_path, filename="dataset_export.zip", media_type="application/zip")
