# Qwen3-30B-A3B Wave-2 background-download policy

This policy covers only `Qwen/Qwen3-30B-A3B` at immutable model and tokenizer
revision `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.  Its frozen
`MODEL_ASSET_MANIFEST.tsv` has 16 safetensors files totaling
`61,066,575,648` bytes.  It is a Wave-2 asset and is never an input to the
RTX3090 Wave-1 rolling packages P0/P1 or a request to attempt CPU offload.

The launch check at `2026-09-12T14:51:10Z` observed `95,164,334,080` bytes
available, greater than the user-authorized `85 GiB` (`91,268,055,040` bytes)
threshold.  A single serial background worker therefore started after that
check.  The lower `15 GiB` (`16,106,127,360` bytes) pause guard remains in
force: it pauses the Wave-2 worker without deleting or altering an accepted
file and leaves Wave-1 transfer workers untouched.

The worker uses pinned revision URLs, HTTP/1.1 `curl --continue-at -`, and a
1 MiB/s background cap to preserve Wave-1 priority.  A shard is first written
as `*.incomplete`; that suffix is never recorded as a checkpoint or a package
asset.  Only a file with both the manifest's exact byte count and remote-LFS
SHA-256 is atomically promoted to its final path.  Already promoted shards are
re-hashed and skipped, not redownloaded.  The live local progress receipt is
`/workspace/c16_assets/c16-a/download_logs/C16_QWEN3_30B_A3B_PROGRESS.json`;
it is not a cross-lane input.  After all 16 independent validations, A will
publish a separate immutable Wave-2 asset/package receipt.

No GPU, CUDA model execution, profiler, NVBit, simulator, SASS, or full-ROI
action is performed by this policy or its worker.
