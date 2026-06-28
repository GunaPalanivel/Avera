# Avera: Candidate Ranking Engine

![CI Status](https://img.shields.io/badge/build-passing-brightgreen)
![Security](https://img.shields.io/badge/security-hardened-blue)

Avera is a high-performance, deterministic ranking engine engineered to evaluate 100,000 candidate profiles in under 20 seconds. Designed around deep semantic job understanding and objective constraints, Avera uses `sentence-transformers` for contextual relevance, filters keyword-stuffing anomalies (honeypots), and prioritizes verified technical expertise, career trajectory, and behavioral signals.

## System Capabilities

| Capability | Description |
|------------|-------------|
| **O(N log K) Min-Heap** | Processes 100K records in memory-efficient `O(K)` space, never loading the entire scored list into memory. |
| **Deep Job Understanding**| Uses `sentence-transformers` (`all-MiniLM-L6-v2`) for semantic cosine-similarity matching against the Job Description. |
| **Defensive Boundary** | Pydantic enforces schema constraints at the ingestion layer, catching missing bounds (`-1` logic) and structural anomalies. |
| **Honeypot Detection** | Detects mathematically impossible timelines, unverified generalists, and ghost candidates. |
| **Explainable Output** | Deterministic (non-LLM) reasoning extraction ensures 100% transparency into *why* a candidate was selected. |
| **Security Hardened** | Employs `defusedcsv` to prevent OWASP A03 (Formula Injection) during CSV/Excel generation. |

## Documentation (Diátaxis Framework)

This repository follows the OSS Diátaxis structure for modular, targeted documentation:

*   **[System Architecture](docs/explanation/architecture.md)**: Explore the architectural decisions (ADRs) powering the system (Why an O(N log K) Heap? Why JSON logging?).
*   **[Scoring Methodology](docs/explanation/methodology.md)**: Deep dive into the hybrid Semantic+Heuristic system (Semantic, Title, Skills, Experience, Location) and the Behavioral Multiplier.
*   **[SRE Day-2 Runbook](docs/how-to/runbook.md)**: Operational guide for local execution, observability patterns, and troubleshooting.
*   **[ADR 003: Semantic Hybrid Layer](docs/adr/003-semantic-hybrid-layer.md)**: Why embeddings sit alongside deterministic scorers for Track 1.

## How Avera Meets Track 1 (Intelligent Candidate Discovery)

Redrob's challenge JD is explicit: **keyword matching is a trap**. The dataset contains honeypots with perfect AI skill lists and non-technical titles. Avera is built to match what the JD *means*, not what a substring search returns.

| JD signal | Avera response |
|-----------|----------------|
| Career trajectory over skill lists | Title & career scorer (35%) + semantic fit on headline, summary, and `career_history` descriptions (15%) |
| Behavioral availability | Multiplicative modifier (0.4×–1.3×) on response rate, activity, notice period, interview/offer rates, GitHub score |
| Honeypot traps | Fictional-company pre-filter + 4-method honeypot detector before scoring |
| Explainable reasoning | Deterministic `reasoning.py` — no LLM in the ranking path |
| India-scale throughput | O(N log K) min-heap, streaming JSONL ingest, structured JSON logs |

Scorer weights are centralized in `src/config.py` and validated at import. The JD parser extracts must-have skills and target cities from `job_description.txt`; semantic similarity uses the full JD text block.

## Quick Start

Execute the core scoring engine against the dataset:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scoring pipeline (full 100K pool → top 100)
python rank.py --candidates DataSet/candidates.jsonl --out submission.csv

# Validate the output contract (exactly 100 rows)
python DataSet/validate_submission.py submission.csv

# Or use Makefile shortcuts
make validate        # health + smoke rank + pytest
make validate-full   # full 100K rank + organizer validation
make ci              # lint + test + security + integration smoke
```

### Offline / CI environment variables

| Variable | Purpose |
|----------|---------|
| `AVERA_SKIP_SEMANTIC=1` | Skip model load in unit tests (default in `tests/conftest.py`) |
| `AVERA_SEMANTIC_MODEL=/path/to/model` | Local MiniLM directory for air-gapped ranking (`has_network_during_ranking: false`) |

## Repository Structure

```
.
├── DataSet/                 # Excluded from version control (Raw JSONL)
├── docs/                    # Diátaxis Documentation (Architecture, Methodology, Runbook)
├── src/                     # Foundational Core and Scoring Engine
│   ├── models.py            # Pydantic boundary
│   ├── ranker.py            # Min-Heap O(N log K) logic
│   ├── logging_config.py    # Structured JSON observability
│   └── scorers/             # Multi-faceted deterministic scorers
├── tests/                   # Pytest suite (Regression & Edge-cases)
├── rank.py                  # CLI Entrypoint
└── README.md                # This document
```
