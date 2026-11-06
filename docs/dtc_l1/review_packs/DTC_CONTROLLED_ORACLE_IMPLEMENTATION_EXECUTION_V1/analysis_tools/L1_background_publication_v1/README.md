# Oracle background read-only watch and Main-enabled publication candidate

This is an engineering candidate only. It is not enabled, is not running in the background, has not written the review worktree, and has executed zero actual Git pushes, science registrations or models. Main owns final enablement after its first publication. No Core/runtime source is changed.

## Interface and scope

The watcher imports the exact SHA-pinned S live consumer and calls snapshot(native_base,matrix_path,out_dir) into its own derived directory. It reads the frozen128 PLAN slots/32 complete input identities. S owns scientific interpretation, result/strict/archive/restore validation and same-binary OFF pairing; the watcher never weakens it, rewrites original states, invents counters or substitutes historical DH-P0. It retains full source RESULT path/SHA/UUID, exact status/classification, un-clipped S/H (including negative H), missing/HOLD/negative states and per-kernel derived reports. Outside3/unresolved7 do not enter the population.

A source RESULT closed fingerprint changes only on actual closed-result identity/state bytes, not generated timestamps, PLAN rows or polling. With zero actual results the watcher only initializes PLAN/current-scope files. With no publication-enable file it always remains collect-only and executes no Git command. With an enable file, it publishes only if an actual closed fingerprint is new and at least1800seconds have elapsed since the last successful publication. The first actual closed update can publish immediately after Main's initial commit. No periodic empty commits are made. Derived files are bounded32MiB each/128MiB per publication payload; exceeding that holds Git publication for Main to choose a thinner report layout and never changes scientific execution or results.

## Unique coordination and Git discipline

The shared nonblocking flock is A/control/publication_v1/LOCK; Main's first publication uses the same lock. The enable file must explicitly acknowledge first_main_publication_complete and its40-digit commit SHA, exact branch and review root. Current local HEAD must equal the remote branch head and descend from that first commit. Divergence holds publication; it never resets, pulls, rebases, overwrites or force-pushes.

Git uses explicit reciprocal linked-worktree git-dir/work-tree and only GIT_INDEX_FILE=A/control/publication_v1/BACKGROUND_INDEX. It read-trees current HEAD after Main's initial publication, adds only the immutable publisher snapshot files plus publisher-owned live_results/LATEST.json, and asserts the cached path set contains exactly those files. The contaminated default worktree index (including preexisting staged deletions) is untouched. It does not use add-all, restore, reset or forced push. Explicit -f applies only to approved report paths to overcome repository CSV ignores. A narrow .gitattributes disables text/LFS transformations inside each frozen payload.

Remote receipt sequence is push -> ls-remote exact commit -> fetch exact branch -> show FETCH_HEAD:exclusive snapshot MANIFEST bytes. Readback receipts stay outside Git under the watcher state directory and do not self-reference a commit. A Git/push/readback failure holds publication and preserves any created local commit; Main must reconcile it. There is no automatic duplicate commit or destructive recovery.

## Main invocation after review

Fill MAIN_ENABLE_TEMPLATE.json into a separate Main-owned enable file only after Main's first commit/push/readback. Pin S's final implementation SHA. Suggested call:

```text
python3 watch_publish_oracle_results.py --base <A> --native-base /root/data/dtc_controlled_oracle_20261106_v1 \
  --matrix <A>/control/authority/FUTURE_DH_ORACLE_MATRIX.json \
  --consumer <A>/agents/S_live_result_consumer_v1/<consumer.py> \
  --consumer-sha256 <frozen S implementation SHA> \
  --state-dir <A>/control/publication_v1/background_state \
  --publication-enable <Main owned enabled config> --watch --poll 60 \
  --stop-file <A>/control/publication_v1/STOP_BACKGROUND_WATCH
```

Omit --publication-enable for read-only initialization. Stop-file is a publisher-only control; no model or dispatcher is stopped. Polling/lock/error behavior has no scientific budget or model effect.

## CPU mock evidence

28 checks use temporary MOCK_NOT_SCIENTIFIC reports and an in-process fake Git runner. They cover complete32/128 scope, zero-result/no-Git initialization,1800second gating, duplicate/no-new suppression, malformed/duplicate identity rejection, negative-H retention, source path/SHA retention, unique lock exclusion, default-index preservation, explicit narrow staging, first-publication acknowledgement and remote manifest readback command order. A recorded fake push command is not executed. A real collect-only interface call with S SHA bc724d78767be34e5ddb32c42c89ca2b96906ae35bd8f4e7daa570a931565e16 sees128 CPU_DRAFT_UNREGISTERED rows across32 inputs, closed0, all cycles/S/H null. No publication enable was supplied, no Git command ran, and no background watcher was started. Real publisher first-commit integration remains Main's gate.
