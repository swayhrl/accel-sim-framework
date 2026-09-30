# Round19 preparation screen | dLLM, adaptive depth, agentic KV

Date: 2026-09-30. Source/literature boundary screen only.

Three new workload families were checked after the Round17 FlowANN and Round18 Engram closeouts.

- **Diffusion LMs:** real workloads and public code exist, but Flash-dLLM already co-designs KV-cache I/O and parallel verification, while a separate 2026 architecture paper targets diffusion sampling's irregular logit/reduction/masked-update behavior. No generic AWMA memory-I/O claim survives.
- **Adaptive-depth / looped LMs:** public Ouro/Huginn-class models make Native work feasible, but Continuous Depth Batching already performs loop-level scheduling, KV management and asynchronous preparation and reports up to 99% of its estimated maximum adaptive-depth speedup. TIDE/FlexEE further strengthen the software baseline.
- **Agentic/tree KV:** the workload is natural and input authority is strong, but ArborKV, TokenDance, AgentKV, ActKV and ForkKV collectively cover tree-aware retention, sharing, page compaction, action/phase-aware eviction and copy-on-write state.

Decision: `NO_NEXT_CANDIDATE_QUALIFIED_PASS07`.

No new problem card is justified. R102 remains dormant pending authoritative real adjacent working-precision payload.

Execution boundaries: CUDA=0; NSYS/NCU=0; 174/Accel-Sim=0; NVBit/SASS=0; synthetic scientific input=0; accepted-contract change=0; mechanism design=0.
