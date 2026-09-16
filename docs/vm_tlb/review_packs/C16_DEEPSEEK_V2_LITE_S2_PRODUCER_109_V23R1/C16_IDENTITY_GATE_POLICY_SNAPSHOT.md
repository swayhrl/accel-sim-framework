# C16 Identity / Authority Gate Policy V1

Purpose: prevent weak derived metadata from blocking execution when stronger identity evidence already closes, while preserving fail-closed behavior for real semantic mismatches.

## Evidence strength hierarchy

### Tier A — hard identity gates

Mismatch must STOP unless an explicit superseding authority is created.

- exact model ID + revision
- exact canonical relative file set for model payload when a manifest exists
- per-file SHA256 for canonical payload and local working copy
- config SHA256
- custom modeling/configuration source SHA256 when runtime uses remote/custom code
- safetensors index / shard identity and required shard presence
- canonical input payload SHA256
- canonical token-matrix/token-ID authority hash under a pinned serialization definition
- no-retokenization / no-substitution proof when required
- semantic replay equality / target-state hashes
- formal raw manifest hashes, terminal/drop/overflow conditions, receiver verification/catalog/ACK

### Tier B — conditional deployment gates

These are hard only when the scientific comparison requires the exact same deployment. Otherwise a changed deployment must be explicitly typed as a new deployment rather than silently accepted.

- torch / transformers / custom runtime version
- attention backend
- MoE grouped/fused implementation path
- CUDA code-object identity
- precision

### Tier C — derived sanity fields

Mismatch alone must NOT block when Tier-A identity closes. Record the discrepancy and its provenance.

- aggregate directory byte sum
- aggregate shard byte sum
- file count when exact path-set + per-file SHA closes
- human-readable model-size labels
- approximate GB values
- timestamps
- absolute local paths
- derived token-sequence hashes if serialization/encoding is not identical to the canonical hash definition
- version labels such as V1/V2 when an exact source ref + payload hash establishes the actual authority

## Required naming discipline

Never compare unlike quantities under the same name. Distinguish at least:

- tensor_payload_bytes / index_metadata_total_size
- safetensors_file_bytes
- repository_payload_bytes
- canonical_manifest_file_count

For input hashes distinguish:

- payload_file_sha256
- canonical_token_matrix_sha256
- token_sequence_sha256_<encoding>

A hash may be a hard gate only if its byte serialization is explicitly defined and matches the canonical authority definition.

## DeepSeek V23 correction

The V22 scalar `asset_bytes = 31418842074` is not accompanied by an exact path-set + per-file hash manifest in that authority pack. V23 independently closed a 15-file source/destination inventory with per-file SHA256 and aggregate sum `31418838087`; config/custom-code/tokenizer/shard hashes close. Therefore the 3987-byte scalar discrepancy is Tier C and must not, by itself, block CUDA execution.

V23R1 must produce a superseding hash-bound asset receipt from the exact canonical source/local destination inventories and use that receipt as Tier-A authority. Preserve the old V22 scalar as a historical discrepancy; do not rewrite historical packs.

The DeepSeek S2 input authority actually closes through exact source ref, payload SHA256 and canonical token-matrix SHA256. Any separately computed token-sequence hash using a different byte encoding is Tier C unless its serialization is explicitly identical to the canonical token-matrix hash definition.

## Audit rule

Before GPU execution in V23R1, audit every Stage-0 check and classify it A/B/C. Do not weaken Tier-A semantic/integrity gates. Do not promote Tier-C derived fields into fail-closed blockers.
