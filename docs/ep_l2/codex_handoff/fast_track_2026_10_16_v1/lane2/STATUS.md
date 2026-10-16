# Lane 2 — Clean/dirty TVD

Status: **IN_PROGRESS — independent TVD module and producer-linked directed verification**.

- Coordination authority: `6c136e2a56a008695f8c8b815723bf8f1a760db9`.
- Node: `huangrulin-174`.
- Framework worktree: `/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane2-v1`.
- Core worktree: `/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane2-v1`.
- Both execution branches: `hrl/ep-l2-ft20261016-lane2-v1`.
- Framework engineering parent: `54fbc7869f4e40b6b48dc936b527fee85dd46406`.
- Core engineering parent: `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e`.
- Duplicate check: no Lane 2 local/remote branch, worktree, or matching active process existed at startup. Lane 1 has a separate Core worktree.
- Read: all five required frozen handoff files plus historical roadmap, charter, current mechanism sequence, headroom plan and final baseline decision at the evidence-index commits.
- Completed: isolated worktrees; frozen contract/source archaeology.
- Executing: bounded shared WAD/TVD state machine, sector-exact read/promotion and dirty lifecycle design, producer-linked data/version tests.
- Dependency: Lane 1 exact published payload/WAD/interface contract not yet consumed; no matching release known at startup.
- Next: freeze clean module and tests, validate and publish clean subset, continue dirty forwarding/retention, consume exact Lane 1 receipt at stage transition.
- Formal experiments: NOT_RUN; Lane 5 quota/registry required. No active runs.
- Review pack: not produced yet. No clean or full TVD readiness claim.

## Clean module checkpoint

Public ABI consumed: Framework `cb7d92e4edde97e81520cfdd00762dfe81ee9b20`, Core `4fb91f0a5c9eb3bf494a154ea1f24b9a56b34617` (cherry-pick with provenance). Clean module source `5267347de7d3244dd68a067fc2120a9cf0c55efb`; four scenario groups pass normal and ASan+UBSan. Pack: `docs/ep_l2/review_packs/FT20261016_LANE2_CLEAN_MODULE_r1/`. Standalone directory + historical production bank arbiter only; real l2_cache producer integration remains pending. Now continuing dirty retention/forwarding and version tests. Lane 5 HOST_BUDGET consumed at `cc97ee2ad9feb4ff57482cb7d826a53a3a4d07a0`; new results root follows it.
