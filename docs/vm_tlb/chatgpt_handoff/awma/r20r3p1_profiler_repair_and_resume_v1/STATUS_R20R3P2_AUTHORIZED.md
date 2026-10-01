# R20R3P2 authorization

Date: 2026-10-01

Parent R20R3P1 authority:
- execution branch: `hrl/awma-r20r3p1-profiler-repair-resume-109-v1`
- commit: `53837e8366f0d96a636c89365b782aa411e7bc63`
- tree: `1c46eb3135093e89d6c7ae1f6c99a1ce97da9c87`
- formal label: `R20R3_CANDIDATE_NUMERICS_NOT_QUALIFIED`

Accepted narrow stop:
- profiler repaired;
- stage selected deterministically: `_update_gradient_incremental`;
- candidate fixed: ascending active IDs, 304 workers;
- B0/S1 pass effective-output/coverage/niter/status gates at t128;
- only the historical final-gradient residual envelope fails;
- fresh paired B0 itself also exceeds that envelope.

Authorized continuation:
- handoff branch: `hrl/awma-r20r3p2-residual-contract-handoff-v1`
- handoff HEAD: `36be18b1318dc68af2e65d10803f3f9120d3fdc5`
- execution branch: `hrl/awma-r20r3p2-residual-contract-resume-109-v1`
- Goal:
  `docs/vm_tlb/chatgpt_handoff/awma/r20r3p2_residual_contract_resume_v1/LANE_F_R20R3P2_RESIDUAL_CONTRACT_RESUME_109_GOAL.md`

R20R3P2 must derive a new residual correctness contract only from:
- pinned source done semantics;
- fresh B0-only repeats;
- directed negative validation.

It may not fit thresholds to the already-known S1 residual values.

If the source-semantic contract qualifies, the exact existing stage/candidate/304-worker mapping is reused and the original correctness -> discovery timing -> conditional holdout chain resumes automatically.

No new profiler, stage selection, candidate, worker count, hardware, node174 or Accel-Sim work is authorized.
