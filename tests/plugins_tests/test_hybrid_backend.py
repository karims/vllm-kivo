from unittest.mock import patch

import pytest
from vllm.plugins.kivo_kv.hybrid_backend import HybridRAMMinIOBackend
from vllm.plugins.kivo_kv.config import KVConfig
import tempfile
import shutil
import os


@pytest.fixture(scope="function")
def mock_minio_config():
    # Temporarily override config to use a local MinIO-like directory
    temp_dir = tempfile.mkdtemp()
    config = KVConfig()
    config.backend = "hybrid"
    config.minio_root = temp_dir  # Custom field for local emulation (optional)
    yield config
    shutil.rmtree(temp_dir)

from unittest.mock import patch, MagicMock
from vllm.plugins.kivo_kv.hybrid_backend import HybridRAMMinIOBackend

@patch("vllm.plugins.kivo_kv.minio_store.Minio")
def test_hybrid_backend_put_get(mock_minio_class):
    # Mock MinIO client and its get_object().read()
    mock_minio = MagicMock()
    mock_minio.get_object.return_value.read.return_value = "bar".encode()
    mock_minio_class.return_value = mock_minio

    # Build config mock
    mock_config = MagicMock()
    mock_config.minio_url = "http://localhost:9000"
    mock_config.minio_key = "key"
    mock_config.minio_secret = "secret"
    mock_config.minio_bucket = "test-bucket"

    backend = HybridRAMMinIOBackend(mock_config)

    # Put value (should go into both RAM and MinIO)
    backend.put("sess1", "foo", "bar")

    # RAM cache hit
    assert backend.get("sess1", "foo") == "bar"
    assert "sess1" in backend.ram_backend._cache
    assert backend.ram_backend.get("sess1", "foo") == "bar"

    # Force RAM eviction and check fallback to MinIO
    backend.ram_backend._cache.clear()
    assert backend.get("sess1", "foo").decode() == "bar"  # Loaded from MinIO


@patch("vllm.plugins.kivo_kv.minio_store.Minio")
def test_hybrid_backend_evict(mock_minio_class):
    # Mock MinIO client and get_object().read()
    mock_minio = MagicMock()
    mock_minio.get_object.return_value.read.side_effect = lambda: b"v5"
    mock_minio_class.return_value = mock_minio

    # Build config mock
    mock_config = MagicMock()
    mock_config.minio_url = "localhost:9000"
    mock_config.minio_key = "key"
    mock_config.minio_secret = "secret"
    mock_config.minio_bucket = "test-bucket"

    backend = HybridRAMMinIOBackend(mock_config)

    # Fill RAM
    for i in range(110):
        backend.put(f"sess{i}", "k", f"v{i}")
    backend.evict()

    # RAM may have evicted sess5, but MinIO fallback should work
    backend.ram_backend._cache.clear()
    assert backend.get("sess5", "k").decode() == "v5"

