# Getting started

## Prerequisites

- Python 3.11+ (3.13 recommended; matches CI and Docker)
- `DataSet/candidates.jsonl` for full ranking (Git LFS)
- CPU only; ~16 GB RAM for 100K runs

## Install

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

## Health check

```bash
python rank.py --health
```

Expected: `[OK] avera foundation ready (... must-have skills loaded)`.

## Smoke rank (fixture)

```bash
python rank.py --candidates tests/fixtures/sample.jsonl --limit 5 --out ci_submission.csv
```

## Full submission pipeline

```bash
python rank.py --candidates DataSet/candidates.jsonl --out submission.csv
python DataSet/validate_submission.py submission.csv
```

Or:

```bash
make validate        # health + smoke rank + pytest
make validate-full   # full 100K rank + organizer validation
make ci              # lint + test + security + integration smoke
make eval            # honeypot rate, NDCG@10, P@5/P@10, Recovery@10
make generalization  # two-JD demo (AI/ML + DevOps)
make mypy            # static type check
```

## Offline semantic model

For air-gapped ranking (`has_network_during_ranking: false`):

```bash
make download-model
# Windows PowerShell:
$env:AVERA_SEMANTIC_MODEL="$PWD\models/all-MiniLM-L6-v2"
python rank.py --candidates DataSet/candidates.jsonl --out submission.csv
```

The Docker image bakes the model at build time — see [how-to/runbook.md](how-to/runbook.md).

## Sandbox demo

**HuggingFace:** https://huggingface.co/spaces/gp5901/avera-ranker

Upload a `.jsonl` file (1–100 rows). Locally:

```bash
python app.py   # Gradio on http://localhost:7860
# or
make docker-sandbox
```

## Next steps

- [README — methodology, architecture, why Avera](../README.md)
- [Developer walkthrough](submission/walkthrough.md)
- [Architecture](explanation/architecture.md)
- [Scoring methodology](explanation/methodology.md)
- [SRE runbook](how-to/runbook.md)
- [Documentation index](README.md)
