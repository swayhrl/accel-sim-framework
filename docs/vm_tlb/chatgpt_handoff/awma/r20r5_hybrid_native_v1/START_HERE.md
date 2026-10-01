# START HERE — AWMA R20R5 fixed-threshold hybrid Native validation

Date: 2026-10-02

User authorization: CONTINUE_WITHOUT_INTERMEDIATE_CONFIRMATION.

Scientific parent:
`769ea5f3592976b2035beb76947b0d934d6efabf`

Parent conclusion:
`R20R4_HYBRID_CANDIDATE_JUSTIFIED_FOR_REVIEW`

Accepted parent facts:
- always-worklist fixed-304 S1 is ~66.6% slower at complete solver boundary;
- selected stage = `_update_gradient_incremental`;
- late region defined only by `active_count<=304`;
- late selected-stage time = 412.097 us / 1024.802 us = 40.21%;
- O2 ideal late H+blocked-Cholesky complete-solver headroom = 11.77%;
- O2 is positive for all four discovery entries;
- fixed source exposes current device `nsolving` before the selected stage;
- exactly one structural hybrid remains scientifically justified.

R20R5 is the one and only runtime test of that hybrid.

Execution branch:
`hrl/awma-r20r5-hybrid-native-109-v1`

Lane F / node109 is the only executor.
Lane E/G and node174 remain STOP.

All CUDA/JIT/capture/replay work must hold:
`/data/c16/locks/c16_gpu_campaign.lock`

No profiler, worker sweep, threshold sweep, second stage, second candidate, whole-physics-step claim or hardware work is authorized.
