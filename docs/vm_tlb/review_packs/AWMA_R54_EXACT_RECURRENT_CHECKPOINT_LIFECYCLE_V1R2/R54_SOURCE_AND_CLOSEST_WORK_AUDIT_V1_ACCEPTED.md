# R54 source and closest-work audit

Round07 identifies Marconi, Sparse Prefix Caching, Tail-Replay, TreeWY, persistent-state accelerators and DAMP as closest work. This stage reached no lifecycle-cost conclusion because the optimized GDN runtime gate failed. Source inspection of Qwen3.5 shows fast kernels are supplied through `causal_conv1d` and `fla` hub-kernel paths; both were absent at runtime, and the executed canary explicitly reported reference fallback. Slow fallback timing is not used as R54 evidence.
