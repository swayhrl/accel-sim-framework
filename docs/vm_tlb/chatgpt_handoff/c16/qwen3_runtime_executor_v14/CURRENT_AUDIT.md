# C16 Qwen3 V14 current audit

## Current producer state

- execution branch: `hrl/c16-qwen3-8b-unattended-campaign-109-v12`
- current producer HEAD: `900588bbb2aaa0106e4ca430002b5eaeb9408ea0`
- latest decision: `C16_QWEN3_8B_UNATTENDED_CAMPAIGN_109_V12_BLOCKED_ENVIRONMENT_RUNTIME_API`
- V13 input transport is resolved and S2 authority is materialized.
- full executor-integrity receipt claims PASS, but the implementation audit below shows this is not sufficient evidence for the real driver.

## Root cause 1 — Qwen3 runtime

The accepted producer environment uses `transformers==4.46.3`, which has no `transformers.models.qwen3` runtime API.

For this checkpoint, the accepted static config records `transformers_version: 4.51.0`. Upstream Qwen3 requires `transformers>=4.51.0`.

Producer engineering authorization for V14:

- exact top-level runtime target: `transformers==4.51.0`;
- required `tokenizers` range from the package metadata is `>=0.21,<0.22`; preferred exact bootstrap pin is `tokenizers==0.21.0`;
- preferred hub pin: `huggingface-hub==0.30.2`;
- retain the existing accepted `torch==2.5.1+cu124` unless an executable compatibility test proves it cannot run the official Qwen3 layer API. Do not upgrade torch merely because newer upstream docs recommend a later version;
- keep existing compatible packages such as `safetensors>=0.4.3`, numpy, packaging, pyyaml, regex, requests and tqdm if `pip check` and runtime import tests pass.

Known official wheel hashes to verify when those exact wheels are used:

- `transformers-4.51.0-py3-none-any.whl`: `2e6baa476735ab8adccbaee6961525a0d1ce8c21d49293af30ef5ee4b082f64d`
- `tokenizers-0.21.0-cp39-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl`: `e84ca973b3a96894d1707e189c14a774b701596d579ffc7e69debfc036a61a04`
- `huggingface_hub-0.30.2-py3-none-any.whl`: `68ff05969927058cfa41df4f2155d4bb48f5f54f719dd0390103eefa9b191e28`

Do not mutate the old accepted environment in place. Build a separate hash-closed Qwen3 runtime environment.

During scientific execution set offline/local-only behavior and use the already accepted local model assets. Do not download model files or remote code at runtime.

## Root cause 2 — the V11 driver is still a scaffold

At current producer HEAD, `util/vm_tlb/c16/campaign/driver.py` is still the V11 plan/resume scaffold and can emit `FRAMEWORK_ONLY` PASS receipts without executing scientific stages.

The V13 `v12_executor_selftest.py` is not a real integration test of that driver. It defines toy helper functions in the test file and verifies their Boolean outputs. It does not exercise the actual receipt chain, actual stage dispatch, actual admission lock, actual shard publication, or actual driver resume behavior.

Therefore V14 must not treat the previous `EXECUTOR_INTEGRITY_V13.json` as sufficient proof of a real unattended executor.

## Required correction

V14 must do all of the following in one Goal:

1. perform one comprehensive producer-readiness sweep instead of fail-fast checking one item at a time;
2. establish the isolated official Qwen3-compatible runtime;
3. replace/upgrade the real campaign driver so scientific PASS can only come from actual stage executors and validators;
4. test that real driver end-to-end in a sandbox before Qwen3 GPU work;
5. if the readiness sweep has no external blocker after authorized automatic remediation, continue immediately into the existing Qwen3 S2 scientific campaign;
6. do not stop merely because runtime/environment preparation completed.

## Comprehensive readiness sweep

Before starting Qwen3 scientific GPU work, inspect all independent producer prerequisites in one pass and write `PRODUCER_READINESS_MATRIX.tsv`. Do not stop the sweep at the first failed row. Rows must include at least:

- exact Qwen3 model revision and all local checkpoint shards/index/config;
- V13 S2 and conditional S3 payload readability and hashes;
- Python/runtime package compatibility;
- official Qwen3 class/config/layer imports;
- CUDA visible device, GPU identity and torch CUDA smoke;
- available GPU memory and selected execution mode;
- local free space for state captures, trace shards, profiler reports and temporary files;
- `nsys`, `ncu`, `cuobjdump`/`nvdisasm` availability;
- NVBit tool source/build/runtime compatibility and a bounded non-scientific instrumentation smoke;
- profiler permissions and a bounded non-scientific NCU smoke;
- Pipeline admission tooling/reachability and global serial-admission lock mechanism, without admitting a new scientific run during preflight;
- writable local staging and approved durable transport path;
- selective safetensors layer-loading ability for all 36 layers;
- exact Qwen3 semantic layer API required to propagate hidden/position/attention/KV state;
- deterministic receipt/state directories and process locks.

Automatically resolve only issues covered by this V14 engineering authorization. Continue the sweep after a row fails so all independent blockers are known at once.

If an external fact is still required after the full sweep, emit one consolidated blocker containing every unresolved row, not a sequence of one-line blockers.

## Runtime bootstrap policy

Search local caches/wheelhouses/environments first. If the exact compatible runtime is already present, record and use it.

If it is absent, V14 explicitly permits a narrowly scoped network bootstrap of Python runtime packages only, using pinned package/version constraints above. This is not permission to download or replace the model, tokenizer authority, input payload, precision, backend or target semantics.

Download wheels into a dedicated wheelhouse first; hash every wheel; verify the three known hashes above when those exact artifacts are used; record resolver output for all transitive packages. Then create a separate environment and install from that wheelhouse. After installation, run `pip check`, freeze package versions/hashes, and switch scientific execution to offline/local-only mode.

No arbitrary `latest` package. No source checkout from an unpinned branch. No in-place mutation of the Qwen2/AWQ accepted environments.

## Runtime acceptance tests

Before scientific GPU execution, the new environment must executable-test:

- import `Qwen3Config`, `Qwen3ForCausalLM`, the exact decoder-layer class and required cache/rotary helpers;
- load the local exact config with `local_files_only` semantics;
- instantiate a single Qwen3 decoder layer and required helper modules without loading the full model;
- load exact layer-0 checkpoint tensors from safetensors and verify names/shapes/dtypes against the official layer state dict;
- run a bounded engineering-only layer forward on CUDA to prove the runtime API/backend is executable;
- record actual attention implementation/backend selected;
- verify no model/network access occurred during the smoke.

Engineering smokes are readiness evidence only, not scientific trace evidence.

## Scientific execution mode

Lack of full BF16 residency is not a blocker. Default to the already authorized `EXACT_SEMANTIC_LAYER_STREAMING_REPLAY` unless a separate preflight proves and records full-resident feasibility.

For streamed execution, use official Qwen3 runtime modules and exact checkpoint weights. Propagate exact model state through all required layers. Synthetic hidden state, standalone replacement GEMM, different model class, quantization or backend substitution are forbidden.
