# EPL2 RTL cost open flow — first cost revision

Three full-size variants completed real mapping and two independent STA runs.
These are **unoptimized controller/access-path prototype reports with timing and design-rule violations**, not whole-L2 costs or a frequency-qualified implementation. No current SIM performance can be paired with them yet.

| Mode | Standard-cell area | Combinational | Sequential | Cells | WNS0.883392226ns | TNS0.883392226ns | WNS2ns |
|---|---:|---:|---:|---:|---:|---:|---:|
| B16 | 2069971.036 | 1562430.800 | 507540.236 | 1775708 | -13.614565 | -1102450.875000 | -12.497957 |
| UNIFIED | 2525345.746 | 1975696.646 | 549649.100 | 2134130 | -36.605915 | -3507322.750000 | -35.489307 |
| S64 | 2121045.696 | 1603792.204 | 517253.492 | 1814606 | -13.612103 | -1121091.250000 | -12.495495 |

Areas are actual Liberty cell-area reference units from Nangate typical1.1V25C,
independently summed from real cell types and checked against Yosys hierarchy
totals. No target-chip mm2/MHz claim. All modes use exactly the same selected
RTL blobs (canonical25097f4b6), library hash2efd0b32..., SDC hashde89d1bd...,
ABC fast-clean effort,5fF output load,0.10ns IO budget,0.05ns uncertainty
and0.20ns max transition.2ns is a separate check of the SAME mapped netlist,
not a relaxed Unified synthesis. No false or multicycle exceptions.

Mapped designs contain zero memories/processes, zero latches and zero unmapped
cells. This does **not** mean excluded structures are free. Four292x1024
SRAM boundaries total146KiB, with no matching macro binding/Liberty. Their
area/delay and traditional full-address Tag/LRU/byte-dirty/MSHR/NoC/DRAM
costs are UNKNOWN. Bank data muxes/byte-enable paths and actual1024-bit
latches are in the mapped cut. Native/DRAM interfaces retain ownership scope.

Functional qualification: independent byte references, B16/U/S64 full size,
GEN3 saturation only, WAD128/129th same-head recovery, WB FIFO wrap, stale
events, rollback, pins, real copy vs in-place and ready/valid stalls. A real
same-edge pin/admission bug was reproduced old-red, minimally fixed, then
all full-size modes requalified. Unified additionally reached slot1167/row291,
retained36 local bank3 WBs while108 slots in other banks remained free,
then resumed the same blocked request after actual lower acceptance. This
is RTL functional qualification, not full GPU numeric or post-map equivalence.

Required scope before paper pairing: read SIM_RTL_TIMING_GAP and WIDTHS_AND_MEMORY.
Frontend readII4/writeII3, static copy, WB return, arbitration and native
preapproval differ from SIM timing. Full-size combinational metadata selection
and hierarchical high fanout have severe real STA/DRC failures. This first
fast-clean effort is bounded, not optimized timing/area closure. Static Tag-map
and owner state are also not yet hardwired; per-word increment logic is
actually replicated. B/U ratios describe this prototype and do not establish
optimized implementation overhead. Do not add a blanket hit cycle or use
160-cycle ROP as free internal timing slack. Lane1 must review any future SIM
timing adaptation; no official Core was changed here.

Tool fixes were limited to dead-node cleanup before ABC buffering, line-buffered
persistent ABC output, and checked formatting of irrelevant signed net declarations
for OpenSTA. Mapping was not repeated after it succeeded: STA resumed from
immutable original netlists. Both raw/STA-input hashes and transformation proof
are attached. check_setup emitted no coverage issues; raw coverage and path
reports are included. report_checks -unconstrained may include clocked paths;
its file length is not an unconstrained-endpoint count.

DC entry/filelists/test entry/common SDC are in rtl/ep_l2/flow. DC is UNRUN.
Supply actual target/link DBs, operating-condition name, drive/load, time-unit
conversion and PVT label. Same controller cut/parameters, private libs stay local.
Power, placement/CTS, post-route/SPEF and SRAM technology cost are absent.

ENGINEERING_ATTEMPTS and ADMISSION_INCIDENT retain failures/incomplete and
invalid-admission history. Only the current qualified receipts count. Old
PREP_r1, simulator candidates and frozen application raw data remain intact.
No complete app, Ideal synthesis, R0/R1 acceptance change or dependency waiter.

All large local own EDA intermediates/reports may be retained losslessly as
gzip with original SHA in ARTIFACT_ARCHIVE_INDEX; restore original bytes before
rerunning a local raw-netlist entry, under current central admission. Copies
here are raw reports or exact gzip, not re-created numeric results.

Local artifact root: /workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_OPEN_FLOW_V1_lane2_r1
Published source/test/DC entry: rtl/ep_l2/README.md.
