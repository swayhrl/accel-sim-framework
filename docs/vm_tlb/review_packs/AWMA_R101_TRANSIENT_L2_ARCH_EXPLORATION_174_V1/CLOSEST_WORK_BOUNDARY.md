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
lifetime* applied to capacity-preserving L2 victim order plus lazy dead-dirty
drop. This is a design-combination boundary for comparison, not a novelty
conclusion. Formal M1 shows a large traffic response but only 0.5027% cycle
improvement, so it does not survive the preregistered 5% performance gate and
is not advanced to C0, holdout validation or novelty positioning.

O1 is a zero-simulated-cost whole-L2 scan at software-declared region death.
It is only a causal/semantic diagnostic and cannot support claims of an
implementable mechanism, attainable hardware speedup, or reproduction of the
Native D1 percentage. M1 versus B0 measures the combined retention-plus-lazy-
drop policy; it cannot isolate those two effects without another matched
ablation, which is outside this fixed first pass.
