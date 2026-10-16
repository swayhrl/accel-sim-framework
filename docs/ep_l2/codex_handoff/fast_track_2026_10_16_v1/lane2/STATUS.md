# Lane 2 — Clean/dirty TVD

Status: **MODULE_REVIEW_READY / DEPENDENCY_PENDING_FOR_PRODUCTION_INTEGRATION**. Full TVD is not complete.

- Node: `huangrulin-174`.
- Coordination authority: `6c136e2a56a008695f8c8b815723bf8f1a760db9`.
- Framework worktree: `/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane2-v1`.
- Core worktree: `/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane2-v1`.
- Both branches: `hrl/ep-l2-ft20261016-lane2-v1`.
- Framework engineering parent: `54fbc7869f4e40b6b48dc936b527fee85dd46406`.
- Core engineering parent: `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e`.
- Core module production source: `56abbacc1192d68995e78561899719649f838079`.
- ABI consumed exactly from Lane 1 Framework `cb7d92e4edde97e81520cfdd00762dfe81ee9b20`, Core `4fb91f0a5c9eb3bf494a154ea1f24b9a56b34617` (provenance-preserving cherry-pick).
- Host budget consumed from Lane 5 Framework `cc97ee2ad9feb4ff57482cb7d826a53a3a4d07a0`; only single-process light tests.

## Completed

Startup duplicate/process/worktree checks found no Lane 2 task; isolated both repositories and left other lanes untouched. Read full frozen contracts and required historical sources. First published clean module subset at Framework `7697ed6b81d39d5eee8c005dd695553d783537b5`, Core `5267347de7d3244dd68a067fc2120a9cf0c55efb`; immutable clean pack remains retained. Then added dirty lifecycle and full-directory promotion, with seven scenario groups passing normally and under ASan+UBSan.

The module has one bounded 128-entry combined WAD/TVD address authority, exact sector masks, extra-cycle lookup, read leases, same-handle promotion, true lower-accept/set_done distinction, nonreclaimable pending/inflight WB and retention slot-cycle accounting. No new payload allocator/data array. Source patch and metadata/state/counter contracts are published.

## Required next executable source

At the bounded stage-transition check, Lane 1 remote Framework remains cb7d92e4 and published Core interface is 4fb91f0a. V1 publishes identity and describes hooks, but allocator reserve/pin/role transfer and WB/Tag producer methods are not implemented in that published source. Integrating by inventing another allocator or address table would violate the common contract.

Next action upon an exact Lane 1 executable release: adapt once to its source; wire real selected victims, shared WAD authority, allocator pins, extra-cycle read service before WAD denial, same-handle tag promotion, actual memport push/set_done and response/epoch cleanup. Run producer-driven data/version tests listed in PRODUCTION_GATES.csv. Lane 1 remains final public Core integrator; Lane 5 owns formal quotas/run keys.

No active runs; no formal experiments; no runtime clean/dirty/full TVD readiness or speedup claim. This status does not promise background work.

## Evidence

- `docs/ep_l2/review_packs/FT20261016_LANE2_CLEAN_MODULE_r1/`
- `docs/ep_l2/review_packs/FT20261016_LANE2_DIRTY_MODULE_r1/`
- `INTEGRATION_REQUEST.md`
