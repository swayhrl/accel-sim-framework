# GEMM and 2DCONV: matched F128 controls

This packet consumes exactly eight closed accepted sources: original CH-P0/DH-P0/DH-F128 and authorized new CH-F128 for each frozen input. No F256 result is included, no new simulation was started, and no owner, controller, input, budget, source, manuscript or historical result was changed. Both new CH results were independently rechecked through the frozen read-only strict/archive/native-restore adapter. Seventy CPU-only evidence checks passed.

GEMM is an exact zero-response control under the fixed replay initial-state policy. 2DCONV is a positive DH response with exact CH zero response: DH speedup 1.057515x (5.75% more throughput, 5.44% fewer simulated cycles). Neither finding establishes an equal-area hardware comparison.

## Exact identity and actual ROI

| Program | Full input digest | Kernel symbol | Grid / block | Retired active-thread instructions | CTAs |
| --- | --- | --- | --- | --- | --- |
| GEMM | fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318 | _Z11gemm_kernelPfS_S_ | [16, 64, 1] / [32, 8, 1] | 739,246,080 | 1,024 |
| 2DCONV | d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0 | _Z20Convolution2D_kernelPfS_ | [128, 512, 1] / [32, 8, 1] | 620,347,492 | 65,536 |

Both are one-kernel stream-0 replays, not the 145,666,048-instruction/two-kernel matrix-vector contract. Current strict proof, frozen full-body qualification and a fresh bounded 4096-byte trace header agree. The preserved whole-body SHA qualification establishes all declared CTAs/warps with terminal EXIT within this trace scope; it does not certify native numerical correctness or capture-time ELF identity.

## Performance

| Program | CH-P0 | CH-F128 | DH-P0 | DH-F128 | S_CH | S_DH | CH/DH at F128 | I = S_DH/S_CH |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GEMM | 1,395,216 | 1,395,216 | 826,089 | 826,089 | 1.000000 | 1.000000 | 1.688942 | 1.000000 |
| 2DCONV | 1,548,909 | 1,548,909 | 462,740 | 437,573 | 1.000000 | 1.057515 | 3.539773 | 1.057515 |

P0->F128 changes only `-gpgpu_frfcfs_dram_sched_queue_size` 64->128 within each design. DRAM remains 850 MHz and the L2 cache remains `S:128:128:16,L:B:m:L:L,A:192:4,32:0,32` (10 MiB). The fixed Core shared-credit formula also changes each memory partition shared-credit limit 255->319; this is FR-FCFS-window plus credit expansion, not an isolated queue-capacity intervention. No cross-design capacity/Tag/PIB/finite-service equality is asserted.

## Additive counters at the single completed-kernel print boundary

L2 GLOBAL accepted reads and misses use 32-byte sectors. Accepted excludes reservation failures; GLOBAL misses = MISS + SECTOR_MISS. DRAM reads/writes are issued 32-byte data atoms across all20 controllers. All-L2 misses include access types beyond GLOBAL reads; keep these populations separate. Counters below are explicit cumulative values from the one-kernel stream-0 replay, not sums of cumulative snapshots. Retry/admission event counts are not occupancy, duration or critical-path fractions.

### GEMM

| Counter | CH-P0 | CH-F128 | DH-P0 | DH-F128 |
| --- | --- | --- | --- | --- |
| L2 GLOBAL accepted read sectors | 4,796,228 | 4,796,228 | 1,716,504 | 1,716,504 |
| L2 GLOBAL read miss sectors | 0 | 0 | 0 | 0 |
| All-L2 miss sectors | 0 | 0 | 0 | 0 |
| DRAM issued read atoms32B | 0 | 0 | 0 | 0 |
| DRAM issued write atoms32B | 0 | 0 | 0 | 0 |
| All-L2 pending hits | 0 | 0 | 0 | 0 |
| All-L2 reservation retry events | 0 | 0 | 0 | 0 |
| ICNT->memory blocked-admission events | 0 | 0 | 1,165,837 | 1,165,837 |

Raw positive-only retry reasons (unprinted means MISSING, never zero):

| Layer:type:reason | CH-P0 | CH-F128 | DH-P0 | DH-F128 |
| --- | --- | --- | --- | --- |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_R:MISS_QUEUE_FULL | 1,632,193 | 1,632,193 | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_R:MSHR_MERGE_ENRTY_FAIL | 226,209,642 | 226,209,642 | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_W:MISS_QUEUE_FULL | 936,357 | 936,357 | 412,936 | 412,936 |

### 2DCONV

| Counter | CH-P0 | CH-F128 | DH-P0 | DH-F128 |
| --- | --- | --- | --- | --- |
| L2 GLOBAL accepted read sectors | 7,734,348 | 7,734,348 | 7,675,016 | 7,679,232 |
| L2 GLOBAL read miss sectors | 2,097,152 | 2,097,152 | 2,097,152 | 2,097,152 |
| All-L2 miss sectors | 4,193,280 | 4,193,280 | 4,193,280 | 4,193,280 |
| DRAM issued read atoms32B | 2,097,152 | 2,097,152 | 2,097,152 | 2,097,152 |
| DRAM issued write atoms32B | 1,931,628 | 1,931,628 | 1,931,720 | 1,931,952 |
| All-L2 pending hits | 365,691 | 365,691 | 3,176,023 | 3,161,410 |
| All-L2 reservation retry events | 54 | 54 | 2,546,098 | 1,584,855 |
| ICNT->memory blocked-admission events | 0 | 0 | 3,701,660 | 2,776,419 |

Raw positive-only retry reasons (unprinted means MISSING, never zero):

| Layer:type:reason | CH-P0 | CH-F128 | DH-P0 | DH-F128 |
| --- | --- | --- | --- | --- |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MISS_QUEUE_FULL | MISSING | MISSING | 908,998 | 165,099 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MSHR_ENRTY_FAIL | MISSING | MISSING | 82 | 30,449 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_R:MSHR_MERGE_ENRTY_FAIL | 54 | 54 | 1,623,233 | 1,386,988 |
| L2_cache_stats_fail_breakdown:GLOBAL_ACC_W:MISS_QUEUE_FULL | MISSING | MISSING | 13,785 | 2,319 |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_R:MISS_QUEUE_FULL | 519 | 519 | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_R:MSHR_MERGE_ENRTY_FAIL | 315,294,062 | 315,294,062 | MISSING | MISSING |
| Total_core_cache_fail_stats_breakdown:GLOBAL_ACC_W:MISS_QUEUE_FULL | 241 | 241 | 2,126 | 1,333 |

## GEMM: facts and limited interpretation

All four closed sources explicitly report zero `n_req`, `n_act`, `n_pre`, `n_rd`, `n_rd_L2_A`, `n_write`, and `n_wr_bk` on every one of20 controllers. L2 GLOBAL read misses, all-L2 misses and L2 reservation failures are also zero. L2 GLOBAL read buckets are all HIT for the measured accepted requests. CH has4,796,228 accepted read sectors; DH1,716,504. Both designs retain exactly the same cycles, selected additive counters, L2 buckets and positive-only retry reasons when F128 is applied.

This excludes exercised DRAM request-window pressure for this fixed sampled condition. It does not show a compute-bound workload: CH still records226,209,642 ordinary-L1 MSHR merge-limit retry events and25,214,976 common Tag-bank conflict attempts; DH records1,165,837 ICNT->memory admission-block events,3,817,106 OO pending-line hits and389,331 ready-but-writeback-blocked events. The misleading legacy name `gpu_stall_dramfull` is an ICNT admission counter and can be nonzero even when issued DRAM traffic is zero. These are observable event populations, not proof of the dominant stall path.

DH finite-service samples52,869,696 and PIB integral3,116,491,485 are identical across F; so are the completion/collection/writeback measures. The speed difference between CH and DH is real for this input/configuration, but causality and hardware cost require the separate frontend architectures and finite service to remain disclosed.

## 2DCONV: facts, associations and hypotheses

Facts: CH remains1,548,909 cycles with identical selected cumulative counters, L2 buckets and retry reasons. DH drops462,740->437,573 cycles (25,167 fewer). Both DH runs issue exactly2,097,152 DRAM read atoms (64 MiB); writes increase1,931,720->1,931,952 atoms (+232, +0.0120%). GLOBAL read misses stay2,097,152 and all-L2 misses stay4,193,280. Therefore fewer DRAM reads or fewer miss sectors do not explain this gain. The printed issued-write counts do not certify all dirty cache state has been drained after the measured kernel.

Associations: DH L2 reservation retries fall37.75% (2,546,098->1,584,855) and ICNT admission blocks fall25.00% (3,701,660->2,776,419). Read MISS_QUEUE_FULL drops908,998->165,099; read MSHR merge-limit failures drop1,623,233->1,386,988. Read MSHR entry-capacity failures instead rise82->30,449. OO lower requests rise1,918,754->1,919,808 (+0.05493%); the L2 GLOBAL accepted-sector count is exactly4 times the128-byte OO lower creations in each run. This is a same-design request conservation check, not proof every DRAM request or lower request has a one-to-one critical-path role.

CH has0 ICNT admission-block events and only54 L2 reservation failures, yet315,294,062 ordinary-L1 merge-limit retries and15,720,960 common Tag-bank conflict attempts. DH has a much larger lower-interface retry population. This contrast supports testing whether the coupled downstream expansion changes admission/overlap for DH while CH exposes a different frontend limitation. It does not prove CH is limited exclusively by merge capacity, nor that increasing it would improve performance.

Hypothesis only: FR-FCFS-window/shared-credit expansion changes the timing of lower responses and overlapping requests, reducing some lower admission/retry pressure in DH. Existing event counts and aggregate cycles are consistent with this but do not isolate queue occupancy, queue residence, critical memory dependencies, bank scheduling or credit occupancy. Static nine-tap reuse and increased OO pending hits do not establish a causal cache-hit/MSHR-merge mechanism.

Contrary evidence against a blanket "all service latency improved" claim: DH ready-to-complete sum71,495,415->74,948,733; ready-to-collect sum60,291,527->63,525,333; writeback wait2,199,467->2,341,112. The finite-service retired denominator remains4,716,288. Mean PIB occupancy across64SM samples stays close to saturation; a shorter total runtime does not imply all entry lifetimes shrink.

## Typed frontend and finite-service domains

CH PAPER_BASE uses the active common PIB256; DH PAPER_OO uses its OO PIB128. DH generic PIB parameter8 is inactive for OO admission. CH common Tag/PIB fields are never inserted into DH OO-named fields. Unprinted OO PIB-full/Tag-conflict events stay null. CH finite-service extension is disabled; this does not imply its ordinary cache has unlimited service.

### GEMM DH finite-service derived quantities

| Profile | Mean PIB entries (all64SM samples) | Mean physical lines | Ready->retire cycles / retired entry | Map-loss->free cycles / recorded event |
| --- | --- | --- | --- | --- |
| P0 | 58.946650 | 443.267749 | 36.143571 | 27.638834 |
| F128 | 58.946650 | 443.267749 | 36.143571 | 27.638834 |

### 2DCONV DH finite-service derived quantities

| Profile | Mean PIB entries (all64SM samples) | Mean physical lines | Ready->retire cycles / retired entry | Map-loss->free cycles / recorded event |
| --- | --- | --- | --- | --- |
| P0 | 125.470887 | 502.771551 | 15.159256 | 0.001016 |
| F128 | 125.415299 | 502.240741 | 15.891467 | 0.000485 |

These ratios use their own known cumulative denominators; the mean across samples is not maximum occupancy, a stall fraction or critical-path latency. Gauges/peaks are retained separately and never differenced.

## Memcpy initial-state policy: runtime-matched evidence

| Program | Closed sources | HtoD calls before kernel | Bytes before kernel |
| --- | --- | --- | --- |
| GEMM | 4 | 3 | 3,145,728 |
| 2DCONV | 4 | 1 | 67,108,864 |

Every closed raw explicitly prints the exact frozen `MemcpyHtoD` commands before `Processing kernel`; the ordered commands match current kernelslist bytes/SHA and the frozen binding. All eight effective option maps retain perf_sim_memcpy=1, L2 flush=0. The fixed Framework calls `perf_memcpy_to_gpu`; Core iterates32-byte addresses and reaches `force_l2_tag_update`/tag-array fill instead of ordinary timed DRAM requests. `CONSUMED_MEMCPY_SOURCE_EVIDENCE.json` carries exact file SHA/commit/line excerpts; its complete source SHA set was rechecked. This is runtime invocation evidence linked to fixed code, stronger than source-only conjecture. It does not quantify which addresses survived replacement to kernel launch or certify capture-time numeric input.

GEMM has three1-MiB copies and its measured L2/DRAM counters confirm zero L2 misses/DRAM requests under this policy. 2DCONV has one64-MiB copy; this must not be interpreted as all64 MiB resident in10-MiB L2, and the measured nonzero DRAM traffic explicitly prevents such a claim. No cold-start or real-GPU generalization follows, and changing the warm-state policy would require a separately authorized experiment.

## Fixed source and evidence levels

Atlas47a097aad4406893a07f8d230e1e0a850609bf39 maps the candidate GEMM source dad09cb0487845edc7524ded814c6cde9f0ef6a1 `GEMM/gemm.cu:124-138;141-173` (SHA1728a0f34c0ef150be6e4ba481f43298753fbcc814e402f853fc0c63a3c3dfbb) and 2DCONV `2DCONV/2DConvolution.cu:108-125;128-151` (SHA5e12047cbe8cc8a21658d15df602434ee70ebf0b873d45119974fb49da63a192). These establish conditional naive-GEMM recurrence/reuse and stencil neighbor overlap. They are fixed candidate source facts; source-to-capture ELF binding remains UNRESOLVED, and static address overlap is not a runtime hit/merge count. Atlas historical "body unresolved" text is not retroactively edited: the separate current full-body qualification now establishes the declared replay body scope only.

Runtime facts use fixed Core9eedb3131937748f0492fa83aad37d3691118d70, Framework02775fd795cde5aae1480d81cee6eb481d0a08f4 and binary02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d. CH/DH intended L1/Tag/PIB/service differences are fully preserved in each `CH_DH_deliberate_option_differences`. StageI original reference roles remain original; new CH remains STAGEII_AUTHORIZED_CH. No R2/IR/EP/PQPS performance result was substituted.

## Missing observations and latency limits

2DCONV DH P0/F128 strict `latency_counters` are empty, despite explicit nonzero DRAM reads: they remain MISSING, never0. Both end before500,000 core cycles; fixed stat-print/update ordering can leave num_mfs un-folded and suppress means. CH prints means (including MRQ41 cycles in both profiles), but this does not supply the missing DH window. GEMM also prints selected means with known sample/tail limitations; no means are summed, differenced, or called a complete L2->DRAM critical-path latency.

No current counter proves time-resolved queue occupancy, credit occupancy, age of critical dependent loads, bank/row scheduling causality or cycle attribution to each retry reason. Useful read-only follow-up is controller issued read/write/activation distribution and complete typed counter reconciliation. A small approved observation experiment would be needed for request/credit occupancy histories and dependency-tagged service residence; none is started or registered here.

## Reproduction and source locator

`python3 analyze_controls.py GEMM`, `python3 analyze_controls.py 2DCONV`, then `python3 build_control_evidence.py` regenerate only this packet outputs from closed read-only sources; `python3 render_controls.py` regenerates this report. Each per-program `MATCHED_FOUR_SOURCE_DATA.json` records all four RESULT paths/SHA, UUID, raw gzip/uncompressed SHA, NATIVE_EXIT SHA, exact input, build/options, individual buckets and retry reasons. `INPUT_CONTRACT_PROJECTION.json` binds the canonical spec and full-body qualification to actual ROI. `RUNTIME_MEMCPY_AND_GEOMETRY_WITNESS.json` pins raw line positions and header geometry. `CPU_VALIDATION.json` records70 passing checks. Original source bytes, existing consumers and all active jobs remain untouched.

| Program | Identity | RESULT path | RESULT SHA256 | UUID | Raw gzip SHA256 |
| --- | --- | --- | --- | --- | --- |
| GEMM | CH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-fc0705ae3721e999-CH-P0-V1.RESULT.json | 52b200fef6a295bcf646f5020cf96c3b8359f15dfb982fbc28849e307866dce9 | f1ea9a8e-173b-4d68-8009-c96179587ddc | e01ee18a5388d0e98993389bb5ef14057317bd311c6864b78aabb0e823448d3a |
| GEMM | DH-F128 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-fc0705ae3721e999-DH-F128-V1.RESULT.json | 602e7a1061785c66c398d7eb0e8ce7170ef9e279a926069ac81e42ba90e6320c | 54b18004-c1a0-4735-aa74-116aa20e857d | 29007ccb310b4e2b8734e17191c031d3631012267882ab1b2958f79fbc1db406 |
| GEMM | DH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-fc0705ae3721e999-DH-P0-V1.RESULT.json | 1e7f73cb3b7fe40abda5b9f126a834b0c8e0ecf64cb411fb09e558e74059aea1 | af004a3c-c264-41c4-a6a4-b7a14d896c69 | d1818bd9c9cf54f1779bb5add239755e2b6b774ac006ba270105fb5caff6bf4f |
| GEMM | CH-F128 | /root/data/dtc_stage_iia_first16_20261104_v1/analysis/E2-DTC2A16-fc0705ae3721e999-CH-F128-V1.RESULT.json | 2e013c4fae2fcc47568576771c6a31b37ec72a8f4bc421dcf978ff16d6a821f2 | 6dcd9d5d-b873-4f16-8246-36d59f8d3c77 | fe7999719bd11aafe8040b8ca81856ff6e9eb7221616c3d841999b4368cd8ca1 |
| 2DCONV | CH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-d984ea5475a581ad-CH-P0-V1.RESULT.json | 438ac5fe48cc93afa6569b4af486fbb8f6dac94baf31dc927b29e101815bbe4c | 49f5e8c8-7db9-46a8-974f-8f585f5ba83d | 35b47c4844fdda6477c0f40e49341acb23e598513cd699d337644bc1e783e5fe |
| 2DCONV | DH-F128 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-d984ea5475a581ad-DH-F128-V1.RESULT.json | 1aff34c15932d48a6509b5153a19c0462dcbd3f80179f6ed19881a028e61883e | 17e5f613-18f6-4633-97c3-70a34e33b1b8 | 702b0626d74136759165f7306cf05959ed492dcde3e0fecdbffe6630c9c35119 |
| 2DCONV | DH-P0 | /root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/E2-DTCL2MLP-d984ea5475a581ad-DH-P0-V1.RESULT.json | 50b11accfa168c0221bcbfce5bda02745d5fa48bea71778d359f68ad09c5b0fc | a659b723-15eb-45cb-90f8-13857f764329 | 1f1693da4f77246203dfb41350fa071071bdfef6cc8b5fdaac6bb81ab92335e0 |
| 2DCONV | CH-F128 | /root/data/dtc_stage_iia_first16_20261104_v1/analysis/E2-DTC2A16-d984ea5475a581ad-CH-F128-V1.RESULT.json | 09958b4f6af72c0b0952d53705873cf952b21ab63dbb09da979a0dc11d8729d8 | 68f571a2-9672-42ea-9c91-9d301dd54924 | 601875c6ce4d3dfb8d704fd56ab73c116137757b2bfa61aa40e51304cec127a4 |
