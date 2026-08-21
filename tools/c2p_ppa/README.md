# C2P PPA smoke flows

These flows establish reproducible tool paths for the C2P experiment model.
They are deliberately split so that a proxy result is never confused with a
complete RTL implementation.

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
routing, detailed routing, and writes DEF/ODB plus timing, congestion, and
DRC reports.  It deliberately excludes a power grid, filler/tap insertion,
extraction calibration, Snapshot SRAM macros, and payload FIFOs.  The DRC
report is retained rather than hidden: this is a transparent physical proxy,
not a sign-off result.

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
The driver combines the five split ASAP7 RVT/TT Liberty groups before mapping;
using only the simple-logic group is invalid because the mapper also needs
inverter/buffer and sequential cells.  The library time unit is one picosecond,
so the Tcl fixture's `1000.0` clock period is explicitly one nanosecond.
