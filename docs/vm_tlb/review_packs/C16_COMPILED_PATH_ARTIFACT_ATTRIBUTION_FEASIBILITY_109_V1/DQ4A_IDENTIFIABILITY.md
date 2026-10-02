# DQ4a compiled-path producer→consumer boundary

The FX graphs preserve a static dependency chain such as layer gate/up linear → SiLU/slice/multiply → down linear, and source-node comments preserve pieces of Inductor's generated call order. This proves a *static graph relationship*, not the observed runtime producer→consumer boundary for each layer and decode step.

The 9122 runtime inventory retains kernel names without launch instance order or callsite correlation. Generic external GEMM kernels are shared by several projection roles, generated symbols can repeat across all 36 layers and 32 forwards, and combo/fused kernels can remove intermediate launch boundaries. No hook-free artifact here uniquely identifies where a particular runtime producer ended and its consumer began.

Decision: `DQ4A_COMPILED_ATTRIBUTION_UNRESOLVED`. No duration is allocated by operation count or theoretical FLOPs.
