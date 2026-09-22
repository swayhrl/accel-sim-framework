# C16 OLMoE V40 — Pipeline V1 Input-Binding Manifest Repair V1

## Failure classification

174-new correctly failed closed on the first published V40 bundle before scientific recompute/admission.

Rejected RUN_ID:

`C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T092141Z_50f32755c1ba`

Rejected source manifest SHA256:

`7402a5e616d6161b5ba25499fd9207e1486dcd032bfb2a9b81d99a74f0c73660`

Observed invalid field:

`input.token_ids_sha256_or_semantic_hash = "S2_TEXT_B1_T2048_D32"`

Pipeline V1 requires this field to be a lowercase 64-hex SHA256.

No scientific raw/admission/catalog/ACK state was created by the receiver. This is a producer packaging/manifest defect, not a scientific data failure.

## Correct accepted input authority

The accepted OLMoE V34 input authority is:

`docs/vm_tlb/review_packs/C16_OLMOE_S2_PRODUCER_109_V34/S2_INPUT_AUTHORITY.json`

at accepted V34 commit:

`ab26365dc663268b0799818db6687ed466e8c925`

Relevant frozen facts:

- source:
  `docs/vm_tlb/assets/c16/prospective_common_input_v1/TEXT.txt`
- source SHA256:
  `52761ce278c0e4819f153036e2b93e2b921d7963dda6a1d67a8192503612fa9c`
- frozen token count: 2048
- add_special_tokens: false
- chat_template: NOT_APPLIED
- no retokenization after freeze
- token-ID serialization:
  `UTF-8 JSON compact list, separators comma/colon; SHA256 applies prior to terminal newline`
- accepted frozen 2048-token compact-list SHA256:
  `5d05e7cb6f5f89dda4feff7aded76f27e9630b57d527526812accf9db329ecc5`
- frozen-file SHA256:
  `bba8ad1051b3e96039933d65ad8d77af3877f5603ae743b5e123d82c64de88e5`

The Pipeline V1 manifest field:

`input.token_ids_sha256_or_semantic_hash`

for this formal V40 bundle must be:

`5d05e7cb6f5f89dda4feff7aded76f27e9630b57d527526812accf9db329ecc5`

Do not put the scenario label in a SHA field.

The accepted Git blob/review-pack SHA for `S2_INPUT_AUTHORITY.json` is recorded by the V34 `SHA256SUMS` as:

`1773bcad6b2ebd6206f96be4b25c268dd316bad1978588530e550459f807e7fb`

If the Pipeline manifest's `input.receipt_sha256` is intended to bind this exact V34 authority receipt, use/verify that SHA. Do not change a different already-valid authority binding without checking its intended source.

## Repair policy

Do not mutate:
- the rejected destination `.partial` in place;
- the producer's already-finalized READY bundle in place;
- the failure receipt;
- any scientific shard/raw artifact.

Build a **new immutable producer bundle with a new RUN_ID** from the retained clean source artifacts.

Only the packaging/manifest layer changes.

The new bundle must:
1. preserve exactly the same scientific shard payloads/hashes;
2. preserve the same selector-authority repair and final scientific review evidence;
3. bind the accepted V34 input authority;
4. use the correct 64-hex token-ID SHA above;
5. have a new RUN_MANIFEST and therefore a new manifest SHA;
6. receive a new local-close receipt;
7. be published copy-only to a new `captures/inbox/<NEW_RUN_ID>.partial`.

Do not reuse the rejected RUN_ID.

## Producer validation before republish

Before transfer, run the same Pipeline V1 manifest validation locally that the receiver uses.

Require local PASS from the shared schema/validator, including:
- `input.receipt_sha256` is lowercase 64-hex;
- `input.token_ids_sha256_or_semantic_hash` equals the accepted V34 token-ID SHA;
- all artifact inventory entries still match the immutable copied payloads;
- producer Git commit in the manifest is the final corrected producer commit;
- `git.dirty=false` at final packaging time if that is the intended producer contract;
- model/revision/scenario/capture target remain unchanged.

Record a producer-side manifest-validation receipt.

## Receiver handling of the rejected partial

The first rejected partial is not accepted authority.

174-new may use the existing Pipeline V1 quarantine path to move the rejected unadmitted partial out of inbox, preserving:
- original RUN_ID;
- failure reason;
- failure receipt;
- rejected manifest SHA.

Do not delete it silently and do not promote it to raw/catalog.

The corrected bundle uses a new RUN_ID, so quarantine of the old partial is not a prerequisite for scientific correctness but is recommended for unambiguous inbox state.

## Receiver handling of the corrected bundle

Receiver must start verification from scratch on the new RUN_ID.

Do not reuse the old failure receipt as a PASS precursor.

Required sequence remains:

new `.partial`
→ manifest/schema/artifact verification
→ selector authority verification
→ independent 243-shard recompute
→ producer/receiver delta comparison
→ immutable raw promotion
→ catalog
→ positive ACK

## Scientific scope

No GPU recapture is authorized or required by this failure.

The already closed producer scientific portfolio remains:
- 243 selected
- 129 executed
- 114 proven zero
- 0 failed
- 132,096 dynamic warp records
- 4,196,352 active-lane events
- typed anchors 101/103/1085

These remain producer-side facts pending independent receiver recompute on the corrected bundle.
