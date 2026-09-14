# C16 RTX4080 Current State

## Scope and ownership

This is the ChatGPT-owned coordination state for the C16 RTX4080 platform lane only.

## Reviewed source anchors

- Latest reviewed Codex execution branch: `hrl/c16-4080-u4-u9-r3`
- Latest reviewed execution commit: `920ab69ca4e59c60fd091e58b8d672f0923283d2`
- Prior R2 execution: `57b42ebbf54e0750aed96aea06ab42e6c63507ae`
- Reviewed U8.5 repair: `c14dae683e7b3be580f484f9a585dc5e061c47d0`
- Userspace runtime U0-U3 closure: `c463c017372361d8422038f1d26d5ba2cbafde41`
- NCU N0/N1 closure: `ba9afb264746b3290607ae5e5e5d8642941bc11f`

## Frozen host/runtime facts

- Research user: `huangrulin`, UID/GID `1004:1004`, no sudo, not in docker group.
- GPU: RTX 4080, UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`, CC 8.9.
- Driver: `580.178.04`.
- Kernel: `7.0.0-31-generic`, classified `PREEXISTING_KERNEL_BOOT_SELECTION`.
- Host CUDA symlink: `/usr/local/cuda -> /usr/local/cuda-12.8`.
- NCU: `/opt/nvidia/nsight-compute/2025.1.1/ncu`, version `2025.1.1.0`.
- Profiling permission: `RmProfilingAdminOnly: 0`.
- Exact userspace runtime: CPython 3.10.12, 66-wheel offline closure, torch `2.5.1+cu124`, transformers `4.46.3`, AutoAWQ `0.2.7.post3`.
- `libtorch_cuda.so` SHA256 matches known-good `761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a`.

## Completed gates

- Phase B1: PASS.
- NCU N0/N1: PASS.
- U0-U3: PASS.
- U8.1-U8.7: PASS after U8.5 custom-tool repair at `c14dae68`; READY/TERMINAL, zero-trace no-match prewarm, normal exit and cleanup are closed.
- No current evidence justifies driver downgrade or root handoff.

## U4 exact model closure

Required model:

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

U4 is now:

`U4_LOCAL_ASSET_EXACT_CLOSURE_PASS`

Formal model path:

`/data/c16/models/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

Importer receipt:

`/data/c16/results/C16_U4_IMPORT_RETRY_20260914T123950Z.json`

Receipt SHA256:

`5b1aed870cd03d50a0da5f6721ab639d56ca0f3a1c3782a9fed9cf8e3dc84a3b`

Source receipt SHA256 remains:

`7694c95442cc7ff1d3fc8ed1104d5c0d6a50c3a17f779f402ef90669edeb7b47`

## U5 frozen-input blocker

U5 did not run. This fail-closed stop is correct.

The required Recovery-V2-S5 semantic contract is:

`S0 / B1 / T128 / Decode4 / TEXT`

The model is available, but the exact frozen input/token binding package and derived token IDs are not present on the RTX4080 host. Historical evidence records SHA identities but not enough payload content to safely reconstruct the input. Re-tokenizing a prompt, selecting a semantically similar prompt, or regenerating token IDs is forbidden.

The reviewed R3 report names four required historical SHA256 identities:

- `bae0b908106146659663fa04f44bc03ec0da18cadb08c9ec357c140afc4d8208`
- `0b5a86fdee44452e74e5d80e8043ebd97054fbbe29a6232a4f5cf5d06568c7dd`
- `f9cf1ea6dca7956c740b3aa0af59acadd17be014df2aaffb75d240383502e3a7`
- `fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624`

The next external task is to locate the exact small input/token binding package on the CPU/source server, verify these identities, and copy it to the RTX4080 host without modifying the model or runtime.

## Asset-migration state

The CPU/source server authority root is:

`/root/share/c16_recovery_v3`

The following have already been copied to RTX4080:

- full `receipts/` tree -> `/data/c16/models/.provenance/c16_recovery_v3/receipts/`
- `inputs/` tree -> `/data/c16/inputs/c16_recovery_v3/`

The prepared bulk-model transfer script on the CPU server has only passed `bash -n`; bulk model transfer has not yet been started. It excludes Llama and is intended for Qwen2.5-0.5B, Qwen2.5-7B raw, Qwen2.5-7B AWQ, Qwen3-8B and DeepSeek-V2-Lite.

Because the GPU experiment is currently stopped at U5, the bulk transfer may run now. It should finish or be paused before timing-sensitive U5/U7/U9 measurements resume, to avoid unnecessary storage-I/O interference.

## Immediate execution order

1. On the CPU/source server, locate the exact S0/B1/T128/Decode4/TEXT frozen input/token binding by historical receipt names and/or the four required SHA256 values. Do not regenerate it.
2. Copy that small binding package to a dedicated RTX4080 provenance/input path and verify source/destination SHA equality.
3. In parallel, optionally run the already-prepared bulk model sync while no GPU profiling/model measurement is active.
4. Resume Codex from U5 only after the exact input/token binding is locally verifiable.
5. Run U5 native baseline -> U6 RTX4080 kernel census -> U7 bounded NCU -> U9 address-bearing NVBit canary.
6. STOP after U9; multi-model formal expansion remains a separate stage.

## Root policy

Remaining work is expected to be userspace. Root is not needed for locating/transferring inputs, model assets, Python/CUDA/NCU/NVBit work or ordinary user-owned data operations. If a genuinely unavoidable host mutation appears, diagnose fully in userspace, produce a minimal administrator handoff with impact/rollback, and stop.
