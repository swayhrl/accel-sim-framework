# DTC-L1 Current State

Last coordination update: 2026-09-03

Status: **M1 PASS; M2 HARD-STOPPED ON IO RESPONSE ROUTING; RECOVERY AUTHORIZED**

## Source anchors

Frozen M0 framework anchor:

- official: `accel-sim/accel-sim-framework:dev`;
- official base SHA: `d930ad6d02c09bb56867132583735aba0389cff4`;
- M0 branch: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-v0`.

Frozen M0 core anchor:

- official: `accel-sim/gpgpu-sim_distribution:dev`;
- official base SHA: `91880c53383d5a6a6742bfb1be2c5f34e39c7871`;
- M0 branch: `swayhrl/gpgpu-sim:hrl/decoupled-l1-v0`.

Active goal branches:

- Core: `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`;
- Framework: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`.

## M1 closeout — PASS

M1 Foundation is independently reviewable at:

`docs/dtc_l1/review_packs/M1_FOUNDATION/README.md`

Validated Core M1 closeout anchor:

`48b0be73833fc89fcf833349e82886ddc6d883b0`

M1 established:

- exact-neutral `LEGACY` boundary against frozen upstream;
- explicit Paper-Base PIB/backpressure;
- paper Tag-bank arbitration;
- conventional Paper-Base MSHR capacity/merge behavior;
- lower outstanding-cap accounting;
- common counters/parser plumbing;
- B07 recovery for the L1-hit true-completion PIB retirement leak;
- all B01-B09 and M1 accounting/hygiene HARD gates PASS.

M1 is closed and must not be weakened to solve later DTC issues.

## Current M2 committed state

After M1, Codex committed directed/scaffolding work for the IO frontend, including:

- whole-line IO logical Tag -> physical model helpers;
- physical `{id,generation}` identity;
- configurable 16KB/4-way logical and 80KB physical geometry;
- RR physical allocation with width control;
- directed IO eviction/generation tests;
- access to already-coalesced source data needed to form 128B line references.

The current committed Core branch is clean at the reported M2 stop SHA. The failed real request/response experiment was discarded rather than pushed.

## M2 HARD failure

The first real `PAPER_IO` VecAdd integration created an IO-owned lower request that correctly bypassed conventional L1D MSHR allocation. On return, the existing `ldst_unit::cycle()` cached-read response branch still called:

`m_L1D->fill(mf, ...)`

That conventional fill path requires `baseline_cache::m_extra_mf_fields`, which a true IO-owned request intentionally does not have. The simulator therefore asserted in `baseline_cache::fill()`.

Evidence:

`docs/dtc_l1/implementation/M2_IO_INTEGRATION_FAILURE.md`

The STOP was correct. No M2 PASS is claimed; M3/M4/M5 have not started.

## ChatGPT recovery design

The failure demonstrates that Paper IO must own the **entire read lifecycle**, not merely Tag/physical allocation and request issue.

Required architecture for cacheable PAPER_IO reads:

1. DTC PIB owns the dynamic instruction lifecycle;
2. DTC logical Tag/physical allocation owns hit/pending/miss state;
3. DTC new miss creates one DTC-owned whole-line lower request;
4. an immutable request identity maps the returning request to `{phys_id,generation}`;
5. response dispatch recognizes DTC ownership before conventional L1D fill;
6. DTC response marks the intended physical allocation ready and releases lower credit;
7. the IO FIFO head retires through a finite operand-collector/writeback-aware DTC path;
8. conventional L1D MSHR/`m_extra_mf_fields`/`next_access()` are not used to simulate DTC read completion.

The detailed authorized recovery is:

`docs/dtc_l1/goal/M2_IO_RESPONSE_RECOVERY_SPEC.md`

## Additional source-review risks to resolve during recovery

### Completion cardinality

The current simulator increments load `m_pending_writes` from upstream `accessq_count()`, which may reflect sector transactions. Whole-line Paper IO instead uses unique coalesced 128B line references. PAPER_IO completion accounting must use the same dependency cardinality as its PIB model while leaving LEGACY/PAPER_BASE unchanged.

### Sticky allocation-block state

The current committed `io_frontend` keeps an `allocation_blocked` entry flag. A failed allocation followed by a retry that resolves as a Valid/Pending Tag hit can leave that flag stale. Recovery must make allocation blocking transient (or otherwise prove every transition clears it correctly) so historical resource pressure cannot permanently prevent retirement.

## Active execution authority

Follow:

- `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`;
- `docs/dtc_l1/goal/M2_IO_RESPONSE_RECOVERY_SPEC.md`;
- existing M1-M4 goal/counter/validation specifications.

Required recovery order:

1. R2.0 prove lower-request identity round trip;
2. R2.1 dedicated IO request ownership and response dispatch;
3. R2.2 dedicated IO PIB payload and writeback/retirement;
4. R2.3 completion-cardinality alignment to 128B line refs;
5. R2.4 allocation-block-state correction/proof;
6. R2.5 prove IO read isolation from conventional L1D MSHR/fill;
7. R2.6 real VecAdd smoke;
8. R2.7 full M2 I01-I15/no-MSHR/accounting closeout.

If M2 fully passes, Codex may automatically continue M3 -> M4. Any HARD failure still requires STOP. M5 remains forbidden.