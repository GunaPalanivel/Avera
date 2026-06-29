#!/usr/bin/env python3
"""Pre-download the semantic model for offline / air-gapped ranking runs."""

import os
from pathlib import Path

# Always pull from HuggingFace hub during download — never the local cache path.
HUB_MODEL_ID = os.environ.get("AVERA_SEMANTIC_HUB", "all-MiniLM-L6-v2")
DEFAULT_OUT = Path("models/all-MiniLM-L6-v2")


def main() -> None:
    out = Path(os.environ.get("AVERA_MODEL_OUT", str(DEFAULT_OUT)))
    out.mkdir(parents=True, exist_ok=True)

    from sentence_transformers import SentenceTransformer

    print(f"Downloading {HUB_MODEL_ID} → {out.resolve()}")
    model = SentenceTransformer(HUB_MODEL_ID)
    model.save(str(out))
    print("Done. Set AVERA_SEMANTIC_MODEL to this path before ranking:")
    print(f"  export AVERA_SEMANTIC_MODEL={out.resolve()}")


if __name__ == "__main__":
    main()
