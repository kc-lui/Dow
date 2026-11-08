# Algorithm contract (frozen before P3; changes require a commit touching this file)

All code in `src/dowtheory/`. Closing prices only (Dow). No lookahead: every derived object carries the bar index at which it became knowable.

## Swing
```python
@dataclass(frozen=True)
class Swing:
    idx: int                    # bar index of the extreme
    ts: datetime.date           # session date of the extreme
    price: Decimal              # close at the extreme
    kind: Literal["H", "L"]
    confirmed_idx: int          # first bar at which the reversal threshold was met (>= idx)
    confirmed_ts: datetime.date
    scale: Literal["minor", "secondary", "primary"]
    amplitude_pct: Decimal      # |price / previous same-scale swing price - 1|
    duration_days: int          # calendar days since previous same-scale swing (0 for first)
    retrace_ratio: Decimal | None  # secondary only: |this leg| / |previous opposite leg|, else None
```
`detect_swings(close: pd.Series, *, method="pct"|"atr"|"pivot", threshold=0.03, atr_mult=2.0, atr_window=14, pivot_n=5, high=None, low=None, scale="minor") -> list[Swing]`
- H and L strictly alternate. First emitted swing may be either kind.
- pct: candidate extreme flips when close moves >= threshold against it; `confirmed_idx` = that bar.
- atr: threshold_i = atr_mult * ATR(atr_window)[i] / candidate_price (needs high/low; falls back to close-based true range if absent).
- pivot: bar i is H if close[i] == max(close[i-n..i+n]) (L symmetric); `confirmed_idx = i + n`; same-kind neighbours collapsed to the more extreme one.
- `swings_as_of(swings, t_idx) -> list[Swing]`: only `confirmed_idx <= t_idx`.
- Truncation invariance (test): `detect_swings(close[:t+1])` restricted to confirmed <= t  ==  `swings_as_of(detect_swings(close), t)`.
- `nest_scales(minor, secondary)`: every secondary swing shares a bar with a minor swing (snap to nearest minor swing of same kind within ±2 bars; else keep and flag `snapped=False` in metadata dict returned alongside).

## TrendStateMachine
States: `UNDEFINED, BULL_PRIMARY, BEAR_PRIMARY, BULL_SUSPECT, BEAR_SUSPECT`. (`LINE` is reported separately by `line.py`, not a state.)
Input: secondary-scale swings (confirmed only) and closes, replayed bar by bar.
```python
@dataclass
class TrendState:
    state: str; since: date | None
    last_H: Swing | None; prev_H: Swing | None; last_L: Swing | None; prev_L: Swing | None
    defense_line: Decimal | None; defense_line_ts: date | None; defense_line_kind: Literal["reaction_low","reaction_high"] | None
    secondary_direction: Literal["up","down","flat"]
@dataclass(frozen=True)
class Signal:
    idx: int; ts: date; kind: Literal["REVERSAL_UP","REVERSAL_DOWN","DEFENSE_BREAK","HH","HL","LH","LL","LINE_BREAKOUT_UP","LINE_BREAKOUT_DOWN"]
    price: Decimal; level: Decimal | None; note: str; agent_defined: bool
```
Transitions (evaluated when a swing becomes confirmed, then on each close):
- UNDEFINED → BULL_PRIMARY on confirmed HH followed by confirmed HL (or HL then HH); → BEAR_PRIMARY on LH + LL.
- BULL_PRIMARY: new H > last_H → HH signal; new L > last_L → HL signal and `defense_line = L.price` (kind reaction_low). New H < last_H → LH signal, state BULL_SUSPECT.
- BULL_SUSPECT: close < defense_line → REVERSAL_DOWN, state BEAR_PRIMARY, defense_line = the LH that formed (reaction_high), since = that bar. New H > last_H → back to BULL_PRIMARY.
- BULL_PRIMARY and close < defense_line without prior LH → DEFENSE_BREAK (agent_defined=True); if `require_lower_high_for_reversal` is false this also flips to BEAR_PRIMARY, else state BULL_SUSPECT.
- Mirror for bears.
- `defense_line` always emitted with `agent_defined: true`.

## line.py
`detect_lines(close_a, close_b, band_pct=0.05, min_days=14) -> list[LineRange(start, end, band_pct_a, band_pct_b, breakout: "up"|"down"|"none", breakout_ts, confirmed_both: bool)]`. Window qualifies when, for both series, (max−min)/mean <= band_pct over >= min_days consecutive sessions; extend greedily; breakout = first close outside the window's band; `confirmed_both` = both series break the same way within `confirmation.max_days` (None = any later date, evaluated only up to as_of).

## confirmation.py
`pair_confirm(state_a: TrendState, state_b: TrendState, signals_a, signals_b, max_days=None) -> ConfirmationResult(status: "confirmed"|"non_confirmation"|"pending", pair_state: str|None, detail: str)`.
`volume_confirms(df, swings) -> bool | None` (None when volume all zero).

## levels.py
`cluster_levels(swings, kind, tol_mode="pct", tol_pct=0.0075, tol_atr_mult=0.5, atr=None, min_touches=2, max_levels=4, ref_price=None) -> list[Level(price, zone_low, zone_high, touches, members: list[date])]`.
`fit_trendlines(swings, kind="up"|"down", closes, tol_pct=0.01) -> list[TrendLine(kind, p0:(date,price), p1:(date,price), slope_per_day, touches, valid: bool, value_at(date))]` — through the last two confirmed secondary HL (up) / LH (down); valid if no close violates the line by > tol_pct between p0 and as_of.

## Analysis JSON (schema.py → `AnalysisResult.to_json()`)
```json
{"meta":{"symbol":"^DJI","pair":"^DJT","as_of":"YYYY-MM-DD","config_hash":"…","swing_method":"pct","thresholds":{"minor_pct":0.03,"secondary_pct":0.10},"run_id":"…"},
 "trend_state":{"primary":"BULL_PRIMARY","since":"YYYY-MM-DD","secondary_direction":"down",
   "confirmation":{"pair_state":"BULL_PRIMARY","status":"confirmed","detail":"…"},
   "defense_line":{"price":0.0,"ts":"YYYY-MM-DD","type":"reaction_low","agent_defined":true},
   "volume_confirms":true},
 "swings":[{"ts":"…","price":0.0,"kind":"L","scale":"secondary","confirmed_ts":"…","amplitude_pct":0.0,"duration_days":0,"retrace_ratio":0.0}],
 "levels":{"support":[{"price":0.0,"zone_low":0.0,"zone_high":0.0,"touches":2}],"resistance":[],
   "trendlines":[{"kind":"up","p0":["…",0.0],"p1":["…",0.0],"slope_per_day":0.0,"touches":2,"valid":true,"value_at_as_of":0.0}]},
 "lines":[{"start":"…","end":"…","band_pct_a":0.0,"band_pct_b":0.0,"breakout":"none","confirmed_both":false}],
 "signals":[{"ts":"…","kind":"REVERSAL_DOWN","price":0.0,"level":0.0,"note":"…","agent_defined":false,"confirmation":"pending"}],
 "status_labels":{"defense_line":"agent-defined","secondary_duration_bounds":"literature-disputed","secondary_retracement":"literature-disputed","hamilton_3pct_filter":"literature-consensus","line_definition":"literature-consensus","two_average_confirmation":"literature-consensus"}}
```
Numbers serialised as floats in JSON; Decimal internally.

## Chart (chart.py)
`render_chart(result: AnalysisResult, df, df_pair=None, out_dir="outputs/charts") -> Path`. Matplotlib `Agg`, figsize (14, 8), two panels (price 4 : volume 1). Price panel: close line; minor swings small grey markers, secondary swings larger (H red ▼, L green ▲); defense line dashed red horizontal from its ts to as_of labelled "Dow defense line (agent-defined)"; support/resistance `axhspan` zones (green/red, alpha 0.15) with touch count; trendlines solid segments extended to as_of; line ranges `axvspan` grey alpha 0.2; signals vertical dotted markers with kind text. Title: `{symbol} vs {pair} | {primary} since {since} | confirmation: {status} | method {method} {minor_pct}/{secondary_pct}`. Legend outside right. File `outputs/charts/{sym}_{pair}_{as_of}_{method}{minor_pct}.png` (`^` stripped). JSON twin in `outputs/json/`, markdown table via `report.to_markdown(result)`.

## CLI
`dow analyze --symbol ^DJI --pair ^DJT [--as-of YYYY-MM-DD] [--start] [--source clickhouse|csv --csv PATH --csv-pair PATH] [--method pct|atr|pivot] [--no-chart] [--persist]` → prints markdown, writes PNG + JSON; `--persist` inserts into `dow.str_swing_log`, `dow.str_trend_state_snapshots`, `dow.str_level_log`.

## Deviations

Recorded by the swings/trend implementation (`swings.py`, `trend.py`).

1. **Pivot alternation.** The contract says same-kind neighbours collapse to the more extreme one. Rewriting an already emitted swing would break truncation invariance, so detection is append-only: two same-kind pivots with no opposite pivot between them are both kept and the deepest close between them is inserted as the opposite swing (its `confirmed_idx` equals that of the second pivot). Plateau repeats without a real dip keep the earlier pivot. Flat windows (bar is both max and min) yield no pivot.
2. **ATR threshold.** `atr_mult * ATR[i] / candidate_price`, ATR a simple rolling mean of true range over `atr_window` bars; no swing can flip while ATR is NaN or zero. Without high/low the true range is `|close - prev close|`.
3. **Multiscale parameters.** `detect_multiscale` widens the minor parameters for the secondary scale by `secondary_pct / minor_pct`: `atr_mult` is multiplied, `pivot_n` multiplied and rounded.
4. **`nest_scales`.** Returns `(snapped_swings, flags)` where `flags[final_idx]` is `snapped`. A snapped secondary swing adopts the minor swing's bar and price and `confirmed_idx = max(secondary, minor)` to avoid lookahead. `compute_secondary_metrics` is applied afterwards by `detect_multiscale`.
5. **Swing signals** (HH/HL/LH/LL) are stamped with the bar at which the swing is confirmed (`Signal.idx/ts`), with `price` the swing price and `level` the previous same-kind swing price.
6. **State machine details.** `secondary_direction` is the opposite of the last confirmed swing kind (last H confirmed means price is correcting down). `since` changes only when the primary direction is established or flips, not on SUSPECT transitions. `REVERSAL_*` from a SUSPECT state requires a counter swing (LH in a bull, HL in a bear) since the last HH/LL; a SUSPECT state reached via `DEFENSE_BREAK` without a counter swing waits for one. In non-strict mode a defense break flips directly and emits only `DEFENSE_BREAK`. `TrendState` and `Swing.retrace_ratio` carry defaults; `State` values are plain `str` constants.
7. `run_trend` returns one `TrendState` snapshot per bar (aligned with `close`).

Recorded by the levels/line/confirmation/analysis/chart implementation.

8. **Level inputs.** `analysis.analyze` clusters *minor* swings (secondary swings alone rarely repeat within 0.75%). Zones span min/max of members, widened to at least +/- tolerance/2 around the mean. `max_levels` keeps the clusters closest to the last close. `kind` accepts `H`/`L`/`resistance`/`support`.
9. **Lines.** Windows are counted in sessions, do not overlap, and the breakout is the first later close outside the window's own min/max in either series (earliest wins). `confirmed_both` needs the other series to break the same way (calendar-day lag <= `max_days`; any later date when `None`). Each line breakout is also emitted as a `LINE_BREAKOUT_UP/DOWN` signal (not agent-defined) by `analysis.py`, since `run_trend` does not see lines.
10. **Pair confirmation.** `pair_confirm` rules: either side UNDEFINED -> pending; opposite sides, or same side with one PRIMARY and one SUSPECT -> non_confirmation; identical states -> confirmed. Per-signal `confirmation` is `confirmed`/`pending` for reversals and line breakouts (other average shows the same kind on/after the date, or within +/- `max_days`), `not_applicable` otherwise or without a pair.
11. **`volume_confirms`.** Compares mean daily volume on legs aligned with the net move vs counter legs over the last four secondary swings; `None` when volume is all zero or either leg group is empty.
12. **Chart.** Two index frames are inner-joined on date before analysis. Pair close is drawn on a right axis. Dotted vertical signal lines with text are limited to `REVERSAL_*` and `DEFENSE_BREAK`; line breakouts are small triangles; HH/HL/LH/LL are not repeated. Line ranges shorter than 28 calendar days are not shaded (at band 5% there are ~100 over 2015-2026).
13. **Result sections** hold native `Decimal`/`date` values; conversion happens only in `to_dict()`. `swings` lists minor and secondary swings of the analysed symbol. `--pair` defaults to the `pairs.yaml` partner of `--symbol` for the ClickHouse source.
14. **A2 EQUAL swings (implementation).** An EQUAL swing emits no HH/HL/LH/LL signal. It still counts as the counter swing when it is the trend-side extreme (double top in a bull, double bottom in a bear), because otherwise the 2016-04-14 REVERSAL_UP on ^DJI (R8 prototype, section I) cannot reappear. Other EQUAL swings change nothing.
15. **A1 filter semantics.** The flip is deferred until `i - previous_swing.idx >= secondary_min_sessions` at the confirmation bar `i`; it applies to pct and atr, not pivot. `detect_multiscale(close, cfg, high=None, low=None, *, symbol=None)` keeps `symbol` keyword-only so positional callers stay valid.
16. **A3.** On return to PRIMARY (HH in a bull, LL in a bear) the defense line is refreshed to the latest confirmed reaction extreme. No extra breaker was added: a SUSPECT state reached by a defense break resolves on the next counter swing or new extreme (^DJI longest stall now 296 sessions from 2018-12-19, a genuine unresolved correction).
17. **A4/A5.** `trend.warmup_note(signals, data_start)` builds `meta.warmup_note`. `Swing.flags` is a dict excluded from the hash; it is `{}` on minor swings.

## Amendments after R8 spec review (2026-11-08, reports/spec_review_p3.md)

A1. `secondary_pct` default 0.08; `swings.secondary_min_sessions` (15) is a causal filter on the secondary zig-zag: a flip is only accepted when ≥ N sessions have elapsed since the previous same-scale swing (evaluated at confirmation time, no lookahead). `swings.per_symbol_secondary_pct` allows per-symbol overrides.
A2. `trend.equal_extreme_tol` (0.005): a new swing within ±tol of the compared extreme is "EQUAL" and emits no HH/HL/LH/LL and no state change.
A3. Strict mode must not deadlock: in `BULL_SUSPECT` a new confirmed H > last_H returns to `BULL_PRIMARY`; in `BEAR_SUSPECT` a new confirmed L < last_L returns to `BEAR_PRIMARY`; in either SUSPECT state the opposite-side swing updates the bookkeeping and the defense line is refreshed to the latest confirmed reaction extreme when the state returns to PRIMARY.
A4. `UNDEFINED → *_PRIMARY` emits `Signal(kind="TREND_ESTABLISHED", ...)`; the first state depends on data start and this is documented in output `meta.warmup_note`.
A5. Secondary swings carry `flags: {rhea_window: bool, schannep_window: bool, retrace_in_third_two_thirds: bool, retrace_in_third_half: bool}`, computed from `secondary_min_days/max_days`, `schannep_min_days/min_pct` and `retrace_ratio`; flags never filter swings.
A6. `LineRange` gains `confirmed_ts: date | None` (the later of the two averages' breakout dates) and `confirmed_both` is evaluated only with information up to `as_of`; `line.min_sessions` counts trading sessions; a window qualifies only if net drift |close_end/close_start − 1| ≤ band_pct × max_drift_frac in both averages.
A7. Pair confirmation is cycle-aware: a signal on A is matched with the nearest same-kind signal on B in either order within the same primary cycle (between consecutive reversals on A); `confirmed_ts` = later of the two dates; status at `as_of` uses only signals ≤ as_of.
A8. Resistance levels are clustered from swing highs ≥ current close (support from swing lows ≤ current close); if fewer than `min_touches` qualify, report what exists and state it.
A9. `status_labels` key `hamilton_3pct_filter` renamed `rhea_3pct_filter` with label `literature-consensus` only if canonical_rules.md supports it, else `single-source`; `secondary_pct_threshold: agent-defined`.
