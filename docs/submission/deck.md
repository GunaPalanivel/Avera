# Avera — Track 1 Ranking Engine

### Redrob India Runs · Intelligent Candidate Discovery

---

## The trap Redrob built into the dataset

> _"The right answer is not find candidates whose skills section contains the most AI keywords."_

- Marketing managers with perfect ML skill lists
- Fictional companies (60% of pool)
- Behavioral ghosts — perfect on paper, unavailable in practice

---

## Our thesis

**Hybrid semantic + deterministic ranking**

- Embeddings capture career narrative fit
- Rules enforce JD constraints (YOE, cities, honeypots)
- Behavioral multiplier for hireability

---

## Pipeline

```
100K JSONL → validate → filter fiction → detect honeypots
→ score (5 dimensions) → behavioral × → heap top-100 → reasoning → CSV
```

O(N log K) memory · Streaming ingest · CPU-only

---

## Scorer weights (JD-backed)

| Title & career | **35%** |
| Skills | **25%** |
| Semantic (MiniLM) | **15%** |
| Experience | **15%** |
| Location | **10%** |
| Behavioral | **×0.4–×1.3** |

---

## Semantic layer (ADR-003)

**Model:** `all-MiniLM-L6-v2`

**Candidate text:** headline + summary + `career_history` descriptions

**Not used:** raw skill keyword density (honeypot vector)

---

## Honeypot defense

1. Fictional company pre-filter
2. Title / skill mismatch
3. Expert-with-zero-months anomaly
4. Impossible seniority
5. Unverified generalist

---

## DevOps / SRE signals

- GitHub Actions: lint · test · security · integration
- Makefile one-command CI
- Structured JSON logs + run_id
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
- Built for **India scale** — 100K in minutes on CPU

**Repo:** github.com/GunaPalanivel/Avera  
**Sandbox:** huggingface.co/spaces/gp5901/avera-ranker

---

_PDF deck: `docs/submission/deck.pdf` — regenerate with `make export-pdf`._
