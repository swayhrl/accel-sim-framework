# Translation event schema

`sim_cycle,event_type,asid,vpn,page_size,sid,waiter_uid,waiter_depth,status`

Keys use the frozen `translation_key` fields. Any unavailable field is emitted as `NA`; events are diagnostic-only and controlled by `AWMA_TRANSLATION_TIMELINE_PATH` being nonempty.
