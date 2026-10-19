# B — source r2; native correctness still pending

Authority d9263fa2431592b33e900d9b48c6f20029d8b544 and original174 retained.
Core b90ed7c14e7b00ec4c68a26af224be3d2620f647 is pushed and exact remote
SHA/tree/all38 B-file bytes verified. Branch hrl/ep-l2-ms20261019-b-victim-v1.
Old clean-first Core89a75b24, Framework ebfb5371, review pack r1, RO/parameter
candidates and all old raw/ledgers remain intact. R1 source was not qualified.

R2 adds two independent SOURCE candidates after the clean checkpoint:

- Dirty pending/inflight: distinct client+UID+generation keys in the existing
  non-RG1 bank scoreboard; hold WB role while a reader pin protects a queued
  operation, defer role transfer across lower acceptance/set_done until actual
  enqueue/unpin. Preserve P1, independent packet snapshot, writer/atomic wait,
  partial unknown-sector fallback, UID cancellation and token drain.
- Fixed capacity64: reciprocal bank quotas16 victim/276 other, total64/1104 of
  original1168. Unused64 is withheld from all non-victim roles even with zero
  victims. One exact-handle replacement credit supports real landing/rollback;
  promotion cannot exceed non-victim quota. This is a fixed bank-capacity
  partition with identical pointer mapping, NOT fixed physical IDs or a new
  victim SRAM. Other-role headroom at1024 residents is80 instead of144.

Six A-owned public files remain identical to84359d4. B only generated a textual
adapter; A alone integrates it with newer diagnostic/observer interfaces and
reviews WAD metadata query/update/completion ports and control costs. No whole
historical branch merge. R2 consumers require r2 adapter, never r1 hooks.
Do not delay A's independent diagnostic release on B. RO/diagnostic/RG1/MQ2/
P2/C8 combinations and fixed+dirty are unqualified.

18 finite process inputs are prepared, zero compiled/executed: source-bound old
bank alias failure (expected21, NOT observed), independent logical drain/P1/
UID cancel/generation reuse; fixed quota/credit/rollback; actual primary cache
nonzero returned-sector reference with OFF/ON lower requests; negative stream;
partial/out-of-order fill; dirty inflight and pending completion while reader
bank-denied; dynamic/fixed96-line contrast; native simple-DRAM issue groups and
host-prefill exact alias gates. Numerical expectations are unexecuted assertions,
not actual hits or saved reads. No runtime effective dump or binary exists.

One bounded current resource/process read at13:34UTC found workspace5600256000B,
below51539607552B. Two simulator processes belonging outside B were observed
and left untouched. New shared registry still lacks E admission/handoff; no
shadow registry or watcher was created. B started zero compiler, native tests,
simulators, leases or full apps. Text/Python AST/hash/patch checks passed ONLY.

Actual clean responses and DRAM-read change remain UNKNOWN; full dirty/fixed
qualification is also pending. Need A's exact integrated objects and metadata
review, E admission under unchanged resource floors, actual finite execution
including remaining ICNT/pin/rollback/generation/epoch boundaries, then E's
independent qualification. Goal is active and incomplete; source progress must
not be labelled completed functionality. Continue on the exact A/E dependency
event without a resident poller. Review pack: MS20261019_B_VICTIM_SOURCE_r2.
