# GPU resume decision package V1

## Recommendation

`RESUME_GPU_FOR_BOUNDED_IDENTITY_REPAIR`

The recovered Q2 traces are locally hash-closed and remain valid anchor evidence. The only blocker to the frozen representative-selection contract is two CUTLASS rows with no admissible actual runtime code-object identity. A narrow identity repair preserves the contract; neither a denominator reduction nor a kernel-name/DSO inference is permitted.

## Minimum bounded GPU work

1. One tiny loader-observer validation (no model trace): prove the observer emits `CUmodule -> actual loaded image/fatbin/cubin bytes -> SHA256` before map selection.
2. One Llama S0 Prefill map-only window for the frozen unresolved CUTLASS function.
3. One Llama S0 Decode map-only window for the frozen unresolved CUTLASS function.

Each is a diagnostic-only, single-process window. It must use the frozen runtime profile and exact function identity, write only compact owner/map receipts, and make no target, coverage, timing, or memory-capture outcome claim.

## Acceptance criteria

- The target `CUfunction` is bound through the observed `CUmodule` to immutable image bytes or a cubin/fatbin payload SHA256.
- The binding is collected before selection and is reproducible on a second identical observer use if a retry is necessary.
- Exact static map validation succeeds with that actual owner token; no default `libtorch_cuda.so`, name-only, or geometry-only fallback occurs.
- If either exact row remains unresolved, retain its failed-closed state, keep it in the denominator, stop the repair path, and return a partial-mapped-subset report rather than broadening GPU exploration.

No formal capture is authorized by this recommendation.

RESUME_GPU_FOR_BOUNDED_IDENTITY_REPAIR
