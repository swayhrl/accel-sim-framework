# Simulator to RTL state mapping

The field-level mapping is frozen in
`util/vm_tlb/awma/prel1_hw_proxy/STATE_MAPPING.tsv`.

Hardware-required state is the exact translation key, leader completion tag,
FREE/LIVE/READY lifecycle, result PPN, bounded waiter allocation and follower
continuation metadata. Registration cycles, wait histograms, service source,
critical-path markers and C++ containers are simulation/debug state only.
The RTL proxy additionally uses one 6-bit drain cursor per entry. Its optional
registered timing variant adds a 197-bit (minimal) or 490-bit (conservative)
transient request pipeline per SID; neither is hidden in the state budget.

The simulator uses a 32-bit `unsigned` ASID field and 64-bit generation field,
but defines no target hardware widths for either. They are reported as
`SIMULATOR_LOGICAL_WIDTH`; a paper implementation must choose and justify real
ASID/generation widths. Request-token width likewise requires an implementation
contract. The proxy uses source UID width 32 as its minimum.

The frozen platform has 76 simulated SIDs. Real RTX4080 SID/SM mapping is not
asserted. GPU-wide state is `N_SID * per_SID_state`.

Frozen capacity remains 2 entries/SID and 32 waiters/entry. Across development,
Pair C and REDUCE, observed entry HWM is 2 and waiter HWM is
15; this does not prove 32 is minimal.
