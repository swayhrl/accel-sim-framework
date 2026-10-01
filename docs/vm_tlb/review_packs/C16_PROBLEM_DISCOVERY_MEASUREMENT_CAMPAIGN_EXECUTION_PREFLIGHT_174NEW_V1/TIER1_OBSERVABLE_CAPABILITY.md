# Future Tier1 NCU capability map — no metric collection

The pinned vLLM source is not a pinned 109 profiler environment. Historical C16 NCU reports do not certify a future vLLM v0.30.0 build or exact tool/counter set. `NCU_VERSION_109 = TO_BE_CONFIRMED`, replay/cache-control mode `TO_BE_CONFIRMED`, and every exact metric name remains unresolved until a future 109 canary. Do not request all metrics at once; NCU multi-pass replay can perturb cache state and is not native timing authority.

| Scientific observable | Proposed minimal group | Admission and boundary |
|---|---|---|
| CTA/wave supply | grid/block/SM count and launch geometry | Source/Tier0 first; number of CTAs ≠ saturation. |
| Active warps/occupancy | selected active-warp and occupancy observables | Only for a Tier0-weighted point; distinguish active fraction, theoretical occupancy and launch waves. |
| Resource stalls | selected stall categories | Correlate with native duration; stall percentages are not additive time savings. |
| L1/TEX request service | selected requests/sectors/hit behavior | Name exact read/write sector scope; do not call it all L1 behavior. |
| L2 service | selected read/write sectors and hit/miss | Miss sectors are not automatically DRAM or critical-path cost. |
| DRAM service | selected bytes/transactions | Preserve kernel and runtime attribution; traffic ≠ timing. |
| TLB/PTW/translation blocked time | `UNKNOWN` on Ada until direct validated capability | If no legal SM89 observable, retain `TRANSLATION_TIME_HEADROOM_UNKNOWN`; VA page proxy does not substitute. |

Only ≤3 future Tier1 points and ≤30 active minutes are in the *design* envelope, contingent on Tier0 whole-run weight, legal oracle, correctness and strong software. No NCU was run in this preflight, no metric names are frozen and no Tier1 contract is issued.
