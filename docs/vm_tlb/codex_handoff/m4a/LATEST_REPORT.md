# M4A-P pre-capture preparation report

Stage: `M4A_PRECAPTURE_PREP`

Status: `CONDITIONAL_PASS`.

## Result

M4A-P completed its authorized preparation scope.  No external GPU was rented,
no LLM trace was collected, no Core VM/TLB source was changed, and M4A-C has
not started.

The required legacy-asset audit recovered the user's actual AutoDL collection
campaign on `hrl/decoupled-l2-exp-v0` at
`3bed497023c7ee52e2b7ea0393628f34997ea974`.  Its preflight, serial campaign,
disk-guard, postprocess verification, checksummed archive, and verified
offload patterns are adapted by the prepared M4A package.  There is no prior
LLM/AutoDL collector or `trace_b200.sh` in the declared search scope.

## Capture recommendation and entry

Rent one exclusive SM86 RTX 3090-class GPU (24 GiB or more), with 500 GiB free
NVMe before tracing.  An RTX3070/3080 Ti is also architecture-compatible if
its VRAM is sufficient.  Do not substitute SM70/80/89/90/120 SASS for the
RTX3070-class paper route.

After explicit M4A-C authorization only, the exact entry is:

```bash
M4A_C_AUTHORIZED=1 bash util/llm_trace_capture/run_m4a_c.sh \
  --framework-root "$PWD" --work-root /mnt/nvme/m4a-llama \
  --workload-command-file /mnt/nvme/m4a-llama/llama_workload.sh \
  --minimum-free-gib 500
```

Without `M4A_C_AUTHORIZED=1` it exits `BLOCKED` before touching the workload.

## Evidence and outstanding blockers

- Stable contracts and the legacy audit: `docs/vm_tlb/llm/`.
- Prepared static tooling and gated driver: `util/llm_trace_capture/`.
- Review entry: `docs/vm_tlb/review_packs/M4A_PRECAPTURE_PREP/README.md`.
- Public author code, exact trace, TP=4 capture method, dtype, contiguous
  loader, sub-entry, PTW, and synthetic-KV details remain
  `PAPER_DETAIL_UNAVAILABLE`.
- Local host has CUDA 11.8 but no visible GPU, no built tracer, no LLM Python
  stack/model cache, and only 231 GiB free, so it correctly classifies as
  `EXTERNAL_SM86_GPU_REQUIRED`.

## Provenance

- Preparation content commit:
  `e6a98c7748e5cd7f55e89eb966506efb1eb54231`.
- This report's closeout commit is the branch `HEAD` after commit/push.
- Core commit: none.

STOP BEFORE `M4A_EXTERNAL_CAPTURE`.
