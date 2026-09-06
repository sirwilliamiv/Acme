#!/usr/bin/env python3
"""Claude Code PreToolUse hook.

Wire-up (.claude/settings.json):

    "hooks": {
      "PreToolUse": [{
        "matcher": "Read",
        "hooks": [{"type": "command",
                   "command": "python3 \"$CLAUDE_PROJECT_DIR\"/shunt/hook.py"}]
      }]
    }

Claude Code sends the pending tool call on stdin:

    {"session_id": "...", "hook_event_name": "PreToolUse",
     "tool_name": "Read", "tool_input": {"file_path": "/abs/path"}}

We answer on stdout. `permissionDecision: "deny"` stops the Read, and
`permissionDecisionReason` is shown to the model -- so the reason field is the
channel we smuggle the digest through. The expensive model never sees the file.

Failure policy: any error at all -> exit 0, print nothing -> Claude Code runs
the Read normally. A token optimizer must never be able to break the editor.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shunt import cache, config, ledger, modes, policy, providers  # noqa: E402

QUESTION = (
    "Summarize this file for an agent that must modify code in this repository."
)


def allow() -> None:
    """Say nothing; Claude Code proceeds with the real Read."""
    sys.exit(0)


def deny_with(digest: str) -> None:
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": digest,
        }
    }, sys.stdout)
    sys.exit(0)


def build_message(path: Path, decision, result, cached: bool, mode_name: str) -> str:
    saved = decision.tokens - config.estimate_tokens(result.text)
    return (
        f"[shunt] This file was read for you by `{mode_name}` "
        f"({'cache' if cached else result.model}) instead of being loaded into "
        f"your context: ~{decision.tokens} tokens -> ~{config.estimate_tokens(result.text)} "
        f"tokens (~{saved} saved).\n\n"
        f"DIGEST OF {path}\n"
        f"{'=' * 60}\n"
        f"{result.text}\n"
        f"{'=' * 60}\n\n"
        f"If you need the exact contents, read it again -- the second read of a "
        f"file in a session is always passed through verbatim. For a specific "
        f"region, use Read with offset/limit, which is never intercepted."
    )


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        allow()

    cfg = config.load()
    session_id = payload.get("session_id", "default")
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}

    seen = policy.load_seen(session_id)
    decision = policy.decide(tool_name, tool_input, cfg, seen)
    if not decision.shunt:
        allow()

    path = decision.path
    mode = modes.load(cfg["mode"])

    hit = cache.get(decision.content, mode.name, QUESTION)
    if hit:
        result = providers.Result(hit["text"], hit["model"], hit["in"], hit["out"])
        cached = True
    else:
        result = providers.run_chunked(
            mode,
            path=str(path),
            content=decision.content,
            question=QUESTION,
            provider=cfg["provider"],
            chunk_tokens=cfg["chunk_tokens"],
        )
        cached = False
        cache.put(decision.content, mode.name, QUESTION, {
            "text": result.text, "model": result.model,
            "in": result.in_tokens, "out": result.out_tokens,
        })

    policy.mark_seen(session_id, path.as_posix())
    ledger.record(
        path=str(path),
        mode=mode.name,
        worker_model=result.model,
        worker_in=result.in_tokens,
        worker_out=result.out_tokens,
        file_tokens=decision.tokens,
        digest_tokens=config.estimate_tokens(result.text),
        cached=cached,
        session_id=session_id,
    )
    deny_with(build_message(path, decision, result, cached, mode.name))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - deliberately total
        print(f"shunt hook error (falling back to a normal Read): {exc}", file=sys.stderr)
        sys.exit(0)
