# compliance-forge

A cross-framework **compliance gap assessment** tool. Answer one questionnaire about your controls and get scores for **NIS2, GDPR and ISO/IEC 27001:2022** at the same time, a requirement crosswalk and a phased remediation roadmap ranked by risk reduced per day of effort.

The idea is "implement once, comply many": most organizations pay several times for the same control (for example MFA or tested backups) because each framework is tracked in a separate spreadsheet.

## What you get

* One catalog of 15 controls, each mapped to NIS2 Art. 21/23, GDPR articles and ISO 27001 Annex A references
* Weighted scoring (implemented = 1.0, partial = 0.5, planned = 0.2, missing = 0, not_applicable excluded)
* Scores per framework and per domain, with text bars
* **Roadmap engine**: gaps ranked by `risk removed / effort`, split into three phases (quick wins, major risks, maturity)
* Crosswalk table to show an auditor which control covers which requirement
* CI gate: `--min-score 70` returns exit code 2 when the organization is below the target

## Quick start

```bash
pip install -e .
compliance-forge examples/assessment.yml -o report.md
compliance-forge examples/assessment.yml --min-score 70   # exit code 2 if below
```

Assessment file:

```yaml
organization: Acme Logistics S.L.
answers:
  ACC-02: {status: missing, owner: IT}
  BCP-01: {status: partial, owner: IT, evidence: Backups run nightly, restores not tested}
```

Every control must be answered, so gaps cannot hide by omission.

## Extending

Add a framework to `catalog/controls.yml` under `frameworks:` and map controls to it. A Spanish ENS or DORA mapping fits the same structure. Loader validation rejects unknown frameworks, bad weights and duplicate IDs.

## Disclaimer

Mappings are indicative and meant for gap analysis. They are not legal advice and do not replace a formal audit.

## Development

```bash
pip install -e .[dev] && pytest -q
```

## License

MIT
