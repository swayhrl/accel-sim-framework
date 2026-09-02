# G3-2 — real PTE L2/DRAM integration (blocked)

Status: `BLOCKED — correctness STOP`

Core source anchor: `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9` plus local,
**uncommitted** G3-2 implementation under review.  Framework handoff:
`198b32b278d30f04d113028cf4c328d457a134b9`.

## What was established before the stop

The local implementation introduces a distinct `PTE_ACC_R` request class.  A
physical, translation-bypassing PTE request is injected at a real cluster
terminal, bypasses shader L1D, traverses the request interconnect, L2 and lower
memory queues, and returns through the response interconnect to the walker.
It is not allowed to enter the shader response FIFO.  The response map keys on
the actual `mem_fetch` UID and carries the original PTE request identity,
because the L2 MSHR path may align `mem_fetch::addr`.

The standalone controller test passed:

```
/tmp/g3-2-unit/vm_m3_g3_2_test
vm_m3_g3_2_test PASS
```

It proves two active walkers, out-of-order identity-correct responses, four
PTE levels per walk, no early completion, exact 8/8 issue/response accounting,
and quiescent M2 invariants.

A standard Framework/Core rebuild succeeded; command output is
`/tmp/g3-2-runtime/build-2.log`.

The one-kernel RTX3070 replay using
`/tmp/g3-2-vm-real.config` completed normally.  Its end statistics in
`/tmp/g3-2-runtime/one-kernel.log` show:

- `PTE_ACC_R` L2 total access/miss = `4/4`;
- `vm_pte_requests/responses = 4/4`;
- `vm_pte_dram_responses = 4` and `vm_pte_response_misassociations = 0`;
- empty translation MSHR/PWQ/walkers.

The small-TLB BFS replay also demonstrated real L2-resident PTE service before
the failure: e.g. an earlier completed kernel reports
`vm_pte_requests/responses = 1568/1568`,
`vm_pte_l2_only_responses = 1556`,
`vm_pte_dram_responses = 12`, and zero response misassociations.  This is in
`/tmp/g3-2-runtime/bfs-small-tlb.log`.

## Hard stop: unsupported trace VPN

That same BFS run reached a later kernel and stopped at:

```
accel-sim.out: vm_translation.cc:73: ... pte_address(...):
Assertion `key.vpn < (1ULL << key_vpn_bits)' failed.
```

The affected request has a VPN outside the current generic backend's frozen
49-bit virtual-address contract.  This is not a queueing delay, an L2 miss, or
a harmless statistic.  It means G3-2 cannot currently claim complete PTE
coverage for the available functional trace set.

Changing the configured virtual-address width, aliasing/truncating the VPN, or
changing the PTE namespace/range would alter accepted G3-1 address semantics.
Those options require an explicit semantic decision/review.  No such change
was made.  G3-3 and later gates must not start.

## Provenance and preserved state

`stash@{0}` was inspected only and remains untouched.  It was neither applied
nor used as evidence.  The local Core G3-2 source and `vm_m3_g3_2_test.cc`
remain uncommitted for review and were not pushed.  This Framework document is
the safe evidence artifact for the STOP boundary.

## Required review decision

Decide the generic M3 virtual-address/backend contract for trace addresses
outside 49 bits, including the required PTE reserved-range non-overlap proof.
Only after that decision may G3-2 be resumed and all M2/G3 regressions be
rerun.
