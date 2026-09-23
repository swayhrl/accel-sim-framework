# Shared-residency independent consumer closure

Producer `1e701f013fc174b5b4df9febb5c33500f9ea586e` closes independently from raw evidence at `SHARED_RESIDENCY_LOCAL_ONLY`.

- rotating policy qualification: PASS;
- multi-target local retention: PASS;
- stable whole-decode 2% materiality: FAIL, as preregistered;
- 14-profile semantic NCU and 10-profile critical-path evidence: PASS;
- up_proj duration response is concentrated in the quantized GEMM while reduction is nearly unchanged;
- aggregate DRAM is not treated as a standalone critical-path proxy.

The run-aligned SHARE3 audit gives median three-target share 1.7400% of stable decode, median summed local saving 0.4582% of decode, and unclamped median realization ratio 0.8852. The sub-0.5% whole-decode result is consistent with limited protected coverage; it is not evidence that local savings fail to realize systemically.

Prior producer/strict-consumer divergence and the traffic caveat remain frozen. No simulator implementation is authorized.
