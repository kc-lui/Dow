# Protocol deviations and proposed clarifications

Format per `analysis/decision_table.md` section 6. Entries below are written by R10 (backtest
engineer) **before the first label-driving run**, against decision table sha256
`c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836` (v2). They are *proposed*
clarifications: places where the table is silent, ambiguous or internally inconsistent and the
harness had to pick one reading. The protocol file was not changed. R12 decides whether to fold
them into a v3 table (new hash, before the run) or keep them as logged deviations.

Pre-registration is git-verifiable: `analysis/decision_table.md` v2 (sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`) was committed in `da6427c` at
2026-11-08 14:09 local (+0800), before the first label-driving run at 14:26 local (06:26 UTC).

Results seen: a development smoke run on the real `DJ` data (300 bootstrap draws, no persist)
was executed after the event code was written and before the report layer was finished. No
interpretation below was changed after that run.

| id | status | topic |
|---|---|---|
| DEV-01 | proposed | Sub-sample split date rule |
| DEV-02 | clarification | Literature label mapping from protocol keys to registry ids |
| DEV-03 | proposed | Two-sample sub-sample `n` |
| DEV-04 | proposed | Random-placement details |
| DEV-05 | proposed | R7 sample start versus swing history |
| DEV-06 | proposed | Bonferroni bound for non-proportion metrics |
| DEV-07 | proposed | `decision_table_hash` value |
| DEV-08 | proposed | R8 sub-sample `n`, call definition, spell null |
| DEV-09 | proposed | Reversals matched later than `c + h` appear in both R3 groups |
| DEV-10 | recommendation (v3) | R1 label null: pre-register the simulated random-walk baseline |
| INC-01 | bug fix, recorded | First persisted run lost rows to the ledger sorting key |
| FIX-01 | tooling fix | Scoped hash used the wrong marker |
| FIX-02 | no output changed | Run start time and R7 `volume_confirms` row dates |

## DEV-01 Sub-sample split date rule (proposed)

- **Before** (1.3): "median calendar date of the pair's sample period, rounded to the preceding 31
  December. For `DJ` ... the split is 2009-12-31 ... For `SP_IYT` ... 2015-12-31."
- **Problem:** the median date of 1992-01-02..2026-11-06 is 2009-06-04, so "preceding 31 December"
  is 2008-12-31, not the stated 2009-12-31. The same holds for `SP_IYT` (2014-12-31 vs 2015-12-31).
- **Implemented:** the explicit example dates, i.e. 31 December of the year that contains the median
  date (`events.split_date`, tested). R11 checked that R1 sub-sample signs are unchanged under
  either split and that no other rule's label depends on it.
- **Recommended v3 text:** "31 December of the year containing the median calendar date".

## DEV-02 Literature label lookup (proposed clarification, applied between the two persisted runs)

- **Before** (3): the literature label is carried from `research/canonical_rules.md` by `rule_key`.
- **Finding:** the registry contains `two_average_confirmation` only; the other seven protocol keys
  are absent because the registry uses finer keys (`secondary_retracement_lower`, ...). Exact
  matching would give `unresolved` for seven rules.
- **Implemented** (`labels.RULE_ENTRIES`, `resolve_literature`; requested by the lead): each protocol
  key maps to registry ids. The label is `literature-disputed` if any mapped row is disputed, else
  `literature-consensus` if all are consensus, else `single-source`. Ids are listed in the notes.

| protocol key | registry ids |
|---|---|
| trend_persistence | R-016, R-017 |
| primary_reversal_signal | R-018, R-020 |
| two_average_confirmation | R-032, R-033, R-034 |
| secondary_retracement | R-008 to R-011 |
| secondary_duration | R-006, R-007 |
| line_breakout | R-022 to R-027 |
| volume_confirmation | R-037, R-038, R-041 |
| hamilton_timing | R-062 |

- **Effect:** none on data labels; only the `literature_label` column and status-table column.

## DEV-03 Two-sample sub-sample `n` (proposed)

- **Before** (1.3, 3): sub-sample consistency needs "`n >= 10`" per sub-sample; for two-sample rules
  (R3) the unit is unstated.
- **Implemented:** sub-sample `n` = events of both groups in that sub-sample, and 0 (not
  assessable) when either group is empty there, because the difference is then undefined.

## DEV-04 Random-placement details (proposed)

- **Before** (1.2): "draw the same number of event bars uniformly at random from eligible bars
  (respecting the sample's minimum spacing between actual events)".
- **Implemented:** bars drawn uniformly without replacement from the contiguous range
  `[first non-UNDEFINED bar, last bar with F_h defined]` subject to a pairwise gap of at least the
  smallest gap between the actual events (exact stars-and-bars sampling). The observed signs are
  randomly re-assigned in every draw. R6 `excess` uses all bars with `F_h` defined as the pool.
  Pooled `^DJI`+`^DJT` rows carry a CI but no p-value.

## DEV-05 R7 sample start versus swing history (proposed)

- **Before** (2): "`^DJI` bars from 2000-01-03 onward only".
- **Implemented:** swings and trend states are computed on the full history (no warm-up artefact at
  2000); only leg pairs whose first leg starts on or after 2000-01-03 count. The row `period_start`
  is 2000-01-03. Truncating the price history at 2000 instead would change the states.

## DEV-06 Bonferroni bound for non-proportion metrics (proposed)

- **Before** (1.4, 3): `bound_bonf` is "the one-sided `(1 - alpha/8)` confidence bound of the effect
  in the predicted direction".
- **Implemented:** all predicted directions are `>`, so the bound is an upper bound. Proportions
  (R1, R4 to R7) use the one-sided Wilson upper bound at level 0.99375. R2, R3 and R8 use the
  0.99375 quantile of the cluster / block bootstrap distribution.

## DEV-07 `decision_table_hash` value (proposed)

- **Before** (1.7): "decision_table_hash from `analysis/decision_table.sha256`", which holds two
  hashes (whole file, and text above `PROTOCOL-HASH-SCOPE`).
- **Implemented:** the whole-file hash is the column value (first line of the file, the one the
  table header describes); the scoped hash prefix goes into `notes` as `table_scoped=`. The harness
  recomputes both and refuses to run if neither matches the stored file.

## DEV-08 R8 details (proposed)

- Sub-sample `n` for the consistency check = number of position changes inside the sub-sample (the
  rule's `n` is trades). Sub-sample estimates are the Sharpe difference on that sub-sample's bars.
- Calls: a call is made at every bar where the pair-confirmed PRIMARY state differs from the
  previous bar's (including after a gap of non-confirmation); the next call is the next such bar.
- Random-spell null: the executed position series is cut into spells, the spell order is permuted
  2000 times, costs are recomputed, and `p_spell = (1 + #{delta* >= delta_obs}) / (B + 1)`.

## DEV-09 Reversals matched later than `c + h` appear in both R3 groups (proposed)

- **Before** (R3 Groups): a signal with no match by `c + h` is *single*; "a signal matched later
  than `c + h` is a confirmed event at its own `confirmed_ts`".
- **Consequence:** such a reversal enters the *single* group at `c` and the *confirmed* group at its
  match date, so one reversal contributes to both groups and `n_total` counts it twice. On `DJ`
  with `h = 60` three of twelve `^DJI` reversals are in this position. The permutation test treats
  all 15 events as exchangeable.
- **Implemented:** as worded. Flagged for R12; the alternative is to drop such reversals from the
  single group.

## DEV-10 R1 label null (recommendation for v3; no change to the v2 label)

- **Finding** (R11 audit F1): the pre-registered null `p_extend = 0.5` is not a random-walk
  baseline. Drift-matched random walks run through the same machinery give `p_extend` of about
  0.65 to 0.69 (auditor: iid 0.654, zero drift 0.633, block bootstrap 0.695, with P(>= 0.8788) of
  about 0.0005, 0.0005 and 0.0085). The harness p_sim is 0.0055 (null mean 0.691, 2000 paths).
- **Applied now:** a mandatory caveat block in `reports/rule_R1.md`, in the R1 row of
  `analysis/rule_status_table.md` and in the run JSON `notes`. Any citation must state the
  baseline 0.65 to 0.69, p_sim and n = 33, never p_holm alone.
- **Recommended v3:** pre-register the simulated null (or the analytic gambler's-ruin baseline) as
  the label null for R1. Changing it after the results would cap the label, so v2 is unchanged.

## DEV-11 R3 and R6 "single" groups (recommendation for v3; labels unchanged)

- **Finding** (R11 F4): the single groups are classified with information up to `c + h`, the
  outcome window itself. For R3 all three "single" events are reversals confirmed later than 60
  bars, so the group holds no unconfirmed reversal and `n_total` counts 3 of 12 reversals twice.
- **Applied now:** every R3 row and the R6 `single` / `conf_minus_single` rows are marked
  exploratory in the reports, the status table and the run JSON. Labels are unchanged
  (R3 is insufficient-evidence either way; the R6 label rests on the confirmed-both group only).
- **Recommended v3:** define single as "not confirmed by `period_end`" (or by a window ending
  before `c + 1`) and count each reversal once.

## Volume caveat correction (R11, no protocol change)

Section 5 says index volume is "sparse or zero before 2000". `^DJI` volume is positive on every
bar since 1992; the real feature is a level break (annual mean 21 to 99 million shares in
1992-1999 against about 205 million in 2000) and a second one in 2016/2017 (about 117 against
311 million), inside R7's sample. The reports print the section-5 text verbatim followed by this
correction. The 2000 start stays as pre-registered; v3 should reword the reason.

## INC-01 First persisted run lost rows to the ledger sorting key (bug fix, recorded)

- **Run:** `b94022285206435e83b1c068eb123dc9`, the first full label-driving run, persisted at about
  06:27 UTC against decision table `c8675eff...`. Its surviving record is
  `reports/backtest_run_20261108_062655.json`.
- **Bug:** `dow.str_rule_backtest_log` was sorted by `(rule_id, pair, run_id)`, so merges collapsed
  all 394 rows to 16 `n/a` rows; the 8 label-driving rows were lost from the database. The 16
  survivors are kept in `dow.str_rule_backtest_log_v2` after the migration
  (`scripts/migrate_rule_log_v2.py`, sorting key now includes `metric_name`).
- **Rows invalidated:** all rows of that run id except the 16 survivors. None was deleted by
  hand.
- **Rerun:** `a6d2d48e46014e7da3cc7c6be7ce8a02`, same code and data, identical data labels and
  estimates (the second run only added the literature mapping of DEV-02 and the refutation-bound
  notes). It is the run of record; 394 rows are in the ledger.
- **Not a protocol deviation** (section 6: an implementation fix that makes the code match the
  document), recorded here with the rows it invalidated.

## FIX-01 Scoped hash tooling (tooling fix)

`protocol.scoped_sha256` matched the first `PROTOCOL-HASH-SCOPE` in the file, the prose mention on
line 5, and so hashed only the first four lines (`3f6d676b...`). It now anchors at a line starting
with `PROTOCOL-HASH-SCOPE:` and reproduces the stored `35de767a...` (unit test). The ledger notes of
both persisted runs carry `table_scoped=3f6d676bcd4c`, which is not a protocol hash. The effective
protection of both runs was the whole-file hash `c8675eff...`, which matched the table on disk.

## FIX-02 Run start time and R7 volume row dates (no persisted number changed)

`BacktestRun.started` was set when the run finished; it is now the start time (the existing JSON
and status table were corrected in place from `finished - runtime`). The R7 `volume_confirms`
descriptive rows were dated at the last bar; they are now dated at the confirmation bar of the
window. This only affects the (unstored) sub-sample assignment of that descriptive row; its value,
n, CI and p are unchanged.
