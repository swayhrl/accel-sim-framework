# CODEX 174-new — Parallel Preflight, Independent Recompute, Admission, and ACK V2

## Goal

Start **now**, in parallel with node109's selector-provenance repair and producer finalization.

This is a fresh Codex window. Assume no prior chat context.

The task has two parts:

1. **Pre-bundle parallel work that can and should start immediately**
   - reconstruct accepted scientific/provenance context from Git and durable node164/174-side evidence;
   - independently preflight the receiver/data-plane;
   - independently prepare the selector-authority verifier and 243-shard scientific recompute;
   - search receiver/authority-side storage for the lost historical V38 selector-hash producer;
   - make the 174-side execution branch/review structure ready.

2. **Bundle-dependent work**
   - when node109 publishes the immutable Pipeline V1 bundle to the node164-mounted inbox, independently verify, recompute, admit, catalog, ACK, and prepare the third-lineage handoff.

Do not wait idly for 109. Do all dependency-free work first.

If the bundle arrives while this Goal is active, continue automatically through authority admission. If it has not arrived after all preflight work is complete, stop in a durable `READY_FOR_BUNDLE` state; absence of the bundle is not a scientific blocker.

---

# 1. Mandatory Git/context bootstrap

Fetch the repository and verify the ChatGPT coordination branch:

`hrl/c16-olmoe-v40-formal-admission-handoff-v1`

Expected coordination HEAD at Goal start:

`<EXPECTED_HEAD_FROM_USER_MESSAGE>`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/olmoe_v40_formal_admission/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/olmoe_v40_formal_admission/SELECTOR_AUTHORITY_REPAIR_V1.md`
3. `docs/vm_tlb/chatgpt_handoff/c16/olmoe_v40_formal_admission/MANIFEST_INPUT_BINDING_REPAIR_V1.md`
4. this file
4. `docs/vm_tlb/chatgpt_handoff/c16/olmoe_v40_formal_admission/CODEX_174_ADMIT_V1.md`
5. current V38/V39/V40 review packs relevant to OLMoE
6. current C16 data-plane implementation under `util/vm_tlb/c16/data_plane/`

Create/use a dedicated clean 174-new execution branch/worktree for receiver-side implementation/review artifacts. Do not edit producer branches.

Do not assume the producer's final Git commit is still `5901495...`; that was the last verified local-formal baseline. The final producer commit must later be taken from the transferred bundle manifest and verified against Git remote.

---

# 2. Frozen scientific identity — do not change

Model:

`allenai/OLMoE-1B-7B-0125-Instruct`

revision:

`b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Scenario:

`S2_TEXT B1/T2048/D32`

Semantic target:

- layer1
- decode32
- natural top-8 `[58,59,47,51,25,15,12,48]`
- rank-0 expert58
- `experts[58].down_proj`
- BF16
- input `[1,1024]`
- weight `[2048,1024]`
- output `[1,2048]`

Implementation evidence condition:

`actual-JIT variant A`

Historical variant B exists but is not formalized. Do not claim implementation-variant invariance.

Accepted actual-A static authority facts:

- complete static instruction count = 1096
- complete selected address-bearing set = 243
- historical all-static SHA =
  `089d264460999f54f9279ccced4b4bab72483d0572e1d08d6797338ef76a9aa3`
- historical V38 normalized selector SHA =
  `9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33`

Important provenance caveat:

The exact historical serialization that produced `9d2d...` was not durably retained in Git. V39R2 historically reported reproducing it, but the complete producer/algorithm was also not durably committed.

Therefore follow `SELECTOR_AUTHORITY_REPAIR_V1.md`. Do not invent or guess the old serialization.

---

# 3. Accepted V40 producer-side facts so far

Official NVBit 1.7.7.1 mem_trace has already been frozen as a healthy actual-A dynamic path:

`NVBIT1771_OFFICIAL_MEMTRACE_ACTUAL_A_CLEAN_DYNAMIC_PATH`

This closed:
- M0–M6
- rc=0
- no timeout
- no target/GPU residual process
- nonzero actual-A memory-event evidence
- BF16 raw-bit hash
- tool/replay SHA binding

Do not reopen:
- NVBit 1.7.5/1.7.7.1 matrix
- 1.7.7.3/1.8 exploration
- R575 downgrade/reboot

Last producer local-formal report before provenance repair:

- 243 selected shards
- 129 executed
- 114 proven zero
- 0 failed/excluded
- 132,096 C16WARP1 **warp records**
- 4,196,352 **active-lane events**
- typed anchors:
  - weight = static 101
  - input = static 103
  - output = static 1085

These are **expectations only** until 174 independently recomputes them from the destination bundle. Never use them as the input truth for the recompute.

Keep units distinct:
- `dynamic_warp_records`
- `active_lane_events`

Do not call both simply “dynamic events”.

---

# 4. Node/data-plane roles

Frozen role split:

- node109 = GPU producer / active local model replica
- 174-new = independent receiver, verifier, CPU-side analyzer, coordinator
- node164-mounted storage = durable formal raw/catalog/model authority

174-new node164 root:

`/root/share/mnt164/huangrulin/c16_ai_workload`

Correct publish path from producer:

`109 -> SSH alias hrl174new -> node164-mounted C16 inbox`

109 does not directly access node164.

Formal admission concurrency:

`FORMAL_ADMISSION_CONCURRENCY=1`

Required authority chain:

producer local close
→ `inbox/<RUN_ID>.partial`
→ independent destination verification
→ independent scientific recompute
→ immutable raw promotion
→ catalog entry/snapshot
→ positive ACK

An rsync success is not admission.
A producer summary is not independent recompute.
A `.partial` directory is not accepted raw.

---

# 5. Phase P0 — immediate 174 environment/data-plane preflight

Start this now.

Verify without modifying accepted scientific data:

- current hostname/user/worktree
- node164 mount exists and is readable
- expected C16 root exists
- `captures/inbox`, raw/catalog layout or current Pipeline V1 equivalent
- free space sufficient for the incoming bundle
- no conflicting admission already in progress for the same OLMoE run
- current Git transport works
- Python environment needed by receiver scripts works

Inspect the current receiver/data-plane code:

- `verify_capture.py`
- `admit_capture.py`
- `catalog.py`
- `rebuild_catalog_snapshot.py`
- `receiver_common.py`
- quarantine helpers
- producer-side `pipeline.validate_ack` contract

Do not redesign Pipeline V1 merely because a helper script is missing. If there is no dedicated ACK writer, implement the smallest receiver-side writer that produces exactly the existing `validate_ack` schema and binds only already verified/admitted receipts.

Do not admit any bundle during preflight.

Use synthetic/temp fixtures only in an explicitly non-authority scratch path if testing is necessary. Never write test data under accepted raw/catalog namespaces.

---

# 6. Phase P1 — independent receiver-side historical provenance search

This can run in parallel with 109's bounded search.

Search **read-only** receiver/authority-side durable locations for the exact producer/artifact that generated the historical selector hash:

`9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33`

Search likely locations only, including:

- Git history/review packs/worktrees visible to 174-new
- node164 C16 authority/provenance trees
- legacy C16/recovery trees already mounted on 174-new, if present
- exact filename references:
  - `VARIANT_A_COMPLETE_STATIC_SELECTOR`
  - `COMPLETE_VARIANT_A_STATIC_SELECTED_SET`
  - selector/hash-generation scripts
- exact textual occurrence of `9d2d4149...`

Do not brute-force arbitrary JSON/TSV canonicalizations.

Produce a durable receiver-side provenance-search note/receipt recording:
- locations searched
- exact producer found/not found
- exact artifact/script hashes if found

If the exact historical producer is found:
- do not alter it;
- preserve/hash it;
- independently test whether it reproduces `9d2d...`;
- report the result.

If not found:
- record that result;
- continue with the explicit V1 provenance repair below.

This search does not block other preflight work.

---

# 7. Phase P2 — prepare an independent selector-authority verifier now

Do not wait for the producer bundle.

From the specification in `SELECTOR_AUTHORITY_REPAIR_V1.md`, implement a **receiver-side independent** `C16_SELECTOR_CANONICAL_V1` verifier.

Independence requirement:
- do not import/call the producer canonicalizer implementation when recomputing the hash;
- implement the same written specification separately on 174-new;
- a shared specification is allowed; shared generated output is not.

Canonical V1 specification:

1. UTF-8 TSV, tab delimiter.
2. reject duplicate column names.
3. reject missing/extra fields.
4. require `static_index`.
5. preserve each parsed field as its exact string value.
6. reject duplicate static indices.
7. sort rows by numeric `int(static_index, 0)`.
8. sort column names lexicographically.
9. each row object contains exactly those sorted columns and exact string values.
10. top-level object:
   `{"schema":"C16_SELECTOR_CANONICAL_V1","columns":[...],"rows":[...]}`
11. serialize:
   `json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"`
12. UTF-8 bytes.
13. SHA256.

Before the real bundle exists, test the receiver implementation using a tiny synthetic TSV fixture created only in scratch:
- reorder input rows and prove same canonical hash;
- alter one field and prove different hash;
- duplicate static index and prove reject;
- missing/extra field and prove reject.

Commit the receiver-side verifier/test fixture or otherwise make its source SHA durable on the 174 execution branch.

Do not compute the real V40 selector hash until the real transferred raw TSV exists on the destination side.

---

# 8. Phase P3 — prepare independent 243-shard recompute logic now

Prepare a receiver-side recompute that reads raw shard evidence, **not producer summaries**, and derives the final numbers.

It must independently perform:

## selector/membership checks
- exactly 243 selector rows
- exactly 243 unique static indices
- selector membership == shard membership
- typed anchors 101/103/1085 are members
- raw TSV SHA
- receiver-side canonical V1 selector SHA
- if exact historical producer was recovered, optional independent historical `9d2d...` reproduction

## per-shard validation
For every shard require:
- selected static identity
- function identity binding
- exact occurrence proof
- valid C16WARP1 header/schema
- exact one terminal
- producer/receiver/serialized closure
- overflow=0
- record-size alignment
- per-record static identity
- lifecycle CLEAN_EXIT
- no timeout
- residual-process closure as required by current supervisor receipt
- same-process ADDRESS_CONTEXT for scientific attribution

Rerun the accepted C16WARP1 validator on destination data.

The aggregate recompute must **not** read `FORMAL_243_SUMMARY.json` or `FORMAL_243_ANALYSIS.json` as input truth. Those files may only be compared after the receiver result has been computed.

Classification:
- record_count > 0 + all gates PASS = `EXECUTED`
- record_count == 0 + all gates PASS = `ZERO_EXECUTION_PROVEN`
- otherwise = `FAILED_EXCLUDED`

## independent analysis
Compute:
- total selected
- executed
- proven zero
- failed/excluded
- dynamic_warp_records
- active_lane_events
- typed role event counts/fractions
- per-shard unique 128B lines
- per-shard unique 4K pages
- per-shard unique 64K pages
- per-shard unique 2M pages
- sums only as `SUM_OF_PER_SHARD_UNIQUES`

Do not compute:
- cross-shard absolute-VA union
- cross-shard global chronology
- cross-shard reuse distance
- fresh-process absolute-VA comparison
- cache/TLB causality

Build this receiver recompute so it can be pointed at the future verified inbox/raw bundle without source changes.

Use synthetic/minimal fixtures now if useful, but no scientific claims from fixtures.

---

# 9. Phase P4 — prepare admission/ACK review structure now

Prepare the 174-side review-pack structure, but leave bundle-dependent receipts explicitly pending.

It should eventually include:
- receiver environment/preflight receipt
- historical selector provenance search
- receiver canonicalizer identity/test receipt
- transport verification receipt
- independent selector-authority verification
- independent 243 recompute summary
- producer-vs-receiver delta report
- admission receipt
- catalog-entry identity
- positive ACK identity
- final OLMoE authority decision
- third-lineage handoff

Do not create a fake PASS placeholder for missing bundle-dependent evidence.
Use explicit `PENDING_BUNDLE` / `NOT_RUN` states.

---

# 10. Phase W — wait/discover the incoming bundle without blocking useful work

After P0–P4 are complete, inspect the node164-mounted inbox.

The producer may not yet have published.

Do not guess RUN_ID from directory name alone. Identify the intended bundle by its manifest:
- model/revision
- OLMoE target
- actual-JIT variant A condition
- scenario S2 B1/T2048/D32
- instrument/formal portfolio identity
- producer hostname
- producer Git commit

If no matching `.partial` bundle exists yet:
- persist a `READY_FOR_BUNDLE` receipt containing completed preflight Git SHA and tool/verifier SHAs;
- optionally perform bounded low-frequency polling if this Goal can remain active without wasting resources;
- do not classify absence as failure;
- do not mutate raw/catalog;
- STOP only if the execution environment requires it.

If the bundle appears while active, continue immediately.

---

# 11. Phase A — independent transport verification after bundle arrival

Use existing Pipeline V1 receiver verification.

Independently verify:
- manifest schema
- exact RUN_ID
- artifact inventory
- file sizes
- SHA256 of every artifact
- no symlinks/unexpected non-regular files
- local-close/manifest bindings required by the contract
- producer Git commit exists remotely

Generate the destination verification receipt.

If verification fails:
- no admission
- no ACK
- quarantine according to Pipeline V1 policy where appropriate
- ordinary packaging/transfer fixes are solve-and-continue with a corrected immutable partial bundle

Do not “repair” scientific raw files on the receiver.

---

# 12. Phase B — independent selector provenance/authority closure

From the **destination bundle**, not producer local paths:

If exact historical serializer was recovered:
- independently reproduce the historical selector SHA `9d2d...`;
- record exact producer/script/artifact identity.

Otherwise:
- verify producer's provenance-repair receipt;
- independently hash the raw TSV bytes;
- independently recompute `C16_SELECTOR_CANONICAL_V1` using the receiver implementation;
- require equality with the producer's newly frozen raw/canonical V1 authority;
- require exact 243 static membership equality with the formal shards.

Preserve provenance wording:
- historical `9d2d...` remains an opaque historical checksum unless actually reproduced;
- new canonical V1 hash is a provenance-repair authority;
- never relabel the new hash as the historical V38 hash.

---

# 13. Phase C — independent 243-shard scientific recompute

Run the prebuilt receiver recompute directly against destination evidence.

Expected producer-reported numbers:

- total = 243
- executed = 129
- proven zero = 114
- failed = 0
- dynamic_warp_records = 132096
- active_lane_events = 4196352
- typed anchors = weight 101 / input 103 / output 1085

But compute first, compare second.

Produce an explicit delta report:
- receiver value
- producer reported value
- equality/difference

Acceptance requires:
- 243 exact coverage
- 129 + 114 = 243 if those counts independently reproduce
- 0 failed/excluded
- all validators PASS
- selector/shard membership exact
- tool/replay/function identity uniform and non-null as required by the producer contract
- typed role closure
- no prohibited cross-shard analysis

Any unexplained mismatch is fail-closed and blocks authority admission.

---

# 14. Phase D — immutable node164 admission

Only after:
- transport verification PASS
- selector authority PASS
- independent scientific recompute PASS
- producer/receiver delta report PASS

perform serial authority admission.

Use existing Pipeline V1:
- `admit_capture.py`
- immutable raw promotion
- immutable catalog entry
- deterministic catalog snapshot rebuild

Do not overwrite an existing RUN_ID.

If post-promotion catalog closure fails, follow existing quarantine semantics. Do not ACK ambiguous raw state.

---

# 15. Phase E — positive ACK

Issue positive ACK only after immutable raw + catalog closure.

It must satisfy the existing producer-side `validate_ack` schema exactly:

- schema_version
- run_id
- source_manifest_sha256
- destination_manifest_or_verification_sha256
- file_count
- total_bytes
- destination_raw_path
- verified_at_utc
- verification_status = PASS
- catalog_entry_sha256

If no dedicated ACK writer exists, implement a minimal receiver-side writer from the already verified/admitted receipts. Do not change the ACK schema.

Persist ACK durably under the authority/review path and make it accessible for producer-side validation.

No ACK before admission.

---

# 16. Phase F — Git closure and third-lineage handoff

Commit/push/remote-verify the 174-new review pack and any receiver-side verifier/recompute sources.

Final OLMoE authority statement must explicitly say:

- natural expert58 down_proj
- actual-JIT variant A conditioned
- 243 selected static paths
- independently recomputed executed/zero/event/page/line/object evidence
- node164 immutable admission
- positive ACK
- historical variant B remains unformalized
- no OLMoE implementation-variant invariance claim

Then prepare the next consumer handoff for:

1. Qwen3-30B natural expert21 down_proj
2. DeepSeek-V2-Lite natural expert4 down_proj
3. OLMoE natural expert58 down_proj / actual-JIT variant A

Allowed wording:
`three-independent-lineage MoE-family pattern`

Not allowed:
`universal MoE law`

This is a descriptive cross-lineage comparison, not a matched-input causal experiment.

---

# 17. Solve-and-continue vs STOP

Solve-and-continue:
- Git/worktree/path issues
- Python environment
- receiver parser bugs
- canonicalizer implementation bugs
- manifest parsing
- catalog tooling
- ACK helper implementation
- inbox discovery
- transport packaging mismatch that requires producer republish
- review-pack organization

Do not relax scientific contracts to solve engineering problems.

STOP for human review only if:
- scientific target/identity must change;
- actual 243 selector membership differs materially;
- immutable shard evidence independently fails;
- receiver scientific recompute differs from producer in a non-packaging way;
- authority/admission contract must change;
- accepted raw/catalog authority would need destructive mutation.

---

# 18. Desired result

Best case, if 109 publishes while this Goal is active:

parallel preflight
→ bundle appears
→ independent verify
→ independent selector authority closure
→ independent 243 recompute
→ immutable node164 admission
→ positive ACK
→ third-lineage handoff
→ STOP

If bundle does not appear before preflight is complete:

parallel preflight
→ `READY_FOR_BUNDLE`
→ durable Git/review state
→ STOP or bounded wait

Do not idle before completing the dependency-free preflight work.


# Addendum — rejected first RUN_ID and corrected republish

The first received RUN_ID:

`C16R_olmoe-1b-7b-0125-instruct_s2-t2048-d32_decode32_nvbit1771-c16warp1_expert58-down-proj-actual-a_20260922T092141Z_50f32755c1ba`

was correctly fail-closed because the manifest used a non-SHA scenario label in `input.token_ids_sha256_or_semantic_hash`.

Failure commit:
`f37684ba863b8c66aa95ee40205df69233e159ff`

Do not retry verification on that same manifest expecting PASS.

The accepted V34 frozen token-ID compact-list SHA is:

`5d05e7cb6f5f89dda4feff7aded76f27e9630b57d527526812accf9db329ecc5`

Producer must publish a **new RUN_ID** with a corrected immutable manifest.

Receiver may quarantine the rejected unadmitted partial using the existing Pipeline V1 quarantine mechanism, preserving the failure reason/receipt. Never promote/delete it silently.

When the replacement partial arrives, verify it from scratch. Require the corrected token-ID SHA above and continue the normal independent selector/scientific recompute only after manifest/schema/artifact verification PASS.
