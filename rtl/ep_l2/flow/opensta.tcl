foreach name {LIBERTY NETLIST OUTPUT_DIR RTL_ROOT IO_DRIVE_CELL OUTPUT_LOAD_LIB_UNITS} {
    if {![info exists ::env($name)]} { error "missing $name" }
}
read_liberty $::env(LIBERTY)
read_verilog $::env(NETLIST)
link_design ep_l2_slice_ctrl
source $::env(RTL_ROOT)/flow/common.sdc
report_checks -path_delay max -group_path_count 10 -format full_clock_expanded -fields {slew capacitance fanout} -digits 6 > $::env(OUTPUT_DIR)/critical_paths.rpt
report_wns -digits 6 > $::env(OUTPUT_DIR)/wns.rpt
report_tns -digits 6 > $::env(OUTPUT_DIR)/tns.rpt
report_checks -path_delay min -group_path_count 5 -format full_clock_expanded -digits 6 > $::env(OUTPUT_DIR)/hold_paths.rpt
check_setup -verbose > $::env(OUTPUT_DIR)/constraint_coverage.rpt
report_check_types -max_fanout -max_slew -max_capacitance -violators -verbose > $::env(OUTPUT_DIR)/design_rules.rpt
# Three requested path classes, at real external data/control boundaries.
report_checks -from [get_ports ram_rdata*] -path_delay max -group_path_count 3 -format full_clock_expanded > $::env(OUTPUT_DIR)/hit_data_interface.rpt
report_checks -from [get_ports req_*] -path_delay max -group_path_count 3 -format full_clock_expanded > $::env(OUTPUT_DIR)/allocation_interface.rpt
report_checks -to [get_ports wb_*] -path_delay max -group_path_count 3 -format full_clock_expanded > $::env(OUTPUT_DIR)/wb_interface.rpt
report_checks -from [get_ports wb_ready] -path_delay max -group_path_count 3 -format full_clock_expanded >> $::env(OUTPUT_DIR)/wb_interface.rpt
report_checks -to [get_ports rsp_data*] -path_delay max -group_path_count 3 -format full_clock_expanded >> $::env(OUTPUT_DIR)/hit_data_interface.rpt
report_checks -unconstrained -path_delay max -group_path_count 5 > $::env(OUTPUT_DIR)/unconstrained_paths.rpt
exit
