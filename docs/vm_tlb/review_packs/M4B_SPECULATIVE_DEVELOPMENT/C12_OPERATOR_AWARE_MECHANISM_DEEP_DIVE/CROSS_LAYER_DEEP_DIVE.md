# Cross-layer mechanism deep dive

`OPERATOR_CROSS_LAYER_DECOMPOSITION.tsv` records exact per-kernel aggregates
for the requested comparisons. It preserves the chain as observations:
`TLB → PTW/PTE → requester latency → KERNEL-scope cache outcomes → cycles`.
It does not claim that adjacent rows establish causality.

## Segment: measured phase contrast

Decode1 F7 reduces formal translation walks from 15,691 to 170 and PTE-DRAM
responses from 4,134 to 104 at every Lseg point. At Lseg=5, direct FFN,
Attention Projection, and Embedding/Output cycle deltas are -493,157,
-49,897, and -33,281; at Lseg=20 they become +870,760, +28,552, and
+594,778 despite the same qualitative slow-path reduction. The requester
translation-latency deltas likewise switch positive at Lseg=20 for all three
classes (+28.17M FFN, +4.26M Attention Projection, +33.74M
Embedding/Output cycles). This is a measured association between higher
lookup setting / requester latency and the phase transition from benefit to
regression, not a proof of a unique downstream bottleneck.

Prefill is importantly different. F7 records approximately 47.9–49.6M
Segment hits/L2 suppressions, but its formal walks and PTE-DRAM responses are
higher than F0 (for example F7-L5: +12,934 walks and +21,086 PTE-DRAM).
Consequently, a Segment suppression counter cannot be equated with a global
traditional-walk reduction in Prefill. The exact cycle response is instead:
FFN -2,728,133 / -95,170 / +7,444,348 and Attention Projection -583,390 /
-74,971 / +1,716,774 at Lseg=5/10/20; Embedding/Output regresses at all three
points (+821,231 / +1,101,745 / +4,157,697). This is why the same aggregate
Segment activity cannot by itself explain Prefill performance.

## F1/F2 and F5/F0 observations

Prefill F1-vs-F2 adds 455,615 full-ROI cycles while adding 31,576 L2-TLB
misses, 8,321 walks, 6,640 PTE-DRAM responses, and 11.95M requester-latency
cycles. The dominant exact cycle contributor is kernel 691 (+483,963 cycles).
These co-movements support a diagnosis target; they do not prove that one of
the translation counters caused the cycle change.

Prefill F5-vs-F0 adds 733,075 full-ROI cycles together with +69,793 L2-TLB
misses, +18,355 walks, and +15,891 PTE-DRAM responses, while PWC hits increase
by 55,060. The contrast is a strong tradeoff signal, but replacement/capacity
counter correlation remains short of causal proof. Decode1 F5-vs-F0 changes
only -5,780 cycles, with -92 L2 misses, zero walk change, -5 PTE-DRAM, and
+10 PWC hits.

## Cache and memory boundary

The decomposition TSV includes exact KERNEL-scope L1D/L2 outcomes and
reservation failures per operator. Those transactions are deliberately not
added to TLB counts. Queue and native-memory summaries remain out of the
per-kernel chain because their emitted scope is not kernel-exact. Therefore no
unique cache/queue/memory explanation for the residual cycle movement is
claimed; that downstream mechanism remains `UNRESOLVED`.
