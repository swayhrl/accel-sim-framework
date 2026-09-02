# M4A-PR2 pre-rental review-fix report

Stage: `M4A_PRERENTAL_REVIEW_FIX`

## READY_TO_RENT_REVIEW_FIX_PASS

The Route-E package passed the final no-GPU review fix. M4A-C remains
unauthorized: this result did not rent/access a GPU, change a driver, download
formal Llama weights, collect a trace, implement Segmentation, or create
synthetic KV.

Route E remains the sole selected formal self-capture route: one physical host
with four same-model SM86 GPUs, actual TP=4, and NVBit injected solely into
rank 0. It is `PAPER_COMPATIBLE_SELF_CAPTURE`, not author-exact. A full-model
single-GPU trace remains rejected as a formal paper workload; Route A remains
an approval-required approximation.

The review-fix began at required handoff
`38c9b224dae55002b159f07c9f4fc3b4035ce8d5`; final commit is recorded in the
review pack after push.

## Completed RF0–RF7

- RF0: clean required handoff and stale lock values audited.
- RF1/RF2: selected `--cuda-home` now controls NVBit Make invocation through
  explicit realpath `nvcc`/`ptxas` and scoped PATH; capture-ready preflight
  records selected and host-PATH tools, versions, provenance, PyTorch runtime
  CUDA, build artifacts, NVBit marker, and artifact digests. Fake CUDA A/B
  proves PATH B cannot be selected.
- RF3: `cuMemcpyHtoD_v2` now uses the same profiler ROI state as kernels when
  `ACTIVE_FROM_START=0`; inactive initialization copies cannot enter formal
  replay lists while active copies remain eligible.
- RF4: classifier has `COMPUTE`, `NCCL_COLLECTIVE`, `MEMCPY`, and
  `UNKNOWN_OTHER`; derived compute-only excludes the latter three and raw order
  remains intact.
- RF5/RF6: lock digests/docs were refreshed and all required no-GPU regression
  tests passed, including M4A-C guard.
- RF7: this report and `M4A_PRERENTAL_REVIEW_FIX` review pack are complete.

## Future-only sequence after a new M4A-C authorization

1. `host_preflight.py` on the rented host.
2. Create the isolated locked environment and run
   `bootstrap_route_e_nvbit.sh --cuda-home /opt/cuda-12.6` with the selected
   CUDA 12.6 toolkit path.
3. Run `run_generic_nvbit_smoke.sh --cuda-home /opt/cuda-12.6`, then
   `capture_ready_preflight.py --cuda-home /opt/cuda-12.6`.
4. Only then run `run_m4a_c.sh --cuda-home /opt/cuda-12.6` separately with `--trace-region prefill` and
   `--trace-region decode1`; preserve raw rank-0 trace and derive manifests.

The review pack is `docs/vm_tlb/review_packs/M4A_PRERENTAL_REVIEW_FIX/`.
STOP for ChatGPT review before M4A-C.
