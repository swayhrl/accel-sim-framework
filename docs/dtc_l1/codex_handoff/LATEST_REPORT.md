# Latest Codex Report

Stage: `M1_FOUNDATION`

Status: **STOPPED — M1 HARD GATE B07 FAILED**

Core SHA: `581fff76cf1dabbf1b2b9fe709a0f2142ab0d8e7`

Framework implementation/evidence base SHA: `1f63d0c793784b41dbf02343c6442af5e68141a3`

## Stop evidence — B07 traditional-MSHR merge-full

M1 must not proceed.  The directed 1,024-thread same-line merge microbenchmark
was run in `PAPER_BASE` with a temporary, uncommitted validation-only override
that set traditional L1 MSHR entries to `1` and merge depth to `1`.  Rather
than draining after `MSHR_MERGE_ENRTY_FAIL` backpressure, the simulator
reported a deadlock: no core-0 writeback after GPU cycle `5081`, followed by
the watchdog after `94,919` more cycles.  The run log is retained outside the
repositories at `/tmp/dtc-l1-paper-merge1-x7Zf3G/run.log`; relevant lines are
`65–66` (effective configuration) and `324–326` (deadlock evidence).

The temporary Core source change that exposed the merge-depth override was
discarded and was never committed or pushed.  The committed Core branch is
clean at the SHA above.  This is a HARD B07 failure, not an architectural
interpretation issue: the source distinguishes `MSHR_ENRTY_FAIL` and
`MSHR_MERGE_ENRTY_FAIL`, but the directed merge-full configuration does not
make forward progress.  Do not begin M2, M3, M4, or M5 until this failure has
been resolved, revalidated, and independently reviewed.

## Main conclusions

The authorized M1 source-integration audit is complete and recorded in
`implementation/SOURCE_INTEGRATION_MAP.md`. Core M1 work now provides
default-off Paper Base PIB/Tag arbitration, a dedicated 32-entry traditional
MSHR default, and a global lower-request token cap (default 256) that is
acquired at L1 new-miss commit and released at final L1 fill. The Core static
library and deterministic CTest target build successfully with the normal
tracing configuration.

Real execution evidence uses an isolated temporary copy of the existing vecadd
PTX application. LEGACY matches clean upstream SHA `91880c53` exactly on this
kernel: 5,376 dynamic instructions, 5,562 cycles, and 96/96 L1D
accesses/misses; both runs pass the application self-check. PAPER_BASE also
passes the self-check. With MSHR=1 it reports 26,265 L1 reservation failures;
with lower cap=2 it reaches peak outstanding=2, records 13,091 cap-full events,
and closes 64 token acquires/releases at drain. Its defined front-end primary
stall accounting closes exactly: 3,970 PIB-full + 72 Tag-bank + 13,091
lower-cap = 17,133 frontend stall cycles.

The Framework CMake integration was corrected to make an isolated external
`GPGPUSIM_ROOT` buildable.  A complete `accel-sim.out` build now succeeds and
its banner reports Core `06a2e689…`.  The host lacks the normal Zstandard
development package, so this build used a transient `/tmp` checkout of the
matching 1.4.8 header and a transient link-name shim for the existing
`libzstd.so.1`; neither is a repository dependency nor formal experiment
evidence.

## Remaining issues

- B07 is failing as described above; this is the immediate stop condition.
- The M1 review pack has not been created and M1 does not pass.  Earlier
  evidence for B01–B06, B08–B09, and LEGACY neutrality remains diagnostic only
  and cannot override this failure.
- No M2/M3/M4 work has started.

## Recommendation

`M1_HARD_FAILURE_B07_STOP`

## Review entry point

`implementation/SOURCE_INTEGRATION_MAP.md`
