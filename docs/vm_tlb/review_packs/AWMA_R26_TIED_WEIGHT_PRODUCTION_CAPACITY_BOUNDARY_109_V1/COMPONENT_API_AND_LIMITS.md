# Component API and limits

`TiedWeightTrainer.run_step(policy="c1")` defaults to C1. S2 requires both explicit `policy="s2"` and the campaign opt-in sentinel. State save/load covers tied BF16 W, FP32 m/v, logical step, CPU/CUDA RNG, identity, and policy metadata; policy changes do not reset state.

Supported scope is only this tied input-embedding/lm-head W with the frozen full backbone in the dH path, fixed CCE exact math, and explicit AdamW. Unsupported: arbitrary autograd consumers, all-parameter training, gradient accumulation, clipping, scaler, checkpointing/offload, distributed training, scheduler, quantization, or automatic OOM fallback. No existing workflow is modified.
