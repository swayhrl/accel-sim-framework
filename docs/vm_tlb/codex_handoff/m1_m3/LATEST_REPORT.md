# Track A report

Stage: `M2_FUNCTIONAL_TRANSLATION / G2-CLOSEOUT`
Status: `RUNNING`

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

M2 closeout is now running.  M3 has not started and remains prohibited until
the required integrated M2 smoke/sensitivity evidence passes.
