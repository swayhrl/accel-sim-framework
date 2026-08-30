# EP-L2 D512 Promotion Fanout Handoff

Date: 2026-08-30

Authoritative upstream state:

```text
D512_PREFLIGHT_PASS
D512_READY
D512_MIRROR_COMPLETE
26/26 PROMOTED_VALID_CALIBRATION
```

Exact promoted parent:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
runtime config composite SHA-256
a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416
```

This handoff authorizes **promotion/documentation only** for already-computed exact matching Lane-C/E descendants. Do not rerun them merely because the promotion gate was previously pending.

## Lane B closeout patch

Read:

```text
docs/ep_l2/chatgpt_handoff/LANE_B_FINAL_CHATGPT_REVIEW.md
```

Perform only the three non-rerun packaging fixes there:

1. correct D256 scan-equivalence gate dependency metadata;
2. publish `docs/ep_l2/calibration/contracts/D512_BASE.json` using `EP_L2_CALIBRATION_CONTRACT_V2`;
3. remove ambiguous `dram_bandwidth_util` naming in review-facing machine-readable analysis and distinguish lower admission from native physical bus utilization.

Do not run any new Lane-B simulator job.

## Lane C — promote and final-package, no rerun

Read:

```text
docs/ep_l2/chatgpt_handoff/LANE_C_CHATGPT_INTERIM_REVIEW.md
```

Verify every D512 META/BANK row has the exact promoted parent identity above. If so:

```text
SPECULATIVE_PENDING_GATE -> PROMOTED_VALID_CALIBRATION
```

for all 14 exact matching D512 descendants without rerun.

Then publish compact review-facing evidence inside:

```text
docs/ep_l2/review_packs/L1_CAUSALITY_CALIBRATION_r1/
```

including at least:

```text
D256_L1_CAUSALITY_COMPARISON.csv
D512_L1_CAUSALITY_COMPARISON.csv
L1_TEMPORAL_SUMMARY.csv
final promotion/run status
config-diff evidence
```

Publish Lane-D V2 contracts for:

```text
D256_META_HR
D256_BANK_HR
D512_META_HR
D512_BANK_HR
```

Each contract must bind the actual runtime config composite SHA-256, source lineage, allowed config fields, PASS equivalence/config-delta evidence, and normalized effective config.

Then set Lane C final local status:

```text
L1_CAUSALITY_SCREEN_COMPLETE
```

and request final ChatGPT review. No simulator rerun is required unless exact candidate/config identity fails.

## Lane E — promote and close, no rerun

Read:

```text
docs/ep_l2/chatgpt_handoff/LANE_E_CHATGPT_REVIEW.md
```

Verify the D512 MSHR128 parent and D512 MSHR256/spmv descendants use the exact promoted Lane-B parent above. If so, promote the exact matching D512-derived Lane-E rows without rerun and update the pack/workboard.

Final Lane-E status may become:

```text
LINE_MSHR_CAUSALITY_PROBE_COMPLETE
```

with accepted scientific classification:

```text
MSHR_ADMISSION_THROTTLE_DOWNSTREAM_LIMITED
```

Do not promote MSHR256 to the primary baseline and do not implement RO/TVD/Unified.

Lane-E MSHR256 is a separate sensitivity result and does not need to be forced into Lane-D's existing D×L1 contract matrix unless a later analysis-extension decision explicitly requests it.

## Lane D — joint calibration after contracts arrive

Once Lane B publishes `D512_BASE.json` and Lane C publishes the four L1 contracts, Lane D may ingest:

```text
D256_BASE
D512_BASE
D256_META_HR
D256_BANK_HR
D512_META_HR
D512_BANK_HR
```

using the already-reviewed V3 analyzer with no semantic changes except bug fixes.

Generate the accepted joint calibration deltas and a convergence summary that incorporates Lane-E's separately reviewed Line-MSHR sensitivity as external causal evidence.

Do not independently declare `BASELINE_DECISION`; prepare the evidence and request ChatGPT/user decision.
