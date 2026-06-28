# Scoring Methodology

The Avera ranking engine implements a hybrid semantic + deterministic scoring system. Weights and logic are derived from the Track 1 Job Description (`idea/ProcessedData/docx_extracts/job_description.txt`).

## 1. Job Description Parsing & Understanding

The pipeline begins with a **JD Parser** that ingests the raw job description text. It extracts:

*   **Must-Have Skills**: Taxonomy-backed matches present in the JD (e.g., `embeddings`, `pinecone`, `sentence-transformers`, `python`).
*   **Nice-to-Have Skills**: Secondary skills (e.g., `lora`, `rag`, `xgboost`).
*   **Target Cities**: JD-named locations (Hyderabad, Pune, Mumbai, Delhi NCR, Noida, etc.).
*   **Raw Text**: Preserved for the semantic embedding layer.

Skill synonyms (e.g., `vector database` → `vector db`, `faiss`) expand matching without scoring on raw substring stuffing alone.

## 2. Feature Engineering & Weights

Base weights sum to **1.0**; behavioral is applied as a **multiplier** after the base sum.

| Scorer | Weight | Core Rationale (JD Derived) |
|--------|--------|-----------------------------|
| **Title & Career** | 35% | AI/ML title tiers and product-company trajectory over title-chasers; consulting-only careers penalized per JD red flags. |
| **Skills Credibility** | 25% | Must-have JD skills with synonym expansion; assessment scores weighted over self-reported proficiency. |
| **Semantic Fit** | 15% | `sentence-transformers` cosine similarity between JD text and candidate headline, summary, and `career_history` descriptions. |
| **Experience Fit** | 15% | ML/AI tenure in career history; step bands for total YOE aligned to the 5–9 year JD band. |
| **Location & Logistics** | 10% | Favors candidates in JD-named Indian cities. |
| **Behavioral Signals** | Multiplier (0.4×–1.3×) | Applied to final base score — see §3. |

## 3. Behavioral Multiplier

Behavioral signals answer: *is this candidate actually available and credible to recruiters?* Factors (from `redrob_signals`):

| Signal | Effect |
|--------|--------|
| Recruiter response rate &lt; 5% | Strong down-weight (ghosting) |
| Last active &gt; 6 months ago | Down-weight |
| Notice period ≤ 30 days | Up-weight |
| Interview completion rate | Up/down by threshold |
| Offer acceptance rate | Up/down by threshold |
| GitHub activity score ≥ 80 | Up-weight |
| Search appearances / saved by recruiters | Mild up-weight |
| Email + phone + LinkedIn verified | Mild up-weight |

Clamped to `[0.4, 1.3]` via `BEHAVIORAL_MODIFIER_MIN/MAX` in `src/config.py`.

## 4. Honeypot Detection Engine

The dataset contains honeypots designed to trick keyword-based matching. The engine applies filters **before** scoring:

| Method | Detection Logic | Result |
|--------|-----------------|--------|
| **Fictional Companies** | Companies like `Dunder Mifflin`, `Globex Inc`, `Acme Corp` at ingestion. | Pre-filter (score 0, skipped) |
| **Method 1: Title/Skill Mismatch** | Non-technical titles claiming many core AI skills. | Honeypot (dropped) |
| **Method 2: Expert Anomaly** | Expert proficiency on 3+ skills with 0 months duration. | Honeypot (dropped) |
| **Method 3: Impossible Seniority** | Senior title with &lt; 2 YOE, or junior title with &gt; 10 YOE. | Honeypot (dropped) |
| **Method 4: Unverified Generalist** | &gt; 15 skills, zero assessment scores (senior YOE exempt). | Honeypot (dropped) |

## 5. Dynamic Reasoning Generation

Reasoning is **deterministic** — no LLM in the output path.

1. **Extract verified facts**: title, company, YOE.
2. **Match must-have skills** against JD requirements.
3. **Construct sentence**: e.g., *"Strong fit: Lead AI Engineer at Razorpay with 6.7 YOE. Demonstrates deep expertise in Embeddings and Python."*
4. **Rank-tone variation**: top-5 vs borderline phrasing via `src/reasoning.py`.

## 6. Output Canary (ADR-16)

Before writing `submission.csv`, `validate_output_canary` enforces:

- Exactly **100** ranked rows for production runs
- Unique `candidate_id` values
- Every output ID present in the input pool processed for that run
