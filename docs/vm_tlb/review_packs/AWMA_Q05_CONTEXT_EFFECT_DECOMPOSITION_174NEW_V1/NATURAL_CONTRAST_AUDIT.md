# Existing-run natural contrast audit

`EXISTING_RUN_CONTEXT_COUNTER_MATRIX.tsv` mines only source-defined cumulative counters at the accepted Q05 boundary. `NATURAL_CONTRAST_COUNTER_DIFFS.tsv` records all selected differences.

P2→P4 holds walks/PWC/PTE constant (128/3/131) while cycles increase 24,058. L2 accesses/misses increase by 1,332/2,008, L2 reservation failures increase 747, packet totals increase 1,332, and DRAM command/request counters differ. P8→P16 improves L2-TLB misses (292→241), requester latency and L2-data misses, while cycles worsen 27,478. P16→P34 reduces walks by one while cycles worsen 9,212 and L2 data misses rise 8,675.

Conclusion: `NON_TRANSLATION_CONTEXT_EFFECT_PRESENT`. The data do not identify one uniquely causal L2/DRAM mechanism, so none is claimed.
