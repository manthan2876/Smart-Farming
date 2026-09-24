"""
model_client.py — HTTP client for invoking Server 2 (Model Inference Server)
"""

from __future__ import annotations

import httpx
from fastapi import HTTPException, status
from app.core.config import settings


async def call_model_service(
    image_bytes: bytes,
    filename: str,
    content_type: str = "image/jpeg",
) -> dict:
    """
    Invoke Server 2 (Model Inference Server) over HTTP.
    Returns the CV prediction results dict (crop, disease, severity, pests, etc.).
    """
    url = f"{settings.MODEL_SERVER_URL.rstrip('/')}/predict"
    headers = {}

    # Support GCP OIDC Identity Token when deployed to Cloud Run in the future
    if "run.app" in settings.MODEL_SERVER_URL:
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import id_token
            auth_req = Request()
            token = id_token.fetch_id_token(auth_req, settings.MODEL_SERVER_URL)
            headers["Authorization"] = f"Bearer {token}"
        except Exception as exc:
            print(f"[ModelClient] Failed to obtain GCP identity token: {exc}")

    try:
        async with httpx.AsyncClient(timeout=float(settings.MODEL_SERVER_TIMEOUT)) as client:
            response = await client.post(
                url,
                files={"file": (filename, image_bytes, content_type or "image/jpeg")},
                headers=headers,
            )

            if response.status_code == 400:
                detail = "Image quality check failed."
                try:
                    data = response.json()
                    detail = data.get("detail", detail)
                except Exception:
                    pass
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Model Server error ({response.status_code}): {response.text}",
                )

            return response.json()

    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model Inference Server is unreachable at {settings.MODEL_SERVER_URL}. Please ensure Server 2 is running on port 8001.",
        )


async def execute_remote_vision_pipeline(
    context: dict,
    image_bytes: bytes,
    filename: str,
    content_type: str = "image/jpeg",
) -> dict:
    """
    Send image to Server 2 and merge the vision results into the pipeline context.
    """
    cv_result = await call_model_service(image_bytes, filename, content_type)

def merge_and_save_cv_result(context: dict, cv_result: dict, filename: str) -> dict:
    """
    Merges CV results from model_service into pipeline context and persists
    the processed Grad-CAM/heatmap image to storage (S3/local).
    """
    context.setdefault("crop", {}).update(cv_result.get("crop", {}))
    context.setdefault("disease", {}).update(cv_result.get("disease", {}))
    context.setdefault("severity", {}).update(cv_result.get("severity", {}))
    context["pests"] = cv_result.get("pests", [])
    context.setdefault("pest_classification", {}).update(cv_result.get("pest_classification", {}))

    for stage, st in cv_result.get("status", {}).items():
        context.setdefault("status", {})[stage] = st

    for stage, stage_info in cv_result.get("stages", {}).items():
        context.setdefault("stages", {})[stage] = stage_info

    for k, v in cv_result.get("image", {}).items():
        if k != "processed_image_base64":
            context.setdefault("image", {})[k] = v

    if "notes" in cv_result:
        context.setdefault("notes", []).extend(cv_result["notes"])

    # Persist the processed Grad-CAM / heatmap image (uploads to S3 + local disk)
    processed_b64 = cv_result.get("image", {}).get("processed_image_base64")
    if processed_b64:
        import base64
        from pathlib import Path
        from app.core.config import settings
        from app.core.storage import get_storage

        try:
            processed_bytes = base64.b64decode(processed_b64)
            clean_filename = Path(filename).name
            storage = get_storage()
            storage.save(processed_bytes, f"processed/{clean_filename}", content_type="image/jpeg")

            # Always maintain a local disk copy for FastAPI static mount
            local_proc_path = settings.DATA_ROOT / "processed" / clean_filename
            local_proc_path.parent.mkdir(parents=True, exist_ok=True)
            if not local_proc_path.exists():
                local_proc_path.write_bytes(processed_bytes)

            context.setdefault("image", {})["processed_path"] = f"data/processed/{clean_filename}"
        except Exception as exc:
            print(f"[ModelClient] Failed to persist processed image: {exc}")

    return context


_merge_and_save_cv_result = merge_and_save_cv_result


async def execute_remote_vision_pipeline(
    context: dict,
    image_bytes: bytes,
    filename: str,
    content_type: str = "image/jpeg",
) -> dict:
    """
    Send image to Server 2 and merge the vision results into the pipeline context.
    """
    cv_result = await call_model_service(image_bytes, filename, content_type)
    return _merge_and_save_cv_result(context, cv_result, filename)


def call_model_service_sync(
    image_bytes: bytes,
    filename: str,
    content_type: str = "image/jpeg",
) -> dict:
    """
    Synchronous version of call_model_service (for ARQ workers or background threads).
    """
    url = f"{settings.MODEL_SERVER_URL.rstrip('/')}/predict"
    headers = {}

    if "run.app" in settings.MODEL_SERVER_URL:
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import id_token
            auth_req = Request()
            token = id_token.fetch_id_token(auth_req, settings.MODEL_SERVER_URL)
            headers["Authorization"] = f"Bearer {token}"
        except Exception as exc:
            print(f"[ModelClient] Failed to obtain GCP identity token: {exc}")

    try:
        with httpx.Client(timeout=float(settings.MODEL_SERVER_TIMEOUT)) as client:
            response = client.post(
                url,
                files={"file": (filename, image_bytes, content_type or "image/jpeg")},
                headers=headers,
            )

            if response.status_code == 400:
                detail = "Image quality check failed."
                try:
                    data = response.json()
                    detail = data.get("detail", detail)
                except Exception:
                    pass
                raise ValueError(detail)

            if response.status_code != 200:
                raise RuntimeError(
                    f"Model Server error ({response.status_code}): {response.text}"
                )

            return response.json()

    except httpx.ConnectError:
        raise RuntimeError(
            f"Model Inference Server is unreachable at {settings.MODEL_SERVER_URL}. Please ensure Server 2 is running on port 8001."
        )


def execute_remote_vision_pipeline_sync(
    context: dict,
    image_bytes: bytes,
    filename: str,
    content_type: str = "image/jpeg",
) -> dict:
    """
    Synchronous version of execute_remote_vision_pipeline.
    """
    cv_result = call_model_service_sync(image_bytes, filename, content_type)
    return _merge_and_save_cv_result(context, cv_result, filename)
