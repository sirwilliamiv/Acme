"""Tests for the routing policy and the hook contract.

The policy tests matter most: every false positive here means the expensive
model acts on a lossy summary of a file where the bytes mattered.

    python3 -m pytest tests/ -q      # or: python3 tests/test_shunt.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402

from shunt import cache, config, ledger, modes, policy, providers  # noqa: E402


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setenv("SHUNT_PROVIDER", "stub")
    return tmp_path


@pytest.fixture
def cfg():
    return config.load()


def big_file(d: Path, name: str = "big.py", tokens: int = 5000) -> Path:
    p = d / name
    p.write_text("def f():\n    return 1\n" * (tokens // 5))
    return p


# --------------------------------------------------------------------------
# policy: when we DO shunt
# --------------------------------------------------------------------------

def test_large_source_file_is_shunted(project, cfg):
    d = policy.decide("Read", {"file_path": str(big_file(project))}, cfg, set())
    assert d.shunt
    assert d.tokens >= cfg["min_tokens_to_shunt"]


# --------------------------------------------------------------------------
# policy: when we MUST NOT shunt
# --------------------------------------------------------------------------

def test_small_file_passes_through(project, cfg):
    p = project / "tiny.py"
    p.write_text("x = 1\n")
    assert not policy.decide("Read", {"file_path": str(p)}, cfg, set()).shunt


def test_targeted_read_passes_through(project, cfg):
    p = big_file(project)
    for extra in ({"offset": 10}, {"limit": 5}, {"offset": 10, "limit": 5}):
        d = policy.decide("Read", {"file_path": str(p), **extra}, cfg, set())
        assert not d.shunt, f"offset/limit read was shunted: {extra}"


@pytest.mark.parametrize("name", [
    "package-lock.json", "Cargo.lock", "config.toml", ".env",
    "data.csv", "schema.sql", "requirements.txt", "server.key",
])
def test_exact_content_files_pass_through(project, cfg, name):
    p = project / name
    p.write_text("k = v\n" * 4000)
    assert not policy.decide("Read", {"file_path": str(p)}, cfg, set()).shunt


def test_binary_file_passes_through(project, cfg):
    p = project / "blob.bin"
    p.write_bytes(b"\x00\x01\x02" * 8000)
    assert not policy.decide("Read", {"file_path": str(p)}, cfg, set()).shunt


def test_missing_file_passes_through(project, cfg):
    d = policy.decide("Read", {"file_path": str(project / "nope.py")}, cfg, set())
    assert not d.shunt


def test_non_read_tool_passes_through(project, cfg):
    p = big_file(project)
    assert not policy.decide("Grep", {"file_path": str(p)}, cfg, set()).shunt


def test_excluded_paths_pass_through(project, cfg):
    nm = project / "node_modules" / "pkg"
    nm.mkdir(parents=True)
    assert not policy.decide("Read", {"file_path": str(big_file(nm))}, cfg, set()).shunt


# --------------------------------------------------------------------------
# the escape hatch
# --------------------------------------------------------------------------

def test_second_read_of_same_file_is_never_shunted(project, cfg):
    p = big_file(project)
    assert policy.decide("Read", {"file_path": str(p)}, cfg, set()).shunt
    policy.mark_seen("s1", p.as_posix())
    seen = policy.load_seen("s1")
    assert not policy.decide("Read", {"file_path": str(p)}, cfg, seen).shunt


def test_seen_set_is_per_session(project):
    policy.mark_seen("s1", "/a/b.py")
    assert "/a/b.py" in policy.load_seen("s1")
    assert "/a/b.py" not in policy.load_seen("s2")


# --------------------------------------------------------------------------
# modes, cache, ledger
# --------------------------------------------------------------------------

def test_every_bundled_mode_loads(project):
    assert modes.available()
    for name in modes.available():
        m = modes.load(name)
        assert m.model in config.PRICES
        assert "{content}" in m.user_template


def test_cache_roundtrip_is_content_addressed(project):
    payload = {"text": "digest", "model": "stub", "in": 10, "out": 5}
    cache.put("aaa", "bulk-reader", "q", payload)
    assert cache.get("aaa", "bulk-reader", "q") == payload
    assert cache.get("bbb", "bulk-reader", "q") is None      # content changed
    assert cache.get("aaa", "code-writer", "q") is None      # mode changed
    assert cache.get("aaa", "bulk-reader", "q2") is None     # question changed


def test_savings_math(project):
    s = ledger.savings({
        "file_tokens": 10000, "digest_tokens": 500,
        "worker_model": "claude-haiku-4-5", "worker_in": 10000, "worker_out": 500,
        "cached": False,
    })
    assert s["tokens_saved"] == 9500
    # opus in: 10000 * $5/M = $0.05  vs  opus 500 * $5/M + haiku(10000 in, 500 out)
    assert s["baseline_cost"] == pytest.approx(0.05)
    assert s["actual_cost"] == pytest.approx(0.0025 + 0.0100 + 0.0025)
    assert s["cost_saved"] > 0


def test_cached_shunt_costs_nothing_extra(project):
    e = {"file_tokens": 10000, "digest_tokens": 500,
         "worker_model": "claude-haiku-4-5", "worker_in": 10000, "worker_out": 500}
    assert (ledger.savings({**e, "cached": True})["actual_cost"]
            < ledger.savings({**e, "cached": False})["actual_cost"])


def test_stub_provider_extracts_structure(project):
    mode = modes.load("bulk-reader")
    src = "import os\n\n\ndef alpha(x):\n    return x\n\n\nclass Beta:\n    pass\n# TODO: fix\n"
    r = providers.run(mode, mode.render(path="m.py", content=src, question="?"), "stub")
    assert "import os" in r.text
    assert "def alpha" in r.text and "class Beta" in r.text
    assert "TODO" in r.text
    assert r.out_tokens < config.estimate_tokens(src) + 200


def test_chunking_splits_oversized_files(project):
    mode = modes.load("bulk-reader")
    r = providers.run_chunked(mode, path="huge.py", content="def f():\n    pass\n" * 5000,
                              question="?", provider="stub", chunk_tokens=1000)
    assert "part 1/" in r.text and "part 2/" in r.text


# --------------------------------------------------------------------------
# hook process contract
# --------------------------------------------------------------------------

def run_hook(payload: dict, project: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "shunt" / "hook.py")],
        input=json.dumps(payload), capture_output=True, text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project), "SHUNT_PROVIDER": "stub"})


def test_hook_denies_and_returns_digest(project):
    p = big_file(project)
    proc = run_hook({"session_id": "t", "hook_event_name": "PreToolUse",
                     "tool_name": "Read", "tool_input": {"file_path": str(p)}}, project)
    assert proc.returncode == 0
    out = json.loads(proc.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "PreToolUse"
    assert out["permissionDecision"] == "deny"
    assert "DIGEST OF" in out["permissionDecisionReason"]


def test_hook_is_silent_when_not_shunting(project):
    p = project / "tiny.py"
    p.write_text("x = 1\n")
    proc = run_hook({"session_id": "t", "tool_name": "Read",
                     "tool_input": {"file_path": str(p)}}, project)
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""


def test_hook_never_blocks_on_malformed_input(project):
    for bad in ("", "not json", "{}", '{"tool_name": "Read"}'):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "shunt" / "hook.py")], input=bad,
            capture_output=True, text=True,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(project)})
        assert proc.returncode == 0, f"hook failed on input {bad!r}"
        assert proc.stdout.strip() == "", f"hook denied on input {bad!r}"


def test_hook_records_to_ledger(project):
    p = big_file(project)
    run_hook({"session_id": "t", "tool_name": "Read",
              "tool_input": {"file_path": str(p)}}, project)
    events = ledger.read()
    assert len(events) == 1
    assert events[0]["file_tokens"] > events[0]["digest_tokens"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
