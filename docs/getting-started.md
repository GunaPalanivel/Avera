# Getting started

## Install

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Health check

```bash
python rank.py --health
```

Expected output includes `[OK] avera foundation ready`.

## Parse a sample file

```bash
python rank.py --candidates tests/fixtures/sample.jsonl --limit 5
```

Full ranking and CSV output arrive in later milestones.
