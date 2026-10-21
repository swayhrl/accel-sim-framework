# Coverage delta: reuse A2 low-level prefill checks; retain one small E input check

Reviewed Core `2aa0ee802e2cdd79d79e352e74522f8b6ae96699`, against the prior `697e2ade` source review. The21 reader/opcode/oracle source objects remain identical. Runtime Framework is still exact `9dd1ee57`.

A2's appended `test_large_capacity.cc:132–146` now drives the actual production `l2_cache::ft_try_force_tag_access` with17 clean same-set addresses and asserts one clean host-prefill replacement. That coverage can be consumed from the final A2 fixture after E independently replays its exact released ELF. No second E17-line conflict fixture is needed. A2 also already supplies the enlarged line/descriptor/per-address and real dirty-WB/copy-latch groups; those should not be duplicated in a new E host-input fixture.

The appended block does not cover the remaining three input obligations:

| Remaining input check | Why the A2 block does not cover it |
| --- | --- |
| Real top-level GPU host-memcpy dispatch,64-bit pointer/byte-range and post-prefill version-zero reads | It calls `f.cache` directly, not `gpu.perf_memcpy_to_gpu` or the partition's guarded input entry. The helper's `part` is a separately constructed partition. The block has no asserted above32bit/unaligned/repeat-epoch path and no read requester after warming. |
| Dirty host owner refusal without version/generation/offset mutation | All17 prefill operations are expected to succeed on clean addresses. The earlier dirty-WB stimulus tests a different production entry and precondition. |
| Actual frontend/lower-pending/queued-response host refusal, then real drain and accepted retry | Prefill starts after prior hardware-drain checks; no host entry is attempted while these resources are live. |

The existing independent `test_capacity_host_prefill.cc` draft covers exactly these three groups in one bounded master-ON test ELF and one invocation. It has no17-line clean-conflict,600-entry expansion or extra dirty-WB group, so no source change is needed to remove duplicated coverage. Its single physical slice retains the actual scale64 native geometry and capacities. Retain that one independently linked test after formal archive delivery unless the final A2 source itself adds all the missing actual entries and assertions. Do not run the old full native suite to close this small delta.

The published r4 receipt at Framework `08529aea3476ff0e2005fc0502ff43de859913c1` has SHA256 `ba3990a0228b479a3527840d2094f2815c140f7679ba2435e08805eda8a44ffc`. It records12 producer native completions on Core `57347614`, with `runtime_ready=false` and `independent_qualification=false`. The new host block was added afterward in `dea44e44`/`2aa0ee80`. These historical producer results cannot qualify that new code, the pending r5 producer, or any E application. The receipt's local bytes were checked against the exact committed blob; no old raw log or overwritten build artifact was substituted for final producer identity.

The machine-readable delta, pinned source objects, coverage matrix and per-input lineage updates are in `NEW_INPUT_SOURCE_COVERAGE_DELTA_r2.json` and five `*_NEW_INPUT_DELTA_r2.json` files. All native PASS/source-binding fields remain pending. This review compiled and executed nothing and changed no registry, CLIENT, production source, input asset or Git state.
