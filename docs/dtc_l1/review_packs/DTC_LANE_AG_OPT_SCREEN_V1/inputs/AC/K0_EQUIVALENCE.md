# OPT-COLLECT OFF equivalence scope

Here OFF/K0 means `collect_wb_pipeline` omitted/0. The independent source-
invalidation switch is tested at0 and1; this does not rename Lane X's K0/K1.

Base is e32afdcf44be3374ff36d22568ed01a075459b6f, freshly built in a new AC-owned
detached worktree/build, without reusing old X2 products. New Core is
83aca449135703c176cfab29ae43e1245d00a557, also freshly independently built.
Each probe uses its own matching headers/library ABI; the baseline compilation
of the same authored fixture uses an explicit test-only macro because e32 has
no new option/member. Source and actual loading identities are bound in
BINARY_IDENTITY.json and CPU_TEST_RECEIPTS.json.

SOURCE_DELTA.json mechanically recovers the entire baseline shader.cc/header,
parameter registration and CMake after removing the explicitly authorized ON
pieces. In particular the original OO WB body is byte-identical after constant-
false gating; the OO selector, service_entry/collection/retirement, full LDST
cycle(), lower issue/return, ordinary invalidation, ledger completion, IO path and
RFU functions are unchanged. All other tracked files are byte-identical. No old
assertion, quota, sector or comparison is weakened. Additional OFF C++ state is
inert host metadata and no pipeline summary prints; this is not a claim that
software object layouts or binary hashes are unchanged.

For17 production-LDST CPU cases, every corresponding edge in {fresh X2,
new omitted, new explicit0} has the same typed state: all640 physical records,
readiness/TagValid/generation/Refs/waiters;128 Tags;128 slot generations; pending
returns and map-loss ledger; frontend owners and partial admission; all five
service-quota widths/use/cycles; service samples/occupancy/latency counters;
completion ledger and pending writes; original K1 observer counters. AC_EDGE and
AC_ENTRY also compare PIB, response FIFO/inflight, collected sectors, retirements,
closed dependencies and every entry's original timestamps/remaining sectors.

All51 corresponding actual normal gpu_print_stat() boundaries match old public
output byte-for-byte except `gpu_total_sim_rate`, which divides by host wall
time. No DTC/service/L1/L2/DRAM numerical field is removed. The same explicit CPU
input sets unused `dram_t::n_ref=0` in both arms because the unchanged source
constructor leaves it uninitialized; no DRAM cycle is executed. This qualification
is conditional on that controlled initialization, not an assertion that original
full runs had well-defined zero refresh counters. Failed pre-initialization
comparisons are retained. Omitted equals0; ON single/empty isolated cases also
have identical typed state/timing in this fixture.

The original7 CTests additionally regress pre-existing common, generation,
completion, finite service, source invalidation, real ordinary pending commit,
and old source-option OFF behavior. These do not supply full application/native/
GPU/trace numerical equivalence. No Gaussian/GEMM/full/canary/native application
is run. Other-mode OFF checks cover initialization only, not full ISA execution.
No old performance row or undefined/uninitialized state is relabeled as an
exact equivalence witness. Future authorized runs must qualify identities anew;
ON timing is a new experiment and cannot reuse old performance results.
