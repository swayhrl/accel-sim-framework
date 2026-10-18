# DC R3 UNRUN by Lane2. Same RTL/parameters/controller timing cut as open flow.
# Required real library values; never upload target DBs/Liberty to GitHub.
foreach key {RTL_REPO TARGET_LIBS LINK_LIBS DC_OUT MODE IO_DRIVE_CELL OUTPUT_LOAD_LIB_UNITS PVT_LABEL OPERATING_CONDITIONS LIB_TIME_UNIT_NS} {
    if {![info exists ::env($key)] || $::env($key) eq ""} { error "Missing required environment $key" }
}
puts "DC PVT_LABEL=$::env(PVT_LABEL); physical time converted by declared LIB_TIME_UNIT_NS=$::env(LIB_TIME_UNIT_NS); verify report_units"
set mode $::env(MODE)
if {[lsearch -exact {0 1 2} $mode] < 0} { error "MODE must be 0=B16,1=Unified,2=S64" }
set wb [expr {$mode==2 ? 64 : 16}]
set target_library $::env(TARGET_LIBS)
set link_library "* $::env(LINK_LIBS)"
foreach lib [concat $target_library $::env(LINK_LIBS)] {
    if {$lib ne "*" && ![file exists $lib]} { error "Library not found: $lib" }
}
file mkdir $::env(DC_OUT)
# Exact private DB identity is recorded only when this entry actually runs.
# Tcl exec passes each path as one argument; there is no shell interpolation.
set library_identity [open $::env(DC_OUT)/library_sha256.txt w]
foreach lib [concat $target_library $::env(LINK_LIBS)] {
    if {$lib ne "*"} { puts $library_identity [exec sha256sum -- $lib] }
}
close $library_identity
define_design_lib WORK -path $::env(DC_OUT)/WORK
set sources [list]
set f [open $::env(RTL_REPO)/rtl/ep_l2/flow/filelist.f r]
while {[gets $f line]>=0} { if {$line ne "" && ![string match "#*" $line]} { lappend sources $::env(RTL_REPO)/$line } }
close $f
analyze -format sverilog -define SYNTHESIS $sources
elaborate ep_l2_slice_ctrl -parameters "MODE=$mode,STATIC_WB=$wb,N_TAG=1024,N_PAYLOAD=1168,N_WAD=128,GEN_W=32"
# Parameterized elaboration may give the top a parameter-suffixed design name.
# Retain the actual current top selected by elaborate; never assume the base name.
set elaborated_top [current_design]
if {$elaborated_top eq ""} { error "elaborate did not select a current top" }
puts "DC_ELABORATED_TOP=$elaborated_top"
link
# Actual operating-condition name from the selected real DB, not a label.
set_operating_conditions $::env(OPERATING_CONDITIONS)
report_design > $::env(DC_OUT)/design_environment.rpt
report_units > $::env(DC_OUT)/units.rpt
check_design > $::env(DC_OUT)/check_design.rpt
source $::env(RTL_REPO)/rtl/ep_l2/flow/common.sdc
compile_ultra
report_area -hierarchy > $::env(DC_OUT)/area.rpt
report_timing -delay_type max -max_paths 10 -input_pins -nets -transition_time > $::env(DC_OUT)/timing.rpt
report_constraint -all_violators > $::env(DC_OUT)/constraints.rpt
report_qor > $::env(DC_OUT)/qor.rpt
check_timing > $::env(DC_OUT)/check_timing.rpt
write -format verilog -hierarchy -output $::env(DC_OUT)/mapped.v
write_sdc $::env(DC_OUT)/mapped.sdc
write -format ddc -hierarchy -output $::env(DC_OUT)/mapped.ddc
quit
