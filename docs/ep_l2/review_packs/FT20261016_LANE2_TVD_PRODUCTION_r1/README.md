# Lane 2 clean/dirty TVD production candidate r1

Status: PRODUCER_READY_FOR_INDEPENDENT_VALIDATION. This replaces the module-only integration request, not the old frozen evidence packs. It is not independent qualification or an application performance result. Clean production was published first at Core 8ae60ff11ad847f28013df2873a5b7a8df7085b4 / Framework b136b395b463f1940a6a4e2365eca871e70ceefd; this new pack adds dirty and combined production coverage without modifying that pack.

Scientific authority 6c136e2a56a008695f8c8b815723bf8f1a760db9; continuation aec01450d3c527524ee09ee59242f582fafe5354. Exact R0 parent 126394be46b15f55b9756d43eb9ca9a9baae1c84; source c197c14d8292e8c2aa522711f4125ed5624b5549. Framework engineering parent b136b395b463f1940a6a4e2365eca871e70ceefd is documentation only. Executable test code/config/stimulus are all in Core; no Framework runtime or SASS trace is consumed by this fixture.

12 actual producer scenario groups and 3 expected-rejection gates pass. PRODUCTION_GATES.csv lists their scope and NOT_RUN boundaries. PRODUCER_EVENTS.log contains actual hooks/counters and named assertions from memory_sub_partition/cache_cycle/simpleDRAM/real queues. Raw paths and content hashes, including earlier failed attempts, are preserved in RAW_EVIDENCE_INDEX.json. Final binary SHA256 94638b624e5c867faf561538f26cb7ba5c649fe592711666730790ba36e5a6b0; CONFIG_IDENTITY.json and TVD_READY_MANIFEST.json bind every identity.

Apply CORE_MINIMAL.patch ONLY to exact R0 126394be46b15f55b9756d43eb9ca9a9baae1c84 using `git apply --check --unidiff-zero CORE_MINIMAL.patch` then `git apply --unidiff-zero CORE_MINIMAL.patch`. This zero-context patch requires that option. PATCH_CHECK.json records private-index apply and exact resulting blob equality. Do not stack old CORE_MODULE.patch or the earlier clean production patch onto it. Lane 1 resolves integration with any separate R1/RO patch and freezes a new candidate; do not change the frozen R0 binary.

Reproduce in an isolated Core tree with an available Lane 5 build lease (2 jobs used here):

```sh
cmake -S . -B build/ft_lane2_r2 -DCMAKE_BUILD_TYPE=Release -DCUDAToolkit_ROOT=/usr/local/cuda-11.8
cmake --build build/ft_lane2_r2 --target ep_l2_tvd_production -j2
build/ft_lane2_r2/ep_l2_tvd_production configs/tested-cfgs/SM7_QV100/gpgpusim.config tests/ep_l2/ft_wbuf.config
```

Run the same command with each final argument `--reject_static_tvd`, `--reject_old_tvd`, `--reject_live_epoch` in a core-dump-disabled child: expect SIGABRT and corresponding marker in NEGATIVE_GATES.json, not a zero exit. No assertions were disabled or removed. CMake Release uses the repository's -O3/-g3 flags and assertions remain enabled. Warnings inherited from simulator polymorphic destructors remain; tested allocation/deletion is the concrete type.

Both new flags default OFF: `-gpgpu_ep_l2_tvd_clean` and `-gpgpu_ep_l2_tvd_dirty`. Supported/tested mode is unified FT2 with WAD128 and WBUF16. The old unsupported `-gpgpu_ep_l2_feature_tvd` placeholder stays OFF. TVD_STATE_AND_SECTOR_CONTRACT.md, METRIC_CONTRACT.md and TVD_METADATA_COST.md define the implemented boundaries.

Next consumer: Lane 1 final public integration; Lane 5 incremental independent validation/parser update, followed by separately authorized matched experiments. Existing R0 B16/U_WB16 qualification and formal runs continue independently. Lane 2 formal workloads=0, active runs=[], build leases released; registry observation is a timestamped snapshot, not a scheduler lease.
