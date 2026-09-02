# Track A report

Stage: `G3-2A address provenance diagnostic`
Status: `PASS — CASE A; STOP FOR CHATGPT ARCHITECTURE REVIEW`

Framework was fetched to the required handoff
`971b1f46b74ed5eaaf4447d416a47f0e3e22d733`.  Core remains anchored at
accepted `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`; G3-2 source is local and
uncommitted because the gate did not pass.

G3-2A D0–D5 are complete.  The first request that trips the 49-bit generic
backend is a real global BFS store: kernel 7, PC `0x250`, raw active-lane trace
address `0x00fffdc0000000cd`, normally coalesced to
`SimVA=0xfffdc0000000c0` (56 bits; 64KB VPN `0xfffdc00000`).  It is neither a
local/param-local linearization nor a recursive `PTE_ACC_R`.  The same
coalesced value occurs in VM_DISABLED and VM_IDEAL_IDENTITY controls, each of
which completes the trace (exit 0); ideal mode retains its SimVA=SimPA
assertion.  This is **Case A: legitimate raw/global simulator trace SimVA
exceeds 49 bits**, not a general hardware-VA validity claim.

No virtual-address-width, masking/truncation/canonicalization, PTE namespace,
page-size, ASID, hierarchy, or translation-scope semantic change was made.
No stash was restored/popped/dropped, no Core G3-2 implementation was
committed, and G3-3 was not started.  The evidence pack is
`docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/G3_2_ADDRESS_PROVENANCE_DIAG.md`.
The Goal remains paused pending ChatGPT's architecture decision.

The local path correctly generated distinct physical `PTE_ACC_R` traffic,
bypassed shader L1D, consumed actual request/response interconnect plus L2 and
DRAM resources, and associated returns by `mem_fetch` UID and PTE request ID.
A one-kernel cold replay completed with four PTE DRAM responses and zero
misassociations.  A small-TLB BFS replay exercised both cold DRAM and L2-only
PTE returns (e.g. 12 DRAM and 1556 L2-only responses in one completed kernel).

The BFS replay then reached a trace VPN outside the G3-1 generic 49-bit
backend contract and asserted in `radix_page_table_backend::pte_address`.
This is an immediate correctness stop: widening/truncating the address space
or changing the PTE namespace would alter frozen semantics.  No workaround,
stash restore, Core commit, or G3-3 work was performed.  Full evidence and the
required decision are in
`docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/G3_2_BLOCKED.md`.

## Historical G3-1-RF report

G3-1-RF repairs the provisional generic PTE physical-address encoding at Core
`a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`; Framework handoff is
`0ca67e7ca0c22f6352b63ff8a24471717be3dc3f`.  The old formula shifted each
namespace by that key's VPN width and let a high 64KB VPN alias a 2MB VPN.
The repaired slot uses the fixed maximum 33-bit 64KB VPN width, consistent
with the reserved range's existing sizing.

The G3-1 directed test now proves the explicit former collision is distinct,
and checks min/max VPN boundaries for every 64KB/2MB × four-level namespace.
It retains the physical/non-recursive request, reserved-range, level/class,
and replacement-backend assertions.  M1/G2/M2-RF regressions, a cold build,
and a bounded M2 functional replay pass; the replay exits at 9522 cycles with
one walk/registration/wakeup and zero active MSHR/PWQ/walkers.

Review entry: `docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/README.md`.
G3-2 is not running and remains unauthorized.  The paused G3-2 work remains
untouched in Core `stash@{0}`.

## Historical M2-RF report

M2 was independently reopened because a registered pending waiter re-probed
and consumed L1/L2 lookup resources before the active MSHR recognized it.
The repair is Core `3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`, on top of the
preserved provisional G3-1 `8c613a356e6a146951cd59c9929046c6c4cfd856`.
Framework handoff is `e6b8d6b6034acd34f5f5176c3b0f4c3a865c09dc`.

The controller now returns `TRANSLATION_PENDING` before any TLB port/probe for
an already registered `(translation key, waiter UID)`.  A new UID still
performs its normal first lookup and then merges.  The exact directed test
proves one A L1/L2 miss, nine A no-probe/no-port retries, B's use of the sole
shared L2 port while A waits, and exact-once registration/wakeup/completion.

The cold build, M1 transparency, G2-1..G2-4, new retry and persistence tests,
one-kernel/LUD/BFS replays, and G3-1 backend/no-recursion test pass.  BFS
latency 5/50 retains seven walks and changes L2 misses only 16→19 while bypass
events rise 57→901; this removes the earlier polling-driven 42→357 miss
explosion.  All functional replays exit normally with MSHR/PWQ/walkers empty.

Review entry: `docs/vm_tlb/review_packs/M2_FUNCTIONAL_TRANSLATION/README.md`.
M2-RF is independently accepted; its historical stop boundary was superseded
only for the authorized G3-1-RF fix above.

## Historical pre-RF closeout

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

M3 entry gate G3-0 remains historical PASS at Core `e7999554` and Framework
`a7020e60`.  Provisional G3-1 `8c613a35` is superseded by the repaired
G3-1-RF Core `a192e5dc`, pending independent review.  Current work is not
G3-2: it is paused pending ChatGPT review of the namespace fix.  No
Segmentation, sub-entry, synthetic-KV, page-fault, migration, MCM, or real PTE
L2/DRAM integration is authorized.
