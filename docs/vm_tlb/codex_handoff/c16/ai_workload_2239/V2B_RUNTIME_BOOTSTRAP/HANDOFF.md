# C16 AI workload handoff — V2B destination GPU/runtime bootstrap

## Scope

Run this phase on the destination/new Docker only. V1 proved external storage and exact model identity, but the destination container exposed no NVIDIA devices and had no CUDA/PyTorch/transformers/NVBit/NCU closure.

V2B first determines whether the container actually has GPU device pass-through. No userspace/runtime installation is allowed before that gate is understood.

This phase does not rerun RTX4080 R5 and does not create new scientific workload results.

## Authority and V1 boundary

Base result:

- branch `hrl/c16-ai-workload-2239-destination-acceptance-v1`
- commit `43212af0de0eef1cd72d905e11bfdeb2fe0e6d37`
- V1 decision `DESTINATION_BLOCKED_MODEL_OR_INPUT_IDENTITY`

V1 accepted:

- storage root `/root/share/mnt164/huangrulin/c16_ai_workload_2239`
- exact Llama asset revision `4e20de362430cd3b72f300e6b0f18e50e7166e08`

V1 did not accept:

- frozen input contract;
- GPU visibility;
- destination runtime equivalence;
- NVBit closure;
- NCU closure.

Frozen-input recovery is handled independently on branch `hrl/c16-ai-workload-frozen-input-recovery-v2a`. Do not regenerate it here.

## Gate B0 — GPU device exposure

Before installing or rebuilding anything, inspect read-only:

- `/dev/nvidia*`;
- `nvidia-smi` availability and output;
- `/proc/driver/nvidia` if present;
- container-visible GPU-related environment;
- OS/container identity sufficient to diagnose device exposure;
- whether any GPU workload/process is already visible.

Do not kill, reset, attach to, or profile any process.

### If NVIDIA device exposure is absent

Stop runtime installation work. Do not install CUDA, PyTorch, transformers, NVBit, or NCU in an attempt to compensate for missing device pass-through.

Create `HOST_GPU_ENABLEMENT_REQUEST.md` describing the minimum host/container action required to expose the intended RTX4080 to this container while preserving the destination storage mount and existing data. Do not attempt privileged host reconfiguration from inside the container and do not commit private network topology, secrets, or credentials.

Decision must be `BLOCKED_GPU_DEVICE_NOT_EXPOSED`.

### If NVIDIA device exposure is present

Record:

- GPU model;
- GPU UUID;
- driver version;
- logical device mapping;
- compute capability if obtainable without broad workload execution.

Then continue to B1.

## Gate B1 — userspace runtime admission

Inventory first; do not assume source-Docker equivalence.

Target historical compatibility tuple is reference-only:

- Python 3.10.x historical known-good closure;
- PyTorch `2.5.1+cu124`;
- `torch.version.cuda == 12.4`;
- exact destination-visible transformers version must be recorded;
- CUDA toolkit 12.4 tools when required by NVBit/static analysis.

A new destination runtime may be non-equivalent to historical R5. That is acceptable if recorded as a new authority. Never label it historical R5 equivalence without exact proof.

Prefer immutable, hash-verified local wheelhouse/runtime assets already referenced by repository receipts. Do not silently use arbitrary latest packages. Do not access or expose credentials.

If required runtime assets are unavailable, stop with `BLOCKED_RUNTIME_ASSETS_UNAVAILABLE` and document exact missing components.

If installation/build is performed, keep it destination-local and record commands, versions, hashes/manifest identities, PATH, LD_LIBRARY_PATH, CUDA_MODULE_LOADING, and CUDA_VISIBLE_DEVICES policy in a fresh receipt.

After installation, allowed bounded probes are limited to:

- Python import/version checks;
- `torch.cuda.is_available()` and device identity;
- at most one tiny allocation/synchronization sanity probe if no other GPU workload is active.

Do not load Llama in V2B.

## Gate B2 — NVBit and NCU preparation

Only after B0/B1 pass:

### NVBit

Verify or rebuild NVBit 1.7.5 from immutable/hash-bound assets. Record release archive, `core/libnvbit.a`, tracer source and tracer binary hashes. Do not run a model trace. A tiny official fixture may be proposed but not required for this V2B closeout.

### NCU

Record `ncu` binary/version and whether it is present. Do not profile Llama. If permission can be determined without a profiling run, record it. Otherwise leave permission as `NOT_YET_TESTED` for a later bounded canary.

## Storage policy

The admitted external root remains:

`/root/share/mnt164/huangrulin/c16_ai_workload_2239`

V2B may create only small runtime receipts/manifests/scripts under this root if needed. It must not bulk-import raw traces, model assets, or RTX3090 history.

## Required result directory

Create:

`docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V2B_RUNTIME_BOOTSTRAP/RESULTS/`

with at least:

- `GPU_VISIBILITY.md`
- `DESTINATION_RUNTIME_RECEIPT.json`
- `RUNTIME_BOOTSTRAP.md`
- `NVBIT_NCU_STATUS.md`
- `HOST_GPU_ENABLEMENT_REQUEST.md` when GPU is not exposed
- `OPEN_ISSUES.md`
- `V2B_DECISION.json`

`V2B_DECISION.json` must be one of:

- `BLOCKED_GPU_DEVICE_NOT_EXPOSED`
- `BLOCKED_RUNTIME_ASSETS_UNAVAILABLE`
- `DESTINATION_RUNTIME_BOOTSTRAP_PASS`
- `DESTINATION_RUNTIME_BOOTSTRAP_PASS_NVBIT_NCU_PENDING`
- `BLOCKED_OTHER`

## Hard prohibitions

- no Llama/model execution;
- no broad GPU workload;
- no NCU model profiling;
- no NVBit model trace;
- no process kill/reset/attachment;
- no host-privilege escalation or Docker-host mutation from inside the container;
- no arbitrary package upgrades to latest versions;
- no frozen-input regeneration;
- no bulk storage import;
- no RTX3090/RTX4080 authority merge;
- no secrets/private keys/tokens in Git.

Commit and push V2B results, then stop.