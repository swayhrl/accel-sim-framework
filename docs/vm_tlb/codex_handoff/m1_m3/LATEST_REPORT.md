# Track A report

Stage: `M2_FUNCTIONAL_TRANSLATION / G2-4`
Status: `BLOCKED`

Core M1 commit: `82fa2bc79cf09dd137073431dc41e48bc2f30cec` (pushed to
`research/hrl/vm-m1-m3-v0`). Framework source anchor before this report:
`aa901732753c5ca0c66694932456720081e468cd`.

M1 preserves `SimVA` and `SimPA` on coalesced transactions and implements only
disabled and ideal identity modes. All required transparency comparisons passed.
Review entry: `docs/vm_tlb/review_packs/M1_VM_CORE_FOUNDATION/README.md`.

G2-4 Core checkpoint: `c1431e01f593719f9201d4ad4d7666bebead8a4f`. All
directed M2 tests and the standard build pass, but the required real VM-mode
trace replay has no completed evidence. QV100 and RTX3070 runs reached
abnormal memory growth; a 54 KiB one-kernel trace reproduced it; a 10 GiB
address-space limit produces deterministic `std::bad_alloc` immediately after
memory-subpartition initialization.

Review evidence: `docs/vm_tlb/review_packs/M2_FUNCTIONAL_TRANSLATION/G2_4_RUNNING.md`.

Required before resuming: an isolated host with enough memory or an approved
fix for the pre-trace allocation. M2 and M3 are not accepted; no M3 work began.
