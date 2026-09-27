# Accepted history and V1R2 scope

- V1 `R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1` remains valid for the local causal-conv1d/FLA package path.
- V1R1 `R54_V1R1_HUB_KERNEL_SEMANTICS_NOT_QUALIFIED` remains valid for exact top1/top2 ordering across fallback and Hub.
- V1R2 separately froze temperature=0 greedy continuation as the application contract before running S0, S1, S2.
- Checkpoint/restore correctness uses the uninterrupted Hub backend as its reference. It does not require unselected fallback logits to match Hub logits.
