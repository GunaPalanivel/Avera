# Scoring Methodology

The Avera ranking engine implements a **hybrid semantic + deterministic** scoring system. Weights and logic are derived from the bundled Track 1 job description ([`DataSet/job_description.txt`](../../DataSet/job_description.txt)) and adjust dynamically when the JD signals different seniority levels.

## 1. Job Description Parsing & Understanding

The pipeline begins with **`jd_parser.py`**, which ingests raw job description text and produces a `JobRequirements` object:

| Field                   | Extraction method                                                                     |
| ----------------------- | ------------------------------------------------------------------------------------- |
| **Must-have skills**    | Controlled taxonomy scanned against JD text (e.g. `embeddings`, `pinecone`, `python`) |
| **Nice-to-have skills** | Secondary taxonomy (e.g. `lora`, `rag`, `xgboost`)                                    |
| **Target cities**       | JD-named locations (Hyderabad, Pune, Mumbai, Delhi NCR, Noida, …)                     |
| **Seniority level**     | Detected from title/YOE cues (`junior`, `mid`, `senior`, `staff`, …)                  |
| **Title keywords**      | Dynamic tokens from JD headings and role lines                                        |
| **Raw text**            | Preserved for semantic embedding (full JD block)                                      |

Skill synonyms (e.g. `vector database` → `vector db`, `faiss`) expand matching without scoring on raw substring stuffing alone.

**Seniority-aware weights** — `get_scorer_weights(seniority_level)` in `src/config.py` shifts emphasis between title/career and skills for junior vs senior JDs. Behavioral scoring remains a separate multiplier in all profiles.

## 2. Feature Engineering & Weights

Default **senior/staff** profile (sums to **1.0**); behavioral is applied as a **multiplier** after the base sum.

| Scorer                   | Weight (senior JD)     | Core Rationale (JD Derived)                                                                                                   |
| ------------------------ | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Title & Career**       | 35%                    | AI/ML title tiers and product-company trajectory over title-chasers; consulting-only careers penalized per JD red flags.      |
| **Skills Credibility**   | 25%                    | Must-have JD skills with synonym expansion; assessment scores weighted over self-reported proficiency.                        |
| **Semantic Fit**         | 15%                    | `sentence-transformers` cosine similarity between JD text and candidate headline, summary, and `career_history` descriptions. |
| **Experience Fit**       | 15%                    | ML/AI tenure in career history; step bands for total YOE aligned to the JD band.                                              |
| **Location & Logistics** | 10%                    | Favors candidates in JD-named Indian cities.                                                                                  |
| **Behavioral Signals**   | Multiplier (0.4×–1.3×) | Applied to final base score — see §3.                                                                                         |

### Semantic performance gate

MiniLM encoding is expensive at 100K scale. Avera uses a **two-pass stream**:

1. **Pass 1 — batch prefill** (`prefill_semantic_stream`): candidates whose heuristic score (title + skills + experience + location, no semantic) ≥ `SEMANTIC_MIN_HEURISTIC_SCORE` (**0.11**) are batch-encoded (`batch_size=512`) with an embedding cache.
2. **Pass 2 — rank**: streaming single pass applies cached semantic vectors only to gate survivors; others receive semantic score `0.0`.

This is hybrid RAG-style retrieval: heuristic recall, semantic rerank on survivors — within CPU budget.

## 3. Behavioral Multiplier

Behavioral signals answer: _is this candidate actually available and credible to recruiters?_ Factors (from `redrob_signals`):

| Signal                                   | Effect                        |
| ---------------------------------------- | ----------------------------- |
| Recruiter response rate &lt; 5%          | Strong down-weight (ghosting) |
| Last active &gt; 6 months ago            | Down-weight                   |
| Notice period ≤ 30 days                  | Up-weight                     |
| Interview completion rate                | Up/down by threshold          |
| Offer acceptance rate                    | Up/down by threshold          |
| GitHub activity score ≥ 80               | Up-weight                     |
| Search appearances / saved by recruiters | Mild up-weight                |
| Email + phone + LinkedIn verified        | Mild up-weight                |

Clamped to `[0.4, 1.3]` via `BEHAVIORAL_MODIFIER_MIN/MAX` in `src/config.py`.

Recency calculations use `AVERA_REFERENCE_DATE` (default `2026-06-27`) for deterministic replay across environments.

## 4. Honeypot Detection Engine

The dataset contains honeypots designed to trick keyword-based matching. The engine applies filters **before** scoring:

| Method                              | Detection Logic                                                          | Result                        |
| ----------------------------------- | ------------------------------------------------------------------------ | ----------------------------- |
| **Fictional Companies**             | Companies like `Dunder Mifflin`, `Globex Inc`, `Acme Corp` at ingestion. | Pre-filter (score 0, skipped) |
| **Method 1: Title/Skill Mismatch**  | Non-technical titles claiming many core AI skills.                       | Honeypot (dropped)            |
| **Method 2: Expert Anomaly**        | Expert proficiency on 3+ skills with 0 months duration.                  | Honeypot (dropped)            |
| **Method 3: Impossible Seniority**  | Senior title with &lt; 2 YOE, or junior title with &gt; 10 YOE.          | Honeypot (dropped)            |
| **Method 4: Unverified Generalist** | &gt; 15 skills, zero assessment scores (senior YOE exempt).              | Honeypot (dropped)            |

Honeypot keywords in `honeypot_detector.py` are **trap detection**, not positive scoring features.

## 5. Dynamic Reasoning Generation

Reasoning is **deterministic** — no LLM in the output path (`src/reasoning.py`).

1. **Extract verified facts**: title, company, YOE, matched JD skills.
2. **Rank-tier templates**:
   - Ranks 1–5: top-tier framing; minor concerns if present.
   - Ranks 6–19: strong match with optional watch-items.
   - Ranks 20–49: solid/good-fit openers with explicit concerns.
   - Ranks 50–89: moderate/partial alignment with gap lists.
   - Ranks 90–100: lower-tier shortlist with key gaps.
3. **Concerns are profile-derived only**: skill gaps, low response rate, long notice, weak GitHub, YOE band mismatch — never invented credentials.

Example (rank 45): _"Competitive candidate: Senior ML Engineer at Razorpay (6.2 YOE); JD-aligned skills: embeddings, python. Concerns: low recruiter response rate."_

## 6. Output Canary (ADR-16)

Before writing `submission.csv`, `validate_output_canary` enforces:

- Exactly **100** ranked rows for production runs
- Unique `candidate_id` values
- Every output ID present in the input pool processed for that run

## 7. Evaluation

```bash
python scripts/eval.py              # honeypot rate in top-100, NDCG@10 (14-ID calibration fixture)
python scripts/eval.py --benchmark  # optional wall-clock on full pool
python scripts/test_generalization.py   # AI/ML + DevOps JD, zero code edits
```
