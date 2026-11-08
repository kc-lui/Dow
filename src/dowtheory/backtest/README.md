# Rule-level backtest harness

Implements `analysis/decision_table.md` (pre-registered protocol) exactly; the table is hashed and
the harness refuses to run when `analysis/decision_table.sha256` matches neither the whole file
nor the text above `PROTOCOL-HASH-SCOPE`. Label-driving runs also require the committed
`config_hash` pinned in section 0 of the table.

| module | role |
|---|---|
| `protocol.py` | protocol constants, hash checks, verbatim caveat extraction |
| `events.py` | event sets from P3 objects (`confirmed_idx`, `Signal.idx`, `confirmed_ts`), forward returns `F_h(c) = ln(P[c+1+h]/P[c+1])`, sub-sample split |
| `stats.py` | exact binomial, Wilson, cluster bootstrap, random placement, permutation, stationary block bootstrap, Holm; fixed seed 20261108 |
| `results.py`, `rules.py`, `nulls.py` | `RuleResult` rows, `R1`..`R8`, simulated nulls (R1 drift-matched walk, R8 random spells) |
| `labels.py` | `decide_label`, `label_all`, canonical-rules lookup (protocol section 3) |
| `runner.py`, `reporting.py`, `ledger.py` | specification grid, labelling, markdown/JSON outputs, `dow.str_rule_backtest_log` rows |

```
dow backtest --pair DJ --pair SP_IYT --persist --workers 8      # about 2 minutes
dow backtest --pair DJ --source csv --csv a.csv --csv-pair b.csv --no-sweeps --out /tmp/out
```

Outputs: `reports/rule_R<n>.md` (`_<PAIR>` suffix for non-label pairs), `reports/backtest_run_<ts>.json`,
`analysis/rule_status_table.md` (only when `DJ` ran). Labels exist for `DJ` only. `--no-sweeps` skips
the robustness grid; R4 and R5 then still use the five-point `secondary_pct` grid for their labels.
Interpretation choices where the table is silent are listed in `analysis/protocol_deviations.md`.
