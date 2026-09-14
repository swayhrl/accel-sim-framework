# C16 RTX4080 Current State

## Scope and ownership

This is the ChatGPT-owned coordination state for the C16 RTX4080 platform lane.

## Reviewed source anchors

- Latest Codex execution branch: `hrl/c16-4080-u5-u9-r4`
- Latest execution commit: `d6702b62717a7f6621dd4e3ca73747075113f0b0`
- U4 exact model closure: `920ab69ca4e59c60fd091e58b8d672f0923283d2`
- Reviewed U8.5 lifecycle closure: `c14dae683e7b3be580f484f9a585dc5e061c47d0`
- Userspace runtime U0-U3 closure: `c463c017372361d8422038f1d26d5ba2cbafde41`
- NCU N0/N1 closure: `ba9afb264746b3290607ae5e5e5d8642941bc11f`

## Frozen platform/runtime facts

- Research user: `huangrulin`, UID/GID `1004:1004`, no sudo, not in docker group.
- GPU: RTX 4080, UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`, CC 8.9.
- Driver: `580.178.04`.
- Kernel: `7.0.0-31-generic`.
- Host CUDA: `/usr/local/cuda -> /usr/local/cuda-12.8`.
- NCU: `/opt/nvidia/nsight-compute/2025.1.1/ncu`, version `2025.1.1.0`.
- Profiling permission: `RmProfilingAdminOnly: 0`.
- Userspace runtime: CPython 3.10.12, torch `2.5.1+cu124`, transformers `4.46.3`, AutoAWQ `0.2.7.post3`.
- `libtorch_cuda.so` SHA256: `761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a`.

## Immutable scientific identities already closed

### U4 model

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

Formal path:

`/data/c16/models/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

U4 receipt SHA256:

`5b1aed870cd03d50a0da5f6721ab639d56ca0f3a1c3782a9fed9cf8e3dc84a3b`

### Frozen Llama input

Semantic contract:

`S0 / B1 / T128 / Decode4 / TEXT`

Local package:

`/data/c16/inputs/.incoming/llama_3p2_1b/S0_B1_T128_Decode4_TEXT/`

Transfer receipt SHA256:

`5eff72842b2e87c79d2070b9085215e5bfca0e98c25e91155aec04aa12d6fe0d`

The four historical identities are closed, including the canonical compact-JSON SHA256 over the 128 authoritative token IDs. No tokenizer reconstruction is permitted.

## R4 review classification

R4 successfully demonstrated the end-to-end mechanism:

- frozen-input admission works and binds the historical payload without tokenizer use;
- U5 can execute the exact model/input contract with CUDA-only float16/sdpa and reproduce the historical output checksum;
- U6 can build an RTX4080-local live function/address census;
- U7 can profile the intended RTX4080 function with NCU 2025.1.1 and reopen/export the report;
- U9 can instrument the RTX4080-local `indexSelectLargeIndex` static target, observe a target launch, collect nonzero addresses, preserve the model checksum and terminate cleanly.

However R4 ran while large model assets were being copied into `/data/c16` on the same host. Therefore R4 is **not accepted as authoritative scientific measurement data**. Treat it as:

`MECHANISM_QUALIFICATION_PASS / SCIENTIFIC_MEASUREMENT_NOT_ACCEPTED`

The following R4 facts remain useful as structural evidence:

- input/model identity checks and output checksum;
- CUDA residency/backend checks;
- successful NCU/NVBit lifecycle and target reachability;
- target semantic identity `indexSelectLargeIndex`, static index `101`, opcode `LDG.E.U16` as the already-selected canary target.

Do not use R4 native timing, NCU metric values, trace counts/frequencies or other quantitative measurements as final evidence. Do not reuse R4 absolute live addresses/launch IDs.

## R4 process issues to fix before the clean rerun

1. `c16_llama_u5_native.py` uses Python `assert` for scientific gates. `assert` can be disabled with `python -O`; fail-closed checks must use explicit conditions/errors.
2. U5 copies each generated token to CPU inside the timed region. That introduces synchronization/D2H overhead. Keep generated-token collection on GPU and copy only after the synchronized timing endpoint.
3. U5 must bind the formal U4 receipt/model path explicitly, rather than merely reporting hard-coded expected model/revision strings.
4. R4's committed review pack is too sparse for U7/U9 provenance. The clean rerun must commit hashes/identities for the NCU metric manifest, exact argv, target contract, raw report SHA256, export SHA256, and U9 target/trace receipt. Raw reports/traces themselves remain outside Git.
5. R4 `READY_FOR_NEXT_STAGE` is superseded by this review. A clean isolated rerun is required before Llama qualification is considered scientifically complete.

## Clean-rerun isolation gate

Do not begin the formal clean rerun until bulk model migration to `/data/c16` has finished or is explicitly stopped.

Before measurement, record a preflight receipt proving at least:

- no active `rsync`/bulk-copy/download process targeting `/data/c16`;
- no `.partial`/transfer file is changing under the model transfer tree;
- no unrelated compute process is using the RTX4080;
- exact GPU UUID/driver/runtime still match authority;
- no NCU/NVBit process is left from an earlier run.

Do not change clocks, power limits, driver, kernel or host policy. No root is required.

## Clean rerun target policy

The canary target was already selected in R4. The clean rerun must not search for a more favorable target.

Freeze before R5 execution:

- function semantic identity: `indexSelectLargeIndex` (exact mangled identity must be recorded from the live R5 code object);
- expected static instruction index: `101`;
- expected opcode: `LDG.E.U16`.

Regenerate R5-local absolute address/launch mappings and verify the frozen semantic/static target. If static index 101 no longer maps to the expected instruction under the same frozen runtime/code object, fail closed rather than reselecting another instruction.

## Multi-model asset/input readiness

The CPU-source lane has recovered and transferred 21 exact historical Qwen bindings to 109:

- Qwen2.5-0.5B-Instruct: 7 exact bindings;
- Qwen2.5-7B-Instruct raw: 7 exact bindings;
- Qwen2.5-7B-Instruct-AWQ: 7 exact bindings.

Each model has S0_TEXT, S1_CODE, S2_CODE, S2_STRUCTURED, S2_TEXT, S3_TEXT and S4_STRUCTURED historical bindings with model-specific authoritative token IDs. These must not be replaced by Llama token IDs.

Qwen3-8B and DeepSeek-V2-Lite currently classify as `NO_HISTORICAL_FROZEN_BINDING`; no substitute input has been manufactured. A future unified multi-model input contract will be required for those two models.

Bulk model asset transfer is still in progress. Do not enter formal multi-model characterization until transfer/admission is complete and the Llama clean rerun is closed.

## Immediate execution order

1. Finish the ongoing bulk model asset transfer.
2. Verify source/destination model transfer closure and stop all bulk writers on 109.
3. Execute the clean isolated Llama rerun described in `CODEX_NEXT_STAGE.md`.
4. Review R5 evidence before authorizing formal multi-model characterization.

## Root policy

Remaining work is userspace. If a genuine host mutation becomes unavoidable, diagnose it fully first, prepare a minimal administrator handoff with impact/rollback, and STOP.