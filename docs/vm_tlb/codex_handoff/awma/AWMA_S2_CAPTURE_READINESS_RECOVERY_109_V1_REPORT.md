# AWMA S2 capture-readiness recovery 109 V1

Status: COMPLETE — offline authority recovery; STOP.

The prior S2 `SELECTOR_IDENTITY_BLOCKED` result is superseded. The Lane A V2 full per-launch ledger was read from node164 and SHA-256 verified against `222d5dfeeb1e7aaae3423f13873053c37c27f5c6290d8a58bd3186a0803ca77a`. Its 34,677 rows recover the exact global launch index, phase, decode step, exact function, grid/block, and occurrence. Each recovered selector is bound to the accepted model revision, S2 T2048 token hash, and accepted historical driver hash.

Five existing assets are exact-safe joins and are `REUSABLE_NOW`: T0 Prefill Flash, T1 Prefill GEMM, T2 Decode GEMV, Decode Flash splitkv, and Decode Flash splitkv-combine. The latter two are reusable under the accepted Lane C requalification authority, not guessed from filenames. Other ledger records remain `CAPTURE_READY`; none are left `SELECTOR_IDENTITY_BLOCKED`.

Same-length different-TEXT content control remains `INPUT_AUTHORITY_BLOCKED`: no second legal frozen T2048 TEXT input was constructed or substituted.

No GPU workload, GPU lock, NSYS, NVBit, producer, capture, or Accel-Sim execution occurred.
