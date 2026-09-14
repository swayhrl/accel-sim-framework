# CUTLASS identity and coverage audit V1

## Result

No recovered artifact establishes a reproducible actual code-object identity for either required CUTLASS function. The existing failed-closed result remains intact. The fatbin registries were recovered and hash-closed, but neither is an admissible function-to-image binding. No default DSO, spelling, geometry, or kernel-name inference is used.

## Recovered observer evidence

| phase | exact function | status | terminal reason | CULibrary chain |
|---|---|---|---|---|
| PREFILL | `_ZN7cutlass7Kernel2I66cutlass_80_tensorop_f16_s16816gemm_relu_f16_128x128_32x5_tn_align8EEvNT_6ParamsE` | FAILED_CLOSED_CODE_OBJECT_IDENTITY_UNRESOLVED | module_owner_not_observed | ABSENT_NO_OBSERVED_CULIBRARY_MODULE_CHAIN |
| DECODE | `_ZN7cutlass7Kernel2I66cutlass_80_wmma_tensorop_f16_s161616gemm_f16_16x16_128x1_tn_align8EEvNT_6ParamsE` | FAILED_CLOSED_CODE_OBJECT_IDENTITY_UNRESOLVED | module_owner_not_observed | ABSENT_NO_OBSERVED_CULIBRARY_MODULE_CHAIN |

## Registry audit

- `/root/share/c16_recovery_v3/raw/llama32_1b/S0/ROUTE_B_V122_CUTLASS_OWNER_PREFILL/89d3eb7c-3b5f-44f0-bf2e-9df8cd969b87/raw/FATBIN_OWNER_REGISTRY.tsv` — 6533127 bytes, SHA256 `338c920864b204f7062ef7962924cb754b4e76eeef127c5d7671f547a8c9a382`, exact unresolved-function text present: `False`.
- `/root/share/c16_recovery_v3/raw/llama32_1b/S0/ROUTE_B_V122_CUTLASS_OWNER_DECODE/f69bc1a7-55df-47fb-ad46-e0f79b7bb944/raw/FATBIN_OWNER_REGISTRY.tsv` — 6533127 bytes, SHA256 `338c920864b204f7062ef7962924cb754b4e76eeef127c5d7671f547a8c9a382`, exact unresolved-function text present: `False`.

The registry cannot by itself prove an observed `CUmodule -> immutable image bytes/hash -> target CUfunction` relation. Therefore it is not a new identity path.

## Frozen coverage sensitivity

### PREFILL

- Full frozen denominator: 35,333,473 ns
- Failed CUTLASS duration: 13,488,636 ns (38.1752%)
- MAPPED_EXACT lower-bound coverage from current request set: 61.8248%
- Mathematical upper bound if every nonfailed duration later mapped: 61.8248%
- >=70% prefix: BLOCKED: required CUTLASS row is FAILED_CLOSED; frozen denominator retained
- >=80% proxy: UNRESOLVED: failed CUTLASS rows have no admissible static MREF map; no MREF count is invented

### DECODE

- Full frozen denominator: 73,172,157 ns
- Failed CUTLASS duration: 20,575,062 ns (28.1187%)
- MAPPED_EXACT lower-bound coverage from current request set: 71.8813%
- Mathematical upper bound if every nonfailed duration later mapped: 71.8813%
- >=70% prefix: BLOCKED: required CUTLASS row is FAILED_CLOSED; frozen denominator retained
- >=80% proxy: UNRESOLVED: failed CUTLASS rows have no admissible static MREF map; no MREF count is invented

## Candidate paths

1. **Identity-path repair (recommended):** add a bounded loader observer that records an actual immutable loaded image/fatbin/cubin hash and binds the observed target `CUfunction` through its `CUmodule` before selection. Run one prefill and one decode exact-function map-only window after a one-run tiny observer validation. Acceptance: exact module/image relation, immutable SHA, successful exact static map, and no DSO/name fallback. This preserves the frozen denominator and needs at most three diagnostic GPU windows; it produces no scientific memory capture.
2. **Coverage-contract revision:** requires independent pre-outcome scientific rationale, application to every row, and explicit user approval. It cannot be activated by this review.
3. **Partial mapped subset:** can report only mapped-anchor evidence, but cannot claim whole-phase representative selection under the current contract.

## Bias controls

Failed CUTLASS rows remain in both frozen duration denominators. No MREF proxy contribution, owner, or mapping is fabricated.
