# R24 tied-weight gradient lifetime tooling

- `run_r24_campaign_executed.py` is the byte-exact GPU campaign source.
- `run_r24_campaign.py` is the same execution source with the post-formal
  decision condition corrected to match the Goal's two-group regression rule.
- `finalize_r24.py` is the CPU-only decision finalizer over frozen Native formal
  timing and memory tables.

The GPU runner requires the caller to hold
`/data/c16/locks/c16_gpu_campaign.lock` and set `R24_GPU_LOCK_HELD=1`. It imports
the isolated accepted CCE first-store source through `PYTHONPATH`; default global
CCE package state is not modified.
