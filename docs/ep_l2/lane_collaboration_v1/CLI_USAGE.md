# Foreground CLI

This script transports small messages. It never runs a message command, simulator, build, controller, resource lease, scientific validator or scheduler. It does not wake another Codex window, fetch, push, merge or reset. Existing experiments and lane publication workflows continue independently.

Run the published script from your own current Framework worktree. `--lane` must match that worktree's exact configured branch and GitHub origin. Absolute worktree paths in the contract are host references; F must explicitly pass its actual `--worktree`. This prevents accidental branch/owner writes; a shared Unix account is not cryptographic agent authentication. E2 must never enter another lane's worktree to forge its status or ACK.

```
python3 /path/to/published/coordination.py --lane D check
python3 /path/to/published/coordination.py --lane F --worktree /actual/current/framework check
```

`check` is read-only by default. `check --consume` records only returned events in this recipient's cursor; it emits no ACK and executes no work. Late unseen lower-sequence events appear in `late_unseen_preserved` and are not silently consumed. Repeated identical deliveries are deduplicated; changed bytes or payload under the same event ID/dedup key are rejected. Root must explicitly review a late/gap/conflict; no cursor reset is implied.

`emit --kind REQUEST|DELIVERY --to D ... --subject ... --dedup-key E2:... --body-json '{...}' --refs-json '[...]'` creates an immutable owner event, own cursor and same-host preview mirror. Optional `--work-key` and `--correlation-id` associate an existing science artifact across old/new channels; they do not replace scientific identity checks. DELIVERY requires at least one artifact ref. A body file, if used instead of JSON, must be inside the caller's own `docs/ep_l2/lane_collaboration_v1/` directory; arbitrary local files are rejected.

Each ref contains exactly `repo`, full `commit`, repo-relative `path`, exact blob `sha256`, and `role`. These commits identify scientific/work artifacts. They differ from the later transport event's publication commit. A newly emitted local event is **preview-only** until its own lane commits, pushes and remotely reads it back through its normal publication process.

To receive a cross-branch/host event, explicitly fetch the owner's branch through the existing workflow, then invoke:

```
python3 /path/to/published/coordination.py --lane D import-event --source-lane E2 --event-id OWNER_EVENT_ID --source-commit FULL_PUBLISHED_COMMIT --event-sha256 EXACT_EVENT_SHA256
```

`import-event` reads the exact event blob without checkout and preserves its original bytes only in the recipient's local inbox cache. It checks the actual remote owner branch with read-only `git ls-remote`, requires the source commit to be its ancestor using already present Git objects, and verifies the event SHA and recipient. Missing objects require an explicit fetch; no retry loop is created. It never creates another owner's event/status in this branch.

`ack` uses the same source arguments plus `--ack-status RECEIVED|BLOCKED|REJECTED` and an optional body/refs. It emits an ACK owned by the current lane and addressed to the original sender. No ACK means unacknowledged, not failed or offline. An ACK does not grant an experiment, budget, contract change or scientific acceptance.

`VALIDATED|APPLIED` additionally requires explicit `--confirm-reference-review`. For those statuses the CLI verifies exact SHA of all target and ACK artifact refs, limited to regular Git files under this Framework repository's `docs/ep_l2/` and declared text-metadata suffixes, within 16MiB total. APPLIED also requires an output evidence ref. This verifies message metadata, not the truth of an application result or whether a requested operation ran; the recipient remains responsible for its statement. Unsupported repo/path/large refs can still receive RECEIVED/BLOCKED; they must not be called automatically validated. `check` and `import-event` always report reference validation as format-only.

`status` reads only your own projection. `status --set --body-json '{"activity":"AT_SAFE_BOUNDARY","current_task":"...","blocking_dependencies":[]}'` emits a self-reported STATUS and updates only your projection. Replacing an existing changed status requires its exact `--expected-status-sha`; unchanged status is a no-op. Status is a timestamped declaration, never a remote process/lease heartbeat. Initial contract membership or E2 setup request cannot count as another lane JOINED; a real independently published self-status and ACK are required.

Bounds: 64KiB/event, 8000 body characters, 32 refs, 128 events/check, 512 scanned transport files, 1MiB cursor and 4096 cursor/outgoing entries. Scans fail closed before oversize reads. Unknown paths, traversal, symlink ancestors, nonregular files, immutable overwrite, owner mismatch and dedup conflict are rejected. Transport locks are per-lane metadata locks, separate from the original central registry/controller lock. No automatic archival, retry, cursor rollover or background polling is provided.
