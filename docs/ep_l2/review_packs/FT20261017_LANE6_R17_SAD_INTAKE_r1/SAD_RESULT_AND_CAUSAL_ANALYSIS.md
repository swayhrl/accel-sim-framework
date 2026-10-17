# Independently ingested SAD negative control

| Metric | B16_BANKED | U_WB16 |
|---|---:|---:|
| Native cumulative cycles | 110773 | 110749 |
| Instructions | 157583646 | 157583646 |
| Completed copy transfers | 3975 | 0 |
| Logical bank operations | 483611 | 475661 |
| Successful send-read grants | 3975 | 3975 |
| WB completed | 3975 | 3975 |
| WB-data-full events | 0 | 0 |
| Pool/eligible-landing failures | 0 | 0 |
| Cumulative bank wait | 2255 | 2233 |
| WAD-full events | 0 | 0 |
| WAD-hazard events | 0 | 0 |
| DRAM write bytes | 508800 | 508800 |

Coverage: Lane6 independently ingested **1/5**, paper numerical coverage **1/5**; Lane5 authority at initial intake accepts **4/5**, generation7, commit `c24816d3c8a7c768c3e254f6c1dc70523e7847ea`. Historical first SAD acceptance0677446/generation4 is retained as provenance, never substituted for current authority. No five-workload chart or group geomean.

Both arms have identical157583646 instructions and identical repaired release/input scope. Cycles decrease by24 (0.021666% relative cycle reduction), B/U=1.000216706246. This single observed near tie has no statistical-significance or equivalence claim. Copy3975→0 and logical operations decrease7950=2×3975, consistent with removing copy read/write work; it is not a unique end-to-end causal proof or a prediction of bank-cycle/energy savings.

Zero WB-data-full/pool/WAD counters and no observed capacity_above_C16 do not establish a capacity benefit for this pair. They do not prove that all possible capacity pressure is absent or that other applications cannot benefit. C1 legacy resident-headroom observations are excluded. The qualified correctness scope is symbolic32B sector versions/requester/WB/64-slice lifecycle under complete native nonatomic input, not numerical SASS payload outputs, atomic accesses, TVD/RO or Ideal.

All values above are independently summed/reparsed from hash-bound raw logs after the existing native adapter and current V2 checks. `SAD_IDENTITY_AND_CLOSURE.json` binds full release/config/trace/raw identities; `SAD_64_SLICE_EVIDENCE.json` preserves per-slice evidence. Runtime totals are native GPU cumulative values, never sums of per-slice cycles. Application bank counters use actual `scope=application` and `interval=application_cumulative`.

Publication closure: current Lane5 generation 8 at `534338ed2219a3e719189c470414152987795fd8` accepts **5/5** pairs. Both SAD rows were rechecked with the unchanged current V2 identity/raw/metrics/withdrawal gates. Lane6 numerical coverage remains **1/5**; all four other pairs are metadata-only prepared adapters, not ingested results. The original generation-7 intake is preserved as historical evidence; `validation/PREPUBLICATION_AUTHORITY.json` supplies the fresh publication binding. No cohort plot or mean is emitted.
