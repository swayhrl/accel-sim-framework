# Q05 full-kernel translation behavior report — 174-new

`AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_V1_COMPLETE_WITH_SCOPE`

The accepted simulator-native trace covers the full selected Q05 kernel, not the full model: 224 CTA, 896 warp records, 13,361,600 warp-instruction records, 971,824 memory-instruction records, 29,564,416 lane-address events and 228 64KiB VPNs. File order is structural only, not a global cycle timeline.

The complete R0 replay naturally completed at 885,681 cycles with 224 issued CTA. The 10k and 50k bounded windows each had 70 issued CTA, 31.25% of the complete CTA denominator. No valid cycle-keyed denominator exists for window warp/memory/page coverage, so none is fabricated.

The evidence favors a mixed interpretation: strong outstanding-translation fanout exists (125 miss requesters = 19 allocations + 106 merges; waiter depth 35), while the complete offline page popularity is strongly skewed. Frozen aggregate telemetry cannot distinguish first-touch from post-fill reuse on a cycle/key basis; no diagnostic instrumentation was added because it would require a D3 neutrality gate. This stage therefore does not authorize a mechanism experiment.