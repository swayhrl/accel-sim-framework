# Lane F / node109 — VLA RTC inference-time VJP boundary

Stage `AWMA_VLA_RTC_VJP_BOUNDARY_109_V1`, execution branch `hrl/awma-vla-rtc-vjp-boundary-109-v1`, starting HEAD `6586b2530c38ccd3e7aa620e14990f0c1274bbef`.

Decision: **`VLA_VJP_RESULT_MIXED_NEEDS_REVIEW`**. The repaired full-network VJP and real LIBERO input qualified; complete-chunk A0/A1 timing and strict trajectory comparison closed. The particular strong software reuse arm gave no material improvement, but the VJP internal state-only residual could not be isolated or bounded above 5%. Validation B remained sealed. See `FINAL_DECISION.md` for raw facts and limitations.

Authority map: `SOURCE_IDENTITY.json`, `REFERENCE_REPAIR.md`, `VJP_SEMANTIC_CANARY.tsv`, `INPUT_RECEIPT.json`, `TARGET_WINDOWS.tsv`, `A0_TIMING.tsv`, `HEADROOM_ANALYSIS.md`, `A1_DESIGN.md`, `A1_IMPLEMENTATION_RECEIPT.md`, `A1_TIMING.tsv`, `PAIRED_TIMING_ANALYSIS.json`, `PROFILE_SUMMARY.tsv`, `RUN_RECEIPTS.json`, `RAW_DATA_INDEX.tsv`, `SHA256SUMS`. Large model/data/raw artifacts reside at the node164 path in the raw index. Runtime caches and the isolated environment stay on node109; all actual CUDA/profiler jobs held the shared campaign GPU lock and terminated.
