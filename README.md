# Avera: Candidate Ranking Engine

![CI Status](https://img.shields.io/badge/build-passing-brightgreen)
![Security](https://img.shields.io/badge/security-hardened-blue)

Avera is a **JD-parameterized candidate ranking engine** that evaluates 100,000 profiles on CPU and outputs an explainable top-100 shortlist. It combines hybrid semantic job understanding with deterministic constraints: `sentence-transformers` for contextual relevance, honeypot filters for adversarial traps, and behavioral signals for hireability — all without LLM calls in the ranking path.

**Sandbox:** https://huggingface.co/spaces/gp5901/avera-ranker (click the bundled "curated strong candidates" example for a representative run)

## In plain terms

Avera is a tireless expert recruiter that reads every single application properly and hands you a ranked shortlist of the best people for a role, in minutes instead of weeks.

**The problem it solves:** a job post can draw thousands of applicants. Keyword filters ("show everyone who typed Python") reward people who stuff their profile with the right words and miss genuinely strong people who described their work differently. A human recruiter catches the nuance but cannot read 100,000 profiles. Avera does.

**What it does:** you give it a job description and a pile of applicants; it returns a ranked top-100 with a plain-English reason for each placement.

**How it works, in everyday terms:**

| Step | What Avera does | Everyday analogy |
| ---- | --------------- | ---------------- |
| 1. Read the job | Understands what the role really needs, not just the buzzwords | Reads the job ad and grasps the intent |
| 2. Drop the fakes | Removes fake companies and too-good-to-be-true profiles | Spots padded and dishonest resumes |
| 3. Judge real fit | Weighs career history, real skills, experience, and location, reading the career story not just the keyword list | Reads between the lines like a seasoned recruiter |
| 4. Check availability | Down-ranks people who never reply to recruiters, went quiet for months, or have a long notice period | Focuses on who you can actually hire now |

**How any company uses it:** it is a reusable engine, not built for one company or one job. Point it at any job description and it adapts. Use the try-it web page for a quick look, or the automated pipeline for the full applicant pool. Standard applicant data goes in; a standard ranked spreadsheet comes out, alongside whatever hiring tools you already use.

**Trust and limits:** every ranking is explained from the person's real profile, it never uses gender, age, or ethnicity, and it is honest when a pool is weak. It supports a hiring decision; a person still makes the final call.

## Why Avera is built this way

Redrob's Track 1 challenge is not a keyword-matching exercise. The job description explicitly warns that **skill-list density is a trap** — the dataset embeds honeypots (marketing managers with perfect ML skills, fictional companies, behavioral ghosts). Judges evaluate **judgment and operability**, not embedding novelty alone.

We designed Avera as a **product-shaped PoC**, not a one-off script:

| Principle                                      | What it means in practice                                                                                        |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Match what the JD means**                    | Semantic cosine on full JD text + career narratives — not skills-section keyword density                         |
| **Enforce hard constraints deterministically** | YOE bands, must-have skills, cities, honeypots — auditable, no hallucination                                     |
| **Separate fit from hireability**              | Base score (5 scorers) × behavioral multiplier — a ghost profile cannot outrank an available one on skills alone |
| **Stay inside CPU / no-network budget**        | Two-stage funnel: heuristic gate (`≥ 0.11`) then semantic rerank on the top-K only; O(N log K) streaming heap    |
| **Prove generalization**                       | Same `rank.py` on AI/ML and DevOps JD files — zero code edits (`scripts/test_generalization.py`)                 |
| **Ship what you can operate**                  | Docker offline model, structured JSON logs, CI (lint/test/mypy/security/docker), runbook                         |

This mirrors how Redrob's production stack is evolving: **BM25 + rules today → hybrid retrieval tomorrow**. Avera demonstrates the retrieval/ranking layer a founding engineer would own — with honest scope claims about what generalizes (semantic + JD parser + domain-branching taxonomy) vs what stays a curated taxonomy per domain.

## Methodology

End-to-end flow from raw data to submission:

```
job_description.txt ──► jd_parser ──► JobRequirements (skills, cities, seniority, title keywords)
                                              │
candidates.jsonl ──► stream ──────────────────┼──► Pass 1: heuristic gen + semantic rerank on top-K (gate ≥ 0.11)
                                              │
                                              └──► Pass 2: Ranker
                                                     ├─ fictional filter + honeypot detector
                                                     ├─ 5 weighted scorers (seniority-aware weights)
                                                     ├─ behavioral multiplier (0.4×–1.3×)
                                                     └─ min-heap top-100
                                                            │
                                                            ▼
                                                   reasoning.py ──► submission.csv (ADR-16 canary)
```

**Scoring stages**

1. **Ingest & validate** — Pydantic boundary; malformed rows skipped, pipeline continues.
2. **Adversarial filters** — ~60% fictional companies dropped; ~1,600 honeypots removed (title/skill mismatch, expert-with-zero-months, impossible seniority, unverified generalist).
3. **Base score** — Weighted sum of semantic (25%), title/career, skills, career trajectory, education, experience, location. Weights adjust by JD seniority (`get_scorer_weights` in `src/config.py`); pure keyword scorers sit below the semantic and career signals.
4. **Semantic funnel** — MiniLM encoding runs only for candidates above the heuristic gate (`0.11`), and only the strongest `SEMANTIC_RERANK_TOPK` (default 5000) of those are encoded. Everyone else receives semantic `0.0`; no on-demand encoding after prefill.
5. **Behavioral multiplier** — Response rate, activity recency (`AVERA_REFERENCE_DATE`), notice period, interview/offer rates, GitHub score, verifications, profile completeness, recent applications — clamped to `[0.4, 1.3]`.
6. **Explainable output** — Rank-tier reasoning in `src/reasoning.py`: top ranks highlight strengths; ranks 20–99 include verifiable concerns (skill gaps, low response rate, notice period). No LLM in the output path.

**Score scale:** the base score is bounded to `[0, 1]` and the behavioral multiplier to `[0.4, 1.3]`, so the written `score` lies in `[0, 1.3]`. A score above 1.0 means a strong base fit lifted by strong availability signals; scores are a ranking order, not a percentage.

**Evaluation hooks**

```bash
python scripts/eval.py              # honeypot rate in top-100, NDCG@10 on calibration fixture
python scripts/test_generalization.py   # AI/ML JD + DevOps alt JD, same pipeline
```

Deep dive: [Scoring Methodology](docs/explanation/methodology.md)

## Technical choices

| Choice                              | Rationale                                                                                           | Rejected alternative                                                     |
| ----------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **Hybrid semantic + deterministic** | Career narrative fit (embeddings) + bounded JD constraints (rules)                                  | Pure BM25/keywords → honeypot traps; end-to-end LLM → unverifiable, slow |
| **`all-MiniLM-L6-v2`**              | 90 MB, CPU-friendly, strong sentence similarity                                                     | Larger cross-encoders → latency budget on 100K                           |
| **Two-stage funnel**                | Heuristic candidate generation then MiniLM rerank on the top-K only — keeps 100K CPU runs tractable | Encode every survivor → ~7× slower with no material top-100 change       |
| **Behavioral multiplier**           | Availability is hireability, not another additive feature                                           | Additive behavioral score → ghosts outrank available candidates          |
| **Pydantic ingestion boundary**     | One bad field cannot crash a 100K run                                                               | Raw dict access → minute-4 `TypeError`                                   |
| **defusedcsv output**               | OWASP A03 formula injection when judges open CSV in Excel                                           | Standard `csv` writer                                                    |
| **Structured JSON logging**         | `trace_id`, `latency_ms`, `prefill_ms` for ops/debug                                                | `print()` — unsearchable at scale                                        |
| **Docker + baked model**            | `has_network_during_ranking: false` reproducibility                                                 | Runtime HuggingFace download — flaky in sandbox                          |
| **mypy + determinism test**         | Type safety and SHA256 replay on fixture                                                            | Hope-based correctness                                                   |

ADRs: [001 min-heap](docs/adr/001-deterministic-min-heap-ranking.md) · [002 honeypots](docs/adr/002-honeypot-threat-modeling.md) · [003 semantic layer](docs/adr/003-semantic-hybrid-layer.md) · [017 domain branching](docs/adr/017-domain-branching-taxonomy.md) · [018 cross-encoder rerank](docs/adr/018-cross-encoder-rerank.md)

## System architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  rank.py CLI                                                     │
│  ├─ load_job_requirements()  → JobRequirements                  │
│  ├─ prefill_semantic_stream() → batch encode (gate survivors)   │
│  └─ Ranker.rank()            → stream → heap → top-100          │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   src/parsers/         src/scorers/          src/detectors/
   candidate_parser     title, skills,        honeypot_detector
   jd_parser             semantic, exp, loc    + fictional filter
                         behavioral_scorer
         │                    │                    │
         └────────────────────┴────────────────────┘
                              ▼
                    src/output_writer.py (defusedcsv + ADR-16 canary)
                              ▼
                    app.py (Gradio sandbox) · Docker · HF Space
```

Full architecture: [docs/explanation/architecture.md](docs/explanation/architecture.md)

## System capabilities

| Capability                 | Description                                                                                                                          |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **O(N log K) min-heap**    | Processes 100K records in `O(K)` memory, never loading the entire scored list.                                                       |
| **Deep job understanding** | JD parser (skills, cities, seniority, domain) + MiniLM semantic fit on headline, summary, `career_history` descriptions, and skills. |
| **Two-stage funnel**       | Heuristic candidate generation, then MiniLM rerank on the heuristic top-K only (`SEMANTIC_RERANK_TOPK`).                             |
| **Defensive boundary**     | Pydantic enforces schema at ingestion, coercing sentinel `-1` values and skipping malformed rows without crashing the run.           |
| **Honeypot detection**     | 4-method detector + fictional-company pre-filter catches impossible timelines, unverified generalists, and ghost profiles.           |
| **Explainable output**     | Deterministic, score-aware rank-tier reasoning via `src/reasoning.py` — no LLM in the output path.                                   |
| **Security hardened**      | `defusedcsv` and `sanitize_cell` on CSV and XLSX prevent OWASP A03 formula injection; path validation; PII-safe logs.                |
| **Output canary (ADR-16)** | Exactly 100 unique IDs, subset of the input pool, validated before write.                                                            |

## Documentation (Diátaxis Framework)

Full index: **[docs/README.md](docs/README.md)**

| Document                                                                        | Description                                                           |
| ------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| [Getting started](docs/getting-started.md)                                      | Install, health check, smoke rank, validation                         |
| [Walkthrough & portal checklist](docs/submission/walkthrough.md)                | Reproduction, sandbox, submission artifacts                           |
| [Portal checklist](docs/submission/portal_checklist.md)                         | Hack2skill + HF Space manual steps                                    |
| [Slide deck (PDF)](docs/submission/deck.pdf)                                    | Portal deck — regenerate with `make export-pdf`                       |
| [System Architecture](docs/explanation/architecture.md)                         | Pipeline, ADRs, exception hierarchy                                   |
| [Scoring Methodology](docs/explanation/methodology.md)                          | Hybrid semantic + heuristic weights, honeypots, behavioral multiplier |
| [SRE Day-2 Runbook](docs/how-to/runbook.md)                                     | Local execution, offline model, Docker, troubleshooting               |
| [ADR 003: Semantic Hybrid Layer](docs/adr/003-semantic-hybrid-layer.md)         | Why embeddings sit alongside deterministic scorers                    |
| [ADR 017: Domain-Branching Taxonomy](docs/adr/017-domain-branching-taxonomy.md) | Per-domain title/skill tables (AI/ML, DevOps, generic)                |

## How Avera Meets Track 1 (Intelligent Candidate Discovery)

Redrob's challenge JD is explicit: **keyword matching is a trap**. The dataset contains honeypots with perfect AI skill lists and non-technical titles. Avera is built to match what the JD _means_, not what a substring search returns.

| JD signal                          | Avera response                                                                                                                                                |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Career trajectory over skill lists | Title & career scorer (35%) + semantic fit on headline, summary, `career_history` descriptions, and skills (15%)                                              |
| Behavioral availability            | Multiplicative modifier (0.4×–1.3×) on response rate, activity, notice period, interview/offer rates, GitHub score, profile completeness, recent applications |
| Honeypot traps                     | Fictional-company pre-filter + 4-method honeypot detector before scoring                                                                                      |
| Explainable reasoning              | Deterministic `src/reasoning.py` — rank-tier templates with honest concerns for mid/low ranks                                                                 |
| India-scale throughput             | O(N log K) min-heap, two-pass streaming ingest, structured JSON logs with `trace_id` / `latency_ms`                                                           |

Scorer weights are centralized in `src/config.py` (`get_scorer_weights` by JD seniority) and validated at import. The JD parser extracts must-have skills, title keywords, seniority, and target cities from any `job_description.txt`; semantic similarity uses the full JD text block.

### Generalization (any JD, zero code changes)

```bash
python scripts/test_generalization.py   # bundled AI/ML JD + DevOps alt JD on same fixture
```

| What generalizes                                 | What is still a curated taxonomy                         |
| ------------------------------------------------ | -------------------------------------------------------- |
| Semantic cosine similarity on full JD text       | Per-domain skill taxonomy lists in `config.py`           |
| City catalog, seniority-based weights            | Title tier tables (AI/ML and DevOps today)               |
| Domain detection + branching title/skill tables  | Experience scorer keyword heuristics                     |
| Honeypot + fictional filters (dataset constants) | New domains beyond AI/ML and DevOps fall back to generic |

A DevOps/SRE JD now surfaces infrastructure titles in the shortlist (0 → 97 infra titles in a full-pool top-100 check) via `detect_domain` + `get_title_tiers`/`get_skill_taxonomy`; adding a new domain is a config table, not a code change.

### Roadmap (deliberately deferred)

Reviewer-suggested items we scoped out on purpose, to avoid over-engineering a CPU PoC and destabilizing a validated submission. Documented here as honest scope, not oversight:

| Item | Why deferred |
| ---- | ------------ |
| BM25 + RRF hybrid retrieval | The keyword skills scorer already covers lexical matches; sparse retrieval adds real complexity for marginal gain at this scale |
| BGE-small embedding swap | Re-bakes the offline model and re-scores everything; the cross-encoder (ADR-018) delivers the precision lift with less blast radius |
| Learned-to-rank weights | No recruiter click data to train on; hand-tuned weights are auditable and defensible for a PoC |
| Learned skill-adjacency graph | A 1.4M-skill graph is out of scope for a CPU PoC; curated synonyms + semantic fit cover adjacency today |

### Compliance posture

Recruitment ranking is treated as high-risk AI in the EU AI Act and subject to bias-audit rules (e.g. NYC Local Law 144). Avera does not use protected attributes (gender, age-derived, ethnicity-inferred) as features; reasoning strings are deterministic and traceable to profile fields for audit.

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
make eval            # honeypot rate + NDCG@10 on calibration fixture
make generalization  # two-JD zero-edit demo
make mypy            # static type check (src + rank.py)
make download-model  # pre-download MiniLM for offline ranking
make export-pdf      # regenerate docs/submission/deck.pdf
make docker-sandbox  # Gradio demo (offline model baked in image)
```

### Offline / CI environment variables

| Variable                              | Purpose                                                                             |
| ------------------------------------- | ----------------------------------------------------------------------------------- |
| `AVERA_SKIP_SEMANTIC=1`               | Skip model load in unit tests (default in `tests/conftest.py`)                      |
| `AVERA_SEMANTIC_MODEL=/path/to/model` | Local MiniLM directory for air-gapped ranking (`has_network_during_ranking: false`) |
| `AVERA_REFERENCE_DATE`                | Fixed reference date for behavioral recency (default `2026-06-27`)                  |
| `AVERA_SEMANTIC_RERANK_TOPK`          | Number of heuristic-top candidates to semantically rerank (default `5000`)          |
| `AVERA_SEMANTIC_BATCH`                | MiniLM encode batch size for host stability (default `128`)                         |

## Submission artifacts

| Artifact     | Path                                  |
| ------------ | ------------------------------------- |
| CSV          | `submission.csv`                      |
| XLSX         | `submission.xlsx` (local only)        |
| Metadata     | `submission_metadata.yaml`            |
| Walkthrough  | `docs/submission/walkthrough.md`      |
| Portal steps | `docs/submission/portal_checklist.md` |
| Slide deck   | `docs/submission/deck.pdf`            |

## Repository Structure

```
.
├── app.py                   # Gradio sandbox (HuggingFace Space)
├── DataSet/                 # candidates.jsonl (LFS), job_description.txt, validate_submission.py
├── docs/                    # Diátaxis docs — see docs/README.md
├── scripts/                 # eval.py, test_generalization.py, download_model.py, export_deck_pdf.py, sync_space.py
├── src/                     # Core engine
│   ├── config.py            # Weights, taxonomies, behavioral bounds, seniority profiles
│   ├── ranker.py            # Min-heap O(N log K) orchestration + semantic prefill
│   ├── reasoning.py         # Deterministic rank-tier explanation strings
│   ├── logging_config.py    # Structured JSON observability
│   ├── parsers/             # jd_parser, candidate_parser
│   ├── scorers/             # Title, skills, semantic, experience, location, behavioral
│   └── detectors/           # Honeypot detection
├── tests/                   # Pytest suite (56 tests)
├── Dockerfile               # Runtime + baked MiniLM for offline ranking
├── docker-compose.yml       # Sandbox and CLI services
├── rank.py                  # CLI entrypoint (two-pass stream)
├── submission.csv           # Track 1 submission output
└── submission_metadata.yaml # Portal metadata
```
