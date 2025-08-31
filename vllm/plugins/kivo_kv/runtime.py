from __future__ import annotations
from typing import Optional
from threading import RLock

from .types import KivoKV

# Global adapter + counters; engine sets, attention reads
__adapter: Optional[KivoKV] = None
__lock = RLock()
__fallbacks_total: int = 0

def set_adapter(adapter: KivoKV) -> None:
    global __adapter
    with __lock:
        __adapter = adapter

def get_adapter() -> Optional[KivoKV]:
    with __lock:
        return __adapter

def incr_fallbacks(n: int = 1) -> None:
    global __fallbacks_total
    with __lock:
        __fallbacks_total += n

def get_fallbacks_total() -> int:
    with __lock:
        return __fallbacks_total
