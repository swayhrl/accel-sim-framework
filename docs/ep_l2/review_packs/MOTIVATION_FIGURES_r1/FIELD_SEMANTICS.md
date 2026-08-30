# EPL2MOTV1 field semantics

The nine reuse bins are exact stack distances over distinct 128-B blocks in
one slice and one kernel epoch. First touches are excluded from the reuse-bin
denominator. The implementation retains 1,025 MRU distinct blocks so that a
distance of exactly 1,024 remains exact; older seen blocks map to `>1024`.

`WB_PATH` is WAD ordering/capacity plus a trace-projected shadow dirty-WB
packet staging capacity. It is not a claim that the baseline has physical
WBUF=4/8/16, nor a performance simulation.

WBUF lives from real WB packet creation through successful `L2interface::push`
into the per-slice L2->DRAM queue. Its release is before channel arbitration,
DRAM issue, and `set_done`; WAD may remain live afterwards. The parser-facing
`wbuf_trace_projected_would_block_cycles` counts eligible frontend
miss-admission cycles/attempts, rather than unique misses.

Application `unique_lines`, `unique_lines_reused_at_least_once`, and
`one_touch_unique_lines` are sums of independent slice/epoch populations. They
are deliberately not global-address deduplications across kernel boundaries.
With distance defined as the number of more-recent distinct lines, `distance <
C` (not `<= C`) is the exact C-entry fully-associative LRU capture condition.
