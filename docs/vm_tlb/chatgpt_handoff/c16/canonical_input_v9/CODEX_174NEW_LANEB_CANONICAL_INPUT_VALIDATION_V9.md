# C16 174-new Lane B — Canonical Input Validation V9

## Accepted base

Start from exact commit:

`ca683527323e26e3415a805c797c53c5edea322c`

V8 created `C16_PROSPECTIVE_COMMON_INPUT_V1`. Preserve it byte-for-byte. Do not overwrite or rewrite V1 payloads, sources, or historical authorities.

## Why this V9 exists

V8 source generation/provenance is deterministic and useful, but tokenization was performed by a repository-local hand-written BPE implementation that reads tokenizer vocab/merges directly. Before V1 is used as formal execution authority, independently validate exact equivalence against the canonical local tokenizer pipeline represented by each archived `tokenizer.json`.

The V8 sources are also synthetic controlled sources. Their primary semantics are token-budget/context control, not realistic/native workload representativeness.

## Primary Goal

Create an independently validated prospective-input authority state suitable for future Qwen3-8B / DeepSeek-V2-Lite / Llama / Qwen comparisons, while keeping historical and prospective axes separate.

CPU-only. No network. No GPU. No formal raw/catalog mutation.

## P0 — Canonical tokenizer revalidation

For all six archived models:

- Llama-3.2-1B
- Qwen2.5-0.5B-Instruct
- Qwen2.5-7B raw
- Qwen2.5-7B AWQ
- Qwen3-8B
- DeepSeek-V2-Lite

use the exact local archived tokenizer assets and an actual tokenizer runtime that executes the complete tokenizer pipeline, preferably `tokenizers.Tokenizer.from_file(tokenizer.json)` or another offline implementation proven equivalent to the archived tokenizer JSON.

Freeze runtime identity at minimum:

- Python
- `tokenizers` version
- tokenizer.json SHA256
- tokenizer_config.json SHA256
- `add_special_tokens=False`
- no chat template
- no network

For every V1 source class and every frozen scenario, recompute canonical token IDs and compare token-for-token with the existing V1 payload.

Do not merely compare lengths or hashes produced by the same hand-written V8 code.

### Decision

If all 42 V1 bindings are token-for-token identical to the canonical tokenizer output:

- keep V1 unchanged;
- issue an independent `V1_CANONICAL_TOKENIZER_VALIDATION.json` receipt;
- status may be `V1_CANONICAL_TOKENIZER_VALIDATED`.

If any binding differs:

- do NOT edit V1;
- create a new no-overwrite authority `C16_PROSPECTIVE_COMMON_INPUT_V2` using canonical tokenizer output;
- record V1 as `SUPERSEDED_FOR_FORMAL_EXECUTION` in the V9 review pack only;
- preserve V1 as historical prospective evidence.

## P1 — Fix input-axis semantics

Explicitly classify the current first-N-token construction as:

`TOKEN_BUDGET_MATCHED_SYNTHETIC_CONTROL`

For every canonical binding record enough source-span metadata to make clear that different tokenizers may consume different text spans for the same N-token budget. Prefer canonical tokenizer offset mappings where available and freeze at least:

- source SHA256
- N tokens
- source prefix end character/byte offset or equivalent exact source span identity
- source prefix SHA256 when deterministically derivable

Do not call this `SAME_SEMANTIC_TEXT_PREFIX` unless exact source-prefix identity is proven.

## P2 — Same-source-prefix diagnostic axis

Create a CPU-only diagnostic table for the same repository-controlled TEXT/CODE/STRUCTURED sources using fixed source-prefix boundaries (prefer deterministic line/byte boundaries).

For each model/tokenizer record token counts for identical source prefixes.

This is a second axis:

`SOURCE_PREFIX_MATCHED_TOKEN_COUNT_DIAGNOSTIC`

It is not automatically a formal GPU scenario. Its purpose is to quantify the unavoidable tradeoff:

- same token count -> source span may differ;
- same source prefix -> token count may differ.

## P3 — raw7B / AWQ compatibility

Because raw7B and AWQ archived tokenizer identities appear identical, independently prove canonical token equality for all seven prospective scenarios using the canonical tokenizer runtime.

Do not use V1 to alter the currently running node109 V8 task. Node109 V8 should continue its original input-authority gate and accepted historical/prospective pair logic.

## Scientific scope guardrails

The repository-controlled V1/V2 sources are synthetic deterministic controls. Do not describe them as representative natural-language/code/structured corpora.

For future MoE routing or semantic-behavior claims, preserve a distinction between:

- controlled synthetic cross-model axis;
- historical/native or separately qualified realistic workload axis.

No reverse decoding.
No external corpus.
No network.
No Qwen3-30B.
No modification of 21 historical Qwen2.5 bindings.
No modification of adopted Llama S0 authority.

## Required review pack

Write:

`docs/vm_tlb/review_packs/C16_CANONICAL_INPUT_VALIDATION_174NEW_LANEB_V9/`

Include at minimum:

- `FINAL_DECISION.json`
- `TOKENIZER_RUNTIME_IDENTITY.tsv`
- `V1_CANONICAL_REVALIDATION.tsv`
- `V1_CANONICAL_TOKENIZER_VALIDATION.json` if all pass
- V2 authority/index files if V1 fails canonical equivalence
- `TOKEN_BUDGET_SOURCE_SPAN.tsv`
- `SOURCE_PREFIX_TOKEN_COUNT_DIAGNOSTIC.tsv`
- `RAW7B_AWQ_CANONICAL_COMPATIBILITY.tsv`
- actual executable tests/results, not hard-coded PASS rows
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Commit, push, and STOP.