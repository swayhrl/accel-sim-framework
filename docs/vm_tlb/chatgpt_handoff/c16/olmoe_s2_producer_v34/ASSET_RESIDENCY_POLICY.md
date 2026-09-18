# C16 model asset residency policy — V34 addendum

This addendum is authoritative for V34 asset handling and supersedes any earlier wording that implies a mandatory fresh transfer from node164 or mandatory model deletion at producer cleanup.

## Global residency policy

- **node164 is the sole model-asset authority.**
  - canonical model files and `MODEL_ASSET_RECEIPT.json`
  - immutable revision-root organization
  - all identity/hash closure originates from node164 authority

- **node109 may retain a long-lived active replica of the model currently under capture.**
  - the replica is not authority
  - it may be reused across NSYS/NVBit/NCU/trace/canary/formal capture work
  - it may be deleted later whenever space is needed, provided node164 authority remains hash-closed

- **174-new must not retain model-weight replicas.**
  - keep only source/worktrees/simulator binaries/limited scratch/small evidence
  - model authority is consumed directly from node164 when needed

## OLMoE V34 concrete handling

V32 previously used the exact local execution root:

`/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

V32 proved that this local replica, when present, exactly matched the accepted node164 receipt-bound 11-file runtime subset.

However V32 reported cleanup of its runtime/model subset at Goal end. Therefore V34 must **not assume** either presence or absence from historical evidence.

### Stage A — local-replica discovery

Before any model transfer, inspect exactly:

`/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

If present:

1. treat it only as a candidate replica
2. compare the exact required runtime subset against node164 `MODEL_ASSET_RECEIPT.json`
3. verify file set, size and SHA256
4. require no unexpected symlink/substitution
5. if all required files close, classify:

`PASS_REUSE_EXISTING_NODE109_REPLICA_HASH_CLOSED_TO_NODE164_AUTHORITY`

and use it directly. **Do not re-transfer it.**

If the path is missing or incomplete/hash-mismatched:

- do not repair it from local guesses
- remove/replace only the invalid replica/staging content as needed
- transfer the exact required runtime subset once from node164 authority using the established C16 transfer mechanism
- independently close size/SHA256
- classify:

`PASS_REFRESHED_NODE109_REPLICA_FROM_NODE164_AUTHORITY`

## Canonical node164 authority

Model:

`allenai/OLMoE-1B-7B-0125-Instruct@b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Canonical authority root:

`/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e/`

Node109 must never promote its local copy to authority.

## End-of-Goal cleanup rule

At V34 completion:

- clean transient runtime scratch
- clean tracer/profiler temporary output not needed by the review pack
- release `/data/c16/locks/c16_gpu_campaign.lock`
- verify no stale CUDA/profiler process
- verify expected GPU-memory baseline after model unload

But **do not delete the valid OLMoE model replica from node109 solely because the Goal ended**.

Retain:

`/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

as the active-model replica for subsequent OLMoE capture/profiling work, unless actual disk pressure requires cleanup.

Any later deletion must be treated as replica cleanup only; node164 remains the recovery authority.

## Review evidence

V34 should record:
- whether an existing node109 replica was found
- whether it was reused or refreshed
- exact node164 receipt SHA
- local required-subset file count
- size/hash closure result
- final retained replica path
- statement that node164 remains authoritative
