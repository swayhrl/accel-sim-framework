# Lane 3 — RO production routing r4

Consumes coordination review_r2 aec01450d3c527524ee09ee59242f582fafe5354; supersedes no old pack. R0 B16/U_WB16 remains frozen and has priority. This branch is an integration candidate for Lane 1, not an independently qualified replacement for R0.

The actual l2_cache now binds the conservative certificate, Tag visibility/generation, original GLOBAL_ACC_R predicate, real lower acceptance/sector returns, and same-cycle L2→ICNT response commit. Runtime switches are separate and default OFF. All allocations and pins use Lane 1's sole physical store; all requesters lease the same D512 descriptor free list. No second data RAM or requester pool is introduced.

The full five-workload oracle input pack from r2 is reused unchanged. FWT's empty certificate remains valid negative coverage. No trace re-certification, input hash scan, new workload simulation, or formal performance comparison was performed for this delivery. Directed fixtures use a separate synthetic certificate and symbolic sector versions.

Read SOURCE_MAP.md, QUALIFICATION.md, RO_READY_MANIFEST.json, METADATA_COST.md and the exact patch checks before consuming. The patches apply to the precise frozen R0 parents. Lane 1 owns final integration; Lane 5 must independently qualify this new source/binary and allocate any application runs. Previous Lane 5 module PASS on Core 57801b42 does not qualify r4.
