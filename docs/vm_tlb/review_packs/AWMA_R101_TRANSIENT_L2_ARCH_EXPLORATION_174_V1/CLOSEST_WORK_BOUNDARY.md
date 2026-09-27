# Closest-work boundary

Round13 authority is
`a63574628b2daf20dd3c9256f53d5cd3ff7df26f`.

This first pass does not claim novelty. A later survivor must be distinguished
from:

- PTX `discard.global.L2` destructive 128-byte discard;
- CUDA L2 access-policy/persisting-region hints;
- Locality Descriptor (ISCA 2018) cross-layer software locality semantics;
- inter-kernel reuse-aware scheduling;
- persistent scratchpad/kernel-to-kernel exchange;
- classic dead-block/reuse prediction;
- HiMuon/Flash-Muon/fused-muon software and fusion;
- Gram Newton-Schulz algebraic transformation.

M1's narrow diagnostic difference is exact software-known *region generation
lifetime* applied to capacity-preserving L2 victim order plus dead dirty drop.
It still requires evidence that coarse region lifetime causes a stable traffic
and cycle response. A first-pass win would remain exploratory.
