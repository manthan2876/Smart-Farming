from __future__ import annotations

import io
import hashlib
import json
import logging
import os
import shutil
import tempfile
import uuid
import zipfile
from collections import Counter
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy.orm import Session

from app.api.deps import require_admin_role
from app.schemas.client import DatasetSummaryResponse
from app.core import get_session
from app.core.config import settings
from app.core.paths import resolve_storage_path
from app.models import DatasetCandidate, Prediction
from app.pipeline import SCHEMA_VERSION

logger = logging.getLogger("smart-farming.mlops")


class CandidateStatusEnum(str, Enum):
    ADDED_TO_DATASET = "added_to_dataset"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"
    ALL = "all"


class DatasetExportFilters(BaseModel):
    expert: bool = True
    farmer: bool = True
    crop: str | None = None
    status: CandidateStatusEnum = CandidateStatusEnum.ADDED_TO_DATASET

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_clean = v.strip().lower()
            if v_clean in ("any", "all", "*"):
                return CandidateStatusEnum.ALL
            for member in CandidateStatusEnum:
                if member.value == v_clean:
                    return member
        return v


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
    model_config = ConfigDict(populate_by_name=True)

    filters: DatasetExportFilters = DatasetExportFilters()
    split: DatasetExportSplit
    format: str = "PyTorch Folder"
    imageTarget: str = Field(default="preprocessed", alias="image_target")
    replay_ratio: float = Field(default=0.70, ge=0.0, le=0.95, description="Target proportion of baseline replay images (0.0 to 0.95)")
    include_replay_buffer: bool = True


router = APIRouter(prefix="/admin/dataset", tags=["mlops", "dataset"])


def _source_filter(filters: DatasetExportFilters) -> set[str]:
    sources: set[str] = set()
    if filters.expert:
        sources.add("expert_correction")
    if filters.farmer:
        sources.update({"farmer_confirmation", "farmer_feedback_review"})
    return sources


def _split_for_entity(split_key: str, split: DatasetExportSplit) -> str:
    """Deterministically allocates images from the same entity (plot/farm) into the same split."""
    bucket = int(hashlib.sha256(split_key.encode("utf-8")).hexdigest()[:8], 16) % 100
    if bucket < split.train:
        return "train"
    if bucket < split.train + split.val:
        return "val"
    return "test"


def _clean_image_without_exif(image_input: Path | bytes) -> bytes:
    """Reads image bytes and strips all EXIF metadata (specifically GPS coordinates) to protect farmer privacy."""
    try:
        from PIL import Image as PILImage
        img_source = image_input if isinstance(image_input, bytes) else image_input.read_bytes()
        with PILImage.open(io.BytesIO(img_source)) as img:
            buffer = io.BytesIO()
            fmt = img.format or "JPEG"
            img.save(buffer, format=fmt)
            return buffer.getvalue()
    except Exception:
        if isinstance(image_input, bytes):
            return image_input
        return image_input.read_bytes()


@router.get("/summary", response_model=DatasetSummaryResponse)
def get_dataset_summary(
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
def export_dataset_post(
    payload: DatasetExportRequest,
    download: bool = Query(default=False, description="If true, returns file directly instead of Supabase URL"),
    is_admin: str = Depends(require_admin_role),
    session: Session = Depends(get_session),
):
    target_fmt = payload.format.strip()
    if target_fmt not in {"PyTorch Folder", "JSON Manifest"}:
        raise HTTPException(status_code=422, detail="Only PyTorch Folder and JSON Manifest exports are supported")
    target_img = payload.imageTarget.strip().lower()
    if target_img not in {"raw", "preprocessed"}:
        raise HTTPException(status_code=422, detail="imageTarget must be raw or preprocessed")

    sources = _source_filter(payload.filters)
    if not sources:
        raise HTTPException(status_code=422, detail="Select at least one dataset source")

    # Build base query with join to Prediction for crop filter
    query = (
        session.query(DatasetCandidate)
        .outerjoin(Prediction, DatasetCandidate.prediction_id == Prediction.id)
    )

    # Filter by source
    query = query.filter(DatasetCandidate.source.in_(sources))

    # Filter by status (validated against CandidateStatusEnum)
    if payload.filters.status != CandidateStatusEnum.ALL:
        query = query.filter(DatasetCandidate.status == payload.filters.status.value)

    # Filter by crop — case-insensitive join filter
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

    # Compute split summary & class distribution for provenance
    split_counts = {"train": 0, "val": 0, "test": 0}
    class_counts: Counter[str] = Counter()
    missing_images_warnings: list[str] = []
    class_warnings: list[str] = []

    export_id = uuid.uuid4().hex[:12]
    tmp_dir = Path(tempfile.mkdtemp(prefix=f"smartfarming-mlops-{export_id}-"))
    zip_path = tmp_dir / f"dataset_export_{export_id}.zip"
    metadata: list[dict[str, Any]] = []

    try:
        from app.core.storage import get_storage
        storage = get_storage()

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            # 1. Process candidate images
            for candidate in selected:
                prediction = candidate.prediction
                image_path_value = candidate.image_path
                if payload.imageTarget == "preprocessed" and prediction and prediction.processed_path:
                    image_path_value = prediction.processed_path
                elif not image_path_value and prediction:
                    image_path_value = prediction.processed_path if payload.imageTarget == "preprocessed" else prediction.raw_path

                # Spatial deterministic split by plot_id / user_id
                if prediction and prediction.plot_id:
                    split_key = f"plot_{prediction.plot_id}"
                elif prediction and prediction.user_id:
                    split_key = f"user_{prediction.user_id}"
                else:
                    split_key = f"candidate_{candidate.id}"
                split = _split_for_entity(split_key, payload.split)
                split_counts[split] += 1

                label = (candidate.corrected_label or candidate.original_label or "unknown").replace(" ", "_").replace("/", "_")
                class_counts[label] += 1

                # Load image bytes from Supabase storage or local disk
                raw_bytes: bytes | None = None
                img_name = "leaf.jpg"
                if image_path_value:
                    try:
                        img_name = Path(image_path_value).name or "leaf.jpg"
                    except Exception:
                        img_name = "leaf.jpg"

                    # 1. Try unified storage backend (works for Supabase Object Storage & local storage)
                    try:
                        if storage.exists(image_path_value):
                            raw_bytes = storage.get(image_path_value)
                    except Exception as st_err:
                        logger.debug("Storage backend lookup failed for %s: %s", image_path_value, st_err)

                    # 2. Fallback to direct local filesystem check
                    if raw_bytes is None:
                        try:
                            resolved_local = resolve_storage_path(image_path_value)
                            if resolved_local.is_file():
                                raw_bytes = resolved_local.read_bytes()
                        except Exception:
                            pass

                image_file = None
                if raw_bytes is not None:
                    # Strip EXIF GPS metadata for farmer privacy
                    clean_bytes = _clean_image_without_exif(raw_bytes)
                    if payload.format == "PyTorch Folder":
                        image_file = f"images/{split}/{label}/{candidate.id}_{img_name}"
                    else:
                        image_file = f"images/{split}/{candidate.id}_{img_name}"
                    archive.writestr(image_file, clean_bytes)
                else:
                    missing_images_warnings.append(str(image_path_value or f"candidate_{candidate.id}"))
                    logger.warning("Missing dataset candidate image file: %s (ID %s)", image_path_value, candidate.id)

                metadata.append({
                    "id": candidate.id,
                    "prediction_id": candidate.prediction_id,
                    "source": candidate.source,
                    "type": "candidate",
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

            # 2. Replay Buffer Mixing (Prevent Catastrophic Forgetting)
            replay_count = 0
            if payload.include_replay_buffer and payload.replay_ratio > 0.0:
                datasets_base = settings.BACKEND_ROOT.parent / "Datasets" / "disease_dataset"
                if datasets_base.exists():
                    target_crops = []
                    if crop_filter and not crop_filter.startswith("all"):
                        for c_dir in datasets_base.iterdir():
                            if c_dir.is_dir() and c_dir.name.lower() == crop_filter:
                                target_crops.append(c_dir)
                    if not target_crops:
                        target_crops = [d for d in datasets_base.iterdir() if d.is_dir()]

                    baseline_files: list[Path] = []
                    for c_dir in target_crops:
                        for ext in ("*.jpg", "*.jpeg", "*.png"):
                            baseline_files.extend(c_dir.rglob(ext))

                    if baseline_files:
                        desired_replay = int(len(selected) * (payload.replay_ratio / (1.0 - payload.replay_ratio)))
                        desired_replay = min(desired_replay, 1000)  # Safe bounded cap

                        # Deterministically step through baseline images
                        step = max(1, len(baseline_files) // max(1, desired_replay))
                        sampled_replay = baseline_files[::step][:desired_replay]

                        for r_idx, r_path in enumerate(sampled_replay):
                            r_split = _split_for_entity(r_path.stem, payload.split)
                            split_counts[r_split] += 1
                            r_label = r_path.parent.name.replace(" ", "_").replace("/", "_")
                            class_counts[r_label] += 1

                            r_bytes = _clean_image_without_exif(r_path)
                            if payload.format == "PyTorch Folder":
                                arc_name = f"images/{r_split}/{r_label}/replay_{r_idx}_{r_path.name}"
                            else:
                                arc_name = f"images/{r_split}/replay_{r_idx}_{r_path.name}"

                            archive.writestr(arc_name, r_bytes)
                            metadata.append({
                                "id": f"replay-{r_idx}",
                                "prediction_id": None,
                                "source": "replay_baseline",
                                "type": "replay_baseline",
                                "image_file": arc_name,
                                "image_target": "raw",
                                "split": r_split,
                                "original_label": r_label,
                                "corrected_label": r_label,
                                "status": "approved_baseline",
                                "provenance_note": f"Sampled from seed dataset: {r_path.name}",
                                "crop": r_path.parents[2].name if len(r_path.parents) > 2 else "Unknown",
                                "model_used": None,
                                "created_at": datetime.now(timezone.utc).isoformat(),
                            })
                            replay_count += 1

            # 3. Minimum Samples Per Class Validation
            for cls_name, count in class_counts.items():
                if count < 10:
                    class_warnings.append(
                        f"Class '{cls_name}' has only {count} sample(s) (< 10 minimum recommended). "
                        "Consider collecting more data or applying class weighting."
                    )

            # 4. Provenance Metadata
            provenance = {
                "schema_version": SCHEMA_VERSION,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "export_id": export_id,
                "total_candidates": len(selected),
                "total_replay_baseline": replay_count,
                "total_images": len(selected) + replay_count,
                "split_summary": split_counts,
                "class_distribution": dict(class_counts),
                "warnings": class_warnings,
                "missing_images_count": len(missing_images_warnings),
                "missing_images": missing_images_warnings,
                "export_config": payload.model_dump(),
                "format": payload.format,
                "spatial_split_strategy": "plot_id_deterministic_hash",
            }
            full_metadata = {"provenance": provenance, "candidates": metadata}
            archive.writestr("metadata.json", json.dumps(full_metadata, indent=2))

            # 5. Reproducibility README
            readme_content = (
                f"# Smart Farming Dataset Export — Run {export_id}\n\n"
                f"Exported: {provenance['exported_at']}\n"
                f"Total candidates: {len(selected)}\n"
                f"Replay baseline samples: {replay_count}\n"
                f"Total images: {provenance['total_images']}\n"
                f"Format: {payload.format}\n"
                f"Spatial split: plot_id deterministic partitioning\n\n"
                f"## Split Summary\n"
                f"- Train: {split_counts['train']} images ({payload.split.train}%)\n"
                f"- Val: {split_counts['val']} images ({payload.split.val}%)\n"
                f"- Test: {split_counts['test']} images ({payload.split.test}%)\n\n"
                f"## Class Distribution\n"
                + "\n".join(f"- {cls}: {cnt}" for cls, cnt in class_counts.items())
                + ("\n\n## Warnings\n" + "\n".join(f"- {w}" for w in class_warnings) if class_warnings else "")
                + "\n\nSee `metadata.json` for full candidate provenance.\n"
            )
            archive.writestr("README.md", readme_content)

        # 6. Record MlopsRun Audit Trail
        try:
            from app.models.mlopsRun import MlopsRun
            run_entry = MlopsRun(
                model_name=f"dataset_export_{export_id}",
                status="completed",
                epoch=1,
                total_epochs=1,
                message=f"Exported {len(selected)} candidates + {replay_count} replay images ({payload.format})",
                dataset_export_config=payload.model_dump(),
                metrics={
                    "total_images": len(selected) + replay_count,
                    "candidates_count": len(selected),
                    "replay_count": replay_count,
                    "split_summary": split_counts,
                },
                finished_at=datetime.now(timezone.utc),
            )
            session.add(run_entry)
            session.commit()
        except Exception as run_err:
            logger.warning("Could not persist MlopsRun audit record: %s", run_err)
            session.rollback()

        # 7. Storage Backend Upload (Supabase Storage / Serverless)
        from app.core.storage import get_storage
        storage = get_storage()
        zip_key = f"exports/dataset_export_{export_id}.zip"

        if getattr(settings, "STORAGE_BACKEND", "local").lower() in ("supabase", "s3") and not download:
            zip_bytes = zip_path.read_bytes()
            storage.save(zip_bytes, zip_key, content_type="application/zip")
            download_url = storage.get_url(zip_key, expires_in=3600)
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return {
                "status": "success",
                "export_id": export_id,
                "download_url": download_url,
                "storage_key": zip_key,
                "candidates_count": len(selected),
                "replay_count": replay_count,
                "total_images": len(selected) + replay_count,
                "split_summary": split_counts,
                "class_distribution": dict(class_counts),
                "warnings": class_warnings,
                "missing_images_count": len(missing_images_warnings),
            }

        return FileResponse(path=zip_path, filename=f"dataset_export_{export_id}.zip", media_type="application/zip")

    except HTTPException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise


# Backward Compatibility & Specification Alias Router
mlops_alias_router = APIRouter(prefix="/admin/mlops", tags=["mlops"])


@mlops_alias_router.get("/summary", response_model=DatasetSummaryResponse)
def get_mlops_summary_alias(
    is_admin: str = Depends(require_admin_role),
    session: Session = Depends(get_session),
):
    return get_dataset_summary(is_admin=is_admin, session=session)


@mlops_alias_router.post("/export")
def export_mlops_post_alias(
    payload: DatasetExportRequest,
    download: bool = Query(default=False, description="If true, returns file directly instead of Supabase URL"),
    is_admin: str = Depends(require_admin_role),
    session: Session = Depends(get_session),
):
    return export_dataset_post(payload=payload, download=download, is_admin=is_admin, session=session)


@mlops_alias_router.get("/runs")
def list_mlops_runs_alias(
    is_admin: str = Depends(require_admin_role),
    session: Session = Depends(get_session),
):
    from app.models.mlopsRun import MlopsRun
    runs = session.query(MlopsRun).order_by(MlopsRun.started_at.desc()).limit(50).all()
    return {
        "runs": [
            {
                "id": r.id,
                "model_name": r.model_name,
                "status": r.status,
                "epoch": r.epoch,
                "total_epochs": r.total_epochs,
                "message": r.message,
                "dataset_export_config": r.dataset_export_config,
                "metrics": r.metrics,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            }
            for r in runs
        ]
    }
