# A dirty/fixed source checkpoint r5

Independent R3 ports frozen B b90ed7c1 onto A CLEAN94996ec5, preserving the
already-published diagnostic/CLEAN/RO worktrees. CURRENT STATUS/RECEIPT,
R3_DIRTY_FIXED_SOURCE_CANDIDATE and native plan bind exact source/config scope.
All21 native processes and new C++ compilation remain UNRUN. The legacy
matching test has expected exit21 only, not observed old-red/new-green.

Two explicit control-source corrections retained by A: indexed row/incarnation
at lower/rollback, existing WB UID/state validation before completion mutation.
The dirty reader pin keeps WB role stable across acceptance/completion until
actual response. Fixed64/1104 is a capacity control, not fixed slot IDs. New
metadata/selection/quota/update logic and unknown PPA are explicit. Original B
source manifests/patches remain input provenance, not current qualification.

PREVIOUS_06c8e258_* preserves the r4 source receipt verbatim. No native compiler,
application, new lease, old-source reset, data deletion or resident waiter. E
owns fresh resource admission and every new full-app start/acceptance. Primary
R1 Core17e7e224 and its exact E-compatible build entry are unchanged and first.
