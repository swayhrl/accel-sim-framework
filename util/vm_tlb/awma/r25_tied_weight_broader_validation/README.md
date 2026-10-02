# R25 tied-weight broader validation tooling

- `run_r25_campaign.py` is the frozen point-generic D0/H0 qualification and formal runner.
- `accepted_r24_base.py` is the exact accepted R24 helper authority (`6526c54c...`).
- `freeze_r25.py` closes the two-point numerical/trajectory gate before formal timing.
- `finalize_r25.py` performs CPU-only decision classification and review-pack generation.
- `publish_r25.py` prepares and verifies the immutable node164 raw publication.

The formal runner requires `R25_GPU_LOCK_HELD=1`; callers must hold
`/data/c16/locks/c16_gpu_campaign.lock` for the entire CUDA/JIT process.
CCE autotuning is disabled and the accepted first-store source must be supplied
through `PYTHONPATH`.

The three arms are `B0_DENSE_STRONG`, `C1_COMPACT_FULL`, and `S2_TILED`.
C1 uses sorted unique lookup rows plus one full classifier/total gradient. S2
uses the same compact lookup reducer plus deterministic row tiles derived from
a 32 MiB FP32-gradient budget and never forms a full VxH gradient in formal
execution.
