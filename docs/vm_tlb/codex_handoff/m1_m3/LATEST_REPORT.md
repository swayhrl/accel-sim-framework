# Track A report

Stage: `M2_FUNCTIONAL_TRANSLATION / G2-2`
Status: `PASS`; `G2-3` is `RUNNING`

Core M1 commit: `82fa2bc79cf09dd137073431dc41e48bc2f30cec` (pushed to
`research/hrl/vm-m1-m3-v0`). Framework source anchor before this report:
`aa901732753c5ca0c66694932456720081e468cd`.

M1 preserves `SimVA` and `SimPA` on coalesced transactions and implements only
disabled and ideal identity modes. All required transparency comparisons passed.
Review entry: `docs/vm_tlb/review_packs/M1_VM_CORE_FOUNDATION/README.md`.

G2-2 Core commit: `740d96f8be80977c150ffc911063969cafd25b8f`. It adds finite
translation MSHRs, same-key merging, UID-based exactly-once waiter
registration, explicit full backpressure, and machine-checkable conservation.
Review evidence:
`docs/vm_tlb/review_packs/M2_FUNCTIONAL_TRANSLATION/G2_2_MSHR.md`.

Next active gate: G2-3 fixed-latency PWQ and walkers.
