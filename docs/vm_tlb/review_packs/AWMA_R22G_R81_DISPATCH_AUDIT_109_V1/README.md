# AWMA R22G R81 online-dispatch CPU audit V1

Stage: `AWMA_R22G_R81_DISPATCH_AUDIT_109_V1`

Final decision:
`R22G_R81_DISPATCH_NOT_JUSTIFIED_FROM_EXISTING_EVIDENCE`

This was a CPU-only retrospective audit of the accepted R81 authority. No GPU
lock, CUDA call, model execution, training, profiling, or node174 access was
used.

## What the accepted data can establish

Matched per-step A0/A3 measurements exist for every retained step and all seven
formal repetitions. Applying the frozen rule

`legal_union_fraction < 0.01 -> A3; otherwise -> A0`

gives the following head-region-only result before dispatch-signal cost:

| Cohort | Steps (A3/A0) | Favorable repetitions | Median all-A0 (ms) | Median RULE_U01 (ms) | Median per-repetition saving |
|---|---:|---:|---:|---:|---:|
| C0 shared discovery | 78 (15/63) | 7/7 | 78.053524 | 72.827530 | 7.1724% |
| C1 heterogeneous discovery | 72 (9/63) | 7/7 | 62.360171 | 59.633101 | 4.3731% |
| H0 heterogeneous, already inspected | 57 (10/47) | 6/7 | 48.077573 | 45.148896 | 6.0916% |

H0 repetition 3 was neutral/slightly negative before dispatch cost
(-0.0088%). All steps were retained. These values are not complete-generation
speedups and are not measurements of a live mixed trajectory.

The explicitly nondeployable per-step `min(A0,A3)` oracle is substantially
better than RULE_U01: its median RULE_U01 gap is 7.86%, 12.34%, and 12.24% of
RULE_U01 time for C0/C1/H0. It is reported only as an upper-bound diagnostic.

## Why the rule is not justified yet

The live R81 path has a CPU XGrammar bitmask and CPU legal-ID lists before the
head, but it does not expose `union_count` or `legal_union_fraction` then. The
union stored in the accepted ledger is computed after head execution. A live
RULE_U01 implementation must add one of:

- a CPU union/unique reduction over the already materialized legal-ID lists; or
- a new bitmask OR plus popcount path.

Neither cost has an accepted measurement. The operation must run on every step,
including the 47--63 broad steps per cohort that ultimately choose A0. The
accepted A0/A3 head timings do not include this pre-dispatch reduction, so its
cost is `UNKNOWN`, not zero. A live mixed trajectory, arm-transition behavior,
and reuse of the upstream legal-ID materialization were also not measured.

The retrospective signal is favorable enough to motivate one bounded future
validation, but existing evidence cannot establish positive deployable net
benefit. This closes the present audit without a hardware claim.

## Files

- `ONLINE_SIGNAL_AVAILABILITY.md` — exact signal timing and residency.
- `RULE_U01_CONTRACT.md` — frozen rule and claim boundary.
- `COST_OWNERSHIP.tsv` — included, excluded, and unknown costs.
- `RULE_U01_RETROSPECTIVE.tsv` — all seven matched repetitions and medians.
- `BEST_OF_ORACLE.tsv` — explicitly nondeployable per-step oracle.
- `RULE_U01_STEP_CLASSIFICATION.tsv` — deterministic step classification.
- `SOFTWARE_CAPABILITY_DELTA.md` — XGrammar/Kestrel/FlashSampling/A3 audit.
- `NEXT_STEP_PROPOSAL.md` — the single unexecuted future validation design.
- `PARENT_AUTHORITY.json`, `AUTHORITY_VERIFICATION.json` — authority closure.
- `RAW_DATA_INDEX.tsv`, `SHA256SUMS` — file provenance and pack integrity.
