# Portal submission checklist (Hack2skill / India Runs Track 1)

Complete these steps manually before the deadline. The repo cannot submit on your behalf.

## Pre-flight (local)

```bash
git checkout main && git pull
make test
make validate-full          # time this; must stay under 5 minutes CPU
python scripts/eval.py
python scripts/test_generalization.py
make export-pdf             # docs/submission/deck.pdf
```

## HuggingFace Space E2E

1. Push latest `main` to the Space repo (`gp5901/avera-ranker`) or trigger rebuild.
2. Open https://huggingface.co/spaces/gp5901/avera-ranker
3. Upload `tests/fixtures/sample.jsonl` (or a small JSONL slice).
4. Confirm results table renders and **Download submission.csv** works.
5. Record date/time in your notes for Stage 5 defense.

## Hack2skill portal uploads

| Field       | Value                                                                  |
| ----------- | ---------------------------------------------------------------------- |
| Ranked CSV  | Rename `submission.csv` to **your registered participant ID** + `.csv` |
| Slide deck  | `docs/submission/deck.pdf`                                             |
| Metadata    | Copy fields from `submission_metadata.yaml`                            |
| Sandbox URL | `https://huggingface.co/spaces/gp5901/avera-ranker`                    |
| GitHub      | `https://github.com/GunaPalanivel/Avera`                               |

**Do not** upload `submission.xlsx` to the portal (CSV only per spec §6).

## Stage 5 talking points

- Keyword matching is a trap; honeypots are filtered before scoring.
- Behavioral signals are a **multiplier**, not a cosmetic add-on.
- Semantic layer is batch-encoded MiniLM behind a heuristic gate for CPU budget.
- Same `rank.py` runs on AI/ML and DevOps JD files (`scripts/test_generalization.py`).
- Offline reproducibility: Docker baked model, `AVERA_REFERENCE_DATE`, deterministic scoring.
