# REVIEW — 174 Translation Frontend Pipelining Recalibration V1

Date: 2026-09-22
Owner: ChatGPT
Status: ACCEPTED_WITH_SCOPE / DIAGNOSTIC_ONLY

## 1. Remote authority independently verified

Execution branch:

`hrl/awma-174-translation-frontend-pipelining-v1`

Remote HEAD:

`ad6f38878bc1e7c268b17e65fdb3793a3899a84d`

The report and review pack are present in the remote tree.

The seven entries listed by the published `SHA256SUMS` were independently re-hashed from the remote file contents and all seven match exactly:

- `CANDIDATE_CROSS_TARGET_MATRIX.tsv`
- `LIVENESS_REPAIR.md`
- `RAW_DATA_INDEX.tsv`
- `README.md`
- `READY_OWNERSHIP_REPAIR.patch`
- `RUN_RECEIPTS.json`
- `SOURCE_ANCHORS.md`

## 2. Accepted input / legacy gates

The stage reports and remote evidence are consistent with the frozen authority:

- canonical V2 T0 recovered;
- legacy T0 10/80 exactly reproduced:
  - cycles = 1,654,548
  - instructions = 368,696,302
  - CTA = 224
  - unique = translated_unique = 3,090,304
  - untranslated = 0
  - unobserved = 0
  - Segment functional activity = 0;
- telemetry-only path reported neutral;
- first candidate liveness failure was traced to READY ownership;
- the bounded repair preserves default legacy consumption and makes prelaunch observe, not consume, READY state.

The first deadlocked candidate is retained as invalid implementation evidence and is not part of the scientific matrix.

## 3. Candidate matrix independently recomputed

Published candidate cycles:

| Target | Legacy 10/80 | Legacy 0/80 | V1 candidate 10/80 | V1 candidate 0/80 |
|---|---:|---:|---:|---:|
| T0 | 1,654,548 | 711,464 | 756,812 | 693,548 |
| T1 | 3,114,834 | 1,252,198 | 1,320,195 | 1,251,826 |
| T2 | 152,777 | 71,654 | 111,607 | 71,743 |

Independent sensitivity recomputation:

| Target | Legacy L1-zero sensitivity | V1 candidate sensitivity | Absolute drop | Fraction of legacy 10→0 cycle benefit removed |
|---|---:|---:|---:|---:|
| T0 | 56.9995% | 8.3593% | 48.6402 pp | 93.2918% |
| T1 | 59.7989% | 5.1787% | 54.6202 pp | 96.3294% |
| T2 | 53.0990% | 35.7182% | 17.3808 pp | 50.8598% |

Legacy 10/80 -> candidate 10/80 cycle reduction:

- T0: 54.2587%
- T1: 57.6159%
- T2: 26.9478%

Candidate 0/80 remains close to the corresponding legacy 0/80 control:

- T0: -2.5182%
- T1: -0.0297%
- T2: +0.1242%

This is a strong causal control: the candidate primarily removes positive-latency frontend amplification rather than creating a general downstream speedup.

## 4. Scientific classification

Project-level V1 classification:

`SERIAL_ACCESSQ_FRONTEND_AMPLIFICATION_PARTIAL`

Interpretation:

- T0 FlashAttention: launch-serialization amplification is strongly confirmed as dominant.
- T1 Prefill GEMM: launch-serialization amplification is strongly confirmed as dominant.
- T2 Decode GEMV: the same effect is material but not sufficient; substantial residual hit-path sensitivity remains.

Therefore the legacy 53–60% sensitivity is not a direct interpretation of a 10-cycle hardware TLB hit latency.

The V1 candidate remains:

`DIAGNOSTIC_RECALIBRATION_CANDIDATE`

It is not promoted to the accepted simulator baseline and supports no RTX4080 hardware-latency claim.

## 5. Residual T2 hypothesis to test next

Source review shows V1 pipelines lookup launch but retains serial READY application at the accessq head:

- non-head accesses may have a controller lookup already READY;
- V1 prelaunch observes READY without consuming/applying it;
- `mem_access_t.vm_translation_applied` remains false until that access reaches the existing head path;
- the repaired downstream guard therefore can still stop after the first untranslated next entry.

This is a distinct remaining frontend serialization axis:

`READY_COMPLETION_APPLICATION_HOL`

It is a plausible explanation for the larger T2 residual and must be tested before external calibration or architecture mechanism work.

## 6. Publication-pack deviations

The execution pack is scientifically usable for the six-point matrix, but it is smaller than the original V1 deliverable contract.

The following originally requested files are absent:

- `COVERAGE_TELEMETRY_SEMANTIC_REPAIR.md`
- `TELEMETRY_NEUTRALITY.tsv`
- `PIPELINED_FRONTEND_SEMANTIC_CONTRACT.md`
- `DIRECTED_PIPELINING_TESTS.tsv`
- `LEGACY_REPRODUCTION.tsv`
- `TRANSLATION_LAUNCH_CONCURRENCY.tsv`
- `HOL_STALL_ACCOUNTING.tsv`
- `RECALIBRATION_DECISION.md`

The report's `## Decision` section is also blank.

The first invalid T1/T2 “0/80” runner-config attempts are described in the README but are not represented in the published raw-data index.

These are closeout/provenance deficiencies, not grounds to rerun accepted scientific points. Do not spend a separate Codex round repairing documentation. Carry the missing provenance/decision references into the next real handoff and preserve the invalid attempts if still available.

GitHub cannot independently prove the executor's local worktree-clean state or re-hash node164-only raw logs; those remain executor-side publication assertions.

## 7. Mainline consequence

Do not start a TLB/PTW/cache mechanism.

Next stage is a bounded simulator-semantic diagnostic:

`AWMA_TRANSLATION_FRONTEND_READY_APPLICATION_RECALIBRATION_V2`

Its purpose is to test whether applying an already-READY translation result to the exact resident accessq entry before it reaches the head removes the remaining V1 completion/admission HOL effect while preserving downstream order and all accepted translation/data-path invariants.

External/reference/native calibration remains required after frontend semantic closure and before baseline promotion.
