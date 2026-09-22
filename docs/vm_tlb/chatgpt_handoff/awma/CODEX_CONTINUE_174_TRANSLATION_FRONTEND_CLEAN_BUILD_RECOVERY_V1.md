# CODEX CONTINUATION GOAL — 174 Translation Frontend V1 Clean Build Recovery

Date: 2026-09-22

Mode:

`GOAL MODE / ENGINEERING-RECOVERY-AND-CONTINUE / solve-and-continue`

Node:

`174-new`

Scientific stage remains:

`AWMA_TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_V1`

This is NOT a new scientific stage.

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

Read first:

1. `CURRENT_STATE.md`
2. `EXECUTION_PRIORITY_POLICY_V5.md`
3. `REVIEW_174_HITPATH_ATTRIBUTION_V1_2026-09-22.md`
4. `CODEX_NEXT_STAGE_174_TRANSLATION_FRONTEND_PIPELINING_V1.md`
5. `TRANSLATION_FRONTEND_V1_CUDA_TOOLCHAIN_RECOVERY_ADDENDUM_2026-09-22.md`
6. this continuation Goal

Recommended execution branch:

`hrl/awma-174-translation-frontend-pipelining-v1`

## 0. Current known state

Do not rediscover already closed facts.

Accepted private toolchain recovery is complete:

- nvcc 12.4.131: available and hash-verified;
- CUDA 12.4 headers: available;
- makedepend: available;
- no driver/system-CUDA change is required.

The remaining problem is engineering-only:

> the candidate-private staging/build output-root accumulated an unstable
> partial build state and did not reliably generate the normal GPGPU-Sim
> object/dependency graph, including `SIM_OBJ_FILES_DIR`.

Previous candidate source/staging changes may contain valuable work and must
not be lost.

Status on entry:

`ENGINEERING_RECOVERY_IN_PROGRESS`

Do NOT mark this Goal blocked for ordinary configure/build failures.

## 1. Preserve candidate source before cleaning build state

First inventory the existing local worktree/staging:

```text
git status --short
git diff
git diff --stat
candidate source paths
candidate semantic patch
telemetry patch
private toolchain paths/hashes
existing build logs
```

Preserve the candidate source changes independently of generated build state.

At minimum create a hash-bound source checkpoint/patch outside directories that
will be cleaned.

If practical, commit a local engineering checkpoint on the execution branch
containing source/docs only, but do NOT publish an incomplete scientific
result as accepted.

Do not delete the only copy of candidate source changes.

## 2. Throw away poisoned generated state, not source

Identify all generated/cache/output products from the failed subdirectory build
attempts.

Clean/recreate only generated state, including as applicable:

- Framework `gpu-simulator/build/<config>`;
- Framework `gpu-simulator/bin/<config>`;
- candidate-private GPGPU-Sim build/object/dependency outputs;
- generated makedepend files;
- stale environment-derived path caches;
- stale `SIM_OBJ_FILES_DIR` roots.

Do not delete:

- candidate semantic source;
- accepted toolchain archive/tree;
- accepted trace/config/map assets;
- historical baseline binaries/evidence.

Prefer a completely clean candidate-private staging if the existing generated
tree cannot be proven clean.

## 3. Reconstruct using the repository-authoritative top-level build path

Do not continue by stacking subdirectory `make` commands on the failed tree.

The checked-in Accel-Sim build contract is:

1. set the accepted private CUDA root through `CUDA_INSTALL_PATH`;
2. ensure the candidate-private GPGPU-Sim source tree is the intended exact
   Core/candidate source, not an arbitrary newly cloned dev head;
3. source the top-level environment:

```bash
source ./gpu-simulator/setup_environment.sh
```

with the intended release configuration/environment;

4. build from the Framework top-level simulator target:

```bash
make -j<N> -C ./gpu-simulator/
```

or the exact repository-authoritative equivalent proven by the current tree.

Important:

- `setup_environment.sh` must consume the existing candidate-private
  GPGPU-Sim tree; it must not silently replace it with an unrelated upstream
  source revision;
- verify `ACCELSIM_SETUP_ENVIRONMENT_WAS_RUN`,
  `GPGPUSIM_ROOT`, `GPGPUSIM_CONFIG`, `CUDA_INSTALL_PATH`,
  `SIM_OBJ_FILES_DIR`, compiler paths and generated dependency roots before
  the full build;
- if the standard GPGPU-Sim top-level setup script is responsible for creating
  `SIM_OBJ_FILES_DIR`, diagnose that setup path rather than fabricating the
  directory manually.

## 4. Build-debug discipline

For every build failure:

1. capture the exact first causal error;
2. identify whether it is environment, dependency-generation, compiler,
   include/library, source, or output-root state;
3. apply the smallest engineering repair;
4. rerun the smallest relevant build step;
5. continue.

Do not repeatedly patch symptoms in generated Makefiles.

Do not mark BLOCKED because a build command fails.

If repeated attempts reveal a poisoned staging tree, recreate a clean isolated
staging from immutable accepted source plus the preserved candidate patch and
continue.

Only a genuine V4 B1/B3/B4 condition may block this Goal.

## 5. Build qualification

A build is not qualified merely because an executable appears.

Record:

- exact Framework source;
- exact Core source;
- candidate patch/source SHA;
- nvcc path/version/hash authority;
- gcc/g++/ld versions;
- relevant environment variables;
- top-level build command;
- build log SHA;
- resulting candidate binary SHA;
- legacy-mode binary/source relation.

Then run the original Frontend Pipelining V1 gates:

```text
directed tests
-> telemetry neutrality
-> legacy reproduction
-> candidate qualification
```

If a test fails due an engineering defect, solve-and-continue.

If it reveals candidate semantics violate the declared candidate contract,
classify `CANDIDATE_SEMANTICS_INVALID` and STOP for scientific review.

## 6. Candidate matrix

Only after all build/directed/neutrality/legacy gates PASS:

run candidate:

- T0 10/80;
- T0 0/80;
- T1 10/80;
- T1 0/80;
- T2 10/80;
- T2 0/80.

Follow `EXECUTION_PRIORITY_POLICY_V5.md`.

Perform dependency/resource audit and launch the maximum safe parallel set.
Do not serialize independent points merely for admission ordering.

## 7. Completion

Continue the existing deliverables and remote publication contract from:

`CODEX_NEXT_STAGE_174_TRANSLATION_FRONTEND_PIPELINING_V1.md`

Do not create a separate scientific report just for build recovery.

Final scientific report remains:

`TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_174NEW_V1_REPORT.md`

Then STOP for ChatGPT review before promoting/replacing any baseline.

## 8. Hard boundaries

Do not:

- modify driver/system CUDA;
- overwrite accepted baseline binary;
- change workload/trace identity;
- change 10/80 parameters merely to make results look reasonable;
- implement a TLB/PTW/cache mechanism;
- silently substitute another Core/Framework revision;
- call an ordinary build failure a scientific blocker.
