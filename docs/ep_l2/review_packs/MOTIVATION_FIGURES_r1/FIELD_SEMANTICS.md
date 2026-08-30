# EPL2MOTV1 field semantics

The nine reuse bins are exact stack distances over distinct 128-B blocks in
one slice and one kernel epoch. First touches are excluded from the reuse-bin
denominator. The implementation retains 1,025 MRU distinct blocks so that a
distance of exactly 1,024 remains exact; older seen blocks map to `>1024`.

`WB_PATH` is WAD ordering/capacity plus a trace-projected shadow dirty-WB
packet staging capacity. It is not a claim that the baseline has physical
WBUF=4/8/16, nor a performance simulation.
