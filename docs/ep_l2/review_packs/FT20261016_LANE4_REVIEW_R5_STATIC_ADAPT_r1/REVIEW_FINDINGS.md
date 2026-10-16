# Static findings and qualification limits

## Exact source, not a runtime PASS

Lane1 candidate62dc and publicationc93d have identical tree
23f407cfadc7728b50f6f91177319ada4029cd2b. The frozen original Lane4 ideal
patch replays without conflict. CORE_R0_1_IDEAL_STATIC.patch includes that
implementation/tests plus the two fixes below. CORE_RUNTIME_ONLY.patch isolates
src changes. Existing producer FT cache include, both new repair tests and
R0_1_REPAIR_SCOPE.md remain byte-identical to62dc (hashes in SOURCE_AUDIT).
No Lane1 file/worktree/branch was edited.

1. **Duplicate accessor, ordinary engineering defect.** Exact62dc
   src/gpgpu-sim/l2cache.h defines ft_bank_grants_for_test(unsigned) twice in
   the same class. R0_1_DUPLICATE_ACCESSOR_ONLY.patch deletes one definition.
   This is source-confirmed; no compiler was invoked. It is a standalone
   producer fix and does not require ideal integration.
2. **Tag timestamp, uncompiled fix.** Ideal resident Tag touch needs
   cycle + m_memcpy_cycle_offset, matching native Tag age ordering. The actual
   ideal payload-bank grant and response timestamps still use physical cycle.
   CORE_IDEAL_TAG_TIMESTAMP_ONLY.patch is one changed call, based on the
   replayed ideal tree after accessor cleanup. No bank/port/timing budget is
   enlarged. Qualification still needs offset0/nonzero production observations.

## Host prefill and reference scope: still an explicit qualification item

62dc prefill checks hardware drain, dirty/pinned/pending/WAD state, one-sector
mask and actual Tag index/handle consistency before completing. It preserves
full-width addresses and touches both partial endpoints. Payload selected
sectors become version-zero symbols; other ready sectors remain intact.
These are source observations; its two new C++ tests remain NOT_RUN here.

The ideal replay still tracks reference bytes through ReferenceMemory::write
and read. It has no reference synchronization hook in
memory_sub_partition::ft_try_force_l2_tag_update. Exact62dc permits a later
clean/quiescent prefill (its scope/test plan says so); clean/quiescent does not
by itself prove no earlier GPU producer version exists in the ideal reference.
Thus static replay is insufficient to qualify I_READ_HIT across that sequence.
An ideal reference update consistent with the accepted host-write semantics,
or an independently approved initial-only scope with a real rejection gate,
must be established and tested by the R1.1 producer/Lane5. This pack neither
narrows the scientific scope nor resets oracle data silently. The issue does
not block R0.1 B16/U_WB16, which has no ideal reference store. No new runtime
qualification is claimed for WB/META either.

## Same-binary and non-binding audit

The runner keeps source/binary/trace/workload/epoch/features/termination equal
to the Lane5 B16 OFF spec. Only the three-bit hashed overlay is appended;
config hash and run key must change accordingly. V1 RO-off and explicit V2
RO-off remain exact identities. Common binary registrations, frozen release
hash, requested ideal gate evidence and current OFF + ideal authorizations
are mandatory. The canonical V2 module binds supersession evidence, generation
and canonical manifest hash; it verifies full identity, raw hash, cycles and
instructions for result intake. A later scientific revocation is recorded
separately after normal execution closure, retaining the execution terminal.
No production path is mocked; only pure unit-test authority loaders use
explicitly synthetic fixtures.

I_WB requires wb_data_full=0 and wbuf_full=0; I_META requires all three
line-MSHR/descriptor/per-address capacity refusals zero. I_READ_HIT must
actually serve reads and drain reference lifetimes. All modes retain 64-slice
requester/exact-once/hardware closure, WB copy/read/accept equality, physical
bank restrictions and the real response path. Zero refusal plus normal exit
is insufficient without these identities and closures. No I_BANK, new workload
or combination outside convolution/FWT was admitted.

Validation logs report 24 same-binary/authorization tests, 24 V2 acceptance
tests and 18 parser/config tests =66 PASS. They verify software checks with
synthetic fixtures; they are not production-driven repair/ideal evidence.
