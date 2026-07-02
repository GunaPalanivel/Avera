# ADR 003: Hybrid Semantic + Deterministic Scoring Layer

## Context

Redrob Track 1 targets a **Senior AI Engineer** role. The hackathon JD states that matching candidates by AI keyword density is an explicit dataset trap. At the same time, the role requires production experience with **embeddings-based retrieval** — the same capability Redrob is hiring to build on top of their current BM25 + rule-based stack.

ADR 001 chose deterministic scorers for explainability and CPU budget. That left a gap: candidates who built recommendation or ranking systems at product companies may never list "RAG" or "Pinecone" in their skills section, yet are strong fits when their career narrative is read in context.

## Decision

Add a **Semantic Scorer** (25% base weight for senior JDs) using `sentence-transformers` (`all-MiniLM-L6-v2`):

1. **JD text** is encoded once at scorer init.
2. **Candidate text** is built from `profile.headline`, `profile.summary`, `career_history[].description`, and skill names.
3. **Cosine similarity** between JD and candidate embeddings is clamped to `[0, 1]` and multiplied by the scorer weight.
4. **Deterministic scorers** cover the remaining base score (title/career 18%, skills 14%, trajectory 14%, education 12%, experience 11%, location 6% for senior JDs) for bounded, auditable constraints. Pure keyword scorers (title + skills = 32%) sit below semantic + trajectory + education combined.
5. **Behavioral signals** remain a multiplicative modifier (0.4×–1.3×) applied after the base sum — availability is not blended into semantic similarity.
6. **Cross-encoder rerank (ADR-018)** nudges the shortlist order after the heap pass; see `src/rerank.py`.

### Performance: two-stage funnel + heuristic gate

Full 100K semantic encode exceeds the CPU time budget. Avera uses a candidate-generation then rerank funnel:

1. **Pass 1 — `prefill_semantic_stream()`**: stream candidates; compute the heuristic score (all scorers except semantic) for all; keep the survivors above `SEMANTIC_MIN_HEURISTIC_SCORE` (**0.11**), then batch-encode only the strongest `SEMANTIC_RERANK_TOPK` (default **5000**, deterministic selection). Batch size is `AVERA_SEMANTIC_BATCH` (default 128). Results cached by `candidate_id`.
2. **Pass 2 — `Ranker.rank()`**: single streaming pass; semantic scorer reads cache for reranked candidates, returns `0.0` otherwise and never encodes on-demand.

This mirrors production hybrid retrieval: **heuristic recall → dense rerank on the top-K**. Encoding about 5000 documents instead of every survivor cut a full 100K CPU run from about 43 minutes to about 6 minutes with no material change to the top-100 (semantic is at most 25% of the base score, so sub-top-K candidates cannot climb into the shortlist).

### Operational constraints

- Model loads lazily on first semantic score; skipped when `AVERA_SKIP_SEMANTIC=1` (unit tests) or JD text is empty.
- `AVERA_SEMANTIC_MODEL` env var points to a pre-downloaded local model directory for offline/Docker runs aligned with `has_network_during_ranking: false` in submission metadata.
- JD must-have skills are extracted via a **controlled taxonomy** scanned against `job_description.txt` — JD vocabulary extraction, not candidate keyword stuffing.
- Weights adjust by JD seniority via `get_scorer_weights()` — behavioral remains a separate multiplier.

## Consequences

- **Positive:** Captures "read between the lines" fit the JD asks for without putting an LLM in the ranking path.
- **Positive:** Aligns with Redrob's stated product direction (embeddings + hybrid retrieval).
- **Positive:** Career descriptions in `career_history` materially affect rank — not just headline keywords.
- **Positive:** Batch prefill + gate keeps 100K runs within hackathon CPU budget.
- **Negative:** First run downloads ~90 MB model unless cached locally; semantic pass still adds latency vs pure heuristics.
- **Negative:** MiniLM is English-centric; acceptable for this JD and dataset but not a production multilingual solution.
- **Negative:** Per-domain skill and title taxonomies are curated (AI/ML and DevOps today); domains beyond those fall back to generic until a table is added (see ADR-17).

## Related

- ADR 001: Min-heap and deterministic core
- ADR 002: Honeypot threat model (keyword traps)
- ADR 017: Domain-branching taxonomy
- `src/scorers/semantic_scorer.py`, `src/ranker.py`, `src/config.py` (`get_scorer_weights`, `SEMANTIC_MIN_HEURISTIC_SCORE`, `SEMANTIC_RERANK_TOPK`)
