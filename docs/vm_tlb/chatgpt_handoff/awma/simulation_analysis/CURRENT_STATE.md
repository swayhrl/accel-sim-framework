# Simulation Analysis Current State

## Project boundary

AWMA has one shared identity/catalog/storage architecture and two evidence planes:

- Native Evidence: NSYS/NCU/NVBit/C16WARP1 real-GPU observations.
- Simulation Evidence: simulator-compatible trace + Accel-Sim/GPGPU-Sim modeled results.

This document tracks only the Simulation Analysis plane.

## Historical inheritance already complete

174-new/node164 has already inherited the usable C12–C15 simulation research assets.

Canonical historical simulation authority is recorded by:

- `hrl/c12-c15-174new-canonical-inheritance-v2`
- commit `7b6f2b88c36b4ed1bbdcd72761063f881c7b6c96`
- review pack `docs/vm_tlb/review_packs/C12_C15_174NEW_CANONICAL_INHERITANCE_V2/`

Key retained historical facts:

- C12 Prefill F0 and Decode F0 remain FORMAL historical baselines.
- C13 repaired evidence remains DIAGNOSTIC.
- C14 remains DIAGNOSTIC and explicitly not full-ROI equivalent.
- C15 remains static/diagnostic and contains no dynamic simulator result.
- Shared M4C/M4B/EP-L2 historical outputs and old174 private scientific exports are archived/indexed on node164.

## Historical runtime exact replay is not available

Historical C12 identity is known:

```text
Framework: d64408a97d76a320a6d49468653d416e33677af8
Core:      57bb71ecd015b6ec0ab32e45b0815e5beaf69172
Binary:    2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a
```

But on 174-new:

- exact historical Core object is unavailable;
- exact historical binary is unavailable;
- the current environment does not yet provide a qualified build/runtime baseline;
- earlier reconstruction found no usable exact-replay path.

Therefore the future mainline is **not** to make all future work depend on exact C12 binary reproduction. Historical C12 is a calibration/reference anchor for a new maintainable baseline.

## Current simulator-facing software authority

Existing reusable or revalidatable entry points include:

```text
util/vm_tlb/run_m4c_replay.sh
util/vm_tlb/export_m4c_telemetry.py
util/vm_tlb/summarize_m4c_runs.py
util/vm_tlb/analyze_m4c_trace_locality.py
util/vm_tlb/c12_cache_behavior_checkpoint.py
configs/vm_tlb/M4C_*.config
configs/vm_tlb/M4B_*.config
configs/vm_tlb/c5_*
```

These are not automatically qualified for the future baseline merely because the files exist.

## Current C16WARP1 input boundary

Current formal C16 MREF-sharded / C16WARP1 data is **not simulator input**.

Decision:

```text
C16WARP1 / MREF_SHARDED_COMPLETE_SET
→ Native/offline characterization: allowed
→ lossless Accel-Sim trace reconstruction: NOT_PROVEN_LOSSLESS
```

Do not synthesize cross-MREF order, missing opcode/access width, synchronization or coalescing semantics.

## What is still missing

The Simulation Analysis mainline still needs:

1. `NEW_SIM_BASELINE_V1`: a maintainable, hash-bound simulator runtime on 174-new.
2. bounded historical calibration against archived traceg/outputs.
3. a canonical simulation input admission/catalog path.
4. a normalized simulation telemetry/dataset path.
5. `SIM_COMPAT_CAPTURE_V1`: a producer contract and later 109 capture implementation that creates true simulator-consumable input.
6. first current-model simulation inputs and baseline runs.
7. only after baseline qualification: architecture mechanism experiments.

## Parallelism rule

This line should be advanced primarily on 174-new and node164 without using the 4080 until a simulator-compatible capture canary is actually required. That lets 109 continue Native Characterization in parallel.
