# Runtime Recovery Strategy

## Objective

Close the only major Simulation Analysis foundation gap: create a maintainable, hash-bound `NEW_SIM_BASELINE_V1` on 174-new and calibrate it against bounded historical traceg anchors.

This is not an attempt to resurrect the exact historical C12 binary at any cost. Historical C12 remains a reference/calibration authority.

## Recovery order

Proceed autonomously through the following recovery ladder; do not stop at the first missing dependency.

### 1. Toolchain discovery

Inventory all plausible local/shared user-space sources before downloading anything:

- `nvcc`, `cuda`, `CUDA_HOME`, `/usr/local/cuda*`;
- conda/mamba environments and package caches;
- `/root/share` and node164 toolchain archives/caches;
- compiler versions, CMake/make, Python, host GCC/G++;
- repo build scripts declaring supported CUDA/toolchain assumptions.

Record absolute paths and hashes/versions.

### 2. Isolated toolchain provisioning

If no compatible nvcc exists locally, provision an isolated toolchain without mutating the base system.

Allowed recovery methods, in preferred order:

1. reuse an already-installed/shared compatible toolkit;
2. use a user-space package/toolchain environment if available;
3. obtain a compatible toolkit from an already-authorized project node such as 109 only after checking version/build compatibility;
4. use a vendor/user-space installer or package source if network access permits;
5. as a last resort, document the exact external artifact/version required.

Do not install system-wide packages or replace host CUDA globally.

A toolkit copied from another node is a build dependency only after its binaries/headers/libs and version are hash/version recorded. Do not assume `/usr/local/cuda-12.8` is compatible merely because it exists on 109; test against the selected source/build contract.

### 3. Source candidate selection

Inventory framework/core candidates with the required hooks:

- trace-driven execution;
- VM/TLB/PTW/PWC support;
- cache/memory telemetry required by AWMA;
- M4C/M4B config compatibility or a documented migration path.

Prefer a current maintainable source pair over an unavailable exact historical object.

Record commit SHAs and all semantic patches. Small portability-only fixes are allowed inline; simulator-semantic changes require explicit rationale and directed tests.

### 4. Isolated build

Build in a fresh worktree/build directory with bounded parallelism (`-j2` by default unless evidence supports more).

Freeze:

- framework SHA;
- core SHA;
- toolchain identity;
- build command/environment;
- binary SHA256;
- config schema/version;
- telemetry schema/version.

### 5. Runtime smoke ladder

Do not jump directly to long C12 replay.

Run in this order:

1. binary startup/config parse;
2. tiny known traceg parser smoke;
3. VM-disabled/reference config smoke;
4. VM-enabled minimal trace smoke;
5. one bounded historical Prefill anchor;
6. one bounded historical Decode anchor.

At each step preserve raw logs and exact command/config hashes.

### 6. Historical calibration

Compare the new baseline against C12 historical reference only on metrics whose definitions align.

Classify differences as:

- `EXACT_OR_TOLERANCE_MATCH`;
- `EXPECTED_NEW_RUNTIME_DELTA`;
- `CONFIG_OR_TELEMETRY_DEFINITION_DELTA`;
- `UNEXPLAINED_MISMATCH`;
- `NOT_COMPARABLE`.

Do not force new results to match the historical binary by changing unrelated semantics.

### 7. Consumer-contract hardening

Fold in the two small review fixes:

- enforce synchronization/control semantics in `SIM_COMPAT_CAPTURE_V1` admission;
- perform real traceg grammar/parser smoke rather than only xz readability when parser/runtime support is available.

Add negative fixtures for both.

## Non-goals

Do not:

- use 109 GPU;
- capture new model traces;
- run a production mechanism sweep;
- attempt to reproduce every C12 arm;
- modify accepted Native raw;
- fabricate missing C16WARP1 semantics;
- mass-rename legacy paths.
