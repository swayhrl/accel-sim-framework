# SG3 C0 memory-service knob selection

This is a pre-result, zero-simulation C0 decision for the downstream-headroom specification.  It preserves all prior evidence and does not change DTC semantics, Core identity, trace identity, channels, L2 capacity/MSHR/miss queue, or mapping.

## Selected knob

`M = -gpgpu_dram_buswidth 16 -> 32` B, with the existing burst length (2), data-command frequency ratio (2), all timing parameters, 20 channels, and all queue capacities unchanged.

The source registers this as the DRAM data-bus width (`gpu-sim.cc:299-300`).  The parsed configuration derives `dram_atom_size = BL * busW * gpu_n_mem_per_ctrlr` (`gpu-sim.h:437-438`); detailed DRAM advances request transmission and data return by precisely that atom (`dram.cc:298-301,570-592`).  Thus M is a single post-admission data-service-width upper-bound probe.  Address-map initialization is separately called with memory-channel/subpartition/shader configuration (`gpu-sim.h:451-452`), not `busW`.

It is deliberately not a claim that the modeled Volta-like system has a 32-B physical bus.  It asks the bounded counterfactual: whether doubling only this source-defined detailed-DRAM transfer width can convert the concurrency available under the fixed default DTC cap of 8192 into performance.

## Why this is source- and telemetry-supported

The accepted BICG defaults retain nonzero detailed-DRAM queue pressure (mean `mrqq` occupancy 13.77 IO / 13.69 OO, with per-channel maxima reported in the immutable stdout) and substantial average MRQ latency (811 / 796 cycles).  The cap controls show these telemetry values and end-to-end latency move materially with injected outstanding demand.  Aggregate `bw_util` is low (about 7.9%), so the result must be interpreted as an upper-bound service sensitivity, not evidence that byte bandwidth is saturated.  This is exactly why C1 is bounded to a 2x2 interaction, with no further memory sweep.

## Explicit exclusions

Scheduler/partition/return queues are buffering or admission controls; timing strings are multi-parameter service models; `dram_latency` is an upstream fixed delay.  None is selected.  No queue=64, timing sweep, capacity/MSHR sweep, channel/mapping change, port change, or new DTC mechanism is authorized.

## Pre-registered C1 / C2 rule

After this C0 commit is pushed, C1 consists only of BICG IO/OO `Q0M1` (queue 32, busW 32) and `Q1M1` (queue 128, busW 32), each with default cap=8192 and fresh UUID/immutable directory.  Existing accepted `Q0M0` and strict-PASS `Q1M0` rows are reused exactly.  GESUMMV is not launched merely because C1 exists: it is authorized only by the already declared 5% Gate M or Gate I plus coherent service telemetry in `CODEX_NEXT_STAGE.md`.
