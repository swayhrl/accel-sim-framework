# AutoDL V100 capture-host handoff

Roles: SIM_HOST owns this branch, immutable replay trace store and all M5
simulation; a temporary AutoDL V100 is a capture worker only. It must not
commit scientific history. The SIM_HOST Goal uses SSH/rsync to preflight,
capture, archive, copy back, verify, unpack once into the shared store, then
continue replay.

## Reused operational evidence (not scientific identity)

| asset | prior proof | M5 reuse |
| --- | --- | --- |
| `3bed4970:.../preflight_host.sh` | single-V100, CUDA11.8, data-mount free-space preflight | template for SSH/preflight, with current tracer/source identity |
| `3bed4970:.../offload_archives.sh` | `rsync --partial --append-verify`, remote/local SHA equality, receipt-before-prune | transfer algorithm only; no old archive identity |
| `/workspace/m4a-rented-host-pilot/*/COPYBACK_VERIFICATION.md` | AutoDL archive copyback SHA PASS | external archive metadata/checksum sequence |
| `/workspace/m4a-rented-host-pilot/pre-shutdown/.../RESUME_STATE.md` | `/root/autodl-tmp` NVMe data mount and no-active-session audit | choose a preflighted large data volume; do not inherit CUDA12.6/NVBit1.7.6 identities |

## AutoDL preflight

Create a remote work root on the preflighted large data mount, never the root
filesystem. Require exactly one CUDA-visible V100, UUID/name/CC 7.0, driver,
CUDA 11.8 `nvcc`/`ptxas`, CPU/RAM, `df`, write test, git/make/g++/zstd/tar,
tmux or screen, and bidirectional SSH/rsync. The current controller independently
proves the selected CUDA logical device using a CUDA-runtime probe.

Remote BICG pilot template (endpoint supplied only after rental):

```bash
ssh <autodl-endpoint> 'cd <remote-framework@0db04452>; CUDA_VISIBLE_DEVICES=0 \
  NVCC=/usr/local/cuda-11.8/bin/nvcc util/dtc_l1/capture_m5_paper10_traces.sh \
  --polybench-src <polybench> --tracer-framework-src <remote-framework> \
  --nvbit-archive <nvbit-1.8.tar.bz2> --out <large-data-volume>/m5-paper10 \
  --workloads bicg --pilot-only'
```

After controller archive PASS, rsync archive and sidecar to SIM_HOST, compare
source/destination SHA, unpack into the one immutable trace store, and rerun
the internal `SHA256SUMS` validation before replay. Existing Llama traces,
CUDA12.6, NVBit1.7.6 and old binary/input/tracer hashes are operational history
only and are never M5 Paper evidence.
