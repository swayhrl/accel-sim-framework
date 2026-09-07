# B9 deterministic matched 16+16 selector

**Evidence label: `SPECULATIVE_DIAGNOSTIC`**

The selector uses immutable kernel-list order plus `stat(2)` compressed-file
size only. It does not open, decompress, hash, or decode trace content. For
each phase it selects one unique nearest candidate for every common
`temporal_quartile x compressed_size_quartile` cell; ties use SHA-256 of the
filename then semantic index. The selector implementation is
`util/vm_tlb/select_b9_matched_kernels.py`.

The signature is a metadata matching signature, not a claim of matched memory
behavior. Any later E09/E10 output must state this limit and produce its own
traffic/reuse measurements.

| ROI | Rank | Semantic index | Kernel ID | Trace filename | Signature |
|---|---:|---:|---:|---|---|
| prefill | 1 | 70 | 807 | kernel-807-ctx_0x55f2413c4de0.traceg.xz | temporal_q0;compressed_size_q0 |
| prefill | 2 | 82 | 820 | kernel-820-ctx_0x55f2413c4de0.traceg.xz | temporal_q0;compressed_size_q1 |
| prefill | 3 | 106 | 845 | kernel-845-ctx_0x55f2413c4de0.traceg.xz | temporal_q0;compressed_size_q2 |
| prefill | 4 | 79 | 816 | kernel-816-ctx_0x55f2413c4de0.traceg.xz | temporal_q0;compressed_size_q3 |
| prefill | 5 | 240 | 985 | kernel-985-ctx_0x55f2413c4de0.traceg.xz | temporal_q1;compressed_size_q0 |
| prefill | 6 | 250 | 996 | kernel-996-ctx_0x55f2413c4de0.traceg.xz | temporal_q1;compressed_size_q1 |
| prefill | 7 | 274 | 1021 | kernel-1021-ctx_0x55f2413c4de0.traceg.xz | temporal_q1;compressed_size_q2 |
| prefill | 8 | 247 | 992 | kernel-992-ctx_0x55f2413c4de0.traceg.xz | temporal_q1;compressed_size_q3 |
| prefill | 9 | 450 | 1205 | kernel-1205-ctx_0x55f2413c4de0.traceg.xz | temporal_q2;compressed_size_q0 |
| prefill | 10 | 449 | 1204 | kernel-1204-ctx_0x55f2413c4de0.traceg.xz | temporal_q2;compressed_size_q1 |
| prefill | 11 | 442 | 1197 | kernel-1197-ctx_0x55f2413c4de0.traceg.xz | temporal_q2;compressed_size_q2 |
| prefill | 12 | 415 | 1168 | kernel-1168-ctx_0x55f2413c4de0.traceg.xz | temporal_q2;compressed_size_q3 |
| prefill | 13 | 616 | 1379 | kernel-1379-ctx_0x55f2413c4de0.traceg.xz | temporal_q3;compressed_size_q0 |
| prefill | 14 | 617 | 1380 | kernel-1380-ctx_0x55f2413c4de0.traceg.xz | temporal_q3;compressed_size_q1 |
| prefill | 15 | 610 | 1373 | kernel-1373-ctx_0x55f2413c4de0.traceg.xz | temporal_q3;compressed_size_q2 |
| prefill | 16 | 625 | 1388 | kernel-1388-ctx_0x55f2413c4de0.traceg.xz | temporal_q3;compressed_size_q3 |
| decode1 | 1 | 74 | 1540 | kernel-1540-ctx_0x55d98da1ddf0.traceg.xz | temporal_q0;compressed_size_q0 |
| decode1 | 2 | 71 | 1537 | kernel-1537-ctx_0x55d98da1ddf0.traceg.xz | temporal_q0;compressed_size_q1 |
| decode1 | 3 | 94 | 1561 | kernel-1561-ctx_0x55d98da1ddf0.traceg.xz | temporal_q0;compressed_size_q2 |
| decode1 | 4 | 85 | 1551 | kernel-1551-ctx_0x55d98da1ddf0.traceg.xz | temporal_q0;compressed_size_q3 |
| decode1 | 5 | 299 | 1775 | kernel-1775-ctx_0x55d98da1ddf0.traceg.xz | temporal_q1;compressed_size_q0 |
| decode1 | 6 | 276 | 1751 | kernel-1751-ctx_0x55d98da1ddf0.traceg.xz | temporal_q1;compressed_size_q1 |
| decode1 | 7 | 288 | 1764 | kernel-1764-ctx_0x55d98da1ddf0.traceg.xz | temporal_q1;compressed_size_q2 |
| decode1 | 8 | 265 | 1739 | kernel-1739-ctx_0x55d98da1ddf0.traceg.xz | temporal_q1;compressed_size_q3 |
| decode1 | 9 | 465 | 1949 | kernel-1949-ctx_0x55d98da1ddf0.traceg.xz | temporal_q2;compressed_size_q0 |
| decode1 | 10 | 460 | 1944 | kernel-1944-ctx_0x55d98da1ddf0.traceg.xz | temporal_q2;compressed_size_q1 |
| decode1 | 11 | 468 | 1952 | kernel-1952-ctx_0x55d98da1ddf0.traceg.xz | temporal_q2;compressed_size_q2 |
| decode1 | 12 | 469 | 1953 | kernel-1953-ctx_0x55d98da1ddf0.traceg.xz | temporal_q2;compressed_size_q3 |
| decode1 | 13 | 645 | 2137 | kernel-2137-ctx_0x55d98da1ddf0.traceg.xz | temporal_q3;compressed_size_q0 |
| decode1 | 14 | 656 | 2148 | kernel-2148-ctx_0x55d98da1ddf0.traceg.xz | temporal_q3;compressed_size_q1 |
| decode1 | 15 | 641 | 2133 | kernel-2133-ctx_0x55d98da1ddf0.traceg.xz | temporal_q3;compressed_size_q2 |
| decode1 | 16 | 649 | 2141 | kernel-2141-ctx_0x55d98da1ddf0.traceg.xz | temporal_q3;compressed_size_q3 |

Fallback rule: if an input phase has fewer than 16 metadata-valid entries, or
a cell cannot choose a unique candidate, fail `INVALID_CONFIG`; do not silently
substitute a trace. In the B9 metadata-only dry run all 32 cells used the normal
`NEAREST_UNIQUE_METADATA_SIGNATURE` path, so no fallback was used.
