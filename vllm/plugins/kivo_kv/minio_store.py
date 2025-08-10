import io
import logging
from minio import Minio
from minio.error import S3Error
from vllm.plugins.kivo_kv.config import KVConfig

logger = logging.getLogger("kivo_kv")
logger.setLevel(logging.DEBUG)  # or INFO in production

class MinIOBackend:
    def __init__(self, config: KVConfig):
        self.client = Minio(
            config.minio_url,
            access_key=config.minio_key,
            secret_key=config.minio_secret,
            secure=False,
        )
        self.bucket = config.minio_bucket
        self._ensure_bucket()

        logger.info(f"[MinIOBackend] Initialized with bucket '{self.bucket}' at {config.minio_url}")

    def _ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
            logger.info(f"[MinIOBackend] Created bucket: {self.bucket}")
        else:
            logger.debug(f"[MinIOBackend] Bucket '{self.bucket}' already exists.")

    def _object_name(self, session_id, key):
        return f"{session_id}/{key}"

    def put(self, session_id: str, key: str, value: bytes):
        object_name = self._object_name(session_id, key)
        data = io.BytesIO(value if isinstance(value, bytes) else value.encode("utf-8"))
        data_len = data.getbuffer().nbytes
        self.client.put_object(self.bucket, object_name, data, length=data_len)
        logger.debug(f"[MinIOBackend] Stored object: {object_name} ({data_len} bytes)")

    def get(self, session_id: str, key: str):
        object_name = self._object_name(session_id, key)
        try:
            response = self.client.get_object(self.bucket, object_name)
            value = response.read()
            logger.debug(f"[MinIOBackend] Fetched object: {object_name} ({len(value)} bytes)")
            return value
        except S3Error as e:
            if e.code == "NoSuchKey":
                logger.debug(f"[MinIOBackend] Object not found: {object_name}")
                return None
            logger.warning(f"[MinIOBackend] Failed to fetch {object_name}: {e}")
            raise

    def evict(self):
        # Optional: implement prefix-based deletion later
        logger.info("[MinIOBackend] Eviction logic not implemented yet.")
