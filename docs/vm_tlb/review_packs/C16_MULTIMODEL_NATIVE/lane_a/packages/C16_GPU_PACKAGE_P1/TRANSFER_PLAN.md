# C16_GPU_PACKAGE_P1 transfer plan

This immutable rolling package is limited to `c16_qwen25_05b_native_reference`. It contains no `.incomplete`, `.curl.download`, remote-only, live-worktree, GPU, profiler, NVBit, simulator, SASS, or full-ROI artifact.

1. Materialize Git rows only from their exact commits in `EXPECTED_HASHES.tsv`; rsync local rows to their listed relative destination.
2. Recheck every size and SHA-256 in `EXPECTED_HASHES.tsv` before model import. A mismatch is quarantined and blocks import.
3. This P0/P1/P2/P3 plan is transfer/import preparation only. It does not itself launch a GPU workload or make a dynamic scientific claim.
