# FAST64.4 2DConvolution lower-cap resolution

Status: **ACTIVE — no FAST64.4 promotion**

## Trigger and preserved evidence

The Core658 common-identity 2DConvolution rows both naturally terminated exit
zero and passed the immutable strict collector:

| mode | UUID | compact record | cycles / instructions | terminal state |
| --- | --- | --- | --- | --- |
| PAPER_IO | `437620fb-ef5b-436e-8f35-63e7f1df0f4c` | `generated/fast64_4_2d_tag_identity_v2/fast64_4_primary_2DConvolution_io_core6587238c_a1_v1.json` | `627,590 / 620,347,492` | lower/PIB/inflight `0/0/0` |
| PAPER_OO | `981ff10e-492d-479d-b41f-a916a0c14a58` | `generated/fast64_4_2d_tag_identity_v2/fast64_4_primary_2DConvolution_oo_core6587238c_a1_v1.json` | `593,208 / 620,347,492` | lower/PIB/inflight/active-refs `0/0/0/0` |

The IO compact record reports `DTC_L1_lower_cap_full_events = 72,236`; OO
reports zero. This is not a lifecycle failure: IO lower
create/issue/response and dependency count/closed are conserved, and final
lower/PIB/inflight is zero. It proves that the 8192-cap candidate binds for
this representative IO traffic. The strict rows are retained as
`CAP_BOUND_DIAGNOSTIC_NOT_PRIMARY_RESULT` for this resolution and cannot enter
the FAST64.4 matrix at candidate cap.

## Source and platform classification

FAST64's frozen platform is **64 x 1 endpoints plus cap 8192**, distinct from
the historical M5 80-SM/cap-10240 platform. The final effective settings in
each FAST64 primary config are `-gpgpu_n_clusters 64`,
`-gpgpu_n_cores_per_cluster 1`, and
`-gpgpu_dtc_l1_lower_outstanding_cap 8192`; earlier shell values are overridden
by the intentional FAST64 overlay.

Core658 `src/gpgpu-sim/gpu-sim.cc` increments
`m_dtc_l1_lower_cap_full_events` only when global outstanding requests are at
the configured cap, then denies the acquisition. The IO observation is
therefore a direct global-lower-cap binding observation, not a Tag-bank alias
or parser artifact.

`FAST64_PLATFORM_CONTRACT.md`, `FAST64_ACCEPTANCE_CONTRACT.md`, and
`FAST64_3_4_EXECUTION_CONTRACT.md` require this outcome to reopen candidate-cap
resolution: when 8192 binds, select the smallest common cap proven non-binding
before primary performance interpretation. The frozen V2 coverage builder
correctly fail-closed at `IO_PROGRESS_OR_CAP_INVALID`; its bytes are unchanged.

## Isolated high-cap control

`FAST64_IO_CAP1048576.config` differs from `FAST64_IO.config` only in the
final effective lower-outstanding cap (`8192` to `1048576`). Its 64-SM
platform, DTC IO mechanism, payload, observer, Core, and trace-config
identities remain unchanged.

After a fresh V3 resource admission at `2026-09-11T16:19:18Z` (`YES`, no
swap-out/OOM/PSI/CFS throttling), the following immutable control launched
once:

| field | value |
| --- | --- |
| namespace | `/workspace/fast64-primary-r4-cap-recovery/fast64_4_2DConvolution_io_cap1048576_core658_a1_v1` |
| UUID | `c6dca067-6de7-47ee-958c-185ce083fb7b` |
| launch UTC | `2026-09-11T16:19:50Z` |
| Core / runtime | `6587238c60214d99491f4048e28ce8a3458c1509` / `29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1` |
| Framework snapshot / A1 | `037f008b330eb230353b60edf126d6be9f45afdc` / `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e` |
| classification | `FAST64_4_NONBINDING_CAP_CONTROL_PENDING_RESOLUTION` |

This is a control, not a performance result. At natural terminal it must
strict-validate its receipt, payload, config-only diff, accounting, drain and
zero cap-full observation. The 8192-versus-high comparison then determines
the next source-correct sweep point(s); no cap is selected for DTC speedup.

## Future-only cap-resolved collector

`util/dtc_l1/collect_fast64_4_cap_resolved_matrix_v1.py` is prepared and
regression-tested, but has not collected a primary matrix. It imports the
frozen V1 writer only after SHA verification and requires a fresh explicit
36-cell cap-resolution map. The map binds one final common cap, each row's
literal config identity, and the SHA of this resolution authority.

A row at the final cap must be classified `REACQUIRED_AT_FINAL_CAP`. An old
8192 row can enter only as
`SOURCE_PROVEN_CAP_INERT_REUSE_8192_TO_FINAL`, with zero cap-full and the
source proof that the cap guard is not reached. Any other cap identity mix,
including the retained bound 2D IO@8192 diagnostic, is rejected before output
publication. The collector has no simulator authority and emits only a
candidate output; it cannot create a FAST64.4 PASS marker.

## First monotonic candidate prepared

The high-cap IO-mode summary does not expose `DTC_L1_lower_outstanding_peak`;
the source only prints that peak in the Base reporting branch.  The first
source-neutral monotonic candidate is therefore `16384`, immediately above
the failed `8192` point.  It is a sweep point, not a selected final cap.

`FAST64_{BASE,IO,OO}_CAP16384.config` each differ from their frozen source
config in exactly one final effective line: `8192 -> 16384`.  Future-only
`dispatch_fast64_4_cap16384_recovery_v1.sh` passes its nine-row dry-run with
immutable runner and namespace absence checks.  Its fixed acquisition set is:

- 2DConvolution IO under Core658/runtime29a;
- Gaussian Base/IO/OO under Core95/runtime462;
- Hotspot1 IO/OO under Core95/runtime462;
- LUD Base/IO/OO under Core95/runtime462.

The set contains every known cap-bound 8192 primary cell and only the two
additional Base rows required to keep new Gaussian and LUD triplets on a
common Core95/runtime462 identity.  Existing 8192 rows with cap-full zero
remain candidates only for source-proven cap-inert reuse; no bound row is
reused.  The sweep will start only after this high-cap strict validation and a
fresh resource admission; no result is selected until a common candidate
passes the same non-binding comparison rule.
