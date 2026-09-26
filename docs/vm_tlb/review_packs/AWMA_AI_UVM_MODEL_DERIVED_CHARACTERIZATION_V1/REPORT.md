# AWMA AI UVM model-derived characterization V1

Final decision: `MODEL_DERIVED_UVM_NO_DISTINCT_PROBLEM`.

This review replaces synthetic laws with exact local model metadata, exact Llama KV accounting, and an actual frozen OLMoE route sequence. It finds a real KV migration cliff just above VRAM, but closest-work screening shows no distinct problem beyond existing UVM/offloading work. The OLMoE model is naturally resident, and the bounded PyTorch managed-tensor bridge is not ready.

Durable raw authority: `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/uvm_model_derived_characterization_20260926`.

Review order: `FINAL_DECISION.md`, `MODEL_DERIVED_RESULT_SUMMARY.tsv`, `REAL_ROUTING_BEHAVIOR.tsv`, `SYNTHETIC_VS_MODEL_DERIVED.md`, `CLOSEST_WORK_SCREEN.md`, then `VALIDATION_SUMMARY.md` and `OPEN_ISSUES.md`. Source/base provenance and the path-scoped diff summary are in `SOURCE_ANCHORS.md`; raw identities are in `RAW_DATA_INDEX.tsv`. `COMPACT_NORMALIZATION.md` explains the Git-copy LF normalization and compact `SHA256SUMS`.

See `FINAL_DECISION.md` for evidence and inference limits.
