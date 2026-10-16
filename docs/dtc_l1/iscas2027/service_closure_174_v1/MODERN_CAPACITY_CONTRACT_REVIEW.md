# RTX4080 fixed128KiB allocation and service review

Current decision consumed in full: Framework `e13266ba207d8b8e47b56d62dfdb8bd04c8e2c5b`, [review decision](../handoffs/parallel_closure_v1/MODERN_4080_CAPACITY_AND_109_REVIEW_DECISION_2026-10-16.md). It was merged into this progressed branch without resetting. **Modern DTC remains HOLD; zero modern DTC performance rows launched.** Only option2 below is authorized. Baseline-only and the64-SM main line continue. The initial issue text is retained below, followed by the concrete CPU audit.

Status: **modern DTC rows gated on resource-contract review**. The authorized old-platform paired rows and modern baseline-only diagnosis can continue independently. No new modern DTC row is launched under an implicit budget change.

User decision received2026-10-16: **keep the total128KiB budget; review the new allocation/support-domain contract first; do not launch modern DTC rows yet**. The additional80KiB/208KiB interpretation is not authorized. Prepare the fixed-budget proposal without implementing a changed legal-capacity definition.

Concrete implemented conflict: `ldst_unit::init` always constructs the conventional `m_L1D` from the platform config and also constructs a separate640×128B DTC physical pool in PAPER_IO/PAPER_OO. The former is still used by the existing store/atomic side paths. Adaptive per-kernel code in `shader_core_config::max_cta` changes conventional L1 associativity; it does not subtract the DTC physical pool from unified capacity or resize that pool.

Consequently, simply selecting mode2/3 on the frozen4080 config gives the no-shared pilot kernels a conventional128KiB array **plus** dedicated80KiB DTC data:208KiB before metadata. Hotspot's observed conventional96KiB plus32KiB shared similarly becomes96+32+80=208KiB. The mode0 baseline uses the frozen128KiB unified budget. Extra searchable Tag/PIB/Ref/waiter state is additional. Neither the native4080 nor an equal-budget comparison is represented by silently activating mode2/3.

The initial review recorded these two interpretations; option1 is now rejected:

1. **Additional dedicated80KiB hypothetical organization.** Preserve current routing and conventional adaptive allocation, report the total208KiB data/shared budget and unequal resources prominently, and make only a simulation/counterfactual claim. This is implementable with configuration and the qualified finite service; it cannot support a same-budget or native4080 DTC speedup claim.
2. **Fixed128KiB unified budget.** Reserve80KiB for DTC, leaving at most48KiB conventional/shared capacity. A new allocator/partition/domain definition is required. Merely replacing unified128 by48 is not a general solution: the platform's64/100KiB shared options would no longer fit, and changing supported shared capacity, side-path allocation or routing crosses the current legal-capacity/protocol boundary. Specify that contract before implementation; do not silently shrink the supported domain or change stores/atomics.

Source anchors: Core `78947aa2e4e8197e14d97d5989109865c6669216`, `src/gpgpu-sim/shader.cc` (`ldst_unit::init`, `dtc_l1_io_memory_cycle`, `dtc_l1_oo_memory_cycle`, `shader_core_config::max_cta`), `src/gpgpu-sim/shader.h` (separate frontend/ordinary-cache ownership); frozen Framework4080 asset `8d1f14a32f5538660d74da86ccb03a2c504c5735`. Baseline startup already confirms128KiB on BICG/Btree/2D and96KiB on Hotspot.

Applicable stop rule in `handoffs/parallel_closure_v1/GOAL_174.md`, R1: “If a necessary fix changes … legal-capacity definition … publish the concrete issue and STOP before that change.” This is a resource/applicability decision, not a build/launcher failure. Preserve all existing evidence. No enlarged-budget result may be relabelled equal-budget, and no fixed-budget implementation proceeds without the new contract.

## Current ownership and per-kernel audit

Current Core is `6fba0136f8465b59fe5858a950fa39efb265f654`. `shader.cc:4291` constructs the conventional `l1_cache` before constructing separate IO/OO physical slots (`shader.cc:4343`, `dtc-l1-common.h:167,496`). `max_cta` (`shader.cc:6382`) limits CTAs by threads/registers/shared, clamps to the grid, selects the shared option, then resizes only the ordinary cache. The unified-size option controls its maximum geometry through `l1d_cache_config::get_max_cache_multiplier` (`gpu-cache.h:936`). Nothing deducts DTC slots or establishes disjoint DTC/ordinary/shared ranges.

The logical128×128B search coverage is **128 mappings, not another16KiB data array**. Physical640×128B slots represent80KiB retained DTC data. The trace simulator represents ownership/readiness rather than checking architectural load values in these slots. Host object sizes do not establish SRAM capacity or functional-value validation. Tag/PIB/Ref/waiter/generation state is additional metadata with separate cost.

`memory_cycle` (`shader.cc:3879`) sends eligible cacheable non-atomic loads to DTC. Stores, atomics and bypass operations retain their source routes; conventional cache/bypass response ownership remains live. Removing the ordinary cache would change these routes.

The complete six-kernel table, SHA identities, full trace CTA coverage and CTA arithmetic are in [ALLOCATION_PROPOSAL_AUDIT_V1.tsv](review_pack/modern_capacity_v2/ALLOCATION_PROPOSAL_AUDIT_V1.tsv). BICG's printed architectural CTA/core=6 precedes the grid clamp: its16-block grid over76SMs imposes cap1, not6.

| Kernels | Observed baseline shared / L1 KiB | Resident shared demand | Proposed DTC / ordinary / shared KiB | CTA cap before/after carve-out |
|---|---|---|---|---|
| BICG1,2 | 0 /128 | 0 | 80 /48 /0 | 1 /1 |
| Btree findRangeK, findK | 0 /128 | 0 | 80 /48 /0 | 6 /6 |
| 2DConvolution | 0 /128 | 0 | 80 /48 /0 | 6 /6 |
| Hotspot1 | 32 /96 | 6×3072B=18KiB | 80 /16 /32 | 6 /6 |

These are possible byte partitions, **not an implemented organization**. All629 frozen kernels have CPU-only calculations in [FROZEN629_CAPACITY_CALCULATION_V1.tsv](review_pack/modern_capacity_v2/FROZEN629_CAPACITY_CALCULATION_V1.tsv): modeled shared options0/8/16/32KiB, ordinary remainder48/40/32/16KiB after80KiB DTC. Arithmetic feasibility for these inputs does not qualify modern execution or authorize reducing the supported platform shared domain. No additional application was run for this audit.

## Service and legal-domain gap

| Resource | Existing source/registered service | Fixed-budget audit |
|---|---|---|
| Ordinary L1 | four bank/latency queues;32-cycle latency;32B data port and32B fill port in `baseline_cache::bandwidth_management` (`gpu-cache.cc:1191,1223`) | Its data capacity and ports remain charged for existing routes. |
| DTC lookup/allocation | four Tag banks; one-cycle lookup; four successful allocations/core-cycle; current LD/ST multiplier1 limits delivered initiation | Search/control state is separate metadata. |
| DTC refill/collection | one32B refill/core-cycle; four32B collected sectors/core-cycle | Current quotas are independent of ordinary ports and shared bank service; capacity subtraction does not prove physical sharing. |
| Shared |32 banks,29-cycle pipeline, dispatch bank-conflict handling (`shader.cc:2427`) | No joint bank arbitration with the DTC resources is represented. |
| Completion | common operand collector; successful retirement≤1/core-cycle | This is already shared and qualified by R1; it does not establish SRAM-port sharing. |

R1 intentionally declares aggregate collection/refill resources with **no invented data-bank mapping**. A config-only carve-out cannot establish the requested storage-and-port organization. Keeping independent ports on disjoint subarrays needs an explicit physical/banking/resource organization and cost; common ports need an arbiter and contention timing. Neither is represented or qualified by R1. No additional ports are assumed free; no equal-area claim is made.

A general-domain conflict also remains: the frozen platform supports shared options64/100KiB and48KiB per CTA. With100KiB shared, effective L1 is28KiB, less than the80KiB pool before any ordinary storage. Setting unified48KiB and truncating shared options to32KiB would fit the pilot but silently narrow the legal domain. **That edit was not made.** Dynamically shrinking DTC changes physical-capacity/progress premises and requires its own legality/service definition.

The smallest reviewable implementation proposal touches option registration, conventional cache construction/max-allocation geometry, `max_cta` partition accounting, DTC/ordinary data-port accounting and per-kernel drain/partition checks. It must retain original shared resources/CTA limits and access routes, prove `P_k+C_k<=L_k` without overlap, and specify behavior when `L_k<80KiB`. Rejecting formerly legal kernels is not a proof of unchanged legal domain. This crosses the decision's new-organization/legal-capacity boundary. **No source or executable config implementing it has been changed.** Hold only modern DTC for review; continue the independent main line and baseline-only evidence.

The initial CPU proposal is preserved in `review_pack/modern_capacity_v1`; V2 adds all629 kernels and explicitly rejects interpreting its32KiB proposal limit as platform authority. Input/source/log hashes are retained. No incomplete average, native DTC speedup or4.7% original-platform area transfer is authorized.
