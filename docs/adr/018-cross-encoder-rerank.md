# ADR 018: Cross-Encoder Rerank on the Shortlist

## Context

The bi-encoder semantic scorer (ADR-003) gives fast, pool-independent similarity but is a weak precision signal on its own. The review flagged the absence of a cross-encoder reranker, the industry-standard precision layer, as the top algorithmic gap. A cross-encoder scores a JD and a candidate together in one pass, which is far more precise than comparing two independent embeddings, but it is too expensive to run on the whole pool.

## Decision

Add a cross-encoder rerank stage that runs only on full ranking passes, after the heap produces a shortlist pool.

1. On a full pass the heap keeps a pool of `RERANK_POOL_SIZE` (default 300) instead of just the top 100.
2. `CrossEncoderReranker` (`src/rerank.py`) scores each pool candidate against the JD with `cross-encoder/ms-marco-MiniLM-L-6-v2` and **min-max normalizes** logits to `[0,1]` (no sigmoid: sigmoid re-compresses already-clustered logits into a narrow band).
3. The blend is additive and bounded: `final = min(1.0, base + RERANK_ALPHA * ce_norm)` (default alpha 0.15). Because the cross-encoder term is non-negative and capped, the output stays in IR convention `[0, 1]`, monotonic when re-sorted, tie-breaks by ascending `candidate_id`, and never drops a candidate below the reasoning floor.
4. The final top 100 is taken from the reranked pool.

## Operational constraints

- Runs only when `require_exact_count` is true (the full CLI pass), so the sandbox `--limit` path and CI stay fast and add no second model.
- Skipped when `AVERA_SKIP_SEMANTIC` or `AVERA_SKIP_RERANK` is set, and degrades gracefully to the base order if the model cannot load.
- Baked for offline runs by `scripts/download_model.py` and the `Dockerfile` (`AVERA_CROSS_ENCODER_MODEL`), preserving `has_network_during_ranking: false`.

## Consequences

- Positive: precision lift on the shortlist, the review's top gap, with a bounded, auditable blend that cannot destabilize the validated output (honeypot rate stays 0, monotonic, above the floor).
- Positive: opt-out via env keeps tests, CI, and the demo unaffected.
- Negative: a second offline model (~80MB) and a few extra seconds of CPU on the full pass.
- Negative: alpha and pool size are hand-tuned, not learned; documented as future LTR work.

## Related

- ADR 003: Hybrid semantic + deterministic layer
- `src/rerank.py`, `src/ranker.py`, `src/config.py` (`RERANK_POOL_SIZE`, `RERANK_ALPHA`, `CROSS_ENCODER_MODEL_NAME`)
