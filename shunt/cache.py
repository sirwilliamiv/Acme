"""Content-addressed digest cache.

Agents re-read the same unchanged files constantly. A digest keyed on
(file content, mode, question) makes the second read free -- in tokens,
in dollars, and in latency. In practice this saves more than the model
swap does.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import config


def _key(content: str, mode_name: str, question: str) -> str:
    h = hashlib.sha256()
    h.update(content.encode("utf-8", "replace"))
    h.update(b"\x00")
    h.update(mode_name.encode())
    h.update(b"\x00")
    h.update(question.encode())
    return h.hexdigest()[:32]


def _path(key: str) -> Path:
    d = config.state_dir() / "cache"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{key}.json"


def get(content: str, mode_name: str, question: str) -> dict | None:
    f = _path(_key(content, mode_name, question))
    if not f.is_file():
        return None
    try:
        return json.loads(f.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def put(content: str, mode_name: str, question: str, payload: dict) -> None:
    try:
        _path(_key(content, mode_name, question)).write_text(json.dumps(payload))
    except OSError:
        pass
