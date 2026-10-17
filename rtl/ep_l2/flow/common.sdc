# Identical control-interface constraints for B16 / U / S64 and DC/OpenSTA.
# All times ns, load in Liberty capacitance units. With Nangate45 that is fF.
# No false paths, no multicycle paths, no guessed SRAM timing arcs.
if {![info exists ::env(CLOCK_PERIOD_NS)]} { set ::env(CLOCK_PERIOD_NS) 0.883392226 }
if {![info exists ::env(IO_DRIVE_CELL)]} { error "IO_DRIVE_CELL must name an actual cell in selected library" }
if {![info exists ::env(OUTPUT_LOAD_LIB_UNITS)]} { error "OUTPUT_LOAD_LIB_UNITS is required in the actual library units" }
# Number of ns represented by one selected library time unit. Open Nangate
# runs use1.0; DC must declare the actual value (e.g.1ps ->0.001).
if {![info exists ::env(LIB_TIME_UNIT_NS)]} { set ::env(LIB_TIME_UNIT_NS) 1.0 }
if {$::env(LIB_TIME_UNIT_NS)<=0} { error "LIB_TIME_UNIT_NS must be positive" }
set unit_scale $::env(LIB_TIME_UNIT_NS)
create_clock -name slice_clk -period [expr {$::env(CLOCK_PERIOD_NS)/$unit_scale}] [get_ports clk]
set_clock_uncertainty [expr {0.05/$unit_scale}] [get_clocks slice_clk]
set_clock_transition [expr {0.05/$unit_scale}] [get_clocks slice_clk]
set data_names [list]
if {[namespace exists sta]} {
    foreach port [all_inputs] {
        set name [get_full_name $port]
        if {$name ne "clk"} { lappend data_names $name }
    }
} else {
    foreach_in_collection port [all_inputs] {
        set name [get_object_name $port]
        if {$name ne "clk"} { lappend data_names $name }
    }
}
set data_inputs [get_ports $data_names]
set_input_delay [expr {0.10/$unit_scale}] -clock slice_clk $data_inputs
set_driving_cell -lib_cell $::env(IO_DRIVE_CELL) $data_inputs
set_input_transition [expr {0.05/$unit_scale}] $data_inputs
set_output_delay [expr {0.10/$unit_scale}] -clock slice_clk [all_outputs]
set_load $::env(OUTPUT_LOAD_LIB_UNITS) [all_outputs]
set_max_fanout 16 [current_design]
set_max_transition [expr {0.20/$unit_scale}] [current_design]
# ram_rdata is an external timing-cut input; ram_* outputs are timing-cut
# endpoints. These are interface budgets, NOT a macro characterization.
