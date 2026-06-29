# Avera: Candidate Ranking Engine

![CI Status](https://img.shields.io/badge/build-passing-brightgreen)
![Security](https://img.shields.io/badge/security-hardened-blue)

Avera is a high-performance, deterministic ranking engine engineered to evaluate 100,000 candidate profiles on CPU. Designed around hybrid semantic job understanding and objective constraints, Avera uses `sentence-transformers` for contextual relevance, filters keyword-stuffing anomalies (honeypots), and prioritizes verified technical expertise, career trajectory, and behavioral signals.

**Sandbox:** https://huggingface.co/spaces/gp5901/avera-ranker

## System Capabilities

| Capability                 | Description                                                                                                                 |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **O(N log K) Min-Heap**    | Processes 100K records in memory-efficient `O(K)` space, never loading the entire scored list into memory.                  |
| **Deep Job Understanding** | Uses `sentence-transformers` (`all-MiniLM-L6-v2`) for semantic cosine-similarity matching against the Job Description.      |
| **Defensive Boundary**     | Pydantic enforces schema constraints at the ingestion layer, catching missing bounds (`-1` logic) and structural anomalies. |
| **Honeypot Detection**     | Detects mathematically impossible timelines, unverified generalists, and ghost candidates.                                  |
| **Explainable Output**     | Deterministic (non-LLM) reasoning via `src/reasoning.py` — transparent _why_ for every ranked candidate.                    |
| **Security Hardened**      | Employs `defusedcsv` to prevent OWASP A03 (Formula Injection) during CSV/Excel generation.                                  |
| **Output Canary (ADR-16)** | Exactly 100 unique IDs, subset of input pool, validated before write.                                                       |

## Documentation (Diátaxis Framework)

Full index: **[docs/README.md](docs/README.md)**

| Document                                                                | Description                                                           |
| ----------------------------------------------------------------------- | --------------------------------------------------------------------- |
| [Getting started](docs/getting-started.md)                              | Install, health check, smoke rank, validation                         |
| [Walkthrough & portal checklist](docs/submission/walkthrough.md)        | Reproduction, sandbox, submission artifacts                           |
| [Slide deck (PDF)](docs/submission/deck.pdf)                            | Portal deck — regenerate with `make export-pdf`                       |
| [System Architecture](docs/explanation/architecture.md)                 | Pipeline, ADRs, exception hierarchy                                   |
| [Scoring Methodology](docs/explanation/methodology.md)                  | Hybrid semantic + heuristic weights, honeypots, behavioral multiplier |
| [SRE Day-2 Runbook](docs/how-to/runbook.md)                             | Local execution, offline model, Docker, troubleshooting               |
| [ADR 003: Semantic Hybrid Layer](docs/adr/003-semantic-hybrid-layer.md) | Why embeddings sit alongside deterministic scorers                    |

## How Avera Meets Track 1 (Intelligent Candidate Discovery)

Redrob's challenge JD is explicit: **keyword matching is a trap**. The dataset contains honeypots with perfect AI skill lists and non-technical titles. Avera is built to match what the JD _means_, not what a substring search returns.

| JD signal                          | Avera response                                                                                                     |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Career trajectory over skill lists | Title & career scorer (35%) + semantic fit on headline, summary, and `career_history` descriptions (15%)           |
| Behavioral availability            | Multiplicative modifier (0.4×–1.3×) on response rate, activity, notice period, interview/offer rates, GitHub score |
| Honeypot traps                     | Fictional-company pre-filter + 4-method honeypot detector before scoring                                           |
| Explainable reasoning              | Deterministic `src/reasoning.py` — no LLM in the ranking path                                                      |
| India-scale throughput             | O(N log K) min-heap, streaming JSONL ingest, structured JSON logs                                                  |

Scorer weights are centralized in `src/config.py` and validated at import. The JD parser extracts must-have skills and target cities from `DataSet/job_description.txt`; semantic similarity uses the full JD text block.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scoring pipeline (full 100K pool → top 100)
python rank.py --candidates DataSet/candidates.jsonl --out submission.csv

# Validate the output contract (exactly 100 rows)
python DataSet/validate_submission.py submission.csv

# Makefile shortcuts
make validate        # health + smoke rank + pytest
make validate-full   # full 100K rank + organizer validation
make ci              # lint + test + security + integration smoke
make download-model  # pre-download MiniLM for offline ranking
make export-pdf      # regenerate docs/submission/deck.pdf
make docker-sandbox  # Gradio demo (offline model baked in image)
```

### Offline / CI environment variables

| Variable                              | Purpose                                                                             |
| ------------------------------------- | ----------------------------------------------------------------------------------- |
| `AVERA_SKIP_SEMANTIC=1`               | Skip model load in unit tests (default in `tests/conftest.py`)                      |
| `AVERA_SEMANTIC_MODEL=/path/to/model` | Local MiniLM directory for air-gapped ranking (`has_network_during_ranking: false`) |

## Submission artifacts

| Artifact    | Path                             |
| ----------- | -------------------------------- |
| CSV         | `submission.csv`                 |
| XLSX        | `submission.xlsx`                |
| Metadata    | `submission_metadata.yaml`       |
| Walkthrough | `docs/submission/walkthrough.md` |
| Slide deck  | `docs/submission/deck.pdf`       |

## Repository Structure

```
.
├── app.py                   # Gradio sandbox (HuggingFace Space)
├── DataSet/                 # candidates.jsonl (LFS), job_description.txt, validate_submission.py
├── docs/                    # Diátaxis docs — see docs/README.md
├── scripts/                 # download_model.py, export_deck_pdf.py, calibration helpers
├── src/                     # Core engine
│   ├── config.py            # Weights, taxonomies, behavioral bounds
│   ├── ranker.py            # Min-heap O(N log K) orchestration
│   ├── reasoning.py         # Deterministic explanation strings
│   ├── logging_config.py    # Structured JSON observability
│   ├── scorers/             # Title, skills, semantic, experience, location, behavioral
│   └── detectors/           # Honeypot detection
├── tests/                   # Pytest suite (44 tests)
├── Dockerfile               # Runtime + baked MiniLM for offline ranking
├── docker-compose.yml       # Sandbox and CLI services
├── rank.py                  # CLI entrypoint
├── submission.csv           # Track 1 submission output
└── submission_metadata.yaml # Portal metadata
```
