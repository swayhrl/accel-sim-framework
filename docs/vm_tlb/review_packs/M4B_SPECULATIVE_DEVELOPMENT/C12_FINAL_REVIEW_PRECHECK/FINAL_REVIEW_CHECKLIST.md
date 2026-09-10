# C12 Final Review Checklist

Use only after fetching the final source commit from `hrl/vm-m4b-speculative-v0`.

## A. Identity / provenance

- [ ] 22/22 primary points present, no F3/F4/F6/H0
- [ ] all terminal status = PASS
- [ ] Framework anchor exact match
- [ ] Core exact match
- [ ] binary SHA exact match
- [ ] same-ROI trace SHA exact match
- [ ] same-ROI registration SHA exact match
- [ ] config SHA matches frozen C11 matrix for every arm
- [ ] charged bits / geometry match frozen C11 matrix

## B. Terminal validity

For every arm:

- [ ] simulator exit = 0
- [ ] marker count = expected ROI kernel count
- [ ] telemetry count = expected ROI kernel count
- [ ] object conservation PASS
- [ ] PTE conservation PASS
- [ ] quiescence / exact-once PASS
- [ ] immutable raw-log SHA recorded
- [ ] time-v evidence recorded

## C. Canonical parser convergence

- [ ] choose one final parser revision/hash
- [ ] parser-only reparse all 22 immutable raw logs
- [ ] no simulator replay
- [ ] normalized final result table produced
- [ ] cycles / instructions / IPC unchanged relative to prior accepted parses
- [ ] any changed validation-only field explained in failure/retry audit
- [ ] C9 HIT_FIRST late-discard semantics applied consistently to all relevant F7/F8 Lseg arms

## D. Arm-specific invariants

- [ ] F1 G96 + `REFERENCE_APPROX_SUBENTRY_16`
- [ ] F5 physical PWC120 40/40/40, four-way, 64,745 total charged bits
- [ ] F7 Segment N8, 35 replicas, exact320, 65,300 bits, Lseg 5/10/20
- [ ] F8 Segment N8 + G32, 57,734 bits, Lseg 5/10/20, both labels preserved
- [ ] F9 exact656, 56,375 bits
- [ ] common modeled PPN / PA fairness unchanged across conventional and Segment arms

## E. Gate-F metric inventory

For every acceptance-required metric, identify exact artifact/column:

- [ ] performance
- [ ] L1/L2 TLB
- [ ] TLB replacement / port stalls
- [ ] MSHR alloc / merge / full / wait / high-watermark / lifetime
- [ ] walker / PWQ
- [ ] PWC counters and F5 physical geometry
- [ ] PTE request/response/L2-only/DRAM/wait
- [ ] requester latency total/max
- [ ] L1D/L2 object-aware outcomes
- [ ] L2 queue pressure
- [ ] DRAM/native-memory latency
- [ ] Segment telemetry
- [ ] Sub-entry telemetry

No missing field may be silently filled with zero.

## F. Independent numerical recomputation

- [ ] recompute all `speedup_vs_f0` from cycles
- [ ] F1 vs F2
- [ ] F5 vs F0
- [ ] F7-L10 vs F0
- [ ] F7 L5/10/20 sensitivity
- [ ] F8-L10 vs F9
- [ ] F8-L10 vs F1
- [ ] F8 L5/10/20 sensitivity
- [ ] Prefill vs Decode comparison
- [ ] never use A/C4 cycles as C5 baseline

## G. Scientific interpretation

- [ ] separate `MEASURED_FULL_ROI_FACT`
- [ ] separate `SUPPORTED_MECHANISM_SIGNAL`
- [ ] separate `UNRESOLVED`
- [ ] do not infer performance causality from miss-count reduction alone
- [ ] do not call modeled PA real hardware PA
- [ ] explain Lseg sensitivity
- [ ] explain why translation-path reductions may yield limited full-ROI speedup
- [ ] compare F7 vs F8 to isolate incremental Sub-entry value
- [ ] connect Cache/memory observations only as supported cross-layer evidence

## H. Final review-pack completeness

Expected at minimum:

- [ ] `FINAL_REPORT.md`
- [ ] `ARM_STATUS.tsv`
- [ ] `ARM_RESULTS.tsv`
- [ ] `SPEEDUP_SUMMARY.tsv`
- [ ] `TRANSLATION_MECHANISM_SUMMARY.tsv`
- [ ] `LSEG_SENSITIVITY.tsv`
- [ ] `CROSS_LAYER_SUMMARY.tsv`
- [ ] `PROVENANCE_MATRIX.tsv`
- [ ] `RESOURCE_HISTORY.tsv`
- [ ] `FAILURE_RETRY_AUDIT.md`
- [ ] `PAPER_FACING_FINDINGS.md`

## Final disposition

Only if all required gates pass:

`C12_FINAL_REVIEW_ACCEPTED`

If C12 itself has only produced its execution closeout but independent review has not yet completed, keep the distinction:

`C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW` != `C12_FINAL_REVIEW_ACCEPTED`
