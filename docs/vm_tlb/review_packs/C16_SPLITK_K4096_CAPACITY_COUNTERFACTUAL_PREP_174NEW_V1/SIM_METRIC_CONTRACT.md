# Simulator metric contract

No run is authorized by this pack. If a future platform-scope review explicitly admits this counterfactual, each arm must replay the exact same GEMM trace at 64/128/256 MiB; only the `dl2` set count may differ.

Pre-registered aggregate observables are completion/return code, quiescence, `gpu_sim_cycle`, `gpu_sim_insn`, issued CTA count, L2 accesses/misses/miss rate, pending hits/reservation failures, and total DRAM reads/writes. Compare deltas within an arm from 64 to 128 and 256 MiB; do not compare absolute cycles to native RTX4080 timing.

The capacity explanation is strengthened only if split1 shows a material, monotonic L2-miss/DRAM reduction and cycle improvement with larger L2 while split8 is substantially less sensitive. A flat, reversed, non-monotonic, incomplete, or non-quiescent result rejects or weakens the proposed mechanism.

The accepted simulator does not expose qweight-range-specific L2 hit/miss/DRAM counters. Recorded 64-bit VA ranges can prove trace coverage and classify trace operands, but aggregate cache counters must not be relabeled as qweight-only telemetry. Adding object counters would be a separate instrumentation/neutrality task and is outside this gate.

Changing sets changes both modeled capacity and set-index range. Results may be called an L2 configuration counterfactual, never pure physical-capacity isolation or cycle-perfect Ada prediction.
