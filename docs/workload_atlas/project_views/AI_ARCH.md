# AI-ARCH reuse view

The atlas covers dense/stencil, reduction, scan/sort, irregular graph, adaptive ODE and search patterns. It is a reusable source taxonomy, not proof these benchmarks model an AI application or are admitted AI-ARCH inputs.

[PolyBench GEMM](../programs/polybench_gpu/GEMM.md), [3MM](../programs/polybench_gpu/3MM.md) and [Parboil sgemm](../programs/parboil/sgemm.md) demonstrate different thread mapping, tiling, register reuse and launch DAGs within one mathematical family. Arithmetic intensity and cache classification cannot transfer without actual source, shape and compiled instructions.

[convolutionSeparable](../programs/cuda_samples/convolutionSeparable.md), [2DCONV](../programs/polybench_gpu/2DCONV.md), [3DCONV](../programs/polybench_gpu/3DCONV.md) and [dwt2d](../programs/rodinia/dwt2d.md) have different staging, halo and multilevel structures. Shared reuse reduces potential global loads without measuring traffic. [scan](../programs/cuda_samples/scan.md), [histogram](../programs/cuda_samples/histogram.md), [mergeSort](../programs/cuda_samples/mergeSort.md) and [hybridsort](../programs/rodinia/hybridsort.md) expose launch/barrier/atomic dependencies.

[particlefilter_naive](../programs/rodinia/particlefilter_naive.md) performs most filtering work on CPU. [particlefilter_float](../programs/rodinia/particlefilter_float.md) moves additional phases to GPU yet retains double arrays. [myocyte](../programs/rodinia/myocyte.md) uses adaptive CPU control and sparsely active GPU threads. Host/device boundaries and selected versions matter.

[vectorAdd](../programs/cuda_samples/vectorAdd.md) and [BlackScholes](../programs/cuda_samples/BlackScholes.md) are simple controls and boundary cases, not replacements for complex workloads. Performance, occupancy, spills, scheduling and queue lifetime require independent runtime evidence.
