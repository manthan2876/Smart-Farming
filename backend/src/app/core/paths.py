from pathlib import Path

from app.core.config import settings


def ensure_storage_directories() -> None:
    for directory in (settings.DATA_ROOT, settings.UPLOAD_ROOT, settings.PROCESSED_ROOT, settings.AUDIO_ROOT):
        directory.mkdir(parents=True, exist_ok=True)


def resolve_backend_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return settings.BACKEND_ROOT / candidate


def resolve_storage_path(path: str | Path) -> Path:
    candidate = resolve_backend_path(path)
    storage_root = settings.DATA_ROOT.resolve()
    try:
        candidate.resolve().relative_to(storage_root)
    except ValueError as exc:
        raise ValueError(f"Path is outside configured storage: {path}") from exc
    return candidate


def storage_relative_path(path: str | Path) -> str:
    return resolve_backend_path(path).resolve().relative_to(settings.BACKEND_ROOT.resolve()).as_posix()