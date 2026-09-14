# C16 Old174 Final Handover to 2239 — V0

## 0. Purpose

This is the **final continuous C16 AI-workload task for the old 174 Docker**.

Source environment:

```text
old174 Docker: root@10.208.130.174 -p 2233
historical C16 root: /root/share/c16_recovery_v3
```

After this handover is accepted, old174 stops independently developing new C16 capture, transfer, storage, or analysis protocols. It becomes a historical/source authority endpoint and is used again only when ChatGPT explicitly requests bounded read-only archaeology or recovery.

The long-term topology after this handover is:

```text
109 / RTX4080  = GPU producer / capture execution plane
174-new / 2239 = ingest / catalog / CPU analysis plane
164            = long-term raw / parsed / feature / dataset storage plane
GitHub         = code / schema / manifest / receipt / audit control plane
old174 / 2233  = historical authority source only after closeout
```

This task implements the final old174 closeout requirements corresponding to Sections 4, 5 and 21 of the C16 AI workload migration/data-pipeline plan.

---

## 1. Branch and authority anchors

Repository:

```text
https://github.com/swayhrl/accel-sim-framework.git
```

Working branch:

```text
hrl/c16-old174-final-handover-to-2239-v0
```

Branch base / current future-use input authority:

```text
494ccc0f5e6be3bba71d35a58c8c61a60b61988a
ADOPTED_INPUT_AUTHORITY_V1_PASS
```

Important historical anchors that must remain separate and immutable:

```text
RTX3090 campaign closeout:
branch: hrl/vm-c16-g-3090-campaign-closeout-v0
commit: 649af1b9d65a774d4aa8c32a15f9b6f4da0dd4d9

RTX4080 clean R5:
branch: hrl/c16-4080-u5-u9-r5-clean
commit: b75f26674a09705659e770ab2134351414aa3c93
status: READY_FOR_MULTIMODEL_REVIEW
R4: MECHANISM_ONLY_NON_AUTHORITATIVE

Historical frozen-input recovery result:
commit: 4b5c2bb79b9e2e79bed8bef10365bf34be6f6cdd
status: HISTORICAL_FROZEN_INPUT_NOT_RECOVERED

Future-use adopted Llama input:
commit: 494ccc0f5e6be3bba71d35a58c8c61a60b61988a
status: ADOPTED_INPUT_AUTHORITY_V1_PASS
authority_type: FUTURE_USE_ADOPTED_INPUT_NOT_HISTORICAL_RECOVERY
```

No old174 closeout classification may rewrite these scientific states.

---

## 2. Required output pack

Create exactly one final review pack:

```text
docs/vm_tlb/review_packs/C16_OLD174_FINAL_HANDOVER_TO_2239/
```

It must contain at least:

```text
README.md
MODEL_AUTHORITY.tsv
INPUT_BINDING_AUTHORITY.tsv
HISTORICAL_TRACE_CATALOG.tsv
SCRIPT_INVENTORY.tsv
STORAGE_INVENTORY.tsv
MIGRATION_STATUS.tsv
OBSOLETE_AND_DIAGNOSTIC.md
OPEN_ISSUES.md
FINAL_HANDOVER_DECISION.json
SHA256SUMS
```

Additional machine-readable CSV/JSON helpers are allowed if useful, but do not replace the required files.

---

## 3. Scope: complete historical asset inventory

Inventory all C16 AI-workload-related assets available to old174, including at least:

```text
model assets
input assets
token bindings
runtime bindings
NVBit artifacts
NCU artifacts
Nsight artifacts
raw traces
parsed traces
scripts
receipts
manifests
temporary staging
historical recovery roots
exchange/returned bundles relevant to C16
```

For every significant group record, where applicable:

```text
absolute_path
size_bytes / total_bytes
file_count
important_sha256 or manifest/receipt hash basis
scientific_status
authority_level
source_authority
migrated_to_109
needed_on_174new_or_164
migration_recommendation
notes
```

Scientific status vocabulary is fixed to:

```text
FORMAL
MECHANISM_ONLY
DIAGNOSTIC
PRE_FIX
OBSOLETE
UNKNOWN
```

Do not invent status values without documenting the mapping.

Use existing closed receipts and the 3090 closeout inventory whenever possible. Do not re-read tens of GiB only to recompute a hash that is already authority-closed unless a mismatch or missing provenance specifically requires it.

---

## 4. MODEL_AUTHORITY.tsv

Must cover at least:

```text
Llama-3.2-1B
Qwen2.5-0.5B-Instruct
Qwen2.5-7B-Instruct raw
Qwen2.5-7B-Instruct-AWQ
Qwen3-8B
DeepSeek-V2-Lite
Qwen3-30B-A3B
```

Required columns:

```text
model
deployment
revision
model_root
asset_receipt
asset_receipt_sha256
total_bytes
scientific_status
authority_level
presence_old174
known_presence_109
needed_164
notes
```

Qwen3-30B-A3B must receive an explicit factual state. If incomplete, say exactly what is present/missing; do not infer completion from partial files.

---

## 5. INPUT_BINDING_AUTHORITY.tsv

Must explicitly reconcile:

### Llama

Historical status:

```text
S0 / B1 / T128 / Decode4 / TEXT
HISTORICAL_FROZEN_INPUT_NOT_RECOVERED
```

Future-use status:

```text
ADOPTED_LLAMA_S0_T128_V1
ADOPTED_INPUT_AUTHORITY_V1_PASS
```

Both rows must remain distinct.

### Qwen deployments

Audit the known 21 historical bindings:

```text
Qwen2.5-0.5B-Instruct × 7
Qwen2.5-7B raw × 7
Qwen2.5-7B AWQ × 7
```

Common scenario set expected from existing authority:

```text
S0_TEXT
S1_CODE
S2_CODE
S2_STRUCTURED
S2_TEXT
S3_TEXT
S4_STRUCTURED
```

Do not assume all 21 are present solely because prior handoff text says so; bind each to an actual path/receipt/hash or mark it unresolved.

### Qwen3-8B / DeepSeek-V2-Lite

Audit for any historical exact frozen input/token authority not previously found.

If none exists, retain:

```text
NO_HISTORICAL_FROZEN_BINDING
```

Do not run tokenizer or create historical bindings retroactively.

Suggested columns:

```text
model
deployment
scenario
binding_type
binding_id
receipt_path
receipt_sha256
payload_root
scientific_status
authority_level
migrated_109
future_use
notes
```

---

## 6. HISTORICAL_TRACE_CATALOG.tsv

Systematically classify old174 / RTX3090 historical traces and captures.

At minimum distinguish:

```text
known-good positive capture
negative control
failed capture
diagnostic-only
formal historical evidence
```

For each meaningful trace/run record:

```text
run_id_or_label
model
scenario
phase
instrument
gpu
source_path
bytes
sha256_or_manifest_basis
scientific_status
capture_class
superseded_by
needed_for_future_comparison
migrate_to_164
reason
```

Explicitly answer:

1. Which 3090 raw traces still have scientific value?
2. Which are recovery/diagnostic only?
3. Which conclusions are superseded by RTX4080 R5?
4. Which raw data are worth preserving on 164?
5. Which need only Git manifest/hash/receipt and do not need raw migration?

Use the accepted 3090 minimal comparison subset from commit `649af1b9...` as a starting point, not as a blind final answer. Preserve the existing recommendation against bulk-copying the ~75 GB recovery root unless new evidence justifies changing it.

---

## 7. SCRIPT_INVENTORY.tsv

Audit C16-related scripts under Git and old174 filesystem.

Classification vocabulary:

```text
REUSE
MIGRATE
REFERENCE_ONLY
OBSOLETE
```

Cover at least:

```text
model download / asset closure
input/token binding
runtime binding
NVBit collection
NCU collection
Nsight collection
trace parsing
migration/rsync
receipt generation
hash validation
sampling
analysis
```

Required columns:

```text
script_or_tool
absolute_or_git_path
in_git
latest_known_commit
classification
runtime_scope
hardcoded_host_or_gpu
hardcoded_path
secret_risk
recommended_action
notes
```

Special attention:

- identify scripts only present on old174 filesystem;
- identify scripts with AutoDL / RTX3090 / driver570 / `/root/share/c16_recovery_v3` hard-coded assumptions;
- identify scripts unsafe to reuse directly on 109 or 174-new;
- never commit secrets, private keys, tokens, or host-private credentials.

If a small source script is important for reproducibility and truly exists only on old174 filesystem, it may be copied into an appropriate Git path **only after** confirming it is not superseded, contains no secrets/host-private data, and its provenance is documented. Otherwise list it as a migration requirement instead of modifying it.

---

## 8. STORAGE_INVENTORY.tsv

Inventory major old174 C16 storage roots, including at least:

```text
/root/share/c16_recovery_v3
/workspace/c16_exchange (C16-relevant subsets)
other C16 data roots discovered during the bounded audit
```

Record:

```text
root
role
bytes
file_count
authority_content
formal_content
archive_content
temporary_content
already_backed_or_migrated
recommended_disposition
```

This is an inventory, not a cleanup task.

---

## 9. MIGRATION_STATUS.tsv

This is the explicit bridge to the future 109 → 174-new → 164 pipeline.

For each authority/data group classify:

```text
ALREADY_ON_109
ALREADY_IN_GIT
NEEDS_164_ARCHIVE
NEEDS_174NEW_CPU_ACCESS
SOURCE_RETAIN_ONLY
DO_NOT_MIGRATE
UNKNOWN
```

Required columns:

```text
artifact_group
source_old174
current_status
destination_role
recommended_destination
copy_required
copy_priority
hash_closure_basis
blocking_issue
notes
```

Do not actually bulk-copy data in this phase.

---

## 10. OBSOLETE_AND_DIAGNOSTIC.md

List old material that should not be used as current scientific authority, especially:

```text
pre-fix runs
failed/partial captures
mechanism-only R4 quantitative outputs where R5 supersedes them
obsolete temporary staging
known wrong-target/predicated-off/capability-limited runs
historical debug copies
```

For every significant class state whether it should be:

```text
retain_for_audit
retain_manifest_only
candidate_for_future_cleanup
```

No deletion is authorized here.

---

## 11. README.md mandatory questions

README must answer, explicitly and concisely:

1. What information/assets does old174 still possess that 109 / 174-new do not?
2. What has already migrated safely?
3. What exists only on old174?
4. What is still worth migrating to 164?
5. What historical results are obsolete or superseded?
6. What model/input/trace authority remains unclosed?
7. What is the actual Qwen3-30B-A3B state?
8. Does old174 retain any continuous C16 responsibility after this handover?

The final answer to #8 should normally be:

```text
NO_CONTINUOUS_C16_ROLE_AFTER_ACCEPTED_HANDOVER
```

unless a concrete blocker makes that scientifically unsafe.

---

## 12. OPEN_ISSUES.md and final decision

`OPEN_ISSUES.md` must list every information gap that may matter to 109/174-new takeover.

Do not count harmless historical clutter as a blocker.

`FINAL_HANDOVER_DECISION.json` must use exactly one top-level decision:

```text
OLD174_HANDOVER_COMPLETE
OLD174_HANDOVER_BLOCKED
```

If blocked, each blocking item must explain:

```text
what is missing
why it matters scientifically or operationally
whether it blocks 109 capture, 174-new ingest/analysis, 164 archive, or only historical archaeology
what evidence would close it
```

A missing historical artifact is not automatically a takeover blocker if a valid future-use replacement authority exists and historical status remains accurately documented.

---

## 13. Required final report back to ChatGPT

After commit/push, report:

```text
Branch
Commit
Review pack path
Final status
```

Then explicitly report:

1. `/root/share/c16_recovery_v3` complete directory/size/authority structure;
2. status of all required models;
3. Qwen3-30B-A3B actual state;
4. historical frozen inputs/bindings;
5. RTX3090 raw traces and scientific-value classification;
6. all formal artifacts still not migrated;
7. all important scripts that exist only on filesystem and are not in Git;
8. data safe to classify obsolete/candidate for later cleanup;
9. data that must be retained long-term;
10. any information gap that could block 174-new takeover.

---

## 14. Hard constraints

This phase is primarily CPU/read-only inventory and documentation.

Forbidden:

```text
NO GPU workload
NO CUDA/Llama/NVBit/NCU/NSYS rerun
NO tokenizer invocation
NO token-ID regeneration
NO new historical authority fabrication
NO change to RTX3090 frozen conclusions
NO change to RTX4080 R5 conclusions
NO rewrite of ADOPTED_INPUT_AUTHORITY_V1
NO deletion/move/rename/compression of existing evidence
NO bulk transfer to 109/174-new/164
NO source cleanup
NO secret/private-key/token publication
NO unrelated decouple-L1/L2 modifications
```

Allowed:

```text
read-only inventory
small-file SHA256
receipt/manifest reconciliation
CPU-only parsing
Git-history inspection
filesystem script inspection
review-pack generation
small reproducibility source commit only when explicitly justified and secret-safe
```

---

## 15. Stop condition

When the review pack is complete:

1. validate pack internal consistency;
2. generate `SHA256SUMS` for review-pack files;
3. ensure no pre-existing scientific evidence changed;
4. ensure no unrelated decouple-L1/L2 work changed;
5. commit;
6. push current branch;
7. stop.

Do not begin Phase B 174-new storage-root setup or any new 109 capture work from old174.
