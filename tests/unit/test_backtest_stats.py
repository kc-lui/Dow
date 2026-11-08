import math

import numpy as np
import pytest

from dowtheory.backtest import stats


def test_binomial_known_values():
    assert stats.binomial_pvalue(8, 10, 0.5, "greater") == pytest.approx(56 / 1024)
    assert stats.binomial_pvalue(8, 10, 0.5, "two-sided") == pytest.approx(112 / 1024)
    assert stats.binomial_pvalue(2, 10, 0.5, "less") == pytest.approx(56 / 1024)
    assert stats.binomial_pvalue(2, 3, 1 / 3, "greater") == pytest.approx(7 / 27)
    assert stats.binomial_pvalue(0, 5, 0.5, "greater") == 1.0
    assert math.isnan(stats.binomial_pvalue(0, 0))
    with pytest.raises(ValueError):
        stats.binomial_pvalue(11, 10)


def test_wilson_known_values():
    lo, hi = stats.wilson_interval(5, 10)
    assert lo == pytest.approx(0.2366, abs=1e-3)
    assert hi == pytest.approx(0.7634, abs=1e-3)
    lo, hi = stats.wilson_interval(0, 10)
    assert lo == 0.0
    assert hi == pytest.approx(0.2775, abs=1e-3)
    assert all(math.isnan(x) for x in stats.wilson_interval(0, 0))


def test_wilson_one_sided_matches_two_sided_at_matching_level():
    assert stats.wilson_bound(7, 20, 0.975, "upper") == pytest.approx(
        stats.wilson_interval(7, 20, 0.95)[1]
    )
    assert stats.wilson_bound(7, 20, 0.975, "lower") == pytest.approx(
        stats.wilson_interval(7, 20, 0.95)[0]
    )


def test_holm_hand_example():
    adj = stats.holm_adjust({"a": 0.01, "b": 0.04, "c": 0.03, "d": 0.005})
    assert adj == pytest.approx({"d": 0.02, "a": 0.03, "c": 0.06, "b": 0.06})
    assert stats.holm_adjust({"a": 0.9, "b": 0.8})["a"] == 1.0


def test_permutation_detects_and_is_symmetric():
    rng = np.random.default_rng(1)
    x, y = rng.normal(1.0, 1.0, 25), rng.normal(0.0, 1.0, 25)
    obs, p_gt = stats.permutation_pvalue(x, y, 1000, stats.make_rng())
    assert obs == pytest.approx(x.mean() - y.mean())
    assert p_gt < 0.01
    # swapping the groups flips the sign of the statistic and the tail
    obs_sw, p_swapped = stats.permutation_pvalue(y, x, 1000, stats.make_rng(), "less")
    assert obs_sw == pytest.approx(-obs)
    assert p_swapped < 0.01
    _, p_wrong_tail = stats.permutation_pvalue(x, y, 1000, stats.make_rng(), "less")
    assert p_wrong_tail > 0.9


def test_permutation_identical_groups_p_one():
    _, p = stats.permutation_pvalue([1.0, 1.0, 1.0], [1.0, 1.0], 200, stats.make_rng())
    assert p == 1.0


def test_permutation_null_is_centered():
    x, y = np.arange(20.0), np.arange(20.0) + 0.5
    null = stats.permutation_diff_null(x, y, 2000, stats.make_rng())
    assert abs(null.mean()) < 0.1


def test_bootstrap_reproducible_under_seed():
    vals = np.random.default_rng(3).normal(size=40)
    ids = stats.cluster_ids(np.arange(40) * 50, 20)
    a = stats.cluster_bootstrap_mean(vals, ids, 300, stats.make_rng())
    b = stats.cluster_bootstrap_mean(vals, ids, 300, stats.make_rng())
    c = stats.cluster_bootstrap_mean(vals, ids, 300, stats.make_rng(1))
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)
    x = np.random.default_rng(4).normal(size=500) * 0.01
    y = np.random.default_rng(5).normal(size=500) * 0.01
    d1 = stats.block_bootstrap_paired(x, y, 20, 100, stats.make_rng())
    d2 = stats.block_bootstrap_paired(x, y, 20, 100, stats.make_rng())
    assert np.array_equal(d1[0], d2[0]) and np.array_equal(d1[1], d2[1])


def test_cluster_ids_chain_overlapping_windows():
    # bars 0 and 10 overlap at h=20 (diff <= h); 100 does not; same bar shares a cluster
    ids = stats.cluster_ids([100, 0, 10, 100], 20)
    assert ids[1] == ids[2] != ids[0]
    assert ids[0] == ids[3]
    assert list(stats.cluster_ids([0, 25, 50], 20)) == [0, 1, 2]
    assert list(stats.cluster_ids([0, 20, 40], 20)) == [0, 0, 0]  # chained single linkage


def test_cluster_bootstrap_mean_centered_on_sample_mean():
    vals = np.array([1.0, 2.0, 3.0, 4.0, 10.0, 11.0])
    ids = np.array([0, 0, 1, 1, 2, 2])
    dist = stats.cluster_bootstrap_mean(vals, ids, 4000, stats.make_rng())
    assert dist.mean() == pytest.approx(vals.mean(), abs=0.2)
    assert dist.min() >= vals.min() and dist.max() <= vals.max()


def test_random_placement_respects_spacing_and_range():
    g = np.arange(100.0)
    null = stats.random_placement_null(g, 10, 89, 5, [1] * 5, 15, 300, stats.make_rng())
    # five bars at least 15 apart inside [10, 89] -> mean of g within the range, positive
    assert null.min() >= 10 and null.max() <= 89
    # with spacing 20 and 5 events, only one layout fits except slack of 0
    tight = stats.random_placement_null(g, 0, 80, 5, [1] * 5, 20, 50, stats.make_rng())
    assert np.allclose(tight, np.mean([0, 20, 40, 60, 80]))
    with pytest.raises(ValueError):
        stats.random_placement_null(g, 0, 50, 5, [1] * 5, 20, 10, stats.make_rng())


def test_random_placement_assigns_signs_randomly():
    g = np.ones(50)
    null = stats.random_placement_null(g, 0, 49, 4, [1, 1, -1, -1], 1, 50, stats.make_rng())
    assert np.allclose(null, 0.0)


def test_one_sided_p_formula():
    null = np.array([0.0, 1.0, 2.0, 3.0])
    assert stats.one_sided_p(null, 2.0) == pytest.approx((1 + 2) / 5)
    assert stats.one_sided_p(null, 2.0, "less") == pytest.approx((1 + 3) / 5)


def test_stationary_indices_block_length_and_range():
    idx = stats.stationary_indices(2000, 20, 50, stats.make_rng())
    assert idx.min() >= 0 and idx.max() < 2000
    steps = np.diff(idx, axis=1) % 2000
    new_block_share = np.mean(steps != 1)
    assert new_block_share == pytest.approx(1 / 20, abs=0.01)


def test_sharpe_and_paired_bootstrap_identical_series():
    r = np.random.default_rng(7).normal(0.0004, 0.01, 400)
    assert stats.sharpe(r) == pytest.approx(r.mean() / r.std(ddof=1) * math.sqrt(252))
    d_sharpe, d_cum = stats.block_bootstrap_paired(r, r, 20, 50, stats.make_rng())
    assert np.allclose(d_sharpe, 0.0) and np.allclose(d_cum, 0.0)
    assert math.isnan(stats.sharpe(np.zeros(10)))


def test_decimal_conversion_and_describe():
    from decimal import Decimal

    d = stats.describe([Decimal("0.1"), Decimal("0.3"), Decimal("0.5")])
    assert d["median"] == pytest.approx(0.3) and d["n"] == 3
    counts = stats.decile_counts([Decimal("0.05"), Decimal("0.95"), Decimal("1.5"), Decimal(1)])
    assert counts[0] == 1 and counts[9] == 2 and counts[10] == 1
    assert stats.describe([])["n"] == 0
    med, lo, hi = stats.median_interval([1.0, 2.0, 3.0, 4.0], stats.make_rng(), 200)
    assert lo <= med <= hi
