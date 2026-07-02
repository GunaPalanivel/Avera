# Avera — Track 1 Ranking Engine

### Redrob India Runs · Intelligent Candidate Discovery

---

## The trap Redrob built into the dataset

> _"The right answer is not find candidates whose skills section contains the most AI keywords."_

- Marketing managers with perfect ML skill lists
- Fictional companies (60% of pool)
- Behavioral ghosts — perfect on paper, unavailable in practice

---

## Why we built it this way

**Product, not a script** — JD-parameterized engine any employer can point at a new `job_description.txt`.

**Hybrid, not pure ML** — embeddings for narrative fit; rules for YOE, cities, honeypots.

**Operable** — Docker offline model, CI, structured logs, runbook.

**Honest** — rank-tier reasoning with concerns; generalization demo on two JDs.

---

## Our thesis

**Hybrid semantic + deterministic ranking**

- Embeddings capture career narrative fit (not skill-keyword density)
- Rules enforce JD constraints (YOE, cities, honeypots)
- Behavioral multiplier for hireability (×0.4–×1.3)

---

## Pipeline

```
100K JSONL → validate → filter fiction → detect honeypots
→ Pass 1: batch semantic prefill (gate ≥ 0.11)
→ Pass 2: score (7 dimensions) → behavioral × → heap → cross-encoder rerank → reasoning → CSV
```

O(N log K) memory · Two-pass streaming · CPU-only

---

## Scorer weights (JD-backed, senior profile)

| Semantic (MiniLM) | **25%** |
| Title & career | **18%** |
| Skills | **14%** |
| Career trajectory | **14%** |
| Education | **12%** |
| Experience | **11%** |
| Location | **6%** |
| Behavioral | **×0.4–×1.3** |

Seniority-aware via `get_scorer_weights()` — shifts emphasis for junior vs senior JDs.

---

## Semantic layer (ADR-003)

**Model:** `all-MiniLM-L6-v2`

**Candidate text:** headline + summary + `career_history` descriptions

**Gate:** heuristic ≥ 0.11 → batch encode (`batch_size=512`)

**Not used:** raw skill keyword density (honeypot vector)

---

## Honeypot defense

1. Fictional company pre-filter
2. Title / skill mismatch
3. Expert-with-zero-months anomaly
4. Impossible seniority
5. Unverified generalist

---

## Generalization proof

```bash
python scripts/test_generalization.py
```

Same `rank.py` · AI/ML JD + DevOps alt JD · zero code edits

---

## DevOps / SRE signals

- GitHub Actions: lint · test · security · mypy · integration · docker-smoke
- Makefile one-command CI
- Structured JSON logs (`trace_id`, `latency_ms`, `prefill_ms`)
- defusedcsv · Docker · HF sandbox
- Runbook for Day-2 ops

---

## Reproduce in one command

```bash
python rank.py --candidates DataSet/candidates.jsonl --out submission.csv
python DataSet/validate_submission.py submission.csv
```

Offline: `make download-model` → set `AVERA_SEMANTIC_MODEL`

---

## Why us for Redrob

- Thinks like **Senior AI Engineer** (embeddings, ranking theory, honeypot reasoning)
- Ships like **DevOps/SRE** (CI, observability, security, reproducibility)
- Built for **India scale** — 100K on CPU with honest latency claims

**Repo:** github.com/GunaPalanivel/Avera  
**Sandbox:** huggingface.co/spaces/gp5901/avera-ranker

---

_PDF deck: `docs/submission/deck.pdf` — regenerate with `make export-pdf`._
