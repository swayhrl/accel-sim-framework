# START HERE — AWMA R20R3P1 profiler admission repair and automatic R20R3 resume

Date: 2026-10-01

User authorization: APPROVED.

The user explicitly authorized continuing the bounded R20 work without asking for another intermediate confirmation. This authorization applies only inside the frozen R20R3 scientific contract and this profiler-repair/resume sequence.

Scientific parent:
`fa292a11dbc196b65ebe1f3a67f39a7837046995`

Parent conclusion:
`R20R3_ACTIVE_WORLD_DIAGNOSTIC_NOT_QUALIFIED`

Precise parent stop:
- four OFF/B0 discovery entries passed the revised numerical contract;
- the sole authorized NSYS workload completed numerically correctly;
- NSYS returned 0 but produced no report / SQLite / qdstrm;
- stage ranking could not be computed;
- no stage, S1, timing or holdout result exists.

This follow-up is an engineering admission repair followed by automatic continuation of the original R20R3 scientific stages if and only if the repaired profiler qualifies.

Execution branch:
`hrl/awma-r20r3p1-profiler-repair-resume-109-v1`

Lane F / node109 is the only executor.
Lane E/G remain STOP.
node174 / Accel-Sim remain STOP.

All CUDA/JIT/capture/replay/profiling work must hold:
`/data/c16/locks/c16_gpu_campaign.lock`
