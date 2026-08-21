# C2P PPA smoke flows

These flows establish reproducible tool paths for the C2P experiment model.
They are deliberately split so that a proxy result is never confused with a
complete RTL implementation.

The read-side functional RTL baseline now lives in [`rtl/`](rtl/README.md).
Its directed test is `run_c2p_rtl_test.sh`; the OpenROAD flow remains a
control-slice proxy until a technology-matched Snapshot SRAM macro is
integrated.

## AccelWattch system-power smoke

`configs/c2p-cache/power-smoke.config` enables stock Volta SASS-SIM
AccelWattch for a regular C2P replay.  It measures baseline GPU component
activity changes (L1/L2/NoC/DRAM) only.  The current C2P C++ model has no
AccelWattch hooks for Snapshot SRAM, BF engines, queues, or the far-L1
transport, so the resulting report is a flow check rather than C2P total
power.

## CACTI Snapshot SRAM proxy

The C2P Snapshot Matrix is 5120 rows by 64 bits, or 40 KiB logical capacity.
The four physical copies are independent banking replicas.  A CACTI report
must retain the single-copy 40 KiB / 64-bank / 8-byte-row result and report a
separate four-copy scaling, rather than modelling it as one monolithic 160 KiB
array.  Run:

```bash
export C2P_GPGPUSIM_ROOT=/path/to/gpgpu-sim-c2p-cache
tools/c2p_ppa/run_cacti_snapshot_proxy.sh
```

The script builds the bundled CACTI source in its result directory and keeps
the exact generated input and output there.

## Yosys control-slice proxy

Run:

```bash
tools/c2p_ppa/run_yosys_control_proxy.sh
```

The fixture includes candidate pruning, 64-way selection, and bounded-resource
control only.  It excludes Snapshot and FIFO payload storage.  Its generic
gate count is therefore a reproducibility test for the synthesis flow, not a
claim of complete C2P control area.  Replace `rtl/c2p_control_proxy.v` with
the future C2P RTL top before reporting a hardware area number.

## OpenROAD physical-control proxy

This final layer is a real standard-cell implementation, not a Yosys-only
area count.  It maps the control fixture to the open ASAP7 RVT/TT library,
runs floorplanning, IO placement, global and detailed placement, CTS, global
routing, detailed routing, and writes DEF/ODB plus timing, area, and DRC
reports.  The standard-cell recipe includes tap/endcap insertion, an ASAP7
PDN grid, filler insertion, and post-route LEF-RC parasitic extraction.  It
still excludes extraction-rule calibration, Snapshot SRAM macros, and payload
FIFOs.  The DRC report is retained rather than hidden: this is a transparent
physical proxy, not a sign-off result.

The flow uses an OpenROAD-flow-scripts checkout as the source of a consistent
ASAP7 technology LEF, cell LEF, Liberty and routing setup.  With an OpenROAD
binary already built, run:

```bash
export C2P_ORFS_ROOT=/path/to/OpenROAD-flow-scripts
export C2P_OPENROAD_BIN=/path/to/openroad
export C2P_YOSYS_BIN=/path/to/yosys       # optional if yosys is on PATH
tools/c2p_ppa/run_openroad_control_proxy.sh
```

`C2P_PPA_RESULT_DIR=/some/ignored/path` overrides the default result location.
`C2P_PPA_CLK_PS` sets the clock period in ps (default `1000.0`, i.e. 1 ns).
`C2P_PPA_UTILIZATION` overrides the default 25% core utilization.  The default
leaves physical whitespace for PDN, taps, filler, clocking, and macro halos;
it is intentionally not the control-only cell utilization reported by Yosys.
`C2P_PPA_DROUTE_END_ITER` overrides the default finite 64 detailed-route
iterations for exploratory runs; retain the resulting DRC report either way.
`C2P_PPA_STOP_AFTER_SYNTH=1` stops immediately after the deterministic ASAP7
mapping and writes the mapped netlist plus `yosys.log`.  It is the intended
fast inner loop for RTL timing/area changes; it does not require an OpenROAD
binary and must not be reported as a physical result.
`C2P_PPA_STOP_AFTER_CTS=1` retains floorplanning, PDN/tap/tie integration,
placement, and CTS, then writes the post-CTS DEF/ODB and timing report without
routing.  It is the fast physical timing loop, not a final PPA result.
`C2P_PPA_REPAIR_SETUP=1` enables OpenROAD setup repair after CTS.  It is
disabled by default so baseline reports remain directly comparable; enable it
only when evaluating whether a remaining violation is architectural or can be
repaired by ordinary standard-cell optimization.
`C2P_PPA_DETAIL_PAD_SITES` controls standard-cell padding before detail
placement (default `1`).  Keeping one site around the dense control logic is
part of the route recipe, not a cosmetic area adjustment.
The driver combines the five split ASAP7 RVT/TT Liberty groups before mapping;
using only the simple-logic group is invalid because the mapper also needs
inverter/buffer and sequential cells.  The library time unit is one picosecond,
so the Tcl fixture's `1000.0` clock period is explicitly one nanosecond.

To implement the actual single-lane C2P request-control RTL rather than the
small historical control fixture, keep the same three environment variables
and run:

```bash
tools/c2p_ppa/run_openroad_c2p_query_engine.sh
```

That top has the real Snapshot request/response ports but intentionally does
not infer the 40 KiB Snapshot array as flip-flops.  Its result is the control
lane PPA; combine it only with a matching four-replica SRAM macro result.
