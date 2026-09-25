# Source anchors

The experiment changes only source-supported queue-chain fields, the detailed
DRAM clock domain, and—at the pre-registered R4 gate—the 20-MiB L2 capacity
ceiling.  DTC semantics, default GPU-wide lower cap (8192), trace, Core, and
runtime are held fixed.

| Mechanism | Source anchor | Interpretation used in this study |
|---|---|---|
| Partition queue order | `core/src/gpgpu-sim/l2cache.cc:488-497` | `64:64:64:64` is ordered ICNT-to-L2, L2-to-DRAM, DRAM-to-L2, L2-to-ICNT. |
| L2-to-DRAM fullness | `core/src/gpgpu-sim/l2cache.cc:1124-1131` | Fullness blocks a miss after it has acquired an L2 memory port. |
| Shared DRAM credits | `core/src/gpgpu-sim/l2cache.cc:139-149` | Scheduler/return changes are coupled; they are not independent queues. |
| Scheduler enqueue failure | `core/src/gpgpu-sim/dram.cc:164-178` | Identifies the source-owned scheduler-full event. |
| Return FIFO fullness | `core/src/gpgpu-sim/dram.cc:120-124` | Identifies DRAM-to-L2 return backpressure. |
| DRAM clock parsing and period | `core/src/gpgpu-sim/gpu-sim.cc:1474-1488` | `1700` changes the modeled DRAM timing rate. |
| DRAM clock-domain scheduling | `core/src/gpgpu-sim/gpu-sim.cc:2348-2368,2451` | The counterfactual affects detailed-DRAM service timing, not a host-side delay. |
| Published latency telemetry | `core/src/gpgpu-sim/mem_latency_stat.cc:353-365` | Per-DRAM MRQQ and bandwidth fields are output-derived evidence. |

The older `busW 16 -> 32 B` result remains immutable provenance but is
non-discriminating because the source-defined DRAM atom is already 32 B; see
the R0 audit index for the precise source references.  No inference is made
from unprinted counters: `L2_dram_queue_full` is labelled `NOT_AVAILABLE`
where a terminal output does not emit it.
