# AWMA R20R3 active-world solver Native, node109

Outcome: `R20R3_ACTIVE_WORLD_DIAGNOSTIC_NOT_QUALIFIED` at the *stage-selection* gate. This is a profiler-evidence stop, not an active-world performance negative. Four exact discovery entries passed OFF/B0 regression. The one permitted NSYS workload completed and its four solver results also passed, but NSYS produced no report/SQLite/qdstrm. The pre-timing `ELIGIBLE_STAGE_AUDIT.md` explicitly forbids selecting a substage by guess when cumulative per-stage GPU time cannot be recovered. Therefore no stage was selected, no S1 was implemented, no candidate correctness or formal timing was run, and holdout remained sealed.

The exact input/source/contract bindings are in `PARENT_AUTHORITY.json` and `REVISED_NUMERICAL_CONTRACT.md`; per-entry OFF results are in `OFF_BASELINE_REGRESSION.tsv`. `B0_PROFILE_SUMMARY.tsv` and `PROFILE_FAILURE_AUDIT.md` document the missing profiler result without fabricating kernel time. All downstream files are marked `NOT_RUN`. `RUN_RECEIPTS.json`, `RAW_DATA_INDEX.tsv`, and `SHA256SUMS` close provenance. Raw outputs and logs are on node164, not Git.

No Accel-Sim, NCU, NVBit, SASS, node174 compute, second scene/batch, candidate, whole-trajectory timing, hardware design or performance claim was performed. Every CUDA/JIT/capture/replay/NSYS operation held `/data/c16/locks/c16_gpu_campaign.lock`.
