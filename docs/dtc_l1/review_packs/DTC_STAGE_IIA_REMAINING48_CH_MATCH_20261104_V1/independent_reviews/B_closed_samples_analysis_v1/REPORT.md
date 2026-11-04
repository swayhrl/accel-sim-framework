# Remaining48: first 13 accepted CH points, closed program/kernel evidence

**Fixed as-of:** 2026-11-04 09:45:49 Asia/Shanghai (01:45:49UTC), source-qualified snapshot 20261104T014550071642Z_5263ab47. This analysis intentionally freezes that snapshot even if the live provider advances. It covers 13/48 new CH points across 10/24 new programs, with 3 new programs complete in both F profiles. Overall CORE32 common coverage at this snapshot is 11/32, including the already completed first 8. No partial GM is computed or presented as a CORE32 conclusion.

**Findings:** twelve matched CH/DH F comparisons are exact zero response within each design, down to every captured kernel cycle and the selected final additive counters. Six programs have 0 issued DRAM reads/writes and 0 controller requests across all consumed closed profiles. Their nonzero all-L2 misses, where present, are GLOBAL writes rather than read misses. The sole nonzero newly matched case is fastWalshTransform-F128: CH improves 418 cycles, DH regresses 65 cycles. Both have identical DRAM volume and fewer retry/admission events; the phase decomposition shows opposing stage movements.

The closed sample is dominated by short jobs that finished first, not a new benchmark selection. Every planned input remains in the consumer's fixed 32 population, and missing CH counterparts remain pending rather than inferred from old DH data. No source, model, dispatcher/owner, registry, input, budget or v0.23 manuscript is modified.

## All thirteen newly closed comparisons

| Program | F | CH0 | CH_F | DH0 | DH_F | S_CH | S_DH | CH_F/DH_F | I |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BlackScholes | F128 | 8,993 | 8,993 | 8,971 | 8,971 | 1.000000 | 1.000000 | 1.002452 | 1.000000 |
| BlackScholes | F256 | 8,993 | 8,993 | 8,971 | 8,971 | 1.000000 | 1.000000 | 1.002452 | 1.000000 |
| fastWalshTransform | F128 | 191,732 | 191,314 | 185,317 | 185,382 | 1.002185 | 0.999649 | 1.031999 | 0.997470 |
| histogram | F128 | 101,432 | 101,432 | 98,202 | 98,202 | 1.000000 | 1.000000 | 1.032891 | 1.000000 |
| mergeSort | F128 | 114,742 | 114,742 | 111,917 | 111,917 | 1.000000 | 1.000000 | 1.025242 | 1.000000 |
| bfs | F256 | 4,330,430 | 4,330,430 | 4,170,294 | 4,170,294 | 1.000000 | 1.000000 | 1.038399 | 1.000000 |
| dwt2d | F128 | 73,691 | 73,691 | 73,071 | 73,071 | 1.000000 | 1.000000 | 1.008485 | 1.000000 |
| dwt2d | F256 | 73,691 | 73,691 | 73,071 | 73,071 | 1.000000 | 1.000000 | 1.008485 | 1.000000 |
| gaussian | F128 | 763,932 | 763,932 | 740,717 | 740,717 | 1.000000 | 1.000000 | 1.031341 | 1.000000 |
| heartwall | F128 | 8,782 | 8,782 | 8,551 | 8,551 | 1.000000 | 1.000000 | 1.027014 | 1.000000 |
| lud | F128 | 485,866 | 485,866 | 478,654 | 478,654 | 1.000000 | 1.000000 | 1.015067 | 1.000000 |
| lud | F256 | 485,866 | 485,866 | 478,654 | 478,654 | 1.000000 | 1.000000 | 1.015067 | 1.000000 |
| particlefilter_naive | F128 | 511,136 | 511,136 | 384,601 | 384,601 | 1.000000 | 1.000000 | 1.329003 | 1.000000 |

The fastWalsh DH-F128 sign is retained as measured (S_DH 0.999649, cycle increase 0.0351%); it is neither discarded as noise nor promoted to a gain. Its CH speedup is 1.002185 and I 0.997470. The original DH-F256 point 185,740 cycles is separately available, but new CH-F256 is pending in this snapshot, so no matched F256 I is claimed.

## Program/kernel scope and source-derived interpretation

| Program / full input identity | Observed launches and unique symbols | Source-candidate behavior | Measured scope/limit |
| --- | --- | --- | --- |
| BlackScholes / b31a85e4eb8d32ef5d706c2a84c999f6e3af598b1df43c85e149d03fa1568ac0 | 1; _Z15BlackScholesGPUPfS_S_S_S_ffi:1 | Grid-stride option pricing; independent input/output arrays, no explicit shared-memory/CTA reduction. | Only write misses are observed at L2; no issued DRAM reads/writes or controller requests. Fixed F has no measured window benefit here. |
| fastWalshTransform / f7f22a2ccc836a8a9b2096d4df50caf00a2c4bcebc7b16d064b8b0287ce593d3 | 16; _Z15fwtBatch2KernelPfS_i:12; _Z15fwtBatch1KernelPfS_i:3; _Z14modulateKernelPfS_i:1 | Global radix4 butterfly passes, shared terminal transform with CTA barriers, and global modulate step. | All issued DRAM reads and L2 retries occur in K6 print interval; later kernel cycle differences include shared terminal transforms. Source timing/ordering hypothesis remains unconfirmed. |
| histogram / 3722a5c85d91a9482233c2bf128a6721e3fb194db3e5e54be6cbec9598518a58 | 8; _Z17histogram64KernelPjP5uint4j:2; _Z22mergeHistogram64KernelPjS_j:2; _Z18histogram256KernelPjS_j:2; _Z23mergeHistogram256KernelPjS_j:2 | Two histogram implementations with shared private/warp-local counts and separate global partial merges. | DRAM-free replay still has ICNT admission events. That legacy stall counter is not an isolated DRAM-queue delay. |
| mergeSort / dd9f695c4f53b08394e7fd53a9eecedfd8372aa5cda7aae047f8a70162a40c48 | 13; _Z21mergeSortSharedKernelILj1EEvPjS0_S0_S0_j:1; _Z25generateSampleRanksKernelILj1EEvPjS0_S0_jjj:3; _Z26mergeRanksAndIndicesKernelPjS_jjj:6; _Z30mergeElementaryIntervalsKernelILj1EEvPjS0_S0_S0_S0_S0_jj:3 | Shared base sort, sample-rank generation, rank/index merge and elementary-interval merges. | All measured miss sectors are GLOBAL writes, not failed reads; fixed F is exactly zero response. |
| bfs / 1df9d5479504d9c7c5f5ef176e9604ce1b43421c7b6be440597259607d3971c0 | 11; _Z17BFS_in_GPU_kernelPiS_P4int2S1_S_S_iS_iiS_:6; _Z26BFS_kernel_multi_blk_inGPUPiS_P4int2S1_S_S_S_S_iiS_S_S_S_:5 | Queue/frontier traversal, graph reads and atomics; single-CTA and multi-block GPU traversal variants. | 11 captured launches are not11proven BFS levels. Read traffic is85CH/159DH atoms and cycles are unchanged by accepted CH-F256. |
| dwt2d / e5638b94095098acf5186be97210cb371bb3f88dcc8ceefb7609b454ef5ce008 | 10; _Z21c_CopySrcToComponentsIiEvPT_S1_S1_Phi:1; _ZN8dwt_cuda12fdwt53KernelILi64ELi8EEEvPKiPiiii:9 | Component split then three channels by three lifting-transform levels, with shared/register neighborhoods. | 10captured kernels all have identical cycles across accepted variants. All-L2 misses are write sectors and DRAM data requests are zero. |
| gaussian / 16f4c42373e4961eac6b16178237f1de2bbdf21d5e08bf669c4b6102bab2c6b3 | 126; _Z4Fan1PfS_ii:63; _Z4Fan2PfS_S_iii:63 | Fan1 multiplier production followed by Fan2 matrix/right-hand-side updates across pivots. | 126captured kernels (63eachFan1/Fan2) are unchanged; no measured DRAM window traffic. |
| heartwall / 731af5428c4b81552d8750c8edf9eeb609b71bd4f3651ca378a4dd73b194d980 | 1; _Z6kernelv:1 | Frozen one-frame/template branch is source-consistent; later-frame tracking/reductions are separate dormant candidate capability. | One captured kernel, two read atoms; do not generalize its response to multi-frame tracking. |
| lud / b33381cf25d443599aea5253936c13914acb0a2e7c22478496025c5234aef1f8 | 46; _Z12lud_diagonalPfii:16; _Z13lud_perimeterPfii:15; _Z12lud_internalPfii:15 | Diagonal factorization, dependent perimeter solves and tiled trailing updates. | 46captured kernels (16diagonal/15perimeter/15internal) are unchanged in both accepted F profiles; no DRAM data requests. |
| particlefilter_naive / 3f85d1878aba9f04916ec52cc1162b37673f92a88be07c4db815240c9564755e | 9; _Z6kernelPdS_S_S_S_S_i:9 | Per-particle sequential CDF threshold search and gather, divergent by threshold; no shared staging or GPU reduction. | Nine captured kernels and two read atoms; inherited DTC/CH ratio1.329 remains under F128 but receives no additional F speedup. |

Program descriptions are fixed Atlas candidate-source deductions, not capture ELF/numeric certification or measured cache-hit/merge behavior. Runtime names/order/instruction contracts and all cycles were independently matched to the actual frozen body qualification. Source reports at Atlas 47a097aad4406893a07f8d230e1e0a850609bf39, their Git paths/SHA and exact per-program provenance limits are preserved in FIXED_ATLAS_REPORT_BINDINGS.json and fixed_atlas_reports/. They are not reintroduced as a new generic source survey.

## Why all-L2 miss does not imply DRAM-read pressure

| Program | CH0 GLOBAL read misses32B | CH0 all-L2 misses32B | Nonzero CH0 miss access types | All consumed profiles DRAM_R/W/n_req zero | Observed HtoD count / bytes |
| --- | --- | --- | --- | --- | --- |
| BlackScholes | 0 | 25,000 | {'GLOBAL_ACC_W': 25000} | 1 | 3 / 1200000 |
| bfs | 85 | 341 | {'GLOBAL_ACC_R': 85, 'GLOBAL_ACC_W': 256} | 0 | 26 / 10258312 |
| dwt2d | 0 | 27,648 | {'GLOBAL_ACC_W': 27648} | 1 | 1 / 110592 |
| fastWalshTransform | 65,280 | 65,280 | {'GLOBAL_ACC_R': 65280} | 0 | 2 / 2105344 |
| gaussian | 0 | 0 | {} | 1 | 3 / 33024 |
| heartwall | 2 | 16,686 | {'GLOBAL_ACC_R': 2, 'GLOBAL_ACC_W': 16684} | 0 | 8 / 1961360 |
| histogram | 0 | 7,752 | {'GLOBAL_ACC_W': 7752} | 1 | 1 / 65536 |
| lud | 0 | 0 | {} | 1 | 1 / 262144 |
| mergeSort | 0 | 4,128 | {'GLOBAL_ACC_W': 4128} | 1 | 2 / 65536 |
| particlefilter_naive | 2 | 2 | {'GLOBAL_ACC_R': 2} | 0 | 54 / 432000 |

BlackScholes 25,000, histogram 7,752, mergeSort 4,128 and dwt2d 27,648 all-L2 miss sectors are explicitly GLOBAL_ACC_W, while GLOBAL read misses and issued DRAM data requests are 0. Gaussian/lud have no measured L2 misses or DRAM data requests. This is a counted access-type distinction, not missing counters treated as zero. All 53 closed sources conserve the per-type MISS+SECTOR_MISS sum against the all-L2 miss total.

The actual fixed L2 string `S:128:128:16,L:B:m:L:L,A:192:4,32:0,32` selects write-back plus LAZY_FETCH_ON_READ. Fixed Core 9eed `gpu-cache.h:696-712;1610-1626` maps this option to `wr_miss_wa_lazy_fetch_on_read`; `gpu-cache.cc:1858-1922` marks writes dirty/valid and returns MISS without an ordinary read fetch, with writeback conditional on a dirty eviction. This provides a source-established reason a counted write miss need not produce a DRAM read. It does not identify every individual event's dynamic path or prove application stores/dirty cache data were absent. Issued write 0 is not a complete eventual dirty-data drain guarantee.

Every closed raw prints the exact frozen ordered MemcpyHtoD/kernel commands; all 53 command lists were checked, not assumed from file names. The actual options retain perf_sim_memcpy=1 and flush_l2_cache=0. Fixed Framework/Core code routes those copies through 32-byte `force_l2_tag_update`/tag fill without ordinary timed host-transfer DRAM traffic. This establishes the active replay prefill policy; reuse during kernels and across kernels can also contribute. It does not certify all data residence, original numerical input or real-GPU warm/cold behavior. CONSUMED_MEMCPY_SOURCE_EVIDENCE.json retains exact source commit/path/SHA/line witnesses.

These six measured replays do not exercise an issued DRAM data-request window under this fixed sampled condition. They must not be called compute-bound, nor used to generalize that L2/DRAM resources never matter to their larger/other inputs. In particular, histogram still reports CH 341,933 / DH 395,635 ICNT blocked-admission events despite DRAM_R/W/n_req0. The legacy label `gpu_stall_dramfull` is an ICNT-to-subpartition admission-event counter, not isolated DRAM queue time or critical-path duration.

## fastWalshTransform: opposite stage responses

The actual 16 kernel sequence is 12 global fwtBatch2,3 shared terminal fwtBatch1,1 modulate. For both CH and DH, K1-K5 cycle counts are unchanged across the matched P0/F128 run. All 65,280 issued read atoms (2,088,960 bytes) and all visible L2 retries occur in the K6 print interval. Later kernel cycles can still move even with 0 new issued DRAM reads in their intervals; a zero-current-traffic phase is not proof of timing/history independence. These are completed-kernel print intervals, not guaranteed request-origin labels.

| K | Actual symbol | CH0 | CH128 | CHdelta | DH0 | DH128 | DHdelta | CH0/128 DRAM read atoms in interval |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | _Z15fwtBatch2KernelPfS_i | 10,247 | 10,247 | 0 | 10,149 | 10,149 | 0 | 0/0 |
| 2 | _Z15fwtBatch2KernelPfS_i | 10,348 | 10,348 | 0 | 10,094 | 10,094 | 0 | 0/0 |
| 3 | _Z15fwtBatch2KernelPfS_i | 10,357 | 10,357 | 0 | 10,099 | 10,099 | 0 | 0/0 |
| 4 | _Z15fwtBatch2KernelPfS_i | 10,791 | 10,791 | 0 | 10,404 | 10,404 | 0 | 0/0 |
| 5 | _Z15fwtBatch1KernelPfS_i | 16,439 | 16,439 | 0 | 16,022 | 16,022 | 0 | 0/0 |
| 6 | _Z15fwtBatch2KernelPfS_i | 13,414 | 13,227 | -187 | 12,858 | 12,641 | -217 | 65280/65280 |
| 7 | _Z15fwtBatch2KernelPfS_i | 10,301 | 10,368 | 67 | 10,044 | 10,153 | 109 | 0/0 |
| 8 | _Z15fwtBatch2KernelPfS_i | 10,523 | 10,455 | -68 | 10,155 | 10,164 | 9 | 0/0 |
| 9 | _Z15fwtBatch2KernelPfS_i | 11,132 | 10,792 | -340 | 10,505 | 10,471 | -34 | 0/0 |
| 10 | _Z15fwtBatch1KernelPfS_i | 16,536 | 16,574 | 38 | 15,951 | 16,185 | 234 | 0/0 |
| 11 | _Z14modulateKernelPfS_i | 12,891 | 12,832 | -59 | 12,801 | 12,722 | -79 | 0/0 |
| 12 | _Z15fwtBatch2KernelPfS_i | 10,370 | 10,459 | 89 | 10,222 | 10,218 | -4 | 0/0 |
| 13 | _Z15fwtBatch2KernelPfS_i | 10,348 | 10,358 | 10 | 10,071 | 10,052 | -19 | 0/0 |
| 14 | _Z15fwtBatch2KernelPfS_i | 10,506 | 10,532 | 26 | 10,205 | 10,132 | -73 | 0/0 |
| 15 | _Z15fwtBatch2KernelPfS_i | 10,925 | 10,821 | -104 | 10,529 | 10,607 | 78 | 0/0 |
| 16 | _Z15fwtBatch1KernelPfS_i | 16,604 | 16,714 | 110 | 15,208 | 15,269 | 61 | 0/0 |

| Design | Candidate phase | P0 cycles | F128 cycles | Delta |
| --- | --- | --- | --- | --- |
| CH | global_radix4 | 129,262 | 128,755 | -507 |
| CH | shared_terminal_transform | 49,579 | 49,727 | 148 |
| CH | modulate | 12,891 | 12,832 | -59 |
| DH | global_radix4 | 125,335 | 125,184 | -151 |
| DH | shared_terminal_transform | 47,181 | 47,476 | 295 |
| DH | modulate | 12,801 | 12,722 | -79 |

CH cycle delta= -507 global +148 shared -59 modulate = -418. DH delta= -151 global +295 shared -79 modulate = +65. Thus a small global-pass gain coexists with a larger shared-terminal-pass regression in DH. Candidate fwtBatch1 uses shared staging/barriers; this is a source characteristic, not proof that shared-memory/barrier service caused the measured regression. Changed timing/order/clock alignment/history are hypotheses until a critical-path observation establishes a cause.

CH L2 retries 147,110 ->133,311 and ICNT admission events 688,493 ->676,494 fall. DH retries 127,552 ->115,953 and admission 639,783 ->623,587 also fall, yet DH total cycles increase. DH OO lower creations 265,674 ->265,624 and valid-line hits 12,854 ->12,904 conserve 278,528 classified line probes, with accepted sectors=4*128B lower creations. These small improvements in selected counters do not imply a faster end-to-end execution.

DH finite-service ready-to-complete sum 678,914 ->680,234 and writeback wait 51,672 ->52,289 rise slightly; these are aggregate entry/sample measures, not critical-path cycles. Reported MRQ 115 ->198(CH)/199(DH) increases while mflatency 1123 ->1114(CH),1168 ->1161(DH) slightly decreases. Means have distinct denominators and known print/update/tail windows; the final dictionary is not an exact per-kernel or full-app mean. Do not subtract/sum means or read missing latency as 0. No proof that average complete L2-to-DRAM critical-load latency fell is available.

## Facts, correlations and unresolved cause

- Facts: 12 zero paired responses include identical per-kernel cycles/selected additive totals; six programs have explicitly 0 DRAM requests; FWT has one cold/read-active print interval and mixed later phase deltas. All source RESULT/raw gzip/raw plain/input-binding/exit hashes and actual kernel contracts were checked.
- Source deductions: fixed replay memcpy prefill, active lazy-write policy, and per-kernel algorithm/control descriptions; capture source/ELF/original numerical completeness remains bounded by each frozen report.
- Correlations: FWT counters for retries/OO misses improve while its DH cycles regress slightly; zero-response cases coincide with little/no DRAM request volume. Neither association identifies a critical path.
- Unconfirmed: bank/credit occupancy, request age, pipeline/barrier/issue/finite-service criticality and causal timing history. Current means/retry counts are not occupancy or stall-time attribution. No new instrumentation, rerun or combination is started.

CH PAPER_BASE common PIB 256 and DH PAPER_OO PIB 128 remain explicitly separate; generic DH PIB 8 does not set OO admission. Unprinted OO PIB-full/Tag-conflict fields stay null and are not populated with CH zeros. Cross-design L1/Tag/physical pool/queues/timing/area differences remain. FR-FCFS 64/128/256 also changes shared-credit limits 255/319/447, while DRAM 850 MHz and 10 MiB L2 stay fixed. This is a coupled-window/credit study, not free equal-area hardware.

## Evidence and reproducibility

Authority 5f67b4d6b94568a9f1acc80c3e56736bd81e4753 and fixed identity plan 5001c3f35052f7f91f1ad41eeff83f2947a0878d remain unchanged. Runtime Core 9eedb3131937748f0492fa83aad37d3691118d70 / Framework 02775fd795cde5aae1480d81cee6eb481d0a08f4 / binary 02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d are verified across all 53 closed sources. SOURCE_SNAPSHOT_RECEIPT.json pins the exact qualified snapshot manifest 1292c386ef93ba0a49772b608a13310fe772db77611f769cc0082c0c35ea9a80, observed provider pointer SHA, source-qualified counts and all compressed file hashes.

CLOSED_SOURCE_KERNEL_COUNTERS.json.gz holds all 53 RESULT/raw/exit/input-binding paths/SHA, UUIDs, roles, every actual kernel name/instruction/cycle/raw-line boundary, explicit additive intervals, retry reasons and command invocations. MATCHED_COMPARISONS.json includes all 13 paired signs/zeros and every kernel cycle delta. TYPE_MISS_AND_INITIAL_STATE.json and TYPED_FRONTEND_SERVICE.json retain access-type/domain distinctions. WALSH_PHASE_GROUPS.json preserves candidate grouping. Fixed source semantics/catalog and 175+173=348 passing evidence checks are separate files. No live raw was read or copied into Git.

The frozen default script does not overwrite a published MANIFEST. For a later naturally closed qualified snapshot, use the same entry with `--provider <official_PUBLICATION_PROVIDER.json> --output-dir <this_dir>/updates/<new_tag>`; it writes a new child, retaining all then-accepted counterparts and pending coverage without altering reader/native files. This is a callable analysis entry, not another daemon or model controller. New source-candidate claims require review; no absent F counterpart or mechanistic counter is inferred.

| Program | Profile | Role | RESULT path | RESULT SHA256 |
| --- | --- | --- | --- | --- |
| BlackScholes | CH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-b31a85e4eb8d32ef-CH-P0-V1.RESULT.json | 9a274b35567d9fe5f6835ae9d2f71742b47b32ec35763cf2162b7a745cdb9492 |
| BlackScholes | CH-F128 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-b31a85e4eb8d32ef-CH-F128-V1.RESULT.json | 79dd18258d13e7457b09b247a56fd0f941d9539367c2bda48a121906f7f1bc82 |
| BlackScholes | CH-F256 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-b31a85e4eb8d32ef-CH-F256-V1.RESULT.json | a3ad878b1d872fdaa1cd7ee4c0f4d4987167b320ce2c73f29773331b319db9d4 |
| BlackScholes | DH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-b31a85e4eb8d32ef-DH-P0-V1.RESULT.json | 81ccd85d831c67931d22f939897247d66b805cf7dcd67050bb6093adafb8ffb0 |
| BlackScholes | DH-F128 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-b31a85e4eb8d32ef-DH-F128-V1.RESULT.json | 9ef431a4a7c846f69781da71f019b3b1779198bc311ababb02ee9c65171b490e |
| BlackScholes | DH-F256 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-b31a85e4eb8d32ef-DH-F256-V1.RESULT.json | 0d42081b1fffe12d5c067057d328e2e80d9adfd291331576b536c0992e7c28e5 |
| fastWalshTransform | CH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-f7f22a2ccc836a8a-CH-P0-V1.RESULT.json | 4d0b7fcf1f135f7c0c042304b83815ded78510f8c6d0ccb82aadf635cd046043 |
| fastWalshTransform | CH-F128 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-f7f22a2ccc836a8a-CH-F128-V1.RESULT.json | a6f6ffff0b8328047380d2c2da972ab4c9ea49747b61f05fcefffcd2c88a87eb |
| fastWalshTransform | DH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-f7f22a2ccc836a8a-DH-P0-V1.RESULT.json | 5018a7c116f04d79801e28ecc48747c7f009456002594c2c1e3ec1552326c36e |
| fastWalshTransform | DH-F128 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-f7f22a2ccc836a8a-DH-F128-V1.RESULT.json | 07616f1096bbd79cf3b05be8a97323efdc72b5885612bfe0d421c9293f96ebe6 |
| fastWalshTransform | DH-F256 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-f7f22a2ccc836a8a-DH-F256-V1.RESULT.json | 61afec1e6df93780e8a8d08a999360226f6d6e26fec9d301ebb98f5734452880 |
| histogram | CH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-3722a5c85d91a948-CH-P0-V1.RESULT.json | 0d90e2c67b9b353115e0b27408ab70961c8433b98635964c9b9302f725820eae |
| histogram | CH-F128 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-3722a5c85d91a948-CH-F128-V1.RESULT.json | 29f5f45d849c43cdfcef139d6dbe92140eb21f0e2d119322d750929a561940f9 |
| histogram | DH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-3722a5c85d91a948-DH-P0-V1.RESULT.json | 3ef7b9b076636a9d839c298ce2365f69632da7a8c6736b3656118953dd0e5bc0 |
| histogram | DH-F128 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-3722a5c85d91a948-DH-F128-V1.RESULT.json | 073b90e208deec64e6bcd4180b6defb17c5bd6c6f10260027b5f8e0c9b87c1f8 |
| histogram | DH-F256 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-3722a5c85d91a948-DH-F256-V1.RESULT.json | bb39980d28157a31dca321c34b2de830f354241e5bcd4cabb635b8bbf2800513 |
| mergeSort | CH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-dd9f695c4f53b083-CH-P0-V1.RESULT.json | 25b4025604ad038f2d6fa88d3c6405d2bd1ba004ee3325a792d9ac814a27b76d |
| mergeSort | CH-F128 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-dd9f695c4f53b083-CH-F128-V1.RESULT.json | d5a16e01769c2833544700070e45399ceac39a962bcef6bd1b468411df8f8cc5 |
| mergeSort | DH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-dd9f695c4f53b083-DH-P0-V1.RESULT.json | 7ff810be923c6f06c3f9e746991419e5aa97aa7540d2df800f550c4620658e27 |
| mergeSort | DH-F128 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-dd9f695c4f53b083-DH-F128-V1.RESULT.json | 2140165a8bcc92dd0bd86c6dac505ab7a20b1d5447f631446ce2e6d364df9d8e |
| mergeSort | DH-F256 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-dd9f695c4f53b083-DH-F256-V1.RESULT.json | e3c4c166efb6504291f1f8bcc9202beb716abfd565b62928dc113cc9c252d382 |
| bfs | CH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-1df9d5479504d9c7-CH-P0-V1.RESULT.json | 625439ea99a4cb8f06e62b3fcdd03f7f1e51246801849df9eb08fd706653d9fe |
| bfs | CH-F256 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-1df9d5479504d9c7-CH-F256-V1.RESULT.json | da16e5d87bef8860fa1662696cfb225ec6c6c408a0515b8616c48f77432fd0fa |
| bfs | DH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-1df9d5479504d9c7-DH-P0-V1.RESULT.json | 656cd84e4b4e308d987dd2085952629cb20e9a5d1f666b6cd42590466ed2480a |
| bfs | DH-F128 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-1df9d5479504d9c7-DH-F128-V1.RESULT.json | 936f19db1a7d1ec50cb83d1036065590d670fa915d65dc0a4305183ce7671782 |
| bfs | DH-F256 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-1df9d5479504d9c7-DH-F256-V1.RESULT.json | b0cd8663bc22a2adc69302a50b21fc5187051cca6e1ebd4233facd5dc7e974b3 |
| dwt2d | CH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-e5638b94095098ac-CH-P0-V1.RESULT.json | 74ad42916e03a15d9899e01b16582c35ffd52a339320138ff579b2610611f020 |
| dwt2d | CH-F128 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-e5638b94095098ac-CH-F128-V1.RESULT.json | a08cfc11bdc309bf4f2fb8ce84b7cd8885ed488b58980dd017fa71d72747110b |
| dwt2d | CH-F256 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-e5638b94095098ac-CH-F256-V1.RESULT.json | da2e6a8d68c790ad5a9e44c88f2625b5dfd893298505d1f8501387b71555e7bf |
| dwt2d | DH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-e5638b94095098ac-DH-P0-V1.RESULT.json | 6c6e3c0a1f09ac958c730914cc9301c18f06c57fd848b86a58827085601e08c7 |
| dwt2d | DH-F128 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-e5638b94095098ac-DH-F128-V1.RESULT.json | 2a8d105e93e1459bb3980b660922f962acc1dbc91a835daa0efb29130789e865 |
| dwt2d | DH-F256 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-e5638b94095098ac-DH-F256-V1.RESULT.json | f415905433b4f04fee3ff6ed48fd05cd174228ac65aa4c128bab49758b335eea |
| gaussian | CH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-16f4c42373e4961e-CH-P0-V1.RESULT.json | 7cdf50cc23ff8c970df1da5378b1257636e587cea50cdfea295c3029e8db248a |
| gaussian | CH-F128 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-16f4c42373e4961e-CH-F128-V1.RESULT.json | a35723b5a91d3ae9aca569b1e60600d631265017c0283d6894b45af943306843 |
| gaussian | DH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-16f4c42373e4961e-DH-P0-V1.RESULT.json | 2d4cd72fe067dcc235562f095f29bd11a721487f0771775af013d5d08e2b12ea |
| gaussian | DH-F128 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-16f4c42373e4961e-DH-F128-V1.RESULT.json | e7964dd5510e66b49af5466fd28014eaf47fe8f4de3ad975e57989bad92518a4 |
| gaussian | DH-F256 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-16f4c42373e4961e-DH-F256-V1.RESULT.json | 7a7edec5116dfad431c404d3c2e9cd270d7340082af9c5a6aea490d16a4773a5 |
| heartwall | CH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-731af5428c4b8155-CH-P0-V1.RESULT.json | aab8063317b452fb6db7bfa2b8e47948d082939e72433b62acf81003eb6d8b2c |
| heartwall | CH-F128 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-731af5428c4b8155-CH-F128-V1.RESULT.json | 577c59dc7f215ce886841998445580e629d561d423c2edb37fab2d1b110ae426 |
| heartwall | DH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-731af5428c4b8155-DH-P0-V1.RESULT.json | 5c18b6dd2ce866c6042db1588632a1862e1315b95f2a9635e6aad8ff600d651d |
| heartwall | DH-F128 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-731af5428c4b8155-DH-F128-V1.RESULT.json | bac564c2e5ec956dd2d102ae56d9d59b973ee991943825b18304cda8b5c628e7 |
| heartwall | DH-F256 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-731af5428c4b8155-DH-F256-V1.RESULT.json | 3b41bf77492e4f094d087df5c8432061f960f2816ed83ca01af8c1cd2b8a1204 |
| lud | CH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-b33381cf25d44359-CH-P0-V1.RESULT.json | 8b745ce8f84d0e188b3fca291cdd920801e655fffa00482c6b23a4da22afc5c4 |
| lud | CH-F128 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-b33381cf25d44359-CH-F128-V1.RESULT.json | 7f91dc779127884d36f7cb5307fd444e66be4c106423f05322862a9c7887c7c5 |
| lud | CH-F256 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-b33381cf25d44359-CH-F256-V1.RESULT.json | 237be1cd71e85074fc48e2a718177a3fa924c87645b08f7262a69320df826901 |
| lud | DH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-b33381cf25d44359-DH-P0-V1.RESULT.json | 4fe4f49e527be4294fd324edfb0e30fcee097791e8e987fffb8c23b6406b8fd7 |
| lud | DH-F128 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-b33381cf25d44359-DH-F128-V1.RESULT.json | 9b90df329e50b79842c9410f4e29ebab8645a793843e5a2a66a450ab5a582d1e |
| lud | DH-F256 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-b33381cf25d44359-DH-F256-V1.RESULT.json | b2082a78e72e7862b18c0103595e9d36865519880c4e02bbf170fdefbc54744c |
| particlefilter_naive | CH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-3f85d1878aba9f04-CH-P0-V1.RESULT.json | ecc70e3759939259361c827d1c5f904f3cadb4899157eb22701279e9e47e66cd |
| particlefilter_naive | CH-F128 | STAGEII_REMAINING48_AUTHORIZED_CH | /root/data/dtc_stage_iia_remaining48_20261104_v1/analysis/E2-DTC2A48-3f85d1878aba9f04-CH-F128-V1.RESULT.json | 0b3fdd6d0a61f7fdc5d2c28fabea7ab488b9884ddee7825f5459c680fe2d8e49 |
| particlefilter_naive | DH-P0 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-3f85d1878aba9f04-DH-P0-V1.RESULT.json | aff055d8d21fd4443c6dcbd19441ec7fdc39f6e196dc42dd7b2ed304fee311da |
| particlefilter_naive | DH-F128 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-3f85d1878aba9f04-DH-F128-V1.RESULT.json | 18f088709173047c5a09f8e4265ecc6fb5d95e0a97c859ee5fb89ef7e86749f0 |
| particlefilter_naive | DH-F256 | ORIGINAL_PHASE_I_SLOT | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-3f85d1878aba9f04-DH-F256-V1.RESULT.json | b1fad552d50ad2e3514472bbc42db8b42e38aaae3a397167ec23a95728c7e70c |
