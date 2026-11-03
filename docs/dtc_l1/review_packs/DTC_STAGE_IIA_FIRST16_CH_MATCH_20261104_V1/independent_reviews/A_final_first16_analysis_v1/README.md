# Final first16 report generator — preparation only

No final report has been generated. Source code and22 CPU checks are complete while the recorded validation input has14 accepted CH points, common n6/8 and Root science_execution_complete=false. These as-of preparation counters are not future final acceptance evidence.

## Root invokes only after all16 terminal closure

```sh
/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/agents/A_figures_v1/plot-venv/bin/python /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/agents/A_final_first16_analysis_v1/generate_final_first16.py --provider /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/agents/B_runtime_analysis_v1/PUBLICATION_PROVIDER.json --root-audit-latest /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1/root_completion_audit_v1/LATEST.json
```

The existing plotting venv provides Matplotlib3.10.8. The generator installs nothing. It copies and calls the unchanged9d996a27 plotting source only after terminal gates; figures, cache and all outputs remain inside this new final-analysis directory. `--no-figures` is optional and has a distinct output snapshot suffix; it does not relax scientific gates. No simulation, registration, model/controller/owner operation, archive writer or Git code is imported.

## Mandatory fail-closed gates

1. Root latest pointer must say science_execution_complete=true; its SHA-pinned AUDIT.json must have the exact Root audit schema and independently say science_execution_complete=true. Goal_complete need not yet be true: this report is one deliverable for later scientific review/publication.
2. B publication provider and its referenced SUMMARY must both say all_registered16_terminal_verified=true; all16 identities consumed, remaining0, verification_hold0, await_result0, accepted+archivednegative16. Every row must be an accepted quadruple or an explicit terminal negative. The compressed RESULTS/SUMMARY bytes must match both provider and B snapshot manifest.
3. Fixed5001 plan, frozen8 program/input order,16 cells, metric/cycle relations and source populations must verify. Cost disclosure8ba5c279, HtoD semanticsf3ff9719 and plotting9d996a27 source SHA must still match. No source drift is silently accepted.

All gates and source checks run before creating outputs or a final marker. A false gate returns HOLD_NO_FINAL_OUTPUT/exit2; malformed evidence raises validation failure. Do not edit authority flags to force a report.

## Final products after Root invocation

Each immutable output snapshot is keyed by Bprovider SHA, Rootaudit SHA and generator SHA. An existing complete snapshot is SHA-verified and reused; partial/colliding folders are preserved as an error. The owned LATEST_FINAL_REPORT.json points to the exact manifest.

- FINAL_FIRST16_REPORT.md: fixed8 programs' six cycles;16 per-input/F S_CH,S_DH,R,I rows; same-common-population GM and sign/missing counts; suite groups; directF128/F256 comparison and explicit boundaries.
- STATISTICS.json: all rows, exact integer rational numerator/denominator, positives/negatives/exactzero/missing, available per-F populations, common populations, suite expected denominators3/5 and same-set directF comparisons. Missing remains null. Exactzero is rational equality to1, not floatepsilon. Main GM and cross-F comparison use a common set, never two differing available denominators.
- FULL_SHA_REFERENCES.json: all8 full input digests, binding/commandlist/member SHA contracts,32 distinct old reference paths/SHA and16 new reference paths/SHA. New terminalnegative paths may be hashed for provenance only when B exposes no accepted-performance source; their cycles never enter performance.
- PROVENANCE.json and provenance/: exact Bprovider/gzip sources, Rootaudit, generator, contract, unchanged plotter and HtoD interpretation note.
- figures/: CH/DH P0-normalized three-profile panels and I plot from the unchanged9d consumer. Titles remain first8 subset. GM uses B's common set and negative/zero/missing cases remain.

## Scientific boundaries carried forward

First8 is not core32/full35. FR-FCFS64/128/256 couples sharedcredits255/319/447;10MiB L2,192x4 MSHR,missQ32 and850MHz remain fixed. CH PAPER_BASE commonPIB256 and Tag scheduling are active; DH PAPER_OO uses PIB128; raw commonPIB8/dtcMSHR32 are not active OO capacities. Declared geometry, active paths and physical area are distinct; no iso-area/frequency/energy result.

The fixed HtoD model directly updates L2 tags under perf_sim_memcpy1/flush_l2_cache0, rather than ordinary timed DRAM transfer. This does not certify all copied data resident (64MiB2DCONV exceeds10MiB L2), captureELF/numeric-state identity or native-application numeric correctness. Counter scopes and correlated traffic/stalls do not isolate L2-to-DRAM queue delay or establish a complete causal bottleneck. No best-per-program GM, IR/R2/EP/PQ/PS substitution, unfinished-cycle estimate, manuscript edit or remaining48 batch design/release occurs here.

## Preparation validation strategy

CPU_VALIDATION.json records22 assertions: actual current Bschema/ratios/commonGMs, fixed8/16/suite populations, original32ref count, null missing values, frozen cost/semantic/plot SHA, exact arithmetic beyond float rounding, both-design regressions with relative tie, false Rootpointer/AUDIT gates, Bterminal/remaining/hold gates and terminalnegative allowance. CLI rejection is exercised with an explicitly false CPU-only Root fixture; no fabricated final report or performance row is published. The actual Root audit was observedfalse during qualification. `validate_preparation.py` is an as-of preparation check and intentionally requires no final outputs; it is not a daemon or a post-completion final-report command.
