# Lane 4 executed audit and ideal-mode candidate

Status: READY_FOR_REVIEW / DEPENDENCY_PENDING_SHARED_B16_RELEASE.

Read IDEAL_CONTRACTS.json, IDEAL_MODE_SOURCE_MAP.md, VALIDATION_SUMMARY.md,
REUSE_AUDIT.csv, CEILING_RESULTS.csv, LIMITER_MOVEMENT.csv, then exact manifests.
The review pack is a source/test/diagnostic candidate, not independent acceptance.

Historical search covers all retained EP-L2 stage refs and known node metadata,
with supplementary earlier LateBind lineage. Search scope and exact matches
are retained in HISTORY_SEARCH.json. No source/config/binary/trace-matched new
B16 ideal row was found. Old shadow WBUF4/8/16, MSHR256 and L1 headroom remain
historical evidence; the earlier ideal_writeback also removed port/data-traffic
constraints and cannot fill I_WB. A plan is not an experiment.

New full-application historical vectorAdd_4M comparison: OFF 73873 versus
I_READ_HIT 42918 cycles, same 56000000 instructions (1.721259x). This is an
OLD_D512_STATIC optimistic read-miss reference with explicit symbolic bytes.
It is NOT new B16 performance, EP-L2 implementable speedup, or a strict bound.
DRAM read bytes change 32000000 -> 0; lower/scheduler pressure also changes.
The measured timing interleaving changes write traffic too; retain both rows.

I_WB and I_META and their combination are implemented and production-tested.
Their B16 application speedups are NOT_RUN, not zero. First-wave baseline rows
are owned by Lane 5. Lane 1 must apply the minimal patch or integrate equivalent
default-OFF diagnostics, then Lane 5 qualifies one common binary and provides
its frozen B16 specs. prepare_ft_lane4_b16.py derives ideal-only overlays and
run_ft_lane4_diagnostic.py consumes the same central registry; a baseline
without these registrations is refused. The normal baseline is never relaunched
under a different identity merely to call it shared reuse.

Next executable command after the common release/spec exists:
`python3 util/ep_l2/prepare_ft_lane4_b16.py --baseline-spec BASE.json --mode I_WB --out IDEAL.json`,
then `python3 util/ep_l2/run_ft_lane4_diagnostic.py --execute-prepared IDEAL.json`.
Repeat only the four first-wave workloads; combination only convolution/FWT.
No new broad calibration, scan, full cross-product, or I_BANK run is claimed.
