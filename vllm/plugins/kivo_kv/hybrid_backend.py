import threading
from collections import defaultdict

class HybridRAMMinIOBackend:
    def __init__(self, config):
        from vllm.plugins.kivo_kv.memory_backend import RAMBackend
        from vllm.plugins.kivo_kv.minio_store import MinIOBackend

        self.ram_backend = RAMBackend()
        self.minio_backend = MinIOBackend(config)

    def get(self, session_id: str, key: str):
        value = self.ram_backend.get(session_id, key)
        if value is None:
            value = self.minio_backend.get(session_id, key)
            if value is not None:
                # Optionally populate RAM cache
                self.ram_backend.put(session_id, key, value)
        return value

    def put(self, session_id: str, key: str, value):
        self.ram_backend.put(session_id, key, value)
        self.minio_backend.put(session_id, key, value)

    def evict(self, max_sessions: int = 100):
        self.ram_backend.evict(max_sessions)
        # Note: Do NOT evict from MinIO automatically
