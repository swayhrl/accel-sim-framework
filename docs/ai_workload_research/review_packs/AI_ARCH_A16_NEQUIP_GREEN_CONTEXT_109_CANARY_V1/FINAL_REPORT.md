# AI-ARCH Round A16｜Green Context canary：G1 STOP

Executor: Lane M / node109. Approval dated2026-10-13; runtime UTC `2026-10-13T16:09:05.630796+00:00`, Asia/Shanghai UTC+08:00. Fixed start56c7901b452138d2beeed754a401a84d8db091e9; contract blob4e00b0b3f3857cc11ee5b41771fc918fd3644153. New independent branch/worktree only. Old V1R1 worktree remains clean at1f69559df4f51290589de72876f36a756c5439f0, and all three reused model/input/AOT hashes were checked before and after this probe.

**STOP at the fixed G1 named-entrypoint requirement.** The contract requires `cuStreamGetDevResource`; it is absent from the existing CUDA12.6 cuda.h, installed bindings declarations, and Driver580.178.04 exported symbols. A single bounded CPU-built Driver probe then confirmed this through the actual `cuGetProcAddress` API using the frozen header CUDA_VERSION12060. The lookup API returned CUDA_SUCCESS, but its separate query status was1 (`CU_GET_PROC_ADDRESS_SYMBOL_NOT_FOUND`) and the returned function pointer wasNULL. API call success is not symbol-resolution success. The frozen entrypoint cannot safely be invoked; no ABI was guessed and no alternative query chain was substituted.

The [official CUDA12.6 Green Context API](https://docs.nvidia.com/cuda/archive/12.6.0/cuda-driver-api/group__CUDA__GREEN__CONTEXTS.html) documents the other resource/context/stream APIs, but does not list this named stream-resource getter. Existing `cuStreamGetCtx_v2`, `cuStreamGetGreenCtx` and `cuGreenCtxGetDevResource` are potential ingredients for a separately reviewed proof chain. Their availability was recorded; that alternative was not executed or admitted under this fixed contract. This result establishes a **source/interface-contract gap**, not that every Green Context API or the device's quota creation is unsupported.

| Gate | Actual qualification and execution |
|---|---|
| G0 | Model/input/AOT byte identities, existing toolchain, GPU UUID/SM89 and nonblocking shared lock passed |
| G1 | **STOP_REQUIRED_STREAM_RESOURCE_ENTRYPOINT_UNAVAILABLE**; cuInit/device attributes/device resource query passed, required getter unresolved |
| G2 | NOT_RUN_G1_STOP; zero small-kernel launches, no green stream/context |
| G3 | NOT_RUN_G1_STOP; runtime torch SUPPORTED not queried, AOT/OEQ/ALCHEMI not imported or evaluated |
| G4 | NOT_RUN_G1_STOP; NUMERIC_UNDER_QUOTA_NOT_ESTABLISHED, no model outputs or numerical comparisons |

Device query returned **76 physical SMs** and the unsplit device resource reported76 SMs. **Actual allocated Green SM quota is NULL / not established**, not76 and not0. No partition candidate was attempted or allocated, no resource descriptor/green context/stream created, and no kernel ran. There was consequently no self-owned GPU context or stream to destroy, no thread-context switch, no device reset, and no external resource destruction.

Scientific status: **API_FEASIBILITY_ONLY / P13_RESOURCE_HEADROOM_NOT_EVALUATED**. Numerical tolerances remain five-trial double means with atol=rtol=5e-5; original NequIP model_dtype=float32, TF32-off/autocast-off and native FP64 auxiliary values remain unchanged. Those conditions were not evaluated under a Green quota and historical V1R1 qualification is not copied into G4. Canary frame allowance remains[0,109], but neither frame was evaluated. Formal timing samples, model evaluations, GPU kernels, performance event/latency measurements and performance ratios are all zero. No formal performance, resource-scaling or hardware-mechanism admission exists.

| Resource | Recorded usage | A16 bound |
|---|---:|---:|
| Shared-lock occupancy | 0.301507 seconds, nonblocking acquisition and release | 600 seconds |
| Sampled task GPU compute-memory peak | 0MiB | 4096MiB |
| Peak sampled aggregate RSS | 66125824 bytes | 12GiB |
| Maximum completed-child maxrss | 74092544 bytes | 12GiB |
| Source build | one g++ route, one sequential Driver probe | at most4 workers |
| New task-directory +worktree bytes after primary archive | 2016143 bytes | 512MiB |
| Downloads /installs /toolchain upgrades | 0 /0 /0 | 0 |
| Quota partitions /green contexts /streams /kernels | 0 /0 /0 /0 | one permitted candidate, not exercised |

Resource wall clocks are budget telemetry, not workload performance data. Sampled GPU peak0 is not an unsampled allocation meter; the probe never created a context/stream, allocated GPU memory or launched a kernel. Preflight CPU hash-read peak was not separately sampled. The C++ executable, CUDA header/source identities, exported-symbol subset, all actual API return codes/query status, stdout/stderr and resource receipts are archived. No model/AOT recompile, PyTorch extension, dependency install, profiler, simulator, training, MD, Qwen, AWMA/C16 or other Lane activity occurred. Old model/input/AOT/env/source caches and scientific records were not changed.

Node164 readback **NODE164_RAW_READBACK_PASS**: 17 files, 89684 bytes. Destination `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/ai_arch/a16_greencontext_109_20261014` on `admin-wcx@10.208.130.164:/home/shared fuse.sshfs`. Archive SHA256 `f27bafac8e9e72a03120139154d91736b9818a3f4a3022379fd2fa9b6d70e01c`; payload manifest SHA256 `774bd18a0d8805c95e77afb3567bb647b252087628ab54e7d3b8236016928bc4`. The report/review pack is also copied as a new closeout snapshot. Producer checksum readback is complete; independent scientific review remains separate.

Uncompleted: stream-bound actual quota proof; G2 microkernel semantics; G3 runtime framework ownership/stream compatibility; G4 numerical/edge canary. A future contract may correct the missing named API with an explicitly reviewed documented proof chain, but this run does not authorize or begin that follow-up. Final commit/tree and all small-file hashes are verified after push; the enclosing commit is the execution delivery commit. **STOP; no coordinator merge or automatic next GPU task.**
