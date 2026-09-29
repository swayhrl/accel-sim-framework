
# Excluded profile attempt

Initial F128 and K128 NCU reports passed output/path checks but omitted `smsp__inst_executed_op_ldgsts.sum`, despite this metric being supported. Static SASS exposed a substantial LDGSTS opcode class in K128, which the direct LDG/LD counter does not cover. The first reports, initial metric preregistration and initial aggregates were moved under node164 `raw/ATTEMPT0_OMITTED_LDGSTS_METRIC/` and `raw/ncu/<arm>/ATTEMPT0_OMITTED_LDGSTS_METRIC/` with an explicit OBSOLETE status. Exactly one bounded same-input/source/config metric-engineering retry per arm supplies the final counters. No performance or counter value was used to choose the repair.
