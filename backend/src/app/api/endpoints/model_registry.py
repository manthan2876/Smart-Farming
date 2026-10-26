"""
model_registry.py — Model Registry & Promotion Gates
=====================================================

Endpoints:
  GET  /admin/models          — List all registered model versions with metrics
  GET  /admin/models/health   — Check which configured models are loadable
  POST /admin/models/promote  — Promote a model version to active (updates config.yaml & registry)
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import require_admin_role
from app.schemas.admin import ModelRollbackResponse
from app.schemas.client import AdminModelHealthResponse
from app.core import get_session
from app.core.config import settings
from app.models.model_registry import ModelRegistryRecord

logger = logging.getLogger("smart-farming.api")

router = APIRouter(prefix="/admin/models", tags=["admin", "model-registry"])

# Path to the model registry manifest
_REGISTRY_PATH = settings.CONFIG_PATH.parent / "model_registry.json"
# Path to runtime config
_CONFIG_PATH = settings.CONFIG_PATH


def _load_registry() -> dict[str, Any]:
    if not _REGISTRY_PATH.exists():
        return {"schema_version": "1.0", "models": {}}
    return json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))


def _save_registry(registry: dict[str, Any]) -> None:
    registry["last_updated"] = datetime.now(timezone.utc).isoformat()
    _REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding="utf-8")


def _seed_db_from_file_if_empty(session: Session) -> None:
    """Bootstrap durable database registry from legacy model_registry.json on first run."""
    try:
        count = session.query(ModelRegistryRecord).count()
        if count > 0:
            return

        file_reg = _load_registry()
        models = file_reg.get("models", {})
        for m_key, m_info in models.items():
            active_ver = m_info.get("active_version")
            for ver_name, ver_info in m_info.get("versions", {}).items():
                rec = ModelRegistryRecord(
                    model_key=m_key,
                    version=ver_name,
                    arch=ver_info.get("arch", "efficientnet_b2"),
                    checkpoint_path=ver_info.get("checkpoint"),
                    labels_json=ver_info.get("labels", []) if isinstance(ver_info.get("labels"), list) else [],
                    num_classes=ver_info.get("num_classes", 0),
                    val_acc=float(ver_info.get("val_acc") or 0.0),
                    test_acc=float(ver_info.get("test_acc") or 0.0),
                    macro_f1=float(ver_info.get("macro_f1") or 0.0) if ver_info.get("macro_f1") is not None else None,
                    temperature=float(ver_info.get("temperature", 1.0)),
                    status="active" if ver_name == active_ver else "retired",
                    promoted_at=datetime.now(timezone.utc),
                    promoted_by="system_bootstrap",
                    notes=ver_info.get("notes"),
                )
                session.add(rec)
        session.commit()
    except Exception as exc:
        logger.warning("Could not bootstrap DB model registry from file: %s", exc)
        session.rollback()


def _load_config() -> dict[str, Any]:
    with _CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _save_config(config: dict[str, Any]) -> None:
    with _CONFIG_PATH.open("w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def _resolve_model_path(relative_path: str | None) -> Path | None:
    if not relative_path:
        return None
    backend_root = _CONFIG_PATH.parent
    project_root = backend_root.parent
    # Models are stored at workspace/project root (models/), check project_root first
    for candidate_base in (project_root, backend_root):
        candidate = candidate_base / relative_path
        if candidate.exists():
            return candidate
    return project_root / relative_path


@router.get("")
def list_models(
    is_admin: str = Depends(require_admin_role),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """List all registered model versions from the durable database registry."""
    _seed_db_from_file_if_empty(session)
    records = session.query(ModelRegistryRecord).order_by(ModelRegistryRecord.promoted_at.desc()).all()
    models_dict: dict[str, Any] = {}
    for r in records:
        entry = models_dict.setdefault(r.model_key, {"active_version": None, "versions": {}})
        if r.status == "active":
            entry["active_version"] = r.version
        entry["versions"][r.version] = {
            "arch": r.arch,
            "checkpoint": r.checkpoint_path,
            "hf_repo_id": r.hf_repo_id,
            "hf_weight_path": r.hf_weight_path,
            "labels": r.labels_json,
            "num_classes": r.num_classes,
            "val_acc": r.val_acc,
            "test_acc": r.test_acc,
            "macro_f1": r.macro_f1,
            "per_class_metrics": r.per_class_metrics,
            "temperature": r.temperature,
            "status": r.status,
            "dataset_hash": r.dataset_hash,
            "git_commit": r.git_commit,
            "random_seed": r.random_seed,
            "promoted_at": r.promoted_at.isoformat() if r.promoted_at else None,
            "promoted_by": r.promoted_by,
            "notes": r.notes,
        }
    return {
        "schema_version": "2.0",
        "storage": "postgresql_database",
        "models": models_dict,
    }


@router.get("/health", response_model=AdminModelHealthResponse)
def model_health(is_admin: str = Depends(require_admin_role)) -> dict[str, Any]:
    """Check which configured models are loadable (file exists on disk)."""
    config = _load_config()
    registry = _load_registry()
    results: dict[str, Any] = {}

    def _check(key: str, path_str: str | None, labels_str: str | None = None) -> dict:
        model_path = _resolve_model_path(path_str)
        labels_path = _resolve_model_path(labels_str)
        model_ok = model_path.exists() if model_path else False
        labels_ok = labels_path.exists() if labels_path else True  # labels optional

        # When running with a remote microservice (inference-service),
        # models are hosted on that service rather than the backend local disk
        if not model_ok and settings.MODEL_SERVER_URL:
            model_ok = True
            labels_ok = True

        reg_entry = registry.get("models", {}).get(key, {})
        active_ver = reg_entry.get("active_version")
        ver_info = reg_entry.get("versions", {}).get(active_ver, {}) if active_ver else {}
        return {
            "status": "ok" if model_ok else "missing",
            "model_file": str(model_path) if (model_path and model_path.exists()) else f"remote ({settings.MODEL_SERVER_URL})",
            "model_exists": model_ok,
            "labels_file": str(labels_path) if (labels_path and labels_path.exists()) else None,
            "labels_exists": labels_ok,
            "active_version": active_ver,
            "val_acc": ver_info.get("val_acc"),
            "test_acc": ver_info.get("test_acc"),
            "trained_at": ver_info.get("trained_at"),
        }

    models_cfg = config.get("models", {})

    # Crop identifier
    ci = models_cfg.get("crop_identifier", {})
    results["crop_identifier"] = _check("crop_identifier", ci.get("path"), ci.get("labels"))

    # Disease classifiers
    for crop, cfg in models_cfg.get("disease_models", {}).items():
        key = f"{crop.lower()}_disease"
        results[key] = _check(key, cfg.get("path"), cfg.get("labels"))

    # Pest classifier
    pest = models_cfg.get("pest_classifier", {})
    results["pest_classifier"] = _check("pest_classifier", pest.get("path"))

    all_ok = all(v.get("status") == "ok" for v in results.values())
    return {
        "overall_status": "healthy" if all_ok else "degraded",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "models": results,
    }


class PromoteRequest(BaseModel):
    model_key: str = Field(description="Registry key, e.g. 'tomato_disease' or 'crop_identifier'")
    version: str = Field(description="Version string, e.g. 'v2.0'")
    checkpoint_path: str | None = Field(default=None, description="Path to .pth checkpoint, relative to backend root")
    hf_repo_id: str | None = Field(default=None, description="Hugging Face Model Hub repository, e.g. 'Maharsh8805/smart-farming-models'")
    hf_weight_path: str | None = Field(default=None, description="Weight filename on HF Model Hub")
    labels_path: str | None = Field(default=None, description="Path to labels.json, relative to backend root")
    arch: str = Field(default="efficientnet_b2", description="Model architecture identifier")
    num_classes: int | None = Field(default=None)
    metrics_json: dict[str, Any] | None = Field(default=None, description="Parsed metrics dictionary from training run")
    metrics_path: str | None = Field(default=None, description="Path to metrics.json file on disk")
    val_acc: float | None = Field(default=None, ge=0.0, le=1.0)
    test_acc: float | None = Field(default=None, ge=0.0, le=1.0)
    macro_f1: float | None = Field(default=None, ge=0.0, le=1.0)
    temperature: float | None = Field(default=1.0, gt=0.0)
    dataset_hash: str | None = None
    git_commit: str | None = None
    random_seed: int | None = None
    notes: str | None = Field(default=None, max_length=1000)
    min_test_acc: float | None = Field(default=0.85, ge=0.0, le=1.0, description="Minimum test accuracy required")
    min_macro_f1: float | None = Field(default=0.80, ge=0.0, le=1.0, description="Minimum macro-F1 score required")
    min_class_recall: float | None = Field(default=0.70, ge=0.0, le=1.0, description="Minimum per-class recall required")


@router.post("/promote")
def promote_model(
    payload: PromoteRequest,
    is_admin: str = Depends(require_admin_role),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """
    Promote a model version to active in the durable PostgreSQL/Supabase registry.

    Validates promotion gates automatically:
    1. Minimum test accuracy gate (min_test_acc, default 0.85)
    2. Minimum macro-F1 score gate (min_macro_f1, default 0.80)
    3. Minimum per-class recall gate (min_class_recall, default 0.70)
    """
    # ── 1. Resolve and Parse Metrics ──────────────────────────────────────────
    metrics: dict[str, Any] = dict(payload.metrics_json or {})
    if payload.metrics_path:
        real_base = os.path.realpath(str(_CONFIG_PATH.parent.parent))
        target_path = os.path.join(real_base, payload.metrics_path.replace("\\", "/").strip("/"))
        real_target = os.path.realpath(target_path)
        if os.path.commonpath([real_base, real_target]) != real_base:
            raise HTTPException(status_code=400, detail="Invalid metrics path: access outside project directory is forbidden.")
        if os.path.isfile(real_target):
            try:
                with open(real_target, "r", encoding="utf-8") as f:
                    loaded_m = json.load(f)
                if isinstance(loaded_m, dict):
                    metrics.update(loaded_m)
            except Exception as exc:
                logger.warning("Could not read metrics file (%s)", exc)

    test_acc = payload.test_acc if payload.test_acc is not None else metrics.get("test_acc") or metrics.get("accuracy")
    val_acc = payload.val_acc if payload.val_acc is not None else metrics.get("val_acc") or 0.0
    macro_f1 = payload.macro_f1 if payload.macro_f1 is not None else metrics.get("macro_f1") or metrics.get("macro_avg", {}).get("f1-score")
    per_class = (
        metrics.get("per_class_metrics")
        or metrics.get("classification_report")
        or metrics.get("per_class_report")
        or {}
    )
    if macro_f1 is None and isinstance(per_class, dict):
        macro_f1 = (
            per_class.get("macro avg", {}).get("f1-score")
            or per_class.get("macro_avg", {}).get("f1-score")
        )
    temperature = payload.temperature if payload.temperature is not None else metrics.get("optimal_temperature") or metrics.get("temperature", 1.0)
    dataset_hash = payload.dataset_hash or metrics.get("dataset_hash") or metrics.get("dataset_sha256")
    git_commit = payload.git_commit or metrics.get("git_commit")
    random_seed = payload.random_seed if payload.random_seed is not None else metrics.get("seed")

    # ── 2. Rigorous Promotion Gates ───────────────────────────────────────────
    if payload.min_test_acc is not None:
        if test_acc is None or test_acc < payload.min_test_acc:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Promotion rejected: test_acc={test_acc} is below "
                    f"the required minimum of {payload.min_test_acc:.4f}."
                ),
            )

    if payload.min_macro_f1 is not None and macro_f1 is not None:
        if macro_f1 < payload.min_macro_f1:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Promotion rejected: macro_f1={macro_f1:.4f} is below "
                    f"the required minimum of {payload.min_macro_f1:.4f}."
                ),
            )

    if payload.min_class_recall is not None and per_class:
        weak_classes = []
        for cls_name, cls_data in per_class.items():
            if isinstance(cls_data, dict) and "recall" in cls_data:
                rec = float(cls_data["recall"])
                if rec < payload.min_class_recall:
                    weak_classes.append(f"{cls_name} (recall={rec:.2f})")
        if weak_classes:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Promotion rejected: Class recall below minimum {payload.min_class_recall:.2f} "
                    f"for: {', '.join(weak_classes)}."
                ),
            )

    # ── 3. Verify Checkpoint (Local or HF Hub) ────────────────────────────────
    if payload.checkpoint_path:
        ckpt_path = _resolve_model_path(payload.checkpoint_path)
        if (ckpt_path is None or not ckpt_path.exists()) and not settings.MODEL_SERVER_URL and not payload.hf_repo_id:
            raise HTTPException(
                status_code=404,
                detail=f"Checkpoint not found at: {payload.checkpoint_path}",
            )

    labels = []
    if payload.labels_path:
        labels_path = _resolve_model_path(payload.labels_path)
        if labels_path and labels_path.exists():
            try:
                labels = json.loads(labels_path.read_text(encoding="utf-8"))
            except Exception:
                # Failed reading labels file; fall back to empty labels list
                pass
    num_classes = payload.num_classes or len(labels) or metrics.get("num_classes", 0)

    # ── 4. Durable DB Registry Update (Supabase / PostgreSQL) ───────────────────
    _seed_db_from_file_if_empty(session)
    # Retire any existing active versions of this model in the database
    existing_actives = (
        session.query(ModelRegistryRecord)
        .filter(ModelRegistryRecord.model_key == payload.model_key, ModelRegistryRecord.status == "active")
        .all()
    )
    for act in existing_actives:
        act.status = "retired"

    new_db_record = ModelRegistryRecord(
        model_key=payload.model_key,
        version=payload.version,
        arch=payload.arch,
        hf_repo_id=payload.hf_repo_id,
        hf_weight_path=payload.hf_weight_path,
        checkpoint_path=payload.checkpoint_path,
        labels_json=labels,
        num_classes=num_classes,
        val_acc=float(val_acc or 0.0),
        test_acc=float(test_acc or 0.0),
        macro_f1=float(macro_f1) if macro_f1 is not None else None,
        per_class_metrics=per_class if per_class else None,
        temperature=float(temperature or 1.0),
        status="active",
        dataset_hash=str(dataset_hash) if dataset_hash else None,
        git_commit=str(git_commit) if git_commit else None,
        random_seed=int(random_seed) if random_seed is not None else None,
        notes=payload.notes,
        promoted_at=datetime.now(timezone.utc),
        promoted_by=is_admin,
    )
    session.add(new_db_record)
    session.commit()
    logger.info("Persisted active model '%s' version '%s' to database registry", payload.model_key, payload.version)

    # ── 5. Backward Compatibility: Sync Local File & config.yaml ─────────────
    registry = _load_registry()
    models = registry.setdefault("models", {})
    model_entry = models.setdefault(payload.model_key, {"versions": {}})
    model_entry["active_version"] = payload.version
    model_entry["versions"][payload.version] = {
        "arch": payload.arch,
        "checkpoint": payload.checkpoint_path,
        "hf_repo_id": payload.hf_repo_id,
        "hf_weight_path": payload.hf_weight_path,
        "labels": payload.labels_path,
        "num_classes": num_classes,
        "val_acc": val_acc,
        "test_acc": test_acc,
        "macro_f1": macro_f1,
        "temperature": temperature,
        "promoted_at": datetime.now(timezone.utc).isoformat(),
        "promoted_by": is_admin,
        "notes": payload.notes,
        "status": "active",
    }
    for ver, ver_info in model_entry["versions"].items():
        if ver != payload.version:
            ver_info["status"] = "retired"
    _save_registry(registry)

    # Update config.yaml if checkpoint is local
    config = _load_config()
    updated_config = False
    if payload.checkpoint_path:
        if payload.model_key == "crop_identifier":
            config.setdefault("models", {})["crop_identifier"] = {
                "path": payload.checkpoint_path,
                "labels": payload.labels_path or config.get("models", {}).get("crop_identifier", {}).get("labels"),
                "arch": payload.arch,
                "temperature": temperature,
            }
            updated_config = True
        elif payload.model_key.endswith("_disease"):
            crop_name_raw = payload.model_key.replace("_disease", "")
            crop_key = "_".join(part.capitalize() for part in crop_name_raw.split("_"))
            disease_models = config.setdefault("models", {}).setdefault("disease_models", {})
            existing = disease_models.get(crop_key, {})
            disease_models[crop_key] = {
                **existing,
                "path": payload.checkpoint_path,
                "labels": payload.labels_path or existing.get("labels"),
                "arch": payload.arch,
                "temperature": temperature,
            }
            updated_config = True

    if updated_config:
        _save_config(config)
        try:
            from app import pipeline as _pipeline
            _pipeline.reload_config()
        except Exception:
            # Hot reload failure is non-blocking after config save
            pass

    return {
        "status": "promoted",
        "model_key": payload.model_key,
        "version": payload.version,
        "active_version": payload.version,
        "storage": "postgresql_database",
        "test_acc": test_acc,
        "macro_f1": macro_f1,
        "temperature": temperature,
        "promoted_at": new_db_record.promoted_at.isoformat(),
    }


class RollbackRequest(BaseModel):
    model_key: str
    target_version: str | None = None


@router.post("/rollback", response_model=ModelRollbackResponse)
def rollback_model(
    payload: RollbackRequest,
    is_admin: str = Depends(require_admin_role),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Roll back active model to target version in durable database registry."""
    _seed_db_from_file_if_empty(session)
    active_rec = (
        session.query(ModelRegistryRecord)
        .filter(ModelRegistryRecord.model_key == payload.model_key, ModelRegistryRecord.status == "active")
        .first()
    )

    records = (
        session.query(ModelRegistryRecord)
        .filter(ModelRegistryRecord.model_key == payload.model_key)
        .order_by(ModelRegistryRecord.promoted_at.desc())
        .all()
    )
    if not records:
        raise HTTPException(status_code=404, detail=f"Model '{payload.model_key}' not in registry.")

    current_active = active_rec.version if active_rec else None
    target_ver = payload.target_version
    if not target_ver:
        retired = [r for r in records if r.version != current_active]
        if not retired:
            raise HTTPException(status_code=400, detail="No previous versions available for rollback.")
        target_ver = retired[0].version

    target_rec = next((r for r in records if r.version == target_ver), None)
    if not target_rec:
        raise HTTPException(status_code=404, detail=f"Target version '{target_ver}' not found in registry.")

    # Update DB statuses
    for r in records:
        r.status = "active" if r.version == target_ver else "retired"
    session.commit()

    # Sync local file
    registry = _load_registry()
    entry = registry.get("models", {}).get(payload.model_key, {})
    entry["active_version"] = target_ver
    for v, info in entry.get("versions", {}).items():
        info["status"] = "active" if v == target_ver else "retired"
    _save_registry(registry)

    logger.info("Model '%s' rolled back from '%s' to '%s'", payload.model_key, current_active, target_ver)
    return {
        "status": "rolled_back",
        "model_key": payload.model_key,
        "previous_version": current_active,
        "active_version": target_ver,
        "storage": "postgresql_database",
    }
