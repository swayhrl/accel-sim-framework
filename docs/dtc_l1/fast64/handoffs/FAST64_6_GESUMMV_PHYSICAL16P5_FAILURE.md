# FAST64.6 — GESUMMV physical-16.5-KiB terminal-failure record

Status: **PRESERVED TERMINAL FAILURE — NOT A RESULT; SOURCE-BACKED
CAPACITY-BOUND CLASSIFICATION CLOSED**

This record preserves the two exact frozen physical-16.5-KiB GESUMMV attempts
separately from retained FAST64.6 precompute results.  It does not alter the
frozen sensitivity roster, claim a stage result, or authorize a mechanism
change.

| mode | UUID | terminal UTC | exit | raw namespace |
| --- | --- | --- | ---: | --- |
| PAPER_IO | `8a6207ac-b653-4c4f-afb5-d298e8a91bcd` | `2026-09-10T19:49:11Z` | 1 | `/workspace/fast64-sensitivity-v1/fast64_sens_v1_gesummv_physical16p5_io` |
| PAPER_OO | recorded in the original v1 launch receipt | `2026-09-10T19:28:47Z` | 1 | `/workspace/fast64-sensitivity-v1/fast64_sens_v1_gesummv_physical16p5_oo` |

Both runs bind formal repaired Core `95ccdb7a...`, runtime `462d105c...`, A1
observer, scientific Framework `037f008b...`, the immutable-v2 runner and the
frozen GESUMMV payload.  The IO manifest specifically records
`FAST64_SENS_PHYSICAL_16p5KB_IO`, SHA `475b8eab...`; its terminal receipt is
atomic and exit status is `1`.

## Observed, not inferred

The IO stdout contains the simulator deadlock detector at local cycle
`37,997,199` (global cycle `4,256,917,296`) after 52,801 no-writeback cycles.
The dump shows an empty L1D MSHR, miss queue, and response FIFO for the printed
core.  The pre-existing OO attempt also reached the deadlock detector.  These
facts are sufficient to exclude either attempt from the strict-pass registry.

They are **not** sufficient to label either failure
`EXPECTED_RESOURCE_DEADLOCK`: the current formal deadlock dump does not print
the mode-equivalent DTC physical-pool ownership/free-line state required to
prove a circular undersized-pool condition.  No timeout, host slowdown, or
lower-cap-full observation is used as a substitute.

## Diagnostic collection and source-backed classification (2026-09-11)

The two V2 observational replays have now both reached their own immutable
terminal receipts (exit `1`) and the unchanged V2 collector atomically
published the mode-specific compact observations:

| mode | diagnostic UUID | terminal UTC | compact observation |
| --- | --- | --- | --- |
| IO | `5a6b4eeb-1563-49f5-8af0-a20ded38fc3c` | `2026-09-11T07:10:43Z` | `generated/fast64_6_diagnostics_v2/fast64_6_gesummv_physical16p5_io_coref283_diag_v2.json` |
| OO | `ac6c1a27-7980-4cdc-85c1-64974a536b76` | `2026-09-11T06:59:05Z` | `generated/fast64_6_diagnostics_v2/fast64_6_gesummv_physical16p5_oo_coref283_diag_v2.json` |

Both observations are explicitly `NONFORMAL_DIAGNOSTIC_NOT_RESULT`.  They
retain the frozen f283 observational Core, its immutable runner, the original
payload/config identity and the source print's mode separation; neither JSON
is a formal sensitivity row.

Each of the 16 printed IO SMs has `allocated_phys=132`, `free_phys=0`, one FIFO
PIB and frontend entry, a non-ready head, `partial_entries=1`,
`partial_lines_held=31`, and zero lower-create/lower-issue/inflight work.  Each
of the same 16 printed OO SMs has one
PIB/frontend entry, `allocated_phys=132`, active references 28--31, and zero
lower-create/lower-issue/inflight work.  The configuration freezes exactly
132 physical 128-B lines (16,896 B), so the OO `allocated_phys=132` state also
exhausts the pool.  Thus the diagnostics exclude a pending lower response,
lower-create queue, lower-credit, or host-progress explanation.

The f283 diagnostic source prints these fields in
`src/gpgpu-sim/shader.cc` through `print_dtc_l1_io_deadlock()` and
`print_dtc_l1_oo_deadlock()`.  The frontend semantics are source-defined:

- IO `access()` keeps an owner's already allocated references when
  `find_free_physical()` fails, records an unresolved line, and its FIFO head
  cannot retire until `entry_ready()`; only retirement releases deferred lines.
- OO `access()` rejects a new allocation when there is no free physical line
  and its victim has nonzero reference count; final-reference reclamation is
  performed only by a ready entry's retirement.

`git diff f2836ea1..dc6062` is empty for these two source files, so the source
mapping is exact for the observational binary rather than inferred from a
later mechanism revision.  The combined terminal state is therefore a
**SOURCE_BACKED_CAPACITY_BOUND_RESOURCE_DEADLOCK** at the frozen undersized
16.5-KiB point.  It is a valid negative sensitivity observation, retained as
failed evidence rather than repaired, normalized, retried, or included in a
curve.

## Superseded next ordinary action

The original V2 dispatcher and parser remain the provenance path that produced
the above observations.  No further diagnostic replay is authorized or
needed for GESUMMV/16.5 KiB.  The original failures and their diagnostics
remain excluded from FAST64.4, FAST64.5, FAST64.6 aggregate curves and every
normalized performance claim.

## V2 diagnostic acquisition record (2026-09-11)

After the V3 admission audit passed two additional workers (no sampled swap
activity, memory PSI, OOM or CFS throttling; 83.9 GiB projected
`MemAvailable` after admission), the committed V2 dispatcher was dry-run
verified and launched exactly once per mode in fresh namespaces:

| mode | CPU | UUID | namespace | status |
| --- | ---: | --- | --- | --- |
| IO | 0 | `5a6b4eeb-1563-49f5-8af0-a20ded38fc3c` | `fast64_6_gesummv_physical16p5_io_coref283_diag_v2` | terminal; `NONFORMAL_DIAGNOSTIC_NOT_RESULT` |
| OO | 7 | `ac6c1a27-7980-4cdc-85c1-64974a536b76` | `fast64_6_gesummv_physical16p5_oo_coref283_diag_v2` | terminal; `NONFORMAL_DIAGNOSTIC_NOT_RESULT` |

Each namespace has an atomic START receipt binding observational Core
`f2836ea1...`, binary `361aada1...`, immutable runner `bf9a84c8...`, A1,
scientific Framework `037f008b...`, the literal original GESUMMV payload and
its respective frozen physical-16.5-KiB config.  These are diagnostic only:
their terminal analyzer output may classify source state but cannot relabel
the preserved formal failures or create a FAST64 result.

The future-only V2 collector
`util/dtc_l1/collect_fast64_6_gesummv_physical16p5_diagnostic_v2.sh` accepted
only exit `1` plus the mode-matching source marker, then atomically
materialized the two separate `NONFORMAL_DIAGNOSTIC_NOT_RESULT` JSON files. It
cannot create a primary or sensitivity-pass record.

Source/consumer compatibility is verified before terminal collection: the
observational Core f283 prints the IO fields at `shader.cc:2256` and the OO
fields at `shader.cc:2283`, matching the analyzer's mode-specific regular
expressions exactly.  A synthetic record for each source format passed the
analyzer and preserved IO `partial_lines_held` and OO `active_refs` separately.
