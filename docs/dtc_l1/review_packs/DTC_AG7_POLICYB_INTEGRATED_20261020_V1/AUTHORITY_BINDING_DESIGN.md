# Source-prepared AG7 canonical BA/root authority adapter

`prepared_ag7/authority_dispatch.py` performs no import-time IO, launch, UUID/ledger mutation, adoption or signal. Only an explicit call of `exclusive_self_lock()` creates/flocks this new path: `/workspace/dtc-ag7-policyb-integrated-174-v1/AG_execution.lock`. It uses O_EXCL/O_NOFOLLOW/O_CLOEXEC, never opens an existing lock, writes an immutable real PID/start_ticks/boot/device/inode/registration-hash receipt, verifies its own kernel fdinfo WRITE FLOCK, and closes only its own fd. It neither removes the new receipt nor reads/writes/acquires an old lock. There is one finite controller instance; reuse/restart is rejected.

This is an **explicit new AG7 registration under the user's canonical BA `/root` authority**, not an inference from UID0, a task/path prefix, a CPU role or the historical AG6 release. The caller must be that canonical BA controller and implement the independently reviewed release-verification callback described below. Chat/task identity is an authorization input verified by the canonical controller/publication chain, not a Linux UID measurement; the adapter does not pretend `/proc` can attest a chat identity.

## Immutable registration without a SHA cycle

The root freezes a new JSON file under this new pack after all source changes are complete. The registration contains:

```json
{
  "schema": "DTC_AG7_BA_ROOT_AUTHORITY_V1",
  "goal": "DTC_AG7_POLICY_B_INTEGRATED_V1",
  "goal_commit": "244eea3d6ccde53bf4ceffdf16da9f25295147cb",
  "canonical_task": "/root",
  "authority_owner": "BA",
  "sole_dispatcher": true,
  "root": "/workspace/dtc-ag7-policyb-integrated-174-v1",
  "own_lock": "/workspace/dtc-ag7-policyb-integrated-174-v1/AG_execution.lock",
  "controller_entry": "ABSOLUTE_NEW_PACK_ENTRY.py",
  "role": {
    "name": "AG7_SOLE_CANONICAL_BA_ROOT_DISPATCH_CONTROLLER",
    "cwd": "/workspace/worktrees/accel-sim-iscas2027-dtc-ag7-policyb-integrated-174-v1",
    "executable": "/usr/bin/python3.10",
    "executable_sha256": "ACTUAL_INTERPRETER_HASH",
    "argvs": [["/usr/bin/python3.10", "-I", "-B", "ABSOLUTE_NEW_PACK_ENTRY.py", "@REG_SHA@"]],
    "source_sha256": {"ABSOLUTE_SOURCE_PATH": "ACTUAL_HASH"}
  },
  "frozen_authority_sha256": {"EXACT_W0_FROZEN_SOURCE_PATH": "EXACT_W0_HASH"}
}
```

The role source closure includes the exact entry, this adapter, the release-verifier's defining file, and `/workspace/dtc-ag7-policyb-integrated-174-v1/evidence/W0_SOURCE_BINDING.json`. The frozen-authority map must exactly equal that index and all indexed source hashes must match. Registration itself is excluded from its source closure, preventing a sourceSHA→registrationSHA→sourceSHA cycle.

After publication and exact independent GitHub readback, the actual launch argv is `/usr/bin/python3.10 -I -B ABSOLUTE_NEW_PACK_ENTRY.py ACTUAL_REGISTRATION_SHA256`. The root entry receives that SHA in its argv and independently binds it to the remote readback. The adapter validates the immutable registration SHA first, then resolves its single literal `@REG_SHA@` into **one exact argv**. Runtime matching never treats the placeholder as a wildcard.

## API and publication callback

Construct `ExplicitAG7Authority(registration_path, pinned_registration_sha256, release_verifier)` only inside the registered root entry. `release_verifier(path, sha)` must validate the exact published registration/blob, remote/fetched HEAD and tree, clean worktree and source closure. Its own defining source file must be in the frozen controller source closure. It returns:

```text
verified=true; remote_head=fetched_head; remote_tree=fetched_tree;
registration_blob=<40hex>; registration_sha256=<pinned SHA>;
clean_worktree=true; canonical_task=/root; authority_owner=BA;
goal_commit=244eea3d6ccde53bf4ceffdf16da9f25295147cb
```

The callback must perform or authenticate the actual publication join; an arbitrary manually asserted status is not evidence. It may reuse the already authenticated readback plus fresh source checks; no repeated network audit is required for each runtime resource sample. The canonical root owns this callback and the final scientific/resource/budget capability, so this adapter alone grants no fullsim authority.

Use `with authority.exclusive_self_lock(): review = authority.bind_review(local_ownership)` and invoke `snapshot, verdict = review(authority.owner)` for the existing paired preflight/runtime checks. `local_ownership` remains the original event-confirmed Ownership object; the adapter adds no process discovery/adoption or signal permission. `peer_provider` and an optional external launch-view callback have the same strict frozen semantics. This Goal defaults to no peer simulator/controller. Imports must resolve to the exact W0 frozen shared-authority, legacy-runtime and ownership source paths.

## Preserved authority checks

The adapter clones the frozen snapshot/review **function code unchanged** into fresh globals whose only alteration is `RAW = new AG7 ROOT`. This recognizes the new exact own-lock path and samples the actual new output filesystem; it does not mutate any frozen module globals or old files. All history, retired dispatcher checks, source-reviewed external controls, external project bindings, current process/FLOCK scanning, unknown control/lock failures, retired Core41 lock prohibition and SharedOwnership classification execute unchanged.

The full all-project snapshot is returned untouched for resource accounting. Only the existing exact-role classifier removes the fully bound current controller from its authority-classification view. No unknown control or lock is exempted. A former BA/AG6 lock is **not** recognized as this new own lock and remains subject to the original source/external/unknown checks; an active foreign/unknown old dispatcher still blocks. The new own FLOCK must appear exactly once in the actual all-scope snapshot, at the exact current controller PID/start_ticks and descriptor. Any cloned/inherited unexpected holder fails closed.

This is source preparation only. This subtask performed no lock acquisition, preflight, test, compile, signal, UUID/ledger work or simulator start. The root must close publication/source, actual authority/lock and all remaining scientific/resource gates before its separate SIMULATION capability can be released.
