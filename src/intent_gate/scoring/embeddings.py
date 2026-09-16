"""Embedding backend: sentence-transformers on CPU with deterministic offline fallback.

Primary: sentence-transformers/all-MiniLM-L6-v2 (80MB, CPU) per blueprint Sec 7.
Fallback keeps pilot/tests runnable without downloads; production must log model hash.
"""
from __future__ import annotations

import hashlib
import math
import os

import numpy as np


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (float(np.linalg.norm(a)) * float(np.linalg.norm(b))) or 1e-9
    return float(np.dot(a, b) / denom)


class EmbeddingBackend:
    def __init__(self, model_id: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_id = model_id
        self._model = None
        self._tried_load = False
        self._hash: str | None = None

    @property
    def model_hash(self) -> str:
        """Functional model digest (probe embedding) or deterministic fallback digest."""
        if self._hash is None:
            self._hash = self._compute_hash()
        return self._hash

    @property
    def metadata(self) -> dict:
        """Run-level provenance logged with every trace (blueprint Sec 8)."""
        self._ensure()
        return {
            "model_id": self.model_id,
            "model_hash": self.model_hash,
            "backend": "sentence-transformers" if self._model is not None else "hash-fallback",
        }

    def _compute_hash(self) -> str:
        self._ensure()
        if self._model is not None:
            probe = np.asarray(
                self._model.encode(["intent-gate-probe"], show_progress_bar=False), dtype=float
            )
            return hashlib.sha256(probe.tobytes()).hexdigest()[:12]
        return hashlib.sha256(f"{self.model_id}:hash-fallback".encode()).hexdigest()[:12]

    def _ensure(self):
        if self._tried_load:
            return
        self._tried_load = True
        if os.getenv("INTENT_GATE_OFFLINE_EMBEDDINGS") == "1":
            self._model = None
            return
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_id)
        except Exception:
            self._model = None  # offline fallback

    def embed(self, texts: list[str]) -> np.ndarray:
        self._ensure()
        if self._model is not None:
            vecs = self._model.encode(texts, normalize_embeddings=False, show_progress_bar=False)
            return np.asarray(vecs, dtype=float)
        return np.asarray([_hash_embed(t) for t in texts], dtype=float)


def _hash_embed(text: str, dim: int = 64) -> np.ndarray:
    """Deterministic char-ngram hash embedding (offline fallback only, not for paper numbers)."""
    vec = np.zeros(dim, dtype=float)
    toks = text.lower().split()
    for tok in toks:
        h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0
    n = math.sqrt(float((vec**2).sum())) or 1.0
    return vec / n
