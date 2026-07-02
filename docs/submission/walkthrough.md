# Avera Walkthrough — Track 1 Intelligent Candidate Discovery

**Team:** Avera DevOps + AI  
**Repo:** https://github.com/GunaPalanivel/Avera  
**Sandbox:** https://huggingface.co/spaces/gp5901/avera-ranker

---

## 1. What problem we solve

Redrob's Track 1 JD asks for candidates who match a **Senior AI Engineer** role — not candidates whose skills section contains the most AI keywords. The dataset embeds honeypots (marketing managers with perfect ML skill lists, fictional companies, impossible timelines).

Avera ranks 100,000 profiles and outputs the **top 100** with explainable reasoning, in one reproducible command.

---

## 2. Why Avera is built this way

| Design choice            | Reason                                                                                       |
| ------------------------ | -------------------------------------------------------------------------------------------- |
| Hybrid semantic + rules  | JD says keyword matching is a trap; embeddings read career narratives rules cannot           |
| Behavioral multiplier    | Hireability ≠ skill fit — ghosts with perfect profiles must not outrank available candidates |
| Two-pass stream          | Batch semantic prefill + streaming rank — CPU budget without materializing 100K scores       |
| No LLM in ranking path   | Explainable, deterministic, auditable output for judges and compliance                       |
| JD-parameterized product | Same `rank.py` on AI/ML and DevOps JD files — proves generalization, not a one-off script    |
| DevOps shell             | Docker offline model, CI (mypy, docker-smoke), structured logs — operable PoC                |

Full blueprint: [README.md](../../README.md) · [architecture.md](../explanation/architecture.md)

---

## 3. Architecture (30-second version)

```
JD file → jd_parser → JobRequirements (skills, cities, seniority)
JSONL stream → validate → fictional filter → honeypot detector
    → Pass 1: batch semantic prefill (heuristic gate ≥ 0.11)
    → Pass 2: 7 scorers + behavioral × → min-heap → cross-encoder rerank → rank-tier reasoning → CSV
```

| Stage         | Purpose                                                                                            |
| ------------- | -------------------------------------------------------------------------------------------------- |
| **Stage 1**   | Drop ~60% fictional companies (`Dunder Mifflin`, `Globex Inc`, …)                                  |
| **Stage 1.5** | Drop ~1,603 honeypot traps (title/skill mismatch, expert anomaly, …)                               |
| **Stage 2**   | Weighted base score: semantic 25%, title/career 18%, skills 14%, trajectory 14%, education 12%, experience 11%, location 6% (senior JD) |
| **Stage 2.5** | Behavioral multiplier 0.4×–1.3× (availability, GitHub, interviews, verifications)                |
| **Stage 3**   | Min-heap top-100, then cross-encoder rerank on shortlist pool (ADR-018)                          |
| **Output**    | ADR-16 canary: exactly 100 unique IDs, subset of input pool, defused CSV                           |

Deep dive: [architecture.md](../explanation/architecture.md) · [methodology.md](../explanation/methodology.md) · [ADR-003](../adr/003-semantic-hybrid-layer.md)

---

## 4. Why hybrid semantic + deterministic?

The JD explicitly states keyword matching is a trap. Pure BM25/keyword rankers promote honeypots.

We use **`sentence-transformers` (`all-MiniLM-L6-v2`)** to compare the full JD text against each candidate's headline, summary, and **`career_history` descriptions** — where real ranking/recommendation experience shows up even when skills omit "RAG" or "Pinecone."

Deterministic scorers enforce bounded constraints (YOE bands, JD cities, must-have skills with synonym expansion). Behavioral signals are a **multiplier**, not additive — a ghost profile with perfect skills still ranks down.

**Performance:** Semantic encoding runs in **Pass 1** as batch prefill only when the heuristic base score (all scorers except semantic) exceeds `SEMANTIC_MIN_HEURISTIC_SCORE` (**0.11** in `src/config.py`). Weak candidates skip embeddings; survivors use a cached vector in Pass 2. Batch size defaults to 128 (`AVERA_SEMANTIC_BATCH`).

---

## 5. Reproduce the submission (Stage 3)

### Prerequisites

- Python 3.11+
- `DataSet/candidates.jsonl` (Git LFS)
- ~16 GB RAM, CPU only

### One-command reproduction

```bash
pip install -r requirements.txt
python rank.py --candidates DataSet/candidates.jsonl --out submission.csv
python DataSet/validate_submission.py submission.csv
```

Or:

```bash
make validate-full
```

### Evaluation & generalization

```bash
python scripts/eval.py                    # honeypot rate, NDCG@10
python scripts/test_generalization.py     # AI/ML + DevOps JD, zero code edits
```

### Offline model (no network during ranking)

```bash
make download-model
# Linux/macOS:
export AVERA_SEMANTIC_MODEL=$PWD/models/all-MiniLM-L6-v2
# Windows PowerShell:
$env:AVERA_SEMANTIC_MODEL="$PWD\models/all-MiniLM-L6-v2"
python rank.py --candidates DataSet/candidates.jsonl --out submission.csv
```

Pre-computation (model download) is ~2 minutes once; ranking completes within the hackathon CPU budget.

---

## 6. Sandbox demo

**HuggingFace Space:** https://huggingface.co/spaces/gp5901/avera-ranker

Upload a `.jsonl` sample (1–100 rows). Output may be **fewer than upload rows** after filters (e.g. 48/100). This is **not** portal `submission.csv` (100 rows from the full 100K pool).

The Gradio UI:

1. Validates the upload filename (no path traversal)
2. Runs `python rank.py --candidates <upload> --limit <N> --out submission.csv`
3. Shows a results table and a **Download submission.csv** button

Bundled JD: `DataSet/job_description.txt` (override with `--jd`).

**Local sandbox smoke** (mirrors HF behavior):

```bash
python -c "
from pathlib import Path
import app
class F: name = str(Path('tests/fixtures/sample.jsonl').resolve())
rows, log, csv_path = app.rank_candidates(F)
assert rows and csv_path
print(log)
"
```

**Docker sandbox** (offline model baked in):

```bash
make docker-build && make docker-sandbox
```

---

## 7. Scoring weights (defensible vs JD)

Senior/staff JD profile (default for bundled `job_description.txt`):

| Component        | Weight    | JD anchor                                                  |
| ---------------- | --------- | ---------------------------------------------------------- |
| Semantic fit     | 25%       | "Read between the lines" — production retrieval experience |
| Title & career   | 18%       | Career trajectory; anti title-chaser; consulting penalty   |
| Skills           | 14%       | Embeddings, vector DB, Python, evaluation frameworks       |
| Career trajectory| 14%       | IC-to-lead progression; product-company experience         |
| Education        | 12%       | Institution tier and degree-field relevance                |
| Experience       | 11%       | 5–9 year band; applied ML tenure                           |
| Location         | 6%        | Pune, Hyderabad, Mumbai, Delhi NCR                         |
| Behavioral       | ×0.4–×1.3 | Down-weight unavailable / low response candidates          |

Weights adjust by JD seniority via `get_scorer_weights()` in `src/config.py` (validated at import).

---

## 8. Honeypot strategy

Honeypot keywords in `honeypot_detector.py` are **intentional trap detection**, not positive scoring. We detect:

- Non-tech titles claiming 5+ core AI skills
- Expert skills with 0 months duration
- Impossible seniority bands
- Unverified generalists (15+ skills, 0 assessments)

Fictional companies are zero-scored before the heap — they never consume a top-100 slot.

---

## 9. Explainable reasoning

`src/reasoning.py` produces **rank-tier** strings — no LLM:

- Top 5: strength-focused with optional minor notes
- Ranks 6–89: explicit concerns (skill gaps, response rate, notice period, GitHub)
- Ranks 90–100: lower-tier framing with key gaps

Every claim traces to parsed profile fields — no invented credentials.

---

## 10. CI / DevOps signals

```bash
make ci    # ruff + pytest + bandit + pip-audit + integration smoke
make mypy  # static type check
```

GitHub Actions: `governance` → `lint` → `test` + `security` + `mypy` → `integration` (smoke rank + generalization) → `docker-smoke`.

Structured JSON logging with `trace_id`, `latency_ms`, `prefill_ms`. CSV output uses `defusedcsv` (OWASP A03). Docker + docker-compose for sandbox parity.

---

## 11. AI tools declaration

Gemini and Claude/Cursor were used for architecture planning and code review. **No candidate records were sent to any LLM.** Ranking and reasoning are fully deterministic.

---

## 12. Portal artifacts checklist

| Artifact         | Path                                                                                          |
| ---------------- | --------------------------------------------------------------------------------------------- |
| CSV submission   | `submission.csv` (rename to participant ID for portal)                                        |
| XLSX submission  | `submission.xlsx` (local only — do not upload to portal)                                      |
| Metadata         | `submission_metadata.yaml`                                                                    |
| This walkthrough | `docs/submission/walkthrough.md`                                                              |
| Portal steps     | `docs/submission/portal_checklist.md`                                                         |
| Slide deck (PDF) | `docs/submission/deck.pdf` (source: `docs/submission/deck.md`; regenerate: `make export-pdf`) |

---

## 13. Known limits & future work

- MiniLM is English-centric; Redrob's multilingual roadmap would need a multilingual encoder.
- Skill taxonomy is AI/ML-biased; non-AI JDs lean more on semantic + JD bullet extraction until taxonomy expands.
- Calibration fixture has 14 labeled IDs; target 20 for stronger NDCG confidence.
- Production scale (900M index, cross-encoder rerank, LTR) is roadmap — not PoC scope.

These are documented tradeoffs (ADR-003), not hidden shortcuts.
