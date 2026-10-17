# Additional diagnosis ONLY. Does not alter the canonical SDC/primary WNS.
foreach key {LIBERTY NETLIST OUTPUT_DIR RTL_ROOT IO_DRIVE_CELL OUTPUT_LOAD_LIB_UNITS LIB_TIME_UNIT_NS CLOCK_PERIOD_NS} {
 if {![info exists ::env($key)]} { error "missing $key" }
}
read_liberty $::env(LIBERTY)
read_verilog $::env(NETLIST)
link_design ep_l2_slice_ctrl
source $::env(RTL_ROOT)/flow/common.sdc
report_wns -digits 6 > $::env(OUTPUT_DIR)/primary_wns.rpt
report_tns -digits 6 > $::env(OUTPUT_DIR)/primary_tns.rpt
# Filters disclose normal sequential/control path depth alongside reset fanout.
# reset remains timed in primary_wns/tns. No case-analysis/false/multicycle.
report_checks -from [all_registers -output_pins] -path_delay max -group_path_count 10 -format full_clock_expanded -fields {slew capacitance fanout} -digits 6 > $::env(OUTPUT_DIR)/register_data_paths.rpt
report_checks -from [get_ports req_*] -path_delay max -group_path_count 5 -format full_clock_expanded -fields {slew capacitance fanout} -digits 6 > $::env(OUTPUT_DIR)/request_paths.rpt
exit
