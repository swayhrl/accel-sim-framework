# C16 V12.8 — Offline science review and resume decision

## Authority

- Scientific branch remains `hrl/vm-c16-g-retry570-v0` at `ef0d89b1ce297518f86c51cddce190abd47e7364`.
- Recovery is closed by `62428f2cea9ed4cd2def11339311d4347282d9c7`.
- `P1=62/62`, `P2_FINAL_DISCOVERED=97`, `LOCAL_SHA_CLOSED=96`, one duplicate, `P2_FINAL_FAILED=0`, `SCIENTIFIC_REMOTE_ONLY_REQUIRED=0`.
- Canonical recovered local root is `/root/share/c16_recovery_v3` on independent self-owned/separate persistent endpoint.
- No rented-GPU work is authorized by this document.

## Goal

Use only recovered local evidence plus Git-published receipts to close the remaining CPU-side science questions before deciding whether another GPU session is justified.

The two blockers to audit are:

1. missing `C16_ROUTE_A_BRIDGE_REFERENCE_V1` / Q2 structural bridge closeout;
2. two unresolved CUTLASS actual-owner rows that make the current representative-selection contract inadmissible.

Do not weaken scientific gates merely to produce a runnable selection.

## Workstream A — reconstruct Route-A bridge reference

Build `C16_ROUTE_A_BRIDGE_REFERENCE_V1` from recovered local historical Route-A evidence, not from memory or prose.

Frozen anchors:

- Prefill: exact `indexSelectLargeIndex` function, historical selected static instruction/index and its accepted Route-A address-footprint evidence.
- Decode: exact `indexSelectSmallIndex` function, historical selected static instruction/index and its accepted Route-A address-footprint evidence.

Procedure:

1. Locate the exact recovered Route-A source artifacts/receipts under `/root/share/c16_recovery_v3` and Git review packs.
2. Bind function identity, phase, static instruction identity, source receipt SHA(s), and original address-footprint summary.
3. Produce `C16_ROUTE_A_BRIDGE_REFERENCE_V1.json` with explicit provenance; no inferred fields.
4. Compare Q2 all-`GLOBAL+MREF` dynamic streams against Route-A only on legitimate structural dimensions:
   - exact function identity;
   - selected static instruction presence;
   - executing-lane/event cardinality relation;
   - address bucket/line/page cardinality relation where the historical Route-A evidence actually supports that comparison.
5. Do not require absolute GPU VA equality across processes.
6. Publish `ROUTE_B_Q2_BRIDGE_CLOSEOUT_V1.json` with `PASS`, `PARTIAL`, or explicit fail-closed reason.

## Workstream B — CUTLASS / coverage-contract audit

Consume the two failed rows and all recovered diagnostics. The current facts remain:

- Prefill CUTLASS is required by the current >=70% full-census duration prefix and is unresolved.
- Decode CUTLASS is also in the required prefix.
- No default `libtorch_cuda.so` assignment, kernel-name inference, or denominator shrinkage is allowed.

Perform a bounded offline audit with these outputs:

### B1. Loader/identity diagnosis

Determine whether the recovered fatbin registries, stderr, parent receipts, mapper evidence, binary/package metadata, or locally installed corresponding runtime files support any *new* deterministic identity path, for example:

- exact fatbin/cubin payload identity;
- registered image bytes/content hash;
- module-handle-to-image identity independent of a filesystem DSO;
- another directly observed loader relation.

Do not claim a solution unless it can be implemented as a pre-outcome, reproducible identity contract.

### B2. Coverage sensitivity report

Produce a phase-by-phase table containing at least:

- full frozen phase duration denominator;
- each failed CUTLASS row's duration share;
- maximum duration coverage attainable using only already `MAPPED_EXACT` rows;
- current >=70% duration-prefix result;
- current >=80% memory-opportunity proxy result/status;
- what quantities are unknown specifically because failed rows lack admissible maps;
- lower/upper bounds where mathematically defensible without inventing MREF counts.

Keep failed rows in the frozen denominator.

### B3. Candidate scientific paths

Evaluate and rank only defensible paths, such as:

1. **Identity-path repair** — capture/hash an actual runtime code image or fatbin/cubin payload, preserving the current coverage contract.
2. **Contract revision with independent scientific rationale** — only if the revised metric can be justified from the research objective, applied pre-outcome to all rows, and does not selectively exclude failed kernels.
3. **Bounded partial result** — explicitly scope conclusions to the mapped subset instead of claiming representative whole-phase coverage.

For every candidate report:

- scientific rationale;
- what existing evidence supports it;
- required code changes;
- whether a GPU rerun is needed;
- estimated number and type of GPU runs;
- acceptance criteria;
- risk of bias / invalidation.

No contract change becomes active automatically. User approval is required.

## Workstream C — analyze the recovered Q2 traces now

Without waiting for formal representative selection, produce a compact characterization of the already valid Q2 anchors:

For Prefill and Decode separately:

- total LANE_EVENT count;
- read/write/atomic split;
- events by `(static_index,mref_ordinal)`;
- unique GPU VA count;
- unique 128B-line count;
- unique 4KiB-page count;
- unique 2MiB-page count;
- per-launch and aggregate footprint;
- reuse-distance / reuse-count summaries only if well-defined from `OBSERVED_CALLBACK_ORDER`, clearly labelled as observed callback order rather than hardware global order;
- executing-lane/predicate statistics;
- any obvious difference between Prefill and Decode relevant to cache/TLB research.

Do not over-generalize these two anchors to whole-phase behavior before representative coverage closes.

## Deliverables

Create an independent offline-review branch from the scientific authority and publish:

- `C16_ROUTE_A_BRIDGE_REFERENCE_V1.json`
- `ROUTE_B_Q2_BRIDGE_CLOSEOUT_V1.json`
- `CUTLASS_IDENTITY_AND_COVERAGE_AUDIT_V1.md`
- `ROUTE_B_SELECTION_SENSITIVITY_V1.json`
- `Q2_ANCHOR_MEMORY_CHARACTERIZATION_V1.md`
- `GPU_RESUME_DECISION_PACKAGE_V1.md`

`GPU_RESUME_DECISION_PACKAGE_V1.md` must end with exactly one recommended next state:

- `RESUME_GPU_FOR_BOUNDED_IDENTITY_REPAIR`
- `REQUEST_USER_APPROVAL_FOR_REVISED_COVERAGE_CONTRACT`
- `KEEP_GPU_OFF_AND_REPORT_PARTIAL_MAPPED_SUBSET`

and list the minimum GPU jobs needed if resumption is recommended.

## Branching / mutation rules

- Do not mutate `hrl/vm-c16-g-retry570-v0` directly.
- Create a fresh offline-review branch/worktree from `ef0d89b1...`.
- Recovery branch remains read-only evidence authority.
- Do not edit historical receipts or raw artifacts.
- Do not run GPU workloads in this Goal.
- Ordinary engineering problems should be solved locally and boundedly; stop only for a genuine evidence/authority decision requiring the user.
