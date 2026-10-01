# R20R4 headroom-audit authorization

Date: 2026-10-02

Parent R20R3P2 authority:
- execution branch: `hrl/awma-r20r3p2-residual-contract-resume-109-v1`
- commit: `3f4e3409ad629d5302a54e9c3a0f356bdc190456`
- tree: `adff579cc8c29908753ebd92852740153c52b60d`
- decision: `R20R3_ACTIVE_WORLD_NO_MATERIAL_GAIN`

Accepted result:
- source-semantic stop contract qualified on 32/32 fresh B0-only replays;
- six directed negatives rejected;
- exact existing 304-worker candidate qualified numerically on all four discovery entries;
- 120 formal complete-solver samples qualified;
- S1 was stably ~66.6% slower than B0;
- holdout remained sealed.

Interpretation:
this is a bounded negative for the fixed 304-worker all-iteration organization, not proof that every active-world organization is negative.

Authorized next step is CPU-only only:
- handoff branch: `hrl/awma-r20r4-hybrid-headroom-audit-handoff-v1`
- handoff HEAD: `2b76d71bdf8e98041f06301b5e16af3947874482`
- execution branch: `hrl/awma-r20r4-hybrid-headroom-audit-109-v1`
- Goal:
  `docs/vm_tlb/chatgpt_handoff/awma/r20r4_hybrid_headroom_audit_v1/LANE_F_R20R4_HYBRID_HEADROOM_AUDIT_109_GOAL.md`

Purpose:
use already-accepted B0 NSYS raw to decompose selected-stage time by outer iteration and compute the ideal complete-solver headroom available only after active_count <= 304.

No GPU execution, no new profiler, no S1, no holdout, no 174/Accel-Sim/hardware work is authorized in R20R4.

If the late-phase targeted H+Cholesky oracle is <5%, close the R20 active-world line.
If it is >=5%, freeze exactly one source-derived hybrid design for later review; do not run it in this Goal.
