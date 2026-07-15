# ADR 019: Education Scorer Weight Rationale

## Context

Post-CTO review questioned whether a 12% education weight was justified for a senior AI engineer JD that does not mention degree requirements. The education scorer uses institution tier and field relevance, but the JD emphasizes production retrieval experience, career trajectory, and semantic fit over pedigree.

## Decision

Reduce education weight from **12% to 8%** (Option A) and redirect the freed 4% to:

- **Semantic fit**: 25% → **27%** (honors the JD's "read between the lines" mandate)
- **Career trajectory**: 14% → **16%** (rewards IC-to-lead progression and product-company paths)

Behavioral scoring remains a separate multiplier; education does not double-count via behavioral signals.

Unknown or missing education tier scores **neutral** (mid-band), not penalized to zero, so candidates without listed degrees are not excluded.

## Consequences

- Positive: aligns weights with JD silence on education and strengthens narrative-fit signals.
- Positive: `CAND_0005538` (Adobe, ex-Google) recovered into the top-100 at rank 52 via vocabulary expansion without keyword stuffing.
- Negative: tier-1 pedigree provides slightly less lift; acceptable given weak JD prior on education.

## Related

- ADR 003: Hybrid semantic + deterministic layer
- `src/config.py` (`get_scorer_weights`, `SCORER_WEIGHTS`)
- `src/scorers/education_scorer.py`
