"""Mode registry.

A "mode" is a declarative agent: instructions + model + parameters, stored as
data rather than code. Swapping the model a workload runs on is then a config
edit, not a refactor -- which is the whole point of this exercise.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

MODES_DIR = Path(__file__).parent / "modes"


@dataclass(frozen=True)
class Mode:
    name: str
    model: str
    system: str
    user_template: str
    max_tokens: int = 1500
    temperature: float = 0.0
    description: str = ""

    def render(self, *, path: str, content: str, question: str) -> str:
        return self.user_template.format(
            path=path,
            content=content,
            question=question,
            line_count=content.count("\n") + 1,
        )


def load(name: str) -> Mode:
    f = MODES_DIR / f"{name}.json"
    if not f.is_file():
        raise KeyError(f"no such mode: {name!r} (have: {', '.join(available())})")
    data = json.loads(f.read_text())
    return Mode(
        name=data["name"],
        model=data["model"],
        system=data["system"],
        user_template=data["user_template"],
        max_tokens=data.get("max_tokens", 1500),
        temperature=data.get("temperature", 0.0),
        description=data.get("description", ""),
    )


def available() -> list[str]:
    return sorted(p.stem for p in MODES_DIR.glob("*.json"))
