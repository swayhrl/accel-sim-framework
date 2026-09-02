# Legacy AutoDL / rented-server capture asset audit

Audit date: 2026-09-02.  Scope: `/workspace/repos`, all visible
`/workspace/worktrees`, and every local/remote ref reachable from the Framework
repository.  Search terms included `AutoDL`, `autodl`, `run_hw_trace.py`,
`install_nvbit.sh`, `trace_b200.sh`, capture/collector variants, archive
formats, NVBit, `vllm`, and `llama`; trace/result payload directories were not
content-scanned.  No `trace_b200.sh` or pre-existing LLM AutoDL collector was
found.

## Reusable assets

| Asset | Provenance and intended environment | What it does | M4A disposition |
|---|---|---|---|
| `experiments/v100_trace_campaign/{README.md,framework_source.json,scripts/preflight_host.sh,build_workloads.sh,campaign.py,offload_archives.sh}` | tracked in `hrl/decoupled-l2-exp-v0`, commit `3bed497023c7ee52e2b7ea0393628f34997ea974` (2026-08-26); V100/SM70, CUDA 11.8, NVBit 1.7.6, AutoDL | strict host preflight; serial resumable NVBit runs; native/discovery/trace phases; disk guard; postprocess validation; SHA256 + `.tar.zst`; verified rsync/rclone offload | **Adapt control pattern**, never reuse its V100 binaries/SASS/manifest as an SM86 LLM trace |
| `experiments/v100_common_trace_campaign/scripts/run_common_capture.sh` | same commit and host | invokes the proven runner for a second manifest | **Reference only**; workload-specific wrapper |
| `util/tracer_nvbit/{install_nvbit.sh,run_hw_trace.py,tracer_tool/*}` | tracked current branch `aa901732753c5ca0c66694932456720081e468cd`; copies in `/workspace/repos/accel-sim-framework` and TLS worktree hash-identical | installs NVBit 1.7.6; instruments workload; post-processes to `kernelslist.g`/`.traceg` | **Reuse as frozen tracer base**, after target-host SM86 smoke |
| `scripts/accelsim/a3_trace_rodinia_smoke.sh` in `/workspace/repos/accel-sim-framework` | tracked at `a1097b4d4f8ddea18fb82511e26f712c26e162e8` | GPU/tracer/app/trace/simulator smoke reporting | **Adapt preflight/reporting ideas**; not an AutoDL LLM collector |
| `src/cuda/vllm/install_vllm.sh` in `/workspace/worktrees/gpu-app-collection-decoupled-l2` | local tracked worktree at `dad09cb0487845edc7524ded814c6cde9f0ef6a1` | creates venv then installs unpinned latest vLLM and fetches examples | **Retire as-is**: lacks version pins, workload contract, tracing, metadata, and archive integrity |
| `util/tracer_nvbit/others/torch_hook/*` | official `upstream/dev`, commit `0db04452ec1c47630e4b08002067d82c6811e243`; Hopper-focused | vLLM/PyTorch layer hook and tracing wrapper | **Do not import in M4A-P**: absent from frozen branch and not an SM86 validation |

The V100 campaign README reports intended AutoDL operation and internal
`PASS tracer smoke` code paths, but this audit found no committed completed-run
log for the LLM workload.  Therefore no asset is treated as evidence that an
LLM trace was previously collected.
