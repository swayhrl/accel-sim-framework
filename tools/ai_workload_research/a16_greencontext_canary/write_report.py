import pathlib,os,json,hashlib,subprocess
root=pathlib.Path(os.environ['TASK_DATA']);p=pathlib.Path('docs/ai_workload_research/review_packs/AI_ARCH_A16_NEQUIP_GREEN_CONTEXT_109_CANARY_V1');api=json.loads((p/'API_QUOTA_RECEIPT.json').read_text());u=json.loads((p/'RESOURCE_USAGE.json').read_text());pub=json.loads((p/'NODE164_PUBLICATION.json').read_text());identity=json.loads((p/'RUN_IDENTITY.json').read_text())
u['task_directory_bytes_after_primary_archive']=int(subprocess.check_output(['du','-sb',str(root)],text=True).split()[0]);u['worktree_bytes']=int(subprocess.check_output(['du','-sb',str(pathlib.Path.cwd())],text=True).split()[0]);u['new_disk_accounted_bytes']=u['task_directory_bytes_after_primary_archive']+u['worktree_bytes'];assert u['new_disk_accounted_bytes']<512*2**20;(p/'RESOURCE_USAGE.json').write_text(json.dumps(u,indent=2)+'\n',encoding='utf-8')
report=f'''# AI-ARCH Round A16｜Green Context canary：G1 STOP

Executor: Lane M / node109. Approval dated2026-10-13; runtime UTC `{identity['execution_UTC']}`, Asia/Shanghai UTC+08:00. Fixed start56c7901b452138d2beeed754a401a84d8db091e9; contract blob4e00b0b3f3857cc11ee5b41771fc918fd3644153. New independent branch/worktree only. Old V1R1 worktree remains clean at1f69559df4f51290589de72876f36a756c5439f0, and all three reused model/input/AOT hashes were checked before and after this probe.

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
| Shared-lock occupancy | {u['gpu_lock_seconds']:.6f} seconds, nonblocking acquisition and release | 600 seconds |
| Sampled task GPU compute-memory peak | {u['peak_sampled_gpu_mib']}MiB | 4096MiB |
| Peak sampled aggregate RSS | {u['peak_sampled_aggregate_RSS_bytes']} bytes | 12GiB |
| Maximum completed-child maxrss | {u['max_completed_child_maxrss_bytes']} bytes | 12GiB |
| Source build | one g++ route, one sequential Driver probe | at most4 workers |
| New task-directory +worktree bytes after primary archive | {u['new_disk_accounted_bytes']} bytes | 512MiB |
| Downloads /installs /toolchain upgrades | 0 /0 /0 | 0 |
| Quota partitions /green contexts /streams /kernels | 0 /0 /0 /0 | one permitted candidate, not exercised |

Resource wall clocks are budget telemetry, not workload performance data. Sampled GPU peak0 is not an unsampled allocation meter; the probe never created a context/stream, allocated GPU memory or launched a kernel. Preflight CPU hash-read peak was not separately sampled. The C++ executable, CUDA header/source identities, exported-symbol subset, all actual API return codes/query status, stdout/stderr and resource receipts are archived. No model/AOT recompile, PyTorch extension, dependency install, profiler, simulator, training, MD, Qwen, AWMA/C16 or other Lane activity occurred. Old model/input/AOT/env/source caches and scientific records were not changed.

Node164 readback **{pub['status']}**: {pub['manifest_items']} files, {pub['payload_bytes']} bytes. Destination `{pub['destination']}` on `{pub['authority_mount']}`. Archive SHA256 `{pub['archive_sha256']}`; payload manifest SHA256 `{pub['manifest_sha256']}`. The report/review pack is also copied as a new closeout snapshot. Producer checksum readback is complete; independent scientific review remains separate.

Uncompleted: stream-bound actual quota proof; G2 microkernel semantics; G3 runtime framework ownership/stream compatibility; G4 numerical/edge canary. A future contract may correct the missing named API with an explicitly reviewed documented proof chain, but this run does not authorize or begin that follow-up. Final commit/tree and all small-file hashes are verified after push; the enclosing commit is the execution delivery commit. **STOP; no coordinator merge or automatic next GPU task.**
'''
(p/'FINAL_REPORT.md').write_text(report,encoding='utf-8');s=(p/'FINAL_REPORT.md').read_text(encoding='utf-8');assert '\ufffd' not in s and '???' not in s;print('REPORT_SHA256',hashlib.sha256((p/'FINAL_REPORT.md').read_bytes()).hexdigest());print('DISK_ACCOUNTED_BYTES',u['new_disk_accounted_bytes'])
