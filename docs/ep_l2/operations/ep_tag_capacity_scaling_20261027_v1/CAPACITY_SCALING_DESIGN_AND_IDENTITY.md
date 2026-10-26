# EP-TAG-FLOW capacity scaling design and identity

Goal: EP_L2_TAG_CAPACITY_SCALING_AND_DETACH_OPPORTUNITY_V1. Date: 2026-10-27 (Asia/Shanghai). Preparation record; application results are recorded separately and cannot be inferred from CPU qualification.

## Controlled intervention

A/B/C/D are 64 slices with (64 sets,16 ways)/(64,8)/(32,16)/(32,8). These represent 8/4/4/2 MiB of nominal Tag-addressable line coverage at 128 B/line. This is not a measurement of Tag SRAM bytes. All use the same new ELF, 32 DRAM channels and 64 memory subpartitions. Only the effective `-gpgpu_cache:dl2` set/way fields change. If a qualifying T-OFF control is selected, its only additional effective-option difference is `-gpgpu_ep_l2_ro_tag_detach` 1→0.

Physical resources remain per slice: Resident1024 + Bypass128 + WB16 =1168 Payload slots; 4 banks with292 slots/bank and1 operation/bank/cycle; descriptor512, WAD128, MSHR128. Full-application miss queue128 and ROP/DRAM timing are unchanged. CPU stress fixtures deliberately use a synthetic queue/timing profile and do not establish DRAM throughput or full-application benefit.

The Tag→Payload sidecar now sizes to logical Tag count1024/512/512/256. Physical handle bounds remain1168; handles above the logical Tag count remain legal. Tag and physical Payload bank colours agree modulo4. IPOLY32 uses its actual production polynomial; it is not IPOLY64 masked down. No detach/reuse/sector/generation protection or correctness assertion was removed.

## Source and application authority

Research Framework base is a9a778ce4c63623785858706e7977fd3153b91d4. Runtime Framework and vendor are separate producer identities. Source KEEP; accepted EP-MAIN and DTC artifacts are not modified. Current user instructions authorize this finite six-start maximum and supersede historical onboarding read-only restrictions. Each start still requires its own exact new native registration, fresh budget1 and consume-before-fork INTENT. Old global epoch2 remaining credits are not borrowed. No automatic retry or refund.

- archive_sha256: `74becb34ba74646e56109f181d4cbae61b2e94540171729754fa6b430f2547c9`
- binary_sha256: `ad4421b441d1f8efef4c956381ede5e6fd7389147d26960931e202e0a38e4b07`
- core_source_commit: `c67b332db703f09571ba6628222c77d71440e141`
- framework_source_commit: `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`
- vendor_pybind11_commit: `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`

Core tree: `2fdf60a69066a896e21d0ec1dd198977de058b75`. SourceQ SHA: `8ec80d30c6d38e5b8d3dfb1cad8c82f0d157f9d0abaa2c98ddb20034b7e01af2`. Its status is SOURCEQ_CPU_PASS_NOT_APPLICATION_ACCEPTED; it grants neither scientific acceptance nor application launch authority. `archive_sha256` denotes the actual linked static library, not core.tar.

Core branch: https://github.com/swayhrl/gpgpu-sim/tree/hrl/ep-l2-tag-capacity-scaling-20261027-v1 . Exact c67b332d remote HEAD was independently read back. The structural source is not merged into accepted Core.

## Bounded execution and interpretation

A/B/C first; at most two concurrent models. D requires an explicit Main decision from accepted B/C. At most four configuration starts. At most two distinct shrink-geometry T-OFF controls, each requiring real production TagFAIL>0 and detach_success>0 in its accepted same-source T-ON mother. Never use observer preview failures as production TagFAIL. All losses and negative results remain visible. Geometry-only outcomes cannot establish silicon area reduction because physical Payload SRAM is fixed. Same-geometry accepted T-ON/OFF is required to attribute a cycle difference to T.

Large input remains the genuine164 two-member Vector input (SHA composite138f33b61fffe99c5e9c31a5943a96edcab180e6aaaa5ed4714021249c0d2940). No local full Trace copy. Literal historical source references inside immutable input-semantic files are input provenance only; the new producer, SourceQ, frozen spec and native receipt define this run's identity.

## Completion and write-traffic boundary

PROVEN: all four configurations retain `-gpgpu_flush_l2_cache=0` and the exact input has two16,000,000B HtoD commands plus one kernel, with no DtoH/output-copy command. Accepted cycles include completion and draining the modeled in-flight work. They do not establish that all terminal dirty cache contents were written to DRAM. The existing `memory_sub_partition::flushL2` also explicitly leaves actual DRAM flush writes TODO (`src/gpgpu-sim/l2cache.cc:2589-2593`; `gpu-sim.cc:2298-2316`). This Goal does not enable or change that path.

Consequently the capacity experiment's DRAM write totals measure writes actually serviced within this accepted trace boundary. Different Tag retention capacities can change dirty-eviction timing and how much dirty state is retained at the boundary. Exact terminal dirty-state cardinality is UNKNOWN unless explicitly emitted. Do not label all extra writes capacity misses, infer a future flush cost, or claim whole-program host-visible output-transfer latency from these runs. Numeric SASS output validation remains UNKNOWN.

Relevant production evidence at Corec67b332d: Tag sidecar logical sizing `gpu-cache.h:2945`; logical index and physical handle checks `gpu-cache.h:3442-3457`; actual lifetime set/way mapping `ep-l2-reservation-lifetime.h:117-122`; dirty replacement and Payload role handling `ep-l2-ft-cache.inc:355-445`; WB counter increments only for a bound dirty replacement L2_WRBK_ACC in `l2_cache::send_write_request`, `ep-l2-ft-cache.inc:558-585`. WB_created therefore has a concrete producer meaning independent of TagFAIL. A whole-cycle decomposition among write service, bank timing, front queues and other effects remains UNKNOWN without an independent controlled service experiment.
