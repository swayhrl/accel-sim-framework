# Latest Codex Report

Stage: M5.0BT exact trace capture and qualification.

Status: M5.0BT T1 ACTIVE; RESOLVING_ISSUE M5-0BT-008.

## Current authoritative state

- One persistent Goal: docs/dtc_l1/m5/M5_TRACE_TO_FINAL_SINGLE_GOAL_CONTRACT.md.
- M5.0BT is active and gates M5.0C. No M5.0C, Extended E2, graphics work, or
  capture-host rental/start is authorized by this report.
- Formal platform is 80 SM, global lower cap 10240 (128 credits/SM), and
  ratio-zero. The 80-SM/cap-256 combination is historical diagnostic-only.
- M5.0BT has a workload-specific, source-pinned CUDA-11.8/sm70 capture
  controller, immutable bundle validation, external archive/transfer states,
  non-bypassable BICG-based storage admission, and SIM_HOST orchestrator.
- The two remote checkouts are non-interchangeable: current M5 control checkout
  runs the command; detached 0db04452ec1c47630e4b08002067d82c6811e243
  supplies tracer sources only.
- The provisioned capture host passed V100/CC7.0, CUDA 11.8, toolchain,
  writable-data-volume and pinned-source preflight. M5-0BT-001 was repaired
  before CUDA build; M5-0BT-002 then found an unrelated root-Makefile legacy
  tool after the required trace tool/postprocessor compiled. Its scoped-build
  repair and regression contract now pass. Retry-4 completed that build but
  exposed M5-0BT-003: the host identity probe used incorrect CUDA Runtime UUID
  APIs. The compact Driver-API UUID adapter passed isolated CUDA-11.8/V100
  revalidation (properties, Driver UUID and CC 7.0 agree with `nvidia-smi`).
  No application, raw trace, immutable bundle or formal result has been
  created. Retry-5 reached the BICG CUDA build and exposed M5-0BT-004: its
  selected-workload loop propagated a false final predicate as status 1 after
  a successful `nvcc` build. The explicit-success repair passed an exact V100
  BICG build retest. Frozen source, CUDA 11.8 and sm70 build contract are
  unchanged; each fresh build's executable SHA is captured as provenance.
  Retry-6 then loaded NVBit on V100 but found the installed CUDA-11.8
  `nvdisasm` absent from the application PATH (M5-0BT-005). Retry-7's PATH
  repair passed: the BICG checker passed and full raw traces were captured.
  Its postprocess exposed M5-0BT-006; retry-8 passed that legacy-layout
  adapter, application checker, raw capture and `.traceg` postprocess. It then
  exposed M5-0BT-007; its CSV repair passed on resume. Strict mapping then
  exposed M5-0BT-008 because source-valid `Memcpy*` list entries were treated
  as malformed kernel rows. The line-preserving replay mapping repair is
  pending; retry-8 remains the sole resumable candidate and no immutable bundle
  exists yet.

## Required next action after a V100 host is supplied

Run the documented BICG pilot. It requires only PolyBench, tracer pin and
NVBit; it intentionally requires no SpMV/Parboil paths. Archive/copyback and
storage admission must pass before any non-BICG capture. Then complete the
Base/IO/OO trace mechanism qualification before entering M5.0C.

## HISTORICAL / SUPERSEDED — DO NOT EXECUTE

The prior execution-driven M5.0B cap-256 workload campaigns, their former
natural-terminal wait, and their five terminated recovery jobs are preserved
only as source/provenance and mechanism-validation evidence. They are not
formal performance inputs and impose no active transition condition.
