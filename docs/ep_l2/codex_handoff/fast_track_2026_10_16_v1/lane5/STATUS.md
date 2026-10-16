# EP-L2 Fast Track — Lane 5

Status: **TOOLING_TESTED / DEPENDENCY_PENDING**. This is an executed tooling and
historical directed-validation checkpoint, not a plan-only report or B16 release.

Node: `huangrulin-174`.
Framework: `/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1`, branch
`hrl/ep-l2-ft20261016-lane5-v1`.
Tooling production source: `de8fe21d9598660e40da8486e48f2d46acee4582`.
Historical Core tested: `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e`.
No Core execution branch was created; production Core has not been modified.
Coordination: `6c136e2a56a008695f8c8b815723bf8f1a760db9`.

## Delivered and executed

- Canonical shared registry, permanent flock, atomic JSON and host budget live at
  `/workspace/ep_l2_ft20261016_shared/`; CLIENT_CONTRACT.json points to frozen
  tooling. All lanes share two long-simulation slots, 8 CPU units, 32 GiB reserved
  memory; scan is exclusive. Build lease is executable, maximum -j4. Existing
  other-project tasks are untouched.
- Frozen runner snapshots binary/config, hashes complete kernel trace content,
  rejects unmatched budget/feature/ideal vectors and requires production-driven
  independent qualification. It retains failed/duplicate/incomplete evidence and
  never treats software exit as hardware resource drain.
- Independent ordered 32B sector/version oracle and event/resource/WB closure
  validator. Ordinary data fixtures do not claim atomic or concurrent production
  semantics; adapters and stage-specific production validation remain required.
- 39 Python tests PASS, including 8-process single-key race, cross-lane reuse,
  quota/scan exclusion, content changes, malformed evidence and lifecycle errors.
- 3 historical Core directed scripts PASS (4 C++ executables: payload store,
  sector lifetime, banked store, descriptor MSHR), under a shared build lease and
  private TMPDIR. These are HISTORICAL_PRODUCTION_DIRECTED_NOT_B16.
- 13-workload inventory: 13/13 list hashes match history, all referenced kernel
  files exist. Input scale and epoch identity remain explicit. No 80-row rerun.
- Machine-readable validation, empty formal result schemas, failures/pending,
  resource movement, source manifest, raw-log index and Lane 6 metric contract.

## Dependencies consumed

Lane 1 publication `cb7d92e4edde97e81520cfdd00762dfe81ee9b20`:
public interface V1/Core source `4fb91f0a5c9eb3bf494a154ea1f24b9a56b34617`;
BASELINE_CONTRACT status PARENT_IDENTIFIED_RUNTIME_VALIDATION_PENDING,
runtime_ready=false, binary/config SHA=null. Interface is consumed as a contract,
not a runtime release. Exact Lane 2/3/4 receipt snapshots are in SOURCE_MANIFEST.

## Scheduling / next executable transition

Lane 5 owns B16_BANKED baselines shared with Lane 4. Lane 4 owns its ideal
runs and uses this same registry/client. RUN_ASSIGNMENTS.json publishes the
five-workload B16/U_WB16 queue without fictitious run keys. It is not an active
run claim. TVD/RO roll in after individual qualification; FULL after interaction.

The next dependent step requires Lane 1's frozen runtime-ready receipt, actual
B16/U_WB16 binary/config and production-driven data/lifecycle evidence. Normalize
and independently verify the release, run all-OFF/finite-WBUF gates, then claim
and execute the first B16/U_WB16 pair; do not wait for TVD/RO. No new formal
performance run is currently launched; active simulations in our registry: 0.
No polling daemon or promised background continuation is running.

Review pack: `docs/ep_l2/review_packs/FT20261016_LANE5_TOOLING_r1/`.
Initial quota pack: `docs/ep_l2/review_packs/FT20261016_LANE5_HOST_BUDGET_r1/`.
