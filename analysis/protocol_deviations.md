# Protocol deviations and proposed clarifications

Format per `analysis/decision_table.md` section 6. Entries below are written by R10 (backtest
engineer) **before the first label-driving run**, against decision table sha256
`c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836` (v2). They are *proposed*
clarifications: places where the table is silent, ambiguous or internally inconsistent and the
harness had to pick one reading. The protocol file was not changed. R12 decides whether to fold
them into a v3 table (new hash, before the run) or keep them as logged deviations.

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

## DEV-01 Sub-sample split date rule (proposed)

- **Before** (1.3): "median calendar date of the pair's sample period, rounded to the preceding 31
  December. For `DJ` ... the split is 2009-12-31 ... For `SP_IYT` ... 2015-12-31."
- **Problem:** the median date of 1992-01-02..2026-11-06 is in June 2009, so "preceding 31
  December" is 2008-12-31, not the stated 2009-12-31. The same holds for `SP_IYT` (2014-12-31 vs
  2015-12-31).
- **Implemented:** 31 December of the year that contains the median date. It reproduces both stated
  dates (`events.split_date`, tested).
- **Proposed text:** "rounded to 31 December of the year containing the median calendar date".

## DEV-02 Literature label lookup (proposed clarification, applied before the persisted run)

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
