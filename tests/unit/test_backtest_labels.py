import pytest

from dowtheory.backtest.labels import (
    PrimaryResult,
    SubSample,
    decide_label,
    label_all,
    label_inputs,
    load_canonical_rules,
    n_ok,
    sign_consistent,
)
from dowtheory.backtest.protocol import FAMILY

NAN = float("nan")


def res(rule="R1", n=40, est=0.7, null=0.5, p=0.001, bound=0.9, a=(20, 0.7), b=(20, 0.7),
        two=False, ga=0, gb=0):
    return PrimaryResult(rule, n, n, ga, gb, two, est, null, p, bound, SubSample(*a), SubSample(*b))


def holm(rule, value):
    return {r: (value if r == rule else 1.0) for r in FAMILY}


CANON = {"trend_persistence": {"literature_label": "literature-consensus"}}


def test_confirmed_when_holm_and_both_subsamples_agree():
    out = decide_label("R1", res(), holm("R1", 0.01), 0.9, CANON)
    assert out["label"] == "data-confirmed"
    assert out["literature_label"] == "literature-consensus"


def test_unresolved_literature_when_key_absent():
    assert decide_label("R2", res("R2"), holm("R2", 0.01), 0.9, CANON)["literature_label"] == (
        "unresolved"
    )


def test_min_n_floor_overrides_significance():
    out = decide_label("R1", res(n=29), holm("R1", 0.0001), 0.9, CANON)
    assert out["label"] == "insufficient-evidence" and out["reason"] == "n below minimum"
    assert n_ok(res(n=30))


def test_two_sample_floors():
    ok = res("R3", n=30, two=True, ga=10, gb=20, est=0.1, null=0.0)
    assert n_ok(ok)
    assert not n_ok(res("R3", n=30, two=True, ga=9, gb=21))
    assert not n_ok(res("R3", n=29, two=True, ga=10, gb=19))


def test_subsample_disagreement_is_insufficient():
    r = res(a=(20, 0.8), b=(20, 0.4))
    out = decide_label("R1", r, holm("R1", 0.001), 0.9, CANON)
    assert out["label"] == "insufficient-evidence"
    assert sign_consistent(r, "predicted") is False


def test_subsample_not_assessable_blocks_confirmation_and_refutation():
    r = res(a=(9, 0.8), b=(30, 0.9))
    assert sign_consistent(r, "predicted") is None
    out = decide_label("R1", r, holm("R1", 0.001), 0.9, CANON)
    assert out["label"] == "insufficient-evidence"
    assert "not assessable" in out["reason"]
    r2 = res(est=0.3, bound=0.4, a=(9, 0.3), b=(30, 0.3))
    assert decide_label("R1", r2, holm("R1", 1.0), 0.4, CANON)["label"] == "insufficient-evidence"


def test_significant_but_not_after_holm():
    out = decide_label("R1", res(p=0.03), holm("R1", 0.06), 0.9, CANON)
    assert out["label"] == "insufficient-evidence"


def test_refutation_requires_bound_below_null_and_both_subsamples_wrong():
    wrong = res(est=0.3, bound=0.45, a=(20, 0.3), b=(20, 0.35))
    assert decide_label("R1", wrong, holm("R1", 1.0), 0.45, CANON)["label"] == "data-refuted"
    # bound touches the null: not strictly on the wrong side
    assert decide_label("R1", wrong, holm("R1", 1.0), 0.5, CANON)["label"] == (
        "insufficient-evidence"
    )
    # point estimate wrong but one sub-sample on the right side
    mixed = res(est=0.3, bound=0.45, a=(20, 0.3), b=(20, 0.6))
    assert decide_label("R1", mixed, holm("R1", 1.0), 0.45, CANON)["label"] == (
        "insufficient-evidence"
    )


def test_refutation_respects_min_n():
    small = res(n=10, est=0.1, bound=0.2, a=(5, 0.1), b=(5, 0.1))
    assert decide_label("R1", small, holm("R1", 1.0), 0.2, CANON)["label"] == (
        "insufficient-evidence"
    )


def test_label_all_family_of_eight_and_missing_enter_as_one():
    prim = {r: res(r, n=5) for r in FAMILY}
    prim["R1"] = res("R1", p=0.001)
    out = label_all(prim, {}, CANON)
    assert set(out) == set(FAMILY)
    # Holm over 8 with seven p=1.0: R1 adjusted = 8 * 0.001
    assert out["R1"]["p_holm"] == pytest.approx(0.008)
    assert out["R1"]["label"] == "data-confirmed"
    assert all(out[r]["label"] == "insufficient-evidence" for r in FAMILY if r != "R1")


def test_worst_grid_rule_for_r4_and_r5():
    primary = res("R4", est=0.5, null=1 / 3, p=0.001, bound=0.7)
    grid = {0.05: res("R4", p=0.2, bound=0.9), 0.08: primary, 0.10: res("R4", p=0.01, bound=0.6)}
    p, bound = label_inputs("R4", primary, grid)
    assert p == 0.2 and bound == 0.9
    # a grid point below the n floor is ignored
    grid[0.06] = res("R4", n=10, p=0.9, bound=0.99)
    assert label_inputs("R4", primary, grid) == (0.2, 0.9)
    # no usable point: cannot confirm and cannot refute
    assert label_inputs("R4", primary, {0.08: res("R4", n=3)}) == (1.0, primary.null_value)
    # other rules ignore the grid
    assert label_inputs("R1", res("R1", p=0.04, bound=0.8), grid) == (0.04, 0.8)


def test_worst_grid_blocks_confirmation():
    prim = {r: res(r, n=5) for r in FAMILY}
    prim["R4"] = res("R4", p=0.0001, est=0.6, null=1 / 3, a=(20, 0.6), b=(20, 0.6))
    grids = {"R4": {0.08: prim["R4"], 0.12: res("R4", p=0.4, est=0.5, null=1 / 3)}}
    assert label_all(prim, grids, CANON)["R4"]["label"] == "insufficient-evidence"
    grids_ok = {"R4": {0.08: prim["R4"], 0.12: res("R4", p=0.0002, est=0.5, null=1 / 3)}}
    assert label_all(prim, grids_ok, CANON)["R4"]["label"] == "data-confirmed"


def test_nan_p_value_enters_family_as_one():
    prim = {r: res(r, p=NAN) for r in FAMILY}
    assert label_all(prim, {}, CANON)["R1"]["p_holm"] == 1.0


def test_canonical_rules_parser(tmp_path):
    md = tmp_path / "c.md"
    md.write_text(
        "| id | rule_key | statement | label | other |\n|---|---|---|---|---|\n"
        "| R-001 | trend_persistence | s | consensus (one lineage) | x |\n"
        "| R-002 | secondary_retracement | s | disputed | x |\n"
        "| R-003 | line_breakout | s | single-source (echoed) | x |\n"
        "| R-004 | hamilton_timing | s | agent-defined | x |\n"
        "\ntext\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
        encoding="utf-8",
    )
    got = load_canonical_rules(md)
    assert got["trend_persistence"]["literature_label"] == "literature-consensus"
    assert got["secondary_retracement"]["literature_label"] == "literature-disputed"
    assert got["line_breakout"]["literature_label"] == "single-source"
    assert got["hamilton_timing"]["literature_label"] == "agent-defined"


def test_resolve_literature_from_registry_rows():
    from dowtheory.backtest.labels import RULE_ENTRIES, resolve_literature

    canon = {}
    for key, ids in RULE_ENTRIES.items():
        for i in ids:
            canon[f"{key}_{i}"] = {"id": i, "literature_label": "literature-consensus"}
    canon["x"] = {"id": "R-009", "literature_label": "literature-disputed"}
    got = resolve_literature(canon)
    assert got["secondary_retracement"]["literature_label"] == "literature-disputed"
    assert got["trend_persistence"]["literature_label"] == "literature-consensus"
    assert got["trend_persistence"]["ids"] == "R-016,R-017"
    canon["y"] = {"id": "R-062", "literature_label": "single-source"}
    canon.pop("hamilton_timing_R-062")
    assert resolve_literature(canon)["hamilton_timing"]["literature_label"] == "single-source"
    canon.pop("y")
    assert resolve_literature(canon)["hamilton_timing"]["literature_label"] == "unresolved"
