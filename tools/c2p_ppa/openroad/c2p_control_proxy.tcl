# C2P control-slice physical implementation using OpenROAD and ASAP7.
#
# This is a reproducibility fixture, not a sign-off flow: it has no power grid,
# filler/tap insertion, extraction-rule calibration, or C2P payload SRAM macro.
# Those omissions are intentional and are recorded by the driver README.

proc require_env {name} {
    if {![info exists ::env($name)] || $::env($name) eq ""} {
        error "environment variable $name must be set"
    }
    return $::env($name)
}

set out_dir [require_env C2P_PPA_RESULT_DIR]
set tech_lef [require_env C2P_ASAP7_TECH_LEF]
set cell_lef [require_env C2P_ASAP7_CELL_LEF]
set liberty [require_env C2P_ASAP7_MERGED_LIB]
set mapped_netlist [require_env C2P_PPA_MAPPED_NETLIST]
set make_tracks [require_env C2P_ASAP7_MAKE_TRACKS]
set set_rc [require_env C2P_ASAP7_SET_RC]

file mkdir $out_dir
read_lef $tech_lef
read_lef $cell_lef
read_liberty $liberty
read_verilog $mapped_netlist
link_design c2p_control_proxy

# ASAP7 Liberty time_unit is 1 ps, so 1000.0 is an explicit 1 ns constraint.
create_clock -name core_clk -period 1000.0 [get_ports clk]
set_thread_count 8

initialize_floorplan -site asap7sc7p5t -utilization 45 -aspect_ratio 1.0 \
    -core_space 2
source $make_tracks
source $set_rc
place_pins -hor_layers M4 -ver_layers M5
set_routing_layers -signal M2-M7 -clock M4-M7
set_global_routing_layer_adjustment M2-M7 0.25

global_placement -density 0.60
detailed_placement
check_placement
estimate_parasitics -placement
tee -file "$out_dir/pre_cts_area.rpt" { report_design_area }
tee -file "$out_dir/pre_cts_timing.rpt" { report_checks -path_delay max -digits 4 }

clock_tree_synthesis -buf_list {BUFx2_ASAP7_75t_R} \
    -root_buf BUFx2_ASAP7_75t_R
set_propagated_clock [get_clocks core_clk]
estimate_parasitics -placement
tee -file "$out_dir/post_cts_timing.rpt" { report_checks -path_delay max -digits 4 }

global_route -congestion_report_file "$out_dir/congestion.rpt"
# The finite iteration count makes the fixture's runtime deterministic.  The
# resulting DRC report is always retained; this proxy is not a sign-off layout.
detailed_route -droute_end_iter 64 -output_drc "$out_dir/drc.rpt"
write_def "$out_dir/c2p_control_proxy.def"
write_db "$out_dir/c2p_control_proxy.odb"
tee -file "$out_dir/post_route_area.rpt" { report_design_area }
tee -file "$out_dir/post_route_timing.rpt" { report_checks -path_delay max -digits 4 }
