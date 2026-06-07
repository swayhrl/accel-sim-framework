# A22C LATPC shadow VM foundation report guidance

## Goal

Synthesize A20-A22 results into a clear foundation readiness report.

A22C decides whether future LATPC mechanism rounds can build on the shadow VM substrate.

## Required script

Create:

scripts/accelsim/a22c_latpc_shadow_vm_foundation_report.py

## Inputs

A20A/A20B/A20C reports.
A21A/A21B/A21C reports.
A22A/A22B reports and CSVs.

## Readiness classification

Assign one:

SHADOW_VM_READY_FOR_REGULARITY_DETECTOR:

- address/VPN stats are present
- page divergence stats non-trivial
- stride and same-L4 stats available or easy to derive
- behavior equivalence passed

SHADOW_VM_READY_FOR_LATC_LATP_STATS:

- above plus TLB/MSHR/PTW shadow stats are present and non-trivial
- MSHR and PTW counters are consistent enough for LATC/LATP shadow mechanisms

PARTIAL_SHADOW_VM_ADDRESS_ONLY:

- address/VPN/page divergence stats work
- TLB/MSHR/PTW shadow stats missing or too approximate

DESIGN_ONLY_BLOCKED:

- no source implementation or no useful stats

FAIL_NOT_READY:

- behavior changed or stats inconsistent

## Required report sections

1. Starting point from A19.
2. Source implementation summary.
3. Hook exactness.
4. Behavior validation result.
5. Stats implemented.
6. Stats approximated.
7. Stats unavailable or deferred.
8. Sanity and sensitivity results.
9. Readiness classification.
10. What A24 can safely do.
11. What A24 must not do.
12. Limitations.

## Readiness matrix CSV columns

- component
- readiness
- evidence_path
- evidence_stat
- confidence
- future_round
- notes

Components:

- address_observation
- vpn_derivation
- page_divergence
- stride_stats
- same_l4pt_locality
- shadow_l1_tlb
- shadow_l2_tlb
- shadow_l1_mshr
- shadow_ptw_queue
- shadow_pwc
- runner
- stats_parser
- behavior_equivalence

## Required outputs

.local_reports/A22C_latpc_shadow_vm_foundation_report_<timestamp>.md
.local_reports/A22C_latpc_shadow_vm_readiness_matrix_<timestamp>.csv

## Status rules

PASS:
Classification is SHADOW_VM_READY_FOR_REGULARITY_DETECTOR or SHADOW_VM_READY_FOR_LATC_LATP_STATS.

PASS_WITH_WARNINGS:
Classification is PARTIAL_SHADOW_VM_ADDRESS_ONLY.

PASS_DESIGN_ONLY:
Classification is DESIGN_ONLY_BLOCKED.

FAIL_NOT_READY:
Behavior changed or stats inconsistent.
