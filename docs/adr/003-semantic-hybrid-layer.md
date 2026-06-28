# ADR 003: Hybrid Semantic + Deterministic Scoring Layer

## Context

Redrob Track 1 targets a **Senior AI Engineer** role. The hackathon JD states that matching candidates by AI keyword density is an explicit dataset trap. At the same time, the role requires production experience with **embeddings-based retrieval** — the same capability Redrob is hiring to build on top of their current BM25 + rule-based stack.

ADR 001 chose deterministic scorers for explainability and CPU budget. That left a gap: candidates who built recommendation or ranking systems at product companies may never list "RAG" or "Pinecone" in their skills section, yet are strong fits when their career narrative is read in context.

## Decision

Add a **Semantic Scorer** (15% base weight) using `sentence-transformers` (`all-MiniLM-L6-v2`):

1. **JD text** is encoded once at scorer init.
2. **Candidate text** is built from `profile.headline`, `profile.summary`, and every `career_history[].description` (not the skills list).
3. **Cosine similarity** between JD and candidate embeddings is clamped to `[0, 1]` and multiplied by the scorer weight.
4. **Deterministic scorers** retain the majority of the base score (title 35%, skills 25%, experience 15%, location 10%) for bounded, auditable constraints.
5. **Behavioral signals** remain a multiplicative modifier (0.4×–1.3×) applied after the base sum — availability is not blended into semantic similarity.

### Operational constraints

- Model loads lazily on first semantic score; skipped when `AVERA_SKIP_SEMANTIC=1` (unit tests) or JD text is empty.
- `AVERA_SEMANTIC_MODEL` env var points to a pre-downloaded local model directory for offline/Docker runs aligned with `has_network_during_ranking: false` in submission metadata.
- JD must-have skills are extracted via a **controlled taxonomy** scanned against `job_description.txt` — this is JD vocabulary extraction, not candidate keyword stuffing.

## Consequences

- **Positive:** Captures "read between the lines" fit the JD asks for without putting an LLM in the ranking path.
- **Positive:** Aligns with Redrob's stated product direction (embeddings + hybrid retrieval).
- **Positive:** Career descriptions in `career_history` materially affect rank — not just headline keywords.
- **Negative:** First run downloads ~90 MB model unless cached locally; full 100K semantic encode adds latency vs pure heuristics.
- **Negative:** MiniLM is English-centric; acceptable for this JD and dataset but not a production multilingual solution.

## Related

- ADR 001: Min-heap and deterministic core
- ADR 002: Honeypot threat model (keyword traps)
- `src/scorers/semantic_scorer.py`, `src/config.py` (`SCORER_WEIGHTS`)
