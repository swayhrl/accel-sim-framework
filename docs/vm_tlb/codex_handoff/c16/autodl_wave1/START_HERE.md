# C16 AutoDL Wave-1 Runtime Handoff

Status: execution handoff only. This branch starts from the accepted Lane-G offline package release `45e293b84940ef59b7b134bcda48aca7d0b99b2f`; it must not rewrite that release.

## Fixed authority and accepted offline inputs

- C16 planning authority: `f222e66f49af56cfd4ded671c4a50c6811237cc2`
- Lane-G accepted offline package / fixed consumption commit: `45e293b84940ef59b7b134bcda48aca7d0b99b2f`
  - producer implementation anchor: `72e9b55f48f04be522ac8937fa1d62e6f7c02baa`
  - publication validator anchor: `e5c86e4be6c02ef2801aceba73869ce7676f163f`
  - G `PUBLISH_MANIFEST.json` SHA256: `7c18c2a806ac37b974702050567430f83f10bbdacc78c5af2fe09ea871896087`
- Lane-C offline Sampling-V2 handoff: `29e669eca19ac3b2a1350bf2d097569a41f123e1`; no native selector may be frozen until G publishes a committed Wave-1 native catalog.
- Lane-H accepted offline memory-fingerprint handoff: `932c6fa44a4896265214fc2136e34698402a5c7f`; C16-4.5 remains pending committed G capture.
- Lane-A rolling package commit is intentionally not hard-coded here. Before any scientific run, G must consume the exact A `P0/P1/...` package commit and its manifest/hash supplied by the user/A lane.

## Execution branch and worktree

- branch: `hrl/vm-c16-g-autodl-wave1-v0`
- recommended local/remote work root: `/root/autodl-tmp/c16/`
- Goal name: `C16_G_AUTODL_WAVE1_RUNTIME`

Do not move or rewrite `45e293b...`. Runtime commits belong only to this continuation branch.

## Preferred Wave-1 GPU platform

Primary target: one exclusive **RTX 3090 24GB (Ampere SM86)** instance. The currently preferred AutoDL class is the 20-core EPYC / 90GB RAM option. Record the actual machine, GPU UUID, driver, clocks/power state, CPU, RAM, disk, and container identity in C16-1.1; do not infer them from a marketplace screenshot.

Storage target: expand the data disk by about 150GB so the working data disk is about 200GB total. Raw profiler/trace data must be hashed and transferred back promptly; do not accumulate the full 64GiB first-wave raw allowance on AutoDL.

## Base image

Preferred public AutoDL base image when available:

`PyTorch 2.5.1 / CUDA 12.4` (the public image currently uses Python 3.12).

Rationale: the image provides a CUDA-12.4 development environment/toolkit close to the frozen `torch==2.5.1+cu124` plan. **Do not use the image's preinstalled Python-3.12 PyTorch as the scientific C16 environment.** The accepted G wheelhouse is Linux x86_64 / CPython 3.10.

All AutoDL images include Miniconda. Create a dedicated Python-3.10 environment under the data/work disk, then install only the accepted hash-closed wheelhouse:

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda create -y -p /root/autodl-tmp/c16/py310 python=3.10 pip
C16_PYTHON=/root/autodl-tmp/c16/py310/bin/python \
  bash util/vm_tlb/c16/lane_g/bootstrap_autodl.sh --install \
  --wheelhouse /root/autodl-tmp/c16/wheelhouse \
  --venv /root/autodl-tmp/c16/env \
  --python /root/autodl-tmp/c16/py310/bin/python
```

The `conda create` step is setup only; the heavy Python/CUDA packages must come from the prebuilt wheelhouse. If the UI offers a clean Miniconda image with Python 3.10 and CUDA 12.x development toolkit, it is also acceptable after recording the exact image identity; keep the same frozen wheelhouse/runtime versions.

## Rolling A package policy

Do not wait for every Wave-1 model if A can publish a hash-closed immutable rolling package.

- `P0`: Llama3.2-1B + frozen input/token receipts + scenarios + accepted G/C/H small artifacts + wheelhouse manifest/hashes.
- `P1+`: immutable delta packages for newly completed Qwen models.

Each package version requires a separate fixed A commit, package manifest, payload hashes, and transfer receipt. Never mutate `P0` in place. A large model transfer must occur between formal profiling/capture runs, not concurrently with a measured run.

## C16-1 inline qualification and release rules

1. **C16-1.1 instance receipt**
   - record actual RTX3090 identity, UUID, driver, CUDA/toolkit view, CPU/RAM/disk, clocks/power/temperature state, AutoDL IDs, and observed instance-start timestamp;
   - initialize the accepted shared execution-budget ledger from this receipt.

2. **C16-1.2 transfer/import closure**
   - transfer the current A rolling package, G wheelhouse, code, and receipts;
   - verify every consumed payload against the exact expected SHA256 before use;
   - quarantine any mismatch; never repair a scientific input in place.

3. **Runtime environment closure**
   - create/use CPython 3.10;
   - install the hash-closed wheelhouse with `--no-index`;
   - `pip check`, import check, and `torch.version.cuda` receipt;
   - G0 must reject CPU fallback, dtype fallback, changed quantization/backend, or unexpected model revision.

4. **G0 native canary**
   - run Llama3.2-1B S0 first when only P0 is available;
   - correctness/output checksum, dtype, backend, peak VRAM, GPU timing, temperature/clock/power state before/after.

5. **G1 Nsight Systems/NVTX canary**
   - verify tool presence/version, launch count, streams, kernel names, CUDA correlation, NVTX phase boundaries, and bounded overhead;
   - if `nsys` is absent, resolve with a pinned/versioned NVIDIA CLI package and hash receipt if practical; otherwise mark G1 capability-limited. Do not block G0 baseline.

6. **G2 Nsight Compute canary**
   - query available metrics on the actual machine;
   - freeze a compact metric list; one bounded target only;
   - if counters are permission-restricted, record `COUNTER_UNAVAILABLE`; do not substitute a vaguely similar metric.

7. **G3 NVBit canary**
   - vector-add/tiny fixture first, then one revalidated model kernel;
   - verify target in/out filtering, trace terminal state, active-mask/width parsing, manifest/hash closure, 4GiB/20min guard;
   - failure does not block G0/G1 census.

**Release rule:** G0 success immediately allows unprofiled native baseline. G1 success immediately allows full lightweight kernel census. Do not wait for G2/G3 if they are capability-limited.

## First scientific sequence

With P0 only:

1. Llama S0 G0/G1/G2/G3 canaries.
2. If G0+G1 pass, Llama S1/S2 native baseline and lightweight kernel census.
3. Publish a small committed canary/native checkpoint as soon as useful; do not wait for Qwen downloads.
4. When A publishes P1/P2 deltas, transfer between formal runs, hash-verify, then execute Qwen scenarios.

Wave-1 deployment order after assets arrive:

1. Llama3.2-1B (bridge/canary; no new large simulator matrix)
2. Qwen2.5-0.5B
3. Qwen2.5-7B raw
4. Qwen2.5-7B AWQ

If a frozen scenario exceeds RTX3090 VRAM, record `SKIPPED_RESOURCE` with peak/failed-allocation evidence. Do not silently shorten context, reduce batch, change dtype, enable CPU offload, or switch to multi-GPU.

## Native catalog publication gate

A committed `NATIVE_CATALOG_V1` usable by Lane C must include at least:

- `KERNEL_CATALOG.tsv`
- `KERNEL_SEMANTIC_MAP.tsv`
- `SEMANTIC_COVERAGE.tsv`
- `NATIVE_BASELINE.tsv`
- `RUNTIME_IMPLEMENTATION_AUDIT.tsv`
- `HEAVY_TAIL_KERNELS.tsv` or sufficient fixed inputs for C to recompute it
- manifest + exact producer/tool/runtime/GPU identity

Semantic/operator mapping must be direct/runtime-evidence-first. Name-only guesses remain `UNKNOWN`. Target >=95% cumulative GPU-time semantic coverage is an engineering goal, not permission to invent labels.

## Measurement hygiene on RTX3090

RTX3090 is the Wave-1 scientific platform, not merely a cheap canary. Keep all Wave-1 comparisons on the same instance if possible. Record at least before/after baseline/profile groups:

- temperature
- performance state
- graphics/memory clocks
- power draw/limit
- throttling reason if exposed

Use the frozen repeat policy (2 warmups + 3 measured runs, bounded extension to 5 for high noise). Report median/min/max/CV. Do not synchronize every kernel merely to obtain timing.

## Data and cost discipline

- One shared execution-budget ledger; <=24 GPU-instance-hours first-wave envelope.
- NVBit: <=6 windows/deployment, <=4GiB or <=20min per window, <=64GiB total first-wave raw.
- Large raw files stay outside Git. Record path/size/SHA/run/transfer/retention in `RAW_INDEX.tsv`.
- Transfer/hash/cleanup of raw data promptly.
- Do not run large rsync/model transfer concurrently with a formal baseline/profile/capture measurement.
- AutoDL is for native inference, profiling, and bounded capture. Do not run long Accel-Sim/GPGPU-Sim experiments there.

## Stop / handoff points

Stop and publish instead of improvising when any of these occur:

- A rolling package hash/identity mismatch;
- GPU/dtype/backend fallback;
- unexpected model revision;
- no room for a frozen scenario (record `SKIPPED_RESOURCE`);
- profiler/counter/NVBit capability gap after bounded attempts;
- budget guard exhaustion.

Ordinary engineering issues (paths, missing CLI package, build fixes, resumable transfer) should be actively solved with exact receipts rather than causing immediate abandonment.

## Scientific boundary

RTX3090 native results and the existing 35-SM modeled paper-style platform are separate evidence domains. Do not describe RTX3090 as the modeled platform. If later representative traces feed Accel-Sim, validate the trace/ISA/config bridge explicitly; C16 Wave-1 does not assume native and modeled hardware are identical.
