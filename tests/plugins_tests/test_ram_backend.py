from vllm.plugins.kivo_kv.memory_backend import RAMBackend

def test_ram_backend_put_and_get():
    backend = RAMBackend()

    backend.put("s1", "k1", "v1")
    backend.put("s1", "k2", "v2")
    backend.put("s2", "k1", "v3")

    assert backend.get("s1", "k1") == "v1"
    assert backend.get("s1", "k2") == "v2"
    assert backend.get("s2", "k1") == "v3"
    assert backend.get("s2", "k2") is None

def test_ram_backend_evict():
    backend = RAMBackend()

    # Insert 105 sessions (exceeds default max_sessions=100)
    for i in range(105):
        sid = f"sess{i}"
        backend.put(sid, "k", f"v{i}")

    # Trigger eviction
    backend.evict(max_sessions=100)

    remaining_sessions = list(backend._cache.keys())
    assert len(remaining_sessions) == 100
    # Oldest ones (sess0, sess1, ...) should be gone
    assert "sess0" not in remaining_sessions
    assert "sess4" not in remaining_sessions
    assert "sess104" in remaining_sessions
