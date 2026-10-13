# A24 GS-Scale node109 CPU platform preflight V1

## Identity and decision

- Lane M / node109; `CPU_METADATA_ONLY`; no runtime, numerical, training or performance qualification.
- Branch: `hrl/aiarch-a24-gsscale-109-cpu-platform-gate-v1`.
- Fixed start: `47acc712aff232bbb4685746ea68e9cb12bcc0a9`.
- Fixed start tree: `ea1ebf4e11528608e39eb679dd2bab88e5d419a7`.
- Contract blob: `f6f2f1f9bfa8691449559d4f85f89142d14ba149`.
- Contract SHA256: `9a6c7c4e8a0ed52902a5448fce1e09b402a5d64b81a11e899aa4c7207ba90700`.
- The fixed task contract and linked unattended operations plan were read in full.
- Author source: `SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`.
- Decision: `PLATFORM_VERSION_GAP` + `SOURCE_ONLY_UNVERIFIED`; existing Lane M environment is `PLATFORM_INCOMPATIBLE_AS_IS` with the author installation entry.
- Intel vendor prerequisite: **PASS**. Isolated future environment: **PLATFORM_CONDITIONAL**, not installation PASS.
- No observed current free-space/RAM scarcity; full-scene resource admission remains unqualified.

## Observed facts versus requirements

| node109 static observation | Fixed author source / contract requirement | Still requires future lawful validation |
|---|---|---|
| GenuineIntel, family 6, Core i7-13700; x86_64; 1 socket / 16 cores / 24 logical CPUs | README states Intel-only support and recommends CUDA 12.x | CPU vendor matches; exact IPEX wheel support for this hybrid client CPU is not proved |
| Common online-CPU flags: SSE3 (`pni`), SSSE3, AVX, AVX2, FMA, AVX-VNNI; no AVX512F/BW/VL | CPUAdam uses SSE control intrinsics, Torch C++ headers and OpenMP; no AVX-512 minimum established by these source files | AVX2 presence alone does not prove IPEX/CPUAdam binary or numerical compatibility |
| Physical RAM [62,63) GiB; available [60,61) GiB; swap [7,8) GiB | Host offloading retains Gaussian parameters and optimizer state in RAM | Scene Gaussian growth, optimizer state, image buffers and peak RSS must be measured; available memory is a snapshot |
| Workspace and existing environment share one filesystem: capacity [936,937) GiB, available [134,135) GiB | Future isolated environment, real images/COLMAP, intermediates and checkpoints require separate reservation | Do not count the two paths as two disks; final dataset/archive/unpack sizes are unknown |
| Ubuntu 24.04.4 LTS, glibc 2.39; GCC/G++ 13.3.0; libgomp1 14.2.0 package metadata | CPUAdam setup uses C++17, `-fopenmp`, `-pthread`; Python/Torch/pybind headers and OpenMP link required | Actual compiler, libstdc++/Torch C++ ABI and loader compatibility not compiled or tested |
| System Python 3.12.3; old Lane M Python 3.11.17; no distro Python 3.10/dev package in queried package records | install.sh creates Python 3.10 | Absence in these records is not absence across all possible environments; do not modify existing interpreters |
| Lane M torch 2.10.0+cu126; torchvision, IPEX, gsplat and CPUAdam absent from that environment's distribution records | install.sh pins torch 2.2.0+cu121, torchvision 0.17.0+cu121 and IPEX 2.2.0 | A separate author-version environment is required; no downgrade or in-place repair of NequIP |
| Lane M NumPy 2.4.6, setuptools 84.0.0, pybind11 3.1.0, ninja 1.13.2 | examples/requirements.txt requires NumPy <2.0.0; other packages include unfrozen versions and two fixed Git dependencies | Existing NumPy directly conflicts; resolve and freeze all future dependencies before install; no wheel/build availability tested |
| Installed toolkit file/distro metadata: CUDA SDK 12.6.3; existing loaded-module version file: driver 580.178.04 | Author install uses Torch cu121; contract distinguishes paper CUDA 12.4 / Torch 2.2 / gsplat 1.5.0 | File metadata is not CUDA initialization, driver-runtime compatibility or GPU capability proof; SDK manifest's bundled-driver 560.35.05 is not the active driver |

All Python package facts above are restricted to the existing Lane M environment, not a global environment inventory.
The collector used system `python3 -S`, standard-library `importlib.metadata.distributions(path=...)`, interpreter `-S --version`, and read-only OS/package/version files.
It did not activate/import the old environment; bytecode writing was disabled. Forbidden framework modules in collector `sys.modules`: empty.
No environment-variable dump, host address, username, private filesystem path or raw mount listing is published.

## Source qualification and installation risks

Fixed source reads: [README](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/README.md), [install.sh](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/install.sh), [CPUAdam implementation](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/cpu_adam/src/cpu_adam.cpp).
Supporting reads: [CPUAdam setup](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/cpu_adam/setup.py), [requirements](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/requirements.txt), [gsplat setup](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/setup.py).
These are `CODE_ONLY` requirements, not observations of a successful build. No author setup script was executed.

- CPUAdam sets denormal/flush-to-zero modes and uses float accessors and explicit OpenMP loops. Several functions call `omp_set_num_threads(64)`; setting `OMP_NUM_THREADS=1` cannot establish a one-worker bound for future execution of those functions.
- Its setup uses Torch CppExtension, Python/pybind headers and OpenMP compilation/linking. Installed GCC/libgomp versions do not establish matching Python 3.10 or Torch 2.2 extension ABI.
- The main gsplat setup normally imports Torch and builds CUDAExtension, defaults MAX_JOBS to 10, and uses CUDA fast-math. Running it would cross this task's boundary; it was only read as text.
- The source install entry and paper-reported stack are distinct identities. The paper versions above come from the approved task contract, not a new paper/runtime verification in this task.
- Intel-only alternative implementation is **not required by observed CPU vendor**. Any replacement of IPEX/CPUAdam is a new implementation/scientific identity requiring a separate contract, not an authorized fallback.
- Feasibility inference: future isolation can preserve NequIP/C16/AWMA, but matching author packages, wheel ABI, CPU extension build, OpenMP scheduling and full runtime remain `NOT_VERIFIED`.
- Reserve future disk/RAM before installation: environment + archive + unpacked scene + intermediates + checkpoints with headroom; host-state peak + image buffers within an explicit RAM cap. This report does not assert an author minimum footprint.

## One future scientific comparison — proposal only

`CONDITIONAL_GO_FOR_PROPOSAL`, not permission to execute: a single real **Mill-19 Rubble** scene could compare fixed-author GS-Scale optimized host offloading against the same-source GPU-only trainer when it fits (OOM is a capacity outcome, not an invented timing).
Freeze actual image/COLMAP SHA, camera/train-test identities, author downsampling 4, initialization, Gaussian growth, seed and quality target. Require complete energy-independent training wall/time-to-quality, PSNR/SSIM/LPIPS, peak RAM/HBM and state/transfer evidence; do not infer a hardware mechanism from static metadata.
The naive host-offload script alone is not a sufficient strong baseline. An optimizer/schedule or quality mismatch must be exposed rather than claimed numerically equivalent.

Future budget proposal, **not used or approved here**: one real-scene archive plus author merged COLMAP, provisionally <=25 GiB download; <=60 GiB total new disk; <=48 GiB RAM; separately declared OpenMP thread allowance addressing the hardcoded 64 threads.
GPU proposal: one independently authorized native qualification/comparison window <=2 hours, model/data identity frozen first, with device-memory and shared-lock limits in its new contract. No guarantee that full training fits that window; if sizes or completion exceed caps, STOP/rebudget before download or execution, never reduce the scientific workload to manufacture completion.
If input identity, matching isolated software, resource envelope or equal-quality comparison cannot be established, the proposed native comparison is **NO-GO**. This task admits no hardware headroom or speedup.

## UNATTENDED_20H_CLOSEOUT

- Start: 2026-10-14 01:48:09 +08:00 (Goal creation); CPU snapshot: 01:51:57 +08:00.
- Report preparation completed: 2026-10-14T01:54:52+08:00; the same short session proceeds only through Git publication/readback, well within the one-hour deadline. Twenty hours is an unattended availability window, not a waiting requirement.
- Research status: static facts **PASS**, existing-stack compatibility **NO-GO / PLATFORM_VERSION_GAP**, future isolated runtime **SOURCE_ONLY_UNVERIFIED**; task **STOP** after publication.
- CPU collector: one worker/thread, no parallel scientific workers; measured collector RSS 23,372 KiB; small child-command high-water 23,372 KiB. Git packaging uses one pack thread; initial fetch RSS was not separately measured.
- New worktree before report: 1,868,922 logical bytes; private receipt directory: 11,909 bytes. With report/Git publication overhead total new task files remain below 4 MiB and the 30 MiB cap; no large source clone.
- CUDA initialization, Torch import, GPU operations, GPU lock acquisition/hold, training, compilation, installation, and model/data/dependency download: **all zero**. Only approved Git fetch/push and fixed small author-source text reads were performed.
- Existing A16R1 `6953ac1690b7a905b6000833a879f9164c7c9e43` and V1R1 `1f69559df4f51290589de72876f36a756c5439f0` retained clean HEADs; their historical STOP/runtime conclusions were not reopened. AWMA/C16 were not altered or run.
- Raw metadata remains private and untracked; private receipt SHA256: `5b88e21d0bd64a6286047f3fcc8ea32a010dba0bb0ed4cbb20ecc82899e577996`.
- Sole deliverable: this sanitized Markdown, <=180 lines. No other Lane outputs, coordination merges, background task, new environment or successor Goal.
- Publication identity: this report's enclosing branch commit and tree, plus its Git blob and SHA256, are bound by remote push/fetch-back. Exact final hashes are returned in the execution closeout; they are not self-referentially embedded in this file.
- Remote verification procedure: compare pushed branch HEAD with fetched HEAD, exact commit/tree/report blob and report SHA256; branch must be ahead=0 / behind=0 after fetch. Recheck both old worktree HEADs and cleanliness before STOP.
- Remaining work: future input lock, full isolated dependency lock/install, compiler/ABI/IPEX/CPUAdam qualification and native numerical/training/resource validation all require a new authorized task. None was attempted here.
