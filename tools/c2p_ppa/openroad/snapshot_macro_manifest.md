# Snapshot SRAM macro manifest

The C2P Snapshot Matrix is not synthesizable as a standard-cell register
array for a meaningful PPA result.  The physical C2P top therefore treats it
as four replicas of one logical 5,120-row x 64-bit matrix.  Each replica is
40 KiB; all four are 160 KiB before spare/ECC/repair overhead.

Before a total-C2P OpenROAD run may be reported, the selected technology must
provide one view set per replica with the following checked properties.

| Required view | Purpose |
| --- | --- |
| Verilog black box or wrapper | synthesis and hierarchy contract |
| Liberty for every STA corner | timing/power arcs and cell area |
| LEF | macro dimensions, pins, obstructions, power pins |
| GDS/OASIS | final physical sign-off handoff |
| RC/extraction setup | post-route timing and power analysis |
| power pins/grid requirements | PDN connection and IR analysis |

## Logical port contract

The functional RTL requires four concurrent row reads for every query and
one update that sets the requesting SM's bit in each of the four encoded
rows.  A macro integration may satisfy that contract through either:

1. four 1R1W read replicas plus a broadcast/masked-write update path; or
2. a wider/multiport macro plus an adapter whose arbitration and latency are
   reflected in `c2p_snapshot_matrix`'s ready/response interface.

The adapter must define read-during-write behavior and preserve the explicit
two-cycle query response contract.  If a macro lacks bit write-enable, its
read-modify-write sequencer must backpressure `update_ready`; it must never
drop an L1-fill update silently.

## Versioned OpenROAD handoff

The reusable OpenROAD driver is
`tools/c2p_ppa/run_openroad_c2p_cache_rtl.sh`.  It refuses to run without the
macro Verilog, LEF, Liberty, and a placement/PDN setup Tcl.  The latter is
intentionally technology-owned: its four replica coordinates, macro halos,
power-pin names, and power-grid connections cannot safely be guessed by a
generic script.  Start from
[`c2p_snapshot_macro_setup.tcl.example`](c2p_snapshot_macro_setup.tcl.example)
and set the four required environment variables documented by the runner.

## PPA reporting rule

Until this manifest is populated with a technology-matched macro, report the
OpenROAD query-engine result as **control only** and the CACTI result as a
separate four-replica SRAM estimate.  Do not add the CACTI area to an ASAP7
standard-cell area and call it a sign-off total: their technology assumptions
and corner definitions differ.
