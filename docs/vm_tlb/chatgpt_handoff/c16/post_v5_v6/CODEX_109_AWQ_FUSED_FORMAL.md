# Codex Goal — 109 fused Qwen2.5-7B-AWQ qualification + formal capture

## Execution base

Start from accepted 109 V5 producer state:

`ea43fa6331dcb2d7d6553f6a48000bdd004458e0`

Suggested branch:

`hrl/c16-qwen25-7b-awq-fused-109-v6`

Use a fresh 109 Codex window/worktree.

## Frozen authorities

Model:

- Qwen2.5-7B-Instruct AWQ canonical model asset;
- historical revision already frozen in C16 authority;
- use only the existing exact historical input binding for the selected scenario.

Primary scenario:

`S2_TEXT B1/T2048/D32`

Do not retokenize.

AutoAWQ kernels source is now available on node164 under the C16 canonical source-assets area. Verify the source-acquisition receipt and archive SHA before use. Do not re-fetch from the network unless the canonical source asset is demonstrably corrupt.

## Goal

Recover a real fused `awq_ext` deployment in an isolated environment, prove it is actually used by the exact AWQ model, then capture a small representative formal memory portfolio using the now-qualified direct + LDGSTS methodology as required by each exact target function.

## Guardrails

- Do not modify or contaminate the already-qualified Qwen0/Llama base environment.
- Build in an isolated env/wheelhouse/staging area.
- Do not silently fall back to unfused AutoAWQ and call it fused.
- Do not change quantization, dtype, batch, context, attention backend, or model revision merely to make the build/run work.
- Do not start Qwen7 raw layer replay, Qwen3, or DeepSeek in this Goal.
- Formal receiver admission concurrency is **1**. Transfer/admit accepted bundles serially.

## Stage A — source/build authority

1. Resolve canonical source asset from node164.
2. Verify source receipt/archive SHA and inventory.
3. Record source identity, build files, CUDA/C++ sources, version metadata, patches if any.
4. Build an SM89-compatible wheel/extension in an isolated environment.
5. Hash-close source, build command, compiler/CUDA versions, wheel, and build logs.

If a source or ABI incompatibility blocks the build, fail this sub-goal explicitly. Do not mutate the base environment.

## Stage B — microvalidation

Before the model workload:

- import the built extension;
- run deterministic small-operation/module-level checks appropriate to the extension;
- compare against the established unfused/reference AWQ semantics with justified tolerance;
- confirm no crash/illegal access and stable output.

Microvalidation alone is not deployment qualification.

## Stage C — exact AWQ deployment proof

Run the exact S2_TEXT AWQ workload with the historical frozen binding.

Use NSYS or equivalent launch evidence to prove that extension/fused AWQ kernel(s) from the newly built deployment actually execute.

Freeze a new deployment identity, e.g. a clearly named `qwen25_7b_awq_..._fused` label, containing:

- model revision;
- source/wheel SHA;
- Python/PyTorch/CUDA/Transformers/AutoAWQ versions;
- attention backend;
- fused kernel identity/code object;
- input binding SHA.

If fused kernels do not execute, classify the deployment as NOT_FUSED and do not promote formal AWQ evidence.

## Stage D — bounded target census and selection

Do not copy Qwen0 target names mechanically.

From the qualified fused deployment, identify representative S2 targets by:

- duration/memory relevance;
- quantized-weight relevance;
- semantic uniqueness;
- Prefill vs Decode shape difference.

Priority portfolio:

1. one Prefill fused quantized GEMM/linear target;
2. one Decode fused quantized GEMM/linear target if materially different in implementation/shape;
3. one Decode attention/KV target only if it is materially distinct and scientifically useful.

Avoid redundant targets.

## Stage E — full-function global-path audit

For every selected exact function/code object:

- inspect all memory-relevant SASS/NVBit rows;
- classify direct GLOBAL MREF, LDGSTS/global-to-shared, other special address-bearing paths, and memory-control instructions separately;
- do not count `LDGDEPBAR` as an address-bearing path;
- assign a coverage qualification.

Use V5 LDGSTS operand-1 GLOBAL-SOURCE qualification only when the exact AWQ function actually contains compatible LDGSTS instructions.

If another special global-address path appears, fail closed or qualify it before claiming complete global-address-path coverage.

## Stage F — formal capture

For each accepted target:

- complete frozen direct GLOBAL-MREF set where present;
- complete frozen LDGSTS GLOBAL-SOURCE set where present/required;
- same-process `C16_ADDRESS_CONTEXT_V1` for every replay;
- exact static-set SHA closure;
- EXECUTED_SHARD / ZERO_EXECUTION_PROVEN closure;
- overflow/drop zero;
- no cross-replay absolute-VA merge.

The best allowed final coverage label is:

`ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL`

when the exact full-function audit and all required address-bearing sets close.

This still does not establish whole-kernel temporal order or reuse distance.

## Stage G — transfer

For every accepted formal bundle:

- local-close first;
- transfer to node164;
- remote independent verification;
- **serial** admission only (`FORMAL_ADMISSION_CONCURRENCY=1`);
- Pipeline ACK;
- no GPU rerun for transfer/catalog recoverable failures.

## Review pack

Create:

`docs/vm_tlb/review_packs/C16_QWEN25_7B_AWQ_FUSED_109_V6/`

Include at minimum:

- source/build receipt;
- wheel/source hashes;
- microvalidation evidence;
- deployment identity;
- NSYS fused-kernel proof;
- target portfolio;
- full-function global-path audit;
- static-set indexes;
- per-shard artifact/address-context indexes;
- Pipeline ACK index;
- final decision;
- open issues;
- SHA256SUMS.

Expected successful final decision:

`C16_QWEN25_7B_AWQ_FUSED_V6_PASS_WITH_SCOPED_EVIDENCE`

If build or fused-runtime qualification fails, record the exact failure and STOP without promoting unfused control data.
