# Developer walkthrough

End-to-end guide for running, evaluating, and extending the Avera ranking engine. For install steps see [getting-started.md](../getting-started.md). For ADR detail see [architecture.md](../explanation/architecture.md) and [methodology.md](../explanation/methodology.md).

**Repo:** https://github.com/GunaPalanivel/Avera  
**Sandbox:** https://huggingface.co/spaces/gp5901/avera-ranker

---

## 1. Problem and approach

Redrob Track 1 ([India Runs](https://hack2skill.com/event/india_runs/)) asks for a **Senior AI Engineer** shortlist from 100K profiles — not a keyword-density leaderboard. The dataset embeds honeypots (marketing managers with perfect ML skills, fictional companies, impossible timelines).

Avera is a **hybrid semantic + deterministic** ranker: embeddings read career narratives; rules enforce YOE, skills, cities, and traps; behavioral signals modulate hireability; output is explainable without LLM calls in the ranking path.

---

## 2. Pipeline (30 seconds)

```
JD file → jd_parser → JobRequirements (skills, cities, seniority, domain)
JSONL stream → validate → fictional filter → honeypot detector (5 methods)
    → Pass 1: heuristic gate + semantic prefill on top-K survivors
    → Pass 2: 7 scorers + behavioral × → min-heap → cross-encoder rerank (min-max)
    → join probability (informational) + rank-tier reasoning → CSV + XLSX
```

| Stage         | Purpose                                                                                                                                   |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Stage 1**   | Drop ~60% fictional companies                                                                                                             |
| **Stage 1.5** | Drop honeypots (title/skill mismatch, expert anomaly, impossible seniority, multi-domain expert trap, unverified generalist)              |
| **Stage 2**   | Base score (senior JD): semantic **27%**, title/career 18%, trajectory **16%**, skills 14%, experience 11%, education **8%**, location 6% |
| **Stage 2.5** | Behavioral multiplier 0.4×–1.3×                                                                                                           |
| **Stage 3**   | Min-heap top-100, cross-encoder rerank on shortlist pool (ADR-018, min-max logits)                                                        |
| **Output**    | CSV (4 cols) + XLSX (5 cols with `join_probability`); ADR-16 canary validation                                                            |

---

## 3. Reproduce locally

```bash
pip install -r requirements.txt
make download-model   # optional; required for offline / Docker parity
python rank.py --candidates DataSet/candidates.jsonl --out submission.csv
python DataSet/validate_submission.py submission.csv
```

Heuristic-only fast path: `python rank.py --fast --candidates DataSet/candidates.jsonl --out submission_fast.csv`

Or: `make validate-full`

### Evaluation

```bash
python scripts/eval.py
# honeypot rate, NDCG@10, Precision@5/10, Recovery@10 (4 real calibration IDs)
# July 2026: NDCG@10 0.3718, Recovery@10 3/4, honeypot rate 0.0

python scripts/test_generalization.py   # AI/ML + DevOps JD, zero code edits
make ci                                 # lint + test + security + smoke rank
```

All written `score` values are clamped to `[0.0, 1.0]` after cross-encoder rerank.

Calibration fixture: `tests/fixtures/calibration_batch.json` (4 real ideal candidates).

---

## 4. Output contract

| File              | Columns                                      | Notes                                                                        |
| ----------------- | -------------------------------------------- | ---------------------------------------------------------------------------- |
| `submission.csv`  | `candidate_id`, `rank`, `score`, `reasoning` | Organizer validator expects exactly 4 columns                                |
| `submission.xlsx` | above + `join_probability`                   | Informational hireability score; also embedded in reasoning for top-20 ranks |

Join probability uses offer acceptance, interview completion, notice period, open-to-work, response rate, response time, work mode, and relocation — not profile views or endorsements.

---

## 5. Sandbox demo

**HuggingFace:** https://huggingface.co/spaces/gp5901/avera-ranker

Upload a `.jsonl` slice (1–100 rows). Bundled examples: 100-row curated demo or 50-row quick demo.

**Local:**

```bash
python app.py
# or
make docker-sandbox
```

---

## 6. Scoring weights (senior JD)

| Component         | Weight    | Notes                                               |
| ----------------- | --------- | --------------------------------------------------- |
| Semantic fit      | 27%       | MiniLM + narrative cosine floor; see ADR-003        |
| Title & career    | 18%       | Domain title tiers; anti-requirement penalties      |
| Career trajectory | 16%       | Progression and product-company paths               |
| Skills            | 14%       | Synonyms, adjacencies, recency-weighted self-report |
| Experience        | 11%       | YOE and ML tenure bands                             |
| Education         | 8%        | Weak prior; unknown tier neutral (ADR-019)          |
| Location          | 6%        | JD cities; remote/hybrid floor boost                |
| Behavioral        | ×0.4–×1.3 | Separate from join probability                      |

Weights live in `src/config.py` (`get_scorer_weights`) and adjust by JD seniority.

---

## 7. Key env vars

See [`.env.example`](../../.env.example) and [runbook.md](../how-to/runbook.md).

| Variable                                    | Purpose                                    |
| ------------------------------------------- | ------------------------------------------ |
| `--fast` (CLI flag)                         | Heuristic-only ranking; sets skip semantic + CE |
| `AVERA_SKIP_SEMANTIC` / `AVERA_SKIP_RERANK` | Fast path for tests and sandbox slices     |
| `AVERA_SEMANTIC_MODEL`                      | Local MiniLM directory for offline ranking |
| `AVERA_SEMANTIC_RERANK_TOPK`                | Heuristic top-K to embed (default 5000)    |
| `AVERA_REFERENCE_DATE`                      | Deterministic behavioral recency anchor    |

---

## 8. Extending the engine

| Task                             | Where to look                                                      |
| -------------------------------- | ------------------------------------------------------------------ |
| New skill synonyms / adjacencies | `src/config.py` (`SKILL_SYNONYMS`, `SKILL_ADJACENCIES`)            |
| New JD domain                    | `detect_domain`, `get_title_tiers`, `get_skill_taxonomy` (ADR-017) |
| Honeypot rules                   | `src/detectors/honeypot_detector.py`                               |
| Scorer weights                   | `get_scorer_weights()` in `src/config.py`                          |
| Reasoning templates              | `src/reasoning.py`                                                 |

---

## 9. Known limits

- MiniLM is English-centric; multilingual production would need a different encoder.
- Skill taxonomy is curated per domain (AI/ML, DevOps); other domains fall back to generic.
- Cross-encoder alpha and pool size are hand-tuned, not learned-to-rank.
- Learned skill-adjacency graphs and BM25+RRF hybrid retrieval are deferred (see README roadmap).

These are documented tradeoffs in ADR-003 and ADR-018, not hidden shortcuts.
