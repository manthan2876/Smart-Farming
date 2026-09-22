import pytest
from pathlib import Path
from app.core.storage import get_storage, LocalStorageBackend, S3StorageBackend

def test_local_storage_backend_save_and_read(tmp_path):
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

def test_s3_storage_backend_instantiation():
    backend = S3StorageBackend(
        bucket_name="smart-farming-data-575509634394-us-east-1-an",
        region_name="us-east-1",
        access_key="test_key",
        secret_key="test_secret",
    )
    assert backend.bucket_name == "smart-farming-data-575509634394-us-east-1-an"
    assert backend.region_name == "us-east-1"

def test_get_storage_factory():
    backend = get_storage()
    assert backend is not None
    assert isinstance(backend, (LocalStorageBackend, S3StorageBackend))

