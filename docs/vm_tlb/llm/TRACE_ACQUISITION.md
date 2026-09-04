# M4A-C external capture runbook (prepared only)

**M4A-C is not authorized.  Do not rent, install, build, or capture from this
runbook until the handoff explicitly changes.**  The executable entry point
also refuses unless `M4A_C_AUTHORIZED=1` is deliberately supplied after that
authorization.

## Exact entry point after authorization

```bash
M4A_C_AUTHORIZED=1 bash util/llm_trace_capture/run_m4a_c.sh \
  --framework-root "$PWD" --work-root /mnt/nvme/m4a-llama \
  --cuda-home /opt/cuda-12.6 \
  --workload-command-file util/llm_trace_capture/run_llama_tp4_rank0.sh \
  --trace-region prefill \
  --required-gpu-count 4 \
  --minimum-free-gib 500
```

Run this command separately for `prefill` and `decode1`; `decode_reuse` is
diagnostic-only. Before it, use the explicit environment in `CAPTURE_ENV_LOCK`,
run host preflight, `bootstrap_route_e_nvbit.sh`, generic smoke, and
capture-ready preflight. Do not use the old unpinned `install_vllm.sh`.

## Required order and release gate

1. Record `nvidia-smi -L`, full `nvidia-smi`, driver, CUDA, CPU/RAM, OS/image,
   free disk, Framework SHA, wrapper digest, and NVBit archive checksum. Require
   four same-node same-model SM86 GPUs with at least 12 GiB each and 500 GiB free disk.
2. Run `host_preflight.py`, then `capture_ready_preflight.py --cuda-home
   /opt/cuda-12.6`; reject any
   non-SM86 source or failed isolated-environment lock.
3. Run a tiny known-good CUDA/NVBit trace through postprocessing and archive
   validation.  Do not start LLM work if it fails.
4. Run the frozen workload normally (`M4A_PHASE=smoke`): B8, S64, 3 tokens,
   exact model/tokenizer/dtype/TP method logged.
5. Produce and validate the contiguous tensor layout and allocation sidecar.
   Runtime VA ranges, no overlap, and cross-kernel stability must be checked.
6. Run the tiny LLM trace smoke, measure bytes/kernel, and recompute the disk
   safety margin.  Stop if inadequate.
7. Trace `prefill` and `decode1` independently with profiler-controlled ROI;
   use minimal `decode_reuse` only diagnostically. Never attempt a 12K trace.
8. Postprocess, validate metadata coverage, produce SHA256 manifest, package
   with `tar.zst` (or documented `tar.gz` fallback), copy back, verify the
   archive, then retain or release the rental instance.

Large traces/model weights/tokens stay out of Git.  A self capture is
`PAPER_COMPATIBLE_SELF_CAPTURE`, never the authors' trace.
