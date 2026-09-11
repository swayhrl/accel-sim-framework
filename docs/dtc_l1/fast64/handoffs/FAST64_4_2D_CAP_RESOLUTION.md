# FAST64.4 2DConvolution lower-cap resolution

Status: **RESOLVED — supports FAST64_4_PRIMARY_PASS**

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

This control naturally terminated exit zero at `2026-09-11T17:11:01Z` and
strict-collected to
`generated/fast64_4_2d_cap_resolution_v1/fast64_4_2DConvolution_io_cap1048576_core658_a1_v1.json`
(SHA-256 `8f157ed21b05c0b55fdb70554808ad8b67e3bed570872a84a9b75bf09b0ca9c1`).
It records `627,281` cycles / `620,347,492` instructions, cap-full `0`, lower
credit acquire/release `3,375,831/3,375,831`, IO
create/issue/response `3,375,831/3,375,831/3,375,831`, dependencies
`7,835,916/7,835,916`, and final inflight/PIB/lower `0/0/0` with a clean
error scan. It remains a control, not a primary performance result.

The 8192-versus-high comparator reports non-cap metric differences, including
cycles `627,590 -> 627,281`, while 8192 has cap-full `72,236` and high has
zero. Thus 8192 is conclusively cap-bound; no performance observation selects
the next point.

## Future-only cap-resolved collector

`util/dtc_l1/collect_fast64_4_cap_resolved_matrix_v1.py` is prepared and
regression-tested, but has not collected a primary matrix. It imports the
frozen V1 writer only after SHA verification and requires a fresh explicit
36-cell cap-resolution map. The map binds one final common cap, each row's
literal config identity, and the SHA of this resolution authority.

A row at the final cap must be classified `REACQUIRED_AT_FINAL_CAP`. A row
observed at any smaller candidate may enter only as
`SOURCE_PROVEN_CAP_INERT_REUSE_TO_FINAL`, with zero cap-full and the source
proof that the cap guard is not reached. This permits an explicit inert reuse
from (for example) 16384 to a later common 32768 cap; it does not silently
equate configs. The legacy 8192-specific spelling remains readable only for
an existing 8192 map. Any other cap identity mix, including the retained bound
2D IO@8192 diagnostic, is rejected before output publication. The collector
has no simulator authority and emits only a candidate output; it cannot create
a FAST64.4 PASS marker.

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
reused. Following high-cap strict validation and fresh resource admission, all
nine immutable-v2 rows launched once at `16384` on distinct physical CPUs
`6,7,8,9,10,11,12,13,15`, with dispatcher SHA-256
`23f2f0ee29954c6eb639691ea235e3871a0e12059dd18a1b6cbd6f57ee547368`.
They remain `FAST64_4_CAP16384_CANDIDATE_PENDING_RESOLUTION`; no result is
selected until a common candidate passes the same non-binding comparison rule.

Hotspot1 IO/OO are the first 16384 terminals. Both strict-validate accounting
and drain but remain bound (`25,887` and `23,026` cap-full events,
respectively), so 16384 is not frozen. Future-only
`dispatch_fast64_4_cap32768_hotspot_v1.sh` and its two full one-line-diff
configs pass dry run for the next 32768 point; it uses only the two CPUs freed
by the terminal Hotspot rows while the other seven 16384 rows remain untouched.

## First strict terminal batch

The first eight recovery compact records have now passed the immutable strict
collector. They are evidence only while the remaining three 16384 rows run:

| workload / mode | observed cap | cycles / instructions | cap-full | disposition |
| --- | ---: | ---: | ---: | --- |
| Gaussian / Base | 16384 | 4,229,815 / 283,685,120 | 0 | explicit inert-reuse candidate for a later common cap |
| LUD / Base | 16384 | 1,113,878 / 184,963,840 | 0 | explicit inert-reuse candidate |
| LUD / IO | 16384 | 1,091,487 / 184,963,840 | 0 | explicit inert-reuse candidate |
| LUD / OO | 16384 | 1,087,849 / 184,963,840 | 0 | explicit inert-reuse candidate |
| Hotspot1 / IO | 16384 | 85,670 / 377,291,004 | 25,887 | cap-bound diagnostic, never primary |
| Hotspot1 / OO | 16384 | 84,174 / 377,291,004 | 23,026 | cap-bound diagnostic, never primary |
| Hotspot1 / IO | 32768 | 85,633 / 377,291,004 | 0 | next-candidate strict terminal; common-cap candidate only |
| Hotspot1 / OO | 32768 | 84,173 / 377,291,004 | 0 | next-candidate strict terminal; common-cap candidate only |

The 16384-to-32768 Hotspot transition is the first source-defined monotonic
proof that 32768 is needed by at least one primary workload: both modes bind
at 16384 and neither reaches the cap guard at 32768. It neither selects based
on speedup nor promotes 32768 until 2DConvolution IO and Gaussian Base/IO/OO
complete the common-cap resolution. The strict JSONs are contained under
`generated/fast64_4_cap16384_recovery_v1/` and
`generated/fast64_4_cap32768_recovery_v1/`; raw simulator output remains only
in the external immutable run namespaces.

## Resolution closeout

Core658 2DConvolution IO@16384 naturally exited zero with UUID
`93fce0ff-5163-4a7c-9d48-6cb01fb04dc7` and strict compact result
`fast64_4_2DConvolution_io_cap16384_core658_a1_v1.json`: `627,281` cycles,
`620,347,492` instructions, cap-full `0`, IO create/issue/response
`3,375,831/3,375,831/3,375,831`, dependencies
`7,835,916/7,835,916`, and terminal inflight/PIB/lower `0/0/0`.

Consequently all former 8192-bound cells have a source-proven non-binding
observation at 16384 or 32768. The SHA-bound
`FAST64_4_CAP_RESOLUTION_AUTHORITY_V1.md` freezes 32768 as the common
formal cap and names the literal source cap/config for every Base/IO/OO cell.
`FAST64_4_CAP_RESOLVED_PRIMARY_REGISTRY_V1.tsv` plus
`FAST64_4_CAP_RESOLUTION_MAP_V1.tsv` were accepted by the fail-closed
cap-resolved collector, producing the exact 36-cell candidate package
`generated/fast64_4_cap_resolved_matrix_v1/`. This resolves the cap gate and
supports `FAST64_4_PRIMARY_PASS`; the high-cap control and all bound rows
remain diagnostics rather than primary performance results.
