#!/usr/bin/env python3
"""Pre-download the semantic and cross-encoder models for offline / air-gapped ranking runs."""

import os
from pathlib import Path

# Always pull from HuggingFace hub during download — never the local cache path.
HUB_MODEL_ID = os.environ.get("AVERA_SEMANTIC_HUB", "all-MiniLM-L6-v2")
DEFAULT_OUT = Path("models/all-MiniLM-L6-v2")
CROSS_ENCODER_HUB = os.environ.get("AVERA_CROSS_ENCODER_HUB", "cross-encoder/ms-marco-MiniLM-L-6-v2")
CROSS_ENCODER_OUT = Path("models/ms-marco-MiniLM-L-6-v2")


def main() -> None:
    out = Path(os.environ.get("AVERA_MODEL_OUT", str(DEFAULT_OUT)))
    out.mkdir(parents=True, exist_ok=True)

    from sentence_transformers import CrossEncoder, SentenceTransformer

    print(f"Downloading {HUB_MODEL_ID} to {out.resolve()}")
    SentenceTransformer(HUB_MODEL_ID).save(str(out))

    ce_out = Path(os.environ.get("AVERA_CROSS_ENCODER_OUT", str(CROSS_ENCODER_OUT)))
    ce_out.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {CROSS_ENCODER_HUB} to {ce_out.resolve()}")
    CrossEncoder(CROSS_ENCODER_HUB).save(str(ce_out))

    print("Done. Set these before ranking for offline runs:")
    print(f"  export AVERA_SEMANTIC_MODEL={out.resolve()}")
    print(f"  export AVERA_CROSS_ENCODER_MODEL={ce_out.resolve()}")


if __name__ == "__main__":
    main()
