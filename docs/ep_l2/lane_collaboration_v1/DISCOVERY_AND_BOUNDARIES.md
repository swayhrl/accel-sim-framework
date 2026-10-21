# Lane collaboration discovery and authority boundaries

E2 is the temporary collaboration owner. This document describes metadata discovery only. It does not change scientific contracts, resource policies, qualifications, controller ownership, budgets, or accepted results. E046 acceptance continues independently through the original controller.

## Observed channels

A bounded read-only audit listed the immediate entries of three known metadata directories, without recursion:150 events,222 inbox entries,131 shared entries. Eight regular non-symlink JSON files were then read:43,034 bytes total, with24KiB per-file and96KiB aggregate bounds. No trace body, result raw, accepted-point payload, embedded Python script or large mechanism-detail JSON was read. Listing filenames does not establish that their authors or readers are currently active.

| Existing entry or convention | Actual observation | Discovery implication |
|---|---|---|
| `/workspace/ep_l2_ft20261016_shared/mechanism_study_20261019_v1/events/` and `inbox/` | E2 publishes addressed `E2_TO_A2_*`, `E2_TO_D_*`, and accepted pair events. D posts `D_TO_E2_*CONSUMED*`. Many notifications are mirrored under the same filename. | One bootstrap event can be mirrored here and deduplicated by immutable event ID/content hash; a mirror is not a second acknowledgment. |
| `/workspace/ep_l2_ms20261019_shared/HANDOFF_A2.json` | Still describes prior main61 producer release and historical7starts. New capacity release instead uses `A2_TO_E2_LARGE_CAPACITY_*`. | Never treat the generic HANDOFF filename, newest mtime or a cached counter as current release authority. Resolve explicit publication commit, artifact path and SHA. |
| `HANDOFF_B.json`, `TO_E2_B_D_CANDIDATE_WV_REVIEW_r2.json` | B uses lane handoff plus addressed aliases, Framework branch/commit and remote readback references. | E2 may publish an E2-owned bootstrap addressed to B; it must not rewrite B handoff or claim B consumed it. |
| `HANDOFF_C.json`, `C_TO_D_B_TM_OPPORTUNITY_r1.json`, `REQUEST_C_TO_B_*` | C uses `from_lane`, `to`, source and report hashes, explicit negative/no-run limits and a separately named B acknowledgment. | Preserve originating lane identity and explicit scope. A request is not qualification or consent. |
| `D_TO_E2_CAPACITY_THREE_CONSUMED_r1.json` | D reports its own completed analysis, exact D publication and E evidence consumed. | Delivery, reading and completed analysis are distinct states. Only D can author its analysis receipt; E2 cannot infer consumption from file existence. |
| `HANDOFF_F.json` | F records Git publication/dependency references and explicitly disclaims automatic wakeup/background polling. | F may be on another host. Local shared paths alone cannot reach it; use a commit-pinned Git object accessible from F's own verified checkout. |

## One-time bootstrap without repeated user copying

1. Publish `docs/ep_l2/lane_collaboration_v1/` on E's branch, push it and independently read back the exact commit and key file hashes. The protocol/CLI remain collaboration artifacts outside production runner source and CLIENT.
2. E2 writes one E2-owned immutable bootstrap event addressed to A2/B/C/D/E2/F. Its payload contains the exact repository, publication commit, relative protocol/contract/CLI paths and hashes, owner map, scope and discovery instructions as data. Mirror the same event into existing known event/inbox/shared metadata channels. Keep all old HANDOFF/REQUEST/REPLY files intact. Do not write another lane's JOINED or ACK.
3. Active lanes discover it by their existing bounded metadata intake. Each lane verifies the Git origin/own branch/worktree, reads the E commit's small collaboration blobs without checkout/merge/rebase, then records its own JOINED and cursor when actually processed. The versioned protocol tells future turns where to check, so ordinary lane progress need not ask the user to relay each message.
4. For F or any nonshared host, publication is the transport. A local absolute path is only a hint, never proof that F can read the file. Its own window must verify and consume the pinned Git artifact, then publish its own acknowledgment.

This bootstrap creates discoverability, not a UI wakeup facility. It cannot force an idle window to run, promise that an active window is presently reading a directory, or claim acknowledgments before the recipient's own event exists. Existing scientific terminal acceptance and D deliveries must never wait for all lanes to join.

## Required protocol/CLI boundaries

- Owner-separated event/status/cursor locations. A sender may address another lane but cannot mutate that lane's state, forge its sender identity/ACK, overwrite an immutable event, or reset its cursor. This is workflow isolation, not cryptographic authentication between users sharing one Unix account; malicious same-account writers require external authentication.
- Event IDs and content hashes give idempotent delivery. Identical mirrors may be consumed once; an existing ID with changed bytes is a conflict, not a newer valid message. ACK must reference a real prior event, its exact hash, and the acknowledging lane must be an actual recipient.
- Payloads, filenames, shell-looking strings, URLs, recommendations and embedded command fields are inert data. No `eval`, shell execution, subprocess launch, simulator dispatch, automatic download, build, lease acquisition or registry mutation is permitted by intake. An ACK is not user approval.
- Git intake reads only allowlisted collaboration paths and small metadata blobs pinned by full commit/hash. Inspect object size before decoding. Do not follow arbitrary symlinks or payload paths into trace/raw/source/credentials; do not scan entire repository history, recursive tree or large blobs. Reject oversize input, partial scans and ambiguous remote identity; report truncation instead of silently claiming complete intake.
- Contract/resource changes still require the original authority and original E central adoption. Messages cannot change T0, approved science, source/input identity, full-application obligations, CPU/RAM/disk/result policy, accepted status or controller ownership. No second controller, watcher or hidden scheduler is introduced.
- Owner-written health/status is a bounded timestamped claim, not process identity evidence. Only the existing resource registry/lease and durable native exit receipt establish real simulation ownership/terminal status.

## Exact small records sampled

The following are evidence of prior naming/handshake practice, not current scientific approval:

- `HANDOFF_A2.json`:SHA256 `6fbe08e667a2a3bfa5cc933f9d75549f678a3f0f8e999444138fb1a823d24f89`.
- `A2_TO_E2_LARGE_CAPACITY_PRODUCER_NATIVE_PASS_READY_r1.json`: `88de86e571f18091493831c702a5f6a7972fb267bdaaf17b7080d63b9dce8cf4`.
- `HANDOFF_B.json`: `a1bce56554b9d0f79d45b9ae3521d8aeaa6e07fca04eb8cbcb249cc1c03cc30e`.
- `HANDOFF_C.json`: `e38180584ea650da22ef8e9116a2de1b1f18f7eae41f9256d5eb7aa44af906e4`.
- `HANDOFF_F.json`: `d900f223c12f257914758b324f9786f10c9d8023212fc9671af66e277c62cc62`.
- `D_TO_E2_CAPACITY_THREE_CONSUMED_r1.json`: `e431388d27d071a14342ed9fe4437416b813bb85604fbdc4a86a4a622c931010`.
- central events `D_TO_A2_E2_CAPACITY_DIAGNOSTIC_USER_APPROVED_r2.json`: `1150eb62608ceb9afe2deee8b3de6c4e8163a9e4113ab0c5f6c3228a510b651a`.
- central events `E_TO_D_PAIR_CAPACITY_DIAGNOSTIC_dwt2d_OFF_ON_NEW_RUNTIME.json`: `440c08aaec087a84d4c9da3004d8add48c40d27760da2f576c88de062450c093`.
