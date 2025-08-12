import os

_truthy = {"1", "true", "yes", "on", "y", "t"}

def kivo_enabled() -> bool:
    """Return True if Kivo is enabled via environment variable."""
    val = os.environ.get("KIVO_ENABLED", "").strip().lower()
    return val in _truthy
