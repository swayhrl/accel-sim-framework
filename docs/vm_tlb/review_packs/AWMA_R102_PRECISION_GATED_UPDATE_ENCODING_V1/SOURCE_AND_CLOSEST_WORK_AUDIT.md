# Source and closest-work audit

## Pinned authority

- Repository: `scitix/helix`
- Commit: `867f76a82822dd87413da4fec617b7f8e7cf6414`
- Tree: `f42dd4dbd47eeabca668f7299d2ec813a53994db`
- Source audit: `PASS_SOURCE_AUTHORITY_ONLY`
- Thirteen required source/input-format files are blob- and SHA256-bound in `R102_SOURCE_RECEIPT.json`.

## Verified source path

`VERIFIED_CODE`:

1. `SparseUpdater.before_copy` retains `shard_model_weight.detach().clone()` as the previous working-precision weight.
2. `get_sparse_diff_indices` compares flattened `curr != prev`, runs `nonzero`, flattens, converts to int32, and applies the parameter offset. For a 1-D mask, PyTorch `nonzero` emits lexicographically ascending indices.
3. `get_sparse_diff` and the observer's optional-value path use `index_select` to gather changed values.
4. The operational updater attaches indices; Slime materializes current values into a NaN-sentinel tensor, and `dense_nan_to_sparse_tensor` uses `where(~isnan)` plus value gather before the per-dtype bucket copies int32 indices and exact values into aligned merged buffers.
5. `compare.py` contains the explicit `TODO: Use triton to implement this.`

This closes software provenance, not performance or hardware causality. Because input authority failed, R102 did not reproduce E0 or implement E1.

## Dump-format boundary

Training writes `rank{rank}_indices_{interval}.pt`. The mandatory field is `model_weight_indices`. `SPARSE_SAVE_VALUES=1` optionally saves changed previous/current values, but defaults to `0`; neither mode saves the complete previous and current tensor pair. The offline reader normalizes indices and optional analysis dictionaries and cannot reconstruct full tensors without an independently bound base state.

## Closest work and paper boundary

The SparseRL-Sync paper states that its experiments captured BF16 snapshots immediately before and after weight-update events and reports aggregate sparsity and bit-exact reconstruction. The public pointer is the Helix repository. At the pinned/default commit the repository has no tracked tensor/checkpoint files, no tags, and no GitHub releases/assets; its README only documents `SPARSE_STATS_SAVED_DIR` as a user-selected output path. No dataset/dump download is documented.

The paper/source already own exact precision-gated sparse synchronization, values/indices bucketing, and lossless reconstruction. R102 makes no architecture or novelty claim.
