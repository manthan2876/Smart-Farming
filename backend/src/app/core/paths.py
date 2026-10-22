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


def _logical_storage_roots() -> tuple[tuple[Path, Path], ...]:
    return (
        (Path("data/uploads"), settings.UPLOAD_ROOT),
        (Path("data/processed"), settings.PROCESSED_ROOT),
        (Path("data/audio"), settings.AUDIO_ROOT),
        (Path("data"), settings.DATA_ROOT),
    )


def resolve_storage_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        for logical_root, configured_root in _logical_storage_roots():
            if candidate.parts[: len(logical_root.parts)] == logical_root.parts:
                candidate = configured_root.joinpath(*candidate.parts[len(logical_root.parts) :])
                break
        else:
            candidate = resolve_backend_path(candidate)

    resolved = candidate.resolve()
    allowed_roots = (
        settings.DATA_ROOT,
        settings.UPLOAD_ROOT,
        settings.PROCESSED_ROOT,
        settings.AUDIO_ROOT,
    )
    for root in allowed_roots:
        try:
            resolved.relative_to(root.resolve())
            return resolved
        except ValueError:
            continue
    raise ValueError(f"Path is outside configured storage: {path}")


def storage_relative_path(path: str | Path) -> str:
    resolved = resolve_storage_path(path).resolve()
    try:
        return resolved.relative_to(settings.BACKEND_ROOT.resolve()).as_posix()
    except ValueError:
        for logical_root, configured_root in _logical_storage_roots():
            try:
                relative = resolved.relative_to(configured_root.resolve())
                return (logical_root / relative).as_posix()
            except ValueError:
                continue
        return (Path("data") / resolved.relative_to(settings.DATA_ROOT.resolve())).as_posix()