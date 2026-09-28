# Lane 4 terminal review contract V1

This contract prepares the review after Lane 4 publishes a terminal pack. It does not inspect active output, change Lane 4 gates, admit a speculative diagnostic now, or produce a scientific result row. The frozen Lane 3 V1 branch remains `a402828860ced26124ddbf3c9d87baa6f6774d55`; a formal Paper/Evidence V2 waits for terminal project review.

## Immutable source and scope

| Identity | Frozen value / authority |
|---|---|
| Core execution commit | `0271de82432db004beed43280ed01057246a0f2c` |
| Core execution binary SHA256 | `6be0986958ffbb8a128ce19e8a88b53a4c4838f97202c2f3d1c9dec6e9a02186` |
| Lane 4 framework snapshot | `8dfd9c0fdc98314c2aa11710da9b89f59e4c7a66` |
| `RUN_MATRIX.json` SHA256 | `b1d0610a79cecea552502b9c3f8e06ba679cdd965170e39b3068ac12848e0d20` |
| R0 config SHA256 | `a8918f1407fc2a9146808625b55a5120f64bb2cf4ce8b6a5b399ac4654d36d96` |
| M1 B16 config SHA256 | `15e06af19200e7fb40af93c6a21b19290b581c327f420dd3fdefc3f4b3af3bdd` |
| Diagnostic config SHA256 | `12434fee397093b2ac13cf65e1b2644b8f7a98ad97e3824a2cbfae5aba5daee7` |
| selected kernelslist SHA256 | `f9a952e2d52420a850dc28554be208a2dd1d7894260d8bff87153637740a5ae8` |
| RTX 4080 platform config SHA256 | `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8` |
| oracle sidecar SHA256 | `6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6` |
| reuse scope SHA256 | `3861e58b45851e1aa94660d2473df2ee475a9135d9c475724d07010ed529ce31` |
| selected sequence SHA256 | `c3bb16d8f40eabdd09c165c7ff7c31ad2ce7aac2f5b7548a639d87dec493a6be` |
| source manifest SHA256 | `db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389` |
| selected scope | 1565 kernels: D1 2926–4430 and D2 prefix 4431–4490; 1,259,187 CTA in the scope contract |

These values were checked against the committed `RUN_MATRIX.json`, `REUSE_WINDOW_SCOPE.json`, sequence, configs and sidecar at the frozen source commit. The expected binary SHA is from committed `HOST_SCALE_AND_TELEMETRY_QUALIFICATION.json` (file SHA256 `0027d43827f8227d6da34e77a093371b95e92b376f74f2b845bf52cdc4fbda63`); `run_b16_reuse_followups.sh` already gates primary and diagnostic receipts on the same exact Core and binary. The terminal receipt's actual binary SHA must **equal** `6be0986958ffbb8a128ce19e8a88b53a4c4838f97202c2f3d1c9dec6e9a02186`; a well-formed but different 64-hex digest fails `IDENTITY_MISMATCH`. Trace instruction records and simulator executed-thread instructions are different quantities and are not required to equal each other.

## Fixed review order

| Order | Gate | Required proof | Failure action |
|---|---|---|---|
| 1 | Git/source authority | Exact commits, committed pack, source/raw SHA and review history | Stop on missing or drifted authority |
| 2 | Binary/config/trace identity | Binary SHA, Core commit, all config/sidecar/list/scope/manifest hashes above | Identity mismatch fails review before timing |
| 3 | Terminal receipt | R0 and M1 final receipt, exit 0 and terminal marker; diagnostic receipt when interpreted | Missing receipt rejects partial packet; failed primary quarantines diagnostic |
| 4 | Exact reuse-window scope closure | Exact 1565 ordered kernels, no filtering/reordering, frozen D1/D2 boundaries and sequence | Stop on scope mismatch; do not relabel the window as full steady-state decode |
| 5 | R0/M1 workload identity | Same executed kernel sequence, kernel count, simulator instruction count and CTA count | Primary failure; diagnostic quarantined |
| 6 | Primary correctness | Accepted R0/M1 comparison and no fail-open; identity is necessary but not sufficient | Primary failure; diagnostic quarantined |
| 7 | Primary timing interpretation | Accepted `C_window`, `C_D2_prefix`, `C_L0_up_D2` cycle pairs; arithmetic response only until materiality authority exists | Reject incomplete timing; do not claim material speedup by sign alone |
| 8 | Diagnostic admission | **Primary terminal PASS AND primary workload identity PASS AND primary correctness PASS**, plus diagnostic terminal and neutrality/counter qualification | Any primary failure gives `QUARANTINE_DIAGNOSTIC` |
| 9 | Diagnostic counters | Protected admission, protected→protected churn, class-1 occupancy survival, denial reasons; old-address survival only if exact old-generation data exists | Normalize observed counts; mark unobserved address survival `UNKNOWN` |
| 10 | Project-level interpretation | Review primary and diagnostic evidence against frozen decision template and strong baselines | A/B/C/D remain `REQUIRES_PROJECT_REVIEW` without existing numeric rules |

`M1_B16_DIAGNOSTIC` is currently `SPECULATIVE_PRE_GATE`. Execution concurrency does not equal scientific admission. A diagnostic alone never selects a branch or validates M1. The frozen `B16_DECISION_TEMPLATE.md` calls for prior materiality/dispersion rules; the Lane 4 source at `8dfd9c0f` explicitly records `arithmetic_sign_only_no_preregistered_materiality_threshold: true`. This is a missing automatic-classification authority, not permission to choose a threshold after seeing a result. Existing native thresholds do not silently become simulator thresholds.

## A/B/C/D preregistration without a post-result threshold

| Candidate | Required pattern after admission | What it could mean | Permitted next discussion |
|---|---|---|---|
| A | High protected→protected churn **and** low old-address/old-class survival | Reuse-survival limitation | Review M1F first as a conditional follow-up |
| B | Low churn, good old-address survival, no timing gain | Survival/fairness is not the missing ingredient | Review critical-path coverage, reuse value and collateral cost; do not run M1F merely because built |
| C | High old-address survival and positive local/window timing | M1 may already be sufficient | Compare strong baselines before adding M1F complexity |
| D | Low target protection because hard admission denial dominates | Admission realization failure | Decompose `QUOTA_FULL_BASELINE_INVALID_PRIORITY` and `QUOTA_FULL_NO_LOCAL_PROTECTED_VICTIM` first |

The current canary schema exposes class-1 occupancy at checkpoints and aggregate counters. Class occupancy is **not** an exact old-address survival census: an old line may be evicted and a new line of the same class filled. Unless terminal evidence binds old-generation address identity, the evaluator leaves `old_address_survival_fraction` null. It reports raw normalized metrics and candidate interpretations, while every A/B/C/D label stays `REQUIRES_PROJECT_REVIEW`.

## CPU-only evaluator boundary

`util/vm_tlb/c16/e1_lane4_terminal_review.py` accepts only a committed `TERMINAL_REVIEW_PACKET.json` under a C16 E1 review pack. Its schema is `C16_LANE4_TERMINAL_GATE_SCHEMA_V1.json`. It never reads a run directory, parses active partial output, writes a paper result row, or supplies numeric high/low/material thresholds. Synthetic tests exercise A/B/C/D routing and invalid/partial/quarantine behavior; those test signals are not experiment evidence. The packet publication and independent raw review must precede formal use.

The first scientific decision after Lane 4 terminal is a human project review against this order. Formal Paper/Evidence V2 remains separately gated.
