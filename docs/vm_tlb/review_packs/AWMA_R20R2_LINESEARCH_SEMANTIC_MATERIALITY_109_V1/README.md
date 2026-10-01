# AWMA R20R2 line-search semantic materiality, node109

Scientific outcome: `R20R2_LINESEARCH_DIAGNOSTIC_THRESHOLD_ONLY` for the single frozen t152/world413 solver entry. See `FINAL_DECISION.md` and `WORLD413_LINESEARCH_TRACE_SUMMARY.md` for the precise boundary. This is a correctness/semantics diagnostic, **not** active-world performance evidence.

Authority is frozen in `PARENT_AUTHORITY.json`. `SOURCE_SEMANTICS.md` was written before the new GPU campaign. The opt-in observer is specified in `OBSERVER_CONTRACT.md`; `OBSERVER_SOURCE_DIFF.patch` is a diff from the exact pinned source to the isolated ON overlay, while OFF imports the unmodified pinned source. The runner and CPU analyzer live under `util/vm_tlb/awma/r20r2_linesearch/`.

`OBSERVER_OFF_REGRESSION.json` records five passing OFF repeats. `T152_REPEAT_SUMMARY.tsv` lists all five OFF and 31 ON same-graph repeats. `WORLD413_LINESEARCH_TRACES.json` retains the chronological first clear/set pair; all per-run complete outputs and traces are in the node164 raw directory indexed by `RAW_DATA_INDEX.tsv`. `SCRATCH_AUDIT.md` documents the bounded source-level graph-local scratch audit. `FUTURE_ACTIVE_WORLD_NUMERICAL_CONTRACT_PROPOSAL.md` is review-only and does not authorize S1.

One early OFF engineering precheck incorrectly imposed a candidate-only residual ceiling on an additional B0 repeat. Its raw is preserved as `OFF_PRE_GATE_FIX_*`. The parent B0-only validator does not gate new B0 repeats on that ceiling; the mistake was corrected before the successful OFF regression and before any ON run. It did not alter the source, input, frozen candidate contract or scientific classification.

Forbidden-path receipts: S1=0, formal timing=0, NSYS=0, NCU=0, NVBit=0, Accel-Sim=0, node174 compute=0. All CUDA initialization, JIT, captures and replays used `/data/c16/locks/c16_gpu_campaign.lock`; node174 serves only as the existing node164 storage gateway.
