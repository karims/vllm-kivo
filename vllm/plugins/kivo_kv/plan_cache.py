from __future__ import annotations
from typing import Dict, List, Sequence, Tuple
from threading import RLock
from .types import KivoPage

class _PlanCache:
    """
    Ephemeral plan storage for the *current decode step*.
    Engine fills it during batch prefetch; attention layer reads per-layer.
    """
    def __init__(self) -> None:
        self._lock = RLock()
        self._step: int | None = None
        self._by_layer: Dict[int, List[KivoPage]] = {}

    def set_step(self, step: int) -> None:
        with self._lock:
            self._step = step
            self._by_layer.clear()

    def add_pages(self, pages: Sequence[KivoPage]) -> None:
        if not pages:
            return
        with self._lock:
            for p in pages:
                self._by_layer.setdefault(p.layer, []).append(p)

    def get_for_layer(self, layer: int) -> List[KivoPage]:
        with self._lock:
            return list(self._by_layer.get(layer, ()))

    def current_step(self) -> int | None:
        with self._lock:
            return self._step

# Singleton instance imported by engine & attention layer
plan_cache = _PlanCache()
