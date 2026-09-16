# Formal admission, ACK, NCU and fingerprint

Formal admission concurrency was one. The frozen formal run is `C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v18r2-k-repeat_20260916T040000Z_ee18ee18ee18`.

The producer local closure, receiver verification, receiver admission, catalog entry binding and transfer ACK are copied in `formal/`. The ACK is PASS and binds source manifest SHA `3a189ae86864e723a7fc0b8fd739db8c3fe3befa33800ee2c444e799f0ad75b8`, catalog entry SHA `a043d78b0069f1acd24d5fdc2fc75ccac32b1e1aa3fa1da55a137e26f24b19ad`, 483 files and 2,543,962 bytes.

The bounded application-replay NCU report and log are preserved in `evidence/`; metric units remain native NCU report units. The target direct-copy signature is observed at grid `(16392,1,1)`, block `(128,1,1)` and its compact artifact fingerprint is the immutable manifest/artifact inventory plus per-shard records and address-context receipts. This pack intentionally does not infer temporal ordering or cache-reuse distance from the capture.
