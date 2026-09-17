# CODEX_NEXT_STAGE_174NEW_STORAGE_CONSUMER_AUDIT_V1

Status: ACTIVE
Ownership: ChatGPT
Node: 174-new / port 2239

## Objective

Independently audit node164 from the consumer/simulator side so that the AWMA storage data plane is not qualified only by the node109 producer.

This is a read-mostly storage/provenance audit. It must not modify simulator science, rerun Q05 characterization, or duplicate the producer capture workflow.

## Inputs

Read:

- `CURRENT_STATE.md`
- `DISCUSSION_REFERENCE.md`
- `STORAGE_GOVERNANCE_POLICY_V1.md`
- `CODEX_NEXT_STAGE.md`
- node109 storage-governance receipts if they already exist

Use the completed Q05 translation-timeline branch/worktree only as a source of already-produced raw-path references. Do not alter its scientific artifacts.

## Required audit

### A. Mount and capacity audit

Record from 174-new:

- mount type/source for `/root/share/mnt164`;
- free/used capacity;
- read/write permissions in the AWMA namespace;
- local 174-new filesystem free capacity;
- confirmation that durable large data does not depend on 174-new local disk.

No large accepted artifact may be copied to 174 local storage merely for audit.

### B. Existing durable artifact audit

Independently inspect and index, without moving:

1. accepted Q05 simulator-native trace bundle;
2. Q05 full/natural-completion simulation raw evidence;
3. Q05 translation-timeline raw evidence;
4. accepted S2 NSYS/full kernel-launch inventory;
5. frozen Qwen2.5 model/input authority references that are already present on node164.

For each, record:

- current durable path;
- type/status;
- size or manifest size root;
- existing accepted SHA/manifest root when available;
- independent consumer-side rehash for small metadata/manifests;
- for very large data, reuse accepted member-hash ledgers where scientifically sufficient rather than recursively rehashing unrelated terabytes;
- owning Git report/review-pack reference;
- retention class.

### C. Consumer-side canary verification

If node109 has completed `AWMA_164_DATA_PLANE_QUALIFIED_V1`, independently verify from 174-new:

- no stale `.partial` object is being mistaken for admitted data;
- promoted canary/test object is visible at the expected durable path before producer cleanup;
- destination size/hash receipt matches the producer receipt;
- read-back hash from 174-new matches;
- ACK semantics are unambiguous.

Do not regenerate the 1-2 GiB payload unless the producer canary is absent or scientifically unverifiable. If a new consumer-only fixture is required, keep it bounded and delete only that fixture after verification.

### D. Catalog audit

Validate that catalog entries/snapshots can be deterministically rebuilt/read from 174-new and that they do not require producer-local paths to locate authoritative data.

Flag:

- duplicate authorities;
- orphan `.partial` items;
- accepted data that exists only on 174 local disk;
- producer paths incorrectly treated as durable authority;
- unknown retention/status entries.

Do not delete or mass-move anything.

### E. Cleanup candidate report

Generate a list only. A path may be labeled `SAFE_TO_DELETE_AFTER_ACK` only when all policy preconditions are proven. No accepted scientific data may be deleted in this stage.

## Acceptance criteria

PASS requires:

- node164 is independently readable from 174-new;
- core accepted AWMA artifacts are indexed with durable paths and provenance;
- producer canary/ACK can be independently verified, or an explicit blocker is reported;
- no accepted large artifact is found to depend solely on 174-new local storage;
- catalog/read-back semantics are consumer-independent;
- no scientific identity or simulator behavior changed.

Success marker:

`AWMA_174NEW_STORAGE_CONSUMER_AUDIT_V1_COMPLETE_WITH_SCOPE`

Possible qualified status if producer Phase A has not finished:

`AWMA_174NEW_STORAGE_CONSUMER_AUDIT_V1_WAITING_FOR_PRODUCER_CANARY`

In that case complete all independent A/B/D/E work, record exactly what remains, and STOP rather than inventing producer receipts.

## Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/STORAGE_CONSUMER_AUDIT_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_STORAGE_CONSUMER_AUDIT_174NEW_V1/`

At minimum include:

- `README.md`
- `STORAGE_MOUNT_AUDIT.txt`
- `DURABLE_ARTIFACT_INVENTORY.tsv`
- `CONSUMER_REHASH_RECEIPTS.tsv`
- `CANARY_CONSUMER_VERIFY.md`
- `CATALOG_AUDIT.md`
- `CLEANUP_CANDIDATES.tsv`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

## Explicitly forbidden

Do not:

- run new TLB/PTW mechanism experiments;
- change Q05/SIM_INPUT identities;
- capture GPU data;
- perform NCU/NVBit/C16WARP1 work;
- reorganize accepted historical node164 paths for neatness;
- delete accepted raw data;
- copy large durable artifacts onto 174 local disk.

Routine storage/index/parser/Git issues are solve-and-continue. Stop only for provenance conflict, destructive risk, or a scientific-authority contradiction.

Finish -> review pack -> report -> hashes -> commit -> push -> remote verify -> clean worktree -> STOP.
