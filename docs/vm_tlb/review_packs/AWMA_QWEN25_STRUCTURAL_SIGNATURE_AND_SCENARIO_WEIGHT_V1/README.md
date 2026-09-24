# Qwen2.5 structural signature and scenario weight V1

This review pack separates structural recurrence observed in the frozen S2 run
from performance weights specific to that run. Start with the stage report,
then inspect:

1. `QWEN25_STRUCTURAL_AND_WEIGHTED_KERNEL_CATALOG_V1.tsv` — selector-facing
   unified table, including asset status and the nine unmapped Native-only rows.
2. `STRUCTURAL_SIGNATURE_SUMMARY_V1.tsv` — pass/step recurrence and stability.
3. `SCENARIO_SPECIFIC_WEIGHT_SUMMARY_V1.tsv` — phase/family/stratum time mass.
4. `CROSS_CONTEXT_VALIDATION_PLAN.md` — no-execution future validation design.
5. `RUN_RECEIPT_V1.json` and checksums — authority and closure.

No GPU capture or Accel-Sim replay was started. A matching kernel-family name
does not establish semantic/operator identity or cross-context invariance.
