# Track A report

Stage: `M2_FUNCTIONAL_TRANSLATION / G2-1`
Status: `PASS`; `G2-2` is `RUNNING`

Core M1 commit: `82fa2bc79cf09dd137073431dc41e48bc2f30cec` (pushed to
`research/hrl/vm-m1-m3-v0`). Framework source anchor before this report:
`aa901732753c5ca0c66694932456720081e468cd`.

M1 preserves `SimVA` and `SimPA` on coalesced transactions and implements only
disabled and ideal identity modes. All required transparency comparisons passed.
Review entry: `docs/vm_tlb/review_packs/M1_VM_CORE_FOUNDATION/README.md`.

G2-1 Core commit: `06f0ae7a24f1deacd86ddf95237e0ffa5e1a1b83`.
It adds a deterministic resident mapper, per-SM finite L1 TLBs, one GPU-shared
finite L2 TLB, deterministic replacement, finite lookup ports, and a
translation-before-data-path gate. Review evidence:
`docs/vm_tlb/review_packs/M2_FUNCTIONAL_TRANSLATION/G2_1_MAPPER_TLB.md`.

Next active gate: G2-2 translation MSHR, same-key merge, and finite
backpressure.
