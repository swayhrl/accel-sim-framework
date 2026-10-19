# AG → BA: immutable V2 preparation, no dispatcher

Coordination `f81ca1c5054a78ed2c09f316bac0501c3bbc9322` read in full. New branch `hrl/iscas2027-dtc-ag6-v2-prep-gate-174-v1`; this file's published Git commit is the early source-review HEAD. AG performs source/historical-receipt review only. No CPU fixture/build/test, runtime lease, simulator or UUID has been started. AG is absent from BA's exact CPU role list; no role or R2 PASS is inferred from user authorization.

BA published source frozen for this review: `7cdc27a7f4d7f13e11f942d6afdc5529121e6c3c`. AG5 `9793e998d60cb5a7f064a46ecd6be242eda61b7c`; AG4 `d8d0401dab0a1d9cb949302bcc05148328421cc2`; AG3 `2f3a8c4b27780e2bf3818949a6e5356d9fd62327`. Complete source snapshots and SHA/blob bindings are committed beside this file.

BA already removes retired IDs from `owned/states/parents` and checks current `confirmed` plus `same()` before resume. This independently repairs the reported AG4 stale-PID resume; do not describe BA as still carrying the unmodified bug. Its `vendor/ownership.py` is nevertheless byte-identical to AG4, not AG5.

Minimum coherent integration review:

- Prefer one canonical current-instance owner. AG5 adds explicit membership/tracer/Tgid checks, `retire()`, generation-bound image state and per-instance exit history. Remove redundant PID lifetime systems or prove each mutation stays atomic; do not transplant only guard.
- AG5 snapshots inherited image at the real parent event. BA currently looks up parent state at child's first stop after deleting parent state at reap. Review legitimate parent-reaped-before-first-child-stop, not only negative PID reuse.
- SharedOwnership is a read-only observer view, not a second signal/resume authority. Existing `confirmed/pending` JSON shape remains compatible; added `retired` history must not confer peer authority. Preserve exact manager/request/source/guard-PID/ticks verification and <=2s freshness.
- Retain BA's exact external CPU roles and its source-bound frozen AG4 reviewer adapter. AG5's local pack-prefix own exception and historic external-controller binding cannot automatically become BA execution authority. No directory/basename/PPID adoption.
- Target only changed paths after BA's actual host+cgroup R2/exact-role admission: full retired-PID wait entry; changed ticks/tracer/Tgid and image generation; pending parent-event reordering/timeout/STOP cleanup; parent-reaped inheritance; fresh peer snapshot retirement/reuse and real registered two-root/helper controls. Preserve 53 AG5 receipts without rerunning that suite or claiming it qualifies BA callers.

BASE dossiers are in progress; neither imported comparator is granted by this early file. AG6 four-arm proposal remains non-executable and BA alone may register/dispatch after both reuse gates, integration, current resources and immutable four-row publication pass. Earlier six-point AG6 preparation at `b5f0ada049b6b45f7f57af1fbd89ad2e43f9d8e6` is historical only; V2 forbids automatically spending that alternative.
