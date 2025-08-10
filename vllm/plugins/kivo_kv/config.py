import os

class KVConfig:
    def __init__(self):
        self.enabled = os.getenv("KV_PLUGIN", "").lower() == "kivo"
        self.backend = os.getenv("KV_BACKEND", "ram").lower()
        self.minio_url = os.getenv("MINIO_URL", "localhost:9000")
        self.minio_key = os.getenv("MINIO_KEY", "minioadmin")
        self.minio_secret = os.getenv("MINIO_SECRET", "minioadmin")
        self.minio_bucket = os.getenv("MINIO_BUCKET", "kivo-kv")

    def __repr__(self):
        return (
            f"KVConfig(enabled={self.enabled}, backend={self.backend}, "
            f"minio_url={self.minio_url}, bucket={self.minio_bucket})"
        )
