# R19F2 authorization

Date: 2026-10-01

R19F1 authority:
- branch: `hrl/awma-r19f1-fp8-readiness-109-v1`
- commit: `7375abd8e86c1523c1873913e8fffccf0b4e3a96`
- conclusion: `R19F1_FP8_READINESS_RESIDUAL_PRESENT`

R19F2 is now authorized as the mandatory strong-software/dataflow counterfactual before any architecture admission.

Handoff:
- branch: `hrl/awma-r19f2-fp8-software-counterfactual-handoff-v1`
- HEAD: `d83259e7c9085de686216b7de0166776f6254922`
- execution branch: `hrl/awma-r19f2-fp8-software-counterfactual-109-v1`
- Goal: `docs/vm_tlb/chatgpt_handoff/awma/r19f2_fp8_software_counterfactual_v1/LANE_F_R19F2_FP8_SOFTWARE_COUNTERFACTUAL_109_GOAL.md`

Order is fixed:

1. Stage A: Qwen layer0 gate_proj and up_proj share one exact TE current-scaling E4M3 input representation.
2. Measure both sibling-projection region and complete natural MLP region.
3. If the complete MLP S1-vs-D0 residual is below the preregistered materiality gate, close as software/dataflow organization.
4. Only if a stable >=5% complete-MLP residual survives, Stage B may run one exact single-launch current-scaling quantizer counterfactual.
5. Only a residual that survives Stage B may receive `READY_FOR_ARCHITECTURE_REVIEW`.

No hardware mechanism, node174, Accel-Sim, second model, second shape, new precision recipe or Blackwell extrapolation is authorized.

Current lanes:
- Lane F / 109: R19F2 authorized
- Lane G fast-weight: STOP
- Lane E IBP: STOP
- node174 simulation: STOP
