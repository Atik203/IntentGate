"""Statistical reporting (blueprint Sec 9): bootstrap 95% CI + paired McNemar.

Phase 6 additions (P1 stats discipline):
- power_analysis: post-hoc power for two-proportion z-test
- bonferroni_alpha: adjusts significance threshold for multiple comparisons
- per_specificity_fpr: FPR stratified by contract specificity level
"""
from __future__ import annotations

from math import comb, erfc, exp, log, sqrt

import numpy as np


def _normal_cdf(x: float) -> float:
    """Standard normal CDF via error function (no scipy needed)."""
    return 0.5 * (1.0 + _erf(x / sqrt(2.0)))


def _erf(x: float) -> float:
    """Error function via Abramowitz & Stegun approximation (7.1.26)."""
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    sign = 1.0 if x >= 0 else -1.0
    x = abs(x)
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * exp(-x * x)
    return sign * y


def _norm_ppf(p: float) -> float:
    """Inverse normal CDF (percent point function) via rational approximation.

    Acklam's algorithm — no scipy dependency. Accurate to ~1e-9.
    """
    if p <= 0.0:
        return float("-inf")
    if p >= 1.0:
        return float("inf")
    a = [-3.969683028665376e+01, 2.209460984245205e+02,
         -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822309e+01, 1.615858368580409e+02,
         -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068133141820e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01,
         2.445134137142996e+00, 3.754470714500752e+00]
    plow = 0.02425
    phigh = 1 - plow
    if p < plow:
        q = sqrt(-2 * log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > phigh:
        q = sqrt(-2 * log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


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


def power_analysis(n: int, p1: float, p2: float, alpha: float = 0.05) -> dict:
    """Post-hoc power analysis for two-proportion z-test (Phase 6 P1 stats discipline).

    Computes the statistical power of detecting a difference between p1 (baseline rate)
    and p2 (treatment rate) with n samples per group, at significance level alpha.

    Uses the normal approximation:
      power = Phi(z_alpha/2 + sqrt(n) * |p1 - p2| / sqrt(p_bar*(1-p_bar)*2))

    where p_bar = (p1 + p2) / 2 and z_alpha/2 is the critical value.

    Args:
        n: Sample size per group (assumes equal groups)
        p1: Baseline proportion (e.g., B1 ASR rate)
        p2: Treatment proportion (e.g., Ours ASR rate)
        alpha: Significance level (default 0.05)

    Returns:
        Dict with n, p1, p2, delta, alpha, power, and whether power >= 0.8
    """
    if n <= 0:
        return {"n": n, "p1": p1, "p2": p2, "power": 0.0, "sufficient_power": False}
    delta = abs(p1 - p2)
    p_bar = (p1 + p2) / 2.0
    if p_bar == 0 or p_bar == 1:
        return {"n": n, "p1": p1, "p2": p2, "delta": delta, "alpha": alpha,
                "power": 1.0 if delta > 0 else 0.0, "sufficient_power": delta > 0}
    se = sqrt(p_bar * (1 - p_bar) * 2.0 / n)
    if se == 0:
        return {"n": n, "p1": p1, "p2": p2, "delta": delta, "alpha": alpha,
                "power": 1.0 if delta > 0 else 0.0, "sufficient_power": delta > 0}
    z_alpha = _norm_ppf(1 - alpha / 2.0)
    z_power = (delta / se) - z_alpha
    power = _normal_cdf(z_power)
    return {
        "n": n,
        "p1": p1,
        "p2": p2,
        "delta": round(delta, 4),
        "alpha": alpha,
        "power": round(power, 4),
        "sufficient_power": power >= 0.8,
    }


def bonferroni_alpha(alpha: float, n_comparisons: int) -> float:
    """Bonferroni-corrected alpha for multiple comparisons (Phase 6 P1 stats discipline).

    Adjusts the significance threshold to control family-wise error rate.

    Args:
        alpha: Original significance level (e.g., 0.05)
        n_comparisons: Number of simultaneous comparisons

    Returns:
        Adjusted alpha = alpha / n_comparisons
    """
    return alpha / max(1, n_comparisons)


def per_specificity_fpr(trace_entries: list[dict]) -> dict:
    """Per-specificity FPR stratification (Phase 6 P1, deferred from E15).

    Stratifies gate decisions by contract specificity level ('specific' vs 'general')
    to check if the gate maintains low false-positive rates across specificity tiers.

    Args:
        trace_entries: List of gate trace JSONL records (each must have 'contract' and 'gate' keys)

    Returns:
        Dict with FPR per specificity stratum + overall
    """
    strata: dict[str, dict[str, int]] = {"specific": {"total": 0, "fp": 0},
                                         "general": {"total": 0, "fp": 0}}
    for entry in trace_entries:
        contract = entry.get("contract", {})
        specificity = contract.get("specificity", "specific")
        if specificity not in strata:
            strata[specificity] = {"total": 0, "fp": 0}
        gate_event = entry.get("gate", {})
        decision = gate_event.get("decision")
        if decision is None:
            continue
        strata[specificity]["total"] += 1
        if decision == "block":
            strata[specificity]["fp"] += 1

    result = {}
    total_fp = 0
    total_calls = 0
    for spec, counts in strata.items():
        if counts["total"] > 0:
            fpr = counts["fp"] / counts["total"]
        else:
            fpr = 0.0
        result[spec] = {"fpr": round(fpr, 4), "blocked": counts["fp"], "total": counts["total"]}
        total_fp += counts["fp"]
        total_calls += counts["total"]

    result["overall"] = {"fpr": round(total_fp / total_calls, 4) if total_calls else 0.0,
                         "blocked": total_fp, "total": total_calls}
    return result
