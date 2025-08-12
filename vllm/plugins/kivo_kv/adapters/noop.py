from __future__ import annotations
from typing import Sequence
from ..types import KivoKV, KivoPage

class NoopAdapter(KivoKV):
    """
    Minimal implementation that never fetches anything and always reports ready.
    Safe for parity runs while wiring engine hooks in PR2.
    """

    def plan(self, req_id: str, step: int, window_W: int) -> Sequence[KivoPage]:
        # Noop: the engine’s GPU-local KV handles everything in PR1.
        return []

    def prefetch(self, pages: Sequence[KivoPage], deadline_ns: int) -> None:
        # Noop: no transfers performed.
        return None

    def ready(self, pages: Sequence[KivoPage]) -> bool:
        # Always ready so PR1 cannot stall or change behavior.
        return True

    def pin_hot(self, req_id: str, window_W: int) -> None:
        # Noop hint.
        return None
