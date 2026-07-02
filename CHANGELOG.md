# Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Domain-branching taxonomy (ADR-17): `detect_domain`, `get_title_tiers`, `get_skill_taxonomy`, and DevOps title/skill tables so non-AI/ML JDs rank on domain-appropriate signals
- Behavioral signal coverage: `profile_completeness_score` and `applications_submitted_30d` folded into the availability multiplier
- Counterfactual notes on top-tier reasoning so rank 1-5 explanations are not uniformly positive
- `AVERA_SEMANTIC_BATCH` and `AVERA_SEMANTIC_RERANK_TOPK` environment overrides
- README blueprint: methodology, technical choices, system architecture, why Avera is built this way
- Two-pass streaming pipeline: batch semantic prefill (`prefill_semantic_stream`) + single-pass rank
- `scripts/eval.py` (honeypot rate, NDCG@10, optional `--benchmark`)
- `scripts/test_generalization.py` (AI/ML + DevOps JD, zero code edits)
- `DataSet/job_description_devops.txt` alternate JD fixture
- Seniority-aware scorer weights (`get_scorer_weights`) and dynamic JD parser fields
- Rank-tier honest reasoning in `src/reasoning.py`
- CI jobs: `mypy`, `docker-smoke`; integration runs generalization script
- `tests/test_ranking_determinism.py` SHA256 replay fixture
- Makefile targets: `eval`, `generalization`, `mypy`
- `docs/submission/portal_checklist.md`
- Structured pipeline logs: `trace_id`, `prefill_ms`, `latency_ms`, `seniority_level`
- `AVERA_REFERENCE_DATE` env for deterministic behavioral recency

### Changed

- Semantic layer is now a two-stage funnel: heuristic candidate generation then semantic rerank on the heuristic top-K only (`SEMANTIC_RERANK_TOPK`, default 5000), cutting a full 100K CPU run from about 43 minutes to about 6 minutes
- Semantic batch size default lowered to 128 and made configurable for host stability
- Semantic scorer no longer encodes on-demand after prefill (funnel invariant)
- Semantic gate tuned to `SEMANTIC_MIN_HEURISTIC_SCORE = 0.11`
- Documentation synced across README, walkthrough, methodology, architecture, deck, ADR-003
- Health check validates config import and JD must-have skills

### Added (unreleased)

- Career-trajectory scorer (`src/scorers/trajectory_scorer.py`) rewarding IC-to-lead progression and product-company experience while down-weighting consulting-only or research-only paths
- Education tier scorer (`src/scorers/education_scorer.py`) using institution tier and field relevance, wired into the seniority weight profiles
- Section-aware JD anti-requirement detection (`anti_requirements` on `JobRequirements`) with bounded penalties for title-chasers and CV/speech/robotics-without-NLP profiles the JD explicitly does not want
- Curated demo sample (`DataSet/sample_candidates_demo.jsonl`) built from real pool records, plus a one-click Gradio example, so the hosted sandbox shows a strong shortlist instead of a noisy arbitrary slice

### Reviewer fixes (unreleased)

- Candidate skills are now included in the semantic embedding text so skill-dense, thin-narrative profiles are represented fairly
- Bullet skill extraction allowlist broadened beyond DevOps (react, java, spark, sql, kafka, and more) so non-DevOps stacks are not silently dropped
- Generic (non-AI/ML, non-DevOps) JDs now inject no title or skill taxonomy instead of falling back to AI/ML
- Top-rank reasoning frames thin must-have coverage as intentional career-trajectory ranking aligned with the JD anti-keyword-stuffing guidance
- XLSX output cells now pass through `sanitize_cell` (ADR-16 parity with the CSV path)
- Score scale `[0, 1.3]` documented in README and methodology; behavioral applications bound justified
- Real primary contact details in `submission_metadata.yaml`
- Residual phase references removed from `.github/ISSUE_TEMPLATE/bug.md` and `CHANGELOG.md`

### Fixed (unreleased)

- Bullet skill extraction now matches tokens on word boundaries, so common substrings (`go` in "going"/"Google", `rust` in "trust") no longer leak into must-have skills and falsely match candidate skills like `MongoDB`, `Django`, or `Go`
- `scripts/eval.py` honeypot lookup now resolves the exact ranked ids across the full pool instead of only the first 100 rows
- Reasoning wording is now gated by absolute score (`STRONG_FIT_SCORE = 0.70`): a weak pool no longer yields an over-claimed "Top-tier" or "Strong match" top rank. Full-pool top-100 output is unchanged (all scores are well above the floor).
- Sandbox UI notes that shortlist quality reflects the uploaded slice; the production shortlist comes from the full 100K pool.

### Added (foundation)

- Foundation modules: `exceptions`, `path_validation`, `logging_config`, `config`, `models`, `parsers`
- Pydantic boundary models including `BehavioralSignals` (ADR-14)
- ADR-15 exception hierarchy with structured context fields
- Streaming JSONL candidate parser with 2GB file and 10MB line guards
- JD requirement loader (`jd_parser`) wired into `--health`
- Path validation for CLI input/output paths and upload filenames (ADR-16)
- Structured JSON logging with PII-safe extra fields (ADR-10)
- `rank.py` CLI with `--health`, path validation, and parse smoke mode
- Makefile targets: `help`, `install`, `lint`, `test`, `security`, `validate`
- CI pipeline: governance, lint, test, security, integration (bandit + pip-audit)
- CI `integration` job: parse smoke after test and security
- Determinism and perturbation tests; expanded `make validate`
- GitHub issue templates: bug, chore
- `docs/getting-started.md` install and health check guide
- Test coverage: path validation, models, parser guards, JD parser, logging, CLI

### Fixed

- Coerce dataset sentinel `-1` on `github_activity_score` and `offer_acceptance_rate` to `None` so real 100K JSONL parses

## [0.0.1] - 2026-06-27

### Added

- Challenge dataset under `DataSet/` (Git LFS for `candidates.jsonl`)
- Dataset README with clone and validation instructions

## [0.0.0] - 2026-06-27

### Added

- Initial repository structure and governance
- MIT license
