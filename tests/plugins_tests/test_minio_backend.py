import io
import pytest
from unittest.mock import MagicMock, patch
from vllm.plugins.kivo_kv.minio_store import MinIOBackend
from vllm.plugins.kivo_kv.config import KVConfig

@pytest.fixture
def mock_minio_client():
    with patch("vllm.plugins.kivo_kv.minio_store.Minio") as mock:
        yield mock

@pytest.fixture
def minio_backend(mock_minio_client):
    config = KVConfig()
    config.backend = "minio"
    config.minio_url = "localhost:9000"
    config.minio_key = "testkey"
    config.minio_secret = "testsecret"
    config.minio_bucket = "kivokv"
    return MinIOBackend(config)

def test_put_calls_minio_put_object(minio_backend, mock_minio_client):
    backend = minio_backend
    backend.client = MagicMock()
    backend.put("sess1", "foo", b"bar")
    backend.client.put_object.assert_called_once()
    args, kwargs = backend.client.put_object.call_args
    assert "sess1/foo" in args

def test_get_reads_data(minio_backend):
    backend = minio_backend
    mock_response = MagicMock()
    mock_response.read.return_value = b"mydata"
    backend.client = MagicMock()
    backend.client.get_object.return_value = mock_response

    result = backend.get("sess1", "foo")
    assert result == b"mydata"
