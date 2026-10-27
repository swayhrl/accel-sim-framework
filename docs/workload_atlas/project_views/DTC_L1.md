# DTC-L1 reading view

This is a source-to-question map for the35 frozen ordinary inputs, with seven conditional identities preserved. Start from [the index](../WORKLOAD_INDEX.tsv), [evidence matrix](../ARCH_FEATURE_MATRIX.tsv) and [scope gaps](../EVIDENCE_GAPS.md). The existing L2 exploration [commit5178408bc28819140d01520f339af76b71f61489](https://github.com/swayhrl/accel-sim-framework/tree/5178408bc28819140d01520f339af76b71f61489/docs/dtc_l1/review_packs/DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_V1) is a time-labelled experiment checkpoint. Its partial results are not a new source certification.

## Searchable tags and physical lines

[ATAX](../programs/polybench_gpu/ATAX.md), [MVT](../programs/polybench_gpu/MVT.md) and [BICG](../programs/polybench_gpu/BICG.md) combine lane-strided matrix loads with thread-local sequential traversal and uniform vectors. One strided instruction can address32 lines while subsequent loop positions revisit those lines. Searchable-address coverage and physical-line retention are separate questions. Only16 CTAs exist per phase at4096 elements. Phase order and data dependencies differ between the programs.

[GEMM](../programs/polybench_gpu/GEMM.md), [3MM](../programs/polybench_gpu/3MM.md) and [Parboil sgemm](../programs/parboil/sgemm.md) are distinct implementations. PolyBench has no software shared tile; Parboil stages B and owns16 register accumulators/thread. Uniform loads, cross-CTA reuse and arithmetic dependence can coexist. Hash/set conflicts require the actual address mapping.

## Pending requests and waiters

[2DCONV](../programs/polybench_gpu/2DCONV.md) and [3DCONV](../programs/polybench_gpu/3DCONV.md) supply shifted overlap; [particlefilter_naive](../programs/rodinia/particlefilter_naive.md) supplies uniform CDF scans followed by dependent coordinate gathers. Static overlap suggests possible pending-line sharing but does not establish simultaneous overlap. Existing-evidence queries must distinguish issued instructions, pending lines, merged waiters and hit responses.

For PIB analysis, distinguish independent operands, arithmetic/load chains, divergence and CTA barriers. [myocyte](../programs/rodinia/myocyte.md) has sparsely active threads; [lud](../programs/rodinia/lud.md) and [scan](../programs/cuda_samples/scan.md) have stage barriers. These source structures bound work release without measuring wait duration or wakeup bandwidth.

## Paths and return service

[sad](../programs/parboil/sad.md), [bfs](../programs/parboil/bfs.md) and conditional [kmeans](../programs/other/kmeans.md) distinguish texture/constant from ordinary global accesses. Histogram and BFS atomics need operation-specific interpretation. Source declarations do not prove the simulator path of a compiled instruction. L1 allocation, lower-return, PIB wakeup, collection and retirement require the relevant counter and exact simulator source/config identity.

## Scope before mechanism

[heartwall](../programs/rodinia/heartwall.md) one-frame input initializes templates rather than tracking. [CFD](../programs/other/cfd.md) and [streamcluster](../programs/other/streamcluster.md) remain conditional. [convolutionSeparable](../programs/cuda_samples/convolutionSeparable.md) and [scan](../programs/cuda_samples/scan.md) expose host/shape differences between source candidates and capture metadata.

No feature is defined by DTC speedup. More useful concurrency, fewer duplicate allocations and reduced traffic remain hypotheses until independently measured at the correct input/model identities. Existing numerical results and manuscript text are unchanged.


## V1R1 phase and evidence usage

For any kernel/phase comparison use [the V1R1 kernel/phase index](../KERNEL_PHASE_FEATURES_V1R1.tsv) and the [disambiguated evidence rows](../EVIDENCE_BINDINGS_V1R1.tsv). CFD remains conditional, one-frame heartwall is initialization, and historical PolyBench capture ELF lineage remains unbound. Details in [shared applicability notes](../PROJECT_SCOPE_ADVISORIES_V1R1.md). No changes to frozen DTC input registration or live L2 MLP goal are implied.
