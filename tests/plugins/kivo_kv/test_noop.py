from vllm.plugins.kivo_kv.adapters import NoopAdapter

def test_noop_adapter_behaves():
    a = NoopAdapter()
    pages = a.plan(req_id="r1", step=0, window_W=4096)
    assert isinstance(pages, (list, tuple)) and len(pages) == 0
    assert a.ready(pages) is True
    a.prefetch(pages, deadline_ns=0)  # no exception
    a.pin_hot("r1", 4096)            # no exception
