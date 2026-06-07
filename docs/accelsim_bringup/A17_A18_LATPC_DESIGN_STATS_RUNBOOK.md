# A17/A18 LATPC Design And Stats-Only Runbook

This runbook records the local A17/A18 pipeline used for LATPC paper-specific
design localization and stats-only instrumentation.

The pipeline is intentionally bounded:

- A17A captures paper-specific requirements and target `latpc_*` stats.
- A17B localizes relevant Accel-Sim source paths without changing source.
- A17C writes the minimum future mechanism design and A18 boundary.
- A17D gates whether A18B may touch simulator source.
- A18A classifies `latpc_*` fields as `IMPLEMENTED`, `DERIVED`,
  `APPROXIMATED`, `UNAVAILABLE`, or `DEFERRED`.
- A18B may add print-only `latpc_*` metadata stats when the gate permits.
- A18C rebuilds and runs the bounded selected-workload stats probe.
- A18D validates that stats-only instrumentation did not change behavior.
- A18E writes the final summary, checklist, diffstat, and review pack.

The round does not implement LATPC, LATC, LATP, TLB prefetching, TLB hit/miss
changes, MSHR behavior, page-walk scheduling, or paper speedup reproduction.

Run stages in order:

```bash
python3 scripts/accelsim/a17a_latpc_paper_requirements.py
python3 scripts/accelsim/a17b_latpc_code_localization.py
python3 scripts/accelsim/a17c_latpc_minimal_design.py
python3 scripts/accelsim/a17d_latpc_readiness_gate.py
python3 scripts/accelsim/a18a_latpc_stats_field_spec.py
python3 scripts/accelsim/a18b_latpc_stats_only_instrumentation.py
python3 scripts/accelsim/a18c_latpc_build_and_stats_probe.py
python3 scripts/accelsim/a18d_latpc_stats_only_validation.py
python3 scripts/accelsim/a18e_latpc_closeout_review_pack.py
```
