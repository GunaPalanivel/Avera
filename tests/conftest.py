import os

# Keep unit tests fast and offline — semantic model loads only in integration/full runs.
os.environ.setdefault("AVERA_SKIP_SEMANTIC", "1")
