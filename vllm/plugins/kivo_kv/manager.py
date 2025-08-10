from vllm.plugins.kivo_kv.config import KVConfig

class KivoKVCacheManager:
    def __init__(self):
        self.config = KVConfig()
        if not self.config.enabled:
            raise RuntimeError("Kivo KV plugin is not enabled.")

        self.backend = self._load_backend()

    def _load_backend(self):
        if self.config.backend == "ram":
            from vllm.plugins.kivo_kv.memory_backend import RAMBackend
            return RAMBackend()
        elif self.config.backend == "minio":
            from vllm.plugins.kivo_kv.minio_store import MinIOBackend
            return MinIOBackend(self.config)
        elif self.config.backend == "hybrid":
            from vllm.plugins.kivo_kv.memory_backend import HybridRAMMinIOBackend
            return HybridRAMMinIOBackend(self.config)
        else:
            raise ValueError(f"Unknown backend: {self.config.backend}")

    def get(self, session_id, key):
        return self.backend.get(session_id, key)

    def put(self, session_id, key, value):
        self.backend.put(session_id, key, value)

    def evict(self):
        if hasattr(self.backend, "evict"):
            self.backend.evict()
