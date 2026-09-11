# C13 preflight audit

Status: `PREFLIGHT_PASS_REPLAY_ADMISSION_DEFERRED_FOR_HOST_HEALTH`

## Frozen identity

- Framework diagnostics HEAD: `38e65f3e880e4e88e91290492c153dcb98f302f9`, proven to descend from formal C12 closeout `a268aba0d01310294074ded5bb8017e2092394c0`.
- Config-only arms bind Core `57bb71ecd015b6ec0ab32e45b0815e5beaf69172` and binary SHA-256 `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`.
- Prefill/Decode1 trace-list and V2 registration SHA-256 values match the C12 anchors, as recorded in `C13_COMMAND_MANIFEST.tsv`.
- The accepted Operator-aware source is read only at `8801f2e9fea4e0df1d79853a5e4440c4da463486`; its parser/map are attribution inputs, never execution identity.

## Seven primary points

`C13-LAT-P8`, `C13-LAT-P9`, `C13-LAT-D11`, `C13-CAP-P320`, and
`C13-CAP-P768S10` are generated config-only and bind the unchanged C12 binary.
Their C13-only config tail chooses `fair_arm=MANUAL` solely because C12 F7's
frozen selector admits only Lseg 5/10/20; final realized geometry is checked
from telemetry against the matrix fields before PASS.

`C13-SEL-P10` and `C13-SEL-D10` require the independent C13 Core overlay.
Their mandatory same-new-binary controls are already in the manifest.  No
cross-binary performance comparison is authorized.

## Replay admission

At preflight sampling, the host had about 512 logical CPUs but roughly 660--700
runnable tasks, active unrelated simulators, effectively exhausted swap, and
about 91--93 GiB free disk.  Although memory/IO PSI were low, that is not a
safe state to add a C13 full-ROI job.  No C13 simulator was launched; the
admission gate will be rechecked and initial launch remains capped at two-way.
