# Modern DTC comparison: capacity-contract decision

Status: **modern DTC rows gated on resource-contract review**. The authorized old-platform paired rows and modern baseline-only diagnosis can continue independently. No new modern DTC row is launched under an implicit budget change.

Concrete implemented conflict: `ldst_unit::init` always constructs the conventional `m_L1D` from the platform config and also constructs a separate640×128B DTC physical pool in PAPER_IO/PAPER_OO. The former is still used by the existing store/atomic side paths. Adaptive per-kernel code in `shader_core_config::max_cta` changes conventional L1 associativity; it does not subtract the DTC physical pool from unified capacity or resize that pool.

Consequently, simply selecting mode2/3 on the frozen4080 config gives the no-shared pilot kernels a conventional128KiB array **plus** dedicated80KiB DTC data:208KiB before metadata. Hotspot's observed conventional96KiB plus32KiB shared similarly becomes96+32+80=208KiB. The mode0 baseline uses the frozen128KiB unified budget. Extra searchable Tag/PIB/Ref/waiter state is additional. Neither the native4080 nor an equal-budget comparison is represented by silently activating mode2/3.

Two concrete interpretations are available for review:

1. **Additional dedicated80KiB hypothetical organization.** Preserve current routing and conventional adaptive allocation, report the total208KiB data/shared budget and unequal resources prominently, and make only a simulation/counterfactual claim. This is implementable with configuration and the qualified finite service; it cannot support a same-budget or native4080 DTC speedup claim.
2. **Fixed128KiB unified budget.** Reserve80KiB for DTC, leaving at most48KiB conventional/shared capacity. A new allocator/partition/domain definition is required. Merely replacing unified128 by48 is not a general solution: the platform's64/100KiB shared options would no longer fit, and changing supported shared capacity, side-path allocation or routing crosses the current legal-capacity/protocol boundary. Specify that contract before implementation; do not silently shrink the supported domain or change stores/atomics.

Source anchors: Core `78947aa2e4e8197e14d97d5989109865c6669216`, `src/gpgpu-sim/shader.cc` (`ldst_unit::init`, `dtc_l1_io_memory_cycle`, `dtc_l1_oo_memory_cycle`, `shader_core_config::max_cta`), `src/gpgpu-sim/shader.h` (separate frontend/ordinary-cache ownership); frozen Framework4080 asset `8d1f14a32f5538660d74da86ccb03a2c504c5735`. Baseline startup already confirms128KiB on BICG/Btree/2D and96KiB on Hotspot.

Applicable stop rule in `handoffs/parallel_closure_v1/GOAL_174.md`, R1: “If a necessary fix changes … legal-capacity definition … publish the concrete issue and STOP before that change.” This is a resource/applicability decision, not a build/launcher failure. Preserve all existing evidence. No enlarged-budget result may be relabelled equal-budget, and no fixed-budget implementation proceeds without the new contract.
