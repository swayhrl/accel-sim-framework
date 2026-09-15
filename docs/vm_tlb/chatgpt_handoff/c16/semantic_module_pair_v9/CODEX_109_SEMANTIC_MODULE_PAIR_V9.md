# C16 109 V9 — Matched Semantic Module Replay Pair

## Accepted bases

- raw7B paired replay authority: `e1d210d662ece6975648d04f628eb3f9e938117f`
- Lane A static semantic inventory authority: `ef8b5629fc8c10d770bed1c24f68c31cabe9912f`
- accepted AWQ formal authority remains `2274ee94c86cac9d37f7ef60c8afee58f8fc74b8`

Do not mutate any accepted raw/catalog evidence.

## Primary goal

Close the first *semantic-module matched* Qwen2.5-7B BF16-raw vs AWQ deployment pair for:

`model.layers.0.mlp.down_proj`

This is a deployment-level operator comparison, not a claim of pure quantization causality and not full-model cache/TLB history.

## Pair input

Use the already proven common historical S2 B1/T2048 sequence from V8. Re-hash before use. No retokenization.

## Raw side

Reuse/extend the exact V8 raw deployment. From the real first-decode execution:

1. capture the exact input tensor entering `model.layers.0.mlp.down_proj`;
2. capture the exact output produced by that module in-context;
3. replay that exact raw module on the captured input;
4. require deterministic output equivalence to the captured in-context output;
5. bind exact model revision, layer, role, input SHA, output SHA, tensor shape, dtype, weight SHA and runtime identity.

## AWQ side

Use the accepted V6/V7 AWQ deployment. Do not try to retrofit the old accepted `DECODE_FUSED_GEMM` bundle into a layer identity.

Instead, from the real first-decode execution:

1. hook the exact `model.layers.0.mlp.down_proj` WQLinear module;
2. capture its exact input and in-context output;
3. replay that exact in-memory WQLinear module on the captured input;
4. require deterministic output equivalence to the in-context module output;
5. use a dedicated semantic replay process/range so NSYS can bind the generated CUDA kernel(s) losslessly to this single module;
6. record exact qweight/qzeros/scales/bias/g_idx tensors actually present, their shapes/dtypes/bytes and checkpoint identities.

If module replay changes kernel implementation/signature relative to its in-context invocation, fail closed. Do not formalize a synthetic substitute.

## Formal capture

For BOTH raw and AWQ semantic module replays:

- full-function static SASS audit;
- direct GLOBAL MREF complete set;
- qualified LDGSTS GLOBAL_SOURCE if present;
- any other address-bearing special path;
- control-only instructions tracked separately;
- EXECUTED_SHARD / ZERO_EXECUTION_PROVEN closure;
- terminal complete, zero overflow/drop;
- same-process ADDRESS_CONTEXT;
- serial Pipeline admission (`FORMAL_ADMISSION_CONCURRENCY=1`);
- remote ACK required.

Allowed strongest label only after closure:

`ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL`

No cross-path fabricated stream, no cross-shard chronology, no reuse distance.

## Matched NCU

Capture matched semantic-module NCU for raw and AWQ using identical descriptor semantics. Prefer `cache-control none` and the same replay mode on both sides.

Important V8 cleanup folded into this goal:

- the existing AWQ V7 numeric exports omitted explicit unit metadata;
- re-export/parse the NCU CSV unit column;
- normalize values to integer bytes only when unit conversion is explicit and recorded;
- otherwise preserve `(value, unit)` and do not label scaled values as bytes.

Do not recapture old reports if the accepted `.ncu-rep` files are intact and export can be regenerated.

## Pair result

Only emit a positive pair qualification if ALL of these match/close:

- same historical token-sequence SHA;
- exact semantic layer `0`;
- exact role `mlp.down_proj`;
- compatible logical input/output shapes;
- raw replay equivalence PASS;
- AWQ replay equivalence PASS;
- raw kernel-signature equivalence PASS;
- AWQ kernel-signature equivalence PASS;
- both formal address-path closures PASS;
- NCU descriptor semantics compatible if NCU values are compared.

Use label:

`MATCHED_SEMANTIC_MODULE_REPLAY_DEPLOYMENT_COMPARISON`

Do NOT call this full-model quantization causality.

## Sidecar: unblock Lane B canonical-tokenizer validation

This sidecar is CPU-only and must not block the primary GPU pair task.

The V8 runtime already imports `transformers`. Probe the current accepted environment for:

- `tokenizers` package/version;
- exact package file path;
- pip cache wheel for that exact version, if any.

No network.

If `tokenizers` is importable:

1. obtain only the small hash-verified V1 assets needed for validation (three source files, six `tokenizer.json`, six `tokenizer_config.json`, V1 binding index/payloads) from node164 via the normal trusted transfer path;
2. use the real canonical pipeline, preferably `tokenizers.Tokenizer.from_file(...)` with no added special tokens;
3. independently recompute all 42 V1 sequences;
4. compare token-for-token to V1;
5. write a validation receipt and mismatch table.

If all 42 match, report `V1_CANONICAL_TOKENIZER_VALIDATED`.
If any differ, preserve V1 and report `V1_CANONICAL_TOKENIZER_MISMATCH`; do not create V2 here.

If `tokenizers` is not importable but an exact cached wheel exists, hash-close/copy the wheel to the durable source-assets area for Lane B. If neither runtime nor wheel exists, record `TOKENIZER_RUNTIME_BRIDGE_NOT_FOUND` and continue the main pair task.

## Output

Commit/push:

`docs/vm_tlb/review_packs/C16_QWEN25_7B_SEMANTIC_MODULE_PAIR_109_V9/`

Then STOP.
