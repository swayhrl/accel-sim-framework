# Lane 3 r16 — independent A2/A3 Bank progress repair

Authority92de53a63616f9fcc53f2058ad975c3c8f90b13c; read r16 and prior r15 SOURCE_AUDIT/RUN_LOCAL_REPRO/repro_bank_retry in full. Same Lane3 branch/worktree, one bounded CONTINUE. Core30c2920a3754bdaae09511f93d91873959c09f15; runner Frameworkea2a38c46 (full identity in SOURCE_IDENTITY). The r14 native-ownership repair and five frozen whole-commandlist oracle inputs are preserved.

Actual execution: four sequential tiny C++11/UBSan builds,18 executions. At both C8 and C16:

| Actual source components | A2 | A3 |
|---|---|---|
| Old3f3a8149 | exit21, no progress,2 Bank tokens parked | exit22, no progress,3 tokens parked |
| A2 only, store-port47fa210c | PASS | exit22 persists |
| A3 only, runtime/scheduler85e625e7 | exit21 persists | PASS |
| Both fixes, final30c2920a | PASS | PASS |

Two additional final control executions pass: denied versus granted selection;1op/bank/physical-cycle; oldest pending RO ahead of later same-bank WB, then WB ahead of the next RO response; ICNT hold and a granted-but-not-enqueued response that pays a new read on retry; late native response arrival; partial fill; exact-once descriptor release; zero pending-token drain; pin retirement; physical slot reuse/stale Payload and Tag generations; incorrect physical-cycle refusal. EXECUTED_MATRIX/CSV and immutable per-build source bindings/logs/binary hashes are the authority. Eight nonzero exits are deliberately retained old/one-fix failure results, not simulator PASS.

This is SOURCE_BOUND_CPP, not full cache/partition/DRAM execution. Actual production store, transactions, store-port and12 MSHR methods are used. Runtime has_response/prepare/commit and response scheduler bodies are copied exactly (scheduler class qualifiers renamed). Clock, Tag callbacks, native-ready input and requester packet copy sink are explicit test facades. Composite one-fix variants are NOT whole-Core production binaries. The standalone WB reservation is a Bank competitor, not a replayed GPU writer or an oracle-validation workload. No frozen real oracle/trace body is read or changed.

Four actual registry leases used one CPU/two GiB each, sequentially; all released. Compile wall times2.72/2.73/2.84/2.73s, peak RSS<=290816KiB. Original50GiB workspace,64GiB RAM and central8CPU/32GiB gates remain. The runner adds a protected4CPU/8GiB Lane1 producer envelope, resolved output-FS checks and bounded child CPU/address-space/output/time. A first over-strict courtesy check yielded to a Lane1 lease before claiming anything; its denial is retained. No full producer, application, scan, GateWaiter, cleanup or other-project process operation started.

A2 delays attached RO->RESIDENT until transaction retirement; A3 keeps the existing reply.transaction while waiting and reserves selected for a real granted response. No public arbiter ABI, allocator, Bank budget, extra metadata field or response data buffer changed. Lane1 should inspect PUBLIC_DELTA_REVIEW_FOR_LANE1.json and the exact-parent RO-only patches; this pack does not merge public R2.

Complete19 production invocations remain NOT_RUN; independent RO scientific qualification=false. Official repaired R0 producer088146/e424 is context, contains no qualified RO and is not a substitute. The remaining official R2 rebase/cache/partition/19-case/Lane5 gates are in PRODUCTION_REPRO_STAGING.md and NEXT_PRODUCTION_INPUTS.json. No performance, pair, geomean or scope upgrade is claimed.
