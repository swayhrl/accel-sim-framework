# B r2 full-source intake — not integrated, not a runtime verdict

Frozen B Coreb90ed7c14e7b00ec4c68a26af224be3d2620f647, Framework3174a3287bab55c770ebb05d1bad5aa07a5b80cb.
A already published separate CLEAN94996ec59b4a0264b64146932977bfe6ea4f195b,
using B89a75b24. Do not replace that candidate or apply a base843 patch over it.
All B r2 native tests remain uncompiled/unrun. No physical reachability failure
or old-red/new-green is claimed by this source intake.

Concrete public-patch gaps versus the now-frozen A contract:

- adapter_r2_full/A_PUBLIC_HOOKS.patch332 retains the two-argument completion
  API, and421–426 locates the row only by address after birth/lifetime state
  has already changed. Port A's existing WB UID check BEFORE mutation and
  completion row incarnation guard; do not restore an address-only callback.
- The same patch608 does a new functional find during rollback;719 does
  another at lower acceptance. A CLEAN already uses owned row tickets there.
  Preserve those exact ticket/liveness checks and declare any genuinely new
  dirty-promotion read/control concurrency; do not count these as observer scans.
- Module ep-l2-tvd-directory.h has no WB UID binding API at this source. Port
  the A CLEAN row fields/bind/complete contract alongside the new dirty states;
  never mix an r2 consumer with an r1/A module by just changing an include.
- B adds same-handle bank client+UID+generation matching and cancellation,
  retaining WB role while a reader pin protects the request. This requires
  actual lower/read competing-grant, set_done-before-reader, role-switch,
  rollback and stale-generation tests on the integrated public arbiter. Its
  pending_operations<=4 assertion is a source obligation, not tested capacity.
- fixed-pool source1–5 says fixed CAPACITY quotas16 victim/276 other perbank,
  not fixed physical slot IDs. This withholds64 capacity and preserves1168
  total; new functional quota scans and the transitional retention credit are
  explicit control costs. It cannot be labeled a measured physical fixed-array
  control or given old R3 PPA. Keep fixed CLEAN separate from full dirty.
- Current A diagnostic/observer fields, real bypass FIFO/admission repair,
  shared128 directory, default-OFF behavior, dirty-sector/atomic completion and
  query/metadata ports must survive any new six-file adapter. TVD/RO/diagnostic
  combinations remain rejected. B r2 does not block the primary R1 build.

This intake identifies exact merge/source-cost obligations. Integration and
new native evidence follow an exact isolated candidate and E admission, not
wholesale restoration of the old base843 public patch.
