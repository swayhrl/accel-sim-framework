# R26 tied-weight production-capacity tooling

- `component.py`: scoped tied-W component; C1 is default and S2 is explicit opt-in.
- `run_r26_campaign.py`: bootstrap, numerical trajectories, resume/switch, probes, endpoint correctness, and formal modes.
- `capacity_search.py`: frozen exponential-plus-midpoint natural-OOM search and 3/3 confirmations.
- `freeze_r26.py`: post-qualification implementation/classifier freeze.
- `finalize_r26.py`: CPU-only evidence and review-pack generation.
- `publish_r26.py`: node164 raw/checkpoint publication and readback closure.
- `closeout_r26.py`: mechanical post-finalizer hash closure.

All CUDA/JIT callers must hold
`/data/c16/locks/c16_gpu_campaign.lock` and set the lock sentinel inherited by
fresh subprocesses. S2 additionally requires the explicit capacity opt-in.
There is no automatic OOM retry or policy fallback.

The supported training scope is deliberately narrow: one BF16 tied
input-embedding/lm-head W, FP32 AdamW moments, and the frozen full backbone in
the dH path. Physical batch repeats one immutable 127-position sequence.
Arbitrary autograd consumers, all-parameter training, accumulation, offload,
activation checkpointing, distributed execution, scheduler, and deployment
integration are unsupported.
