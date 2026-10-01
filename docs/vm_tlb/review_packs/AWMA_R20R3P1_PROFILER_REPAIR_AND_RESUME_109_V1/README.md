# AWMA R20R3P1 profiler repair and bounded resume, node109

Outcome: the installed NSYS path was repaired and produced attributable stage timing, but the one selected active-world candidate did not clear the frozen t128 final-gradient residual correctness gate. Formal discovery timing and holdout were **not run**. See `FINAL_DECISION.md` and `CANDIDATE_FAILURE_AUDIT.md`; this is not an active-world performance negative.

The exact parent R20R3 source-eligible audit and stage-ranking rule were retained. `NSYS_TOOLCHAIN_RECEIPT.md` and `NSYS_CANARY_RECEIPT.json` document the bounded engineering admission. `REPAIRED_PROFILE_RECEIPT.json`, `REPAIRED_B0_PROFILE_SUMMARY.tsv` and `SELECTED_STAGE.md` bind the sole scientific B0 profile and deterministic stage selection. `DIAGNOSTIC_CONTRACT.md` freezes the single candidate before timing; `CANDIDATE_SOURCE_DIFF.patch` is the opt-in/default-OFF source change. `CANDIDATE_CORRECTNESS.tsv` records the t128 stop and explicit NOT_RUN entries.

Large NSYS report/SQLite, full per-kernel manifest, complete solver outputs, source overlay and all raw receipts are on node164, indexed by `RAW_DATA_INDEX.tsv` and SHA manifests. No NCU, NVBit, SASS, Accel-Sim, node174 compute, whole-trajectory timing, policy training or hardware design occurred. All CUDA/JIT/capture/replay/profile work held `/data/c16/locks/c16_gpu_campaign.lock`.
