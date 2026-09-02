# Latest Codex Report

Stage: `M1_FOUNDATION`

Status: **IN_PROGRESS — M1 RESOURCE PATHS VALIDATED; HARD GATES PENDING**

Core SHA: `e363a7730ac4ae4f00e6fa252c18653468ba672a`

Framework implementation/evidence base SHA: `c05b84e83c215e5f63aa6218f85666847b03c272`

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

- M1 HARD validation remains incomplete: full directed simulator-path B02-B09
  evidence, the remaining two LEGACY-neutrality workloads, primary/non-exclusive
  stall closure, and the M1 review pack are still required. A strict
  provenance-bearing JSON parser now exists, but it has only been used for a
  diagnostic vecadd smoke run and is not review-pack evidence.
- No M2/M3/M4 work has started.

## Recommendation

`M1_IN_PROGRESS`

## Review entry point

`implementation/SOURCE_INTEGRATION_MAP.md`
