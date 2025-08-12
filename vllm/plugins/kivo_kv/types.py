from __future__ import annotations

from typing import NamedTuple, Optional, Sequence, Protocol, runtime_checkable
import enum


class DType(str, enum.Enum):
    """Storage dtype for KV pages (on-disk/in-flight)."""
    FP16 = "fp16"
    BF16 = "bf16"
    FP8_E4M3 = "fp8_e4m3"
    FP8_E5M2 = "fp8_e5m2"
    INT8 = "int8"
    INT4 = "int4"


class KivoPage(NamedTuple):
    """
    A fixed-granularity KV page request/handle.

    layer/head: attention coordinates (0-indexed)
    start_tok:  first token index covered by this page (inclusive)
    n_tok:      number of tokens covered by this page
    dtype:      storage dtype for this page (e.g., INT8)
    scale/zero: optional quantization params (per-head or per-page)
    """
    layer: int
    head: int
    start_tok: int
    n_tok: int
    dtype: DType
    scale: Optional[float] = None
    zero: Optional[int] = None


@runtime_checkable
class KivoKV(Protocol):
    """
    Kivo plugin surface used by the engine. Implementations:
      - NoopAdapter (always ready; PR1)
      - NVMe/MinIO-backed adapters (PR3/PR6)
    """

    def plan(self, req_id: str, step: int, window_W: int) -> Sequence[KivoPage]:
        """
        Decide which pages must be resident on GPU for this request and step.
        Should only include hot-window pages (older ones are pruned).
        """
        ...

    def prefetch(self, pages: Sequence[KivoPage], deadline_ns: int) -> None:
        """
        Begin moving pages toward GPU (DRAM->GPU, NVMe->DRAM->GPU, etc.)
        Must be non-blocking; honor deadlines in Hydrator (PR4).
        """
        ...

    def ready(self, pages: Sequence[KivoPage]) -> bool:
        """
        True if all pages are resident on GPU (or otherwise satisfied).
        Engine may fall back to GPU-local path if False after a short wait.
        """
        ...

    def pin_hot(self, req_id: str, window_W: int) -> None:
        """
        Optional hint to keep hot-window pages warm for req_id.
        Implementations may treat this as a no-op.
        """
        ...
