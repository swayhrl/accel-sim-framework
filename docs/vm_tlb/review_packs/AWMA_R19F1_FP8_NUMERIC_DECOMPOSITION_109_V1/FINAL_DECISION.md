# Final decision — R19F1

`R19F1_FP8_READINESS_RESIDUAL_PRESENT`

The separate representation-matched F0-versus-R0 numerical gate passed with the frozen TE E4M3 tolerance. The original R19 V1 B0-versus-FP8 allclose failure remains a failure. Exact input FP8 bits/scale and cached weight representation were closed; a single NSYS/CUPTI capture proved the *same native SM89 E4M3 GEMM* in online and ready arms. The public D0 path skips only input readiness work and yields bitwise-identical outputs.

Formal complete synchronized operator wall medians: A1 `0.085846 ms` (MAD `0.003176`) and D0 `0.062693 ms` (MAD `0.001412`), a `0.023153 ms` / `26.97%` reduction. CUDA-event medians were `0.081024 ms` and `0.059456 ms`, respectively (`26.62%`). All three paired-group median gaps were positive (`0.024846`, `0.019387`, `0.020258 ms`), and the combined wall gap exceeded 3× the larger arm MAD. Thus the preregistered >=5% complete-region investment screen passed. All 30 formal samples, warmup schedule and group ordering are retained in `TIMING.tsv` and node164 raw.

This is a causal **operator-boundary representation-readiness** diagnostic under frozen BF16 input and TE FP8 consumer math, not a BF16-to-FP8 speedup and not a whole-model/online request gain. The NSYS capture locates four A1-only scale/quantize kernels (~5 µs summed GPU service per range) plus launch-chain gaps; the latter are profiler-sensitive and not exactly quantified by NSYS. The same GEMM itself remained ~16 µs in both arms. The formal difference cannot be attributed to a changed GEMM function, shape, output, first-microbatch weight conversion or JIT. NCU was not needed because identity and localization were already established; zero NCU targets were run.

The result is **review-only**. D0 assumes an already-ready representation and is not by itself a feasible deployment policy. No hardware mechanism, 174, Accel-Sim, NVBit, custom FP8 kernel, new model/shape/recipe, or Blackwell FP4/TMEM inference is authorized or claimed here.
