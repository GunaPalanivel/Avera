# Avera Walkthrough — Track 1 Intelligent Candidate Discovery

**Team:** Avera DevOps + AI  
**Repo:** https://github.com/GunaPalanivel/Avera  
**Sandbox:** https://huggingface.co/spaces/GunaPalanivel/avera-ranker  

---

## 1. What problem we solve

Redrob's Track 1 JD asks for candidates who match a **Senior AI Engineer** role — not candidates whose skills section contains the most AI keywords. The dataset embeds honeypots (marketing managers with perfect ML skill lists, fictional companies, impossible timelines).

Avera ranks 100,000 profiles and outputs the **top 100** with explainable reasoning, in one reproducible command.

---

## 2. Architecture (30-second version)

```
JSONL stream → Pydantic validate → Fictional filter → Honeypot detector
    → 5 base scorers (title, skills, semantic, experience, location)
    → Behavioral multiplier → Min-heap top-100 → Reasoning → CSV + XLSX
```

| Stage | Purpose |
|-------|---------|
| **Stage 1** | Drop ~60% fictional companies (`Dunder Mifflin`, `Globex Inc`, …) |
| **Stage 1.5** | Drop ~1,603 honeypot traps (title/skill mismatch, expert anomaly, …) |
| **Stage 2** | Weighted base score: title 35%, skills 25%, semantic 15%, experience 15%, location 10% |
| **Stage 3** | Behavioral multiplier 0.4×–1.3× (availability, GitHub, interviews, verifications) |
| **Output** | ADR-16 canary: exactly 100 unique IDs, subset of input pool, defused CSV |

Deep dive: [architecture.md](../explanation/architecture.md) · [methodology.md](../explanation/methodology.md) · [ADR-003](../adr/003-semantic-hybrid-layer.md)

---

## 3. Why hybrid semantic + deterministic?

The JD explicitly states keyword matching is a trap. Pure BM25/keyword rankers promote honeypots.

We use **`sentence-transformers` (`all-MiniLM-L6-v2`)** to compare the full JD text against each candidate's headline, summary, and **`career_history` descriptions** — where real ranking/recommendation experience shows up even when skills omit "RAG" or "Pinecone."

Deterministic scorers enforce bounded constraints (YOE bands, JD cities, must-have skills with synonym expansion). Behavioral signals are a **multiplier**, not additive — a ghost profile with perfect skills still ranks down.

**Performance:** Semantic encoding runs only when the heuristic base score (title + skills + experience + location) exceeds `SEMANTIC_MIN_HEURISTIC_SCORE` (0.06 in `src/config.py`). Weak candidates skip the embedding step so 100K ranking stays within the CPU budget.

---

## 4. Reproduce the submission (Stage 3)

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

## 5. Sandbox demo

**HuggingFace Space:** Upload a `.jsonl` sample (≤100 rows). The Gradio UI runs:

```bash
python rank.py --jd <bundled-jd> --candidates <upload> --out submission.csv
```

For local smoke:

```bash
python rank.py --candidates tests/fixtures/sample.jsonl --limit 1 --out ci_submission.csv
```

---

## 6. Scoring weights (defensible vs JD)

| Component | Weight | JD anchor |
|-----------|--------|-----------|
| Title & career | 35% | "Career trajectory > skill lists"; anti title-chaser |
| Skills | 25% | Embeddings, vector DB, Python, evaluation frameworks |
| Semantic | 15% | "Read between the lines" — production retrieval experience |
| Experience | 15% | 5–9 year band; applied ML tenure |
| Location | 10% | Pune, Hyderabad, Mumbai, Delhi NCR |
| Behavioral | ×0.4–×1.3 | Down-weight unavailable / low response candidates |

Weights live in `src/config.py` and are validated at import (`sum == 1.0`).

---

## 7. Honeypot strategy

Honeypot keywords in `honeypot_detector.py` are **intentional trap detection**, not positive scoring. We detect:

- Non-tech titles claiming 5+ core AI skills
- Expert skills with 0 months duration
- Impossible seniority bands
- Unverified generalists (15+ skills, 0 assessments)

Fictional companies are zero-scored before the heap — they never consume a top-100 slot.

---

## 8. CI / DevOps signals

```bash
make ci    # ruff + pytest + bandit + pip-audit + integration smoke
```

GitHub Actions: lint → test → security → integration (smoke rank on fixture).

Structured JSON logging with `run_id` for traceability. CSV output uses `defusedcsv` (OWASP A03). Docker + docker-compose for sandbox parity.

---

## 9. AI tools declaration

Gemini was used for architecture planning and code review. **No candidate records were sent to any LLM.** Ranking and reasoning are fully deterministic.

---

## 10. Portal artifacts checklist

| Artifact | Path |
|----------|------|
| CSV submission | `submission.csv` |
| XLSX submission | `submission.xlsx` (auto-generated alongside CSV) |
| Metadata | `submission_metadata.yaml` |
| This walkthrough | `docs/submission/walkthrough.md` |
| Slide deck (export to PDF) | `docs/submission/deck.md` |

---

## 11. Known limits & future work

- MiniLM is English-centric; Redrob's multilingual roadmap would need a multilingual encoder.
- Semantic encoding is per-candidate on CPU; batching would further reduce latency.
- JD skill extraction uses a controlled taxonomy scanned against JD text — not generative NLP parse.

These are documented tradeoffs (ADR-003), not hidden shortcuts.
