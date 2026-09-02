# M4A-PR pre-rental finalization report

Stage: `M4A_PRERENTAL_FINALIZE`

## READY_TO_RENT

The Route-E package is ready for the user to rent a qualifying host. This is a
package readiness decision only: M4A-C remains unauthorized and this stage did
not rent/access an external GPU, download model weights, collect a trace,
implement Segmentation, or create synthetic KV.

Route E remains the sole selected formal self-capture route: one physical host
with four same-model SM86 GPUs, actual TP=4, and NVBit injected solely into
rank 0. It is `PAPER_COMPATIBLE_SELF_CAPTURE`, not author-exact. A full-model
single-GPU trace remains rejected as a formal paper workload; Route A remains
an approval-required approximation.

The finalized Route-E package source commit is
`4c4c083bac8d17f9a6901fc7132c273ade2d6849`, based on the required handoff
`51a36b376a8c6a59c02c181b26233bd0c4c3322f`.

## Completed PR0–PR10

- PR0: required handoff `51a36b376a8c6a59c02c181b26233bd0c4c3322f` was the
  starting `HEAD`; Route E, frozen NVBit 1.7.6, and profiler capability audited.
- PR1: parent and wrapper clear inherited injection; only `trace` rank 0 sets
  it. The no-GPU four-rank mock proves smoke none / trace rank-0-only.
- PR2: separate `prefill` and `decode1` runs use `ACTIVE_FROM_START=0` plus
  CUDA profiler control; loading, TP setup, flat binding, sidecar prep, and
  warmup remain inactive. `decode_reuse` is diagnostic-only.
- PR3/PR4: explicit Python/PyTorch/CUDA/tool/package/model/NVBit lock,
  metadata-only immutable model SHA, SHA-verifying NVBit bootstrap, and generic
  CUDA/NVBit smoke are prepared. No driver change is permitted.
- PR5–PR9: split preflights, real KV runtime event preparation, raw NCCL
  preservation/classification, separate ROI archives, and AutoDL checklist are
  complete. RTX 3080 Ti 12 GiB is acceptable; rent one host with >=4 idle
  same-model SM86 GPUs, >=500 GiB free/expandable local disk, adequate RAM, and
  SSH/copy-back.
- PR10: all permitted no-GPU syntax, static, fake, mock, dry-run, classifier,
  and authorization-guard tests passed. See the review pack.

## Future-only sequence after a new M4A-C authorization

1. `host_preflight.py` on the rented host.
2. Create the isolated locked environment and run
   `bootstrap_route_e_nvbit.sh` with its explicit CUDA toolkit path.
3. Run `run_generic_nvbit_smoke.sh`, then `capture_ready_preflight.py`.
4. Only then run `run_m4a_c.sh` separately with `--trace-region prefill` and
   `--trace-region decode1`; preserve raw rank-0 trace and derive manifests.

The review pack is `docs/vm_tlb/review_packs/M4A_PRERENTAL_FINALIZE/`.
STOP BEFORE M4A-C.
