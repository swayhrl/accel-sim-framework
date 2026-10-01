# C16 Stage A dense-first Tier0 current state

Status: `STAGEA_TIER0_CONSUMER_PARTIAL` (174-new independent raw closure). Contract `fad9da8116c8ad794f99a93f153b0866162158a4`, producer `82788c2d587e86f94791d65aaa2bde28929f9303`, consumer branch `hrl/c16-stagea-dense-first-tier0-independent-consumer-174new-v1`. All 89 164 raw files independently rehashed PASS; producer numeric crosscheck 52261/52261 cells MATCH.

MP01 BF16 prefill and MP05 AWQ representation control are the only admitted complete points. MP02 BF16 B1 decode and MP03 BF16 B4 decode failed Graph-OFF token correctness and stopped before observed/NSYS; their native timing is quarantined. All four DQ questions are `QUESTION_INCOMPLETE`; zero project-level Tier0 survivors. MP01 has material Graph-OFF producer→consumer chronology, but no causal hardware handoff claim. Graph-ON 85% matched DQ2 absorption and comparable whole-run 2% ceiling are not identifiable. Do not claim `NO_NEW_ARCHITECTURAL_PHENOMENON_FOUND` from incomplete coverage.

Review pack: `docs/vm_tlb/review_packs/C16_STAGEA_DENSE_FIRST_TIER0_INDEPENDENT_CONSUMER_174NEW_V1/`. No freeze-receipt draft, holdout, Tier1, GPU, simulator or mechanism work is authorized by this closure. STOP for project review.
