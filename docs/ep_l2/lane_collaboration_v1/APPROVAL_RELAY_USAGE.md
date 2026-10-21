# E2 approval relay

The foreground workflow is: E2 publishes a precise packet → the user approves → E2 transcribes that approval → E2 runs this relay. The user does not need to copy the resulting message into each lane. This script only delivers the recorded packet; it does not authenticate the human, interpret approval, grant new scientific permissions, execute a task or wake an idle Codex window. Existing science/resource/identity/qualification gates remain with their owners.

Only the original E2 worktree and branch can use it. Run from `/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1`; `coordination.Client` checks current worktree/branch/origin, and the relay additionally requires that exact original E2 root. The CLI, contract, producer/runtime, ledger, lease and active simulation are unchanged.

A packet is a small JSON object with exactly:

```json
{
  "schema": "E2_APPROVED_RELAY_PACKET_V1",
  "dispatch_id": "unique_lowercase_id_v1",
  "recipients": ["A2", "D"],
  "task_ids": ["EXACT_TASK_ID"],
  "scope": "Exact human-reviewed scope",
  "subject": "Short routing subject",
  "body": {"instructions": "Human-readable packet content; never executed by this tool"},
  "refs": []
}
```

The approval transcription is a separately published small JSON object with exactly:

```json
{
  "schema": "E2_APPROVED_RELAY_AUTHORIZATION_V1",
  "user_message_verbatim": "The original user words, transcribed exactly by E2",
  "approved_packet_path": "docs/ep_l2/path/to/packet.json",
  "approved_packet_sha256": "EXACT_64_HEX_PACKET_SHA256",
  "approved_recipients": ["A2", "D"],
  "approved_task_ids": ["EXACT_TASK_ID"],
  "approved_scope": "Exact human-reviewed scope",
  "approval_kind": "COORDINATION_RELAY_ONLY"
}
```

Use `COORDINATION_RELAY_ONLY` for the current process agreement. `USER_APPROVED_TASK_PACKET` is available for later precise approved packets; that label does not itself grant an application launch, mechanism change, experiment, budget or waiver. The script requires exact path/SHA, recipient array, task array and scope matches. It cannot determine whether a human approved the text or whether a task is scientifically eligible. An amended packet or approval needs a new unique dispatch ID; reuse with changed bytes is rejected.

Commit, push and remotely read back both documents using E2's existing publication process first. Each CLI argument is a standard collaboration ref containing exactly `repo`, full40 `commit`, repo-relative `path`, 64hex `sha256`, and `role`. The relay accepts only regular JSON files in this Framework repository's `docs/ep_l2/`, at most64KiB each, and proves both commits are ancestors of the actual remote E2 branch head. Packet refs are forwarded without reading large science data; receivers retain responsibility for consuming their evidence.

```
python3 docs/ep_l2/lane_collaboration_v1/approval_relay.py \
  --packet-ref '{"repo":"swayhrl/accel-sim-framework","commit":"FULL40_PACKET_COMMIT","path":"docs/ep_l2/path/to/packet.json","sha256":"EXACT64_PACKET_SHA256","role":"request_context"}' \
  --approval-ref '{"repo":"swayhrl/accel-sim-framework","commit":"FULL40_APPROVAL_COMMIT","path":"docs/ep_l2/path/to/approval.json","sha256":"EXACT64_APPROVAL_SHA256","role":"request_context"}'
```

Default is dry-run: reference/field checks only, no event, cursor, alias, dispatch journal or Git write. Add `--publish` after review to perform the already-authorized relay; no further approval cycle is introduced.

`--publish` uses a per-dispatch metadata lock, emits one immutable E2 REQUEST fanout with both packet/approval refs, and reuses E2's original `publish.py` to commit/push/read back the event. Only after that proof does it create byte-stable `E2_TO_<lane>_APPROVED_RELAY_<dispatchid>.json` pointers in the original three recipient directories: shared campaign `events`, shared campaign `inbox`, and `/workspace/ep_l2_ms20261019_shared`. It then publishes its own dispatch receipt. Old HANDOFF files and other lane state/ACKs are untouched. Serialize this foreground publication with E2's existing Git publisher; unrelated staged files are rejected.

Journal and immutable error records live under this owner's `dispatches/<id>/`. A retry reuses the exact event/dedup ID, resumes a commit whose push/readback failed, verifies or restores identical local aliases, and publishes the delivery receipt. Conflicting immutable files or changed approval/packet inputs are rejected; no old evidence is reset. `DELIVERED_NOT_ACKNOWLEDGED` means published bytes plus local pointers only. A recipient must later check at its safe boundary, consume, publish its own ACK/status and do its work under its own existing authority. There is no daemon, watcher, second controller, automatic retry loop or supported cross-window wake interface.
