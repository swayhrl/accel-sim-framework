# Pass06 | bounded next-candidate screen after Engram closeout

Date: 2026-09-30

Decision: `NO_NEXT_CANDIDATE_QUALIFIED_PASS06`

This pass intentionally did not reopen Round17, the Round16 dormant lines, or the Pass03/Pass04 families.

## Family A: speculative-decoding verification / scheduling

Recent direct neighbors already make this a crowded problem-definition space:
- Speculative Verification (arXiv:2509.24328) dynamically controls verification length from predicted draft/target alignment.
- HiSpec (arXiv:2510.01336) explicitly identifies target verification as a bottleneck and inserts low-overhead intermediate verification with KV/hidden-state reuse.
- SPECTRE (arXiv:2605.08151) overlaps remote drafting and target verification in a serving system.
- Spexis (arXiv:2609.34370) adds speculative parallelism/lookahead scheduling to vLLM-scale multi-GPU serving.

There may still be implementation-specific kernels worth profiling, but no distinct memory-system residual with a clean novelty boundary and cheap first falsification was identified. No candidate is admitted.

## Family B: multi-LoRA adapter residency / transfer

This line has strong direct systems and architecture neighbors:
- Punica already provides heterogeneous-adapter GPU kernels.
- InfiniLoRA (arXiv:2604.07173) explicitly decouples LoRA execution from base-model serving, including GPU-initiated communication and specialized kernels.
- PLoRA (arXiv:2608.05483) directly targets the CPU-DRAM/PCIe adapter-staging problem with pooled memory, GPU-initiated read-compute, NDP execution, and GPU caching; it reports 1000-adapter H100 evaluations.

Because PLoRA already makes the adapter data-movement/capacity problem an explicit architecture target, a generic “LoRA adapter traffic/cache” AWMA line would not have a defensible novelty boundary. No candidate is admitted.

## Family C: disaggregated memory-processing pipeline

“Understand and Accelerate Memory Processing Pipeline for Disaggregated LLM Inference” (arXiv:2603.29002) reports 22--97% overhead across Prepare/Compute-Relevancy/Retrieval/Apply stages and demonstrates a GPU+FPGA heterogeneous solution.

This is scientifically important, but its claimed residual is broad, spans multiple long-context/RAG techniques, and its demonstrated causal solution relies on a heterogeneous GPU-FPGA platform. It does not presently yield one narrow, real-input, 109/174-cheap falsification that survives the already-screened sparse-KV/RAG/graph-retrieval neighbors. No candidate is admitted.

## Admission result

No newly screened family satisfies all four gates:
1. real public scientific workload/input authority;
2. a specific residual not directly targeted by strong existing software/system/architecture work;
3. a cheap and semantically valid first falsification on available 109/174 paths;
4. a clear nearest-neighbor boundary before mechanism design.

Therefore:
`NO_NEXT_CANDIDATE_QUALIFIED_PASS06`

This is a legitimate stop point. Do not create a speculative R19 card merely to fill unattended time.

R102 remains a watch line only:
`R102_DORMANT_WAITING_FOR_REAL_UPDATE_AUTHORITY`
until an authoritative adjacent working-precision tensor pair or reconstructible real patch chain becomes public/available.
