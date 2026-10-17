# Identical control-interface constraints for B16 / U / S64 and DC/OpenSTA.
# All times ns, load in Liberty capacitance units. With Nangate45 that is fF.
# No false paths, no multicycle paths, no guessed SRAM timing arcs.
if {![info exists ::env(CLOCK_PERIOD_NS)]} { set ::env(CLOCK_PERIOD_NS) 0.883392226 }
if {![info exists ::env(IO_DRIVE_CELL)]} { error "IO_DRIVE_CELL must name an actual cell in selected library" }
if {![info exists ::env(OUTPUT_LOAD_LIB_UNITS)]} { error "OUTPUT_LOAD_LIB_UNITS is required in the actual library units" }
create_clock -name slice_clk -period $::env(CLOCK_PERIOD_NS) [get_ports clk]
set_clock_uncertainty 0.05 [get_clocks slice_clk]
set_clock_transition 0.05 [get_clocks slice_clk]
set data_names [list]
foreach name [get_full_name [all_inputs]] { if {$name ne "clk"} { lappend data_names $name } }
set data_inputs [get_ports $data_names]
set_input_delay 0.10 -clock slice_clk $data_inputs
set_driving_cell -lib_cell $::env(IO_DRIVE_CELL) $data_inputs
set_input_transition 0.05 $data_inputs
set_output_delay 0.10 -clock slice_clk [all_outputs]
set_load $::env(OUTPUT_LOAD_LIB_UNITS) [all_outputs]
set_max_fanout 16 [current_design]
set_max_transition 0.20 [current_design]
# ram_rdata is an external timing-cut input; ram_* outputs are timing-cut
# endpoints. These are interface budgets, NOT a macro characterization.
