# Lane2 — EPL2_RTL_COST_OPEN_FLOW_V1 first revision delivered

First revision is complete before the8h checkpoint (T0 2026-10-17T14:55:14Z; checkpoint22:55:14Z).
[Cost review pack](../../../review_packs/RTL_COST_OPEN_FLOW_V1_r1/README.md) contains actual reports and exact identities.
Canonical changed-path hardware25097f4b6; B16/Unified/S64 use identical selected RTL blobs, reference Liberty/PVT/SDC and ABC fast-clean effort.

| Mode | Standard-cell reference area | WNS0.883392226ns | WNS2ns |
|---|---:|---:|---:|
| B16 | 2069971.036 | -13.614565 | -12.497957 |
| UNIFIED | 2525345.746 | -36.605915 | -35.489307 |
| S64 | 2121045.696 | -13.612103 | -12.495495 |

All three mapped controller/access cuts have zero latches and zero unmapped cells.
All three have **unclosed target timing and design rules**; not whole-L2 area/Fmax,
optimized area overhead or a current-SIM-performance pairing. SRAM146KiB and reused
native Tag/MSHR costs remain UNKNOWN. No matching macro delay; no SPEF/CTS/layout.

Actual functional proof: byte oracle, full-size three modes, real static copy/U
in-place, WAD128/129th same-head retry, FIFO wrap, stale events, pins/rollback.
A same-edge destructive-admission/pin bug was reproduced old-red and minimally
fixed before the final hardware freeze and new-green suite. Unified additionally
filled1024 Tags and reached PID1167/row291 with36 bank3 WBs, correctly blocking
despite108 free slots elsewhere, then resuming the same requester on real credit.
This is bounded non-atomic RTL qualification, not full GPU/post-map equivalence.

Read SIM_RTL_TIMING_GAP and WIDTHS_AND_MEMORY. Frontend II4/II3, static copy/WB
return/round-robin/native approval differ from SIM; baseline map/owner FFs and
per-word metadata logic are not optimized away by assertion. Actual critical
paths identify metadata selection/admission/high fanout. Lane1 timing-review
handoff is in the pack; no official Core change or app request was made.

DC scripts/filelists/constraints/actual operating-condition and library entrances
are delivered; DC UNRUN (no dc_shell here). Power and full physical flows UNRUN.

All own Goal leases are released. Large own EDA files were losslessly archived
with decoded-byte SHA verification; retained EDA266.8MB, central total10.779GB
at audit, floors unchanged. No old frozen application raw results or foreign
project processes touched. Historical failures/admission incident remain disclosed.

TVD/common/structural Core candidates remain clean at be5dcbe1/099aeb5a/26ed1da6.
Old review packs remain. Three TVD r14 tests remain NOT_COMPILED_NOT_RUN.
No complete app, scientific acceptance mutation or resident dependency waiter.
