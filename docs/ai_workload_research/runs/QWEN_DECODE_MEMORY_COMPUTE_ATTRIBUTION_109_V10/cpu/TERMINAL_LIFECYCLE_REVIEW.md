# Terminal lifecycle CPU audit

Historical NCU_B1 STOP is consistent with a narrow completion/teardown observation issue. Keep its original GPU_RESOURCE_DEFERRED receipt unchanged; this review does not retroactively accept the run.

Among 149 samples, only zero-based sample 147 has a gap: WORKER_NOT_HEALTHY. No sample has unknown/invalid/unqualified GPU PID. Sample 147 still identifies actual worker 3747110 with the same birth and NVML memory; worker RSS was 0. Sample 148 has own NVML bytes 0. All recorded resource peaks were below limits.

WORKER_FINISHED matches bound task,nonce,supervisorPID,full worker identity and sourceSHA; raw identity matches, and both statuses are V9_WORKER_COMPLETE. Launcher exit is 0. The log contains one pass, terminal status, profiler disconnect and completed report. Marker mtime precedes failing sample by 0.232s; final zero-context sample follows failure by 0.321s. These are wall/mtime comparisons, not recorded first-seen monotonic timestamps.

The old dispatcher uses WORKER while any owned GPU context remains, even after a terminal marker. rss_lifecycle then requires healthy worker. This explains the sole observed failure without authorizing unknown compute. RSS0 alone does not establish zombie state or no CUDA activity.

A distinct FINISHED_CONTEXT_DRAIN phase is acceptable only after strict marker/raw/frozen-source validation, with first-seen monotonic deadline<=6s, original GPU worker binding retained and every other monitor rule unchanged. Require context clearance and successful exit before next task. PID absence with NVML row, identity reuse/unreadability, unknown compute, shared-gate failure, memory/disk/time overrun or deadline expiry must still STOP. Existing censored RSS race rules remain unchanged.

Tests must cover valid bounded teardown; each marker mismatch; malformed/stale markers; wrong raw status; unresettable timeout; every existing resource/identity failure; launcher-first exit; nonzero exit; prohibited next task and context reappearance.

JSON includes exact sample summaries, marker comparisons, source lines/hashes and risk boundaries. The new B2 implementation is recorded only as parent-reported; its outcome is not inferred here. No GPU or model execution occurred, and no execution source or old raw was modified.
