# Challenge dataset (Track 01)

Redrob **Intelligent Candidate Discovery** release files for local ranking and validation.

| File | Description |
|------|-------------|
| `candidates.jsonl` | Full candidate pool (~100K profiles). Stored with **Git LFS** (>100 MB). |
| `candidate_schema.json` | JSON schema for candidate records |
| `sample_candidates.json` | Small sample for quick inspection |
| `sample_submission.csv` | Example output shape |
| `validate_submission.py` | Organizer validation script for your CSV |
| `submission_metadata_template.yaml` | Portal metadata template |
| `job_description.docx` | Target role for scoring (Note: specifications have been extracted and live in `idea/ProcessedData/docx_extracts/`) |
| `submission_spec.docx` | CSV format and rules (Note: specifications have been extracted and live in `idea/ProcessedData/docx_extracts/`) |
| `redrob_signals_doc.docx` | Behavioral / honeypot signal definitions (Note: specifications have been extracted and live in `idea/ProcessedData/docx_extracts/`) |
| `README.docx` | Organizer readme (Note: specifications have been extracted and live in `idea/ProcessedData/docx_extracts/`) |

## Clone note

After cloning, fetch LFS objects:

```bash
git lfs install
git lfs pull
```

Verify `candidates.jsonl` is present and non-empty (expect ~465 MB on disk).

## Default paths (Avera CLI, when available)

```bash
python rank.py --candidates ./DataSet/candidates.jsonl --out ./submission.csv
python DataSet/validate_submission.py ./submission.csv
```
