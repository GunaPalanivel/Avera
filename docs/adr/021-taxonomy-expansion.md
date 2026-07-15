# ADR 021: Title Tier and Skill Taxonomy Expansion

## Context

Post-PR #31 Fix 1 (industry-aware trajectory, ADR-020), analysis of the PRO
expert ideal top-10 showed several expected candidates missing from the top-100
because titles like "Applied Scientist" and "Recommendation Systems Engineer"
were absent from `AI_TITLE_TIERS`, and BM25 / learning-to-rank sat only in
`SKILL_TAXONOMY_NICE`.

## Decision

**Evaluated and reverted.** Expand taxonomy tables without changing scoring
formulas was tried on the full 100K pool:

- Added Applied Scientist / Recommendation Systems Engineer title tiers
- Promoted `bm25` and `learning to rank` into `SKILL_TAXONOMY_MUST`
- Added RecSys-adjacent skills to `SKILL_TAXONOMY_NICE`

| Change | NDCG@10 | Recovery@10 | Rank 1 |
| ------ | ------- | ----------- | ------ |
| Fix 1 only (ADR-020) | **0.3980** | **3/4** | CAND_0018499 (Zomato) |
| Fix 1 + taxonomy expansion | 0.2503 | 2/4 | CAND_0018499 (Zomato) - **reverted** |

Widening recognition surfaced some PRO ideal candidates (e.g. Meta Applied
Scientist into top-100) but increased top-of-list competition and dropped one
of the four tracked calibration ideals out of the top 10. Net calibration
regressed.

## Consequences

- Positive: experiment confirms title/skill table coverage matters for
  RecSys and Applied Scientist profiles.
- Negative: naive expansion diluted Recovery@10 under the current weight
  scheme; not safe to ship before July 22 without a better calibration set.
- Deferred: targeted title/skill additions need a held-out PRO ranking fixture
  and NDCG hold vs Fix 1 before reintroduction.

## Related

- ADR 020: Industry-aware trajectory (Fix 1 shipped; this ADR is follow-up,
  reverted)
- `src/config.py` - `AI_TITLE_TIERS`, `SKILL_TAXONOMY_MUST`, `SKILL_TAXONOMY_NICE`
