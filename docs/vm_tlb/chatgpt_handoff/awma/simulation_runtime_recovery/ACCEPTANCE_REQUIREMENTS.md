# NEW_SIM_BASELINE_V1 Acceptance Requirements

`NEW_SIM_BASELINE_V1` may be declared only when every required gate below is closed by reviewable evidence.

## A. Source/toolchain identity

Required:

- framework/core source SHAs are stable and fetchable;
- semantic patches are explicit;
- CUDA/nvcc/host-compiler identity is frozen;
- build environment and command are recorded;
- produced simulator binary SHA256 is frozen;
- rebuild from the same source/toolchain does not silently change the declared baseline identity.

## B. Functional runtime qualification

Required:

- simulator starts and parses the selected baseline config;
- trace-driven input path accepts a real admitted `.traceg.xz` bundle;
- VM/TLB/PTW/PWC features required by the baseline are recognized;
- L1/L2/DRAM/memory-system telemetry required by AWMA is emitted;
- a VM-disabled/reference smoke and a VM-enabled smoke both complete or have an explicitly supported bounded completion contract.

A binary that merely runs non-VM EP-L2 workloads is not sufficient.

## C. Input/consumer correctness

Before baseline qualification:

- historical/native traceg input must pass hash-bound `SIM_INPUT` admission;
- malformed trace/list/hash inputs must fail closed;
- synchronization/control semantics are explicitly represented and admission-tested;
- at least one malformed traceg record must fail a real parser/grammar smoke;
- current `C16WARP1` / MREF-sharded data remains simulator-ineligible.

## D. Historical calibration

Required anchors:

- C12 Prefill F0 or a bounded formally linked Prefill anchor;
- C12 Decode1 F0 or a bounded formally linked Decode anchor.

For each anchor preserve:

- exact SIM_INPUT identity;
- config hash;
- baseline/binary identity;
- command/environment receipt;
- raw log SHA;
- normalized telemetry SHA;
- completion/timeout status;
- comparison table against historical reference where metric definitions align.

At least two independent anchors must be understood before `NEW_SIM_BASELINE_V1` becomes QUALIFIED.

`understood` means either matched within a justified tolerance or a concrete source/config/definition reason for the delta is demonstrated. An unexplained mismatch fails qualification.

## E. Determinism/regression

Required:

- repeat parser/config smoke is deterministic in identity;
- catalog same-ID identical-content insert is idempotent;
- same-ID conflicting content fails closed;
- telemetry normalization is deterministic;
- existing Simulation Foundation tests still pass;
- small inline repairs have directed regression tests.

## F. Node164/control-plane closure

Create/hash-close small authoritative metadata under the AWMA simulation namespace for:

- toolchain receipt;
- source/baseline receipt;
- binary receipt;
- admitted historical SIM_INPUT entries;
- baseline entry;
- bounded SIM_RUN entries;
- calibration dataset/report.

Large raw traces remain referenced by existing canonical storage; do not duplicate them merely for layout.

## Allowed final statuses

Preferred:

`NEW_SIM_BASELINE_V1_QUALIFIED`

If a genuinely external, unrecoverable dependency remains after the full recovery ladder, the stage may close as:

`AWMA_SIM_RUNTIME_RECOVERY_BLOCKED_EXTERNAL_DEPENDENCY`

but only if:

- all feasible user-space/shared/authorized-node recovery methods were actually attempted or proven incompatible;
- the exact missing artifact/version is named;
- no independent stage work remains unfinished;
- no unsupported baseline claim is made.

A bare `nvcc not found` is not sufficient for this blocked status.
