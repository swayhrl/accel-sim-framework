# M4A-PF pre-capture fixup report

Stage: `M4A_PRECAPTURE_FIXUP`

Status: `CONDITIONAL_PASS`.

## Result

The authorized fixup completed. No external GPU was rented, no LLM trace was
collected, no Core VM/TLB source was changed, and M4A-C has not started.

The formal preferred candidate is Route E: real TP=4 on one **4 x SM86** node
and NVBit injection only for rank 0. It is `PAPER_COMPATIBLE_SELF_CAPTURE`,
not author-exact. Rank-0 collective/NCCL activity is retained and tagged for a
later explicit compatibility decision. Route A (one SM86 rank-local emulation)
remains a `DOCUMENTED_APPROX` candidate requiring approval. A full-model
single-GPU trace is explicitly rejected as a formal paper workload.

## Capture recommendation and entry

Do not rent yet. If Route E is selected after review, require four same-model
SM86 GPUs on one node (24 GiB+ each) and 500 GiB free NVMe. A single RTX3090
is appropriate only if Route A is later selected and explicitly approved.

After explicit M4A-C authorization only, the exact entry is:

```bash
M4A_C_AUTHORIZED=1 bash util/llm_trace_capture/run_m4a_c.sh \
  --framework-root "$PWD" --work-root /mnt/nvme/m4a-llama \
  --workload-command-file util/llm_trace_capture/run_llama_tp4_rank0.sh \
  --required-gpu-count 4 \
  --minimum-free-gib 500
```

Without `M4A_C_AUTHORIZED=1` it exits `BLOCKED` before touching the workload.

## Evidence and outstanding blockers

- Route analysis: `docs/vm_tlb/llm/TP_CAPTURE_ROUTE_DECISION.md`.
- Concrete wrapper: `util/llm_trace_capture/run_llama_tp4_rank0.sh`.
- Pinned runtime: `util/llm_trace_capture/requirements-llama-tp4.txt`.
- Runtime flat-buffer binder/sidecar: `util/llm_trace_capture/llama_tp_workload.py`.
- Review entry: `docs/vm_tlb/review_packs/M4A_PRECAPTURE_FIXUP/README.md`.
- Public author code, exact trace, TP=4 capture method, dtype, contiguous
  loader, sub-entry, PTW, and synthetic-KV details remain
  `PAPER_DETAIL_UNAVAILABLE`.
- Local host has CUDA 11.8 but no visible GPU, no built tracer, no LLM Python
  stack/model cache, and only 231 GiB free, so it correctly classifies as
  `EXTERNAL_SM86_GPU_REQUIRED`.

## Provenance

- Prior M4A-P preparation commit: `e6a98c7748e5cd7f55e89eb966506efb1eb54231`.
- This report's closeout commit is the branch `HEAD` after commit/push.
- Core commit: none.

STOP BEFORE `M4A_EXTERNAL_CAPTURE`.
