from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .model import EFFORT_DAYS, STATUS_SCORE, Answer, Control


def _pct(num: float, den: float) -> float:
    return round(100.0 * num / den, 1) if den else 0.0


def weighted_score(controls: list[Control], answers: dict[str, Answer]) -> float:
    num = den = 0.0
    for c in controls:
        a = answers[c.id]
        if a.status == "not_applicable":
            continue
        num += c.weight * STATUS_SCORE[a.status]
        den += c.weight
    return _pct(num, den)


def by_framework(frameworks: dict[str, str], controls: list[Control], answers: dict[str, Answer]) -> dict[str, float]:
    return {fw: weighted_score([c for c in controls if fw in c.mappings], answers) for fw in frameworks}


def by_domain(controls: list[Control], answers: dict[str, Answer]) -> dict[str, float]:
    groups: dict[str, list[Control]] = defaultdict(list)
    for c in controls:
        groups[c.domain].append(c)
    return {d: weighted_score(cs, answers) for d, cs in sorted(groups.items())}


@dataclass
class Gap:
    control: Control
    status: str
    risk_points: float      # weight * (1 - score): how much compliance this gap costs
    payoff: float           # risk points removed per 10 days of effort (quick-win ranking)
    frameworks: list[str]


def gaps(controls: list[Control], answers: dict[str, Answer]) -> list[Gap]:
    out = []
    for c in controls:
        a = answers[c.id]
        if a.status in ("implemented", "not_applicable"):
            continue
        risk = c.weight * (1 - STATUS_SCORE[a.status])
        payoff = round(risk / EFFORT_DAYS[c.effort] * 10, 2)
        out.append(Gap(c, a.status, round(risk, 2), payoff, sorted(c.mappings)))
    return out


def roadmap(gap_list: list[Gap]) -> dict[str, list[Gap]]:
    """Phase 1: quick wins (high payoff). Phase 2: big risks. Phase 3: the rest."""
    ordered = sorted(gap_list, key=lambda g: (-g.payoff, -g.risk_points, g.control.id))
    p1 = [g for g in ordered if g.control.effort == "low" or g.payoff >= 1.0]
    rest = [g for g in ordered if g not in p1]
    p2 = [g for g in rest if g.control.weight >= 4]
    p3 = [g for g in rest if g not in p2]
    return {"Phase 1 (0-30 days): quick wins": p1, "Phase 2 (30-90 days): major risks": p2, "Phase 3 (90+ days): maturity": p3}
