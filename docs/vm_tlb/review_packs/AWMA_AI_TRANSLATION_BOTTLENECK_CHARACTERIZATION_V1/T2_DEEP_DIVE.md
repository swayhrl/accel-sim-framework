# T2 deep dive

T2's frozen V1 10/80-to-0/80 sensitivity is **10.3568%** (93,079 versus 83,439 cycles). At 10/80, the L1 TLB hit rate is 99.436% and the L2 hit rate among L1 misses is 40.567%.

The aggregate request-to-completion total is decomposed as follows: L1 service 77.41%, MSHR/merged-request wait 16.30%, L2 service 3.49%, L2 queue 0.73%, and `UNATTRIBUTED_TRANSLATION_RELATED` 2.06%. Average requester latency is 12.92 cycles. These are aggregate requester-cycle shares, not additive global critical-path cycles.

There are 134 walk starts and 134 completions, 1,249 merges, MSHR high-water mark 9, no MSHR-full event, and no PWQ-full event. The accepted receipts expose only final-zero PWQ/walker occupancy, not their high-water marks; therefore the defensible statement is **no source-supported saturation evidence**, not proof that instantaneous saturation never occurred.

The strongest classification is `HIT_PATH_EXPOSURE_DOMINANT`. MSHR wait is a secondary component. L2 miss service/PTW and queueing are not dominant in the available decomposition. The difference between aggregate requester latency and global cycle sensitivity also supports bounded scheduling/concurrency coupling, but the data do not justify relabeling that coupling as a new translation mechanism.
