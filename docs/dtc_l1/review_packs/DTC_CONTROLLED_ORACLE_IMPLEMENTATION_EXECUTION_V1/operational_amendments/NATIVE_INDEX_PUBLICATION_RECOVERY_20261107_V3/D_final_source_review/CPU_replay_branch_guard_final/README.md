# Unified publisher V3: native index and bounded transaction recovery

Independent source candidate; not started by its author. No real Git command, remote operation, production lock/index change, science registration/model start, owner/dispatcher action or service stop occurred during preparation. The40-case CPU report uses explicit fake Git/process backends and a disposable native CPU-only lock/index directory. The old V1/V2 sources and historical leaves remain unchanged.

## Small operational changes

V3 loads exact reviewed V2 source and updates the emitted watcher implementation SHA to this V3 file. It preserves common PUBLOCK, Main enable, fixed128 scope, scientific statistics, explicit narrow staging, no-overwrite leaves, standalone index, original remote fetch/manifest checks and30-minute publication cadence.

Main must explicitly supply `native_private_index` under `/root/data/dtc_oracle_publication_v3/`, with filename `CLEAN_UNIFIED_BACKGROUND_INDEX`. It must be a nonsymlink native-ext4 path on the same device as `/root/data`. The new private index is created by original read-tree from the current verified HEAD, not copied from V2 or the default index. V2's index and quarantined lock are untouched. Git auto-maintenance/gc are disabled only per publication command to avoid untracked background maintenance. Bounded timeouts are commit900 seconds, index metadata operations300, network180 and other read commands120. Timeout outcomes remain uncertain until reconciled.

Each publication records its exact precommit HEAD, immutable intended leaf/manifest, and narrow expected paths. Git write command intent/outcome and incomplete-cycle errors are preserved. On first cycle or uncertainty, while holding the original common PUBLOCK, V3 compares actual local HEAD and remote SHA and reads the committed `FETCH_HEAD` LATEST/manifest/scope objects. It never trusts working-tree LATEST. It checks fixed authority/matrix/128 scope, approved current/prior watcher and bridge hashes, manifest/scope hashes and source RESULT identities/roots. An already-published108 checkpoint can be adopted even if the current consumer later sees127: no new commit or reset is performed for that checkpoint. Adoption is a forward WATCH_STATE record; the conservative30-minute timer begins at verified adoption.

If a sole pending local commit differs from the remote, V3 only completes its push when its own journal proves the exact single parent, expected manifest and exact narrow changed paths. It pushes that existing SHA without force, then reads it back. Unknown divergence or ambiguous provenance is HOLD. No commit is replayed simply because its command timed out.

## Private abandoned-lock handling

Only the exact new caller index is eligible, inside the Main-approved native path. Same PUBLOCK ownership must be visible in `/proc/locks`. Two independent process scans must show no matching GIT_INDEX_FILE/related Git writer and no open index/lock FD. Unreadable process state, a recent lock, an active writer, symlink/hardlink, changed inode/content/index fingerprint, or any uncertainty is HOLD. Environment contents are never recorded; only match decisions/process counts are retained.

After stable dev/inode/size/mtime/ctime/SHA checks, the lock is atomically renamed on the same native filesystem into `abandoned_lock_quarantine`; it is never deleted. The true164 state directory receives preserved intent/proof/receipt metadata, and any reappearing lock stops recovery. Common PUBLOCK serializes all authorized publication writers; two static scans do not claim to stop an unauthorized future writer outside that lock.

## Main caller fields and CLI

`UNARMED_V3_ENABLE.template.json` retains the exact previous Main enable schema with `enabled:false`. Main supplies a new enabled release file after D review and actual source-pin checks. Four additions are `native_private_index`, `caller_bindings:{path,sha256}`, `approved_consumer_bridge_sha256`, and `approved_prior_watcher_sha256`. The current V3 hash is accepted as the running pinned source; older watcher hashes must be explicitly listed. The caller bindings still pin the already-reviewed dual-root consumer and actual new operational source-forward references. They cannot authorize a science model.

Use the existing full CLI with executable `unified_watch_publish_v3.py`; retain the same approved bridge and its SHA, `--native-base` pointing to the caller binding JSON, fixed matrix and Main-enabled worktree config. Use a new `--state-dir`, for example `A/control/publication_unified_v3/background_state`, and a new stop-file owned by Main. `--watch --poll60` remains optional; without `--publication-enable` collection has no Git side effects. Main must normally stop a superseded publisher and check release/source pins before starting V3; this candidate does not do that.

The incident evidence supports avoiding a large private index over sshfs and preserving timeout ambiguity. It does not establish a precise FUSE function or a scientific performance issue. All experiments, cycles, statistics, traces, raw results and paper v0.23 remain unchanged.


## Minimal branch-guard forward revision

The original V3 source/MF remains unchanged. This revision restores the original actual-branch guard on the reconciliation path: immediately after confirming common PUBLOCK, `symbolic-ref --short HEAD` must equal the fixed publication branch before any quarantine, continuation push or remote adoption. Configured branch alone is insufficient. Wrong-branch CPU cases prove zero push, unchanged WATCH_STATE and no quarantine. No timeout, index, statistics, dispatcher, signal/process-group or scientific route is added.
