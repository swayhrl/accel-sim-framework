# VM access UID invariant

A target-only disabled-by-default observer records actual L1 lookup launches and READY deliveries by existing `mem_access_t::get_uid()`. All six rows have `post_ready_retranslation=0`; `launch_gt1_before_ready` is the normal pre-READY L1 re-entry population after a miss path, not a post-READY translation.
