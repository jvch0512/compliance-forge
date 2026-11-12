from pathlib import Path

import pytest

from compliance_forge.cli import main
from compliance_forge.model import Answer, load_assessment, load_catalog
from compliance_forge.scoring import by_framework, gaps, roadmap, weighted_score

ROOT = Path(__file__).parent.parent
FW, CONTROLS = load_catalog(ROOT / "catalog/controls.yml")
META, ANSWERS = load_assessment(ROOT / "examples/assessment.yml", CONTROLS)


def uniform(status):
    return {c.id: Answer(status) for c in CONTROLS}


def test_extremes():
    assert weighted_score(CONTROLS, uniform("implemented")) == 100.0
    assert weighted_score(CONTROLS, uniform("missing")) == 0.0
    assert weighted_score(CONTROLS, uniform("partial")) == 50.0


def test_not_applicable_excluded_from_denominator():
    a = uniform("implemented")
    a["ACC-02"] = Answer("not_applicable")
    assert weighted_score(CONTROLS, a) == 100.0


def test_framework_scores_in_range_and_complete():
    s = by_framework(FW, CONTROLS, ANSWERS)
    assert set(s) == set(FW) and all(0 <= v <= 100 for v in s.values())


def test_gaps_exclude_implemented():
    g = {x.control.id for x in gaps(CONTROLS, ANSWERS)}
    assert "GOV-01" not in g and "INC-02" in g


def test_low_effort_critical_gap_is_phase_one():
    rm = roadmap(gaps(CONTROLS, ANSWERS))
    phase1 = {g.control.id for g in next(iter(rm.values()))}
    assert {"INC-02", "ACC-02"} <= phase1


def test_every_gap_lands_in_exactly_one_phase():
    g = gaps(CONTROLS, ANSWERS)
    placed = [x.control.id for items in roadmap(g).values() for x in items]
    assert sorted(placed) == sorted(x.control.id for x in g)


def test_catalog_has_all_three_frameworks_mapped():
    for fw in FW:
        assert any(fw in c.mappings for c in CONTROLS)


def test_incomplete_assessment_rejected(tmp_path):
    f = tmp_path / "a.yml"
    f.write_text("answers:\n  GOV-01: {status: implemented}\n")
    with pytest.raises(ValueError, match="missing answers"):
        load_assessment(f, CONTROLS)


def test_invalid_status_rejected(tmp_path):
    f = tmp_path / "a.yml"
    f.write_text("answers:\n  GOV-01: {status: done}\n")
    with pytest.raises(ValueError, match="invalid status"):
        load_assessment(f, CONTROLS)


def test_cli_report_and_gate(tmp_path):
    out = tmp_path / "r.md"
    assert main([str(ROOT / "examples/assessment.yml"), "-o", str(out)]) == 0
    text = out.read_text()
    assert "Remediation roadmap" in text and "crosswalk" in text
    assert main([str(ROOT / "examples/assessment.yml"), "-o", str(out), "--min-score", "99"]) == 2
