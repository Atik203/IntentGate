"""Statistics: bootstrap CI + paired McNemar (blueprint Sec 9)."""
from __future__ import annotations

import pytest

from intent_gate.eval.stats import (
    _norm_ppf,
    bonferroni_alpha,
    conformal_band,
    bootstrap_ci,
    exact_binomial_p,
    mcnemar,
    per_specificity_fpr,
    power_analysis,
)


def test_bootstrap_ci_constant_values():
    lo, hi = bootstrap_ci([0.5] * 40, n_resamples=200)
    assert lo == pytest.approx(0.5)
    assert hi == pytest.approx(0.5)


def test_bootstrap_ci_is_seeded_and_brackets_mean():
    values = [1.0] * 30 + [0.0] * 10
    first = bootstrap_ci(values, n_resamples=500, seed=7)
    second = bootstrap_ci(values, n_resamples=500, seed=7)
    assert first == second
    assert first[0] <= sum(values) / len(values) <= first[1]


def test_bootstrap_ci_empty_is_nan():
    import math

    lo, hi = bootstrap_ci([])
    assert math.isnan(lo) and math.isnan(hi)


def test_exact_binomial_matches_known_value():
    assert exact_binomial_p(0, 8) == pytest.approx(2 / 256)
    assert exact_binomial_p(8, 8) == pytest.approx(2 / 256)
    assert exact_binomial_p(4, 8) == pytest.approx(1.0)


def test_mcnemar_perfect_protection_is_significant():
    b1 = [True] * 10
    ours = [False] * 10
    result = mcnemar(b1, ours)
    assert result["b1_only"] == 10 and result["ours_only"] == 0
    assert result["method"] == "exact_binomial"
    assert result["p_value"] < 0.01


def test_mcnemar_no_difference():
    result = mcnemar([True, False, True, False], [False, True, False, True])
    assert result["b1_only"] == 2 and result["ours_only"] == 2
    assert result["p_value"] == pytest.approx(1.0)


def test_mcnemar_zero_discordant_pairs():
    result = mcnemar([True, False], [True, False])
    assert result["method"] == "no_discordant_pairs"
    assert result["p_value"] == 1.0


def test_mcnemar_chi2_path_with_correction():
    b1 = [True] * 30 + [False] * 30
    ours = [False] * 30 + [True] * 0 + [False] * 30
    result = mcnemar(b1, ours, correction=True)
    assert result["method"] == "chi2_yates"
    assert result["p_value"] < 1e-5


def test_mcnemar_rejects_unpaired():
    with pytest.raises(ValueError):
        mcnemar([True], [True, False])


def test_power_analysis_large_effect_low_power():
    result = power_analysis(n=10, p1=0.19, p2=0.01, alpha=0.05)
    assert result["delta"] == pytest.approx(0.18)
    assert result["power"] < 0.8


def test_power_analysis_phase5_sample_sufficient():
    result = power_analysis(n=2108, p1=0.19, p2=0.007, alpha=0.05)
    assert result["power"] >= 0.8
    assert result["sufficient_power"] is True


def test_power_analysis_corrected_alpha():
    result = power_analysis(n=2108, p1=0.19, p2=0.007, alpha=0.005)
    assert result["alpha"] == 0.005


def test_bonferroni_alpha_basic():
    assert bonferroni_alpha(0.05, 1) == pytest.approx(0.05)
    assert bonferroni_alpha(0.05, 10) == pytest.approx(0.005)


def test_bonferroni_alpha_zero_comparisons():
    assert bonferroni_alpha(0.05, 0) == pytest.approx(0.05)


def test_conformal_band_calibrates_target_coverage():
    result = conformal_band([0.70, 0.72, 0.74, 0.76, 0.80], tau=0.75, alpha=0.2)
    assert result["method"] == "split_conformal_absolute_deviation"
    assert result["delta"] == pytest.approx(0.05)
    assert result["empirical_coverage"] >= result["target_coverage"]


def test_conformal_band_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        conformal_band([], tau=0.75)
    with pytest.raises(ValueError):
        conformal_band([0.5], tau=0.75, alpha=1.0)


def test_per_specificity_fpr_stratification():
    entries = [
        {"contract": {"specificity": "specific"}, "gate": {"decision": "block"}},
        {"contract": {"specificity": "specific"}, "gate": {"decision": "allow"}},
        {"contract": {"specificity": "general"}, "gate": {"decision": "allow"}},
        {"contract": {"specificity": "general"}, "gate": {"decision": "block"}},
    ]
    result = per_specificity_fpr(entries)
    assert result["specific"]["fpr"] == pytest.approx(0.5)
    assert result["general"]["fpr"] == pytest.approx(0.5)
    assert result["specific"]["total"] == 2
    assert result["general"]["total"] == 2


def test_per_specificity_fpr_empty_handling():
    entries = [{"contract": {}, "gate": {"decision": "allow"}}]
    result = per_specificity_fpr(entries)
    assert result["overall"]["fpr"] == 0.0
    assert result["overall"]["total"] == 1


def test_norm_ppf_known_values():
    assert _norm_ppf(0.975) == pytest.approx(1.96, abs=1e-4)
    assert _norm_ppf(0.5) == pytest.approx(0.0, abs=1e-9)
    assert _norm_ppf(0.025) == pytest.approx(-1.96, abs=1e-4)


def test_norm_ppf_lower_tail_finite():
    assert _norm_ppf(0.01) == pytest.approx(-2.3263, abs=1e-4)
    assert _norm_ppf(0.995) == pytest.approx(2.5758, abs=1e-4)
