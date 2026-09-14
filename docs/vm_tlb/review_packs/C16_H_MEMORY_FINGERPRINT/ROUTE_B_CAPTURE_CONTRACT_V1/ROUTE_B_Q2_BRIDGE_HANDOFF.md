# Route-B Q2 Llama bridge handoff

Q2 is producer qualification, not a representative-selection capture. It runs
only after Q1 passes.

| phase | frozen exact Route-A anchor | historic selected static index |
| --- | --- | ---: |
| PREFILL | `indexSelectLargeIndex` full mangled identity in `route_b_q2_bridge.py` | 101 |
| DECODE | `indexSelectSmallIndex` full mangled identity in `route_b_q2_bridge.py` | 17 |

For each anchor, Lane A must generate a fresh actual-owner, one-function
static map, then freeze every `GLOBAL && has_mref` row and every MREF ordinal.
Historical Route-A maps are not silently promoted because they do not carry
the new width/MREF-count authority.  The structural bridge compares only the
selected-PC dynamic lane instances and VA-bucket cardinality; it never
requires absolute GPU VA equality across processes.
