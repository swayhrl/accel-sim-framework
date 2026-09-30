# Exact-loss review status

Date: 2026-09-30

Execution authority:
- branch hrl/awma-cce-liger-exact-loss-boundary-109-v1
- commit ad9a302a49cdb3b1e75a9bbf04dab819c362cb1a
- tree f7eee1a828061cb94952ef3c133ba355e60ede5f

Formal execution label remains EXACT_LOSS_STATE_LIFETIME_RESIDUAL_PRESENT.

Accepted local facts:
- real shape B1 T255 H896 V151936 BF16
- B0 PyTorch materialized median 4.890624 ms
- B1 CCE exact no-filter median 7.571456 ms
- B2 Liger Triton Ada median 673.950745 ms
- B1 has a full FP32 classifier-gradient accumulator of 544538624 bytes
- explicit full accumulator zero initialization costs 0.751779 ms and 9.55 percent of the profiled B1 GPU-kernel timeline

Interpretation boundary:
- the contract-level state/lifetime residual is accepted for the fastest qualified no-full-logits arm
- this is not yet a workload-level hardware gap
- on this frozen shape B0 is faster than B1 and has a smaller observed peak allocated delta
- pinned CCE source creates dc using torch.zeros_like and later combines chunk contributions through lock/add accumulation
- therefore the next scientific question is software removability of the pre-zero rather than hardware design

Recommended next gate, not yet authorized:
1. one bounded CCE-exact software counterfactual that removes full-dC pre-zero while preserving the same full-gradient contract
2. same real shape only; no shape sweep
3. if software removes the residual, close it as software organization
4. only if the residual survives should a second natural workload shape be reviewed before architecture admission, because T255 still prefers materialized B0

No new 174 work or mechanism is authorized by this status.
