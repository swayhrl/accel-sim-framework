# E-notice → incremental D projection

This extends `full_v2_analysis.py`, using the existing `sync_intake.analyze_pair`, exact receipt pointers and `full_v2_analysis.qualification`. It does not implement a second acceptor or invoke native validation. `control_incremental.py` is a one-shot paper/plot adapter. No polling service or second controller is started.

For each E2 `*_D_INCREMENTAL_NOTICE.json`, invoke from the original D worktree with a **new** output revision (replace `accepted_snapshot_02` if already used):

```bash
/usr/bin/python3 util/ep_l2/mechanism_study_lane_d/control_incremental.py \
  --plan docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/controls_20261020_r1/APPROVED_ANALYSIS_PLAN.json \
  --out docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/controls_20261020_r1/accepted_snapshot_02 \
  --cache docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/controls_20261020_r1/accepted_snapshot_01 \
  --cache docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/four_pairs_20261020_r2 \
  --render
```

Add the previous latest snapshot as the first `--cache` on subsequent calls. Cache manifests and per-observation raw hashes bind reused snapshots; current accepted receipt bytes are still checked on every invocation. Only newly accepted raw logs need decoding. This run reused all eight original S/F snapshot observations and read **zero raw log bodies and zero trace bodies**. Each E control is handled independently; missing endpoints stay UNKNOWN and do not block other controls.

## Current-boundary checks

The canonical shared registry is read once under its shared lock. Its campaign, owner and authority are checked. E's current MAIN pairs are projected through existing full-V2 intake. Every control must have its own explicit current E `accepted_pairs` declaration and exact `accepted_results` endpoint references. The adapter checks the predeclared anchor attempt/receipt against the current MAIN endpoint, each endpoint's current qualification, the exact prepared control identity (including config/input/source/feature/ideal/termination), profile, selection and comparison invariant. No qualification transfers from S/F to a control. All ten prepared E qualification pointers were independently read as **current E-qualified pointers**, not rerun or newly qualified by D.

`APPROVED_ANALYSIS_PLAN.json` binds ten exact E plans/specs and E commit `eb889b4077c43cca591afbc5c05eee6beffe5d73`; four revision approvals remain subject to E's stopped-boundary adoption and resource gates. This adapter cannot launch a run or authorize a condition. DWT F_MINUS_R and SAD W_ONLY are expressly outside this plan. Unlisted accepted pairs do not enter this control projection.

## Outputs

* `CONTROL_ACCEPTANCE_AND_ANCHORS.csv`: ten conditions, exact predeclared anchor, acceptance status, accepted endpoint cycles and signed control-minus-anchor difference. A qualification/preparation record alone yields no result.
* `CURRENT_ENDPOINT_IDENTITIES.csv`: current S/F and accepted controls, exact binary/source/input/config/run-key/qualification/receipt/attempt identities. A withdrawn MAIN anchor removes dependent controls and all derived comparisons from current output.
* `CONDITIONAL_COMPARISONS.csv`: original four MAIN contrasts plus the specified conditional control contrasts; endpoint receipt IDs and the signed right-minus-left cycle delta. Derived cross-control differences are clearly **D arithmetic on E-accepted endpoints**, not newly E-accepted pairs.
* `CONTROL_KERNEL_TIMING_AND_SNAPSHOTS.csv`: identical named-kernel sequences joined using the existing observation helper; adjacent cumulative counter deltas, separate endpoint clock lines, elapsed GPU duration differences and final residual. Every completed contrast must close to its exact whole-program cycle difference. Clock/sequence mismatch holds only the timing join, not E's acceptance.
* `RAW_MECHANISM_COUNTS.csv`: existing `mechanism_table` output, relabeled **left/right profiles**, not generic S/F for a control. Records retain per-reason nonexclusive wait boundaries; peaks and missing/OFF records are not silently summed or filled with zero.
* `INCREMENTAL_SUMMARY.json`: current acceptance count, exact registry/plan hashes, cached/new observation provenance, held timing joins, RO four-corner values and signed interaction. Any missing/withdrawn corner leaves the interaction UNKNOWN.
* PDF/PNG performance and conditional endpoint plots; missing control bars remain explicitly pending. Four-pair interim GM never becomes the complete seven-input mean.

In the RO grid, `C00=F_MINUS_R`, `C10=WV_T`, `C01=WV_M`, `C11=F`. Report `C10−C00`, `C11−C01`, `C01−C00`, `C11−C10` separately as applicable; the signed interaction is `C11−C10−C01+C00`. Negative cycle change means faster right endpoint. No sum of request/slice/reason waits is used as elapsed GPU stall time.

All outputs are analysis evidence only. E remains qualification/acceptance and execution owner. There is no claim that D continues monitoring after this Codex turn ends; the next E notice or continuation invokes this bounded adapter again.
