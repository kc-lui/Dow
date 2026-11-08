import datetime as dt
from decimal import Decimal
from types import SimpleNamespace

import pandas as pd

from dowtheory.confirmation import confirm_signal, pair_confirm, volume_confirms


def _state(name):
    return SimpleNamespace(state=name)


def _sig(kind, day):
    return SimpleNamespace(kind=kind, ts=dt.date(2024, 1, 1) + dt.timedelta(days=day - 1))


def test_confirmed_when_states_match():
    r = pair_confirm(_state("BULL_PRIMARY"), _state("BULL_PRIMARY"), [], [])
    assert (r.status, r.pair_state) == ("confirmed", "BULL_PRIMARY")


def test_non_confirmation_variants():
    assert pair_confirm(_state("BULL_PRIMARY"), _state("BEAR_PRIMARY"), [], []).status == (
        "non_confirmation")
    assert pair_confirm(_state("BULL_PRIMARY"), _state("BULL_SUSPECT"), [], []).status == (
        "non_confirmation")


def test_pending_when_undefined():
    r = pair_confirm(_state("UNDEFINED"), _state("BULL_PRIMARY"), [], [])
    assert r.status == "pending" and r.pair_state is None


def test_detail_reports_reversal_confirmation():
    a = [_sig("REVERSAL_DOWN", 5)]
    r = pair_confirm(_state("BEAR_PRIMARY"), _state("BEAR_PRIMARY"), a, [_sig("REVERSAL_DOWN", 9)])
    assert "matched by B" in r.detail and r.confirmed_ts == dt.date(2024, 1, 9)
    r = pair_confirm(_state("BEAR_PRIMARY"), _state("BEAR_PRIMARY"), a, [_sig("REVERSAL_DOWN", 9)], 2)
    assert "not yet confirmed" in r.detail and r.confirmed_ts is None


def _swing(idx, price):
    return SimpleNamespace(idx=idx, price=Decimal(str(price)))


def _df(volumes):
    return pd.DataFrame({"volume": volumes})


def test_volume_confirms_uptrend_with_heavy_up_legs():
    vols = [1] * 3 + [10] * 3 + [1] * 3 + [10] * 3  # idx 0..11
    swings = [_swing(2, 100), _swing(5, 110), _swing(8, 105), _swing(11, 120)]
    assert volume_confirms(_df(vols), swings) is True


def test_volume_does_not_confirm_when_counter_legs_heavier():
    vols = [1] * 3 + [1] * 3 + [10] * 3 + [1] * 3
    swings = [_swing(2, 100), _swing(5, 110), _swing(8, 105), _swing(11, 120)]
    assert volume_confirms(_df(vols), swings) is False


def test_volume_none_cases():
    swings = [_swing(2, 100), _swing(5, 110), _swing(8, 105), _swing(11, 120)]
    assert volume_confirms(_df([0] * 12), swings) is None
    assert volume_confirms(_df([1] * 12), swings[:2]) is None


def test_leading_signal_on_b_confirms_at_a_date():
    a = [_sig("REVERSAL_DOWN", 100)]
    b = [_sig("REVERSAL_DOWN", 40)]
    res = confirm_signal(a[0], a, b)
    assert res.status == "confirmed" and res.confirmed_ts == a[0].ts
    assert res.matched_ts == b[0].ts


def test_match_does_not_cross_cycles_or_opposite_reversals():
    # B's only REVERSAL_DOWN comes after A's next reversal (another cycle) -> pending.
    a = [_sig("REVERSAL_DOWN", 10), _sig("REVERSAL_UP", 50)]
    b = [_sig("REVERSAL_DOWN", 200)]
    assert confirm_signal(a[0], a, b).status == "pending"
    # B reversed back up before reaching A's date -> its earlier down no longer confirms.
    b2 = [_sig("REVERSAL_DOWN", 5), _sig("REVERSAL_UP", 8)]
    assert confirm_signal(a[0], a, b2).status == "pending"


def test_as_of_hides_future_matches_and_max_days_limits():
    a = [_sig("REVERSAL_DOWN", 10)]
    b = [_sig("REVERSAL_DOWN", 30)]
    assert confirm_signal(a[0], a, b, as_of=dt.date(2024, 1, 20)).status == "pending"
    assert confirm_signal(a[0], a, b).confirmed_ts == b[0].ts
    assert confirm_signal(a[0], a, b, max_days=5).status == "pending"


def test_pair_confirmation_invariant_under_truncation():
    kinds = ["REVERSAL_DOWN", "REVERSAL_UP"]
    a = [_sig(kinds[i % 2], d) for i, d in enumerate([10, 60, 130, 200, 260])]
    b = [_sig(kinds[(i + 1) % 2], d) for i, d in enumerate([4, 20, 75, 135, 150, 215, 300])]
    for s in a:
        full = confirm_signal(s, a, b)
        for t in range(1, 320, 7):
            asof = dt.date(2024, 1, 1) + dt.timedelta(days=t - 1)
            if s.ts > asof:
                continue
            cut_a = [x for x in a if x.ts <= asof]
            cut_b = [x for x in b if x.ts <= asof]
            part = confirm_signal(s, cut_a, cut_b, as_of=asof)
            known = full.confirmed_ts is not None and full.confirmed_ts <= asof
            assert (part.status == "confirmed") is known, (s.ts, asof)
            assert (part.confirmed_ts == full.confirmed_ts) if known else part.confirmed_ts is None
