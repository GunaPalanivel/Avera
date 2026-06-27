# Avera

High-throughput, deterministic candidate ranking engine for the Redrob Track 01 Challenge. 
Processes 100K+ JSONL profiles with strict Pydantic boundaries to score JD fit, career trajectory, and behavioral signals with zero hallucination risk.

## Architecture (Up to Phase 2)

Avera uses a deterministic weighted scoring system over LLM-based parsing, heavily optimizing for speed and deterministic reasoning. The system is built for the Redrob Senior AI Engineer job description.

### The Pipeline

1. **Boundary Validation (Pydantic)**
   The 100K `candidates.jsonl` dataset is streamed line-by-line and strictly validated against Pydantic models. Malformed rows are gracefully skipped, preventing pipeline crashes. The `-1` sentinel for missing behavioral data is safely coerced.

2. **Honeypot & Fictional Company Filter**
   Fast-fail filters eliminate fictional companies (e.g., Stark Industries) and keyword-stuffed traps (Marketing Managers with AI skills) instantly before any scoring logic executes.

3. **Deterministic Scoring Engine**
   Five independent scorers calculate a composite score, strictly weighted according to the Redrob JD parameters:
   * **Title & Career Scorer (35%)**: Prioritizes Product/AI roles over consulting, severely penalizing title-chasers averaging <1.5 years per role.
   * **Behavioral Scorer (25%)**: Down-weights low recruiter response rates and long inactivity. Max points for <30 days notice period.
   * **Skills Scorer (20%)**: Emphasizes embeddings, vector DBs, and evaluation metrics. Verified skill assessments get a 3x multiplier over self-reported skills.
   * **Experience Scorer (10%)**: Optimal band at 5-9 years experience.
   * **Location Scorer (10%)**: Preferred geofence in Noida/Pune or explicit willingness to relocate.

4. **O(K) Memory Ranker**
   Scores are fed into a Min-Heap of size `K=100`, bounding memory usage while instantly sorting the top 100 candidates from the 100K stream.

### Quick Start

```bash
# Run tests and linting
make test
make lint

# Run the ranking pipeline on the full dataset
make rank
# Alternatively:
python rank.py --candidates DataSet/candidates.jsonl
```

## DevOps & Security

Avera is built with a dual-role mindset (AI Engineering + DevOps). It features:
* **Structured JSON Logging**: Every pipeline event is logged in a machine-readable format.
* **Graceful Degradation**: 5-level custom exception hierarchy (DataError, ScoringError, etc.).
* **Security Scanning**: Integrated `pip-audit` and `bandit` in CI/CD.
