# C16 OLMoE exact S2 input authority recovery — 174-new V33

## Goal mode
Execute this task in **GOAL MODE** on 174-new. CPU-only. No GPU. Do not modify accepted C16 raw/catalog.

Suggested implementation branch:

`hrl/c16-olmoe-s2-input-recovery-174new-v33`

Use:
- repo: `/root/workspace/accel-sim-framework`
- durable node164 mount: `/root/share/mnt164`
- existing HTTPS + authenticated `gh` integration
- explicit `git -C /root/workspace/accel-sim-framework ...`
- if command stdout is unexpectedly empty, redirect to `/tmp` and read the file

## Accepted upstream

OLMoE authorization:
- branch: `hrl/c16-olmoe-third-moe-authorization-174new-v31`
- HEAD: `4013582e5cedef3e2ecaf7b7c74d9bb45a1af8ce`
- decision: `C16_OLMOE_THIRD_MOE_AUTHORIZATION_174NEW_V31_PASS`

OLMoE producer blocker:
- branch: `hrl/c16-olmoe-s2-producer-109-v32`
- HEAD: `ed22d57255a52e492e332f3f8efa619e217c3cc6`
- decision: `C16_OLMOE_S2_PRODUCER_109_V32_FAIL_CLOSED_EXACT_S2_TOKEN_FREEZE_UNPROVEN`

V32 already proved:
- canonical 11-file OLMoE payload closure
- only extra canonical-directory file is `MODEL_ASSET_RECEIPT.json`
- exact native BF16 full-resident RTX4080 capacity PASS
- blocker is input authority only

Do not reopen model capacity/runtime in this CPU Goal.

## New exact raw-source recovery artifact

This coordination branch contains:

`docs/vm_tlb/assets/c16/recovered_q30_s2_raw_payload_v1/TEXT.txt`

and

`docs/vm_tlb/assets/c16/recovered_q30_s2_raw_payload_v1/RECOVERY_RECEIPT.json`

The candidate bytes were reconstructed from V32 evidence:
- decoded minimum Q30 period = 19 tokens
- decoded UTF-8 period text exactly:
  `A reproducible system records identity, inputs, transformations, and checksums before interpreting results. `
- period byte length = 108
- period SHA256 = `7c072b754618dd7ab930526cd576ec0de011bb24e93d967c279591504996cc3f`
- repeat count = 108
- recovered byte length = 11664
- recovered SHA256 = `dc7e280c7ad2e31f243e23c12bee6a66aaf93dfba9be9f976c35d73832c85792`

That recovered SHA is exactly the raw-payload SHA pinned by the Q30 S2 receipt and required by V32.

This is **not authorization to trust the prose by inspection**. Independently hash the file and require byte-for-byte hash closure.

## Stage 0 — exact-byte recovery gate

Independently verify:
1. file is exactly 11664 bytes
2. SHA256 exactly equals:
   `dc7e280c7ad2e31f243e23c12bee6a66aaf93dfba9be9f976c35d73832c85792`
3. no newline/normalization/strip/re-encoding has changed the bytes
4. recovery receipt matches the V32 pinned expected raw-payload hash

If any mismatch: fail closed.

Classify a successful result as:

`PASS_HASH_VERIFIED_EXACT_RAW_PAYLOAD_RECOVERY`

Do not call this a semantically equivalent replacement. It is acceptable only because exact byte identity closes to the pre-existing pinned SHA256.

## Stage 1 — optional Q30 corroboration

If an exact Q30 tokenizer and/or original Q30 token authority is available from canonical node164 assets/provenance without SSH or mutation:
- tokenize the recovered bytes under the exact Q30 input policy
- verify first 2048 IDs against an existing independently bound Q30 token authority/hash if one is available
- record the corroboration

This is supporting evidence. The hard source-identity gate is the exact recovered raw-payload hash above.

Do not use SSH to node109 merely to obtain the old token file.

## Stage 2 — freeze exact OLMoE S2/T2048 IDs

Canonical OLMoE asset:

`/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e/`

Model:
`allenai/OLMoE-1B-7B-0125-Instruct@b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Use the exact tokenizer files already validated by V31.

The C16 matched-input scientific axis is direct model tokenizer encoding of the exact common raw source, with no prompt re-authoring. Preserve the established prospective-common-input policy:
- source bytes = exact recovered 11664-byte artifact
- `add_special_tokens=False`
- chat template = `NOT_APPLIED`
- tokenize exact UTF-8 bytes/text without normalization
- require at least 2048 tokens
- freeze the **first exact 2048 token IDs**
- batch = 1
- scenario = `S2_TEXT B1/T2048/D32`

Do not pad, regenerate prose, append content, or silently alter source bytes.

Persist:
- model ID/revision
- source artifact path + SHA256
- tokenizer.json SHA256
- tokenizer_config SHA256
- special_tokens_map SHA256
- exact token count before truncation
- exact frozen 2048 IDs
- token serialization definition
- token-sequence/token-matrix SHA256
- payload JSON SHA256
- `no_retokenization_after_freeze=true`

## Stage 3 — durable authority

Create a durable recovered-input authority under node164, for example:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/recovered_inputs/C16_Q30_S2_RAW_PAYLOAD_RECOVERY_V1/`

It must contain only small authority artifacts, not model weights:
- exact `TEXT.txt`
- recovery receipt
- OLMoE S2 token-IDs payload
- OLMoE S2 input receipt/manifest

Copy bytes exactly; verify hashes after write.

Also commit repo-side review evidence. Do not modify accepted raw/catalog.

## Stage 4 — producer continuation contract

Generate a node109 continuation contract that starts from the accepted V32 state but does **not** claim V32 formal PASS.

The future producer must:
1. reverify exact OLMoE asset/runtime identity
2. consume the frozen OLMoE token IDs directly; no retokenization
3. load native BF16 model and re-establish runtime identity
4. capacity may rely on V32 as prior evidence, but actual model execution still must fit naturally
5. execute S2
6. capture natural top-8 router receipt
7. qualify target hierarchy:
   - natural selected-expert down_proj if losslessly attributable
   - else grouped/fused expert-down with lossless group attribution
   - else narrower routed-expert weight consumer
8. exact replay/signature where semantics permit
9. fresh SM89 static/path audit
10. known-good warp-regsource canary
11. complete formal capture
12. serial transfer/admission/positive ACK
13. review pack + Git closure

`FORMAL_ADMISSION_CONCURRENCY=1`

## Required review pack

Create:

`docs/vm_tlb/review_packs/C16_OLMOE_S2_INPUT_RECOVERY_174NEW_V33/`

Include at least:
- `UPSTREAM_AUTHORITY.tsv`
- `RAW_PAYLOAD_RECOVERY.json`
- `RAW_PAYLOAD_HASH_AUDIT.json`
- `Q30_CORROBORATION.json`
- `OLMOE_S2_INPUT_AUTHORITY.json`
- `OLMOE_S2_TOKEN_IDS.json`
- `NODE164_DURABLE_AUTHORITY.json`
- `NODE109_CONTINUATION_CONTRACT.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preferred PASS:

`C16_OLMOE_S2_INPUT_RECOVERY_174NEW_V33_PASS`

Only PASS if the recovered raw bytes hash exactly to the V32 pinned raw-payload SHA and exact OLMoE 2048-token authority is frozen.

## Git closure

Complete:
`review pack -> SHA256SUMS -> commit -> push -> LOCAL == git ls-remote == authenticated gh api -> clean worktree -> STOP`
