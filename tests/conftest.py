"""Test-wide defaults: keep CI/tests fast by skipping the heavy embedding model."""
from __future__ import annotations

import os

os.environ.setdefault("INTENT_GATE_OFFLINE_EMBEDDINGS", "1")
