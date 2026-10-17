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
IO_DRIVE_CELL, OUTPUT_LOAD_LIB_UNITS, PVT_LABEL and LIB_TIME_UNIT_NS; optionally CLOCK_PERIOD_NS. Run:

    dc_shell -f rtl/ep_l2/flow/run_dc.tcl

DC is UNRUN here. Canonical physical constraints use ns; LIB_TIME_UNIT_NS declares the ns represented by one actual library time unit (1.0 for ns,0.001 for ps). The SAME SDC converts every time value. Check units.rpt and set OUTPUT_LOAD_LIB_UNITS to the actual5fF equivalent in that library; do not silently change physical constraints across modes. Private technology libraries must stay local. The provided
DC target is the same controller cut. To integrate SRAM in an SoC, replace the
blackbox memory wrapper with a pin-compatible actual macro adapter, constrain
its real Liberty and budget all external traditional logic. Do not interpret
the controller report as full-slice SRAM area or full-hit timing. Power and
placement/routing are not part of this first delivery.

`--mapping standard` is the default ABC effort. `--mapping fast` selects the
Yosys ABC fast technology-mapping script when a bounded standard attempt
does not finish. This is still real Liberty mapping and independent STA,
but lower optimization effort can change area/timing. All compared modes
must use the identical effort, library and physical constraints. Incomplete
standard attempts do not constitute cost results. Exact synth.ys, tool
versions and effort are retained with every successful mapping.

`full_slice_filelist.f` adds the synthesizable `ep_l2_slice` integration top
with four explicit SRAM blackboxes. The controller cost filelist excludes
these macros at its documented timing cut. `run_functional.py --full-top`
qualifies this integration using the same byte-reference transaction tests.

The installed ABC fast default failed at `buffer`: a dangling mapped node
had no fanout. `--mapping fast-clean` uses explicit strash/map, then
`cleanup -i -o` before buffer/upsize/dnsize/stime. Cleanup removes only dead
logic and preserves all PIs/POs; it changes no clock/IO/fanout constraints.
ABC receives combinational graphs only; state registers remain at the RTL
boundaries. This explicit effort must be the SAME for B16/Unified/S64. Raw
failed/default scripts and the full-size cleaned-graph diagnosis are retained.
Final timing comes from independent OpenSTA, not ABC's requested target.
All future tool temporaries use TMPDIR inside the counted output directory.
OpenSTA is explicitly single-threaded.
