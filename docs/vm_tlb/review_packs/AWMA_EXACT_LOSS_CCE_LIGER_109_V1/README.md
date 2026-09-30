# AWMA_EXACT_LOSS_CCE_LIGER_109_V1

Decision: EXACT_LOSS_STATE_LIFETIME_RESIDUAL_PRESENT.

Read HEADROOM_ANALYSIS.md first, then the numerical, timing, memory, saved-state,
and profile tables. This compact pack records one real Qwen2.5-0.5B-Instruct
next-token loss shape on node109 RTX4080/SM89.

All formal CUDA work held the shared lock. There was one NSYS capture and zero NCU
captures. This is a local quick-falsification boundary, not hardware design or
end-to-end training evidence.
