# ADR 020: Industry-Aware Career Trajectory

## Context

Post-PR #30 merit tiebreak fixed score-ceiling ordering, but rank 1 still favored services-weighted careers (Genpact AI, CAND_0046525) over product-company retrieval engineers (Zomato, CAND_0018499). The trajectory scorer read `career_history[].industry` only for research/academia penalties; consulting detection used company-name lists instead of the dataset industry field.

Follow-up experiments (July 2026):

| Change                                | NDCG@10    | Recovery@10 | Rank 1                               |
| ------------------------------------- | ---------- | ----------- | ------------------------------------ |
| PR #30 baseline                       | 0.3718     | 3/4         | CAND_0046525 (Genpact)               |
| **Fix 1 - industry trajectory**       | **0.3980** | **3/4**     | **CAND_0018499 (Zomato)**            |
| Fix 1 + duration-weighted skill embed | 0.2731     | 1/4         | CAND_0068351 (Sarvam) - **reverted** |
| Fix 1 + aspiration phrase penalty     | 0.2731     | 1/4         | same regression - **reverted**       |
| Fix 1 + taxonomy expansion (ADR-021)  | 0.2503     | 2/4         | CAND_0018499 (Zomato) - **reverted** |

## Decision

Ship **Fix 1 only**: `PRODUCT_INDUSTRIES` / `SERVICES_INDUSTRIES` frozensets in `config.py`; duration-weighted `product_company_ratio()` in `trajectory_scorer.py` with bonus (ratio ≥ 0.7) and penalty (ratio < 0.4). Services-only careers penalized via `industry in SERVICES_INDUSTRIES`, not company-name substring matching.

**Not shipped:** duration-weighted skill repetition in `build_candidate_text()`, aspiration phrase penalties, and taxonomy expansion (ADR-021) - all regressed calibration metrics on the full 100K run despite passing unit tests.

## Consequences

- Positive: rank 1 aligns with product retrieval trajectory; NDCG@10 improved vs PR #30.
- Positive: industry classification scales to new companies without maintaining firm name lists for product bonus.
- Negative: curated industry taxonomy; unknown industries default to neutral 0.5 ratio.
- Deferred: duration-weighted embeddings, aspiration detection, and taxonomy expansion need safer calibration before reintroduction.

## Related

- ADR 018: Cross-encoder rerank
- ADR 019: Education / vocabulary expansion (CAND_0005538)
- ADR 021: Title tier and skill taxonomy expansion (evaluated and reverted)
- `src/config.py`, `src/scorers/trajectory_scorer.py`
