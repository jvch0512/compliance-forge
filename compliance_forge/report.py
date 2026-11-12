from __future__ import annotations

from .model import Answer, Control
from .scoring import Gap, by_domain, by_framework, roadmap, weighted_score


def _bar(p: float, width: int = 20) -> str:
    n = round(p / 100 * width)
    return "█" * n + "░" * (width - n)


def to_markdown(meta: dict, frameworks: dict[str, str], controls: list[Control], answers: dict[str, Answer], gap_list: list[Gap]) -> str:
    L = [f"# Compliance gap assessment: {meta.get('organization', 'Organization')}", ""]
    if meta.get("assessed_on"):
        L += [f"Assessment date: {meta['assessed_on']}", ""]
    L += [f"## Overall score: {weighted_score(controls, answers)}%", "", "### By framework", "", "| Framework | Score | |", "|---|---|---|"]
    for fw, s in by_framework(frameworks, controls, answers).items():
        L.append(f"| {frameworks[fw]} | {s}% | `{_bar(s)}` |")
    L += ["", "### By domain", "", "| Domain | Score | |", "|---|---|---|"]
    for d, s in by_domain(controls, answers).items():
        L.append(f"| {d} | {s}% | `{_bar(s)}` |")
    L += ["", "## Remediation roadmap", ""]
    for phase, items in roadmap(gap_list).items():
        L += [f"### {phase}", ""]
        if not items:
            L += ["_Nothing in this phase._", ""]
            continue
        L += ["| Control | Status | Owner | Effort | Frameworks |", "|---|---|---|---|---|"]
        for g in items:
            a = answers[g.control.id]
            L.append(f"| **{g.control.id}** {g.control.title} | {g.status} | {a.owner or '-'} | {g.control.effort} | {', '.join(g.frameworks)} |")
        L.append("")
    L += ["## Requirement crosswalk", "", "| Control | " + " | ".join(frameworks) + " |", "|---|" + "---|" * len(frameworks)]
    for c in controls:
        L.append(f"| {c.id} | " + " | ".join(", ".join(c.mappings.get(fw, [])) or "-" for fw in frameworks) + " |")
    L += ["", "> Mappings are indicative and intended for gap analysis, not legal advice."]
    return "\n".join(L) + "\n"
