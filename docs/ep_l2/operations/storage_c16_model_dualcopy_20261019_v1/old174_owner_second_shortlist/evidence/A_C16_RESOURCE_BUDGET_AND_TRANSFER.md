# C16 Resource, Budget, and Transfer Policy

## 1. Principle

AutoDL GPU time is reserved for tasks that require a real GPU: native inference, nsys census, bounded NCU, bounded NVBit. Model download, parser development, estimator development, asset hashing, input preparation, most post-processing, and most report generation belong on the local server before/after rental.

## 2. Local pre-rental gate

Recommended gate: `C16_LOCAL_GPU_PACKAGE_READY`.

Before rental, aim to have:
- model assets already present locally;
- per-file SHA256 and immutable revision receipts;
- wheelhouse / requirements lock / bootstrap scripts;
- unified native runner and nsys/ncu/nvbit wrappers;
- frozen input corpus + token receipts;
- frozen scenario matrix;
- object-map and offline parser fixtures;
- sampling V2 estimator fixtures;
- transfer manifest and expected hashes.

If one noncritical Wave-2 model asset is missing, Wave-1 may still start if all Wave-1 assets are complete.

## 3. AutoDL instance

Preferred first instance: single exclusive 80GB-class GPU when available, CPU >=16 cores, RAM >=64GiB (128GiB preferred), local work disk >=300GiB (500GiB preferred for trace-heavy work).

The exact GPU is recorded, not assumed. Do not use native A100/other-GPU timing as C12/C13 simulated timing.

## 4. Inline qualification

Qualification is not a separate long campaign. Start with the smallest Qwen2.5-0.5B S0 canary:

- G0 native correctness → immediately permits native baseline.
- G1 nsys/NVTX → immediately permits lightweight census.
- G2 NCU → permits only metrics that pass availability/scope checks.
- G3 NVBit → permits only bounded target capture.

Failure of G2/G3 does not block G1 results.

## 5. Native baseline/profile budget

Per deployment/scenario:
- 2 warmups;
- 3 measured unprofiled repeats;
- if CV exceeds the predeclared engineering threshold, increase at most to 5 measured repeats and retain all measurements;
- one nsys census pass after native baseline;
- separate NCU/NVBit passes only for frozen representative targets.

Do not add repeated profiling simply because the GPU is idle.

## 6. NCU budget

Start with a compact metric set focused on L1/TEX, L2, DRAM, throughput and a small set of stall metrics that are actually available on the rented GPU. Record replay/cache-control behavior.

Do not invoke broad `--set full` over whole models. One representative target at a time unless tool semantics explicitly support safe batching.

## 7. NVBit / trace budget

First-wave policy:
- initial target count: normally 4–6 windows per deployment, fewer if enough information is obtained;
- hard per-window bound: stop at 4GiB raw output OR 20 minutes, whichever occurs first;
- first-wave raw trace total: <=64GiB across all deployments;
- one active capture process per GPU;
- target identity must be revalidated in the capture run.

When a limit is reached, status is `BOUNDED_PARTIAL`; preserve the receipt and move on. Do not silently extend.

## 8. GPU-hour planning

Initial planning envelope: up to 24 GPU-instance-hours for Wave-1 qualification/census/counters/limited traces. This is a planning cap, not a requirement to consume all hours. Wave-2 expansion should be authorized only after Wave-1 produces useful cross-model/catalog evidence.

Track separately:
- instance rental wall time;
- GPU-active measurement time;
- model load/JIT time;
- idle/debug time;
- transfer time;
- failed/retry time.

## 9. Data placement

Local server canonical roots should be versioned in the A plan. Suggested logical layout:

`/workspace/c16_assets/{models,inputs,wheelhouse,gpu_package}`
`/workspace/c16_exchange/{native_catalogs,counters,traces,imports}`

AutoDL suggested work root:

`/root/autodl-tmp/c16/{models,env,code,inputs,runs,raw}`

Do not assume these exact paths exist; record actual paths in transfer receipts.

## 10. Transfer

Use resumable `rsync -avP --partial` over SSH when available. After transfer, verify SHA256 against the local manifest before any scientific run.

Large raw results should be rsynced back to local storage as soon as a bounded capture finishes. Git stores only `RAW_INDEX.tsv` and small summaries.

For every transfer record:
- source host/path;
- destination host/path;
- file/dir identity;
- byte count;
- SHA256 for immutable files or manifest hash for directory bundles;
- transfer start/end;
- verify status.

## 11. Cost accounting

Every lane reports its own cost. A integrates:

`prepare + metadata + download + upload + environment + model_load + warmup + baseline + profiling + capture + parse + retry + transfer + storage`.

Unknown is `NA`, never zero. Do not claim a 10x/100x cost reduction without a measured or clearly estimated baseline using the same accounting boundary.

## 12. Stop rules

Stop or skip a task when:
- asset identity/hash fails;
- GPU memory cannot support the frozen scenario and reducing the scenario would alter the question;
- profiler causes unacceptable perturbation and cannot be reduced within bounded debugging;
- target identity changes between census and capture and cannot be remapped safely;
- disk/raw trace approaches hard bound;
- tool permission/compatibility prevents the requested evidence tier.

A capability failure is not a scientific negative result.