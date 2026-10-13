# Round A18｜A16R1 Green Context：G1/G2 PASS，G3 STOP

Executor: Codex Lane M /node109. Date:2026-10-14, Asia/Shanghai. Start commit3dfc5826960ada62548183365d5ad7489f89ae12; coordination/approval source0374cdc901729a18f1c2098f0c38f930d0e5fe0c. Contract blob4c96cd4026523274bfbb8fc621bff8808675109d matches the approved proposal. New independent branch/worktree only; neither coordinator merge nor old A16/V1R1 edit occurred.

| Gate | Actual result |
|---|---|
| G0 | PASS; fixed asset hashes, existing environment, exact CUDA12.6 declarations/Driver exports, compiler ABI asserts and nonblocking lock verified |
| G1 | **PASS**: one request38 SM, actual partition38, stream-bound resource38 out of76 physical SM; exact returned Green handle equality |
| G2 | **PASS**: one tiny kernel,256 exact integer outputs; same stream Green owner before/after, explicit sync, previous context restored and all self-owned objects cleaned |
| G3 | **INTEROP_UNQUALIFIED_STOP**: actual Torch shim SUPPORTED=True, but no live whole-model AOT/OEQ/ALCHEMI Green ownership/dependency proof established |
| G4 | **NOT_RUN_G3_STOP**: no NequIP evaluations, outputs, trial means or directed periodic edge comparisons under quota |

The approved G1 correction was implemented directly against CUDA12.6 cuda.h, without invented ABI or dlsym casts. Compiler static asserts checked `cuStreamGetCtx_v2(CUstream,CUcontext*,CUgreenCtx*)`, `cuGreenCtxGetDevResource(CUgreenCtx,CUdevResource*,CUdevResourceType)`, and resource ABI1 size144 /SM offset96. Driver reported CUDA API version13000 while the fixed compile header CUDA_VERSION remained12060 and the existing Torch wheel remained2.10.0+cu126. Exactly one `cuDevSmResourceSplitByCount` candidate used flags0 and minCount38, computed from the fresh76-SM resource and the documented8.x min4/even guideline. API-created partition and queried stream Green owner's resource both returned38. No remainder or alternate quota was used.

Created Green handle `101687647437968`; created stream `101687649711872`; `cuStreamGetCtx_v2` returned Green handle `101687647437968` — exact equality. The additionally returned normal/primary context `101687637389248` was recorded as a borrowed handle, never treated as the Green quota proof. These opaque addresses were valid only in the isolated Driver process; all created objects were destroyed before that process exited and no address was transferred into another process's ExternalStream.

G2 used the existing nvcc to produce a small local sm89 cubin before GPU lock acquisition. Kernel `a16r1_integer_canary` ran once (grid2×1×1, block128×1×1, n256) and wrote `3*i+11`. All256 values are preserved and independently match this CPU formula. Device and pinned-host allocations were each1024 bytes. `cuCtxFromGreenCtx` created the documented converted context, `cuCtxPushCurrent` made it current, current-context resource query agreed with38 SM, and the launch plus async device→host copy used the self-owned Green stream. Explicit stream synchronization completed before reading outputs. `cuCtxPopCurrent` returned the same converted context and restored the original NULL context. Owned memory, module, stream and Green Context were released; no device reset, borrowed primary-context destruction or foreign resource destruction occurred. All recorded Driver API return codes were CUDA_SUCCESS.

G3 actual pinned runtime facts: **SUPPORTED=True** and `_CUDAGreenContext` present; early `GreenContext.create(num_sms,device_id)` plus set/pop API are exposed; modern `.Stream()` is absent; ExternalStream exists. Torch CUDA context initialization remained false during this capability inspection. No claim of “cu126 universally cannot use Green Context” is made. The create/set/pop/ExternalStream execution path was not exercised, and no AOT/OEQ/ALCHEMI GPU operation or NequIP model load was performed in G3. This is a limited capability/source inspection, not an executed whole-model interoperability test.

The [fixed v2.10 C++ implementation](https://raw.githubusercontent.com/pytorch/pytorch/v2.10.0/aten/src/ATen/cuda/CUDAGreenContext.cpp) makes the current stream a default stream on setContext and keeps the underlying context private. Installed OEQ sources access the current Torch CUDA stream; ALCHEMI's scoped Warp helper compares/binds current Torch stream handles; Warp's device/context scope and AOT custom-op loader add ownership/dependency questions. Stream-pointer equality and source accessors alone do not prove the same live Green Context for every required model operation. The completed Driver process cannot supply live addresses to the later framework process. No unsafe handle reuse, monkeypatch, hook, new extension, old-library/cache mutation or AOT replacement was used to fill that proof gap. No actual Warp/AOT escape or numerical failure was observed; none is asserted. Under the contract's explicit missing-proof STOP condition, G3 remains unqualified and this one-shot exploration ends without an automatic A16R2/R3 or additional GPU attempt.

G4 numerical qualification is **NUMERIC_UNDER_QUOTA_NOT_ESTABLISHED**. The reused OAM-S package, Si input and AOT hashes remained respectively63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa /c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770 /6b4ceb69ebaa7670f5bfdb06e8d0648644b467eec28983fb3d436a18f4f953f7. Original frame0/109 allowance, five-trial double means, atol=rtol=5e-5, model_dtype=float32 with native FP64 auxiliaries, TF32/AMP-off, complete energy/force/stress and exact directed periodic edges were preserved as an unevaluated contract. Historical V1R1 numeric PASS is not inherited as Green-path qualification. No model output or performance data was fabricated.

| Resource | Recorded value | A16R1 bound |
|---|---:|---:|
| GPU shared-lock occupancy | 1.159878s, nonblocking and released | 600s |
| Sampled GPU compute-memory peak | 0MiB; transient peak not fully captured | 4096MiB |
| Explicit self-owned device allocation | 1024 bytes; context/module overhead not separately peak-metered | 4GiB total |
| Sampled aggregate RSS peak | 653582336 bytes | 12GiB |
| Completed-child maximum RSS | 770711552 bytes | 12GiB |
| CPU build route | one local nvcc cubin+g++ probe route, workers≤4 | workers≤4 |
| New task-directory+worktree disk after primary archive | 2340563 bytes | 512MiB |
| Quota candidates /standalone kernel launches | 1 /1 | 1 /1 |
| New downloads /installs /upgrades | 0 /0 /0 | 0 /0 /0 |
| Model evaluations /formal timing blocks /speed ratios | 0 /0 /0 | conditional numeric only, no performance |

The short Driver context existed between GPU-memory telemetry samples: sampled0MiB does not prove an actual zero transient peak. The probe used1024 explicit device bytes; no OOM/budget-stop event occurred. Sampling plus completed-child maxrss were retained; preflight hash-read peak was not separately sampled. Resource wall clocks only check budgets, not model/kernel performance. Caches/TMPDIR were task-local; old A16/V1R1 model, AOT, input, environment, manifests and worktrees were read-only and checked unchanged. No NCU/NSYS/NVBit, simulator, training, MD, Qwen, old C16/AWMA/Lane task or SM sweep ran.

Node164 raw readback **NODE164_RAW_READBACK_PASS**: 28 files /190020 bytes. New destination `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/ai_arch/a16r1_greencontext_109_20261014` on `admin-wcx@10.208.130.164:/home/shared fuse.sshfs`. Archive SHA256 `47be2bab307e506dec4ec6862fd388b870a2b85251cfd3ecaa3fbbbb1ed9833f`; manifest SHA256 `9524292f7c6924417dec7786043453ad865d1386618aab0aaeabe6216a306b4c`. Raw C++/CUDA sources, local binaries, exact outputs, API statuses, ownership/cleanup and source/runtime/resource receipts are retained. A closeout snapshot of the review pack is also saved and read back. Commit/tree and every review-pack SHA are verified after push; the enclosing commit is the final execution commit.

Scientific status: **API_AND_MICROKERNEL_FEASIBILITY_ONLY / P13_RESOURCE_HEADROOM_NOT_EVALUATED**. This establishes actual38/76 stream-bound quota and one correct Driver kernel, not model numerical qualification or a hardware mechanism. Uncompleted: G3 whole-model execution-path proof and G4 two-frame numerical/edge canary. **STOP at G3; no coordinator merge, automatic R2/R3 or next GPU task.**
