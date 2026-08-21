# Place the twenty ASAP7 Snapshot SRAM macros before tap/PDN generation.
# Names are discovered from the linked design, not guessed from Yosys's
# hierarchy flattening convention.  Five columns x four rows gives each
# 30.348 x 77.760 um macro a 13.652 x 16.240 um signal-routing channel.
set db [ord::get_db]
set block [ord::get_db_block]
set macros {}
foreach inst [$block getInsts] {
    if {[[$inst getMaster] getName] eq "srambank_256x4x64_6t122"} {
        lappend macros [$inst getName]
    }
}
set macros [lsort $macros]
if {[llength $macros] != 20} {
    error "expected 20 C2P ASAP7 Snapshot macros, found [llength $macros]"
}
set macro_i 0
foreach macro $macros {
    set col [expr {$macro_i % 5}]
    set row [expr {$macro_i / 5}]
    set x [expr {16.0 + $col * 44.0}]
    set y [expr {16.0 + $row * 94.0}]
    place_inst -name $macro -location [list $x $y] -orientation R0 -status FIRM
    incr macro_i
}
