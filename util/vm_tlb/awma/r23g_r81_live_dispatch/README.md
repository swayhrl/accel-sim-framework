# R23G live RULE_U01 validation

- `prepare_public_input.py` performs CPU-only canonical extraction, XGrammar
  compile filtering, hash sorting, and 24-record pool creation.
- `run_live_dispatch_campaign.py` runs the single persistent GPU campaign:
  B0-only qualification, final-12 freeze, old-R81 union canary, new semantic
  qualification, and paired B0/M1 timing.

The campaign runner requires `R23_GPU_LOCK_HELD=1`; the caller must hold
`/data/c16/locks/c16_gpu_campaign.lock`. The accepted R81 `heads.py` is imported
unchanged. Union/dispatch follows the review pack's frozen contract and no
alternative algorithm is implemented.
