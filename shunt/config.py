"""Configuration and price table.

Prices are USD per 1M tokens, first-party Anthropic API rates.
Kept here so the ledger can price a shunt in dollars, not just tokens.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

PRICES = {
    # model id           input $/MTok, output $/MTok
    "claude-opus-5":    (5.00, 25.00),
    "claude-sonnet-5":  (2.00, 10.00),
    "claude-haiku-4-5": (1.00,  5.00),
    "stub":             (0.00,  0.00),
}

# What the expensive model would have paid to read the file itself. Every
# saving in the ledger is measured against this.
DRIVER_MODEL = "claude-opus-5"

DEFAULTS = {
    # Files whose estimated token count is below this are cheaper to read
    # directly than to round-trip through another model.
    "min_tokens_to_shunt": 2000,

    # Refuse to send absurdly large files to the cheap model in one piece.
    # Above this we chunk (see providers.summarize_large).
    "chunk_tokens": 60000,

    # Extensions where an approximate reading is worse than useless: the
    # agent needs the exact bytes (a version string, a key, a schema).
    "exact_content_suffixes": [
        ".json", ".lock", ".toml", ".ini", ".cfg", ".env",
        ".csv", ".tsv", ".sql", ".pem", ".key", ".patch", ".diff",
    ],

    # Same idea, by filename.
    "exact_content_names": [
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Cargo.lock",
        "poetry.lock", "go.sum", "requirements.txt", ".env",
    ],

    # Never shunt anything under these path fragments.
    "exclude_path_fragments": [".git/", "node_modules/", ".shunt/"],

    "mode": "bulk-reader",
    "provider": "auto",          # auto | anthropic | stub
    "state_dir": ".shunt",
}


def project_root() -> Path:
    """Claude Code exports CLAUDE_PROJECT_DIR for hooks; fall back to cwd."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def load() -> dict:
    """DEFAULTS, overlaid with shunt.config.json if the project has one."""
    cfg = dict(DEFAULTS)
    override = project_root() / "shunt.config.json"
    if override.is_file():
        try:
            cfg.update(json.loads(override.read_text()))
        except (OSError, json.JSONDecodeError):
            pass  # a broken config must never break the user's Read tool
    if os.environ.get("SHUNT_PROVIDER"):
        cfg["provider"] = os.environ["SHUNT_PROVIDER"]
    if os.environ.get("SHUNT_MIN_TOKENS"):
        cfg["min_tokens_to_shunt"] = int(os.environ["SHUNT_MIN_TOKENS"])
    return cfg


def state_dir() -> Path:
    d = project_root() / load()["state_dir"]
    d.mkdir(parents=True, exist_ok=True)
    return d


def estimate_tokens(text: str) -> int:
    """~4 chars per token. Cheap, offline, and good enough for a routing decision.

    For billing-grade numbers use client.messages.count_tokens instead; this
    runs on every Read, so it has to cost nothing.
    """
    return max(1, len(text) // 4)


def cost(model: str, in_tokens: int, out_tokens: int) -> float:
    inp, outp = PRICES.get(model, (0.0, 0.0))
    return (in_tokens / 1_000_000) * inp + (out_tokens / 1_000_000) * outp
