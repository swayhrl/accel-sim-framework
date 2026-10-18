# Equivalence scope

All production sources (src/, libcuda/, libopencl/, configs/) are byte-identical
to fixed parent AC83aca449. Only a new test and test-only CMake wiring differ.
Thus the old pipeline option's default, omitted/0 behavior and ON160KiB behavior
are not rewritten. No compact parser registration exists; unimplemented compact1
is explicitly rejected. There is no claim for compact0/1 production equivalence.

Fresh independent CPU builds use matching headers and own libcudart paths. The
immutable parent's runner is rerun with fresh X2 and AC2 products:17 omitted/0/X2
typed-state triples and51 normal public boundaries. Separate parent AC ON versus
AC2 ON comparisons cover the same17 production-LDST cases, including all original
finite counters and normal export. New boundary/capacity cases compare AC2 OFF
against fresh X2 and parent OFF, and AC2 ON against parent ON. Concrete final
receipts and counts are in CPU_TEST_MATRIX.md / QUALIFICATION.json.

State includes every physical identity/generation/Ref/waiter, Tag, slot, lower
credit/return, PIB owner, service quota/timestamp, completion ledger and original
K1 counters dumped by the unchanged parent fixture. Public comparison removes
only gpu_total_sim_rate (host wall-time rate). The fixture explicitly initializes
unused/no-DRAM-cycle dram_t::n_ref=0 in all arms, as parent AC does; production
DRAM remains untouched. This is controlled CPU equivalence, not full application,
loaded-value, real-trace, ISA or coherence equivalence. X2/AC old binaries/raw are
not reused. Old locked datasets and other Lane worktrees remain untouched.
