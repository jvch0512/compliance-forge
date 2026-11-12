from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .model import load_assessment, load_catalog
from .report import to_markdown
from .scoring import gaps, weighted_score

DEFAULT_CATALOG = Path(__file__).resolve().parent.parent / "catalog" / "controls.yml"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="compliance-forge", description="Cross-framework compliance gap assessment.")
    p.add_argument("assessment", help="assessment YAML (see examples/assessment.yml)")
    p.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    p.add_argument("-o", "--output", help="write Markdown report to file")
    p.add_argument("--min-score", type=float, help="exit with code 2 if the overall score is below this value")
    args = p.parse_args(argv)

    frameworks, controls = load_catalog(args.catalog)
    meta, answers = load_assessment(args.assessment, controls)
    report = to_markdown(meta, frameworks, controls, answers, gaps(controls, answers))
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    if args.min_score is not None and weighted_score(controls, answers) < args.min_score:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
