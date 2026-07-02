# Avera documentation

Diátaxis layout for the Track 1 ranking engine. The **[README](../README.md)** is the blueprint entry point: methodology, technical choices, system architecture, and why Avera is built this way.

## Tutorials & getting started

| Document                                                         | Purpose                                          |
| ---------------------------------------------------------------- | ------------------------------------------------ |
| [getting-started.md](getting-started.md)                         | Install, health check, smoke rank, validation    |
| [submission/walkthrough.md](submission/walkthrough.md)           | Full walkthrough, reproduction, portal checklist |
| [submission/portal_checklist.md](submission/portal_checklist.md) | Hack2skill + HF Space manual steps               |
| [submission/deck.md](submission/deck.md)                         | Slide deck source                                |
| [submission/deck.pdf](submission/deck.pdf)                       | Portal PDF deck (`make export-pdf`)              |

## Explanation (methodology & architecture)

| Document                                                   | Purpose                                                                    |
| ---------------------------------------------------------- | -------------------------------------------------------------------------- |
| [explanation/architecture.md](explanation/architecture.md) | Pipeline, two-pass stream, ADR summary, CI, observability                  |
| [explanation/methodology.md](explanation/methodology.md)   | Scorers, semantic gate, behavioral multiplier, honeypots, honest reasoning |

## How-to guides

| Document                               | Purpose                                                   |
| -------------------------------------- | --------------------------------------------------------- |
| [how-to/runbook.md](how-to/runbook.md) | Local ops, offline model, Docker sandbox, troubleshooting |

## Evaluation & generalization

| Script / target                     | Purpose                                                  |
| ----------------------------------- | -------------------------------------------------------- |
| `scripts/eval.py`                   | Honeypot rate in top-100, NDCG@10 on calibration fixture |
| `scripts/test_generalization.py`    | Same pipeline on AI/ML + DevOps JD — zero code edits     |
| `make eval` / `make generalization` | Makefile shortcuts                                       |

## Architecture decision records

| ADR                                                                                    | Topic                                      |
| -------------------------------------------------------------------------------------- | ------------------------------------------ |
| [adr/001-deterministic-min-heap-ranking.md](adr/001-deterministic-min-heap-ranking.md) | O(N log K) heap, streaming ingest          |
| [adr/002-honeypot-threat-modeling.md](adr/002-honeypot-threat-modeling.md)             | Adversarial dataset traps                  |
| [adr/003-semantic-hybrid-layer.md](adr/003-semantic-hybrid-layer.md)                   | MiniLM semantic layer + deterministic core |
| [adr/017-domain-branching-taxonomy.md](adr/017-domain-branching-taxonomy.md)             | Per-domain title/skill tables                |
| [adr/018-cross-encoder-rerank.md](adr/018-cross-encoder-rerank.md)                     | Cross-encoder shortlist rerank               |

## External

- **Sandbox:** https://huggingface.co/spaces/gp5901/avera-ranker
- **Repo:** https://github.com/GunaPalanivel/Avera
