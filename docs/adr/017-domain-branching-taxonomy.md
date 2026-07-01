# ADR 017: Domain-Branching Title and Skill Taxonomy

## Context

Avera is positioned as a JD-agnostic product: any employer supplies a job description plus an applicant pool and receives a ranked shortlist. The initial implementation, however, hardcoded AI/ML title tiers (`AI_TITLE_TIERS`) and an AI/ML skill taxonomy in `src/config.py`. Running the same pipeline on a DevOps/SRE JD validated and produced 100 rows, but the top-100 contained zero DevOps, SRE, platform, or infrastructure titles: it surfaced AI/ML engineers who happened to list Kubernetes or Python. The engine was overfit to one domain, which undercuts the "works for any JD" product claim.

## Decision

Branch the domain-specific taxonomy by JD, keeping AI/ML as the default so existing behavior is unchanged.

1. `detect_domain(text_lower)` classifies a JD as `ai_ml`, `devops`, or `generic` by keyword prevalence.
2. `get_title_tiers(domain)` returns `DEVOPS_TITLE_TIERS` for DevOps JDs and `AI_TITLE_TIERS` otherwise.
3. `get_skill_taxonomy(domain)` returns the DevOps must/nice skill sets for DevOps JDs and the AI/ML sets otherwise.
4. `jd_parser.load_job_requirements` records `domain` on `JobRequirements` and selects the taxonomy accordingly; bullet-token skill extraction is retained.
5. `TitleCareerScorer` accepts a `title_tiers` table; `Ranker` injects `get_title_tiers(job_reqs.domain)`.

## Consequences

- **Positive:** A DevOps/SRE JD now surfaces infrastructure titles in the shortlist (0 to 97 infra titles in a full-pool top-100 check).
- **Positive:** Adding a new domain is a config table plus a keyword list, not a code change in the scorers.
- **Positive:** AI/ML JDs resolve to `ai_ml` and use the existing tables, so the Track 1 shortlist is unchanged.
- **Negative:** Domains beyond AI/ML and DevOps fall back to `generic` (AI/ML default tables) until a table is authored; this is honest partial coverage, not universal generalization.

## Related

- ADR 003: Hybrid semantic + deterministic layer
- `src/config.py` (`detect_domain`, `get_title_tiers`, `get_skill_taxonomy`, `DEVOPS_TITLE_TIERS`, `DEVOPS_SKILL_TAXONOMY_MUST/NICE`)
- `src/parsers/jd_parser.py`, `src/scorers/title_career_scorer.py`, `src/ranker.py`
