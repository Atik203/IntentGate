"""Statistics: bootstrap CI + paired McNemar (blueprint Sec 9)."""
from __future__ import annotations

import pytest

from intent_gate.eval.stats import bootstrap_ci, exact_binomial_p, mcnemar


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
