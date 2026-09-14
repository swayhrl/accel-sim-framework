# Bounded identity-repair GPU handoff V1

## Current execution state

`RENTAL_GPU_STOP_ALLOWED`

`GPU_WORK_DEFERRED_PENDING_USER_DECISION`

This handoff is preparation only.  It authorizes **no** connection to a rented
GPU and no NVBit, Nsight, CUTLASS-owner, map, canary, or formal-capture run
unless the user explicitly re-authorizes GPU work after this document is
published.

The V12.8 review has already preserved all raw evidence locally and published
the following science conclusion: Route-A/Q2 bridge is `PASS`; the current
representative-selection contract remains blocked solely by two CUTLASS rows
whose actual runtime code-object identities are `FAILED_CLOSED`.

## Frozen authorities and runtime

- Scientific authority: `ef0d89b1ce297518f86c51cddce190abd47e7364`
- Recovery authority: `62428f2cea9ed4cd2def11339311d4347282d9c7`
- Offline-review authority: `cbc63026651abb0715a29918915a77726c57b976`
- Runtime profile if later re-authorized: RTX3090/SM86, driver `570.124.04`,
  CUDA `12.4`, PyTorch `2.5.1+cu124`, NVBit `1.7.5`,
  `CUDA_MODULE_LOADING=EAGER`.

No CUDA, driver, PyTorch, NVBit, model, input, shape, dtype, backend, frozen
coverage denominator, or selected-function identity may be changed to make a
window run.

## Hard campaign limits

- Exactly the three windows below are eligible; maximum count is **3**.
- One GPU process per window; `<=20` minutes and `<=4 GiB` retained output per
  window.
- The windows are diagnostic-only and not eligible for timing, memory
  fingerprint, selector, coverage, or formal-capture conclusions.
- A failed or ambiguous window consumes its slot. No retry, target
  substitution, owner defaulting, kernel-name inference, or coverage-denominator
  change is allowed.
- Before each window: no `MEASUREMENT_ACTIVE`, no stale GPU process, no active
  large transfer, and storage gate passes. After each: remote size/SHA manifest,
  terminal receipt, process cleanup, and publication checkpoint are required.

## Window 1 of 3 — tiny loader-observer validation

**Purpose:** validate the *new* observer contract without a model trace.

**Work:** a minimal CUDA module/image load must emit a pre-outcome relation
`CUmodule -> immutable loaded image/fatbin/cubin bytes -> SHA256`.  The receipt
must additionally name the loader callback/API that created the relation and
prove the content hash was taken from observed bytes, not from a guessed DSO
path.

**PASS:** compact receipt validates the module handle, image byte count and
SHA256; no target inference occurs.  This does not map CUTLASS and does not
authorize formal capture.

**FAIL/CAPABILITY_LIMITED:** publish the evidence, stop immediately, retain
the two current CUTLASS rows as failed-closed, and do not consume Windows 2–3.

## Window 2 of 3 — Prefill exact-function map-only

**Frozen phase/function:** `PREFILL`,
`_ZN7cutlass7Kernel2I66cutlass_80_tensorop_f16_s16816gemm_relu_f16_128x128_32x5_tn_align8EEvNT_6ParamsE`.

**Work:** under the frozen Llama S0 runtime/input identity, use the validated
observer to bind the actual target `CUfunction` through its observed `CUmodule`
to immutable image bytes/SHA256, then generate an exact-function static map.
No dynamic memory trace, selection result, or coverage claim is produced.

**PASS:** exact full mangle; observed module/image relation; content SHA256;
nonempty static map with unique parseable static indices; and no default
`libtorch_cuda.so`, spelling, geometry, or kernel-name fallback.

**Otherwise:** `FAILED_CLOSED_CODE_OBJECT_IDENTITY_UNRESOLVED`; preserve the
frozen Prefill denominator and do not replace the function.

## Window 3 of 3 — Decode exact-function map-only

**Frozen phase/function:** `DECODE`,
`_ZN7cutlass7Kernel2I66cutlass_80_wmma_tensorop_f16_s161616gemm_f16_16x16_128x1_tn_align8EEvNT_6ParamsE`.

The procedure and acceptance conditions are identical to Window 2, with the
Decode function above.  A failure remains `FAILED_CLOSED`; it cannot be masked
by the Prefill result.

## Stop and next decision

After every eligible window, publish only compact receipts, source/tool hashes,
owner/map manifests, remote SHA closure, and status.  Raw payloads stay outside
Git.  At the third window or an earlier terminal failure, shut down the GPU
workflow and return to offline review.

Only if both exact-function maps pass may a later, separately authorized review
decide whether representative selection is admissible.  This handoff itself
does not authorize Route-B capture, Route-C coverage, a model canary, or any
scientific GPU measurement.
