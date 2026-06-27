# Contributing to Avera

Two-person team project. All changes to `main` go through pull requests.

**Maintainer / approver:** [@GunaPalanivel](https://github.com/GunaPalanivel)  
**Second contributor:** TBD (add GitHub handle when known)

## Prerequisites

- Python 3.11+ (3.13 OK locally; CI uses 3.11)
- Git

## Branch workflow

1. Pull latest `main`
2. Create a branch: `feat/short-description`, see internal `poc_process.md` (not in repo)
3. One milestone of work per PR when possible
4. Push and open a PR to `main`
5. CI green + maintainer approval, then merge

Examples: `feat/candidate-parser`, `fix/path-validation`, `spike/calibration-weights`

No ticket IDs in branch names.

## Pull requests

- Fill in the PR template
- Do not commit secrets or `idea/` paths

## Commit messages

```
<type>: <imperative summary>

<body only if reasoning isn't obvious from the diff>
```

Examples:

```
feat: add behavioral scorer with recency decay
fix: reject path traversal in CLI input path
spike: compare weights on calibration batch
docs: add scoring methodology page
```

No `(scope)`. No DCO/Signed-off-by.

## Code comments

- Comment **why**, not what
- No step-number scaffolding or boilerplate docstrings
- `# TODO: … fine for POC scale` is fine, name the corner you cut

## CI

Every PR runs GitHub Actions (see [.github/workflows/ci.yml](.github/workflows/ci.yml)):

- **governance** — required files, issue templates, `idea/` not tracked, application layout
- **lint** — `ruff check` and `ruff format --check`
- **test** — `pytest` and `python rank.py --health`
- **security** — `bandit` on `src/` and `pip-audit` on dependencies

## Code style

- Python 3.11+ type hints where practical
- `ruff` for lint and format (added with foundation & CI)
- Structured JSON logging in application code, no bare `print()` in `src/`

## Questions

Open a PR draft or issue on GitHub. Maintainer reviews all merges.
