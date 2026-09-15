# Simulation Analysis Current State

## Project boundary

AWMA has one shared identity/catalog/storage architecture and two evidence planes:

- Native Evidence: NSYS/NCU/NVBit/C16WARP1 real-GPU observations.
- Simulation Evidence: simulator-compatible trace + Accel-Sim/GPGPU-Sim modeled results.

This document tracks only the Simulation Analysis plane.

## Execution status

Simulation Analysis foundation is now **ACTIVE and allowed to run in parallel** with the ongoing Native Characterization/Qwen Decode work.

Parallel execution is safe only with strict isolation:

```text
109 / RTX4080
  Native capture / profiling / C16WARP1

174-new worktree A
  active Qwen Decode/native analysis

174-new worktree B
  AWMA Simulation Foundation
```

The simulation Goal must not mutate or disturb the Native worktree/processes and must use bounded CPU/I/O resources.

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

But exact historical Core/binary availability is not guaranteed on 174-new, and the current environment has not yet qualified a maintainable runtime baseline.

The mainline therefore does not require exact resurrection of the historical binary. C12 is a calibration/reference anchor for a new maintainable baseline.

## Current simulator-facing software authority

Reusable or revalidatable entry points include:

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

File existence is not runtime qualification; the Simulation Foundation Goal must revalidate the executable path.

## Current C16WARP1 input boundary

Current formal C16 MREF-sharded / C16WARP1 data is **not simulator input**.

Decision:

```text
C16WARP1 / MREF_SHARDED_COMPLETE_SET
→ Native/offline characterization: allowed
→ lossless Accel-Sim trace reconstruction: NOT_PROVEN_LOSSLESS
```

Do not synthesize cross-MREF order, missing opcode/access width, synchronization or coalescing semantics.

## Current missing pieces

The Simulation Analysis mainline still needs:

1. fail-closed simulation input admission and stable `SIM_INPUT_ID`;
2. normalized Simulation Evidence telemetry/dataset layer;
3. `NEW_SIM_BASELINE_V1`: a maintainable, hash-bound simulator runtime on 174-new;
4. bounded calibration against archived historical traceg/outputs;
5. a machine-checkable `SIM_COMPAT_CAPTURE_V1` consumer contract;
6. later, 109 producer implementation/capture qualification;
7. first current-model baseline simulation;
8. only after baseline qualification: architecture opportunity/mechanism experiments.

## Immediate active Goal

Execute:

```text
docs/vm_tlb/chatgpt_handoff/awma/simulation_analysis/
CODEX_NEXT_STAGE_174NEW_SIMULATION_FOUNDATION.md
```

with:

```text
PARALLEL_EXECUTION_AND_AUTONOMOUS_RECOVERY.md
ACCEPTANCE_AND_REVIEW_REQUIREMENTS.md
```

as mandatory operating/acceptance policy.

## Parallelism rule

The current foundation stage uses no 109 GPU. It should advance consumer/runtime/catalog/telemetry infrastructure while 109 continues Native Characterization. Later, only the producer-side `SIM_COMPAT_CAPTURE_V1` canary will require the 4080.
