# C16 Lane G transfer plan

1. A publishes a fixed-commit C16 GPU package manifest with Wave-1 asset/input/scenario hashes.
2. G copies only that fixed package and this G source bundle with `rsync -avP --partial` to the recorded AutoDL work root.
3. G runs `bootstrap_autodl.sh --install --wheelhouse ...`; the script refuses an empty or hash-mismatched wheelhouse manifest.
4. G records an instance receipt, then compares every used asset/input/wheel SHA256 to `EXPECTED_HASHES.tsv` before G0.
5. G creates one shared execution-budget ledger in the AutoDL work root. Every real runner/profiler command receives that ledger; NVBit obtains an exclusive bounded lease before launch.
6. Profiler databases and raw NVBit output remain outside Git. Each bounded capture is returned through an exchange path and represented by path/host/size/SHA256/run/target/terminal status in `RAW_INDEX.tsv`.

This package is deliberately incomplete until A's committed asset/input/scenario package is available. It is not permission to download models on rented GPU or to begin G0.
