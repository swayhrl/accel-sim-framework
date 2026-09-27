# Input authority audit

## Qualification criterion

Scientific GPU work required at least one exact pair:

- `PREV_LOW_PRECISION_WEIGHT`
- `CURR_LOW_PRECISION_WEIGHT`

or a source training dump that deterministically reconstructs both with tensor identity, dtype, shape, step/update identity, and provenance. Statistics, plots, NNZ counts, indices alone, and unrelated checkpoints do not qualify.

## A. Existing project assets

Searches were path/metadata-only; no tensor was loaded and no whole-storage hash was performed.

- Node109 C16/AWMA: no Helix/SparseRL stats directory, `rank*_indices_*.pt`, before/after weight snapshot, or update tensor was found. Existing static model caches each bind pretrained/inference assets, not a training transition.
- Node164: candidate path-name search and small metadata-content search returned no Helix/SparseRL dump or before/after update asset. Its model archive contains single static revisions. Qwen2.5 raw versus AWQ are different representations/artifacts, not consecutive training updates.
- Irrelevant P1 `paired_indices.pt` files are selector outputs, not model-weight updates and were excluded.

Commands and complete compact outputs are preserved in `raw/NODE109_INPUT_PATH_AUDIT.txt` and `raw/NODE164_INPUT_PATH_AUDIT.txt` on node164.

## B. Pinned public artifact

- Helix HEAD/main equals the pinned commit.
- Tracked tree: code, patches, paper PDF, and two chart images; zero `.pt`, `.pth`, `.safetensors`, `.bin`, `.npy`, or `.npz` files.
- Tags: none.
- GitHub releases/assets: zero.
- README/source document where users may write their own stats but provide no external tensor dump location.
- Primary paper reports measurements from real snapshots but does not publish those snapshots or a reconstructible training dump.

## Missing artifact

The missing scientific payload is an identity-bound full before/after working-precision weight pair, or equivalently a bound base tensor plus exact update payload and metadata sufficient to reconstruct both. No such payload was found.

## Gate

`R102_INPUT_AUTHORITY_NOT_QUALIFIED_V1`.

No fallback data was synthesized. GPU execution is forbidden and was not performed.
