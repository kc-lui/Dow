import datetime as dt
from decimal import Decimal
from types import SimpleNamespace

import pandas as pd

from dowtheory.confirmation import pair_confirm, volume_confirms


def _state(name):
    return SimpleNamespace(state=name)


def _sig(kind, day):
    return SimpleNamespace(kind=kind, ts=dt.date(2024, 1, day))


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
    assert "confirmed by B" in r.detail and "not yet" not in r.detail
    r = pair_confirm(_state("BEAR_PRIMARY"), _state("BEAR_PRIMARY"), a, [_sig("REVERSAL_DOWN", 9)], 2)
    assert "not yet confirmed" in r.detail


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
