# C16 AI workload handoff — V2A frozen-input recovery

## Scope

Run this phase on the source/old Docker only. Its purpose is to recover the exact historical Llama S0/B1/T128/Decode4/TEXT frozen-input bundle that blocked V1 destination acceptance, then preserve that small immutable bundle in Git if and only if all historical hashes close exactly.

This phase does not run GPU workloads and does not modify RTX3090 or RTX4080 scientific authority.

## Authorities

Destination V1 result:

- branch `hrl/c16-ai-workload-2239-destination-acceptance-v1`
- commit `43212af0de0eef1cd72d905e11bfdeb2fe0e6d37`
- decision `DESTINATION_BLOCKED_MODEL_OR_INPUT_IDENTITY`

RTX4080 R5 authority remains:

- branch `hrl/c16-4080-u5-u9-r5-clean`
- commit `b75f26674a09705659e770ab2134351414aa3c93`
- status `READY_FOR_MULTIMODEL_REVIEW`

RTX3090 authority remains separate:

- branch `hrl/vm-c16-g-3090-campaign-closeout-v0`
- commit `649af1b9d65a774d4aa8c32a15f9b6f4da0dd4d9`

## Exact frozen-input contract

Required files:

1. `TEXT.txt`
2. `TEXT_T128.json`
3. `LLAMA_S0_TEXT_TOKEN_IDS.json`
4. `LLAMA_S0_TEXT_BINDING_RECEIPT.json`
5. `C16_FIND_AND_TRANSFER_LLAMA_S5_FROZEN_INPUT_BINDING_RECEIPT.json`

Required four-hash contract:

- raw text SHA256: `bae0b908106146659663fa04f44bc03ec0da18cadb08c9ec357c140afc4d8208`
- token receipt file SHA256: `0b5a86fdee44452e74e5d80e8043ebd97054fbbe29a6232a4f5cf5d06568c7dd`
- canonical target token IDs SHA256: `f9cf1ea6dca7956c740b3aa0af59acadd17be014df2aaffb75d240383502e3a7`
- derived token IDs file SHA256: `fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624`

Semantic identity must be exactly:

- scenario `S0`
- batch size `1`
- prefill tokens `128`
- decode tokens `4`
- input class `TEXT`
- model `meta-llama/Llama-3.2-1B`
- revision `4e20de362430cd3b72f300e6b0f18e50e7166e08`

Validator authority:

`util/vm_tlb/c16/host_4080/c16_frozen_input_admission.py`

Do not invoke a tokenizer and do not regenerate any token IDs.

## Search policy

Perform a bounded, read-only search of source-visible C16 data roots, historical transfer/staging roots, old 4080 work directories, receipts, and Git-referenced paths. Search by both exact filenames and expected SHA256 values. Do not search unrelated user/private directories broadly and do not collect secrets.

If exact files are found, verify the five files together as one coherent bundle using the validator and direct SHA256 checks. A raw-text-only match is insufficient.

If multiple copies exist, prefer the copy with the strongest path/receipt provenance, but record every exact duplicate path found.

## Git publication policy

Only if the exact historical bundle passes all checks, copy-not-move the five small files byte-for-byte into:

`docs/vm_tlb/codex_handoff/c16/ai_workload_2239/FROZEN_INPUTS/LLAMA32_1B_S0_T128_D4_TEXT_V1/`

Also add:

- `SHA256SUMS`
- `PROVENANCE.md`

Requirements:

- preserve exact bytes;
- re-hash after copying into the repository;
- do not edit or normalize JSON/text content;
- do not regenerate token IDs;
- do not replace historical files with newly generated equivalents.

If exact historical files are not recoverable, do not synthesize them. Record `HISTORICAL_FROZEN_INPUT_NOT_RECOVERED` and stop. A future destination baseline may create a new input authority, but it must not masquerade as historical R5 input identity.

## Secondary bounded locator audit

Without copying large data, inspect existing receipts/manifests for locators of:

- R5 U5/U6/U9 raw/static-map/stdout;
- N1 `.ncu-rep` and CSV;
- U8 NVBit raw root / `FINAL_SHA256SUMS`.

This is locator/provenance work only. Do not run workloads and do not bulk-copy data.

## Required results

Create:

`docs/vm_tlb/codex_handoff/c16/ai_workload_2239/V2A_FROZEN_INPUT_RECOVERY/RESULTS/`

with at least:

- `FROZEN_INPUT_SEARCH.md`
- `FROZEN_INPUT_RECOVERY_RECEIPT.json`
- `R5_ARTIFACT_LOCATOR_AUDIT.tsv`
- `OPEN_ISSUES.md`
- `V2A_DECISION.json`

`V2A_DECISION.json` must be one of:

- `HISTORICAL_FROZEN_INPUT_RECOVERED_AND_PUBLISHED`
- `HISTORICAL_FROZEN_INPUT_RECOVERED_NOT_PUBLISHED`
- `HISTORICAL_FROZEN_INPUT_NOT_RECOVERED`
- `BLOCKED_OTHER`

## Hard prohibitions

- no GPU/CUDA/Llama/NVBit/NCU execution;
- no tokenizer invocation;
- no regeneration of frozen inputs;
- no deletion/move/rename of source evidence;
- no 75 GB recovery-root migration;
- no RTX3090/RTX4080 authority merge;
- no large raw/model/profiler payloads in Git;
- no secrets/private keys/tokens in Git.

Commit and push only the V2A reports plus the exact small frozen-input bundle if it passes. Then stop.