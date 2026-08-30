# Codex → ChatGPT latest report

Stage: Final Target Baseline — Interim 22/26

Status: **INTERIM_FORMAL_22_OF_26**

Core SHA: `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`
Framework SHA: `f08d2ce857972fad73c4e1ab7162ba94c6336507`

Completed: 22 / 26

Missing: gemm Legacy/Banked; 3mm Legacy/Banked

22-run provenance audit: **PASS** (all completed runs are `VALID_FOR_FORMAL`)

C7e telemetry observed on natural formal runs: **PASS**

Main interim findings:

- The shared descriptor pool reaches 256 with pool-full events in six completed workloads while line-MSHR-full remains zero.
- `cfd_097k` is the only completed Banked workload with measured nonzero C6d true conflict and wait.
- Scan/vectorAdd/convolution/FWT_7 show request-side lower pressure; ReturnQ and DRAM-to-L2 path are measured zero in the completed subset.

Issues requiring action before 26/26:

- None identified in the completed-run provenance, terminal invariants, parser outputs, or C7e completeness audit.
- This is not final: do not publish `TARGET_BASELINE_26RUN_PASS`, `READY_FOR_OPPORTUNITY`, or final aggregates until the four live runs complete and final aggregation passes.

Running jobs healthy: **YES**

Review entry point: [TARGET_BASELINE_FINAL_INTERIM_22OF26_r1](../review_packs/TARGET_BASELINE_FINAL_INTERIM_22OF26_r1/README.md)
