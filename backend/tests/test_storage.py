import io
import os
import glob
import re
import sys
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch



try:
    import pytest
except ImportError:
    class _MockPytest:
        @staticmethod
        def raises(expected_exception, match=None):
            @contextmanager
            def _ctx():
                try:
                    yield
                except expected_exception as e:
                    if match and not re.search(match, str(e)):
                        raise AssertionError(f"Pattern '{match}' did not match '{str(e)}'")
                    return
                except Exception as e:
                    raise AssertionError(f"Expected {expected_exception}, got {type(e)}")
                else:
                    raise AssertionError(f"Expected {expected_exception} but nothing was raised")
            return _ctx()
    pytest = _MockPytest()

from app.core.config import settings
from app.core.storage import (
    LocalStorageBackend,
    SupabaseStorageBackend,
    get_storage,
    reset_storage,
    purge_orphaned_blobs,
    compress_image_bytes,
    prune_cached_audio,
    prune_unflagged_heatmaps,
)


# ==============================================================================
# LocalStorageBackend Tests
# ==============================================================================

def test_local_storage_backend_save_and_read(tmp_path: Path):
    backend = LocalStorageBackend(data_root=tmp_path)
    data = b"sample leaf image bytes for testing"
    key = backend.save(data, "uploads/test_leaf.jpg", content_type="image/jpeg")

    assert "uploads/test_leaf.jpg" in key
    assert backend.exists(key)
    assert backend.get(key) == data

    # Test presigned / local URL
    url = backend.get_url(key)
    assert "test_leaf.jpg" in url

    # Test delete
    assert backend.delete(key) is True
    assert not backend.exists(key)


def test_local_storage_backend_path_traversal(tmp_path: Path):
    backend = LocalStorageBackend(data_root=tmp_path)
    with pytest.raises(ValueError, match="Path traversal detected"):
        backend.save(b"malicious", "../../etc/passwd")


def test_local_storage_backend_list_objects(tmp_path: Path):
    backend = LocalStorageBackend(data_root=tmp_path)
    backend.save(b"data1", "uploads/a.jpg")
    backend.save(b"data2", "uploads/b.jpg")
    backend.save(b"data3", "processed/c.jpg")

    all_objs = backend.list_objects()
    assert len(all_objs) == 3

    upload_objs = backend.list_objects(prefix="uploads")
    assert len(upload_objs) == 2


# ==============================================================================
# SupabaseStorageBackend Tests
# ==============================================================================

def test_supabase_storage_backend_instantiation_defaults():
    backend = SupabaseStorageBackend()
    assert backend.bucket_name == settings.SUPABASE_BUCKET
    assert backend.supabase_url == (settings.SUPABASE_URL or "").rstrip("/")


def test_supabase_storage_backend_instantiation_custom():
    backend = SupabaseStorageBackend(
        supabase_url="https://xyzcompany.supabase.co",
        service_role_key="service_role_test_key",
        bucket_name="custom-farming-bucket",
    )
    assert backend.supabase_url == "https://xyzcompany.supabase.co"
    assert backend.service_role_key == "service_role_test_key"
    assert backend.bucket_name == "custom-farming-bucket"


def test_supabase_storage_key_normalization():
    backend = SupabaseStorageBackend()
    assert backend._normalize_key("data/uploads/leaf.jpg") == "uploads/leaf.jpg"
    assert backend._normalize_key(r"data\uploads\leaf.jpg") == "uploads/leaf.jpg"
    assert backend._normalize_key("/uploads/leaf.jpg") == "uploads/leaf.jpg"
    assert backend._normalize_key("processed/gradcam.png") == "processed/gradcam.png"


def test_supabase_headers():
    backend = SupabaseStorageBackend(
        supabase_url="https://xyz.supabase.co",
        service_role_key="secret-key-123",
        bucket_name="test-bucket",
    )
    headers = backend._get_headers()
    assert headers["Authorization"] == "Bearer secret-key-123"
    assert headers["apikey"] == "secret-key-123"


def test_supabase_save():
    backend = SupabaseStorageBackend(
        supabase_url="https://xyz.supabase.co",
        service_role_key="secret-key",
        bucket_name="test-bucket",
    )
    mock_resp = MagicMock()
    mock_resp.status_code = 200

    content = b"leaf-raw-image-bytes"
    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.post.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        saved_key = backend.save(content, "data/uploads/leaf_01.jpg", content_type="image/jpeg")
        assert saved_key == "uploads/leaf_01.jpg"
        mock_client.post.assert_called_once()
        args, kwargs = mock_client.post.call_args
        assert "storage/v1/object/test-bucket/uploads/leaf_01.jpg" in args[0]
        assert kwargs["headers"]["Content-Type"] == "image/jpeg"
        assert kwargs["content"] == content


def test_supabase_get():
    backend = SupabaseStorageBackend(
        supabase_url="https://xyz.supabase.co",
        service_role_key="secret-key",
        bucket_name="test-bucket",
    )
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b"downloaded-leaf-content"

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        content = backend.get("uploads/leaf_01.jpg")
        assert content == b"downloaded-leaf-content"
        args, _ = mock_client.get.call_args
        assert "storage/v1/object/authenticated/test-bucket/uploads/leaf_01.jpg" in args[0]


def test_supabase_get_url_signed():
    backend = SupabaseStorageBackend(
        supabase_url="https://xyz.supabase.co",
        service_role_key="secret-key",
        bucket_name="test-bucket",
    )
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"signedURL": "/storage/v1/object/sign/test-bucket/uploads/leaf.jpg?token=abc123xyz"}

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.post.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        url = backend.get_url("uploads/leaf.jpg", expires_in=600)
        assert url == "https://xyz.supabase.co/storage/v1/object/sign/test-bucket/uploads/leaf.jpg?token=abc123xyz"


def test_supabase_delete():
    backend = SupabaseStorageBackend(
        supabase_url="https://xyz.supabase.co",
        service_role_key="secret-key",
        bucket_name="test-bucket",
    )
    mock_resp = MagicMock()
    mock_resp.status_code = 200

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.request.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        res = backend.delete("uploads/leaf.jpg")
        assert res is True
        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert args[0] == "DELETE"
        assert kwargs["json"] == {"prefixes": ["uploads/leaf.jpg"]}


def test_supabase_list_objects():
    backend = SupabaseStorageBackend(
        supabase_url="https://xyz.supabase.co",
        service_role_key="secret-key",
        bucket_name="test-bucket",
    )
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {"name": "leaf1.jpg", "id": "id-1"},
        {"name": "leaf2.jpg", "id": "id-2"},
    ]

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.post.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        items = backend.list_objects(prefix="uploads")
        assert len(items) == 2
        assert items[0] == "uploads/leaf1.jpg"
        assert items[1] == "uploads/leaf2.jpg"


# ==============================================================================
# Factory & Implementation Verification Tests
# ==============================================================================

def test_get_storage_factory_supabase():
    reset_storage()
    with patch.object(settings, "STORAGE_BACKEND", "supabase"):
        backend = get_storage()
        assert isinstance(backend, SupabaseStorageBackend)
    reset_storage()


def test_get_storage_factory_local():
    reset_storage()
    with patch.object(settings, "STORAGE_BACKEND", "local"):
        backend = get_storage()
        assert isinstance(backend, LocalStorageBackend)
    reset_storage()


def test_aws_and_google_storage_removed():
    import app.core.storage as storage_mod
    assert not hasattr(storage_mod, "GCSStorageBackend"), "GCSStorageBackend must be removed"
    assert not hasattr(settings, "GCS_BUCKET"), "GCS_BUCKET setting must be removed"


def test_purge_orphaned_blobs_supabase():
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = []

    with patch("app.core.storage.SupabaseStorageBackend") as mock_supa_cls:
        mock_instance = MagicMock()
        mock_instance.bucket_name = "test-bucket"
        mock_instance.list_objects.return_value = ["uploads/orphan1.jpg", "uploads/orphan2.jpg"]
        mock_supa_cls.return_value = mock_instance

        with patch.object(settings, "STORAGE_BACKEND", "supabase"):
            res = purge_orphaned_blobs(mock_session, dry_run=True, prefixes=["uploads"])
            assert res["status"] == "dry_run"
            assert res["cloud_unreferenced_count"] == 2
            assert "uploads/orphan1.jpg" in res["cloud_files"]


def test_compress_image_bytes_downscaling():
    from PIL import Image

    # Create large 2000x1500 test image
    img = Image.new("RGB", (2000, 1500), color="forestgreen")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    raw_data = buf.getvalue()

    compressed, mime = compress_image_bytes(raw_data, max_dim=1280, quality=85)
    assert mime == "image/jpeg"
    assert len(compressed) < len(raw_data)

    with Image.open(io.BytesIO(compressed)) as res_img:
        w, h = res_img.size
        assert max(w, h) <= 1280
        assert w == 1280 or h == 1280


def test_compress_image_bytes_preserves_small():
    from PIL import Image

    img = Image.new("RGB", (400, 300), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=75)
    raw_data = buf.getvalue()

    compressed, mime = compress_image_bytes(raw_data, max_dim=1280, quality=85)
    assert mime == "image/jpeg"
    with Image.open(io.BytesIO(compressed)) as res_img:
        assert res_img.size == (400, 300)


def test_prune_cached_audio(tmp_path: Path):
    import time

    audio_dir = tmp_path / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    old_file = audio_dir / "old_audio.wav"
    old_file.write_bytes(b"old wav content")
    new_file = audio_dir / "new_audio.mp3"
    new_file.write_bytes(b"new mp3 content")

    # Set old_file mtime to 35 days ago
    old_mtime = time.time() - (35 * 86400)
    os.utime(old_file, (old_mtime, old_mtime))

    with patch.object(settings, "AUDIO_ROOT", audio_dir), patch.object(settings, "DATA_ROOT", tmp_path):
        # Dry run
        dry_res = prune_cached_audio(dry_run=True, max_age_days=30)
        assert dry_res["local_pruned"] == 1
        assert old_file.exists()

        # Actual run
        run_res = prune_cached_audio(dry_run=False, max_age_days=30)
        assert run_res["local_pruned"] == 1
        assert not old_file.exists()
        assert new_file.exists()


if __name__ == "__main__":
    import inspect
    import sys
    import tempfile
    passed = 0
    failed = 0
    for name, func in list(globals().items()):
        if name.startswith("test_") and callable(func):
            try:
                sig = inspect.signature(func)
                if "tmp_path" in sig.parameters:
                    with tempfile.TemporaryDirectory() as td:
                        func(Path(td))
                else:
                    func()
                print(f"[PASS] {name}")
                passed += 1
            except Exception as e:
                print(f"[FAIL] {name}: {e}")
                import traceback
                traceback.print_exc()
                failed += 1
    print("\n==========================================")
    print(f"Results: {passed} passed, {failed} failed")
    print("==========================================")
    sys.exit(1 if failed else 0)
