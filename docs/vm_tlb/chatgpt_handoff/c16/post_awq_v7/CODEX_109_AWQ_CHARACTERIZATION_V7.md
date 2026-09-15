# CODEX node109 Goal — C16 Qwen2.5-7B AWQ Characterization V7

Fresh branch/worktree from accepted V6 producer state:

`2274ee94c86cac9d37f7ef60c8afee58f8fc74b8`

Read first:

`docs/vm_tlb/chatgpt_handoff/c16/post_awq_v7/NODE109_AWQ_CHARACTERIZATION_SCOPE.md`

Suggested branch:

`hrl/c16-qwen25-7b-awq-characterization-109-v7`

Reuse the accepted isolated V6 AWQ environment and model deployment if intact. Do not modify qualified Qwen0/Llama environments.

## P0 — Re-verify deployment/source identity

Before new measurements, verify without unnecessary rebuild:

- model revision and local asset receipt;
- frozen input authority for each scenario used;
- accepted wheel SHA;
- installed extension SHAs;
- AutoAWQ source commit;
- source tree SHA (`HEAD^{tree}`) and clean worktree;
- Python / torch / torch CUDA / nvcc / host compiler / driver / GPU identity.

Fold the minor V6 source-manifest completeness improvements here. No separate repair round.

## P1 — Exact S2 application-context NCU

For the two accepted V6 target roles:

1. `PREFILL_AWQ_DEQUANT`
2. `DECODE_FUSED_GEMM`

run bounded Nsight Compute measurements using the exact S2_TEXT B1/T2048/D32 deployment and exact target kernel identity.

Requirements:

- query the actual RTX4080 metric availability first;
- choose a compact cache/memory metric set covering L1/TEX, L2, DRAM traffic/throughput and useful memory stalls where available;
- record unavailable metrics explicitly instead of substituting guessed names;
- preserve exact argv, kernel selector, launch selector, replay mode and cache-control behavior;
- prefer application-context `cache-control none` evidence;
- optionally add one cold/isolated control only if inexpensive and clearly labelled;
- save raw `.ncu-rep`, exported machine-readable summary and SHA256 receipts;
- validate application output/checksum around profiling.

Do not interpret NCU replay as exact full-model global L2/TLB history.

## P2 — Cheap AWQ scenario-axis census

Use only already frozen exact historical AWQ inputs; do not retokenize.

Run native/runtime receipt + bounded NSYS census for:

- S1_CODE B1/T256/D16
- S3_TEXT B1/T8192/D16
- S4_STRUCTURED B4/T2048/D16

S2 is the accepted reference.

For each scenario record at least:

- exact input binding/hash semantics;
- output checksum;
- peak allocated/reserved memory;
- prefill/decode latency summary;
- kernel names/signatures;
- instance counts;
- duration mass;
- grid/block where available;
- whether the accepted S2 dequant/GEMM implementation remains the same code path;
- attention/KV implementation identity.

If a scenario cannot execute because of capacity/runtime constraints, record the exact fail-closed result; do not change model precision/backend or silently offload.

## P3 — Material-difference decision

Classify each S1/S3/S4 candidate target as one of:

- `SAME_IMPLEMENTATION_SHAPE_SCALING_ONLY`
- `MATERIALLY_NEW_SHAPE_BUCKET`
- `MATERIALLY_NEW_IMPLEMENTATION`
- `MATERIALLY_NEW_ADDRESS_PATH`
- `NOT_USEFUL_FOR_FORMAL_EXTENSION`

Do not mechanically repeat V6 formal capture.

Highest-interest checks:

- whether S3 long-context attention/KV becomes materially distinct and useful given the previously observed Qwen0 S2/S3 LDGSTS scaling;
- whether S4 batch changes the AWQ GEMM implementation/shape bucket;
- whether S1 small prefill selects a different quantized kernel.

## P4 — At most one formal extension

Only if P3 identifies a scientifically useful materially distinct target, formalize at most one new target in V7.

Required flow:

- exact target census and SASS audit;
- full-function audit for direct GLOBAL MREF, LDGSTS/global-to-shared and other address-bearing special paths;
- memory-control instructions separated from address-bearing paths;
- complete static set;
- EXECUTED / ZERO_EXECUTION_PROVEN closure;
- same-process ADDRESS_CONTEXT;
- zero overflow/drop;
- serial Pipeline admission (`FORMAL_ADMISSION_CONCURRENCY = 1`);
- remote ACK.

Do not count LDGDEPBAR as address-bearing.

Best possible coverage remains:

`ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL`

If no material target exists, formal extension count should be zero and that is a successful result.

## P5 — Output for Lane A

Produce compact indexes that Lane A can consume without parsing raw NCU/NSYS itself:

- S2 target NCU summary with metric definitions/units;
- S1/S2/S3/S4 scenario kernel census comparison;
- target material-difference classification;
- any new formal target index/ACK if created;
- exact deployment/input/source receipts.

## Guardrails

- Do not start raw7B layer replay.
- Do not start Qwen3/DeepSeek.
- Do not mutate accepted V6 raw bundles.
- Keep the phase-mislabeled V6 bundle excluded.
- Do not combine separately replayed address shards into fabricated temporal streams.
- Do not infer quantization causality from Qwen0.5 vs Qwen7-AWQ.

## Review pack

Create:

`docs/vm_tlb/review_packs/C16_QWEN25_7B_AWQ_CHARACTERIZATION_109_V7/`

Include at least:

- `README.md`
- `FINAL_DECISION.json`
- `SOURCE_BUILD_RUNTIME_RECEIPT_V7.json`
- `S2_NCU_TARGET_INDEX.tsv`
- `S2_NCU_METRICS.tsv`
- `SCENARIO_RUNTIME_INDEX.tsv`
- `SCENARIO_NSYS_CENSUS.tsv`
- `MATERIAL_DIFFERENCE_DECISION.tsv`
- optional formal-extension index/ACK evidence
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Expected success label:

`C16_QWEN25_7B_AWQ_CHARACTERIZATION_109_V7_PASS`

A valid zero-new-formal-target outcome is still PASS if NCU and scenario census close correctly.

Commit/push and STOP.
