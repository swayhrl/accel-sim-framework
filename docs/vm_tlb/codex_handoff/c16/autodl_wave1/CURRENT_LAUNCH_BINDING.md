# C16 AutoDL Wave-1 Current Launch Binding

This file binds the current real execution launch. It does not replace `START_HERE.md`.

## Runtime branch

- `hrl/vm-c16-g-autodl-wave1-v0`
- Base accepted G offline package: `45e293b84940ef59b7b134bcda48aca7d0b99b2f`

## Current AutoDL platform

User has rented one RTX 3090 24GB instance. Marketplace configuration reported before runtime verification:

- GPU: RTX 3090 24GB, one GPU
- CPU: 14 vCPU Intel Xeon Gold 6330 @ 2.00GHz
- RAM: 90GB
- system disk: 30GB
- data disk: 50GB free + 100GB paid, approximately 150GB total
- base image selected: PyTorch 2.5.1 / Python 3.12 / Ubuntu 22.04 / CUDA 12.4

These are launch expectations only. C16-1.1 must query and record actual GPU UUID, driver, CUDA/toolkit, CPU/RAM/disk, clocks/power/temperature, and instance identity after login. Never treat this file as an observed machine receipt.

## Lane-A rolling packages available now

### P0 — Llama3.2-1B

- immutable publication commit: `20fb38e6ca629f1a93db7939248bd1a03790724c`
- package path: `docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_a/packages/C16_GPU_PACKAGE_P0/`
- package manifest SHA-256: `ac59f0d2aca95021c686948d7244ce50375530bbe983c8508ca5f6954e80230f`
- model revision bound by A: `4e20de362430cd3b72f300e6b0f18e50e7166e08`
- scope: immutable Llama-only rolling transfer/canary package; it does not close multi-model C16-0.9.

### P1 — Qwen2.5-0.5B

- immutable publication commit: `4e73a1d0f435ba4d1dae1a9e749b8b82e54b7f63`
- package path: `docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_a/packages/C16_GPU_PACKAGE_P1/`
- package manifest SHA-256: `d8ac3ca44c4344b9a5fa752ba5a6549c007e901b26b426c9713b4d7e8749eb84`
- scope: immutable Qwen2.5-0.5B delta package.

Lane A continues downloading Qwen2.5-7B raw and AWQ. Do not wait for them before starting P0/P1 runtime work. Later P2/P3 must be consumed as new immutable deltas and must not mutate P0/P1.

## Fixed offline inputs

- G offline package: `45e293b84940ef59b7b134bcda48aca7d0b99b2f`; manifest SHA256 `7c18c2a806ac37b974702050567430f83f10bbdacc78c5af2fe09ea871896087`
- C Sampling-V2 offline: `29e669eca19ac3b2a1350bf2d097569a41f123e1`
- H memory-fingerprint offline: `932c6fa44a4896265214fc2136e34698402a5c7f`

## Immediate execution order

1. Verify this runtime branch is clean/non-detached and read `START_HERE.md` fully.
2. C16-1.1: record actual AutoDL instance receipt; initialize the shared execution-budget ledger from the observed instance start receipt.
3. C16-1.2: consume and verify P0 plus G wheelhouse/code using exact commit/manifest/hash. Any mismatch is fail-closed.
4. Create CPython 3.10 environment and install only the accepted hash-closed wheelhouse with no-index; run `pip check` and import/runtime receipts.
5. Llama S0: G0, G1, G2, G3 inline qualification.
6. If G0+G1 pass, execute Llama S1/S2 baseline + lightweight native census and publish an early committed native checkpoint.
7. Between formal measured runs, consume P1, hash-verify it, then run Qwen2.5-0.5B according to frozen scenarios.
8. Continue to wait for later A deltas without leaving the GPU idle solely because 7B assets are still downloading; however do not invent or download unapproved model revisions on AutoDL.

## Measurement / transfer discipline

- Do not run model rsync concurrently with formal baseline/profile/capture measurements.
- The 150GB data disk is sufficient only with rolling cleanup. Hash and transfer raw profiler/NVBit outputs back promptly; delete remote raw only after transfer receipt/hash closure.
- Do not CPU-offload a frozen deployment to make it fit. OOM -> `SKIPPED_RESOURCE` with receipt.
- Do not run long Accel-Sim/GPGPU-Sim workloads on AutoDL.

## Stop points

Stop and publish a bounded checkpoint rather than improvising on:
- identity/hash mismatch;
- dtype/backend/revision fallback;
- profiler or NVBit capability limits after bounded attempts;
- execution budget exhaustion.
