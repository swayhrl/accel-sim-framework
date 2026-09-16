# CODEX GOAL — C16 Qwen3 Independent Consumer + Cross-Lineage V16 (174-new)

## Mission
Resume the blocked 174-new consumer task using exact producer identities and exact node164 paths. Do not enumerate/search for the Qwen3 run. Directly open the known catalog entry and accepted raw directory, independently recompute formal integrity and replay-local memory fingerprints, then compare Qwen2.5-7B raw vs Qwen3-8B at the matched semantic operator `first-decode layer0.mlp.down_proj`.

CPU-only. No GPU/model execution. No accepted raw/catalog mutation. No Qwen3-30B/DeepSeek.

## Fixed Qwen3 producer evidence authority
Producer evidence-closure HEAD:
`ac4420f81dfafbe03b96e1bda63b4af31fe77f6a`

Review pack:
`docs/vm_tlb/review_packs/C16_QWEN3_8B_EVIDENCE_CLOSURE_109_V15/`

Formal run ID:
`C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v14-layer0-downproj_20260916T020000Z_dd14dd14dd14`

Exact node164 catalog entry:
`/root/share/mnt164/huangrulin/c16_ai_workload/catalog/entries/C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v14-layer0-downproj_20260916T020000Z_dd14dd14dd14.json`

Expected catalog-entry SHA256 from accepted ACK receipt:
`21f799d4079ffcabe9892876541abfcf26e5641ca3ed59f12ff9864862c01461`

Exact node164 accepted raw directory:
`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v14-layer0-downproj_20260916T020000Z_dd14dd14dd14`

Expected source manifest SHA256:
`2784c8c23fe4e2173a4d5dd3d8595d4fadd8fc66fb1ffa50b883052ece6c540d`

Expected accepted transfer metadata:
- file_count = 732
- total_bytes = 883510599
- destination verification SHA256 = `6bb85bd599142ea67f5dbf1c4b78c78709c3cd1c74d0712c4ec4305957fb483f`

Qwen3 producer semantic/formal expectations to independently audit, not blindly copy:
- semantic target: `model.layers.0.mlp.down_proj`
- scenario: S2_TEXT, first decode
- direct-global static set = 243
- LDGSTS global-source = 0
- executed = 129
- zero-proven = 114
- expected/present/terminal-closed shards = 243/243/243
- drop_total = 0
- overflow_total = 0

## Fixed Qwen2.5 raw comparison identity
Accepted V10 RAW run ID:
`C16R_qwen25-7b-raw_s2-text_decode_nvbit-warp-mref-shard_v10-semantic-downproj-r2_20260916T005000Z_cc10cc10cc10`

Exact node164 catalog entry:
`/root/share/mnt164/huangrulin/c16_ai_workload/catalog/entries/C16R_qwen25-7b-raw_s2-text_decode_nvbit-warp-mref-shard_v10-semantic-downproj-r2_20260916T005000Z_cc10cc10cc10.json`

Exact node164 raw directory:
`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen25-7b-raw_s2-text_decode_nvbit-warp-mref-shard_v10-semantic-downproj-r2_20260916T005000Z_cc10cc10cc10`

The Qwen2.5 V10/174-new V11 accepted evidence remains the comparison authority.

## P0 — Exact-path readability triage
Do NOT use broad `find`, catalog grep, semantic search, or directory enumeration as the first gate.

For each of the four exact paths above:
1. run `stat` and record exit code, stdout, stderr;
2. use Python `Path.exists()`, `is_file()/is_dir()` and direct `open()`/`iterdir()` where appropriate;
3. for catalog files compute SHA256 from bytes;
4. for raw directories open the exact `RUN_MANIFEST.json`, `STATIC_MREF_MAP.tsv`, `WARP_SHARD_MANIFEST.json`, and receipt files by exact relative path;
5. distinguish `ENOENT`, `EACCES`, mount/I/O error, and empty file explicitly.

An empty stdout is NOT evidence of absence if exit status/stderr were not captured.

Produce `SOURCE_READABILITY_AUDIT.tsv` including command/method, exact path, exit code, errno/error, bytes if file, and status.

If the Qwen3 exact accepted raw/catalog paths are not readable, emit `C16_QWEN3_CONSUMER_174NEW_V16_BLOCKED_SOURCE_IO_<errno>` with concrete diagnostics and STOP. Do not fall back to producer summary for independent raw analysis.

## P1 — Independent Qwen3 formal audit
Read the accepted node164 artifacts directly and independently recompute:
- catalog entry SHA and manifest identity;
- model/revision/scenario/phase/target descriptors;
- fresh static direct-global set membership/count from accepted static map;
- executed vs ZERO_EXECUTION_PROVEN partition from accepted shard artifacts/manifest;
- expected/present/terminal-closed shard counts;
- each raw binary SHA256 and ADDRESS_CONTEXT SHA256;
- drop/overflow totals;
- static-PC membership;
- same-process context count and evidence class;
- verification/admission/ACK receipt consistency.

Do not use producer V15 counts as the computation source; use them only as expected values for mismatch detection.

Produce:
- `QWEN3_FORMAL_INDEPENDENT_AUDIT.json`
- `QWEN3_STATIC_EXEC_ZERO.tsv`
- `QWEN3_SHARD_FINGERPRINTS.tsv`
- `QWEN3_PIPELINE_RECEIPT_AUDIT.json`

Mismatch with accepted durable evidence -> fail closed.

## P2 — Semantic evidence audit using hash-closed V15 pack
Independently inspect the producer V15 Git evidence for:
- `S2_STATE_CAPTURE_RECEIPT.json`
- `S2_REPLAY_EQUIVALENCE.json`
- `S2_SIGNATURE_GATE.json`
- `S2_STATIC_PATH_SUMMARY.json`
- `S2_FORMAL_CAPTURE_SUMMARY.json`
- `S2_PIPELINE_ACK_RECEIPT.json`

Confirm hash closure against `SHA256SUMS` and consistency with the accepted raw identity. Record semantic status separately from raw/formal validity.

Expected producer evidence includes:
- decode token 15;
- down_proj input `[1,1,12288]` BF16;
- output `[1,1,4096]` BF16;
- replay bitwise equal, max_abs=0;
- in-context/replay `internal::gemvx::kernel` with grid `(1024,1,1)` and block `(32,4,1)`;
- target weight SHA and state/input/output SHA identities.

Do not promote anything that does not hash-consistently join.

## P3 — Qwen3 replay-local memory fingerprint
Decode every EXECUTED direct-global shard using the established C16WARP1 parser. Compute only supported metrics:
- active-lane dynamic memory events;
- load/store event counts;
- per-static-PC event counts;
- per-shard unique 4K/64K/2M page counts;
- per-shard unique 128B line counts;
- any mathematically safe summary distributions across independent shards;
- same-process object composition only from direct ADDRESS_CONTEXT range identity; otherwise `UNKNOWN_RUNTIME`.

Never form a cross-shard VA union unless the existing C16 contract explicitly proves it lossless. Never infer chronology/reuse distance.

Produce:
- `QWEN3_MEMORY_FINGERPRINT.json`
- `QWEN3_STATIC_PC_DYNAMIC_SUMMARY.tsv`
- `QWEN3_OBJECT_ATTRIBUTION.tsv`

## P4 — Qwen2.5 raw matched-semantic comparator
Independently consume or reuse already independently accepted Qwen2.5 raw V10/V11 fingerprint evidence, binding the exact RAW run ID above.

Compare Qwen2.5-7B raw vs Qwen3-8B for the matched semantic operator only:
- model target dimensions / down_proj weight shape and static bytes;
- semantic input/output logical shapes;
- qualified kernel family/signature;
- static direct-global set size and special-path classes;
- executed/zero partition;
- dynamic active-lane event totals/distributions;
- page/line footprint summaries;
- object attribution where independently supported.

Label this exactly:
`CROSS_LINEAGE_MATCHED_SEMANTIC_OPERATOR_COMPARISON`

It is NOT same numeric input and NOT a causal architecture-only experiment.

Every comparison row must have `evidence_status = PROVEN | PENDING | NOT_COMPARABLE` and provenance identifiers for both sides.

NCU rule: Qwen3 V15 metric CSV has `CSV_DISPLAY_UNIT_UNSPECIFIED` and raw values currently unavailable. Do not compare NCU traffic numerically unless both sides have explicit comparable units and durable numeric values.

Produce:
- `QWEN25_RAW_VS_QWEN3_DOWNPROJ_COMPARISON.tsv`
- `CROSS_LINEAGE_INTERPRETATION.md`

## P5 — Next-target decision
Based on the independently verified comparison, decide whether the next Qwen3 information gain should come from:
- attention/KV at S2 first decode;
- S3 long-context attention/KV census/target;
- another MLP operator only if it is materially new.

Do not execute GPU work. Produce `NEXT_QWEN3_TARGET_RECOMMENDATION.json` with rationale and evidence needed.

## P6 — Output
Create:
`docs/vm_tlb/review_packs/C16_QWEN3_CONSUMER_174NEW_V16/`

Include all outputs above plus:
- `SEMANTIC_EVIDENCE_AUDIT.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Allowed decisions:
- `C16_QWEN3_CONSUMER_174NEW_V16_PASS`
- `..._PASS_WITH_NCU_GAP`
- `..._BLOCKED_FORMAL_INTEGRITY`
- `..._BLOCKED_SOURCE_IO_<specific>`

Commit/push and STOP.