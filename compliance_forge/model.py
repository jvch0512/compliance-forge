from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

STATUS_SCORE = {"implemented": 1.0, "partial": 0.5, "planned": 0.2, "missing": 0.0}
EFFORT_DAYS = {"low": 15, "medium": 45, "high": 90}


@dataclass(frozen=True)
class Control:
    id: str
    title: str
    domain: str
    weight: int
    effort: str
    mappings: dict[str, list[str]]


@dataclass
class Answer:
    status: str
    owner: str = ""
    evidence: str = ""


def load_catalog(path: str | Path) -> tuple[dict[str, str], list[Control]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    controls = [Control(**c) for c in data["controls"]]
    ids = [c.id for c in controls]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate control ids in catalog")
    for c in controls:
        if c.effort not in EFFORT_DAYS:
            raise ValueError(f"{c.id}: invalid effort {c.effort!r}")
        if not 1 <= c.weight <= 5:
            raise ValueError(f"{c.id}: weight must be 1..5")
        unknown = set(c.mappings) - set(data["frameworks"])
        if unknown:
            raise ValueError(f"{c.id}: unknown frameworks {sorted(unknown)}")
    return data["frameworks"], controls


def load_assessment(path: str | Path, controls: list[Control]) -> tuple[dict, dict[str, Answer]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    valid = set(STATUS_SCORE) | {"not_applicable"}
    answers: dict[str, Answer] = {}
    known = {c.id for c in controls}
    for cid, a in data.get("answers", {}).items():
        if cid not in known:
            raise ValueError(f"assessment references unknown control {cid}")
        if a.get("status") not in valid:
            raise ValueError(f"{cid}: invalid status {a.get('status')!r}")
        answers[cid] = Answer(a["status"], a.get("owner", ""), a.get("evidence", ""))
    missing = known - set(answers)
    if missing:
        raise ValueError(f"assessment is missing answers for: {sorted(missing)}")
    meta = {k: v for k, v in data.items() if k != "answers"}
    return meta, answers
