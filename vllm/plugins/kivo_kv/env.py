import os

_truthy = {"1", "true", "yes", "on", "y", "t"}

def kivo_enabled() -> bool:
    val = os.environ.get("KIVO_ENABLED", "").strip().lower()
    return val in _truthy

def get_window_tokens(default: int = 4096) -> int:
    try:
        return int(os.environ.get("KIVO_WINDOW_TOKENS", default))
    except Exception:
        return default

def get_deadline_ns(default_ms: int = 2) -> int:
    # tiny per-layer deadline; engine uses monotonic_ns
    try:
        ms = int(os.environ.get("KIVO_DEADLINE_MS", default_ms))
    except Exception:
        ms = default_ms
    return ms * 1_000_000

def log_fallbacks() -> bool:
    val = os.environ.get("KIVO_LOG_FALLBACKS", "").strip().lower()
    return val in _truthy
