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

Refresh the Space to the current codebase, then verify:

```bash
python scripts/sync_space.py   # rebuilds space_deploy/ from current src, rank.py, app.py, JD files
hf auth login                  # one-time; needs a write token from huggingface.co/settings/tokens
hf upload gp5901/avera-ranker space_deploy . --repo-type=space --commit-message "sync current codebase"
```

1. `python scripts/sync_space.py` mirrors the current code into `space_deploy/` (preserves the Space README frontmatter and runtime `requirements.txt`).
2. `hf upload ... --repo-type=space` pushes it; the Space rebuilds automatically.
3. Open https://huggingface.co/spaces/gp5901/avera-ranker
4. Upload `tests/fixtures/sample.jsonl` (or a small JSONL slice).
5. Confirm results table renders and **Download submission.csv** works.
6. Optional checks: `hf spaces info gp5901/avera-ranker` and `hf spaces logs --build gp5901/avera-ranker`.
7. Record date/time in your notes for Stage 5 defense.

Note: sandbox output can be fewer than 100 rows (honeypots and fictional companies are filtered); the exactly-100-row rule in `DataSet/validate_submission.py` applies to the portal `submission.csv` from the full 100K pool, not to sandbox output.

## Hack2skill portal uploads

| Field       | Value                                                                  |
| ----------- | ---------------------------------------------------------------------- |
| Team        | The Maverick's (Leader: Guna Palanivel, Member: Vidyasree)             |
| Participant | `gunapalanivel2003_9679`                                               |
| Ranked CSV  | Rename `submission.csv` to `gunapalanivel2003_9679.csv` before upload  |
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
