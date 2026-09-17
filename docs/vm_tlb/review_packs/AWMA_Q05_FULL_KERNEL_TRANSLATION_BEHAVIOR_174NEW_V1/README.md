# Q05 full-kernel translation behavior — 174-new

Completion: `AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_V1_COMPLETE_WITH_SCOPE`.

This is pre-mechanism diagnostic characterization. It does not modify frozen identities, trace semantics, translation timing, or simulator functional behavior.

The complete Q05 trace has 224 CTA records, 896 warp records, 13,361,600 warp-instruction records, 971,824 memory-instruction records, 29,564,416 lane-address events and 228 unique 64KiB VPNs. Trace file order is `STRUCTURAL_TRACE_ORDER_ONLY`, not a cross-CTA simulator-cycle timeline.

Natural R0 completion reached 885,681 cycles and 224 issued CTA. 10k and 50k each issued 70 CTA (31.25% CTA-issued coverage). Completed CTA and cycle-ordered per-VPN page coverage are unavailable in frozen telemetry.