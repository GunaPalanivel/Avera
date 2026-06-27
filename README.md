# Avera

Deterministic candidate ranking for the Redrob **Intelligent Candidate Discovery** challenge (Track 01).

Ranks candidates from a JSONL pool against a job description using JD-calibrated scorers, behavioral signals, and honeypot detection — CPU-only, no hosted LLM calls.

**Status:** Early development — repository and contributor workflow only. Ranking CLI not yet available.

## Built for

- [India Runs](https://hack2skill.com/event/india_runs) — Redrob AI hackathon on Hack2skill
- [Redrob](https://redrob.io/) — India's AI platform for hiring, talent, and professional workflows

## Track 01 — Intelligent Candidate Discovery

Part of **The Data & AI Challenge** track. The problem: keyword filters miss candidates whose fit shows up in context, career trajectory, and behavioral signals—not just title matches.

**Mission:** Build a workable proof of concept that **ranks**, not just filters—a system that acts like a sharp recruiter:

- **Deep job understanding** — interpret nuanced job descriptions
- **Contextual relevance** — semantic fit beyond keywords
- **Signal integration** — profile attributes, career metadata, and activity/behavioral signals
- **Output** — a fast, accurate top-100 shortlist from the released candidate pool

No fixed architecture required; evaluators care about methodology, reproducibility, and results.

## Dataset

Track 01 challenge files live in [`DataSet/`](DataSet/). The full pool is `DataSet/candidates.jsonl` (~465 MB, **Git LFS**).

```bash
git lfs install
git lfs pull
```

See [`DataSet/README.md`](DataSet/README.md) for file descriptions and validation commands.

## Quick start

Not yet available. After **foundation & CI** lands:

```bash
pip install -r requirements.txt
python rank.py --health
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for branching, PR process, and CI requirements.

## License

MIT — see [LICENSE](LICENSE).
