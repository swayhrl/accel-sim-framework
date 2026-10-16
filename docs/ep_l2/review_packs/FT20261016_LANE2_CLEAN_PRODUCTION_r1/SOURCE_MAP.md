# Actual producer bindings

- ep-l2-ft-cache.inc::ft_access: selected clean victim, disjoint bank-compatible landing, successful production commit -> retained role; mandatory WB reservation uses shared directory. Existing reserve/pin/transfer/request APIs from exact R0 are reused.
- ep-l2-tvd-cache.inc::tvd_frontend: actual Tag miss, +1 cycle, sector readiness, shared bank request; called BEFORE normal preview/WAD rejection in memory_sub_partition::cache_cycle.
- cache_cycle actual L2-to-ICNT push -> tvd_response_commit: requester admission/response exact-once audit and allocator pin retirement.
- tvd_promote: bank-compatible resident way, same handle; dirty victim produces a real L2_WRBK_ACC and reuses the directory address slot atomically.
- lower_accepted / ep_l2_wad_complete: real lower-data ownership and true set_done remain distinct. Dirty candidate code is not production-qualified in this clean checkpoint.
- memory_sub_partition::flushL2/invalidateL2 -> l2_cache cleanup: refuses mandatory/pinned loss and reclaims opportunistic handles.
- test_tvd_production.cc: real partition tests; no replacement toy cache. Test-only bank-conflict injection uses the actual R0 public arbiter.
