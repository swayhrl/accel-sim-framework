# Exact R2 DC entrance (UNRUN here)

Run `rtl/ep_l2/flow/run_dc_r2.sh` under authorized EDA admission. Same checked-in
filelist.f, ep_l2_slice_ctrl, full1024/1168/128/GEN32, STATIC_WB16/64, P1 and
common.sdc as the R2 open controller cut. Repeat MODE0/2/1 at both0.883392226ns
and2ns in six new output directories with one actual library set/corner/load.
The wrapper freezes RTL/flow/Git/env identity. Supply actual libraries as Tcl
lists through TARGET_LIBS and LINK_LIBS, not substituted open reference cells.

Required env: RTL_REPO, DC_OUT(new), MODE, TARGET_LIBS, LINK_LIBS,
OPERATING_CONDITIONS(actual DB name), PVT_LABEL, LIB_TIME_UNIT_NS,
IO_DRIVE_CELL(actual), OUTPUT_LOAD_LIB_UNITS(actual). Optional CLOCK_PERIOD_NS
(default0.883392226). Units are explicit; preserve physical0.10ns IO,
0.05ns uncertainty/clock/input transition,0.20ns max transition,fanout16.
Use5fF equivalent only after conversion to actual cap units. No false/multicycle.

`run_dc.tcl` does analyze/elaborate/link, selects the actual operating condition,
reports units/environment/check_design, compile_ultra, hierarchical area,
max-path timing, constraints/QOR/check_timing and mapped Verilog/SDC/DDC.
No dc_shell is installed in this host: delivery is a precise **UNRUN** handoff,
not a licensed synthesis result or proof that the target library closes timing.

Macro integration top `ep_l2_slice` / full_slice_filelist.f retains four explicit
`ep_l2_payload_sram` blackboxes: each292rows x1024bits, sync1RW,128 byte enables,
ROW_W9. Physical payload capacity146KiB. Use actual matching macro(s), adapters,
Liberty/LEF and actual read latency to cost/STA the full boundary. Unknown macro
area/delay remains null, never a DFF expansion estimate. Native Tag/LRU/MSHR,
dirty-byte mask storage, NoC/lower queues are reused/external and unknown.

For reproducible open comparison, mapping target remains883ps and bothSTA
periods use the same mapped netlist. DC's six separate optimizations are DC
results and must not be substituted into the open-flow before/after table.

Final source includes ep_l2_control_buffer/ep_l2_control_inverter in the existing
metadata file; the filelist is unchanged. Open flow preserves real inverter
pairs to distribute fanout; DC can optimize/rebuffer the same function under
the actual target DB and set_max_fanout. Verify both global reset and data nets,
with reset still timed. Parallel-prefix generation is GEN32 and adds no state.

Actual DC execution also writes hashes of every selected target/link DB to
library_sha256.txt; no private DB or invented hash is part of this handoff.
