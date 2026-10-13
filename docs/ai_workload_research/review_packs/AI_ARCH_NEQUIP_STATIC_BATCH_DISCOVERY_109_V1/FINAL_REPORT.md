# Round A8 执行结果：ENVIRONMENT_BLOCKED / STOP

Task: `AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1`. Executor: Codex / Lane N-109 / independent window. Client date: 2026-10-13.

The approved V1 execution stopped at its environment wheel-availability gate. The single controlled resolution locked 82 distributions, including `antlr4-python3-runtime==4.9.3` via the Hydra/OmegaConf dependency graph. The wheel-only download failed on that exact version. Its version-specific PyPI metadata lists one sdist and zero wheels. V1 section3 explicitly requires STOP for an unavailable leaf wheel and prohibits another version scan. No source-only leaf installation, package upgrade, alternative environment route, or model fallback was attempted.

The fixed approval record overrides the contract's historical pending-approval label. Execution branch HEAD was fetched and matched `cb1081328303f2655cbf1a3f3042cc01abe83b2c`; contract blob `0101a33c27090ee5ef4f0f29ad5d98b492e6280b` matches the approval. An independent worktree was created. The original worktree remains clean at `bd988aeb570708e5a41bab45433e9e49eac53c9a`. No reset, coordinator merge, old experiment edit, or new GPU task occurred.

| Condition | Actual result | Timing samples | Numeric qualification |
|---|---|---:|---|
| N-C2 | NOT_RUN_ENVIRONMENT_STOP | 0 | NOT_RUN |
| N-G2 | NOT_RUN_ENVIRONMENT_STOP | 0 | NOT_RUN |
| N-G4 | NOT_RUN_ENVIRONMENT_STOP | 0 | NOT_RUN |
| N-G8 | NOT_RUN_ENVIRONMENT_STOP | 0 | NOT_RUN |

No compiled product or runtime energy/force/stress outputs exist. Native FP32, units, model outputs, geometry, edge multisets, reference repeatability, and canary qualification remain untested. There are zero fresh formal processes, zero blocks, and zero timing/diagnostic samples. Empty TSVs contain headers only; they represent no observations. Scientific status is `NOT_EVALUATED`, not a positive, negative, or unresolved timing response. No performance ranking or hardware-mechanism claim is qualified.

Legal preparation evidence includes node109 IP and RTX4080/SM89 identity, driver580.178.04, existing CUDA12.6/nvcc12.6.85, nonblocking shared-lock availability checks, isolated Python3.11.17, the one complete resolved version/hash lock, acquisition provenance, model ZIP members and text metadata, and the wheel failure. The fixed model MD5 is `399a98bf36fc4550bc85d48f35451c6c`; independently calculated SHA256 is `63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa`. Input bytes784661 and SHA256 `c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770` match. Fixed canary and32-frame indices are preserved in INPUT_MANIFEST. Packaged source versions are recorded separately from proposed installed versions; no loaded model object was inspected. A task-local DNS transport override fetched the same fixed input URL with normal TLS verification and exact byte hash. The official OEQ CMake LibTorch2.10 CPU dependency was prefetched and hashed; no source build used it.

| Resource | Observed / accounted usage | V1 ceiling |
|---|---:|---:|
| Model + geometry download | 6423337 bytes (6.13MiB) | 12MiB |
| Dependency download envelope | 3333112827 bytes (3.11GiB) | 8GiB |
| Task data directory after primary archive | 1249667059 bytes | 25GiB |
| Free disk after primary archive | 155963666432 bytes | keep8GiB |
| Supervised wheel-step peak aggregate RSS | 97128448 bytes (92.6MiB) | 32GiB |
| Source-build CPU workers used | 0 | 8 |
| GPU execution-lock occupancy | 0 seconds | 5400 seconds |
| Formal observation | 0 seconds | 900 seconds |
| Task GPU peak | 0MiB; no CUDA initialization | 12288MiB |
| Raw/log bytes before packaging | 276976 bytes | 256MiB |
| Primary raw payload / gzip archive | 11209866 /9440774 bytes | 256MiB |

Dependency accounting includes observed active-resolver TCP receive counters, a conservative512MiB allowance for previous setup/unobserved small connections, subsequent whole-interface receives, and1MiB final metadata allowance. It also counts TLS/SSH and unrelated receives. This is an accounted conservative envelope, not an exact application-layer transfer counter. Resolver peak RAM was not measured; the supervised wheel-step peak must not be presented as the whole-task RAM peak. Resolution took21m41s; the supervised failed wheel step took5.07s. Two brief nonblocking lock probes were not timed; no CUDA happened while probing. The execution lock was never held for build or evaluation.

The primary node164 archive was read back through the established SSHFS authority mount: `admin-wcx@10.208.130.164:/home/shared fuse.sshfs`. All56 manifest entries, 11209866 bytes, passed size/SHA checks. Archive SHA256 is `c20621864e07e0f0d9fcddd1fff4ffe232e3c8c83613e67ff7f76ad9592a67a9`; payload manifest SHA256 is `54d6b96b50aa114b150c2b69c931e5cd380c9bfa8f086fab2ce6bb07dcc0f7cd`. Destination: `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/ai_arch/nequip_static_batch_109_v1_20261013_stop_20261013T111728Z`. Initial extraction hit SSHFS ownership restrictions; the packaging-only repair used no-same-owner/no-same-permissions without changing archive bytes or scientific assets. NODE164_PUBLICATION and RAW_INDEX provide exact paths and hashes.

Uncompleted: full isolated core installation; loaded model dtype/cutoff/type/output/unit identity; native geometry/duplicates and exact edges; official compile; reference/eager-OEQ/compiled canary; all four conditions in3 fresh processes with144 timings; post-timing numeric checks and auxiliary diagnostics. Prepared GPU/canary/observation code is explicitly unexecuted and has no native qualification. All original174 Lane N/Lane T, C16 and AWMA terminal states remain STOP. The task ends at this contract-defined STOP and grants no automatic retry or next-GPU authorization.

Preparation source commit: `860037b6882f16162e88f280e17c575414379b6e`. The final execution delivery commit is the enclosing Git commit of this report; publication verifies that commit/tree and every review-pack byte hash after push.
