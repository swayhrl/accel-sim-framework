# Round A9｜V1R1 NequIP 原生观察：PASS / MIXED_RESPONSE / STOP

Executor: Codex Lane M / node109 RTX4080. Client date: 2026-10-13. Task: AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1.

Packaging qualification: **PACKAGING_SOURCE_WHEEL_PASS**. Environment qualification: **PASS**. Numerical/edge qualification: **NATIVE_QUALIFIED**. Execution qualification: **PASS**. Scoped scientific observation: **MIXED_RESPONSE**. STOP reason: normal completion after the approved fixed observations; no unresolved execution item or automatic next GPU task.

The fixed approved official ANTLR4.9.3 sdist was built exactly once with Python3.11.17 / pip26.2.1 / setuptools84.0.0 / wheel0.48.0, without index access, dependency build isolation or dependency re-resolution. Sdist SHA256 `f224469b4168294902bb1efa80a8bf7855f24c99aef99cbefc1bcd3cce77881b`; local wheel SHA256 `d3869949aef650531d2950a0896eed26207c29a937e5afe1772654feee546423`. The pure Python tag is py3-none-any. The native declared pygrun script was checked against the original source body; isolated import passed. All82 original versions and their original hash policy were retained; only ANTLR has an explicitly derived artifact hash. The pinned Triton3.6.0 wheel came from its original official PyTorch index with an original locked hash. All82 actual wheel bytes, ANTLR/OmegaConf/Hydra imports, CPU pip check, and full source-environment pip check passed. No second unapproved sdist was installed or third-party wheel used.

The same genuine32 Si structures /2048 atoms were completed by every sample. Three fresh processes each ran12 complete Latin-rotated blocks: **144 timings,36 per condition, zero discarded or replaced samples**. Whole-group wall includes dictionary/type preparation, required transfer, fresh native neighbor graph, energy/forces/stress through the same compiled model, and CPU result availability. Per-structure values below divide the group median by32. Raw timing files retain their historical .tsv filename suffix but are comma-separated; TIMING_SAMPLES.tsv is a lossless normalized TSV. All raw bytes remain unchanged.

| Condition | Actual samples | Median whole32-frame wall (ms) | Per structure (ms) | Numeric |
|---|---:|---:|---:|---|
| N-C2 | 36 | 20.758169 | 0.648693 | PASS |
| N-G2 | 36 | 26.044453 | 0.813889 | PASS |
| N-G4 | 36 | 13.548172 | 0.423380 | PASS |
| N-G8 | 36 | 7.602214 | 0.237569 | PASS |

| Paired comparison | Median Tbase/Tcandidate | Median time reduction 1−Tcandidate/Tbase | Ratio95% bootstrap interval |
|---|---:|---:|---|
| N-C2/N-G2 | 0.796968 | -25.476% | [0.795469, 0.797475] |
| N-G2/N-G4 | 1.925497 | 48.065% | [1.922160, 1.928330] |
| N-G2/N-G8 | 3.432042 | 70.863% | [3.419052, 3.438518] |

B2 placement result: N-G2 is slower than N-C2 by about25.5% wall time, with all3 process medians in the same direction. GPU batch result: G4/G8 reduce wall relative to G2 by about48.1%/70.9%. Per-process medians and MAD, all paired block values, and all raw timings are provided. Bootstrap uses seed20261013 and10000 resamples of complete paired blocks within each fixed process stratum; intervals describe these run fluctuations. Three processes and32 structures do not support a population, MD-trajectory, cross-model or chemical-accuracy claim.

Numerics retain five trials per arm, means after double conversion, and unchanged atol=rtol=5e-5. Canary reference repeatability, original-eager→eager-OEQ→compiled-OEQ comparisons, every fresh process's full32-frame pre-timing qualification and post-timing checks passed. CPU-only raw readback recomputed132 formal field comparisons with zero failing elements. All45 five-trial output files have separately archived exact pinned-Torch double means. Across all formal checks, maximum absolute differences were atomic_energy3.78507e-5, total_energy6.13129e-5, forces5.90682e-5, stress5.33328e-7. These maxima alone are not failure criteria: the fixed allclose rule includes relative tolerance. Every condition/process had the exact same44388 directed periodic edges for the32-frame set, no cross-frame or zero-shift self edges, and maximum26 neighbors below the fixed128 capacity. All required outputs were finite. Dataset DFT labels were not used as prediction gold values.

Precision identity is the original NequIP **model_dtype=float32**, TF32 off/ieee and autocast off, with FP32 coordinates. This is not a claim of uniform FP32 storage or that every native operation is FP32. The fixed model has eight native float64 Bessel coefficients; its packaged source explicitly casts Bessel features to the model's float32 output dtype. Native float64 energy scaling/shifting and physical constants were preserved. An initial over-strict all-parameters-FP32 validator was corrected by read-only source/object verification; no parameter, weight, constant, model file, precision switch, output, graph algorithm or tolerance was altered. All intermediate assertion failures and the failed scale/shift-only diagnostic hypothesis are archived. The model's ZBL metal prefactor and force/stress derivatives establish native eV, Angstrom, eV/Angstrom and eV/Angstrom³ units.

The official batch AOT artifact uses the approved --num-frames2,8 /--num-nodes128,512 /--num-edges2,65536 bounds, OpenEquivariance atomic path, all four output types and --no-tf32. Internal official checks were retained. Compiled SHA256 `6b4ceb69ebaa7670f5bfdb06e8d0648644b467eec28983fb3d436a18f4f953f7` was common to all four conditions and all processes. Compilation logged a determinant proxy-executor fallback before freeze; it was part of this one qualified artifact, not a newly introduced formal-time fallback. Cache artifact identities before/after formal observation were unchanged, and224 post-run binary cache files were indexed and archived. Equal artifact identity does not assert identical internal instruction paths at every shape.

Auxiliary diagnostics occurred only after all main timings, three complete sweeps per condition. Median instrumented neighbor wall was10.675ms for C2 and16.295/8.269/4.219ms for G2/G4/G8; median model GPU-event intervals were7.402/3.823/2.383ms for G2/G4/G8. Fewer batches accompany shorter graph and model intervals, consistent with software organization/launch amortization. Events followed the fixed ALCHEMI current-Torch-stream dependency. Instrumented intervals are not additive critical-path weights, GPU-event elapsed is not a hardware utilization counter, and these observations do not establish SM/bandwidth causality or a new hardware mechanism. Separate thermal-throttling telemetry was not recorded; no external GPU user, cache mutation or timing-contamination event was observed. No NSYS, NCU, NVBit, Accel-Sim, training, MD or other GPU campaign ran.

| Resource | V1R1/cumulative observed or accounted value | Approved limit |
|---|---:|---:|
| New dependency download envelope | 4135896040 bytes | 5256821765 bytes |
| V1+V1R1 dependency envelope | 7469008867 bytes | 8589934592 bytes |
| New model/input downloads | 0; cumulative6423337 bytes | 12MiB cumulative |
| Directory/worktree/global-cache disk envelope after primary archive | 12852061472 bytes | 25GiB cumulative |
| Free disk after primary archive | 144235888640 bytes | at least8GiB |
| Peak sampled aggregate RSS | 7269203968 bytes (6.77GiB) | 32GiB |
| GPU shared-lock cumulative occupancy | 77.682916 seconds | 5400 seconds |
| Formal phase incl. fresh-process qualifications/postchecks/diagnostics | 29.494542 seconds | 900 seconds |
| Sampled task GPU memory peak | 460MiB | 12288MiB |
| Torch peak allocated/reserved in diagnostics | 66057728 /98566144 bytes | 12GiB |
| Primary raw payload /gzip archive | 66850400 /25516605 bytes | raw/log256MiB |

Network accounting is1MiB setup allowance plus whole-interface receive deltas across supervised phases, including TLS/SSH/other traffic, added to V1's fixed3333112827-byte conservative charge. It is an accounted envelope, not an exact application-layer download meter. CPU build workers and TorchInductor compile workers were capped at8. One-second aggregate-RSS/GPU sampling plus completed-child maxrss were recorded; initial preflight/seed-copy peak was not sampled. V1 historical resolver RAM remains unmeasured. The initial ANTLR command also wrote its standard global pip wheel cache; this was retained untouched and a1MiB disk allowance recorded. All later commands used task-local caches. GPU-lock accounting includes failed prefreeze inspection, the read-only native dtype audit, the successful scientific run, and a CUDA-hidden CPU-only mean archive import guard. That last step performed zero model evaluations and initialized no CUDA context. All task processes ended and owned locks were released.

Start commit: `06674a961632c107681ac146d735d932dde112d6`. Approved coordination commit: `bff12efa72a5d73e4358f9900229e779f5d8dc3e`. Original contract blob: `0101a33c27090ee5ef4f0f29ad5d98b492e6280b`. Draft blob: `60c50c55c1173441b4cd83cbeb166baf7e38b7e7`. Runner freeze commit/tree: `75cfac972a56b71c4b776ce87c8ab311732ec75b` /`e3a5488536c4374ab4e3b1cdbba65d80d287a72e`. Model SHA256 `63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa`; input SHA256 `c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770`. The original V1 STOP branch and its data directory remain unchanged, including original lock bytes, source archives and model/input hashes. Lane N/174, Lane T/174, C16 and AWMA remain in their previous terminal states. No coordinator merge occurred.

Node164 archive readback: **NODE164_RAW_READBACK_PASS**, 444 files and66850400 bytes, including all224 indexed binary cache files. Authority mount: `admin-wcx@10.208.130.164:/home/shared fuse.sshfs`. Destination: `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/ai_arch/nequip_static_batch_109_v1r1_20261013`. Archive SHA256 `cb40e93b801a9683bb7a1c8d6c4bbdd5e75325935c03f0da1792f103fceb73d5`; raw manifest SHA256 `b4b6520169b71c03bed69306dacd3b371ae78e8cfebef4f5370d4a4e871ce9a4`. RAW_INDEX and NODE164_PUBLICATION provide every file's size/hash/path. The final review pack is additionally saved as a closeout snapshot. Producer readback is complete; independent ChatGPT scientific review is pending. The final delivery commit is the enclosing commit of this report and is verified after push with its tree and every review-pack SHA.

**Execution complete; STOP. No automatic next GPU task or hardware promotion.**
