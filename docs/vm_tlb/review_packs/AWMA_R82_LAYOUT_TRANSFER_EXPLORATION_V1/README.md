# AWMA R82 native layout-transfer exploration V1

Final state: `R82_CURRENT_SOFTWARE_SUFFICIENT_IN_SCOPE`.

Start with `DECISION.md`, then `SOURCE_CAPABILITY_MAP.md`, `IR_NATIVE_BINDINGS.md`, `TIMING_RESULTS.tsv`, and `CONVERSION_LEDGER.tsv`.

The qualified P1 fixed-split-256 real target retains one nontrivial conversion in each kernel under Triton 3.8.0. The only frozen joint-layout candidate is bitwise exact but does not eliminate either conversion and is 0.239% slower by paired median, below run CV. The FLA GDN path has real native transfers but remains audit-only because its inherited Hub full-model semantic gate failed and exact binary-to-call attribution is unresolved.

No holdout or NCU was triggered. No architecture mechanism, FIBER reconstruction, node174 simulation, Accel-Sim run, full NVBit capture, or model download occurred. Durable authority: `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/round08_20260927/R82/`.
