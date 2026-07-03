# Avera documentation

Diátaxis layout for the Track 1 ranking engine. Start with the **[README](../README.md)** for the product overview, then use the guides below to run, extend, or operate the codebase.

## Getting started

| Document | Purpose |
| -------- | ------- |
| [getting-started.md](getting-started.md) | Install, health check, smoke rank, full validation |
| [submission/walkthrough.md](submission/walkthrough.md) | End-to-end developer walkthrough: pipeline, outputs, evaluation |

## Explanation

| Document | Purpose |
| -------- | ------- |
| [explanation/architecture.md](explanation/architecture.md) | Pipeline, two-pass stream, ADRs, CI, observability |
| [explanation/methodology.md](explanation/methodology.md) | Scorers, semantic funnel, join probability, honeypots, reasoning |

## How-to

| Document | Purpose |
| -------- | ------- |
| [how-to/runbook.md](how-to/runbook.md) | Local ops, offline model, Docker sandbox, troubleshooting |

## Evaluation and generalization

| Script / target | Purpose |
| --------------- | ------- |
| `scripts/eval.py` | Honeypot rate, NDCG@10, Precision@5/10, Recovery@10 |
| `scripts/test_generalization.py` | Same pipeline on AI/ML + DevOps JD — zero code edits |
| `make eval` / `make generalization` | Makefile shortcuts |

## Architecture decision records

| ADR | Topic |
| --- | ----- |
| [adr/001-deterministic-min-heap-ranking.md](adr/001-deterministic-min-heap-ranking.md) | O(N log K) heap, streaming ingest |
| [adr/002-honeypot-threat-modeling.md](adr/002-honeypot-threat-modeling.md) | Adversarial dataset traps |
| [adr/003-semantic-hybrid-layer.md](adr/003-semantic-hybrid-layer.md) | MiniLM semantic layer + deterministic core |
| [adr/017-domain-branching-taxonomy.md](adr/017-domain-branching-taxonomy.md) | Per-domain title/skill tables |
| [adr/018-cross-encoder-rerank.md](adr/018-cross-encoder-rerank.md) | Cross-encoder shortlist rerank (min-max, no sigmoid) |
| [adr/019-education-scorer-rationale.md](adr/019-education-scorer-rationale.md) | Education weight reduced to 8% |

## External

- **Sandbox:** https://huggingface.co/spaces/gp5901/avera-ranker
- **Hackathon:** https://hack2skill.com/event/india_runs/
- **Repo:** https://github.com/GunaPalanivel/Avera
