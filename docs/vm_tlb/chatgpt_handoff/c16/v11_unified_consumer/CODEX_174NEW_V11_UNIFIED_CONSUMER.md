# C16 V11 — 174-new Unified Consumer

## Goal
One consolidated CPU-only consumer pass that merges the prior Lane A + Lane B follow-up work after V10 pair closure.

Do NOT split into repair sub-rounds. Small defects found while executing must be folded into this goal unless they invalidate a scientific claim.

## Authoritative inputs

- V10 producer/pair closure: `57ca798c851a3b9d4a2c787c01f4e2b3a16fcdea`
- Lane A V9 static semantic metadata: `ef8b5629fc8c10d770bed1c24f68c31cabe9912f`
- Lane B V8 prospective common input authority: `ca683527323e26e3415a805c797c53c5edea322c`
- Durable tokenizers wheel on node164:
  `/root/share/mnt164/huangrulin/c16_ai_workload/assets/wheels/tokenizers/0.20.3/tokenizers-0.20.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl`
  expected SHA256: `1fd9fee817f655a8f50049f685e224828abfadd436b8ff67979fc1d054b435f1`

CPU-only. Do not modify formal raw artifacts or accepted catalog entries.

## P0 — Independently audit the V10 formal pair

For both V10 runs:

- AWQ run:
  `C16R_qwen25-7b-awq_s2-text_decode_nvbit-warp-mref-shard_v10-semantic-downproj_20260916T001000Z_aa10aa10aa10`
- RAW run:
  `C16R_qwen25-7b-raw_s2-text_decode_nvbit-warp-mref-shard_v10-semantic-downproj-r2_20260916T005000Z_cc10cc10cc10`

Independently re-check from catalog/raw artifacts on node164:

- catalog entry exists and points to the accepted physical raw path;
- every retained artifact SHA matches;
- no symlink substitution;
- terminal/complete state;
- overflow/drop = 0;
- same-process address context is valid;
- static-set identity closes;
- every static global-address-bearing instruction is either EXECUTED or ZERO_EXECUTION_PROVEN;
- fresh V10 counts are independently reproduced:
  - AWQ: 43 direct GLOBAL MREF, 0 LDGSTS;
  - RAW: 243 direct GLOBAL MREF, 0 LDGSTS;
- no hidden special global-address path was omitted;
- Pipeline ACK exists for both;
- admission was serial (`FORMAL_ADMISSION_CONCURRENCY=1`).

Do not trust the producer summary alone.

## P1 — Build paired formal memory fingerprints

For each side, derive bounded per-shard/per-static evidence and a compact side-level summary.

At minimum include:

- static index / PC / SASS / access kind;
- EXECUTED vs ZERO_EXECUTION_PROVEN;
- active-lane events;
- read vs write composition;
- unique start VA count;
- unique 4K / 64K / 2M pages;
- unique 128B lines;
- exact touched page/line counts only where access width is actually derivable;
- same-process object attribution only where lossless event-to-range binding exists;
- object-relative offset only where semantic object identity is lossless.

Attempt, but do not force, attribution to:

- RAW `model.layers.0.mlp.down_proj.weight`;
- AWQ `qweight`, `qzeros`, `scales`, and bias if present;
- input/output runtime buffers.

Use `UNKNOWN_RUNTIME` wherever the join is not proven.

Cross-deployment absolute VA comparison is forbidden.
Cross-shard chronology, merged VA stream and reuse-distance claims are forbidden.

## P2 — Pair-level scientific comparison

Join the V10 formal evidence with the exact Lane A V9 checkpoint metadata for `layer0.mlp.down_proj`.

Produce a machine-readable comparison and a concise scientific memo covering only what is proven.

Required dimensions:

1. checkpoint static storage:
   - RAW BF16 weight bytes;
   - AWQ qweight/qzeros/scales/bias bytes;
   - ratio clearly labeled `CHECKPOINT_STATIC_STORAGE_ONLY`;
2. CUDA implementation identity:
   - RAW BF16 gemvx signature;
   - AWQ 4-bit GEMM signature;
3. static global-address-bearing instruction complexity (43 vs 243, after independent re-audit);
4. dynamic active-lane event counts;
5. replay-local page/line footprints;
6. object-attributed event/page/line composition where losslessly proven;
7. formal scope statement:
   `MATCHED_SEMANTIC_MODULE_REPLAY_DEPLOYMENT_COMPARISON`.

Explicitly preserve these limits:

- same model family / same historical token sequence / same decode token / same semantic module / same logical shape;
- RAW and AWQ module input VALUES naturally diverge across deployments;
- therefore this is not a single-variable quantization causal experiment;
- it is not a full-model comparison;
- it is layer0, first-decode, `mlp.down_proj` only.

## P3 — NCU evidence handling

Audit the V10 NCU index and search node164 durable namespaces for transferred V10 reports/exports.

If durable report/export bytes are available:

- rehash them;
- parse explicit metric values and units;
- normalize to base bytes only when the source unit is explicit;
- compare RAW vs AWQ L1/TEX, L2 and DRAM traffic under matching `cache-control none` + application replay.

If the actual V10 report/export bytes are still only on node109:

- do NOT invent numeric values;
- emit exactly `NCU_NUMERIC_ANALYSIS_PENDING_DURABLE_EXPORT`;
- retain the report SHA + descriptor as accepted provenance;
- generate a compact machine-readable durable-export request for the next node109 campaign instead of opening a separate repair round.

## P4 — Implement a real independent pair comparator

The previous Lane A V9 only defined a contract. V10 has a producer-side gate. Build an independent consumer comparator that reads real evidence files / receipts rather than hard-coding PASS booleans.

It must fail closed on at least:

- missing/mismatched token sequence;
- decode token mismatch;
- layer / role / logical-shape mismatch;
- replay-equivalence failure;
- in-context vs replay signature failure;
- static-set / execution closure failure;
- missing Pipeline ACK;
- incompatible NCU descriptor if NCU comparison is requested;
- unverified producer artifact hashes.

Create real positive and negative fixtures and execute them.

## P5 — Canonically validate `C16_PROSPECTIVE_COMMON_INPUT_V1`

Use an isolated local environment and the exact durable `tokenizers==0.20.3` wheel above. No network.

Use the actual complete tokenizer pipeline (`tokenizers.Tokenizer.from_file(tokenizer.json)` or an equivalently exact local canonical runtime), not the custom V8 BPE reimplementation.

For all 6 models × 7 scenarios = 42 bindings:

- reproduce canonical token IDs from the repository-controlled TEXT/CODE/STRUCTURED sources;
- `add_special_tokens=False`;
- compare token-for-token with V1, not just length;
- verify source/tokenizer hashes and exact model revisions.

If all 42 match:

- preserve V1 byte-for-byte;
- emit `V1_CANONICAL_TOKENIZER_VALIDATED`.

If any differ:

- preserve V1 unchanged;
- create a no-overwrite `C16_PROSPECTIVE_COMMON_INPUT_V2` using canonical output;
- explicitly supersede V1 only on the prospective axis;
- do not rewrite historical bindings.

Also emit:

- `TOKEN_BUDGET_MATCHED_SYNTHETIC_CONTROL` classification;
- source-byte/character span consumed for each N-token binding;
- `SOURCE_PREFIX_MATCHED_TOKEN_COUNT_DIAGNOSTIC` showing token counts each tokenizer produces from identical source prefixes.

Do not claim the synthetic TEXT/CODE/STRUCTURED sources represent natural workload distributions or MoE routing distributions.

## P6 — Final integrated decision and next-model gate

Produce one integrated status answering:

1. Is the V10 pair independently validated by 174-new?
2. What RAW-vs-AWQ memory differences are actually proven?
3. What remains descriptive / unresolved?
4. Is prospective common input V1 canonically valid, or was V2 required?
5. Is C16 ready to move the GPU producer to Qwen3-8B?

If ready, generate a compact machine-readable Qwen3-8B next-campaign contract based on the already audited exact revision:
`b968826d9c46dd6066d109eabc6255188de91218`.

Do NOT run GPU/model execution in this task.
Do NOT touch Qwen3-30B.

## Output

Review pack:

`docs/vm_tlb/review_packs/C16_UNIFIED_CONSUMER_174NEW_V11/`

Expected final decision should be one of:

- `C16_UNIFIED_CONSUMER_174NEW_V11_PASS`
- `C16_UNIFIED_CONSUMER_174NEW_V11_PASS_WITH_SCOPED_GAPS`
- fail-closed only if a producer claim does not survive independent verification.

Commit and push a dedicated execution branch, then STOP.