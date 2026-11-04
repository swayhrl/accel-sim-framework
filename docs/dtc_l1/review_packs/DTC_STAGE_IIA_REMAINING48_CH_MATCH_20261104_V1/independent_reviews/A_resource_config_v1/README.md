# Remaining48 resource/config CPU qualification

Scope: exact approved commit `5f67b4d6b94568a9f1acc80c3e56736bd81e4753` 48 CH candidates, 24 frozen inputs × F128/F256. This agent performed no registration, owner/controller change, simulator launch, trace capture, historical result edit or asset deletion. Root alone owns registration and dispatch.

## Direct integration

Copy `stage2_resources.py` into the new R2/tools only; bind its SHA and private module instance in the new same-owner addon. API: `resources(spec, fresh_source=False)`, `sample_system()`, `choose_dispatch(pending, sample, claims, history=None, previous=None, policy=None, dispatch_index=0)` and `preclaim_diagnostics()`. Production `resources` requires the actual registered new request, exact48 admitted specs and real `E2-DTC2A48-...` cohort; no dummy or unregistered scientific identity is accepted. `RESOURCE_POLICY.candidate.json` is the new independent policy to copy into R2/control/RESOURCE_POLICY.json. `RESOURCE_SPEC_FIELDS.json` binds each candidate's resource forecast and emergency limits; it is not a scientific native spec.

`choose_dispatch` checks fresh full resource admission before returning each candidate and before the sole owner adds its claim. It can try a smaller fitting candidate without permanently excluding a blocked candidate. This avoids all-pending claims producing a disk-budget deadlock. Registration does not reserve all48 unstarted outputs simultaneously.

## RAM, CPU and health

Historical same-input peakRSS includes negative as well as accepted runs. Registered forecast = max(512MiB, 1.20 × historical peak +384MiB); aggregate48 forecast174.174GiB. This is not the RSS hard limit. Emergency RSS limit = max(8GiB, ceilGiB(1.75 × peak+2GiB)); scalarProd19GiB, cutcp26GiB, sgemm29GiB, others at most16GiB. VMS limit = max(4 × RSS limit, RSS limit+32GiB). Live peakRSS and recent same-input observations enlarge admission forecasts conservatively within the registered emergency limit.

Target admission uses88% safe host/cgroup headroom, with8GiB host/cgroup floors. PSI, active swap growth, current OOM/limit increments and CPU pressure pause new admission. Runtime healthy RAM pass remains true under predicted pressure; native physical floor, actual output cap and emergency RSS/VMS limits remain enforced by the qualified lifecycle. Static historical swap/OOM counts alone do not permanently block new tasks.

Observed cpuset0–511 and quota384 CPU equivalents. `NEW_ADDON_CPU_MASK.json` proposes0–31,64–511 for only the new addon thread. The owner's MAIN32–63 and old threads are preserved. The scheduler must still inspect actual claims/observed model affinities before assigning a CPU. This observation is not a CPU grant and not a promised concurrency.

## Storage and old scopes

Use native device2128 bounded gzip spool, asynchronous genuine164 SOURCE_KEEP archive, and complete native restore. No output symlink or bulk164 device assertion bypass is used. True164 mount source and archive headroom are checked. Native5GiB free safety floor and minimum100000 free inodes remain hard boundaries.

The log hard caps are512MiB per myocyte point,256MiB per srad_v1 point, and64MiB per other point. These exceed observed same-input logs with at least4× history+4MiB rounded to a power of2. Source+full restore lifetime upper bound is8.5GiB, plus256MiB metadata =8.75GiB registered ceiling. A cap is distinct from the forecast; no64MiB identity was consumed before this new contract. Active claims/candidate reserve their incremental source+restore bound; already present df bytes are not charged twice. Archived/nonlive points have no future growth. Unclaimed points receive no speculative future write claim.

Pinned R20 accounting is read unchanged. Unknown foreign scopes retain their budgets. StageI scan remains accounted, and first16 future reserve becomes0 only after16 exact archive/DONE/EXIT/INTENT/registry joins plus nonlive generations. Three later fully CLOSED known scopes have1GiB metadata-only projections despite no future work. The new private accounting releases only those future projections after a fresh CLOSED/rem0/consumed=budget/no unusedclaim/write_entries=[]/every exact archive+nonlive proof. `CLOSED_METADATA_JOIN_CERTIFICATE.json` records q/claims canonical hashes, registered values and every INTENT/DONE/EXIT/archive/PIDMAP SHA and PID generation. LAVA2, REMAINING4 and RECOVERY12 are the18 joined points;3GiB future prediction is released. Existing df bytes, registered reservations, old files and old source are unchanged. Missing evidence, a new live generation, an unused claim or unknown scope retains the base budget.

The runtime `physical_disk_pass` reflects only actual unsafe conditions. `admission_disk_pass` includes the complete future-write/restore budget and must be required by both prepare and archive restore gates. Archive unavailability pauses new admission/restore; healthy native-spool models are not stopped merely because a forecast or remote mount changed.

## Evidence and limitations

`CONFIG_INPUT_QUALIFICATION.json`: exact48 membership,24 binding/trace entry SHA and qualified trace-member current size/mtime,96 original accepted RESULT pins,72 original spec pins,8 fixed5001 config byte SHA. Full large trace bodies were not reread; their fullbody SHA qualification is reused only with unchanged current member metadata. The prior fixed evidence/manifest was revalidated. No input numerical-semantic or equal-area claim is added.

`CPU_RESOURCE_QUALIFICATION.json`:56 assertions across independent condition families, including closed-scope positive/negative boundaries, real pinned peer observations, forecast/cap separation and disk-before-claim behavior. Counts of point-loop assertions are not additional evidence levels. The prefix0/1/8/16/24/48 claim projections are CPU qualification fixtures, not new registered identities or dispatch batches. At that sample, nativefree10.92GiB permits the fixed first16 small-cap fixture but not all48 concurrent write bounds; RAM can admit all48 estimates. Actual dispatch must resample and dynamically hold when disk or health requires it.

Reproduction: `python3 -B qualify_resource_cpu.py` and `python3 -B qualify_config_input.py` only create this agent's report files and read existing authority/source/input files. Do not rerun these into a frozen published snapshot; use a fresh agent snapshot directory and update O in a private copy. No simulation executable is called.
