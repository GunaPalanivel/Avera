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

Skill synonyms (e.g. `embeddings` → `vector representations`, `vector database` → `pgvector`) and curated **skill adjacencies** (e.g. `pinecone` ↔ `weaviate`, `milvus`) expand matching without scoring on raw substring stuffing alone. Adjacent skills earn partial credit (0.7× assessed, 0.35× self-reported).

**Seniority-aware weights** — `get_scorer_weights(seniority_level)` in `src/config.py` shifts emphasis between title/career and skills for junior vs senior JDs. Behavioral scoring remains a separate multiplier in all profiles.

**Domain branching (ADR-17)** — `detect_domain` classifies each JD as `ai_ml`, `devops`, or `generic` by keyword prevalence. `get_title_tiers(domain)` and `get_skill_taxonomy(domain)` then select the appropriate title tier table and skill taxonomy, so a DevOps or SRE JD ranks on infrastructure titles and skills rather than AI/ML ones. AI/ML remains the default, so existing AI/ML behavior is unchanged.

## 2. Feature Engineering & Weights

Default **senior/staff** profile (sums to **1.0**); behavioral is applied as a **multiplier** after the base sum.

| Scorer                   | Weight (senior JD)     | Core Rationale (JD Derived)                                                                                                                                                             |
| ------------------------ | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Semantic Fit**         | 27%                    | `sentence-transformers` cosine similarity between JD text and candidate headline, summary, `career_history` descriptions, and skills. Raised to honor the JD's beyond-keywords mandate. |
| **Title & Career**       | 18%                    | Domain-appropriate title tiers (AI/ML or DevOps); consulting-only careers penalized; bounded penalties for JD-named anti-requirements (title-chasers, CV/speech/robotics without NLP).  |
| **Skills Credibility**   | 14%                    | Must-have JD skills with synonym and adjacency expansion; assessment scores weighted over self-reported proficiency with recency decay on duration.                                                                                  |
| **Career Trajectory**    | 16%                    | Rewards IC-to-lead progression and product-company experience; down-weights consulting-only and research-only paths.                                                                    |
| **Education**            | 8%                     | Weak prior: institution tier (tier_1..tier_4) and degree-field relevance; unknown tier neutral (ADR-019).                                                                                                                           |
| **Experience Fit**       | 11%                    | ML/AI tenure in career history; step bands for total YOE aligned to the JD band.                                                                                                        |
| **Location & Logistics** | 6%                     | Favors candidates in JD-named Indian cities; remote/hybrid work mode earns a floor boost for flexible tier-2 talent.                                                                                                                                            |
| **Behavioral Signals**   | Multiplier (0.4×–1.3×) | Applied to final base score — see §3.                                                                                                                                                   |

Weights are the senior/staff profile in `get_scorer_weights`; junior and mid profiles shift emphasis but keep the same scorers. Pure keyword scorers (title + skills = 32%) now sit below the semantic, trajectory, and education signals combined.

### Cross-encoder rerank (ADR-018)

On a full ranking pass, after the heap yields a shortlist pool (`RERANK_POOL_SIZE`, default 300), a cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) re-scores JD vs candidate and nudges the order with a bounded additive blend (`final = base + 0.15 * ce_norm`). Logits are min-max normalized to `[0,1]` without sigmoid recompression (ADR-018). This preserves monotonicity and the reasoning floor, is baked for offline runs, and is skipped in the sandbox and CI.

### Semantic performance gate and funnel

MiniLM encoding is expensive at 100K scale. Avera uses a **two-stage funnel**:

1. **Pass 1 — heuristic candidate generation + prefill** (`prefill_semantic_stream`): every candidate is scored on the heuristic base (all scorers except semantic). Candidates clearing `SEMANTIC_MIN_HEURISTIC_SCORE` (**0.11**) are the survivor set; only the strongest **`SEMANTIC_RERANK_TOPK`** of them (default **5000**, deterministic selection) are batch-encoded. Batch size is configurable via `AVERA_SEMANTIC_BATCH` (default 128) for host stability.
2. **Pass 2 — rank**: streaming single pass applies cached semantic vectors to the reranked top-K; everyone else receives semantic score `0.0`. After prefill the scorer never encodes on-demand (funnel invariant).

This is hybrid RAG-style retrieval: heuristic recall, semantic rerank on the top-K only. Encoding roughly 5000 documents instead of every survivor cuts a full 100K CPU run from about 43 minutes to about 6 minutes. A candidate below the heuristic top-K cannot realistically reach the final top-100 because semantic contributes at most 25% of the base score, so the shortlist is effectively unchanged. Raise `AVERA_SEMANTIC_RERANK_TOPK` to trade latency for recall margin.

## 3. Behavioral Multiplier

Behavioral signals answer: _is this candidate actually available and credible to recruiters?_ Factors (from `redrob_signals`):

| Signal                                   | Effect                         |
| ---------------------------------------- | ------------------------------ |
| Recruiter response rate &lt; 5%          | Strong down-weight (ghosting)  |
| Last active &gt; 6 months ago            | Down-weight                    |
| Notice period ≤ 30 days                  | Up-weight                      |
| Interview completion rate                | Up/down by threshold           |
| Offer acceptance rate                    | Up/down by threshold           |
| GitHub activity score ≥ 80               | Up-weight                      |
| Search appearances / saved by recruiters | Mild up-weight                 |
| Email + phone + LinkedIn verified        | Mild up-weight                 |
| Profile completeness (≥ 90 / &lt; 40)    | Mild up-weight / down-weight   |
| Applications submitted in 30d (1–20)     | Mild up-weight (active intent) |

The applications bound is `1 <= applications_submitted_30d <= 20`: below 1 is passive, above 20 in 30 days signals spray-and-pray, so neither extreme earns the availability boost.

Clamped to `[0.4, 1.3]` via `BEHAVIORAL_MODIFIER_MIN/MAX` in `src/config.py`.

**Join probability** (informational, does not change rank): a separate `[0, 1]` score from offer acceptance, interview completion, notice period, open-to-work, recruiter response rate, response time, preferred work mode (remote/hybrid), and willingness to relocate. Profile views, connection count, and endorsements are excluded. Reported in XLSX (5th column) and embedded in reasoning for top-20 ranks; CSV stays 4 columns for organizer validation.

Recency calculations use `AVERA_REFERENCE_DATE` (default `2026-06-27`) for deterministic replay across environments.

### Score scale

The base score sums to `[0, 1]` (semantic 0.27 + title/career 0.18 + skills 0.14 + trajectory 0.16 + education 0.08 + experience 0.11 + location 0.06, each scorer bounded to its weight). The behavioral multiplier is bounded to `[0.4, 1.3]`, so the final written `score` lies in `[0, 1.3]`. A value above 1.0 therefore means a strong base fit further lifted by strong availability signals; it is not an error. Scores are only meaningful as a ranking order, not as a percentage.

## 4. Honeypot Detection Engine

The dataset contains honeypots designed to trick keyword-based matching. The engine applies filters **before** scoring:

| Method                              | Detection Logic                                                          | Result                        |
| ----------------------------------- | ------------------------------------------------------------------------ | ----------------------------- |
| **Fictional Companies**             | Companies like `Dunder Mifflin`, `Globex Inc`, `Acme Corp` at ingestion. | Pre-filter (score 0, skipped) |
| **Method 1: Title/Skill Mismatch**  | Non-technical titles claiming many core AI skills.                       | Honeypot (dropped)            |
| **Method 2: Expert Anomaly**        | Expert proficiency on 3+ skills with 0 months duration.                  | Honeypot (dropped)            |
| **Method 3: Impossible Seniority**  | Senior title with &lt; 2 YOE, or junior title with &gt; 10 YOE.          | Honeypot (dropped)            |
| **Method 4: Multi-Domain Expert**   | Expert/advanced in 3+ disjoint domains (CV, NLP, speech, robotics) with thin duration and no assessment backing; exempt senior YOE with NLP/IR exposure. | Honeypot (dropped)            |
| **Method 5: Unverified Generalist** | &gt; 15 skills, zero assessment scores (senior YOE exempt).              | Honeypot (dropped)            |

Honeypot keywords in `honeypot_detector.py` are **trap detection**, not positive scoring features.

## 5. Dynamic Reasoning Generation

Reasoning is **deterministic** — no LLM in the output path (`src/reasoning.py`).

1. **Extract verified facts**: title, company, YOE, matched JD skills.
2. **Rank-tier templates**:
   - Ranks 1–5: top-tier framing; a minor concern when present, otherwise an explicit counterfactual ("trails a perfect match on N uncovered JD skills", "no GitHub signal to corroborate depth") so no top entry reads as uniformly positive.
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
