# R9 user-authorized40-slot host scheduling plan

The user explicitly raised the scheduling upper bound to40 and requested that
work start whenever resources permit. This is an upper bound, not a claim that
40models were already live. The container has256GiB RAM, while each unchanged
scientific job retains its16GiB hard RSS/address-space cap. Treating every hard
cap as committed future physical RAM prevents high concurrency even when actual
working sets are much smaller.

New never-spent cells use HOST_WORKINGSET40_V2. Its admission estimate is
min(hard,max(4GiB,ceilGiB(8*largest_trace_member+1GiB),
ceilGiB(2*actual_model_RSS+1GiB))). This is a planning estimate, not an absolute
peak guarantee or a4GiB hard cap. Admission retains64GiB host and48GiB cgroup
headroom plus projected additional working sets. Runtime safety uses actual
host/cgroup effective headroom instead of killing a completed-input candidate
merely because a future reservation estimate changed. The clean-inactive-cache
credit still excludes shared/mapped/dirty/writeback pages plus8GiB; its raw
memory.stat inputs and each per-job envelope are now captured in samples.
All original hard caps, BA policy/telemetry, Core/cache/config/input and model
argv remain unchanged. No new scientific canary or model retry is introduced.

Every already-spent141-prefix native frontend/model remains untouched. While
any such V1 model is live, new admission and runtime ALSO retain the exact V1
full-hard-cap predicate; new admission adds8GiB compatibility margin. Thus the
old guard can temporarily limit actual parallelism near11–12 even with a40-slot
parent. As those original models naturally close, the new-only working-set pool
can expand without stopping or relabeling an old run. There are at most4fresh
admissions per60seconds,40maximum, on distinct physical model cores with a
separate frontend CPU pool. Original result caps remain unchanged; any growth
of the registered own write ceiling stays within fresh5GiB+peer capacity.

The latest R8 issue is COPY-only: BFS-CM naturally ended and passed independent
full strict checks, but the shared receiver was busy. The newer frontend's
BlockingIOError(11,...) representation was not recognized by a brittle string
matcher. R9 recognizes structured errno11 and both legacy EAGAIN forms only for
archive waiting. The frontend preserves legacy str(error) text and adds typed
errno. Resource HOLDs still defer ONLY before INTENT and consumption; there is
no second model execution for any spent cell. Unknown issues still checkpoint.

The same finite356 parent request, canonical cells,141spent prefix and72x4 final
scope remain. Parent-only retirement preserves all live original generations.
A stable, independently rechecked natural/strict closed point awaiting COPY may
be adopted without waiting for the old parent to resolve its string-matcher
checkpoint. Its final performance acceptance still requires true164 archive and
independent native restore. R6 Cutcp and all final SHA/publication/recovery/
authority gates remain mandatory. Seventeen zero-model checks and exact source
publication precede activation; runtime receipts establish actual outcomes.
