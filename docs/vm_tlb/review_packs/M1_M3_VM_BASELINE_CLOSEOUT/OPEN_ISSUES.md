# Known limitations and intentional exclusions

- One translation page size per run; no mixed-page placement/promotion policy.
- Generic identity-like mapping only; no allocation metadata, fault, migration,
  UVM or MCM.
- PWC organization, radix split and lookup timing are reusable generic choices,
  not target-paper claims.
- No Segmentation L2-TLB sub-entry/coalescing, synthetic KV, LLM segmentation,
  multi-ASID study or AI-aware TLB mechanism.
- The local trace corpus contains LUD and BFS only.

These are scope boundaries, not correctness blockers for M1-M3.
