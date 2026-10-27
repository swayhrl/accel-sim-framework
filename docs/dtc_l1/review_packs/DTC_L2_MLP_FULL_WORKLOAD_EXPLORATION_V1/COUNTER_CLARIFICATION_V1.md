# Counter interpretation clarification V1

Some analysis drafts described L2 failure-reason counters as unprinted. That inference was incorrect: the frozen result proof did not extract them. The original raw logs already contain reason breakdowns. The targeted V2 sidecar verifies closed natural completion, compressed/uncompressed raw SHA and exact line/UID/stream/UUID provenance. This changes analysis coverage, not raw results, strict acceptance, input identity, model source or cycles.

heartwall DH P0/M8/M16 shows GLOBAL_ACC_R MSHR_MERGE_ENRTY_FAIL at raw lines2508/2508/2509 with values241/207/144. The printed totals match the read reservation-failure aggregate for these records. vectorAdd DH-E384 raw lines25906/25907 show MISS_QUEUE_FULL=5,471,878 reads+14,318 writes=5,486,196, equal to its available aggregate. Other unprinted reasons are not zero-filled.

The launch checkpoint's statements about missing reason fields refer to frozen proof coverage; they must not be used as evidence that the original raw lacks those counters. Current analysis must use agents/D/current_results_analysis_v1/REPORT_V2.md and RAW_REASON_ADDENDUM.json. V1 source artifacts remain preserved at their original paths and are not promoted over V2.

Core9eedb313 gpu-sim.cc1866 prints gpu_stall_icnt2mem under the label gpu_stall_dramfull. Lines2463–2467 increment it for blocked ICNT-to-subpartition admission. It can exceed whole-input cycles because it aggregates events across subpartitions. It is not a measured DRAM queue latency. histogram DH-P0 has395,635 such events,98,202 cycles and zero DRAM read atoms.

All35 frozen inputs have one stream each, verified from7,368 qualified headers; last per-stream cumulative L2 buckets therefore cover each declared trace. This does not establish whole-application numerical correctness. Missing latency remains missing, and last printed averages are not summed or represented as application-weighted values. Complete source contexts are preserved in coordinator/counter_scope_v1/SOURCE_SCOPE_EVIDENCE.json and agents/D/current_results_analysis_v1/SOURCE_COUNTER_SCOPE_V2.json.
