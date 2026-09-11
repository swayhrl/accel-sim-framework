# PWC tradeoff audit

F5-vs-F0 uses exact per-kernel checkpoint deltas, with a separate formal
full-ROI cycle anchor. The physical F5 configuration reduces L2-TLB capacity
from 768 to 656 entries; its measured PWC counter changes are kept distinct
from TLB/PTW counters.

## Measured tradeoff

| ROI | full-ROI cycle delta | L2-TLB miss delta | walk delta | PTE-DRAM delta | PWC-hit delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| Prefill | +733,075 | +69,793 | +18,355 | +15,891 | +55,060 |
| Decode1 | -5,780 | -92 | 0 | -5 | +10 |

Prefill's largest exact regression is direct Embedding/Output kernel 691
(+700,253 cycles), accounting for 78.0% of its absolute per-kernel change.
At operator level Embedding/Output carries +63,780 L2 misses, +17,658 walks,
and +15,693 PTE-DRAM responses; direct FFN contributes only +824 cycles and
Attention Projection -1,260 cycles. Decode has no comparable hotspot and its
full-ROI effect is near zero.

## Interpretation

The Prefill co-occurrence of more PWC hits with more L2 misses/walks/PTE-DRAM
and a cycle regression is a `SUPPORTED_MECHANISM_SIGNAL`: the capacity tradeoff
is a credible hypothesis, especially at the final Embedding/Output GEMM. It
does not prove that a particular PWC hit or TLB eviction caused a particular
cycle, nor does it isolate a counterfactual capacity-only intervention. A
future replay must independently vary L2-TLB capacity and PWC enablement.

`PWC_TRADEOFF.tsv` supplies all direct operator rows and Top-20 regression
kernels, including PWC accesses/hits/misses, without turning PWC activity into
a causal saving claim.
