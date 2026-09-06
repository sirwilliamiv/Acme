"""Savings ledger.

Every shunt appends one JSON line. `python -m shunt.report` turns them into a
table. If you cannot show the number, you do not have an optimization -- you
have a belief.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from . import config

LEDGER = "ledger.jsonl"


def _path() -> Path:
    return config.state_dir() / LEDGER


def record(**event) -> None:
    event.setdefault("ts", time.time())
    try:
        with _path().open("a") as fh:
            fh.write(json.dumps(event) + "\n")
    except OSError:
        pass


def read() -> list[dict]:
    f = _path()
    if not f.is_file():
        return []
    out = []
    for line in f.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def savings(event: dict) -> dict:
    """What one shunt cost, versus letting the driver model read the file.

    baseline: driver ingests the whole file.
    actual:   cheap model ingests the file and emits a digest; driver ingests
              the digest. A cache hit skips the cheap call entirely.
    """
    driver = config.DRIVER_MODEL
    baseline_tokens = event["file_tokens"]
    digest_tokens = event["digest_tokens"]

    baseline_cost = config.cost(driver, baseline_tokens, 0)
    cheap_cost = 0.0 if event.get("cached") else config.cost(
        event["worker_model"], event["worker_in"], event["worker_out"])
    actual_cost = config.cost(driver, digest_tokens, 0) + cheap_cost

    return {
        "baseline_tokens": baseline_tokens,
        "actual_tokens": digest_tokens,
        "tokens_saved": baseline_tokens - digest_tokens,
        "baseline_cost": baseline_cost,
        "actual_cost": actual_cost,
        "cost_saved": baseline_cost - actual_cost,
    }


def report() -> str:
    events = read()
    if not events:
        return "No shunts recorded yet. Run `python demo/run_demo.py` first."

    rows, tot_base_t, tot_act_t, tot_base_c, tot_act_c, hits = [], 0, 0, 0.0, 0.0, 0
    for e in events:
        s = savings(e)
        tot_base_t += s["baseline_tokens"]
        tot_act_t += s["actual_tokens"]
        tot_base_c += s["baseline_cost"]
        tot_act_c += s["actual_cost"]
        hits += 1 if e.get("cached") else 0
        rows.append((
            Path(e["path"]).name[:30],
            e["worker_model"] if not e.get("cached") else "cache",
            s["baseline_tokens"],
            s["actual_tokens"],
            f"{100 * s['tokens_saved'] / max(1, s['baseline_tokens']):.0f}%",
            f"${s['cost_saved']:.5f}",
        ))

    w = "{:<30} {:>16} {:>10} {:>10} {:>7} {:>10}"
    lines = [
        f"shunt ledger  --  {len(events)} reads intercepted, {hits} served from cache",
        "",
        w.format("file", "worker", "baseline", "actual", "saved", "$ saved"),
        "-" * 88,
    ]
    lines += [w.format(*r) for r in rows]
    lines += [
        "-" * 88,
        w.format("TOTAL", "", tot_base_t, tot_act_t,
                 f"{100 * (tot_base_t - tot_act_t) / max(1, tot_base_t):.0f}%",
                 f"${tot_base_c - tot_act_c:.5f}"),
        "",
        f"Driver model: {config.DRIVER_MODEL} "
        f"(${config.PRICES[config.DRIVER_MODEL][0]:.2f}/MTok in)",
        f"Context ingested by driver: {tot_base_t:,} -> {tot_act_t:,} tokens",
        "",
        "Note: this counts each file once. In a real agent loop the context is",
        "resent on every subsequent turn, so a token removed from context early",
        "is saved once per remaining turn. That is where a 90% headline comes",
        "from -- and why you should measure your own loop, not trust this table.",
    ]
    return "\n".join(lines)
