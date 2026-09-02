# Track A report

Stage: `M2_FUNCTIONAL_TRANSLATION / G2-CLOSEOUT`
Status: `PASS`

Core M1 commit: `82fa2bc79cf09dd137073431dc41e48bc2f30cec` (pushed to
`research/hrl/vm-m1-m3-v0`). Framework source anchor before this report:
`aa901732753c5ca0c66694932456720081e468cd`.

M1 preserves `SimVA` and `SimPA` on coalesced transactions and implements only
disabled and ideal identity modes. All required transparency comparisons passed.
Review entry: `docs/vm_tlb/review_packs/M1_VM_CORE_FOUNDATION/README.md`.

M2-D and G2-4 are now `PASS`.  Core fix:
`e7999554200760b31b4efe16d98e050370e1ea71`; Framework dependency fix:
`4012be3606c300d11e7b34826ee1cb22b0852b93`.  The pre-replay allocation was a
stale Framework/Core C++-layout build artifact, not a VM resource requirement.
After a cold rebuild, functional one-kernel replay completes within the 10 GiB
bound with final MSHR/PWQ/walker state empty and waiter registration/wakeup 1/1.

Review evidence: `docs/vm_tlb/review_packs/M2_RUNTIME_MEMORY_DIAG/README.md`.

M2 closeout is PASS.  The final pack is
`docs/vm_tlb/review_packs/M2_FUNCTIONAL_TRANSLATION/README.md`: it records all
directed expected-versus-actual tests, conservation checks, cold build,
disabled/ideal transparency, real functional replay, and integrated LUD/BFS
smokes with the required small resource sweeps.  The local trace set contained
LUD and BFS only; LUD was used as regular/memory-path smoke and BFS as the
available irregular smoke.  No unsupported third workload claim is made.

M3 entry gate G3-0 is PASS at Core `e7999554` and Framework `a7020e60`.
The G3-0 pack records the compact M2 regression freeze and an explicit
parameter/evidence ledger.  Current work is G3-1: a generic replaceable PTE
backend and physical/non-recursive request contract.  No Segmentation,
sub-entry, synthetic-KV, page-fault, migration, or MCM work is authorized.
