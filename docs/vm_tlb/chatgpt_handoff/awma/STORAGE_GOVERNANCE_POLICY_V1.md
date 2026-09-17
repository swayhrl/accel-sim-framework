# AWMA Storage Governance Policy V1

Date: 2026-09-17
Ownership: ChatGPT
Status: ACTIVE POLICY

## 1. Core rule

AWMA uses three distinct node roles:

```text
109 / RTX4080
  = GPU producer and short-lived local staging

174-new
  = simulator / analysis / coordinator
  = NOT a durable large-data store

164
  = durable authority for large AWMA data
```

The durable root is:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
```

Large artifacts must not depend on 174-new local disk for long-term retention.

## 2. Data placement

Durable on node164:

- model assets and model receipts;
- frozen inputs / token bindings;
- NSYS reports and full launch inventories;
- NCU reports;
- NVBit / C16WARP1 raw;
- simulator-native trace bundles / traceg;
- large simulator raw output;
- cycle-level diagnostic timelines;
- large parsed/feature datasets;
- manifests, receipts and durable catalogs associated with these artifacts.

Git / local worktrees may contain only:

- source code;
- schemas;
- small manifests / receipts;
- TSV/CSV/JSON summaries;
- review packs;
- raw-data indexes and hashes.

174-new may use local scratch only for small or temporary working files. Any large temporary working copy is non-authoritative and may be cleaned after node164 hash closure.

109 may stage raw data locally while the GPU tool is running. A producer-side local copy must not be deleted merely because a transfer command returned success.

## 3. Existing accepted paths are immutable provenance

Do not physically reorganize or rename already accepted historical paths merely for layout cleanliness.

Examples include the accepted Q05 simulator-native producer path under:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/raw/
```

and already published analysis/census artifacts.

Existing durable paths are indexed in the storage catalog as legacy/current durable authorities. New governance does not rewrite historical provenance.

## 4. New publish lifecycle

For new producer captures, the logical lifecycle is:

```text
109 local staging/<RUN_ID>
    -> local finalize: manifest + size + SHA + terminal closure
    -> ready/<RUN_ID>
    -> transfer to node164 partial namespace
    -> independent destination size/SHA verification
    -> no-overwrite admission / rename to durable namespace
    -> durable receipt + ACK
    -> producer copy marked transferred
    -> later explicit cleanup policy may remove the producer copy
```

Recommended partial namespace on node164:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/captures/inbox/<RUN_ID>.partial
```

Recommended durable simulator/native capture namespace remains compatible with existing AWMA practice:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/raw/<RUN_ID>
```

Do not change an existing accepted producer path unless an execution-stage audit proves that a path change is safe and all downstream consumers are updated explicitly.

## 5. Required data-plane properties

The producer-to-durable path must support:

- resumable transfer;
- `.partial` state;
- no-overwrite admission;
- source and destination byte counts;
- SHA256 closure;
- independent destination rehash;
- durable transfer receipt;
- explicit ACK;
- quarantine for failed/mismatched bundles.

`rsync exit 0` alone is not scientific admission.

## 6. Storage data-plane qualification canary

Before new large captures rely on the new governance path, perform one deterministic 1-2 GiB canary:

```text
109
 -> hrl174new
 -> node164 .partial path
```

The canary must demonstrate:

1. partial/resume behavior;
2. final size equality;
3. source SHA256 = destination SHA256;
4. promotion/rename into a final test path on the same durable mount;
5. read-back SHA256 after promotion;
6. cleanup of the test fixture only after all checks pass.

Success marker:

```text
AWMA_164_DATA_PLANE_QUALIFIED_V1
```

Failure of this canary blocks new large formal capture publication, but does not invalidate existing accepted data already on node164.

## 7. Storage catalog

Maintain immutable per-artifact or per-run catalog entries and deterministic snapshots.

Recommended logical layout:

```text
catalog/
  entries/
  snapshots/

provenance/
  storage/
```

Every indexed large artifact should record at least:

```text
artifact_id / run_id
scientific_status
artifact_type
model / revision
scenario / phase / target when applicable
producer node
source path
durable path
size
sha256 or manifest hash root
Git report/review-pack reference
retention class
```

Suggested retention classes:

```text
AUTHORITATIVE
DURABLE_ACCEPTED
WORKING_COPY
LEGACY_DURABLE
QUARANTINED
SAFE_TO_DELETE_AFTER_ACK
UNKNOWN
```

No automated deletion is authorized by this policy.

## 8. Current artifacts that must be indexed first

At minimum index without moving:

1. accepted Q05 simulator-native trace bundle;
2. Q05 natural-completion simulator raw evidence;
3. accepted full S2 NSYS/kernel-launch inventory;
4. current Qwen2.5 frozen model/input authority references;
5. new side-lane captures created after this policy is activated.

Do not recursively rehash tens of terabytes of unrelated historical storage. Reuse existing accepted manifests/hash ledgers where they already close the artifact identity.

## 9. Cleanup policy

This stage may generate a cleanup candidate list, but may not delete accepted scientific data.

A producer or analysis copy can be considered for later deletion only when:

```text
node164 durable copy exists
+ independent destination hash verification passed
+ catalog entry exists
+ scientific owner/status is known
+ explicit cleanup stage authorizes deletion
```

The only file this governance stage may delete automatically is its own storage-canary fixture after verification.

## 10. Relationship to GPU side-lane capture

Storage governance is the gate before new large side-lane captures.

Once `AWMA_164_DATA_PLANE_QUALIFIED_V1` is reached, node109 may use the same publish protocol for newly authorized selected-kernel captures.

Storage qualification does not authorize arbitrary kernel capture; capture scope is defined separately by the current `CODEX_NEXT_STAGE`.
