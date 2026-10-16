# Counter definitions

Counters are cumulative per directory instance. `read_responses` increments only on successful response-commit, once per lease. `dirty_forward_responses` is its subset begun while WB staged/inflight. `avoided_lower_sectors` counts popcount(requested valid mask), and bytes=32*sectors; no assumption that a 128B frontend request equals one lower transaction. End-to-end avoided lower transactions additionally require matched production OFF/ON lower-issue counts.

`clean_installs`, `dirty_installs`, `promotions`, `reclaimed`, `cancelled_reads`, `lower_accepts`, `wb_completions` count successful transitions, not retry attempts. Preview calls mutate no statistics. `wb_staging_slot_cycles` integrates retained WB_STAGED entries; `tvd_extra_retention_slot_cycles` integrates retained WB_INFLIGHT and WB_COMPLETE after true lower acceptance. Snapshot with `advance(now)` at observation/epoch boundaries.
