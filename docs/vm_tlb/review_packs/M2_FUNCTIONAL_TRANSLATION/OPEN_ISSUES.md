# Open issues and frozen boundary

- `MODELING_DECISION`: M2 TLB hit latency is zero while L1/L2 lookup ports are
  finite.  It is functional behavior, not target-paper exact timing.
- Nonzero/configurable TLB lookup latency belongs to M3 timing decomposition;
  it must not be inferred from M2 counters.
- M2 is resident-memory only: no real PTE traffic, PWC, 2MB page behavior,
  page fault, migration, or UVM residency policy is implemented.
- `8c613a35` remains a preserved provisional G3-1 contract.  RF8 reruns its
  unit test, but independent ChatGPT review must accept repaired M2 before any
  G3-2 real PTE L2/DRAM work resumes.
- This RF repair does not claim hardware retry arbitration.  It is the frozen
  simulator semantic that an already accepted `(translation key, waiter UID)`
  is pending rather than a new TLB lookup.
