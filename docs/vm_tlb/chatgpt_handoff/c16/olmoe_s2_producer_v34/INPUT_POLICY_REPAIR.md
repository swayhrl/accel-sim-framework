# C16 OLMoE S2 input-policy repair V34

## Decision

The V32/V33 requirement that OLMoE reproduce the Q30-local 11664-byte raw payload is superseded for the cross-lineage MoE-family axis.

Reason: the accepted V25 Q30↔DeepSeek comparison is a same-scenario/natural-routed expert-down **family comparison**, not a matched-input comparison. Q30 and DeepSeek do not require byte-identical model inputs for that accepted claim.

Therefore OLMoE must use the established C16 prospective common TEXT source authority rather than padding/extending the Q30-local raw payload.

## Exact source authority

Authority:
`C16_PROSPECTIVE_COMMON_INPUT_V1`

Authority branch/commit:
`hrl/c16-prospective-common-input-174new-laneB-v8@ca683527323e26e3415a805c797c53c5edea322c`

Source:
`docs/vm_tlb/assets/c16/prospective_common_input_v1/TEXT.txt`

Exact properties:
- byte count: 976000
- SHA256: `52761ce278c0e4819f153036e2b93e2b921d7963dda6a1d67a8192503612fa9c`
- normalization: exact UTF-8 generator output
- no external corpus
- no reverse decoding
- truncation policy: first exact N token IDs

The producer must retrieve these exact bytes from the pinned commit/path and independently re-hash them before tokenization.

## OLMoE model-specific freeze

Model:
`allenai/OLMoE-1B-7B-0125-Instruct@b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Use exact canonical tokenizer files already closed by V31/V32.

Policy:
- source = exact pinned prospective common TEXT bytes above
- `add_special_tokens=False`
- `chat_template=NOT_APPLIED`
- require source tokenization length >= 2048
- freeze first exact 2048 IDs
- batch=1
- scenario=`S2_TEXT B1/T2048/D32`
- no padding
- no prompt re-authoring
- no source extension
- no retokenization after freeze

Persist source SHA, tokenizer hashes, full pre-truncation token count, exact 2048 IDs, serialization definition, token-sequence/token-matrix SHA, payload SHA.

## Claim boundary

Future Q30+DeepSeek+OLMoE synthesis may evaluate a **three-independent-lineage MoE-family pattern** only.

It must NOT claim:
- matched-input causality across all three lineages
- same numeric hidden states
- same selected expert
- vendor/model causal effects
- cache/TLB causality

Any common pattern must be descriptive across natural-routed expert-down semantic anchors under S2 decode.

## V33 status

The local V33 blocker based on 1837 OLMoE tokens from the Q30-local recovered source is scientifically superseded by this policy repair.

Do not pad or alter that 11664-byte Q30-local payload. Preserve it as historical evidence if later archived.

The 174 smart-HTTP Git transport outage is operational and does not change the scientific authority above.
