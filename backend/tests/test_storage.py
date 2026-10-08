import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.storage import (
    LocalStorageBackend,
    S3StorageBackend,
    get_storage,
    reset_storage,
    purge_orphaned_blobs,
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
# S3StorageBackend Tests (AWS S3)
# ==============================================================================

def test_s3_storage_backend_instantiation_defaults():
    backend = S3StorageBackend()
    assert backend.bucket_name == settings.AWS_S3_BUCKET
    assert backend.region == settings.AWS_REGION
    assert backend.region_name == settings.AWS_REGION


def test_s3_storage_backend_instantiation_custom():
    backend = S3StorageBackend(
        bucket_name="custom-farming-bucket",
        region="us-west-2",
        access_key_id="test_key_id",
        secret_access_key="test_secret",
        endpoint_url="http://localhost:4566",
    )
    assert backend.bucket_name == "custom-farming-bucket"
    assert backend.region == "us-west-2"
    assert backend.access_key_id == "test_key_id"
    assert backend.secret_access_key == "test_secret"
    assert backend.endpoint_url == "http://localhost:4566"


def test_s3_storage_key_normalization():
    backend = S3StorageBackend()
    assert backend._normalize_key("data/uploads/leaf.jpg") == "uploads/leaf.jpg"
    assert backend._normalize_key(r"data\uploads\leaf.jpg") == "uploads/leaf.jpg"
    assert backend._normalize_key("/uploads/leaf.jpg") == "uploads/leaf.jpg"
    assert backend._normalize_key("processed/gradcam.png") == "processed/gradcam.png"


def test_s3_client_configuration():
    backend = S3StorageBackend(
        bucket_name="test-bucket",
        region="us-east-1",
        access_key_id="AKIAEXAMPLE",
        secret_access_key="SECRETEXAMPLE",
    )
    with patch("boto3.client") as mock_boto:
        mock_boto.return_value = MagicMock()
        client = backend.client
        assert client is not None
        mock_boto.assert_called_once()
        args, kwargs = mock_boto.call_args
        assert args[0] == "s3"
        assert kwargs["aws_access_key_id"] == "AKIAEXAMPLE"
        assert kwargs["aws_secret_access_key"] == "SECRETEXAMPLE"
        config = kwargs["config"]
        assert config.signature_version == "s3v4"
        assert config.region_name == "us-east-1"


def test_s3_save_applies_aes256_encryption():
    backend = S3StorageBackend(bucket_name="my-bucket")
    mock_client = MagicMock()
    backend._client = mock_client

    content = b"leaf-raw-image-bytes"
    saved_key = backend.save(content, "data/uploads/leaf_01.jpg", content_type="image/jpeg")

    assert saved_key == "uploads/leaf_01.jpg"
    mock_client.put_object.assert_called_once_with(
        Bucket="my-bucket",
        Key="uploads/leaf_01.jpg",
        Body=content,
        ContentType="image/jpeg",
        ServerSideEncryption="AES256",
    )


def test_s3_get_reads_content():
    backend = S3StorageBackend(bucket_name="my-bucket")
    mock_client = MagicMock()
    mock_body = MagicMock()
    mock_body.read.return_value = b"retrieved-leaf-bytes"
    mock_client.get_object.return_value = {"Body": mock_body}
    backend._client = mock_client

    result = backend.get("data/uploads/leaf_01.jpg")
    assert result == b"retrieved-leaf-bytes"
    mock_client.get_object.assert_called_once_with(
        Bucket="my-bucket",
        Key="uploads/leaf_01.jpg",
    )


def test_s3_get_url_generates_presigned_url():
    backend = S3StorageBackend(bucket_name="my-bucket")
    mock_client = MagicMock()
    mock_client.generate_presigned_url.return_value = "https://my-bucket.s3.amazonaws.com/uploads/leaf.jpg?sig=xyz"
    backend._client = mock_client

    url = backend.get_url("uploads/leaf.jpg", expires_in=600)
    assert url == "https://my-bucket.s3.amazonaws.com/uploads/leaf.jpg?sig=xyz"
    mock_client.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={"Bucket": "my-bucket", "Key": "uploads/leaf.jpg"},
        ExpiresIn=600,
    )


def test_s3_delete_success():
    backend = S3StorageBackend(bucket_name="my-bucket")
    mock_client = MagicMock()
    backend._client = mock_client

    assert backend.delete("uploads/leaf.jpg") is True
    mock_client.delete_object.assert_called_once_with(
        Bucket="my-bucket",
        Key="uploads/leaf.jpg",
    )


def test_s3_delete_handles_exception():
    backend = S3StorageBackend(bucket_name="my-bucket")
    mock_client = MagicMock()
    mock_client.delete_object.side_effect = Exception("AWS Access Denied")
    backend._client = mock_client

    assert backend.delete("uploads/leaf.jpg") is False


def test_s3_exists_true():
    backend = S3StorageBackend(bucket_name="my-bucket")
    mock_client = MagicMock()
    mock_client.head_object.return_value = {"ContentLength": 1234}
    backend._client = mock_client

    assert backend.exists("uploads/leaf.jpg") is True
    mock_client.head_object.assert_called_once_with(
        Bucket="my-bucket",
        Key="uploads/leaf.jpg",
    )


def test_s3_exists_false():
    backend = S3StorageBackend(bucket_name="my-bucket")
    mock_client = MagicMock()
    mock_client.head_object.side_effect = ClientError(
        {"Error": {"Code": "404", "Message": "Not Found"}},
        "HeadObject",
    )
    backend._client = mock_client

    assert backend.exists("uploads/nonexistent.jpg") is False


def test_s3_list_objects():
    backend = S3StorageBackend(bucket_name="my-bucket")
    mock_client = MagicMock()
    mock_paginator = MagicMock()
    mock_paginator.paginate.return_value = [
        {"Contents": [{"Key": "uploads/leaf1.jpg"}, {"Key": "uploads/leaf2.jpg"}]},
        {"Contents": [{"Key": "uploads/leaf3.jpg"}]},
    ]
    mock_client.get_paginator.return_value = mock_paginator
    backend._client = mock_client

    keys = backend.list_objects(prefix="uploads")
    assert keys == ["uploads/leaf1.jpg", "uploads/leaf2.jpg", "uploads/leaf3.jpg"]
    mock_client.get_paginator.assert_called_once_with("list_objects_v2")
    mock_paginator.paginate.assert_called_once_with(
        Bucket="my-bucket",
        Prefix="uploads",
    )


# ==============================================================================
# Factory & Module Interface Tests
# ==============================================================================

def test_get_storage_factory_s3():
    reset_storage()
    with patch.object(settings, "STORAGE_BACKEND", "s3"):
        backend = get_storage()
        assert isinstance(backend, S3StorageBackend)
    reset_storage()


def test_get_storage_factory_local():
    reset_storage()
    with patch.object(settings, "STORAGE_BACKEND", "local"):
        backend = get_storage()
        assert isinstance(backend, LocalStorageBackend)
    reset_storage()


def test_google_storage_implementation_removed():
    import app.core.storage as storage_mod
    assert not hasattr(storage_mod, "GCSStorageBackend"), "GCSStorageBackend must be removed"
    assert not hasattr(settings, "GCS_BUCKET"), "GCS_BUCKET setting must be removed"


def test_purge_orphaned_blobs_s3():
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = []

    with patch("app.core.storage.S3StorageBackend") as mock_s3_cls:
        mock_instance = MagicMock()
        mock_instance.bucket_name = "test-bucket"
        mock_client = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {"Contents": [{"Key": "uploads/orphan1.jpg"}, {"Key": "uploads/orphan2.jpg"}]}
        ]
        mock_client.get_paginator.return_value = mock_paginator
        mock_instance.client = mock_client
        mock_s3_cls.return_value = mock_instance

        with patch.object(settings, "STORAGE_BACKEND", "s3"):
            res = purge_orphaned_blobs(mock_session, dry_run=True, prefixes=["uploads"])
            assert res["status"] == "dry_run"
            assert res["s3_unreferenced_count"] == 2
            assert "uploads/orphan1.jpg" in res["s3_files"]
