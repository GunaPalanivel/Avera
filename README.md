# Avera

Deterministic candidate ranking for the Redrob **Intelligent Candidate Discovery** challenge (Track 01).

Ranks candidates from a JSONL pool against a job description using JD-calibrated scorers, behavioral signals, and honeypot detection — CPU-only, no hosted LLM calls.

**Status:** Early development — repository and contributor workflow only. Ranking CLI not yet available.

**Repository:** https://github.com/GunaPalanivel/Avera

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
