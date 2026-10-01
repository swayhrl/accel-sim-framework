# R20R2 authorization

Date: 2026-10-01

R20R1 authority:
- execution branch: `hrl/awma-r20r1-solver-entry-local-contract-109-v1`
- commit: `8a1a8baf6ac5b6eff0c32f04b572eb1d34873d24`
- formal label: `R20R1_SOLVER_BASELINE_NOT_QUALIFIED`

Accepted narrow failure:
- t128/t136/t144 passed the frozen local solver contract;
- t152 failed because world413 set LS_ITERATIONS in 1/5 identical-input B0 replays;
- nefc=46 and solver_niter=8 remained exact;
- floating outputs remained inside the pre-frozen local contract.

Authorized follow-up:
- handoff branch: `hrl/awma-r20r2-linesearch-semantic-materiality-handoff-v1`
- handoff HEAD: `f7bc6fe191aed831c6fd401c678847359d858534`
- execution branch: `hrl/awma-r20r2-linesearch-semantic-materiality-109-v1`
- Goal: `docs/vm_tlb/chatgpt_handoff/awma/r20r2_linesearch_semantic_materiality_v1/LANE_F_R20R2_LINESEARCH_SEMANTIC_MATERIALITY_109_GOAL.md`

R20R2 is correctness/semantics only:
- exact t152 solver entry
- world413
- no active-world S1
- no performance timing
- no NSYS/NCU/NVBit/SASS
- no 174/Accel-Sim
- no solver parameter/tolerance changes

Purpose:
determine whether the LS_ITERATIONS flip is a threshold-local diagnostic status difference, a materially different numerical path, or unresolved hidden graph-local state.

R20R1 historical contract remains unchanged.
