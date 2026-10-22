from pathlib import Path

import pytest

from app.core.config import settings
from app.core.paths import resolve_storage_path, storage_relative_path


def test_external_upload_root_round_trips_through_logical_storage_path(monkeypatch, tmp_path: Path):
    backend_root = tmp_path / "backend"
    data_root = backend_root / "data"
    upload_root = tmp_path / "uploads"
    processed_root = data_root / "processed"
    audio_root = data_root / "audio"
    for setting, value in (
        ("BACKEND_ROOT", backend_root),
        ("DATA_ROOT", data_root),
        ("UPLOAD_ROOT", upload_root),
        ("PROCESSED_ROOT", processed_root),
        ("AUDIO_ROOT", audio_root),
    ):
        monkeypatch.setattr(settings, setting, value)

    image_path = upload_root / "scan.jpg"
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b"image")

    logical_path = storage_relative_path(image_path)

    assert logical_path == "data/uploads/scan.jpg"
    assert resolve_storage_path(logical_path) == image_path.resolve()

    data_file = data_root / "metadata.json"
    data_file.parent.mkdir(parents=True)
    data_file.write_text("{}", encoding="utf-8")
    data_logical_path = storage_relative_path(data_file)

    assert data_logical_path == "data/metadata.json"
    assert resolve_storage_path(data_logical_path) == data_file.resolve()


def test_resolve_storage_path_rejects_paths_outside_configured_roots(monkeypatch, tmp_path: Path):
    backend_root = tmp_path / "backend"
    data_root = backend_root / "data"
    for setting, value in (
        ("BACKEND_ROOT", backend_root),
        ("DATA_ROOT", data_root),
        ("UPLOAD_ROOT", data_root / "uploads"),
        ("PROCESSED_ROOT", data_root / "processed"),
        ("AUDIO_ROOT", data_root / "audio"),
    ):
        monkeypatch.setattr(settings, setting, value)

    with pytest.raises(ValueError, match="outside configured storage"):
        resolve_storage_path(tmp_path / "private" / "secret.txt")
