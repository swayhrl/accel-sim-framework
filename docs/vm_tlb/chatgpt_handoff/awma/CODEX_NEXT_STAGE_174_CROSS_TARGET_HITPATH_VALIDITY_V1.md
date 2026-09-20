# CODEX NEXT STAGE — 174 Cross-Target Repaired Hit-Path Validity V1

Date: 2026-09-20

Mode:

`GOAL MODE / solve-and-continue`

Node:

`174-new`

Stage:

`AWMA_174_CROSS_TARGET_REPAIRED_HITPATH_VALIDITY_V1`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

Read first:

1. `CURRENT_STATE.md`
2. `EXECUTION_PRIORITY_POLICY_V2.md`
3. `CANDIDATE_SIDE_LANES.md`
4. `174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`
5. this Goal

Suggested execution branch:

`hrl/awma-174-cross-target-hitpath-validity-v1`

## 0. Hard prerequisite

Do not start new simulation until V4 publication is truly remote-closed.

Require:

`hrl/awma-174-hitpath-v4-provenance-closeout-exec`

to resolve to the actual zero-science closeout HEAD containing the final V4 report and:

- `REPAIRED_HIT_PATH_LATENCY_MATRIX_V4.tsv`
- `TARGET_DELTA_METRICS.tsv`
- `COVERAGE_INVARIANTS.tsv`
- `MODEL_VALIDITY_ENVELOPE.md`
- `RUN_RECEIPTS.json`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

If the ref still resolves to `c8657cf...` without these files, STOP this Goal as:

`BLOCKED_BY_174_V4_REMOTE_PUBLICATION`

Do not rerun V4 science.

## 1. Scientific objective

Question:

> Does the repaired simulator's large translation hit-path sensitivity appear across representative AI kernel classes, or is it specific to Q05 Attention?

This is model-validity characterization, not a mechanism experiment.

## 2. Frozen target set

### T0 — Attention anchor

`Q05_PREFILL_ATTN_FLASH`

Reuse published V4 repaired/contextual evidence.

Do not rerun T0 unless a tiny exact control is required for parser/schema compatibility.

### T1 — Prefill GEMM

Target ID:

`PREFILL_GEMM_PRIMARY_OCC0`

Producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

Durable producer bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native_prefill-gemm-primary-occ0_20260918T052739Z_01540d931e17`

Frozen producer facts:

```text
raw records                = 12,043,648
memory instruction records = 2,298,240
effective lane addresses   = 70,352,896
64 KiB VM-entry pages      = 495
```

No recapture.

### T2 — Decode GEMV

Target ID:

`DECODE_GEMV_PRIMARY_STEP16`

Producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

Durable producer bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_decode-gemv-primary-step16_20260918T074437Z_b0dfb1af1ae1`

Frozen producer facts:

```text
raw records                = 1,515,136
memory instruction records = 318,592
effective lane addresses   = 9,022,720
64 KiB VM-entry pages      = 135
```

Step16 was preselected as the middle point of the already accepted stable primary GEMV decode family.

No result-driven target substitution.

## 3. Runtime authority

Reuse the repaired runtime semantics qualified in V4.

Required:

- exact loaded repaired core authority;
- exact repair marker/coverage support;
- natural baseline L1/L2 lookup = 10/80;
- no new VM/TLB/cache functional semantics.

If a rebuild is required for engineering reasons:

- rebuild using the already qualified V4 build/load path;
- prove loaded-core SHA/build-id;
- run only the smallest load canary before science.

Do not change simulator source semantics to make T1/T2 run.

## 4. Input admission

For T1 and T2 independently:

1. validate producer manifest/hash;
2. validate simulator grammar/terminal completion;
3. bind a new target-specific `SIM_INPUT_ID`;
4. record exact kernel identity;
5. verify no drop/overflow/truncation.

A target that cannot be admitted without changing trace semantics is task-local:

`TARGET_NOT_ADMITTED`

Continue the other target.

## 5. Per-target repaired qualification

Before lookup overrides, run one complete repaired natural 10/80 replay.

Require:

- natural completion;
- all VM-eligible downstream admissions translated;
- untranslated = 0;
- unobserved = 0;
- post-ready retranslation = 0;
- target completion identity stable.

Admission counts are target-specific and should be derived from the run, not copied from Q05.

If coverage fails:

`STOP_SCIENTIFIC_<TARGET>_REPAIRED_COVERAGE_FAIL`

Freeze that target and continue the other.

## 6. Minimal hit-path matrix

For each admitted T1/T2 target run:

### Required R0
`10/80`

### Required L1-zero
`0/80`

### Required zero/zero
`0/0`

All overrides are target-only.

No predecessor-kernel context is assumed.

Label all T1/T2 results:

`REPAIRED_ISOLATED_SCREEN`

### Conditional I0

Run target-I0 only if the already-qualified target-I0 diagnostic path transfers exactly to the new target identity without new functional semantics.

If not:

`I0_NOT_RUN_CONTRACT_NOT_TRANSFERRED`

Do not implement a new idealization just to fill the table.

## 7. Metrics

Per target/point collect:

- target cycles;
- target instructions/CTA completion;
- downstream admissions;
- translated/untranslated/unobserved;
- L1 lookup launches/hits/misses;
- L2 lookup launches/hits/misses;
- L1 lookup service;
- L2 lookup service;
- MSHR alloc/merge/full/HWM;
- walks;
- PWC;
- PTE;
- requester total latency;
- requester MSHR wait;
- L2 data accesses/misses;
- DRAM/PTE memory evidence when available.

All values must be target-boundary deltas.

## 8. Derived target descriptors

For each target compute:

```text
L1_HIT_RATE
L2_HIT_RATE_GIVEN_L1_MISS
WALKS_PER_1K_LOOKUPS
LOOKUPS_PER_MEMORY_INSTRUCTION_RECORD
LOOKUPS_PER_1K_EFFECTIVE_LANE_ADDRESSES
L1_ZERO_DELTA_CYCLES = cycles(10/80) - cycles(0/80)
L1_ZERO_DELTA_FRAC_R0
ZERO_ZERO_DELTA_CYCLES = cycles(10/80) - cycles(0/0)
ZERO_ZERO_DELTA_FRAC_R0
```

If I0 exists:

```text
TOTAL_I0_GAP
L1_ZERO_AS_FRACTION_OF_I0_GAP
ZERO_ZERO_RESIDUAL_VS_I0
```

Do not convert requester-cycle sums directly into GPU exposed stall cycles.

## 9. Cross-target table

Create:

`CROSS_TARGET_HITPATH_VALIDITY.tsv`

Rows:

- T0 Q05 contextual repaired anchor;
- T1 Prefill GEMM isolated repaired screen;
- T2 Decode GEMV isolated repaired screen.

Columns must distinguish:

- contextual vs isolated;
- phase/operator family;
- producer memory/page descriptors;
- simulated translation descriptors;
- modeled latency-sensitivity descriptors.

Do not compare absolute simulator cycles across different kernels as if they were normalized performance.

## 10. Interpretation boundary

This Goal may report evidence for:

- systematic modeled hit-path sensitivity;
- target-dependent sensitivity;
- Attention-specific sensitivity;
- need for simulator semantic recalibration.

It must NOT:

- claim RTX4080 TLB lookup latency;
- propose a new TLB/PTW mechanism;
- tune TLB capacity/ports/walkers/PWC/page size;
- start cache mechanisms.

## 11. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/CROSS_TARGET_HITPATH_VALIDITY_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_174_CROSS_TARGET_HITPATH_VALIDITY_V1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
RUNTIME_AUTHORITY.json
TARGET_INPUT_AUTHORITY.tsv
TARGET_COVERAGE_INVARIANTS.tsv
TARGET_HITPATH_MATRIX.tsv
TARGET_DELTA_METRICS.tsv
CROSS_TARGET_HITPATH_VALIDITY.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

## 12. Mandatory remote closeout

Apply `174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`.

Before final COMPLETE:

- node164 durable closure;
- commit;
- push;
- fetch;
- remote HEAD == local HEAD;
- remote tree contains all required files;
- worktree clean.

Success:

`AWMA_174_CROSS_TARGET_REPAIRED_HITPATH_VALIDITY_V1_COMPLETE_WITH_SCOPE`

STOP and return to ChatGPT.
