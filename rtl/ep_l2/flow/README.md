From repository root, under a central resource lease in the shared environment:

    python3 rtl/ep_l2/flow/run_open.py --mode B16 --liberty /absolute/real.lib --out /absolute/new_B16

Repeat UNIFIED and S64 with exactly the same library, drive/load and SDC. This
maps ep_l2_slice_ctrl (including actual data buses/latches), not a full L2.
Full capacity is mandatory for cost; all three use 1024 Tags/1168 payloads and
128 WAD entries. Four 292x1024-bit synchronous 1RW SRAM models are connected in
the testbench. Their technology area/delay are UNKNOWN, not zero. They are
blackboxes under SYNTHESIS; they are external ports at the controller STA cut.
Traditional Tag/LRU/dirty-byte/MSHR/noC/DRAM control is external and not free.

DC: set RTL_REPO, TARGET_LIBS (Tcl list of actual .db files), LINK_LIBS (Tcl
list, including real macro libraries if applicable), DC_OUT, MODE=0/1/2,
IO_DRIVE_CELL, OUTPUT_LOAD_LIB_UNITS and PVT_LABEL; optionally CLOCK_PERIOD_NS. Run:

    dc_shell -f rtl/ep_l2/flow/run_dc.tcl

DC is UNRUN here. Canonical constraints use ns; check the emitted units.rpt against the actual target library before accepting results. A non-ns library needs a unit conversion of every common time value, not a changed physical constraint. Private technology libraries must stay local. The provided
DC target is the same controller cut. To integrate SRAM in an SoC, replace the
blackbox memory wrapper with a pin-compatible actual macro adapter, constrain
its real Liberty and budget all external traditional logic. Do not interpret
the controller report as full-slice SRAM area or full-hit timing. Power and
placement/routing are not part of this first delivery.
