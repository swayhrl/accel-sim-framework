# Cumulative result budget amendment:16GiB

Direct user authorization received2026-10-18 (Asia/Shanghai):

> 可以把12G限制调整为16G，保证能做完成

This supersedes only the12GiB cumulative retained-result ceiling previously authorized by coordination20f1aab8df7c81a822b780172d8a3fa62bff3fb9. The one central EP-L2 host policy max_result_bytes becomes17179869184. It is aggregate across original results, new results, all campaigns and retained attempts; no per-campaign reset. All new full application output remains on the verified physical workspace filesystem.

Workspace48GiB, Share40GiB, available-memory64GiB, max4sim/8CPU/32GiB reservation, per-run2GiB raw cap, conservative concurrent output reserves,72 starts, original T0/deadline and current V2 scientific qualification/acceptance remain unchanged. This amendment grants no cleanup, migration, build, alternate registry, extra watcher or scientific promotion.16GiB is a ceiling, not a reservation of physical free space or a guarantee against other projects' writes. Fail closed at any unchanged protection boundary; do not expand again without authorization.

R3 had already stopped before any operator signal: FWT/S64 failed after2351.5s because its monitor stat raced with replacement of .PAPER_CLOSURE_QUEUE_R3_PROGRESS.json temporary file. Preserve FAILED raw/result and the prior final checkpoint c0ff10d43e045687914c23a317870c40b0a220de. Only ENOENT during retained-file enumeration is ignored by the repaired counter; permissions and I/O failures still propagate. No Core/binary/config/input/scientific parser changes.

One same-key audited S005 retry uses a distinct output directory, keeps the failed attempt in attempt_history, and consumes one original campaign start. R4 is a replacement scheduler process for the same campaign, not a new Goal or experiment. It adopts an existing exact audited retry only; cannot implicitly retry a terminal key. Other admitted/accepted keys are never duplicated. Four-way results and terminal boundary checkpoints continue through existing V2 and Lane3/6 deliveries.
