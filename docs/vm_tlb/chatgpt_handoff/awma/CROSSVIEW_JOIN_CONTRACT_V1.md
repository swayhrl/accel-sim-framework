# AWMA Cross-view Join Contract V1

Date: 2026-09-20
Status: ACTIVE FOR MAINLINE

Stage:

`AWMA_CROSS_TARGET_HITPATH_VALIDITY_AND_NATIVE_CROSSVIEW_V1`

## 1. Exact target set

```text
T0  Q05_PREFILL_ATTN_FLASH
T1  PREFILL_GEMM_PRIMARY_OCC0
T2  DECODE_GEMV_PRIMARY_STEP16
```

All joins use relation:

`EXACT_WORKLOAD_TARGET`

only after model/scenario/phase/target identity is independently bound.

## 2. Shared identity columns

Both 109 and 174 outputs should expose:

- target_id
- model
- model_revision
- scenario
- phase
- semantic_family
- exact implementation/kernel fingerprint
- occurrence/decode_step
- producer authority
- producer run/bundle identity
- relation label

## 3. Native columns

109 should provide where supported:

- native timing source and duration statistic
- CTA/grid/block shape
- warp/record count
- dynamic memory instruction records
- effective lane addresses
- unique 4 KiB pages
- unique 64 KiB pages
- NCU L1/TEX bytes
- NCU L2 bytes
- NCU DRAM bytes
- occupancy/activity/utilization descriptors
- NCU protocol/selector identity

Missing or incomparable metrics must be explicit.

## 4. Simulation columns

174 should provide:

- context_class = CONTEXTUAL or ISOLATED
- repaired baseline cycles
- L1/L2 lookup config
- lookup launches/hits/misses
- walks/PWC/PTE
- downstream admissions
- coverage invariants
- requester accounting
- L1-zero cycle delta
- 0/0 cycle delta
- optional I0 gap when exact contract transfers

## 5. Valid analyses

Allowed:

- compare workload/operator descriptors to simulated hit-path sensitivity;
- compare page-footprint scale across exact targets;
- compare memory-reference density across exact targets;
- identify whether modeled sensitivity tracks native workload structure;
- identify a systematic simulator effect that is weakly related to workload structure.

## 6. Invalid analyses

Do not directly equate:

- native CUDA milliseconds with simulator cycles;
- NCU L2 bytes with simulator L2 accesses without definition alignment;
- NCU cache-control state with TLB state;
- native cache hit rates with simulator TLB hit rates;
- simulator lookup latency with hardware TLB latency.

## 7. Cross-view decision

After both tracks close, ChatGPT will review the joined evidence and classify:

- `HITPATH_SENSITIVITY_SYSTEMATIC_ACROSS_KERNEL_CLASSES`
- `HITPATH_SENSITIVITY_ATTENTION_DOMINANT`
- `HITPATH_SENSITIVITY_TARGET_DEPENDENT`
- `SIMULATOR_HITPATH_MODEL_REQUIRES_SEMANTIC_RECALIBRATION`
- `INSUFFICIENT_CROSS_TARGET_EVIDENCE`

No architecture mechanism is authorized by this contract.
