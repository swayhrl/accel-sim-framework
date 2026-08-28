# Memory-partition arbitration audit

## Return capacity

The official `can_issue_to_dram(spid)` checked `dram_L2_queue_full()` before
inspecting the request.  That coupled all L2→DRAM traffic to return capacity.
The corrected interface receives the head `mem_fetch` and classifies only
`L1_WRBK_ACC` and `L2_WRBK_ACC` as no-return traffic.  Reads and normal stores
retain their existing return behavior.

No-return writebacks still require real DRAM scheduler availability.  They may
use one explicit channel-local progress credit when general credits are fully
occupied.  The credit is recorded against the precise `mem_fetch` and is
released exactly once in `set_done()`.

## Scheduler head-of-line audit

Both DRAM issue loops formerly used `break` when a selected request class found
its scheduler queue full.  With separate read/write scheduler queues this can
falsely prevent a later subpartition from issuing an admissible opposite-class
request.  The corrected loops use `continue`: they still issue at most one
request per channel cycle and do not change FR-FCFS scheduling, but inspect the
remaining subpartitions for a request that the existing scheduler accepts.

## Non-goals

This audit does not create a new lower-read-credit design, additional response
virtual channels, an unlimited writeback bypass, or a different DRAM scheduler.
