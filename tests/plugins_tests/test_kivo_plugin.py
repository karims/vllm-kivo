# tests/plugins_tests/test_kivo_plugin.py

import os
import sys

import pytest
from vllm.engine.llm_engine import LLMEngine
from vllm.engine.arg_utils import EngineArgs
from vllm.plugins.kivo_kv.manager import KivoKVCacheManager


@pytest.fixture
def dummy_engine_args(tmp_path):
    return EngineArgs(
        model="facebook/opt-125m",  # Use any small model
        tokenizer="facebook/opt-125m",
        enforce_eager=True,
        dtype="float32",
        disable_log_stats=True,
        seed=42,
        max_num_batched_tokens=512,
        max_model_len=512,
        swap_space=2,
        download_dir=str(tmp_path),
        disable_custom_all_reduce=True,
        trust_remote_code=True,
        block_size=16,
        tokenizer_mode="slow",
    )


import pytest
from vllm.engine.llm_engine import load_kv_plugin_if_any

def test_kivo_plugin_direct(monkeypatch):
    monkeypatch.setenv("KV_PLUGIN", "kivo")

    plugin = load_kv_plugin_if_any()

    assert plugin is not None, "KivoKVCacheManager plugin was not loaded"
    assert plugin.get("__init__", "test") == "value"

def test_kivo_plugin_instantiates(monkeypatch):
    monkeypatch.setenv("KV_PLUGIN", "kivo")
    monkeypatch.setenv("KV_BACKEND", "ram")

    kv = KivoKVCacheManager()
    kv.put("s1", "k", "v")
    assert kv.get("s1", "k") == "v"

@pytest.mark.skipif(sys.platform == "darwin", reason="Engine tests fail on macOS due to missing C++ ops")
def test_kivo_plugin_enabled(monkeypatch):
    monkeypatch.setenv("KV_PLUGIN", "kivo")
    monkeypatch.setenv("KV_BACKEND", "ram")

    from vllm.engine.llm_engine import LLMEngine, EngineArgs

    engine_args = EngineArgs(
        model="facebook/opt-125m",
        dtype="float32",
        disable_log_stats=True,
    )
    engine = LLMEngine.from_engine_args(engine_args)

    assert engine.kivo_kv is not None
    engine.kivo_kv.put("test_session", "foo", "bar")
    assert engine.kivo_kv.get("test_session", "foo") == "bar"
