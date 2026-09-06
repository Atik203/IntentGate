"""Statistical reporting (blueprint Sec 9): bootstrap 95% CI + paired McNemar."""
from __future__ import annotations

import numpy as np


def bootstrap_ci(values: list[float], n_resamples: int = 1000, alpha: float = 0.05) -> tuple[float, float]:
    v = np.asarray(values, dtype=float)
    rng = np.random.default_rng(0)
    means = [rng.choice(v, size=len(v), replace=True).mean() for _ in range(n_resamples)]
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def mcnemar(b1: list[bool], ours: list[bool]) -> tuple[float, float]:
    """Paired per-case: b1/ours are 'attack succeeded' booleans. Returns (statistic, p)."""
    a = int(np.sum(np.asarray(b1) & ~np.asarray(ours)))  # B1 failed, ours protected
    b = int(np.sum(~np.asarray(b1) & np.asarray(ours)))  # B1 protected, ours failed
    # TODO(Gate 3): implement exact binomial p (and continuity correction) - scipy optional.
    return float(a + b), float(a)  # placeholder count pair; refine before paper use
