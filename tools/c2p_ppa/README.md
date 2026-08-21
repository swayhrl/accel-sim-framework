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
