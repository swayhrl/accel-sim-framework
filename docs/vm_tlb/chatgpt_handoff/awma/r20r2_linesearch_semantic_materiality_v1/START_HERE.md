# START HERE — AWMA R20R2 line-search semantic-materiality diagnostic

Date: 2026-10-01

User authorization: APPROVED.

Scientific parent:
`8a1a8baf6ac5b6eff0c32f04b572eb1d34873d24`

Parent conclusion:
`R20R1_SOLVER_BASELINE_NOT_QUALIFIED`

Why:
- t128/t136/t144 solver entries passed the pre-frozen local numerical contract;
- t152 failed only because world 413 set `LS_ITERATIONS` in 1/5 identical-input B0 replays;
- nefc=46 and solver_niter=8 were unchanged;
- floating solver outputs remained inside the pre-frozen contract.

This follow-up does **not** relax or reinterpret R20R1. It asks what that one line-search flag flip means.

Execution branch:
`hrl/awma-r20r2-linesearch-semantic-materiality-109-v1`

Lane F / node109 is the only executor.
Lane E/G remain STOP.
node174 / Accel-Sim remain STOP.

All CUDA/JIT/capture/replay work must hold:
`/data/c16/locks/c16_gpu_campaign.lock`

No performance campaign, no active-world S1, no NSYS/NCU/NVBit/SASS, no solver-parameter change.
