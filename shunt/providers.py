"""Providers that execute a Mode.

Two of them:
  anthropic - the real thing, via the official SDK.
  stub      - a deterministic offline extractor so the demo and the tests run
              with no API key and no network. It is a real (crude) summarizer,
              not a mock: it exercises the same code path end to end.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from . import config
from .modes import Mode


@dataclass
class Result:
    text: str
    model: str
    in_tokens: int
    out_tokens: int

    @property
    def cost(self) -> float:
        return config.cost(self.model, self.in_tokens, self.out_tokens)


# --------------------------------------------------------------------------
# real provider
# --------------------------------------------------------------------------

def _run_anthropic(mode: Mode, prompt: str) -> Result:
    import anthropic  # imported lazily: the stub path must not need the SDK

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=mode.model,
        max_tokens=mode.max_tokens,
        temperature=mode.temperature,
        system=mode.system,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    return Result(
        text=text,
        model=mode.model,
        in_tokens=resp.usage.input_tokens,
        out_tokens=resp.usage.output_tokens,
    )


# --------------------------------------------------------------------------
# stub provider
# --------------------------------------------------------------------------

_SIGNATURE_PATTERNS = [
    re.compile(r"^\s*(?:async\s+)?def\s+\w+\s*\("),           # python
    re.compile(r"^\s*class\s+\w+"),                            # python / ts
    re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+"), # js / ts
    re.compile(r"^\s*export\s+(?:const|let|type|interface)\s+"),
    re.compile(r"^\s*(?:pub\s+)?fn\s+\w+"),                    # rust
    re.compile(r"^\s*func\s+"),                                # go
    re.compile(r"^\s*(?:public|private|protected)\s+.*\("),    # java / c#
]
_IMPORT_PATTERN = re.compile(r"^\s*(?:import|from|require|use|#include)\b")
_MARKER_PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX|WARNING|DEPRECATED)\b")


def _run_stub(mode: Mode, prompt: str) -> Result:
    """Extractive digest: keep the lines that carry structure, drop the bodies."""
    body = prompt
    if "<file>" in prompt:
        body = prompt.split("<file>", 1)[1].rsplit("</file>", 1)[0]
    lines = body.splitlines()

    imports, signatures, markers = [], [], []
    for i, line in enumerate(lines, 1):
        if len(line) > 400:
            continue
        if _IMPORT_PATTERN.match(line):
            imports.append(line.strip())
        elif any(p.match(line) for p in _SIGNATURE_PATTERNS):
            signatures.append(f"L{i}: {line.strip()}")
        elif _MARKER_PATTERN.search(line):
            markers.append(f"L{i}: {line.strip()}")

    out = [f"[stub digest] {len(lines)} lines."]
    if imports:
        out.append("DEPENDS ON: " + ", ".join(dict.fromkeys(imports))[:600])
    if signatures:
        out.append("SYMBOLS:")
        out.extend("  " + s for s in signatures[:60])
    if markers:
        out.append("MARKERS:")
        out.extend("  " + m for m in markers[:20])
    if not signatures and not imports:
        out.append("PREVIEW:")
        out.extend("  " + l for l in lines[:25])
    out.append(
        "GAPS: function bodies, comments, and string literals were dropped. "
        "This is an offline extractive stub -- set SHUNT_PROVIDER=anthropic "
        "for a real summary."
    )
    text = "\n".join(out)
    return Result(
        text=text,
        model="stub",
        in_tokens=config.estimate_tokens(prompt),
        out_tokens=config.estimate_tokens(text),
    )


# --------------------------------------------------------------------------
# dispatch
# --------------------------------------------------------------------------

def _has_credentials() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


def resolve(requested: str) -> str:
    if requested == "auto":
        return "anthropic" if _has_credentials() else "stub"
    return requested


def run(mode: Mode, prompt: str, provider: str = "auto") -> Result:
    chosen = resolve(provider)
    if chosen == "anthropic":
        try:
            return _run_anthropic(mode, prompt)
        except Exception as exc:  # network down, no key, rate limit
            # Degrading to the stub is better than blocking the user's Read.
            res = _run_stub(mode, prompt)
            res.text = f"[shunt: {mode.model} unavailable ({type(exc).__name__}), used offline extractor]\n{res.text}"
            return res
    return _run_stub(mode, prompt)


def run_chunked(mode: Mode, *, path: str, content: str, question: str,
                provider: str = "auto", chunk_tokens: int = 60000) -> Result:
    """Digest a file too large for one call, then digest the digests."""
    chars = chunk_tokens * 4
    if len(content) <= chars:
        return run(mode, mode.render(path=path, content=content, question=question), provider)

    lines = content.splitlines(keepends=True)
    chunks, cur, size = [], [], 0
    for line in lines:
        cur.append(line)
        size += len(line)
        if size >= chars:
            chunks.append("".join(cur))
            cur, size = [], 0
    if cur:
        chunks.append("".join(cur))

    parts, in_tok, out_tok, model = [], 0, 0, "stub"
    for n, chunk in enumerate(chunks, 1):
        r = run(mode, mode.render(
            path=f"{path} (part {n} of {len(chunks)})", content=chunk, question=question), provider)
        parts.append(f"--- part {n}/{len(chunks)} ---\n{r.text}")
        in_tok += r.in_tokens
        out_tok += r.out_tokens
        model = r.model
    joined = "\n".join(parts)
    return Result(text=joined, model=model, in_tokens=in_tok, out_tokens=out_tok)
