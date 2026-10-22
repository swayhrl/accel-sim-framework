# Project identities, authority and missing prerequisites

## EP-L2

Conditional portability is plausible for CPU trace simulation, but current Target is not a qualified execution environment. The exact latest inspected attempt is `E057_b4a7e175` (recorded COMPLETE_VALID). Its diagnostic TAGPRESSURE identity is Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`, Core `1093d2629e3d6a9130ba25b9dd119b6f3e16c092`, binary SHA256 `e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33`. The core worktree HEAD matches that Core. The existing88 MB binary was statted, not rehashed or run. Management/evaluation HEAD `7b999841d7d6b1135a32f32b30e9c7280067cf92` is a different role from Framework scientific producer identity.

The earlier MAIN61 producer is separately frozen: Core `d010911e3174a3764791183cd108fe4664ba8731`, same Framework9dd1, binary `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`, vendor pybind11 `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`. A newer diagnostic binary cannot silently replace this baseline or change historical claims.

Source `/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json` SHA256 `ac0fa2e7919e89a95357a21102083e37875c177859a2b3878966806f00779b62` contained57 actual starts, STOPPED controller and no active physical-resource leases at inspection. A legacy top-level status still mentions14/40; it is stale relative to57 and later scoped amendments. `maximum_actual_starts=null` follows specific capacity-diagnostic approvals, not a universal unlimited campaign. Preserve original T0, all57 attempts including failures, source/config/trace bindings, matrix decisions, per-endpoint and aggregate output budgets, and scope of later approvals. Do not reset to0 or reinterpret this as another40 starts.

Current Source campaign policy `E_USER_WORKSPACE_5G_20261020_V1` explicitly applies to `huangrulin-174`, its boot ID and this campaign:5 GiB residual floor,2 GiB monitoring reserve,0.2 s monitoring,3 s termination grace, all physical workspace writes. This supersedes that campaign's older48 GiB policy only. Existing Ops copy-only waivers are unrelated. A Target handoff needs explicit device/host policy rebinding and peak-write accounting, not inheritance of a convenient threshold. Registry observations are not a fresh resource PASS.

E057's command/config evidence is persisted in `evidence/EP_CURRENT_EXECUTION_REQUEST.json`. Its dwt2d kernelslist is a199 B regular file on Source overlay156, inode49298827; realpath does not resolve into `/root/data` or `/root/share`. First two trace member metadata were read (58,212,412 and95,059,024 B), without reading their content. Target has no `/workspace` and cannot open that exact path. The current list SHA `337087fedad435cd92cbd7e0f962f90d567ec9e77038fd8150977b7c6beb7164` is not automatically the registry's composite trace identity: compare each identity's defined construction before qualification.

Required bundle: exact role-selected Framework/Core/vendor commits, clean/dirty diff and generated-source identities, immutable executable plus complete ELF dependency closure, all ordered config copies and effective options, kernel/member manifests and original parser format, Python interpreter/module closure, launcher environment, qualified monitoring/decoder versions, immutable baseline counters. Target's main repo HEAD `5a8bcd63638847c0f2a0951046ec9cb2ba1994a2` is on a C16 branch and must not be checked out or borrowed for this work. New isolated project worktrees would be a future authorized step.

## DTC-L1

DTC likewise requires a distinct source/runtime/authority bundle; the old FAST64 checkout alone is insufficient. Source legacy framework worktree is `18a68dcccd795f1b6cda75504e9450d00c9cee02`. More recent AG8R1 actual attempts bind Framework `8e43c75a5e2eb60a8466084602b7df8117111e89`, Core `c8090115bd57512b1b23fca7d925301fa620c751`, runtime `/workspace/dtc-ag7-policyb-integrated-174-v1/build/accel-sim.out` SHA `1004880fd7f01f815eb55d3e23fee451d95bb90eef7ecfb19ec8fd9531b9bd6c`, and custom `libcudart.so` SHA `aee7c03cf30c2e9c2c9577165e019ce1dde929a668ca84882b5286415989cec2`. These hashes are existing receipts, not new full-binary certification here.

Static ELF inspection confirms that runtime requires libcudart.so, libzstd.so.1, libstdc++.so.6, libgcc_s.so.1 and libc.so.6, with an embedded RUNPATH to Source-private `combined-final`. Target lacks this runtime/library and the exact Gaussian/GEMM trace paths. Both kernelslists remain Source overlay156; current small-file hashes match their existing runtime identity records. Sharing `/root/data` does not expose them.

AG8R1 Source Git HEAD `c1ae89f1055af90f81836a4d7724cfe0f3876730` contains an **inactive pre-execution ledger** saying0 starts. Current on-disk attempts show two later conservative-start-consumed records:

| Attempt | UUID | Observed terminal | Meaning |
|---|---|---|---|
| AD_GEMM |940981e5-61c4-4772-83a3-50593fd1ba3a|returncode0, identity_pass=true|Evidence to join with strict acceptance; not a new acceptance decision by this study.|
| AD_Gaussian |bfa88e61-9daf-48a3-ab5a-b0251afdb68b|OWN_ATTEMPT_STREAM_OUTPUT_BOUND, identity_pass=false|Preserve failure and consumed opportunity; no automatic retry.|

The published contract preserves old AG6 consumed1, AG7 consumed3/accepted2, AG8 consumed0 and BA original0 at its publication. Its original IO admission rule has a separately published IO-warning-only user amendment; disk floor>5 GiB after2 GiB projected writes, single simulator,21600 s deadline, output/freshness/ownership/OOM safeguards remain. Never use the old inactive0 ledger to issue replacement starts, nor impose the old IO rule on an amended cohort. A current owner-signed consolidated ledger, terminal publication and queue disposition are required before any future handoff; this study does not infer global remaining budget.

Ten legacy DTC collector/monitor/waiter processes were visible on Source, including FAST64 qualification collectors. Exact AG8R1 historical lock-holder PIDs2576378 and2584485 were absent, but lock metadata absence/presence or a PID filter is not an authority-release certificate. No lock was acquired, broken or removed. No matching EP/DTC simulator appeared in the bounded process filter; this is not proof that the whole server is idle or all A-F tasks have finished.

Original authority depends on owner BA, fresh PID/start_ticks/boot identity, exact ELF/argv/cwd/source bindings, root-child/helper/ptrace evidence, progress channel credentials and complete lifecycle closure. Different Target PID namespace and path/environment invalidate blind reuse. CPU fixture qualification is not production simulator correctness. Existing SG3/FAST64/AD results, trace-parser semantics and held/problematic workload classifications must remain immutable.

## Shared environment gaps

Both system compilers report GCC/G++11.4.0 and Python3.10.12. Matching version strings do not freeze loader/libstdc++/zstd/module bytes or compile flags. Source CUDA11.8 nvcc/header exists outside login PATH; Target CUDA11.8 paths are absent. Source legacy controllers use `/scratch/root/oss-eda/oss-cad-suite/libexec/python3.11` through a bundled loader/library path; Target `/scratch` is absent. No dependency installation, package import, compilation or application smoke run was performed. Existing CPU trace simulation does not establish a requirement for, or permission to use, a physical GPU.

For each project, future qualification must either expose an owner-approved read-only trace tree with exact member identity through a legitimate mount, or explicitly authorize one content-addressed input materialization on an adequate disk. A Source SSH stream/FIFO is not a drop-in trace filesystem: seek/reopen/member lookup and failure semantics must match. Do not inspect Docker upperdirs through namespace escapes or treat a guessed `container-workspaces` path as Source data.
