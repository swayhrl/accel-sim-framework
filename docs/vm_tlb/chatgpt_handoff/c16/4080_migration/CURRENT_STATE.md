# C16 RTX4080 Current State

## Scope and ownership

This is the ChatGPT-owned coordination state for the C16 RTX4080 platform lane only.

## Source anchors

- Latest reviewed Codex execution branch: `hrl/c16-4080-u4-u9-r1`
- Latest reviewed execution commit: `c14dae683e7b3be580f484f9a585dc5e061c47d0`
- Prior coordination handoff: `f1d088f21012b2d111c50ebd468418f17ee3b0ac`
- Userspace runtime U0-U3 closure: `c463c017372361d8422038f1d26d5ba2cbafde41`
- NCU N0/N1 closure: `ba9afb264746b3290607ae5e5e5d8642941bc11f`

## Frozen host/runtime facts

- Research user: `huangrulin`, UID/GID `1004:1004`, no sudo, not in docker group.
- GPU: RTX 4080, UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`, CC 8.9.
- Driver: `580.178.04`.
- Kernel: `7.0.0-31-generic`, already classified `PREEXISTING_KERNEL_BOOT_SELECTION`.
- Host CUDA symlink: `/usr/local/cuda -> /usr/local/cuda-12.8`.
- NCU: `/opt/nvidia/nsight-compute/2025.1.1/ncu`, version `2025.1.1.0`.
- Profiling permission: `RmProfilingAdminOnly: 0`.
- Data root: `/data/c16`.
- Exact Python runtime closure: CPython 3.10.12, 66-wheel offline environment, torch `2.5.1+cu124`, transformers `4.46.3`, AutoAWQ `0.2.7.post3`.
- `libtorch_cuda.so` SHA256 matches known-good: `761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a`.

## Completed gates

- Phase B1: PASS.
- NCU N0: PASS.
- NCU N1: `NCU_N1_HARDWARE_COUNTER_CANARY_PASS`.
- U0-U3: PASS.
- U8.1-U8.4: PASS.
- U8.6-U8.7: PASS.
- U8.5 custom no-match lifecycle: `U8_5_C16_CUSTOM_TOOL_CLOSURE_PASS` at `c14dae683e7b3be580f484f9a585dc5e061c47d0`.
  - Native and PyTorch bounded no-match prewarm emitted NVBit banner, READY and TERMINAL.
  - Zero trace files.
  - Normal exits.
  - No residual compute process.
- No evidence justifies driver downgrade or root handoff for NVBit.

## U4 exact Llama asset state

Required identity:

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

Operator-side transfer evidence previously showed six payload files at:

`/data/c16/models/.incoming/Llama-3.2-1B/4e20de362430cd3b72f300e6b0f18e50e7166e08`

with source-vs-destination payload SHA256 equality after rsync from:

`/root/share/c16_recovery_v3/models/llama_3p2_1b/4e20de362430cd3b72f300e6b0f18e50e7166e08`

However the Codex execution at `c14dae68` recorded that the exact incoming revision directory was empty at its observation time. This conflicts with the earlier operator-observed post-rsync state and must be reconciled by a fresh live filesystem check. Do not silently choose either observation as authority.

The source-side CPU-server audit also reported an authoritative `R1_LLAMA3P2_1B_ASSET_RECEIPT.json` (or equivalent receipt) binding exact model/revision and payload size/SHA identities, but that small receipt was not locally available to the RTX4080 execution.

U4 status remains `PENDING_LIVE_RECONCILIATION_AND_SOURCE_RECEIPT`.

## Importer semantics

The importer at `c14dae68` correctly requires explicit `--source-receipt` provenance and refuses directory-name-only promotion. Preserve this fail-closed behavior.

Evidence priority:

1. exact source receipt binding model/revision and payload hashes/sizes;
2. live destination byte inventory matching that source receipt;
3. then and only then promotion to a stable exact-revision model path.

Do not manufacture provenance from the directory name and do not redownload the model while the transferred exact asset can be recovered/verified.

## Immediate execution order

1. Fresh live check of the exact incoming revision directory and reconcile the `empty` vs `post-rsync payload-present` discrepancy.
2. Obtain/copy only the small authoritative source receipt from the CPU server if it is still absent locally.
3. Run importer against the exact revision directory plus source receipt; require `U4_LOCAL_ASSET_EXACT_CLOSURE_PASS` before promotion.
4. After U4 PASS, run U5 native Llama baseline.
5. Run U6 RTX4080-local kernel census; never reuse RTX3090 launch/static identities.
6. Run U7 bounded Llama NCU capture with frozen metrics and U6-bound targets.
7. Run U9 address-bearing NVBit canary only after U4/U5/U6 and the already-passed U8.5 lifecycle gate are bound into the new run receipt.
8. STOP after U9. Multi-model expansion is a separate stage.

## Root policy

Remaining work is expected to be userspace. Do not request root for model import, Python, CUDA builds, NCU, NVBit or ordinary user-owned data operations. If a genuinely unavoidable host mutation is identified, fully diagnose in userspace first, generate a minimal administrator handoff with impact/rollback, and stop.
