"""Embedding backend: sentence-transformers on CPU with deterministic offline fallback.

Primary: sentence-transformers/all-MiniLM-L6-v2 (80MB, CPU) per blueprint Sec 7.
Fallback keeps pilot/tests runnable without downloads; production must log model hash.
"""
from __future__ import annotations

import hashlib
import math
import os
from typing import List

import numpy as np


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (float(np.linalg.norm(a)) * float(np.linalg.norm(b))) or 1e-9
    return float(np.dot(a, b) / denom)


class EmbeddingBackend:
    def __init__(self, model_id: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_id = model_id
        self._model = None
        self._tried_load = False

    @property
    def model_hash(self) -> str:
        return hashlib.sha256(self.model_id.encode()).hexdigest()[:12]

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

    def embed(self, texts: List[str]) -> np.ndarray:
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
