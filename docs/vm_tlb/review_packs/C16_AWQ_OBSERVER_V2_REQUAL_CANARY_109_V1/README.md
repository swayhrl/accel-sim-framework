# C16 AWQ Observer V2 requalification canary — node109

Final decision: `OBSERVER_V2_NEUTRALITY_PASS`.

This is an observer-neutrality qualification only. It is not a Tier0 scientific
measurement and does not authorize Tier0 execution.

The authoritative six native samples used the frozen order
`OFF, ON, ON, OFF, OFF, ON`. The host-wall medians were 54.955816 ms OFF and
57.840243 ms ON, an absolute delta of 2.884427 ms against the unchanged
5.495582 ms gate. The request-level CUDA Event medians were 54.945057 ms OFF
and 57.830399 ms ON, an absolute delta of 2.885342 ms against the 5.494506 ms
gate. Both pass.

All six outputs produced the exact token sequence `[785, 9234, 330, 90371]`.
The semantic order/shape receipt contains exactly 576 occurrences and matches
the accepted V1 semantic hash. OFF and ON each contained 1,850 CUDA kernel
activities with the same exact inventory SHA256
`2212bbf7bb4d8cfdc7c8ba0a3e310594d33882ac868646f6f3a6f11b3a45e8fe`.
Runtime identity remained `AutoAWQMarlinLinearMethod` /
`MarlinLinearKernel` with `NO_REQUANTIZATION`.

The final NSYS `cuda,nvtx` trace contains one target outer range, 576 semantic
ranges with ordinals 0–575, and CUDA runtime/kernel activity inside the target
range. It is structural evidence only and no timing from it enters the native
neutrality statistics.

Three lock acquisitions are retained transparently. The first two stopped on
NSYS packaging issues and did not cause a native rerun; the third produced the
formal structural trace. All locks were released, and cumulative GPU-active
time was 40 seconds against the 60-second cap.

Accordingly, `MP05_RUNTIME_STATUS = RUNTIME_READY_WITH_OBSERVER_V2`. Observer
V3, threshold changes, and automatic Tier0 startup remain forbidden.
