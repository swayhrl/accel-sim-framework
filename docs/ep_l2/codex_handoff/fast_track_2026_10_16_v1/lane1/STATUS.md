# Lane 1 status

Status: IN_PROGRESS — finite-WBUF/U_WB production candidate under regression.
Node: huangrulin-174.
Framework: `/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-v1`; Core: `/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane1-v1`.
Both branches: `hrl/ep-l2-ft20261016-lane1-v1`.
Core candidate source: `10d7f4fea1f9699b4e091091f7e23e072c19d453`.
Parents: Framework 54fbc786 / Core 1fc248aa.
Coordination: 6c136e2a56a008695f8c8b815723bf8f1a760db9 (not runtime).

Completed: interface V1 remotely published and fetched back (Framework cb7d92e4,
Core 4fb91f0a). Isolated release build PASS. Real finite staging admission and
static copy service, U_WB in-place ownership and bank-preserving landings,
bounded WAD/lower control, production lower-accept release, response pins and
terminal FT telemetry implemented. Initial six scenario groups passed at Core
c4896d7d; expanded same-bank/pool and independent reference suite is in progress.
All failed build/test diagnostics are retained, including a fixture packet-drain
boundary fix. No failed result is treated as a performance point.

Next: finish expanded production regression, old all-OFF three-workload
qualification with exact seven-family counters, then publish frozen B16/U_WB
baseline/binary/config to Lane 5. No formal B16/U_WB run has been claimed.
Lane 5 registry/client consumed: source de8fe21d, central shared directory
`/workspace/ep_l2_ft20261016_shared`. Builds use its lease; future simulations
use its full-content run identity. Existing unrelated experiments untouched.
Lane 2 module received at 56abbacc; requires public-production adaptation and
independent gates. Lane 3 is still implementing its oracle/module.

Review packs: FT20261016_LANE1_INTERFACE_r1 (immutable) and
FT20261016_LANE1_WBUF_CANDIDATE_r1 (candidate evidence, not runtime-ready).
