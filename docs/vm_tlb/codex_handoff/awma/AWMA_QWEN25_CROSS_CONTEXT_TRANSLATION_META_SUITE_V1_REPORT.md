# AWMA Qwen2.5 cross-context translation meta-suite V1

Stage: AWMA_QWEN25_CROSS_CONTEXT_TRANSLATION_META_SUITE_V1
Status: META_SUITE_DESIGN_FOR_REVIEW

The accepted S2 BALANCED suite is a 25-target common structural core for
S2, T256, T8192, B4, and D128. Source Native structure and scenario
duration select 20 extension groups with 28 actual measurement targets.
The combined planning meta-suite has 53 unique targets instead of five
independent 25-target lists.

The S2 BALANCED-only Level 3 exact Native-time coverage is 89.96% (S2),
79.21% (T256), 39.04% (T8192), 7.13% (B4), and 87.05% (D128).
The proposed meta-suite raises these to 90.96%, 89.87%, 90.86%,
80.03%, and 93.95%, respectively. Level 2 implementation/recurrence
and Level 1 archetype coverage use their own nested, scenario-specific
mass numerators and are reported separately.

The five S2 Decode GEMV shapes remain exact in T256 and T8192.
T256 Flash shares splitkv/combine implementation families while shape or
template specialization changes. Long-context Prefill Flash and GEMM
dominate T8192-specific high-mass extensions. B4 has no Decode GEMV;
68,254,217 ns of Decode GEMM and 29,655,318 ns of Decode Flash
establish a dispatch-family shift without proving model-operator
equivalence. D128 extends the same 48-per-step elementwise trajectory
through 96 new step 33–128 grids totaling 28,654,328 ns.

The requested cluster map, coverage, target manifests, and
capture-priority ranking are in
docs/vm_tlb/review_packs/AWMA_QWEN25_CROSS_CONTEXT_TRANSLATION_META_SUITE_V1/.
All missing trace entries are planning only. No GPU, trace capture,
Accel-Sim, mechanism, C1, or Lane B operation was performed.
