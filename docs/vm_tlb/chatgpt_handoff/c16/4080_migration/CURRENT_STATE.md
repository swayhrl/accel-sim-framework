# C16 RTX4080 Current State

## Scope and ownership

This file is the ChatGPT-owned coordination state for the C16 RTX4080 platform lane only.
It must not replace the older top-level `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`, which belongs to the M4 integration track.

## Source anchor

- Repository: `swayhrl/accel-sim-framework`
- Current execution branch: `hrl/c16-4080-userspace-runtime-ncu-nvbit175`
- Current execution HEAD: `8b1fae1b1d4eb3d95928f51020a94fa04e9635c1`
- Previous userspace-runtime closure: `c463c017372361d8422038f1d26d5ba2cbafde41`
- NCU N0/N1 closure: `ba9afb264746b3290607ae5e5e5d8642941bc11f`

## Frozen host facts

- Research user: `huangrulin`, UID/GID `1004:1004`, no sudo, not in docker group.
- GPU: NVIDIA GeForce RTX 4080, UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`, CC 8.9.
- Driver: `580.178.04`.
- Kernel: `7.0.0-31-generic`; classified as `PREEXISTING_KERNEL_BOOT_SELECTION` because `-31` was installed before C16 B1.
- Host CUDA symlink: `/usr/local/cuda -> /usr/local/cuda-12.8`.
- NCU: `/opt/nvidia/nsight-compute/2025.1.1/ncu`, version `2025.1.1.0`.
- Profiling permission: `RmProfilingAdminOnly: 0`.
- Data root: `/data/c16`.

## Completed stages

### Host / NCU

- Phase B1: PASS.
- NCU N0: `NCU_N0_ORDINARY_USER_PERMISSION_PASS`.
- NCU N1: `NCU_N1_HARDWARE_COUNTER_CANARY_PASS`.
- N1 metric: `sm__cycles_elapsed.avg = 32375.236842 cycle`.
- N1 raw report: `/data/c16/ncu/C16_NCU_N1_vector_add_20260914T094300Z.ncu-rep`.
- N1 raw SHA256: `d2e97a920a998d76f14902d21e3d71b6e23d11ad00cf2eed797b4b0758e07102`.

### Userspace runtime U0-U3

- U0: PASS userspace build path.
- U1: PASS CPython 3.10.12 userspace build.
- U2: PASS exact 66-wheel offline runtime.
- `torch == 2.5.1+cu124`, `torch.version.cuda == 12.4`, `transformers == 4.46.3`, `AutoAWQ == 0.2.7.post3`.
- `libtorch_cuda.so` SHA256 matches known-good: `761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a`.
- U3: PASS RTX4080 PyTorch CUDA canary with `CUDA_MODULE_LOADING=EAGER`.

## Llama U4 asset state

Required identity:

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

A server-to-server rsync has placed the six payload files at:

`/data/c16/models/.incoming/Llama-3.2-1B/4e20de362430cd3b72f300e6b0f18e50e7166e08`

Source host path used for transfer:

`/root/share/c16_recovery_v3/models/llama_3p2_1b/4e20de362430cd3b72f300e6b0f18e50e7166e08`

The source-side operator reported an `R1_LLAMA3P2_1B_ASSET_RECEIPT.json` binding the exact model/revision and hash-closed payloads. Source and destination payload SHA256 values were manually checked to match after rsync. This transfer evidence is useful but U4 is not yet formally closed until the importer binds payload hashes to an authoritative provenance receipt/manifest rather than to the directory name alone.

U4 status: `LOCAL_ASSET_IMPORT_PENDING`.

## NVBit U8 state

Environment: NVBit 1.7.5, SM89, driver 580.178.04, `CUDA_MODULE_LOADING=EAGER`.

- U8.1 archive/core hash: PASS.
- U8.2 SM89 build: PASS.
- U8.3 official vectoradd native: PASS.
- U8.4 official `instr_count_bb`: PASS; 50,066 instructions observed.
- U8.5 custom C16 no-match/zero-trace closure: `PARTIAL_FAIL_TOOL_CLOSURE`; Python fixture exited 0 and zero traces were produced, but the custom tool did not emit the required NVBit READY marker.
- U8.6 PyTorch elementwise under NVBit: PASS.
- U8.7 PyTorch GEMM under NVBit: PASS; kernel `ampere_sgemm_64x32_sliced1x4_tn` observed.
- No evidence justifies a driver/root handoff. Driver 580 is empirically usable for official and PyTorch NVBit diagnostics on this RTX4080.

Raw U8 evidence root:

`/data/c16/results/C16_U8_NVBIT175_20260914T111145Z`

Raw manifest SHA256:

`6c801de25d08a58bf04f8ef6a5349665bfeb3ee6d99e28795e530d935cb30f8e`

## Interpretation of U8.5

U8.5 is a userspace custom-tool closure defect, not evidence of an NVBit/driver platform failure. It does not block U5-U7 once U4 closes. It does block U9 because U9 requires a qualified C16 custom tracer lifecycle and exact READY/no-prearm behavior.

## Immediate execution order

1. Close U4 using the transferred local exact asset and authoritative source provenance/hash evidence.
2. In parallel or before U9, repair U8.5 custom C16 tool closure so READY/TERMINAL and bounded no-match zero-trace behavior are proven.
3. After U4 PASS: run U5 Llama native baseline.
4. Run U6 RTX4080-local kernel census; never reuse RTX3090 launch/static identities.
5. Run U7 bounded Llama NCU capture with frozen metrics and U6-bound targets.
6. Run U9 only when both U4 and the repaired U8.5 custom-tool gate are PASS.
7. STOP after U9; multi-model expansion is a separate stage.

## Root policy

The remaining U4-U9 work is expected to be userspace. Do not request root for Python, model import, CUDA builds, NCU, NVBit, or ordinary downloads/builds. If a genuinely unavoidable host mutation is identified, complete userspace diagnosis first, produce a minimal administrator handoff with rollback, and stop.
