# Project acceptance and recovery contract

| Project / class | Target acceptance | Source action / reason |
|---|---|---|
| EP-L2 S01/S02 historical .vvp | Only exact frozen inventory and source-owned atomic READY; <=512MiB, 30MiB/s | Source owner alone rechecks the existing V5 permitted release class |
| New EP-L2 cold data | Owner COLD_COPY_OK, COLD state, full producer/config/identity/hash/reader/recovery metadata | SOURCE_KEEP; target integrity is not release permission |
| DTC-L1 cold data | Same rules, and explicit source owner/active-run boundary | No manifest received; source scope UNKNOWN, SOURCE_KEEP |
| Other qualified project cold data | Explicit owner/retention, safe project and globally unique batch ID, regular single-link files and exact reviewed manifest | SOURCE_KEEP; no permission inferred from project name |
| Current experiment output, trace authority, unique scientific input, credentials or Git | Excluded from automatic receiver | SOURCE_KEEP; dedicated human review required for any separate manual backup scope |
| Legacy 36 Git-pack backups | Existing byte-verified archives indexed without recopy | SOURCE_KEEP; old staging route is not retrospectively V4 compliant |
| Sparse/symlink/multi-link or >512MiB files | HOLD for an explicit supported plan/adapter | No silent dereference, metadata loss, enlarged limit or partial-upload verification |

The source window is the sole global candidate and release authority. Target does not decide DTC-L1 ownership, inspect its source directories or issue run/cleanup instructions to research users. Rejected/unknown quantities remain UNKNOWN, not invented zero-byte inventories.

A general READY uses `STORAGE_OPS_V6_SOURCE_BATCH_READY`, fixed roots, a pinned `source_receipt_commit`, project, globally unique batch ID, source root/namespace/mount, owner COLD_COPY_OK, SOURCE_KEEP retention, COLD asset state, an explicit false unique-original-input flag, source commit/config/producer/run keys, rehydration recipe, source stability and reopened bridge hash declarations, counts and exact file records. Each record preserves canonical source/relative/bridge/destination paths, logical/allocated bytes, dev/inode/nlink, mtime/ctime, UID/GID/mode, empty reader/in-flight references and source/bridge SHA256. Recipes are data; the receiver never executes them.

The explicit V5 S01/S02 adapter accepts their narrower legacy metadata only when all exact source identities/hashes match the frozen 102-file inventory. It does not claim missing source config/UID/ctime values are known. New projects cannot use that exception.

Recovery drills copy archive bytes to a separate path under the same authorized root and close/reopen/hash the restored file. Receipt fields separate primary archived bytes, exact sampled/full restore scope, independent source allocated bytes released and each source df before/after window. A sample never advances the whole batch to RESTORE_VERIFIED. Real scientific offload additionally requires the project owner's complete recovery/metadata/link/runner-lookup validation and separately applicable release approval.

Indexes are immutable snapshots inside `infrastructure/indexes`, grouped by project and batch. Current source action evidence is an explicitly pinned source-repository commit and raw receipt SHA256. Source file identities/digests and the referenced target receipt are checked before accounting for release. The sum of independent df windows is reported as observations, not a promise of the current filesystem free space or build admission. 48GiB floor, 2GiB build growth, RAM/CPU/simulation and Share gates remain unchanged.
