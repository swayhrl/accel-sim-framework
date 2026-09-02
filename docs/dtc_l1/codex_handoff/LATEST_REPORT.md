# Latest Codex Report

Stage: `M1_FOUNDATION`

Status: **IN_PROGRESS — B07 RECOVERED; R07.6 FULL M1 REVALIDATION PENDING**

Core SHA: `06aa534aab516578cb481e74bf006927a1828d58`

Framework implementation/evidence base SHA: `9c2e10a191991148e447b1b170bec0491f25e839` (before this report update)

## B07 recovery status

The authorized R07.1 diagnosis confirmed the proposed source-backed cause:
an L1 hit reached `warp_inst_complete()` without retiring its tracked Paper
Base PIB UID.  The minimal fix pairs that existing true-completion event with
idempotent `dtc_l1_retire()`.  A default-off bounded diagnostic trace,
drain assertion, and directed CTest accompany the change.

Using a reproducible source-supported conventional L1 configuration
(`entries=1`, `max_merge=1`), the repaired B07 run completes with
`MSHR_MERGE_ENRTY_FAIL=166`, PIB `33/33/0`, and application PASS.  The
less-pathological `max_merge=2` run also passes.  Frozen clean upstream under
the same `A:1:1` L1 geometry completes and reports the same 166 merge-full
events, so the recovery does not alter native MSHR semantics.  Full details
and raw-log hashes are in `implementation/B07_RECOVERY_EVIDENCE.md`.

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

- R07.6 still must re-run every M1 HARD gate, including exact LEGACY
  differential checks and counter/parser closure.
- The M1 review pack has not been created and M1 does not pass yet.
- No M2/M3/M4 work has started.

## Recommendation

`R07.6_M1_REVALIDATION_REQUIRED`

## Review entry point

`implementation/B07_RECOVERY_EVIDENCE.md`
