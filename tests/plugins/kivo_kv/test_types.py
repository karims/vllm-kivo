from vllm.plugins.kivo_kv import KivoPage, DType, KivoKV

def test_kivo_page_defaults():
    p = KivoPage(layer=2, head=1, start_tok=512, n_tok=128, dtype=DType.INT8)
    assert p.layer == 2 and p.head == 1
    assert p.start_tok == 512 and p.n_tok == 128
    assert p.dtype == DType.INT8
    assert p.scale is None and p.zero is None

def test_protocol_has_expected_methods():
    for name in ("plan", "prefetch", "ready", "pin_hot"):
        assert hasattr(KivoKV, name)
