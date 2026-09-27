"""Statistical reporting (blueprint Sec 9): bootstrap 95% CI + paired McNemar."""
from __future__ import annotations

from math import comb, erfc, sqrt

import numpy as np


def bootstrap_ci(
    values: list[float],
    n_resamples: int = 10000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, float]:
    """Percentile bootstrap CI of the mean (seeded, deterministic)."""
    v = np.asarray(values, dtype=float)
    if v.size == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, v.size, size=(n_resamples, v.size))
    means = v[indices].mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def exact_binomial_p(k: int, n: int) -> float:
    """Two-sided exact binomial p-value for H0: p=0.5 (McNemar exact test)."""
    if n == 0:
        return 1.0
    probabilities = [comb(n, i) for i in range(n + 1)]
    observed = probabilities[k]
    p = sum(prob for prob in probabilities if prob <= observed) / (2 ** n)
    return float(min(1.0, p))


def mcnemar(b1: list[bool], ours: list[bool], correction: bool = False) -> dict:
    """Paired McNemar for per-case 'attack succeeded' booleans (B1 vs ours).

    Counts discordant pairs (b = B1 only, c = ours only). Uses the exact two-sided
    binomial test when b + c < 25, otherwise chi-square (optional Yates correction).
    Returns counts, statistic, p-value and method used.
    """
    if len(b1) != len(ours):
        raise ValueError("b1 and ours must be paired (same length)")
    a = np.asarray(b1, dtype=bool)
    b = np.asarray(ours, dtype=bool)
    b1_only = int(np.sum(a & ~b))  # B1 attack succeeded, ours protected
    ours_only = int(np.sum(~a & b))  # ours failed where B1 protected
    discordant = b1_only + ours_only
    result = {
        "b1_only": b1_only,
        "ours_only": ours_only,
        "n_pairs": len(b1),
        "discordant": discordant,
    }
    if discordant == 0:
        result.update({"statistic": 0.0, "p_value": 1.0, "method": "no_discordant_pairs"})
        return result
    if discordant < 25:
        result.update(
            {
                "statistic": float(min(b1_only, ours_only)),
                "p_value": exact_binomial_p(min(b1_only, ours_only), discordant),
                "method": "exact_binomial",
            }
        )
        return result
    delta = abs(b1_only - ours_only) - (1.0 if correction else 0.0)
    statistic = max(0.0, delta) ** 2 / discordant
    p_value = erfc(sqrt(statistic / 2.0))
    result.update(
        {
            "statistic": float(statistic),
            "p_value": float(p_value),
            "method": "chi2_yates" if correction else "chi2",
        }
    )
    return result
