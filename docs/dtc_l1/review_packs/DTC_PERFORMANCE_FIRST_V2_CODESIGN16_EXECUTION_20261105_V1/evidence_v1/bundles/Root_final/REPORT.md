# DTC-L1 Performance-First V2: Codesign16 execution closeout

## Outcome

The requested Physical x PIB performance comparison was not obtained. All 16 frozen one-use identities were consumed at INTENT. Every launcher returned 127 before the simulator was observed. There are **0 accepted performance results, 16 launcher engineering negatives, and 0 observed simulator starts**. Cycles, combination speedup, comparison to CH, and interaction J are missing; GM is N/A with n=0. These failures are neither cache regressions nor zero speedups.

The request is `DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1`: budget 16, consumed 16, remaining 0. No credit was refunded or extended. No consumed UUID was reused or retried. The performance objective remains unfulfilled. This package closes the failed execution evidence and prepares a separately approved recovery scope; it does not authorize that recovery.

## Authority and fixed scientific identity

Authority: `320b1365902a72502fa61ba114cb4a4a28b934bb`.

Approved contract and matrix are under `docs/dtc_l1/plans/DTC_PERFORMANCE_FIRST_V2_CPU_PREPARATION_20261104_V1/`. Approved matrix SHA256 is `1b2994cd2be327182d4db9f956e99400c3597be3bb2ee59fbb18d6c281cf4c20`; materialized matrix SHA256 is `112321797ece7c6832314463d1ea182c45bcff2a75ca7ee8677507fe876306b7`.

The eight inputs are 2DCONV, GEMM, convolutionSeparable, scan, ATAX, MVT, BICG and vectorAdd, each paired with Physical768+OO PIB192 and Physical1024+OO PIB192. Exact input SHA, four-file configuration SHA, original CH/DH-P0 provenance, UUID, INTENT and DONE are retained in the matrix, specifications and terminal ledger.

- Core: `9eedb3131937748f0492fa83aad37d3691118d70`.
- Framework: `02775fd795cde5aae1480d81cee6eb481d0a08f4`.
- Simulator SHA256: `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`.
- libcudart SHA256: `694f05ce97fe3e1552d94803c2202d8d037769c61624cde5f6a832622ed60c56`.

The 270 expected effective options and fixed Core, framework, binaries, input and configuration identities did not change. A declared whole-trace-body SHA is not certification of complete-application capture, numerical correctness or original application ELF identity.

## Root cause and repair

The coordinator initialized the new namespace without its `tools/bin` and `tools/lib` links. The native launcher invokes the private loader and `tools/bin/strace` before the model. Model binary and library checks did not cover this entire executable chain. All sixteen original 236-byte raw logs report the same missing new-namespace strace path. This initialization and qualification omission is the coordinator's engineering error.

The repair adds exactly the two missing links to the original verified read-only tool objects. The same loader/strace chain now executes `/usr/bin/true` successfully. The tracer's six and simulator's eight ELF dependencies resolve. Simulator inspection uses readelf and loader --list only; repair qualification never executes the simulator main. All 222 active source pins remain unchanged.

The repair packet is `engineering_incidents/launcher_runtime_missing_v1/MANIFEST.json`, SHA256 `28c2a8988f5ff9905b87fe5facdaf96e4ed6f63db492925dd9b5b03f99bbcc6e`. Independent launcher-layout review has 313 checks and concludes only `PASS_CPU_LAUNCHER_LAYOUT_ONLY`. It does not restore a consumed scientific identity or prove a scientific result.

## Earlier pre-INTENT incident and source history

Before any charged identity, a new helper tried to acquire a shared registry lock through another file descriptor while already holding its exclusive lock. Shadow tests missed this real locking edge. The coordinator preserved the incident, stopped only the new private request thread, and terminated two verified no-child, no-INTENT, no-model frontends. The legal owner and healthy V1 models were not signaled. Registry readers and postprocessing were delayed; the V1 read-only readiness waiter timed out before invoking its final audit.

The minimal helper fix reads the already locked request and canonical specification SHA without re-entering the authority reader. Real same-inode, two-descriptor fixtures reproduce the old timeout and verify the corrected paths. An independently reviewed zero-model continuation kept the same request, budget, specifications, lease and source histories. Its engine SHA is `5ef37b56961101681c61d4e849381e1395d7e8017efba0e240367622e78e42db`, controller SHA `5ceb606b84c435457f3a6c8841525c8018d52d7e0ba8cc7e7962bb9a11dd0d86`, plan SHA `f336334774e5603ba6f97e19259470043fd3fc17ca0d043c144f8de01b254439`.

Two earlier UUID directories are pre-INTENT engineering tombstones, separate from the sixteen charged identities: `2a6e4b2a-a060-4817-8c44-fa3577e5ef37` and `aca642eb-5914-4151-bafd-3b64ba18d2c2`. They were never reused. Earlier CPU-mask, callback-directory, resource-field and mutable-pool preparation corrections are preserved with their actual qualification limits.

## Engineering-negative evidence and archive boundary

Each original INTENT, DONE, NATIVE_EXIT, raw gzip and raw bytes is retained. Missing model PID/maps, strace, kernel counters and population guards remain missing. No empty substitute is manufactured. No performance strict acceptance is asserted.

The original outbox requires a PID map, which legitimately does not exist for this failure. A separate closed-negative archive adapter accepts only the exact diagnosed class: the same request and UUID join, launcher 127, observed simulator false, unchanged original missing-strace raw bytes, and absent PID/trace. Its manifest contains only actual source files. SOURCE_KEEP, typed SHA, true164 chunk/full-stream verification and native restore remain required.

The adapter source SHA is `88f553f6be55aceee1b7a4849c1db13eac4b5cee21b4a069ef1f8a77ecc3ab18`; preparation manifest SHA is `510990aa05321c7eff338137f2666631ae1a8dce2af15fb7bcebee2e1c22c3c8`. Explicit archive provenance distinguishes this adapter from the registered original outbox. Actual per-identity archive receipts, native-restore proofs and the independent final review determine archive closure; CPU qualification alone does not.

True164 root: `/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1`.

Native evidence root: `/root/data/dtc_perf_first_v2_codesign16_20261105_v1`.

## Mechanism and hardware-cost limits

There is no measured combination interaction. Accepted V1 single-factor records remain separate evidence and cannot be multiplied into an unmeasured V2 combination or substituted into its failed cell. Kernel/request hypotheses remain attributed to their original sources.

Both intended combinations retain 512 lookup Tags and the original Hash, service, allocation and downstream conditions. With declared 128-byte physical-line accounting, 640 to 768/1024 lines is 80 to 96/128 KiB, or +20%/+60%. OO PIB and coupled lower-create depth each increase from 128 to 192, or +50%. These figures are resource accounting, not payload-SRAM, timing, area or equal-PPA proof. This execution supplies no measured benefit against those costs.

V1 and Remaining48 identity/budget/results stay separate. No Tag experiment, new reclamation mechanism, extra combination, capture, 109/GPU task or manuscript change was performed. English LaTeX v0.23 remains frozen.

## Next authorization boundary

The repaired launcher can support CPU-only preparation, but the old sixteen identities are exhausted. A recovery would require a new explicitly approved request and sixteen new one-use identities with the same frozen scientific scope. The pending recovery contract preserves all original negatives, introduces no replacement data, and proposes end-to-end launcher closure checks plus a small gate using legitimate planned identities. No recovery model is authorized or started by this closeout.

## Verified execution closure

All sixteen closed-negative archives and native restores completed. Independent final audit passed 207 checks, including each true164 chunk and whole-stream SHA, every restored typed entry and SOURCE_KEEP original, unchanged UUID/INTENT/DONE/raw joins, and the absence of invented PID, trace or performance strict evidence.

Independent final audit manifest: `agents/D_independent_review_v1/final_engineering_negative_archive_audit_v1/MANIFEST.json`, SHA256 `36dbbca1231b4142f025cf01b823ce6fb6dde8268ace5be7add0d04182df7ffe`.

All-16 archive summary: `engineering_incidents/launcher_runtime_missing_v1/negative_archive_forward_v1/ALL16_NEGATIVE_ARCHIVE_SUMMARY.json`. The source index binds its exact SHA and all sixteen result/receipt files. Native `analysis/EXECUTION_TERMINAL.json` records all sixteen archived engineering negatives. No model or archive task remains in this V2 cohort. The registry's historical request state field remains RUNNING because the original controller's exhausted-all-terminal branch writes EXECUTION_TERMINAL without changing that field; it is not evidence of a running simulator. Budget, consumed and remaining remain 16, 16 and 0.
