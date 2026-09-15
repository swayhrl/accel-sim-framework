# CODEX 174-new Lane A Goal — C16 AWQ Consumer Analysis V7

Fresh branch/worktree on node174-new.

Base from accepted Lane A state:

`cff4b238c5c98c09b5eda96f3e1df4e1d78b57d3`

Producer authority to consume:

`2274ee94c86cac9d37f7ef60c8afee58f8fc74b8`

Read first:

`docs/vm_tlb/chatgpt_handoff/c16/post_awq_v7/LANEA_CURRENT_SCOPE.md`

Suggested branch:

`hrl/c16-awq-consumer-174new-laneA-v7`

CPU-only. Do not run GPU/CUDA inference. Do not mutate node164 raw/catalog data.

## P0 — Independent formal-bundle closure

Independently ingest both ACKed V6 AWQ formal bundles from node164/catalog and re-verify:

- catalog identity and run id;
- complete expected artifact set;
- no symlink substitution;
- independent SHA256 of every required artifact;
- terminal completeness;
- overflow/drop = 0;
- static-set closure;
- EXECUTED / ZERO_EXECUTION_PROVEN closure;
- same-process ADDRESS_CONTEXT binding;
- exact SASS path audit proving direct GLOBAL only and no LDGSTS/other address-bearing special path;
- remote Pipeline ACK.

Verify that the excluded phase-mislabeled bundle is excluded from every V7 scientific table and aggregate.

## P1 — Frozen-input hash semantics audit

For AWQ `S2_TEXT B1/T2048/D32`, trace the relationship among:

- historical authority receipt / `token_payload_sha256`;
- V6 runtime `token_file_sha256`;
- V6 runtime `token_canonical_sha256`;
- actual executed 2048 integer token IDs.

Produce `AWQ_S2_INPUT_BINDING_AUDIT.json` describing exactly what each hash covers.

PASS only if the executed token sequence is provably the intended frozen authority. Do not retokenize.

## P2 — Formal AWQ memory fingerprint

For each accepted target, produce per-static/per-shard analysis including at least:

- static index / PC / opcode / access kind;
- executed or zero-proven state;
- active-lane address events;
- exact accessed bytes where derivable from qualified event width/mask semantics;
- unique 4K pages within that shard;
- unique 64K pages within that shard;
- unique 128B lines within that shard;
- same-process object attribution;
- object-relative offsets when the semantic object identity is lossless and independently proven.

Object classes should preserve at least:

- `WEIGHT`
- `QUANT_METADATA`
- `UNKNOWN_RUNTIME`

Do not force unknown runtime storage into guessed activation/output classes.

Do not construct a cross-shard absolute-VA union or temporal stream.

## P3 — Target-level interpretation

Answer separately:

### Prefill AWQ dequant

- which qualified semantic objects are read/written;
- whether quant metadata accesses are directly observed;
- which static accesses dominate dynamic address events;
- whether the target behaves primarily as quantized-weight/metadata read plus runtime-output traffic.

### Decode fused GEMM

- 27 executed vs 16 zero-proven static instructions;
- weight / quant-metadata / runtime composition;
- dominant per-static page/line/event behavior;
- whether this target provides a stable AWQ decode memory fingerprint suitable as the AWQ side of a future raw7B-vs-AWQ pair.

## P4 — Descriptive context only

Optionally build a compact cross-deployment table against accepted Qwen0.5 S2 evidence, but label it explicitly:

`DESCRIPTIVE_ONLY_SCALE_AND_QUANTIZATION_CONFOUNDED`

Useful dimensions may include:

- detected global path type;
- static-set size;
- executed fraction;
- presence/absence of LDGSTS;
- object-class mix;
- per-static page/line/event summaries.

Do not call this a quantization comparison.

## P5 — Future raw7B pair contract

Create a small machine-readable handoff specifying what the future Qwen2.5-7B raw exact-layer/runtime replay must match before a controlled raw-vs-AWQ comparison is allowed:

- model family/revision relationship;
- exact semantic layer/operator role;
- scenario/input source semantics;
- runtime/backend identity or documented difference;
- target shape;
- object-role mapping;
- page/line metric definitions;
- claim boundary for replay-local VA.

## Tests/regressions

If shared parser/fingerprint code is changed:

- rerun LDGSTS CPU unit tests;
- rerun exact RTX3090 Q2 Prefill/Decode CPU fixture regressions;
- retain raw immutability.

## Review pack

Create:

`docs/vm_tlb/review_packs/C16_AWQ_ANALYSIS_174NEW_LANEA_V7/`

Include at least:

- `README.md`
- `FINAL_DECISION.json`
- `RUN_VERIFICATION.tsv`
- `AWQ_S2_INPUT_BINDING_AUDIT.json`
- `AWQ_FORMAL_MEMORY_FINGERPRINT.tsv`
- `AWQ_OBJECT_ATTRIBUTION.tsv`
- `PREFILL_DEQUANT_FINDINGS.md`
- `DECODE_FUSED_GEMM_FINDINGS.md`
- `RAW7B_AWQ_FUTURE_PAIR_CONTRACT.json`
- optional descriptive cross-deployment table
- regression results
- `SHA256SUMS`

Expected success label:

`C16_AWQ_ANALYSIS_174NEW_LANEA_V7_PASS`

If the frozen-input relationship cannot be proven exactly, use a scoped/fail-closed decision and do not promote the AWQ fingerprint as pair-ready.

Commit/push and STOP.
