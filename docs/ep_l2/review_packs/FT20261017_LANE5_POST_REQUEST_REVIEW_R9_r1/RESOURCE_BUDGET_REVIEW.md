# New independent review after exact Lane1 request

Decision: **NO_SAFE_PILOT_ENVELOPE_AFTER_REQUEST**. This is a new assessment of248c93acc611679afe42590760481f451773003d, request SHA3f4dfd9618602dfd3f2dc5d92d0d497987f9c6ea53088a6409648506f1c10dcb, pilotEP_L2_R0_1_ENGINEERING_20261017_L1_P01. Prior refusal300c1010 was earlier than the request and is retained intact. Missing request/identity is now resolved; it is not a refusal reason here.

## New evidence

Published driver65500bb9 exact bytes, isolated clean source/vendor,15 input hashes, original formal entry, five targets and21 commands independently checked once. Local Lane1 runner now belongs to a newer clean code revision and differs from248 request; record both hashes rather than authorizing an unbound revision. This is an in-progress ordinary integration update, separate from resource safety. Fresh roots and actual domains match. No old source/qualification suite rerun. Central CLIENT's registry6b20231e and pilot e236bdbf hashes match actual files; the prior Lane4 expected8b4 hash is historical. Existing consumer pin checks must stay strict.

Four fresh samples span30.060s. Workspace available28,279,255,040B and Share47,631,331,328B at the last sample. Workspace/tmp are the same budget domain; Share is separate. RAM after8GiB reservation185,240,739,840B exceeds64GiB; no EP-L2 active run/build lease. C16 and DTC remain active and untouched.

| Domain | Proposed entry / component sum | Proposed hard stop | Fresh30s net change | Independent finding |
|---|---|---|---|---|
| workspace+tmp |26GiB /24GiB (2GiB arithmetic extra) |12GiB |available fell248,233,984B |8GiB external reserve over3600s corresponds2,386,093B/s; observed peak10s net contraction8,466,067B/s is greater. No full-hour upper bound. |
| Share |43GiB /43GiB (zero arithmetic extra) |40.5GiB |available fell12,288B |New short sample is quiet; old343,343,104B/30s episode and upcoming permitted Ops range copies show nonstationarity.40GiB is retained, never reallocated to pilot. |

These short rates are not a forecast, proven burst cap, or attribution. Stopping at net external reserve consumption is a guard, not a limit on other projects' writes between observations.256MiB RLIMIT_FSIZE is per file; it does not bound aggregate concurrent files, compiler/linker temp allocation, other processes or delayed writeback.1s sampling+2s watchdog+3s TERM(+wait) does not prove an end-to-end stop latency/byte upper bound. Proposed overshoots2GiB workspace/512MiB Share remain unverified. All six proposal terms are positive and arithmetic closes, but empirical/enforced safety closure does not follow.

## Ops and actual automation

Exact source Ops840e3370 and target172affd2 statuses were read. They report ordinary copy/restore progress and new PolyBench receiver readiness, not a low-I/O window ACK. A source-bound query is prepared for existing Ops owners; it authorizes no pause, deletion, movement or quota change, and no acknowledgement is assumed. Even an Ops quiet window would still need DTC/C16 and aggregate stop-overshoot protection. No new transport/worker is started.

The Git report649f8afa says waiter active, but real PIDs1137150/1141719 are absent, their singleton locks free, and central status says WAITER_STOPPED_BY_SIGNAL at17:26:29Z with zero invocations. This factual drift is separate from disk refusal. Lane5 does not restart a signalled owner process or create a second waiter; Lane1 must reconcile its own stopped automation before future automatic continuation.

Historical runner655 snapshot: the frozen runner expects ENGINEERING_PILOT_V1 claim/record_process/heartbeat/finish and a nested CLIENT adapter; existing Lane5 audited core has another API and the nested adapter is absent. Both fail closed. This was a normal integration item at that earlier snapshot, not a substitute for quantitative resource review or a reason to weaken canonical hashes. There is no safe envelope now to activate an adapter against. Existing39+10 tests are preserved, not re-executed unchanged.

## Result and next boundary

No authorization file/token/exception registration/lease or CMake call. The exact request is recorded, but reliable external burst and aggregate monitor/termination overshoot bounds have not been independently established for the two real filesystems. Do not lower entry/stop/emergency constants to force a pass. Next useful evidence is owner-acknowledged scheduling plus enforceable/measured limits, or separately approved precise cold-asset release/alternative build-host proposal. No asset release or alternate host is authorized by this review. Formal48GiB/50GiB build policy, eleven scientific gates, five paired applications, old six withdrawals and no engineering-binary promotion remain unchanged.

Final stage-transition live check at2026-10-16T17:34:08.969567+00:00: workspace27898707968B; requested26GiB entry False. Share47106551808B; requested43GiB entry True. Exact device/fsid and central state in FINAL_CURRENT_RESOURCE_CHECK.json. This is one bounded closeout read, no new watcher.

Concurrent Lane1 update: local clean313233ad runner SHA35a414f1 now contains the caller bridge to Lane5 API. That differs from the exact248 request driver655/d2c; published request review and live revision eligibility are recorded separately. No duplicate adapter work or repeated original tool suite was started by Lane5.

## Published r2 closeout supplement

Lane1 published request revision2 at50d3a648704235ff03be6b5b7e4f8f33a904500d during review. Exact raw SHA f992a65187ea46413cec85623af16cdd39e180b817e23f9002419d03cbf7129e, frozen runner1c544c4a/f5e66091 and waiter58a44e05 match the live files and immutable r2 central inbox. The published caller bridge and exact current Lane5 hash pins resolve the API/source drift described above; they are not remaining refusal reasons. Numerical envelope, source pins,15 inputs,21 commands, targets, CPU/memory/time remain identical, so no duplicate static/test campaign is needed.

The Lane1 owner has now replaced its stopped idle control. Actual replacement waiter PID1156558/start892416307 matches /proc; both singleton locks are held, central state WAITING_RESOURCE_OR_LANE5_AUTHORIZATION, invocations0. This supersedes the earlier stopped-automation snapshot. Lane5 started/signalled no owner control. Newer published r2 identity and actual waiting status do not establish missing burst/overshoot bounds and do not change the independent resource refusal. See LANE1_R2_SUPPLEMENT.json and exact latest STATUS/RECEIPT bytes in this pack.
