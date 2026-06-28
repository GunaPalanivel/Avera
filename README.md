# Avera: Candidate Ranking Engine

![CI Status](https://img.shields.io/badge/build-passing-brightgreen)
![Security](https://img.shields.io/badge/security-hardened-blue)

Avera is a high-performance, deterministic ranking engine engineered to evaluate 100,000 candidate profiles in under 20 seconds. Designed strictly around the objective requirements of a DevOps/SRE Job Description, Avera filters keyword-stuffing anomalies (honeypots) and prioritizes verified technical expertise, career trajectory, and behavioral signals.

## System Capabilities

| Capability | Description |
|------------|-------------|
| **O(N log K) Min-Heap** | Processes 100K records in memory-efficient `O(K)` space, never loading the entire scored list into memory. |
| **Defensive Boundary** | Pydantic enforces schema constraints at the ingestion layer, catching missing bounds (`-1` logic) and structural anomalies. |
| **Honeypot Detection** | Detects mathematically impossible timelines, unverified generalists, and ghost candidates. |
| **Explainable Output** | Deterministic (non-LLM) reasoning extraction ensures 100% transparency into *why* a candidate was selected. |
| **Security Hardened** | Employs `defusedcsv` to prevent OWASP A03 (Formula Injection) during CSV/Excel generation. |

## Documentation (Diátaxis Framework)

This repository follows the OSS Diátaxis structure for modular, targeted documentation:

*   **[System Architecture](docs/explanation/architecture.md)**: Explore the architectural decisions (ADRs) powering the system (Why an O(N log K) Heap? Why JSON logging?).
*   **[Scoring Methodology](docs/explanation/methodology.md)**: Deep dive into the 5-scorer system (Title, Skills, Behavioral, Experience, Location) and the 5-method Honeypot Detector.
*   **[SRE Day-2 Runbook](docs/how-to/runbook.md)**: Operational guide for local execution, observability patterns, and troubleshooting.

## Quick Start

Execute the core scoring engine against the dataset:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scoring pipeline
python rank.py --candidates DataSet/candidates.jsonl --out submission.csv

# Validate the output contract
python DataSet/validate_submission.py submission.csv
```

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
