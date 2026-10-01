# START HERE — AWMA R20R3P2 residual-contract requalification and automatic resume

Date: 2026-10-01

User authorization: CONTINUE_WITHOUT_INTERMEDIATE_CONFIRMATION.

Scientific parent:
`53837e8366f0d96a636c89365b782aa411e7bc63`

Parent conclusion:
`R20R3_CANDIDATE_NUMERICS_NOT_QUALIFIED`

Precise parent stop:
- profiler repaired and exact stage ranking closed;
- selected stage = `_update_gradient_incremental`;
- selected candidate = online ascending active IDs, fixed 304-worker mapping;
- OFF/list canaries passed;
- at t128, B0 and S1 both passed effective-output, coverage, niter, status and qfrc-relation gates;
- only the historical final-gradient residual envelope failed;
- importantly, the fresh paired B0 itself exceeded that historical envelope in 11 worlds.

This follow-up is a new B0-only numerical-contract qualification. It does not retroactively alter R20R3P1.

Execution branch:
`hrl/awma-r20r3p2-residual-contract-resume-109-v1`

Lane F / node109 is the only executor.
Lane E/G and node174 remain STOP.

If the new B0-only source-semantic contract qualifies, automatically reuse the exact selected stage/candidate and resume correctness -> discovery timing -> conditional holdout without another confirmation.

All CUDA/JIT/capture/replay work must hold:
`/data/c16/locks/c16_gpu_campaign.lock`
