# Served data and actual lower traffic

`served_sectors` counts requested 32B sectors exactly once at successful real TVD response enqueue. `served_sector_bytes = 32 * served_sectors`; partial requests use their actual mask. These are response service counts. `dirty_forward_responses` records the lease being mandatory at its accepted read, not a post-hoc classification at set_done.

Old directory fields `avoided_lower_sectors` / `avoided_lower_bytes` are explicitly DEPRECATED SERVED-only compatibility aliases. Their values do not measure avoided lower or DRAM transfers. The production EPL2TVDV2 summary uses served names only. Native Tag/cache counters omit the side-service TVD path; report TVD and native denominators separately. Existing requester audit records the real direct admission before response and commits it exactly once.

The matched OFF/ON directed scenario uses the same final source/binary, ordered config files and stimulus. Only clean TVD changes. Actual lower read packets/bytes increment at the real lower_accepted hook after memport push, including OFF. Observed OFF=2 packets/64B, ON=1 packet/32B. These are actual lower-boundary request bytes for this directed sequence; they are not measured DRAM transfer bytes or application acceleration. A separate DRAM metric and independently qualified application pair would be needed for either claim.

`role_tvd` is part of physical payload conservation; WB_STAGED remains WB role, retained lower-accepted data transfers to TVD role/TVD_INFLIGHT, set_done -> TVD_VALID. New free slots exclude all TVD slots. Consumers must add TVD to the role sum rather than use the old R0 three-role equation unchanged.

`retention_slot_cycles` currently accounts only retained dirty data in WB_INFLIGHT/WB_COMPLETE after lower acceptance. The separate directory `wb_staging_slot_cycles` covers mandatory WB_STAGED. Clean retention duration is not included in this field (a clean-only test can legitimately show zero); do not interpret it as total clean+dirty occupancy or area. Wait counters are per frontend service attempt/cycle at lookup, WB, bank or ICNT boundary and need the supplied scope, not a fabricated global stall sum.
