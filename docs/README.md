# Avera documentation

Diátaxis layout for the Track 1 ranking engine.

## Tutorials & getting started

| Document                                               | Purpose                                          |
| ------------------------------------------------------ | ------------------------------------------------ |
| [getting-started.md](getting-started.md)               | Install, health check, smoke rank, validation    |
| [submission/walkthrough.md](submission/walkthrough.md) | Full walkthrough, reproduction, portal checklist |
| [submission/deck.md](submission/deck.md)               | Slide deck source                                |
| [submission/deck.pdf](submission/deck.pdf)             | Portal PDF deck (`make export-pdf`)              |

## Explanation

| Document                                                   | Purpose                                                  |
| ---------------------------------------------------------- | -------------------------------------------------------- |
| [explanation/architecture.md](explanation/architecture.md) | Pipeline, ADR summary, exception hierarchy               |
| [explanation/methodology.md](explanation/methodology.md)   | Scorers, behavioral multiplier, honeypots, output canary |

## How-to guides

| Document                               | Purpose                                                   |
| -------------------------------------- | --------------------------------------------------------- |
| [how-to/runbook.md](how-to/runbook.md) | Local ops, offline model, Docker sandbox, troubleshooting |

## Architecture decision records

| ADR                                                                                    | Topic                                      |
| -------------------------------------------------------------------------------------- | ------------------------------------------ |
| [adr/001-deterministic-min-heap-ranking.md](adr/001-deterministic-min-heap-ranking.md) | O(N log K) heap, streaming ingest          |
| [adr/002-honeypot-threat-modeling.md](adr/002-honeypot-threat-modeling.md)             | Adversarial dataset traps                  |
| [adr/003-semantic-hybrid-layer.md](adr/003-semantic-hybrid-layer.md)                   | MiniLM semantic layer + deterministic core |

## External

- **Sandbox:** https://huggingface.co/spaces/gp5901/avera-ranker
- **Repo:** https://github.com/GunaPalanivel/Avera
