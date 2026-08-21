# C2P standard-cell physical implementation using OpenROAD and ASAP7.
#
# This is a reproducibility fixture, not sign-off: extraction uses LEF RC and a
# C2P payload SRAM macro still needs technology-specific views.  The flow does
# include the standard-cell PDN, tap/endcap, filler, and tie-cell steps.

proc require_env {name} {
    if {![info exists ::env($name)] || $::env($name) eq ""} {
        error "environment variable $name must be set"
    }
    return $::env($name)
}

set out_dir [require_env C2P_PPA_RESULT_DIR]
set design_name [require_env C2P_PPA_TOP]
set tech_lef [require_env C2P_ASAP7_TECH_LEF]
set cell_lef [require_env C2P_ASAP7_CELL_LEF]
set liberty [require_env C2P_ASAP7_MERGED_LIB]
set mapped_netlist [require_env C2P_PPA_MAPPED_NETLIST]
set make_tracks [require_env C2P_ASAP7_MAKE_TRACKS]
set set_rc [require_env C2P_ASAP7_SET_RC]
set tap_tcl [require_env C2P_ASAP7_TAP_TCL]
set pdn_tcl [require_env C2P_ASAP7_PDN_TCL]
set rcx_rules [require_env C2P_ASAP7_RCX_RULES]
set utilization [expr {[info exists ::env(C2P_PPA_UTILIZATION)] ?
                       $::env(C2P_PPA_UTILIZATION) : 25}]
set clock_period [expr {[info exists ::env(C2P_PPA_CLK_PS)] ?
                        $::env(C2P_PPA_CLK_PS) : 1000.0}]
set droute_end_iter [expr {[info exists ::env(C2P_PPA_DROUTE_END_ITER)] ?
                           $::env(C2P_PPA_DROUTE_END_ITER) : 64}]
set stop_after_cts [expr {[info exists ::env(C2P_PPA_STOP_AFTER_CTS)] ?
                          $::env(C2P_PPA_STOP_AFTER_CTS) : 0}]
set repair_setup [expr {[info exists ::env(C2P_PPA_REPAIR_SETUP)] ?
                        $::env(C2P_PPA_REPAIR_SETUP) : 0}]
set repair_util [expr {[info exists ::env(C2P_PPA_REPAIR_UTILIZATION)] ?
                       $::env(C2P_PPA_REPAIR_UTILIZATION) : 70}]
set detail_pad [expr {[info exists ::env(C2P_PPA_DETAIL_PAD_SITES)] ?
                      $::env(C2P_PPA_DETAIL_PAD_SITES) : 1}]
set post_grt_repair [expr {[info exists ::env(C2P_PPA_POST_GRT_REPAIR)] ?
                           $::env(C2P_PPA_POST_GRT_REPAIR) : 1}]

file mkdir $out_dir
read_lef $tech_lef
read_lef $cell_lef
read_liberty $liberty
if {[info exists ::env(C2P_PPA_EXTRA_LEF)] && $::env(C2P_PPA_EXTRA_LEF) ne ""} {
    read_lef $::env(C2P_PPA_EXTRA_LEF)
}
if {[info exists ::env(C2P_PPA_EXTRA_LIBERTY)] && $::env(C2P_PPA_EXTRA_LIBERTY) ne ""} {
    read_liberty $::env(C2P_PPA_EXTRA_LIBERTY)
}
read_verilog $mapped_netlist
link_design $design_name

# ASAP7 Liberty time_unit is 1 ps, so 1000.0 is an explicit 1 ns constraint.
create_clock -name core_clk -period $clock_period [get_ports clk]
set_thread_count 8

initialize_floorplan -site asap7sc7p5t -utilization $utilization -aspect_ratio 1.0 \
    -core_space 2
source $make_tracks
source $set_rc
# A total-C2P run supplies the SRAM macro LEF/Liberty above and a
# technology-specific placement/PDN fragment through this hook.  The fragment
# owns concrete macro coordinates, halo, power-pin hookup, and any keepouts;
# this generic lane flow intentionally cannot invent those process facts.
if {[info exists ::env(C2P_PPA_MACRO_SETUP_TCL)] && $::env(C2P_PPA_MACRO_SETUP_TCL) ne ""} {
    source $::env(C2P_PPA_MACRO_SETUP_TCL)
}
# Use the same ASAP7 standard-cell integration conventions as ORFS.  This
# flow has no hard SRAM macro yet, but the halo and grid setup are retained so
# the physical recipe carries forward when the Snapshot macro is supplied.
set ::env(TAP_CELL_NAME) TAPCELL_ASAP7_75t_R
set ::env(MACRO_ROWS_HALO_X) 2
set ::env(MACRO_ROWS_HALO_Y) 2
source $tap_tcl
source $pdn_tcl
# OpenROAD represents Verilog literals as the supply-typed zero_/one_ nets.
# Convert them to regular signal nets driven by the technology tie cells before
# TritonRoute sees them; their VDD/VSS pins remain connected by the PDN rules.
insert_tiecells TIELOx1_ASAP7_75t_R/L -prefix C2P_TIELO_
insert_tiecells TIEHIx1_ASAP7_75t_R/H -prefix C2P_TIEHI_
pdngen
place_pins -hor_layers M4 -ver_layers M5
set_routing_layers -signal M2-M7 -clock M4-M7
set_global_routing_layer_adjustment M2-M7 0.25

global_placement -density 0.60
set_placement_padding -global -left $detail_pad -right $detail_pad
detailed_placement
# The C2P lane has a few legitimate high-fanout control enables (FIFO push,
# candidate retirement, and reset).  Buffer/resize them from placement RC
# before timing or CTS; otherwise the proxy exaggerates their wire delay by
# several nanoseconds and is not useful as an RTL feedback loop.
repair_design -max_wire_length 10
detailed_placement
check_placement
estimate_parasitics -placement
tee -file "$out_dir/pre_cts_area.rpt" { report_design_area }
tee -file "$out_dir/pre_cts_timing.rpt" { report_checks -path_delay max -digits 4 }

clock_tree_synthesis -buf_list {BUFx2_ASAP7_75t_R} \
    -root_buf BUFx2_ASAP7_75t_R
set_propagated_clock [get_clocks core_clk]
estimate_parasitics -placement
if {$repair_setup} {
    repair_timing -setup -max_utilization $repair_util
    detailed_placement
    estimate_parasitics -placement
}
tee -file "$out_dir/post_cts_timing.rpt" { report_checks -path_delay max -digits 4 }

if {$stop_after_cts} {
    write_def "$out_dir/$design_name.post_cts.def"
    write_db "$out_dir/$design_name.post_cts.odb"
    exit
}

global_route -congestion_iterations 30 \
    -congestion_report_file "$out_dir/congestion.rpt"
# Match the ORFS route sequence: construct legal access points before
# TritonRoute.  Skipping this step lets detailed route invent access geometry
# and produces avoidable M1/M2 shorts even at very low utilization.
pin_access
# Placement-RC repair only fixes the deliberately short inner loop.  The
# physical flow also needs the normal ORFS global-route repair/re-route pass:
# its estimates include real detours and it re-routes exactly the nets changed
# by buffering/resizing.  Keep it enabled by default so a retained DRC result
# is from the same implementation sequence used by an ordinary OpenROAD flow.
if {$post_grt_repair} {
    set_propagated_clock [get_clocks core_clk]
    estimate_parasitics -global_routing
    repair_design -max_wire_length 10
    detailed_placement
    global_route -start_incremental
    global_route -end_incremental \
        -congestion_report_file "$out_dir/congestion_post_repair_design.rpt"

    estimate_parasitics -global_routing
    if {$repair_setup} {
        repair_timing -setup -max_utilization $repair_util
        detailed_placement
        global_route -start_incremental
        global_route -end_incremental \
            -congestion_report_file "$out_dir/congestion_post_repair_timing.rpt"
        estimate_parasitics -global_routing
    }
}
# The finite iteration count makes the fixture's runtime deterministic.  The
# resulting DRC report is always retained; this proxy is not a sign-off layout.
detailed_route -droute_end_iter $droute_end_iter -output_drc "$out_dir/drc.rpt"
filler_placement {FILLERxp5_ASAP7_75t_R FILLER_ASAP7_75t_R}
# LEF-RC lacks ASAP7's synthetic Pad layer, so it cannot produce a legal
# extracted SPEF for this design.  Use the versioned ORFS OpenRCX patterns
# instead; this is the same technology extraction input used by the ASAP7
# reference flow.
set_extraction_rules_file $rcx_rules
extract_parasitics
write_def "$out_dir/$design_name.def"
write_db "$out_dir/$design_name.odb"
tee -file "$out_dir/post_route_area.rpt" { report_design_area }
tee -file "$out_dir/post_route_timing.rpt" { report_checks -path_delay max -digits 4 }
