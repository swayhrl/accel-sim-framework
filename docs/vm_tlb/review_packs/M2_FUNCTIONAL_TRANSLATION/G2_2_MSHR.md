# G2-2 — translation MSHR merge and backpressure

Status: `PASS`  
Core: `740d96f8be80977c150ffc911063969cafd25b8f`  
Framework source: `ed43cc81e3f5cea179281307b1ebb7f3e718e94b`

Translation MSHRs are finite and keyed by `(ASID, VPN, page-size-class)`.
Every entry holds unique `(SM, mem_access UID)` waiters. A same-key request
from another transaction merges; replay of the same UID is pending without a
second registration. A full MSHR returns `MSHR_FULL` without losing the
request. Completion fills every waiter's L1, fills L2, and releases the entry.

Directed command:

`g++ -std=c++11 -Wall -Wextra -Isrc tests/vm_m2_g2_2_test.cc src/gpgpu-sim/vm_translation.cc -o /tmp/vm_m2_g2_2_test && /tmp/vm_m2_g2_2_test`

Result: `vm_m2_g2_2_test PASS`.

- two waiters for one VPN: allocations=1, merges=1, registrations=2;
- repeated replay of the first waiter: no additional registration or merge;
- completion: wakeups=2, releases=1, quiescent conservation holds;
- one-entry pressure: second distinct key returns `MSHR_FULL`, then succeeds
  after the first completion;
- active and quiescent invariant checks verify unique active keys, unique
  waiters, allocation/release conservation, and registration/wakeup
  conservation.

The G2-1 regression test and the standard Core+Framework build both passed.
