# Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

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
- GitHub issue templates: bug, phase work, chore
- `docs/getting-started.md` install and health check guide
- Test coverage: path validation, models, parser guards, JD parser, logging, CLI

### Changed

- Health check validates config import and JD must-have skills

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
