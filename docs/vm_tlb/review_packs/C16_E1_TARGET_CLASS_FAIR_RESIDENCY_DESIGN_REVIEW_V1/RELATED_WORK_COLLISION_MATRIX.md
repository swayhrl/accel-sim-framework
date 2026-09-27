# Related-work collision matrix

This is a bounded collision check, not an exhaustive prior-art or novelty review.

| Source | Known element | Collision | Not provided |
|---|---|---|---|
| CUDA_L2_ACCESS_POLICY_WINDOW | shared persisting set-aside, unused-capacity borrowing, per-access fractional persisting/streaming property | M1F fractional admission is not novel as a broad concept | semantic target-class occupancy quota, survival floor, or class-aware victim selection |
| PTX_CREATEPOLICY_FRACTIONAL | fractional evict_last/secondary eviction priority probability | fractional priority assignment is ISA-supported prior art | global occupancy accounting or fairness across 28 sequential semantic objects |
| AUTOSCRATCH_MLSYS_2023 | learned selection and pinning of address slices under L2 residency capacity | object/slice selection for inference residency is established | online equal-opportunity turnover control among all qweight classes with no training/search |
| PCAL_HPCA_2015 | priority-marked cache blocks, non-polluting threads, and optional opportunistic allocation | priority protection and borrowing/nonpollution are established | semantic-object fractional fairness in a global protected pool |
| ORCHESTRATED_GPU_CACHE_TVLSI_2014 | multi-level request/line priority and bypass when no lower/equal-priority victim exists | priority-aware replacement and fail-safe bypass are established | equal-share target classes or CUDA-hitRatio-aligned admission |
| LOCALITY_DRIVEN_GPU_BYPASS_ICS_2015 | reuse/locality-based insertion filtering and bypass | admission filtering is established | fairness between equally designated target classes at L2 |

## Primary sources

- [CUDA C++ Programming Guide: L2 Policy for Persisting Accesses](https://docs.nvidia.com/cuda/archive/12.5.1/cuda-c-programming-guide/index.html#l2-policy-for-persisting-accesses)
- [Parallel Thread Execution ISA: createpolicy](https://docs.nvidia.com/cuda/archive/13.0.0/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-createpolicy)
- [AutoScratch: ML-Optimized Cache Management for Inference-Oriented GPUs](https://proceedings.mlsys.org/paper_files/paper/2023/file/9d32b9324a89001520ae456b9e5ec73b-Paper-mlsys2023.pdf)
- [Priority-Based Cache Allocation in Throughput Processors](https://research.nvidia.com/sites/default/files/pubs/2015-02_Priority-based-cache-allocation/li_and_rhu.hpca2015.pdf)
- [Orchestrating Cache Management and Memory Scheduling for GPGPU Applications](https://icas.tsinghua-sz.edu.cn/WebPublications/PaperDetail/768?unit=1002)
- [Locality-Driven Dynamic GPU Cache Bypassing](https://research.nvidia.com/publication/2015-06_locality-driven-dynamic-gpu-cache-bypassing)

No novelty claim is made. The checked sources establish the component ideas; they do not establish the exact 28-class problem-specific combination reviewed here.
