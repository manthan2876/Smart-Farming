from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.api.deps import require_admin_role
from app.core import get_session
from app.core.paths import resolve_storage_path
from app.models import DatasetCandidate, Prediction
from app.pipeline import SCHEMA_VERSION


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
    total = session.query(DatasetCandidate).count()
    expert_count = (
        session.query(DatasetCandidate)
        .filter(DatasetCandidate.source == "expert_correction")
        .count()
    )
    farmer_count = (
        session.query(DatasetCandidate)
        .filter(DatasetCandidate.source.in_(["farmer_confirmation", "farmer_feedback_review"]))
        .count()
    )
    pending = (
        session.query(DatasetCandidate)
        .filter(DatasetCandidate.status == "pending_review")
        .count()
    )
    added = (
        session.query(DatasetCandidate)
        .filter(DatasetCandidate.status == "added_to_dataset")
        .count()
    )

    # Crop distribution of candidates
    from sqlalchemy import func
    crop_rows = (
        session.query(Prediction.crop, func.count(DatasetCandidate.id))
        .join(Prediction, DatasetCandidate.prediction_id == Prediction.id)
        .group_by(Prediction.crop)
        .all()
    )
    crop_distribution = [{"crop": r[0] or "Unknown", "count": r[1]} for r in crop_rows]

    return {
        "total": total,
        "expert_overridden": expert_count,
        "farmer_confirmed": farmer_count,
        "by_status": {"pending_review": pending, "added_to_dataset": added},
        "by_crop": crop_distribution,
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

    # Build base query with join to Prediction for crop filter
    query = (
        session.query(DatasetCandidate)
        .join(Prediction, DatasetCandidate.prediction_id == Prediction.id)
    )

    # Filter by source
    query = query.filter(DatasetCandidate.source.in_(sources))

    # Filter by status
    valid_statuses = {"pending_review", "added_to_dataset", "rejected", "all"}
    if payload.filters.status and payload.filters.status.lower() not in valid_statuses:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status filter '{payload.filters.status}'. Allowed: {sorted(list(valid_statuses))}",
        )
    if payload.filters.status and payload.filters.status.lower() != "all":
        query = query.filter(DatasetCandidate.status == payload.filters.status)

    # Filter by crop — proper case-insensitive join filter
    crop_filter = (payload.filters.crop or "").strip().lower()
    if crop_filter and not crop_filter.startswith("all"):
        from sqlalchemy import func as sqlfunc
        query = query.filter(sqlfunc.lower(Prediction.crop) == crop_filter)

    selected = query.all()

    if not selected:
        raise HTTPException(status_code=404, detail="No dataset candidates match the selected filters")

    if len(selected) > 5000:
        raise HTTPException(
            status_code=400,
            detail=f"Export candidate count ({len(selected)}) exceeds safe maximum limit of 5,000.",
        )

    # Compute split summary for provenance
    split_counts = {"train": 0, "val": 0, "test": 0}
    missing_images_warnings = []

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
                split_counts[split] += 1

                image_file = None
                if image_path.is_file():
                    # PyTorch ImageFolder expects images/<split>/<class_label>/filename.ext
                    label_dir = (candidate.corrected_label or candidate.original_label or "unknown").replace(" ", "_").replace("/", "_")
                    if payload.format == "PyTorch Folder":
                        image_file = f"images/{split}/{label_dir}/{candidate.id}_{image_path.name}"
                    else:
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
                    "provenance_note": candidate.provenance_note,
                    "crop": prediction.crop if prediction else None,
                    "model_used": prediction.model_used if prediction else None,
                    "created_at": candidate.created_at.isoformat(),
                })

            # metadata.json with full provenance block
            provenance = {
                "schema_version": SCHEMA_VERSION,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "total_candidates": len(selected),
                "split_summary": split_counts,
                "export_config": payload.model_dump(),
                "format": payload.format,
            }
            full_metadata = {"provenance": provenance, "candidates": metadata}
            metadata_path = tmp_dir / "metadata.json"
            metadata_path.write_text(json.dumps(full_metadata, indent=2), encoding="utf-8")
            archive.write(metadata_path, arcname="metadata.json")

            # README for reproducibility
            readme_content = (
                f"# Smart Farming Dataset Export\n\n"
                f"Exported: {provenance['exported_at']}\n"
                f"Total candidates: {len(selected)}\n"
                f"Format: {payload.format}\n"
                f"Image target: {payload.imageTarget}\n\n"
                f"## Split\n"
                f"- Train: {split_counts['train']} images ({payload.split.train}%)\n"
                f"- Val: {split_counts['val']} images ({payload.split.val}%)\n"
                f"- Test: {split_counts['test']} images ({payload.split.test}%)\n\n"
                f"## Structure\n"
                f"For PyTorch Folder format: `images/<split>/<class_label>/<filename>`\n"
                f"Load with `torchvision.datasets.ImageFolder`.\n\n"
                f"See `metadata.json` for full provenance and candidate details.\n"
            )
            readme_path = tmp_dir / "README.md"
            readme_path.write_text(readme_content, encoding="utf-8")
            archive.write(readme_path, arcname="README.md")

    except HTTPException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    return FileResponse(path=zip_path, filename="dataset_export.zip", media_type="application/zip")
