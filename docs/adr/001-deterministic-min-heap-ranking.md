# ADR 001: Deterministic Min-Heap Ranking over LLM Inference

## Context
When building a candidate ranking system for 100,000 resumes, the initial inclination in modern AI engineering is often to use an LLM for zero-shot ranking or a Vector Database for semantic similarity search. However, evaluating candidates strictly against a Job Description involves objective, deterministic factors (e.g., specific YOE boundaries, location constraints) that LLMs often hallucinate or fail to strictly bound.

## Decision
We chose a **Deterministic Scoring Engine** combined with a **Min-Heap (Priority Queue)** for extraction.
1. **Pydantic Validation**: All incoming JSONL data is strictly parsed to enforce schema compliance.
2. **Modular Scorers**: Individual components (Title, Location, Skills, Behavioral) assign weighted numeric values.
3. **O(N log K) Min-Heap**: Instead of storing 100,000 records in memory and sorting them `O(N log N)`, we maintain a Min-Heap of size `K=100`. 

## Consequences
- **Positive:** Latency is drastically reduced. We can parse, score, and rank 100,000 records in ~16 seconds using less than 150MB of RAM.
- **Positive:** Explainability. Every candidate's score is a mathematically traceable sum, eliminating the "black box" nature of LLM ranking.
- **Negative:** We lose the ability to perform fuzzy semantic matching on unstructured text blocks without explicitly coding heuristic parsers (e.g., regex for "NDCG" or "RAG" in summaries). *Addressed in ADR-003 via the Semantic Scorer on career narrative text.*
