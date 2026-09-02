# M4A-C external capture runbook (prepared only)

**M4A-C is not authorized.  Do not rent, install, build, or capture from this
runbook until the handoff explicitly changes.**  The executable entry point
also refuses unless `M4A_C_AUTHORIZED=1` is deliberately supplied after that
authorization.

## Exact entry point after authorization

```bash
M4A_C_AUTHORIZED=1 bash util/llm_trace_capture/run_m4a_c.sh \
  --framework-root "$PWD" --work-root /mnt/nvme/m4a-llama \
  --workload-command-file /mnt/nvme/m4a-llama/llama_workload.sh \
  --minimum-free-gib 500
```

Before this command, use an isolated venv/container and build the frozen
Framework NVBit tracer under the selected checkout.  Pin and record every
package/model revision; do not use the old unpinned `install_vllm.sh` as-is.

## Required order and release gate

1. Record `nvidia-smi -L`, full `nvidia-smi`, driver, CUDA, CPU/RAM, OS/image,
   free disk, Framework SHA, and NVBit archive checksum.  Require one SM86 GPU
   with at least 24 GiB VRAM and 500 GiB free disk.
2. Run `preflight.py`; reject a non-SM86 source for the paper route.
3. Run a tiny known-good CUDA/NVBit trace through postprocessing and archive
   validation.  Do not start LLM work if it fails.
4. Run the frozen workload normally (`M4A_PHASE=smoke`): B8, S64, 3 tokens,
   exact model/tokenizer/dtype/TP method logged.
5. Produce and validate the contiguous tensor layout and allocation sidecar.
   Runtime VA ranges, no overlap, and cross-kernel stability must be checked.
6. Run the tiny LLM trace smoke, measure bytes/kernel, and recompute the disk
   safety margin.  Stop if inadequate.
7. Trace only allocation context, seq-64 prefill, first decode, and minimal
   reuse iterations.  Never attempt a 12K instruction trace.
8. Postprocess, validate metadata coverage, produce SHA256 manifest, package
   with `tar.zst` (or documented `tar.gz` fallback), copy back, verify the
   archive, then retain or release the rental instance.

Large traces/model weights/tokens stay out of Git.  A self capture is
`PAPER_COMPATIBLE_SELF_CAPTURE`, never the authors' trace.
