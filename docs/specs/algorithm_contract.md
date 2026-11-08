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
