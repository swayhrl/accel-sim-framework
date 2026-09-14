# V2A frozen-input search

## Decision

`HISTORICAL_FROZEN_INPUT_NOT_RECOVERED`

The bounded source search found three byte-exact historical payloads, but did
not find the complete five-file bundle.  In particular, the required
`C16_FIND_AND_TRANSFER_LLAMA_S5_FROZEN_INPUT_BINDING_RECEIPT.json` and
`LLAMA_S0_TEXT_BINDING_RECEIPT.json` were absent under the permitted source
data/exchange roots.  A local `FROZEN_BINDING.json` is semantic evidence only;
it was not renamed or promoted to replace either missing receipt.

## Roots and method

Read-only exact-name searches were performed under:

- `/root/share/c16_recovery_v3`
- `/workspace/c16_exchange`
- the current repository/worktree

The same roots were searched for the four exact SHA256 values, limited to files
at most 5 MiB.  This avoids reading model/raw-trace payloads.  Git receipts and
the historical package/exchange manifests were read only.  No tokenizer was
loaded or invoked.

## Exact payloads found

| Contract role | Actual historical source path | Bytes | SHA256 | Result |
|---|---|---:|---|---|
| raw text | `/workspace/c16_exchange/autodl_wave1/P0_20260912T2225/a_assets/inputs/TEXT.txt` | 203 | `bae0b908106146659663fa04f44bc03ec0da18cadb08c9ec357c140afc4d8208` | PASS |
| token receipt | `/workspace/c16_exchange/autodl_wave1/P0_20260912T2225/a_assets/TOKEN_RECEIPTS/c16_llama32_1b_frozen_compatible/TEXT_T128.json` | 1946 | `0b5a86fdee44452e74e5d80e8043ebd97054fbbe29a6232a4f5cf5d06568c7dd` | PASS |
| derived token-ID payload | `/workspace/c16_exchange/autodl_wave1/returned/llama_s0_g1_formal_5bfbe62b-6140-4f94-8a91-2e433000572c/frozen_token_ids.json` | 618 | `fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624` | PASS |
| canonical compact JSON of those IDs | derived locally from the preceding existing payload, without tokenizer use | 128 IDs | `f9cf1ea6dca7956c740b3aa0af59acadd17be014df2aaffb75d240383502e3a7` | PASS |

Two other returned `frozen_token_ids.json` copies are byte-identical to the
selected 618-byte payload.  Five identical text payloads also occur in Qwen
staging roots; those copies are not Llama binding evidence and were not used.

## Missing required members

| Required member | Search result | Consequence |
|---|---|---|
| `LLAMA_S0_TEXT_TOKEN_IDS.json` | no file under this exact historical name; only byte-identical `frozen_token_ids.json` candidates | cannot publish a five-file bundle |
| `LLAMA_S0_TEXT_BINDING_RECEIPT.json` | absent | cannot establish required bundle member provenance |
| `C16_FIND_AND_TRANSFER_LLAMA_S5_FROZEN_INPUT_BINDING_RECEIPT.json` | absent | existing `c16_frozen_input_admission.py` cannot validate its required transfer inventory |

The semantic fields in three existing `FROZEN_BINDING.json` files agree with
S0/B1/T128/Decode4/TEXT and the exact Llama revision, but their different
historical filenames and the missing transfer-binding receipt prevent their use
as substitutes.

## Validator result

`NOT_RUN_FAIL_CLOSED_MISSING_REQUIRED_BUNDLE_MEMBERS`.

The validator was not pointed at a synthesized, renamed, partial, or temporary
bundle.  Its required `C16_FIND_AND_TRANSFER...` receipt is absent, so a PASS
could not truthfully be produced.  No `FROZEN_INPUTS/` payload directory,
`SHA256SUMS`, or `PROVENANCE.md` was published to Git.
