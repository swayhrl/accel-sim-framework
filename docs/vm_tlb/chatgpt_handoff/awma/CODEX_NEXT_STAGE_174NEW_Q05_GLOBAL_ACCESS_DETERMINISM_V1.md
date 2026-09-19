# CODEX NEXT STAGE — 174-new Q05 Global Access Determinism Closure V1

Date: 2026-09-19

Status: ACTIVE MAINLINE.

Stage:

`AWMA_Q05_GLOBAL_ACCESS_DETERMINISM_CLOSURE_174NEW_V1`

Node:

`174-new / port 2239`

## 0. Scientific reason

The accepted lookup-stream identity stage closed several possibilities:

- natural P34/P8 controls reproduce;
- no post-READY retranslation of one `mem_access_t`;
- LOCAL and PARAM_LOCAL generated access counts are invariant;
- the lookup-stream delta is entirely GLOBAL;
- dynamic GLOBAL memory-instruction count and aggregate active lanes remain fixed.

Accepted P34 GLOBAL counts:

```text
point    global generated accesses
10/80    549754
 5/80    551798
 0/80    637816
 0/0     644990
```

Yet:

```text
GLOBAL dynamic_insts = 139776 in every row
GLOBAL active_lanes  = 4386816 in every row
```

For trace-driven execution, global active masks and lane addresses are loaded directly from the trace before coalescing. The standard global coalescer has no intended dependency on TLB lookup latency.

Therefore this is now a **simulation determinism / identity question**, not a TLB mechanism question:

> For the same formal Q05 trace, why does changing target translation timing change the number of GLOBAL coalesced `mem_access_t` objects?

No architecture mechanism may begin until this closes.

## 1. Coordination and parent

Read:

`hrl/awma-q05-global-access-determinism-handoff-v1`

Execution parent:

```text
hrl/awma-q05-lookup-stream-identity-174new-v1
42f7c134ac9f2d1b0d789ba455a7cea76703ab56
```

Recommended execution branch:

`hrl/awma-q05-global-access-determinism-174new-v1`

Node109 remains on the independent V2.1 side campaign. Do not use or interrupt it.

## 2. D0 — Mine existing logs before any new run

The previous diagnostic prints, per PC:

- dynamic memory instruction count;
- active lanes;
- generated access count;
- transaction-size histogram.

Parse the existing durable P34 10/80, 5/80, 0/80, 0/0 logs and create:

`PER_PC_INPUT_OUTPUT_MATRIX.tsv`

For each GLOBAL PC report:

- dynamic_insts per row;
- active_lanes per row;
- generated_accesses per row;
- tx32/64/128 per row.

Determine first:

1. whether per-PC dynamic_insts differ;
2. whether per-PC active_lanes differ;
3. whether only generated_accesses differ.

Do not infer from aggregate totals.

If per-PC dynamic instruction or active-lane identity already changes, classify that fact immediately and focus the next source audit on trace-instance binding.

## 3. D1 — Freeze the source determinism contract

Document exact accepted source semantics.

### Trace parser

Each trace instruction carries:

- thread-block coordinates in the trace stream;
- trace warp id;
- instruction order within that warp;
- PC;
- active mask;
- explicit/decompressed memory lane addresses.

Address decompression is local to the trace instruction record.

### Trace-driven instruction construction

`trace_warp_inst_t::parse_from_trace_struct()`:

- copies the trace active mask;
- copies PC;
- copies trace memory addresses into the instruction;
- sets memory space/opcode semantics.

For GLOBAL memory operations, `checkExecutionStatusAndUpdate()` does not rewrite lane addresses.

Only LOCAL addresses are remapped by `translate_local_memaddr()`.

### Coalescing

`warp_inst_t::generate_mem_accesses()` is guarded by:

`m_mem_accesses_created`

and GLOBAL uses:

`memory_coalescing_arch()`

with the instruction's active lanes/addresses and fixed coalescing configuration.

Document:

`TRACE_TO_GLOBAL_COALESCING_DETERMINISM_CONTRACT.md`

This is a simulator-source contract, not a hardware claim.

## 4. D2 — Canonical trace instruction identity

Runtime `inst_uid` is timing-order dependent and is not sufficient for cross-run alignment.

Add diagnostic-only canonical identity based on the trace itself:

```text
(trace_thread_block_x,
 trace_thread_block_y,
 trace_thread_block_z,
 trace_warp_id,
 trace_instruction_ordinal)
```

The trace parser already reads TB coordinates, warp id and instruction order.

Propagate this identity through diagnostic-only trace-driven metadata without changing the accepted trace file or functional instruction semantics.

Preferred implementation:

1. retain TB coordinates from `get_next_threadblock_traces()`;
2. retain trace warp id + per-warp instruction ordinal;
3. before issuing the trace instruction, register the canonical identity for the exact hardware warp/issued instruction;
4. let target-only diagnostics query that identity synchronously during `func_exec_inst()`.

Avoid changing core architectural state or scheduler behavior.

If adding fields to common `warp_inst_t` would alter broad ABI/layout unnecessarily, prefer trace-driven-side metadata/registries.

## 5. D3 — Generation-time input/output fingerprint

For exact target Q05 only, record at the actual access-generation boundary.

### Pre-coalescing canonical input

For each canonical GLOBAL memory instruction:

- canonical identity;
- PC;
- opcode/base opcode;
- data_size;
- cache operator;
- active mask;
- ordered active-lane addresses;
- load/store/atomic type.

Compute a stable digest.

Also retain bounded raw detail for any mismatching canonical instructions under node164.

### Post-coalescing output

Immediately after `generate_mem_accesses()`, before memory-pipeline retry behavior:

- number of generated `mem_access_t` objects;
- for each object: address, size, active mask, byte mask, sector mask, access type;
- stable order-independent and order-preserving digests;
- generated access UIDs if available.

Also count:

- access-generation invocations per canonical instruction;
- `m_mem_accesses_created` state before/after;
- any canonical instruction generating accesses more than once.

Expected:

`ONE_GENERATION_PER_CANONICAL_MEMORY_INSTRUCTION`

Do not use later `memory_cycle()` observation as the only proxy for generation.

## 6. D4 — Generation-to-VM conservation

For each run, close:

```text
generation-time mem_access objects
        ==
unique access UIDs first observed at VM boundary
        ==
translation READY access UIDs
```

modulo source-defined cases that intentionally bypass VM.

For GLOBAL Q05, explicitly reconcile any excluded/bypassed categories.

Create:

- `GENERATION_TO_VM_CONSERVATION.tsv`
- `ACCESS_GENERATION_INVARIANTS.md`

If generation-time objects are stable but later VM-observed objects differ, the problem is downstream observation/lifecycle.

If generation-time objects themselves differ, continue with canonical input/output comparison.

## 7. D5 — Neutrality gate

With the canonical fingerprint telemetry enabled but no lookup override, rerun:

`P34_10_80_DETERMINISM_CONTROL`

Require exact reproduction of accepted P34 natural scientific metrics:

```text
cycles = 871835
GLOBAL generated/observed accesses = accepted control value
translation counters = accepted control values
```

Also verify all canonical diagnostic invariants.

If telemetry perturbs scientific behavior, repair before continuing.

## 8. D6 — Minimum causal comparison

Run only:

```text
P34_10_80_DETERMINISM_CONTROL
P34_0_80_DETERMINISM
```

Fresh process per row; natural P34 prefix unchanged.

Do not rerun the entire lookup matrix.

Only if necessary to distinguish a threshold/non-zero effect after D7, add:

`P34_5_80_DETERMINISM`

No P8 rerun is required unless P34 result remains ambiguous.

## 9. D7 — Canonical cross-run diff

Join the two P34 runs by canonical trace instruction identity.

For every canonical GLOBAL memory instruction compare:

### A. Trace/coalescer input

- PC;
- opcode;
- data size;
- active mask;
- active-lane address vector.

### B. Generated output

- access count;
- transaction address/size/mask fingerprint.

Classify every instruction into:

```text
INPUT_SAME_OUTPUT_SAME
INPUT_DIFFERENT
INPUT_SAME_OUTPUT_DIFFERENT
MISSING_IN_ONE_RUN
DUPLICATE_GENERATION
```

Output:

- counts by class;
- top PCs;
- top trace TBs/warps;
- bounded examples of raw mismatches.

Required conservation:

```text
sum(output count deltas across canonical instructions)
=
observed GLOBAL generated-access delta
```

## 10. D8 — Trace-derived offline reference, if source-parity can be closed

Prefer, but do not block the stage on, an offline deterministic reference using the formal member34 trace.

The reference must reuse or faithfully wrap the accepted parser/coalescing semantics rather than ad hoc approximating them.

For each canonical GLOBAL instruction derive expected coalesced output.

Validate first against P34 10/80 generation-time fingerprints.

If exact parity closes, compare P34 0/80 against the same immutable trace-derived reference.

If parity cannot be closed without duplicating complicated simulator semantics, record:

`OFFLINE_COALESCING_REFERENCE_NOT_QUALIFIED`

and rely on D7's canonical cross-run input/output comparison.

## 11. D9 — Scientific decision

Allowed classifications:

### `GLOBAL_STREAM_INPUT_CHANGED_BY_TRACE_BINDING`

Use only if canonical trace instruction input differs between timing points.

### `GLOBAL_COALESCING_NONDETERMINISM_OR_STATE_COUPLING`

Use only if identical canonical input produces different coalesced output.

### `ACCESS_GENERATION_DUPLICATION`

Use only if one canonical instruction generates access objects more than once.

### `GENERATION_STABLE_VM_OBSERVATION_DIVERGES`

Use only if generation-time output is identical but VM-boundary observation differs.

### `PREVIOUS_STREAM_TELEMETRY_ARTIFACT`

Use only if corrected generation-time accounting shows the earlier GLOBAL delta was diagnostic accounting rather than simulator behavior.

### `GLOBAL_STREAM_DELTA_UNRESOLVED`

if none can be proven.

If the result exposes a simulator correctness defect whose fix would change accepted Q05 scientific results, STOP_FOR_SCIENTIFIC_REVIEW after diagnosis. Do not silently repair the scientific baseline in this stage.

## 12. Claim boundary

Until this stage closes:

- lookup-latency sensitivity remains qualitative simulator evidence only;
- 10/80 remain generic model assumptions;
- no hardware speedup claim;
- no TLB/PTW mechanism evaluation.

Do not use the observed changing GLOBAL stream as an architecture characteristic.

## 13. Durable output

Large diagnostic artifacts:

`/root/share/mnt164/huangrulin/awma_q05_global_access_determinism_v1/`

Full canonical per-instruction fingerprints belong on node164.

Git review pack stores bounded summaries/digests only.

## 14. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/Q05_GLOBAL_ACCESS_DETERMINISM_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_Q05_GLOBAL_ACCESS_DETERMINISM_174NEW_V1/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
PER_PC_INPUT_OUTPUT_MATRIX.tsv
TRACE_TO_GLOBAL_COALESCING_DETERMINISM_CONTRACT.md
CANONICAL_TRACE_ID_CONTRACT.md
ACCESS_GENERATION_INVARIANTS.md
NEUTRALITY_RESULTS.tsv
P34_GENERATION_SUMMARY.tsv
GENERATION_TO_VM_CONSERVATION.tsv
CANONICAL_INPUT_DIFF_SUMMARY.tsv
CANONICAL_OUTPUT_DIFF_SUMMARY.tsv
GLOBAL_DELTA_CONSERVATION.tsv
TOP_CANONICAL_MISMATCHES.tsv
OFFLINE_COALESCING_REFERENCE.md
DETERMINISM_DECISION.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Success marker:

`AWMA_Q05_GLOBAL_ACCESS_DETERMINISM_CLOSURE_174NEW_V1_COMPLETE_WITH_SCOPE`

Then report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.
