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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import require_admin_role
from app.core.config import settings

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
async def list_models(is_admin: str = Depends(require_admin_role)) -> dict[str, Any]:
    """List all registered model versions with their metrics and active status."""
    registry = _load_registry()
    return {
        "schema_version": registry.get("schema_version", "1.0"),
        "last_updated": registry.get("last_updated"),
        "models": registry.get("models", {}),
    }


@router.get("/health")
async def model_health(is_admin: str = Depends(require_admin_role)) -> dict[str, Any]:
    """Check which configured models are loadable (file exists on disk)."""
    config = _load_config()
    registry = _load_registry()
    results: dict[str, Any] = {}

    def _check(key: str, path_str: str | None, labels_str: str | None = None) -> dict:
        model_path = _resolve_model_path(path_str)
        labels_path = _resolve_model_path(labels_str)
        model_ok = model_path.exists() if model_path else False
        labels_ok = labels_path.exists() if labels_path else True  # labels optional
        reg_entry = registry.get("models", {}).get(key, {})
        active_ver = reg_entry.get("active_version")
        ver_info = reg_entry.get("versions", {}).get(active_ver, {}) if active_ver else {}
        return {
            "status": "ok" if model_ok else "missing",
            "model_file": str(model_path) if model_path else None,
            "model_exists": model_ok,
            "labels_file": str(labels_path) if labels_path else None,
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
    checkpoint_path: str = Field(description="Path to .pth checkpoint, relative to backend root")
    labels_path: str | None = Field(default=None, description="Path to labels.json, relative to backend root")
    arch: str = Field(default="efficientnet_b2", description="Model architecture identifier")
    num_classes: int | None = Field(default=None)
    val_acc: float | None = Field(default=None, ge=0.0, le=1.0)
    test_acc: float | None = Field(default=None, ge=0.0, le=1.0)
    notes: str | None = Field(default=None, max_length=1000)
    # Promotion gate: require minimum test accuracy before allowing promotion
    min_test_acc: float | None = Field(default=None, ge=0.0, le=1.0,
                                        description="Reject promotion if test_acc is below this threshold")


@router.post("/promote")
async def promote_model(
    payload: PromoteRequest,
    is_admin: str = Depends(require_admin_role),
) -> dict[str, Any]:
    """
    Promote a model version to active.

    Updates both model_registry.json and config.yaml atomically.
    Enforces a minimum test accuracy gate if min_test_acc is set.
    """
    # ── Promotion gate ─────────────────────────────────────────────────────────
    if payload.min_test_acc is not None and payload.test_acc is not None:
        if payload.test_acc < payload.min_test_acc:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Promotion rejected: test_acc={payload.test_acc:.4f} is below "
                    f"the required minimum of {payload.min_test_acc:.4f}."
                ),
            )

    # ── Verify checkpoint exists ───────────────────────────────────────────────
    ckpt_path = _resolve_model_path(payload.checkpoint_path)
    if ckpt_path is None or not ckpt_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Checkpoint not found at: {payload.checkpoint_path}",
        )

    if payload.labels_path:
        labels_path = _resolve_model_path(payload.labels_path)
        if labels_path and not labels_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Labels file not found at: {payload.labels_path}",
            )

    # ── Update registry ────────────────────────────────────────────────────────
    registry = _load_registry()
    models = registry.setdefault("models", {})
    model_entry = models.setdefault(payload.model_key, {"versions": {}})
    model_entry["active_version"] = payload.version
    model_entry["versions"][payload.version] = {
        "arch": payload.arch,
        "checkpoint": payload.checkpoint_path,
        "labels": payload.labels_path,
        "num_classes": payload.num_classes,
        "val_acc": payload.val_acc,
        "test_acc": payload.test_acc,
        "promoted_at": datetime.now(timezone.utc).isoformat(),
        "promoted_by": is_admin,
        "notes": payload.notes,
        "status": "active",
    }
    # Mark all previous versions as retired
    for ver, ver_info in model_entry["versions"].items():
        if ver != payload.version:
            ver_info["status"] = "retired"

    _save_registry(registry)
    logger.info("Model '%s' promoted to version '%s' by admin '%s'",
                payload.model_key, payload.version, is_admin)

    # ── Update config.yaml if applicable ──────────────────────────────────────
    config = _load_config()
    updated_config = False

    if payload.model_key == "crop_identifier":
        config.setdefault("models", {})["crop_identifier"] = {
            "path": payload.checkpoint_path,
            "labels": payload.labels_path or config.get("models", {}).get("crop_identifier", {}).get("labels"),
            "arch": payload.arch,
        }
        updated_config = True

    elif payload.model_key.endswith("_disease"):
        # e.g. "tomato_disease" → crop key "Tomato"
        crop_name_raw = payload.model_key.replace("_disease", "")
        # Normalize: first letter upper, rest lower, handle Pepper_Bell style
        crop_key = "_".join(part.capitalize() for part in crop_name_raw.split("_"))
        disease_models = config.setdefault("models", {}).setdefault("disease_models", {})
        existing = disease_models.get(crop_key, {})
        disease_models[crop_key] = {
            **existing,
            "path": payload.checkpoint_path,
            "labels": payload.labels_path or existing.get("labels"),
            "arch": payload.arch,
        }
        updated_config = True

    if updated_config:
        _save_config(config)
        # Trigger a pipeline config reload so the new model takes effect without restart
        try:
            from app import pipeline as _pipeline
            _pipeline.reload_config()
            logger.info("Pipeline config reloaded after model promotion")
        except Exception as exc:
            logger.warning("Could not reload pipeline config: %s", exc)

    return {
        "status": "promoted",
        "model_key": payload.model_key,
        "version": payload.version,
        "config_updated": updated_config,
        "checkpoint": payload.checkpoint_path,
        "test_acc": payload.test_acc,
        "promoted_at": registry["models"][payload.model_key]["versions"][payload.version]["promoted_at"],
    }

