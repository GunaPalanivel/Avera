# SRE Day-2 Operations Runbook

This document details local execution, observability patterns, and troubleshooting steps for the Avera Ranking Engine.

## Quick Start (Local Execution)

Avera requires Python 3.13 and has minimal external dependencies.

```bash
# 1. Install Dependencies
python -m pip install -r requirements.txt

# 2. Run the Test Suite (Verifies deterministic output and honeypot flags)
python -m pytest tests/ -v

# 3. Execute the Ranking Pipeline
python rank.py --candidates DataSet/candidates.jsonl --out submission.csv

# 4. Validate output format via the official contract
python DataSet/validate_submission.py submission.csv
```

### Makefile targets

```bash
make validate        # health check + smoke rank + pytest
make validate-full   # full 100K rank + organizer validation
make ci              # lint + test + security + integration smoke
make download-model  # pre-download MiniLM for offline ranking
make export-pdf      # regenerate docs/submission/deck.pdf
make docker-build    # build image with baked semantic model
make docker-sandbox  # Gradio on http://localhost:7860
```

### Environment variables

| Variable               | Default            | Purpose                                                         |
| ---------------------- | ------------------ | --------------------------------------------------------------- |
| `AVERA_SKIP_SEMANTIC`  | unset (load model) | Set to `1` in tests to skip `sentence-transformers` load        |
| `AVERA_SEMANTIC_MODEL` | `all-MiniLM-L6-v2` | HuggingFace model id or **local directory** for offline ranking |

For sandbox/Docker with `has_network_during_ranking: false`, pre-download the model once:

```bash
make download-model
# Linux/macOS:
export AVERA_SEMANTIC_MODEL=$PWD/models/all-MiniLM-L6-v2
# Windows PowerShell:
$env:AVERA_SEMANTIC_MODEL="$PWD/models/all-MiniLM-L6-v2"
python rank.py --candidates DataSet/candidates.jsonl --out submission.csv
```

The **Docker image** bakes the model at build time (`Dockerfile` runs `scripts/download_model.py`) and sets `AVERA_SEMANTIC_MODEL=/app/models/all-MiniLM-L6-v2` so ranking works with no HuggingFace network access at runtime.

```bash
make docker-build
make docker-sandbox   # Gradio on http://localhost:7860
```

Unit tests set `AVERA_SKIP_SEMANTIC=1` automatically via `tests/conftest.py`.

## Observability (Structured Logging)

We employ a custom `JSONFormatter` in `src/logging_config.py` to output structured JSON logs, which can be easily ingested by Datadog, ELK, or CloudWatch.

### Log Format

```json
{
  "timestamp": "2026-06-27T14:30:00.000Z",
  "level": "INFO",
  "module": "rank",
  "message": "Scoring Engine completed in 15.4 seconds.",
  "run_id": "c70f9159-df76-4347-9b32-c70f91596b92"
}
```

### Performance Tuning

To monitor memory consumption over large datasets, the engine will emit `WARNING` logs if heap growth exceeds predefined bounds. Because the engine leverages an `O(K)` min-heap, memory footprints should remain strictly sub-50MB regardless of dataset size (N).

## Troubleshooting Common Errors

| Symptom                                                | Cause                                                                                                   | Resolution                                                                                                                          |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `ValidationError: 1 validation error for Candidate...` | Foundational Core rejected an object missing a critical field (e.g., `candidate_id`).                   | The system gracefully skips these. No action needed unless the error rate > 5%. In that case, check upstream data source integrity. |
| `FileNotFoundError: DataSet/candidates.jsonl`          | The data directory is not mounted or the file is missing.                                               | Verify the symlink or Docker volume mount in your `docker-compose.yml`.                                                             |
| `ZeroDivisionError` in Scorers                         | Highly anomalous edge cases (e.g., a candidate with exactly 0 total experience months and no fallback). | Scorer will log a `ScoringError` and default to `0.0` for that candidate. Ensure Pydantic constraints catch these early.            |
| `ImportError: No module named defusedcsv`              | Missing operational dependencies.                                                                       | Run `pip install -r requirements.txt` or execute via Docker container.                                                              |
