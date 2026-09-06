"""The routing decision: is this Read worth handing to a cheaper model?

Everything expensive about this idea lives here. Getting the policy wrong in
the permissive direction means the expensive model acts on a lossy summary of
a file where the exact bytes mattered. So the default posture is: shunt only
when the file is big, prose-or-code shaped, and not being read surgically.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from . import config


@dataclass
class Decision:
    shunt: bool
    reason: str
    path: Path | None = None
    content: str = ""
    tokens: int = 0


def _is_probably_text(sample: bytes) -> bool:
    if b"\x00" in sample:
        return False
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def decide(tool_name: str, tool_input: dict, cfg: dict, seen: set[str]) -> Decision:
    if tool_name != "Read":
        return Decision(False, f"tool is {tool_name}, not Read")

    raw_path = tool_input.get("file_path")
    if not raw_path:
        return Decision(False, "no file_path in tool_input")

    # A Read with offset/limit is a surgical read. The model already knows what
    # it wants and where. Summarizing it would answer a question it didn't ask.
    if tool_input.get("offset") is not None or tool_input.get("limit") is not None:
        return Decision(False, "targeted read (offset/limit given)")

    path = Path(raw_path)
    if not path.is_file():
        return Decision(False, "not a regular file")  # let Read produce the real error

    posix = path.as_posix()
    if any(frag in posix for frag in cfg["exclude_path_fragments"]):
        return Decision(False, "path is on the exclude list")

    if path.name in cfg["exact_content_names"] or path.suffix.lower() in cfg["exact_content_suffixes"]:
        return Decision(False, f"{path.suffix or path.name} needs exact content")

    # THE ESCAPE HATCH. If the agent comes back to a file we already digested,
    # it is telling us the digest was not enough. Never shunt the same file
    # twice in one session -- that is how an agent gets trapped in a lossy loop.
    if posix in seen:
        return Decision(False, "already shunted this session; passing through raw")

    try:
        with path.open("rb") as fh:
            head = fh.read(8192)
        if not _is_probably_text(head):
            return Decision(False, "binary file")
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return Decision(False, f"unreadable: {exc}")

    tokens = config.estimate_tokens(content)
    if tokens < cfg["min_tokens_to_shunt"]:
        return Decision(False, f"only ~{tokens} tokens (< {cfg['min_tokens_to_shunt']})")

    return Decision(True, f"~{tokens} tokens", path=path, content=content, tokens=tokens)


# --------------------------------------------------------------------------
# per-session memory of what we have already digested
# --------------------------------------------------------------------------

def _session_file(session_id: str) -> Path:
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")[:64] or "default"
    return config.state_dir() / f"session-{safe}.json"


def load_seen(session_id: str) -> set[str]:
    f = _session_file(session_id)
    if not f.is_file():
        return set()
    try:
        return set(json.loads(f.read_text()))
    except (OSError, json.JSONDecodeError):
        return set()


def mark_seen(session_id: str, posix_path: str) -> None:
    seen = load_seen(session_id)
    seen.add(posix_path)
    try:
        _session_file(session_id).write_text(json.dumps(sorted(seen)))
    except OSError:
        pass
