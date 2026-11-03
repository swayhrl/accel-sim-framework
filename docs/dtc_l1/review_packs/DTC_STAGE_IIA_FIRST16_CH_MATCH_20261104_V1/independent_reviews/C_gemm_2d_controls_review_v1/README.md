# Independent interim GEMM/2DCONV F128 control review

Decision: **PASS_WITH_EXISTING_INITIAL_STATE_AND_SOURCE_LIMITS**. All57 check groups pass. The review is limited to eight closed sources in B_gemm_2d_f128_controls_v1, manifest `81a5c3a53dad7ea01d632228036b19275bb64ce6b45b8a180097a08e7d422b69`. It is not the all16 final review or a release of further experiments.

The two new CH-F128 results pass independent RESULT/strict/21-entry native restore/chunk SHA checks, with the genuine164 SSHFS mount and separate native filesystem confirmed. Original PhaseI sources retain their roles. All eight raw gzip/uncompressed hashes, natural exits, build identities, exact cycles and declared replay geometry were rechecked.

| Program | Actual replay | CH P0 / F128 cycles | DH P0 / F128 cycles | CH speedup | DH speedup |
| --- | --- | --- | --- | --- | --- |
| GEMM | 1kernel,739246080 active-thread instructions,1024CTAs | 1395216 /1395216 | 826089 /826089 | 1 | 1 |
| 2DCONV | 1kernel,620347492 active-thread instructions,65536CTAs | 1548909 /1548909 | 462740 /437573 | 1 | 1.057514975 |

GEMM is an exact zero response for the selected measured counters and cycles. Each of20 controllers explicitly prints zero request/activation/precharge/read/write fields, and GLOBAL L2 accepted reads are all HIT. This is not a compute-bound proof: CH retains226209642 L1 merge-limit retry events and DH retains1165837 ICNT admission-block events. Events are not critical-path cycles.

2DCONV CH is exactly unchanged. DH is25167cycles shorter, with unchanged2097152 DRAM read atoms and unchanged GLOBAL read misses. L2 reservation retries decline2546098 to1584855 and ICNT blocked-admission events decline3701660 to2776419. Contrary evidence remains: read MSHR entry failures rise82 to30449, ready-to-complete sum71495415 to74948733, ready-to-collect sum60291527 to63525333 and writeback wait2199467 to2341112. These are compatible associations, not an isolated cause or proof all service latency improved. Missing DH latency means remain missing despite nonzero DRAM reads.

The raw ordered memcpy commands precede each kernel and equal the SHA-pinned commandlist. Fixed Framework/Core source bytes and commit excerpts verify perf_memcpy_to_gpu ->32B address loop ->force_l2_tag_update ->tag-array fill. This establishes the fixed replay initial-state policy, not ordinary timed DRAM transfers, all copied-address residency, native GPU traffic or capture-time numeric correctness. GEMM copies3MiB;2DCONV copies64MiB, which must not be called fully resident in10MiB L2. Candidate source is not capture-ELF binding; declared trace completeness is not numerical certification.

CH common PIB256/Tag service and DH OO PIB128 retain distinct active domains; generic DH PIB8 is inactive for OO admission. F128 changes FRFCFS64 to128 plus the fixed shared-credit coupling255 to319. No equal-area or frontend-resource equality is inferred.

The first audit draft had two harness-only assumptions corrected before freeze: true164 canonical paths use /home/shared rather than containing the literal164; the actual report state-fill wording differs from the draft literal search. No scientific source or result changed. The final57 checks and included audit reproduce the corrected checks.

No models, owner, source, history,48 planning or v0.23 manuscript were changed. See CONTROLS_REVIEW.json for all paths, SHA and per-source evidence.
