import logging
import threading
from collections import defaultdict
import time

logger = logging.getLogger("KivoKV")

class RAMBackend:
    def __init__(self):
        self._cache = defaultdict(dict)
        self._lock = threading.Lock()

    def get(self, session_id: str, key: str):
        with self._lock:
            value = self._cache[session_id].get(key, None)
            logger.debug(f"[KivoKV] GET session={session_id} key={key} -> {value is not None}")
            return value

    def put(self, session_id: str, key: str, value):
        with self._lock:
            self._cache[session_id][key] = value
            logger.debug(f"[KivoKV] PUT session={session_id} key={key}")

    def evict(self, max_sessions: int = 100):
        with self._lock:
            current_sessions = len(self._cache)
            if current_sessions > max_sessions:
                to_remove = list(self._cache.keys())[:current_sessions - max_sessions]
                for sid in to_remove:
                    del self._cache[sid]
                    logger.warning(f"[KivoKV] EVICTED session={sid}")

