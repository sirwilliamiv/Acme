#!/usr/bin/env python3
"""End-to-end demo: feed the hook the same JSON Claude Code would, and watch.

    python3 demo/run_demo.py            # offline extractive stub, no key needed
    SHUNT_PROVIDER=anthropic python3 demo/run_demo.py   # real Haiku 4.5 calls
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("CLAUDE_PROJECT_DIR", str(ROOT))

from shunt import config, ledger  # noqa: E402

FIXTURES = ROOT / "demo" / "fixtures"
HOOK = ROOT / "shunt" / "hook.py"


def make_fixtures() -> None:
    """A big module (worth shunting), a lockfile (must not be), a stub (too small)."""
    FIXTURES.mkdir(parents=True, exist_ok=True)

    big = ['"""Order pipeline. Generated fixture: large enough to be worth shunting."""',
           "import dataclasses", "import logging", "from decimal import Decimal", "",
           "TAX_RATE = Decimal('0.0825')  # do not change without finance sign-off", ""]
    for i in range(120):
        big += [
            f"def handle_step_{i:03d}(order, ctx):",
            f'    """Step {i} of the pipeline."""',
            f"    logging.debug('step {i}')",
            "    total = Decimal(0)",
            "    for line in order.lines:",
            "        total += line.price * line.qty",
            f"    ctx['step_{i}'] = total * (1 + TAX_RATE)",
            "    return ctx",
            "",
        ]
    big.append("# TODO: retire handle_step_007, superseded by the batch path")
    (FIXTURES / "pipeline.py").write_text("\n".join(big))

    (FIXTURES / "package-lock.json").write_text(
        json.dumps({"name": "demo", "lockfileVersion": 3,
                    "packages": {f"node_modules/pkg{i}": {"version": f"1.{i}.0"}
                                 for i in range(400)}}, indent=2))

    (FIXTURES / "tiny.py").write_text("def add(a, b):\n    return a + b\n")


def call_hook(tool_input: dict, session: str = "demo-session") -> dict | None:
    payload = {"session_id": session, "hook_event_name": "PreToolUse",
               "tool_name": "Read", "tool_input": tool_input}
    proc = subprocess.run(
        [sys.executable, str(HOOK)], input=json.dumps(payload),
        capture_output=True, text=True, env={**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT)})
    if proc.stderr.strip():
        print("   stderr:", proc.stderr.strip())
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def show(title: str, tool_input: dict, session: str = "demo-session") -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")
    print(f"Claude Code is about to call: Read({json.dumps(tool_input)})")
    out = call_hook(tool_input, session)
    if out is None:
        print("-> hook stayed silent. The real Read proceeds, file enters context.")
        return
    reason = out["hookSpecificOutput"]["permissionDecisionReason"]
    print(f"-> hook returned permissionDecision="
          f"{out['hookSpecificOutput']['permissionDecision']!r}")
    print("-> what the expensive model actually receives:\n")
    print(textwrap.indent(reason[:1400], "   "))


def main() -> None:
    shutil.rmtree(config.state_dir(), ignore_errors=True)
    make_fixtures()
    big = str(FIXTURES / "pipeline.py")

    show("1. Big source file -> intercepted and digested", {"file_path": big})
    show("2. Same file again -> ESCAPE HATCH, passed through verbatim",
         {"file_path": big})
    show("3. Targeted read (offset/limit) -> never intercepted",
         {"file_path": big, "offset": 40, "limit": 20}, session="other")
    show("4. Lockfile -> exact content required, never intercepted",
         {"file_path": str(FIXTURES / "package-lock.json")}, session="other")
    show("5. Tiny file -> below threshold, not worth the round trip",
         {"file_path": str(FIXTURES / "tiny.py")}, session="other")
    show("6. Big file, fresh session -> CACHE HIT (content unchanged)",
         {"file_path": big}, session="third")

    print(f"\n{'=' * 78}\n{ledger.report()}")


if __name__ == "__main__":
    main()
