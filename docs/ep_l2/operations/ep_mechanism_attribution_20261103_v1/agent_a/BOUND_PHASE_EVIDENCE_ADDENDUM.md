# Bounded accepted-ON phase evidence addendum

Status: **PASS actual production PHASE extraction; requester-class and query-phase attribution remain PARTIAL**.

This addendum supplements the original T funnel delivery without changing its report, JSON, CSV or original manifest. Main authorized only a bounded read of the three exact, already accepted ON raws. The initially proposed64MiB read limit was raised explicitly to72MiB after validation preflight showed exact logical bytes70235553 (66.98MiB). There is no new Source, ELF, mode, run or scientific budget.

## What was read and verified

Existing validation bundles contained only the diagnostic record census, not PHASE counters; their cache directories were empty. Therefore each exact accepted ON `raw.log.gz` was read once in a forward stream. The stream computed both compressed and logical SHA and bytes and matched all four against the accepted validation bundle. Actual aggregate: **70235553 logical bytes,12445290 compressed bytes**, three raw passes total,1.44seconds. The72MiB hard cap was enforced. No Trace, active Stencil raw or unrelated raw was read.

The reducer retains the actual final PHASE records by slice, phase and final-cycle stamp. Intermediate snapshot cycles are recorded separately. Every original PHASE counter, not merely detach, was checked to sum to its final SLICE counter and existing compact final GLOBAL counter. Final phase catalogs identify phase0=UNASSIGNED, phase1=OVERLAP_UNKNOWN, phase2=kernelUID1, phase3=kernelUID2. Existing kernel-name/launch-UID log pairs map UID1 to `_Z21convolutionRowsKernelPfS_iii` and UID2 to `_Z24convolutionColumnsKernelPfS_iii`. Global final stamps are362791/367152/364463. The parser found704 PHASE,192 SLICE,3 GLOBAL and64 SAMPLE records per raw; SOURCE records are absent.

The summaries bind exact accepted-point, frozen-spec, validation, NI and Source5 identities. They expose their full raw SHA and selected final slice/phase counters plus all-counter phase totals for independent review. See `BOUNDED_PHASE_READ_RECEIPT.json`, the three `*_ACCEPTED_FINAL_PHASE.json` files and `extract_bounded_phase.py`.

## Actual backend events by active kernel interval

| Arm | Rows actual backend TagFAIL / detach | Rows trigger accepted / denied | Rows old detached retired | Columns actual backend TagFAIL / detach |
|---|---:|---:|---:|---:|
| A F-minus-T | 0 / 0 | 0 / 0 | 0 | 0 / 0 |
| B Legacy-F | 237 / 237 | 237 / 0 | 237 | 0 / 0 |
| C Corrected-F | 360 / 360 | 353 / 7 | 360 | 0 / 0 |

All these backend events and detached-old-transaction retirements occur in actual production **phase2 Rows**. Phase0/unassigned and phase1/overlap contributions are zero. This is a direct production PHASE measurement, not an allocation inferred from frontend virtual-MISS totals matching backend GLOBAL totals.

Columns still has174918/174399/173721 raw-full frontend head-cycle observations in A/B/C; its RO admits and merges are zero. The prior C-vs-B cycle localization of Rows+654, Columns-3308 and residual-35 must therefore not be described as detach events directly occurring in Columns. The actual backend detach count there is zero. Effects of preceding Rows state, queue/cache changes, altered request timing, common M operations or T checks are not causally separated by these interval totals. Zero detach does not prove zero indirect T effect or zero policy-check cost.

Production `PHASE` means the currently single-active-kernel interval at the event notification (`ledger::phase` in ep-l2-detach-diag.h:248-252, print_counts:290-298). It is not a recorded old-RO owner-kernel identity. The backend PHASE counters do **not** split detach by RO versus ordinary requester. They do not assign the63 ordinary frontend virtual-MISS observations to63 backend detach events. Backend requester class remains **NOT_INSTRUMENTED**.

The P1 paid-query records remain only cumulative per-slice values, exactly2954 issued/2954 wait exposures in C, zero ordinary port-wait attempts; they have no phase key. Query issue/wait exposure by Rows/Columns remains **NOT_INSTRUMENTED**. No sum or residual difference is used to fill this gap.

## Capacity consultation is not the paid query

The actual counter name is `eligible_capacity_consulted`, paired with `eligible_capacity_not_consulted` (there is no `pressure_eligible_capacity_consulted` wire field). The producer has two separate flags:

- `o.capacity_consulted`: set only when the RO preview calls `capacity(m,existing,o)`, ep-l2-ro-runtime.inc:243-258 and319. It records actual descriptor/per-address/ordinary-LineMSHR capacity predicate evaluation. It is not a metadata-query ticket.
- `o.consulted`: set when the RO or corrected ordinary path actually consults set-relief eligibility; ordinary producer is gpu-cache.cc:2829-2834. A paid ordinary query can complete and set `o.consulted` without setting `o.capacity_consulted`.

For raw-full+structural-eligible observations, gpu-cache.cc:3154 records which `capacity_consulted` branch occurred. Therefore C's split is:

| Counter population | Head-cycles |
|---|---:|
| `eligible_capacity_consulted` -- RO virtual-MISS | 297 |
| `eligible_capacity_not_consulted` -- RO paid-query early reject | 301 |
| `eligible_capacity_not_consulted` -- ordinary query wait | 63 |
| `eligible_capacity_not_consulted` -- ordinary query complete, virtual-MISS allow | 63 |
| Total eligible | 724 |

Thus **427 not-consulted includes63 successfully queried ordinary virtual-MISS observations**. Calling427 'unqueried requests' is false. The360 consulted virtual-MISS observations comprise297 RO plus63 ordinary and use the other flag. All these are same-arm actual joint head-cycle counts, not distinct UID populations or exclusive GPU-stall cycles. The field split is identical in final phase2 because all724 operational eligible exposures occur there; this does not change the field definition.

## Boundary retained

Existing aggregate count closure and compact NI remain PASS. Seven triggering requests denied immediately after detach are not seven lost requests; their later UID-linked acceptance/completion and exact joint rejection gate remain NOT_MEASURED/NOT_INSTRUMENTED. Numerical application output and physical PPA closure remain UNKNOWN. No new instrumentation or CPU test was needed or performed for this addendum.
