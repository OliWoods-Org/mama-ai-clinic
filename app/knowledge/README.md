# Medical Knowledge Bases

All clinical knowledge in this directory is sourced from publicly available WHO publications. The AI language model does NOT generate medical decisions -- it only translates structured data into plain language.

## Data Provenance

| File | Source | License |
|------|--------|---------|
| `imnci/chart_booklet.json` | WHO IMNCI Chart Booklet (2014 revision) | WHO Open Access |
| `imnci/danger_signs.json` | WHO IMNCI Chart Booklet | WHO Open Access |
| `imnci/classify.json` | WHO IMNCI Chart Booklet | WHO Open Access |
| `essential_medicines/eml_24.json` | WHO Model List of Essential Medicines, 24th List (2025) | WHO Open Access |
| `essential_medicines/dosing_tables.json` | WHO formulary + national guidelines | WHO Open Access |
| `essential_medicines/interactions.json` | WHO formulary | WHO Open Access |
| `first_aid/protocols.json` | WHO first aid guidelines | WHO Open Access |
| `training/chw_modules.json` | Original content based on WHO CHW competency framework | Apache 2.0 |
| `training/quiz_bank.json` | Original content | Apache 2.0 |
| `training/case_studies.json` | Original content based on IMNCI training materials | Apache 2.0 |

## Clinical Review

All knowledge base content should be reviewed by a clinician familiar with IMNCI before field deployment. File a GitHub issue with the `clinical-review` label for any concerns.

## Updating Knowledge Bases

1. Edit the relevant JSON file
2. Run `python scripts/validate_knowledge.py` to check integrity
3. Run `python eval/triage_eval.py` to verify triage accuracy
4. Submit a PR with clinical justification
