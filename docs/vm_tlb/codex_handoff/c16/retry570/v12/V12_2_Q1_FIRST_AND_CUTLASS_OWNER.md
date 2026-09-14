# C16 Recovery-V3 V12.2 — Q1-first Route-B handoff

## Authoritative review snapshot

This handoff was reviewed against:

- active GPU/scientific branch `hrl/vm-c16-g-retry570-v0` at `8f2e7cadf3f591548c5fbe5fe685d1d587fb6761`;
- Route-B producer branch `hrl/vm-c16-g-routeb-producer-v0` at `2b8ab6512ba60fd1c03144be5f6a3408834ef9bb`.

Do not assume either branch is an ancestor of the other. They have diverged. Do not merge the whole producer branch into the active scientific branch.

## Closed facts

1. Llama-3.2-1B S0 campaign G1 is complete and is the sole Route-B selection authority.
2. `ROUTE_B_MAP_RESULTS_V2.json` is terminal for all 36 frozen exact-function requests:
   - 34 `MAPPED_EXACT`;
   - 2 `FAILED_CLOSED/CODE_OBJECT_IDENTITY_UNRESOLVED`.
3. The two unresolved functions are the leading CUTLASS functions for Prefill and Decode. The Prefill CUTLASS alone accounts for about 38% of phase duration, so the current formal >=70% duration-coverage requirement cannot be lawfully satisfied while it remains unresolved.
4. All 34 successful V2 map payloads are remote-SHA-closed and `COPYBACK_READY`; copyback is not a prerequisite for further GPU work.
5. Route-B raw schema is now explicitly `C16_ROUTE_B_LANE_EVENT_V1`: one executing lane per record, explicit `warp_instruction_instance_id`, `(static_index,mref_ordinal)` identity, explicit predicate masks, and no reconstruction from adjacent callback slots.
6. Q0 CPU contract/host preflight is substantially implemented. This does not authorize Q1 until the multi-launch/raw-cap issues below are closed.
7. Previously prepared fallback campaign-G1 rows are already terminal and must not be rerun merely to keep the GPU busy.

## Immediate scientific priority

The next goal is not additional documentation. The next goal is to get a correct Route-B producer onto the RTX3090 as quickly as possible:

1. close the producer multi-launch correctness defects on CPU;
2. build and run Q1 tiny-CUDA on the RTX3090;
3. if Q1 passes, immediately run Q2 on the frozen Llama Route-A bridge anchors;
4. in parallel, continue a bounded attempt to resolve the two CUTLASS owning code objects, especially the Prefill CUTLASS;
5. only after the selection coverage gate is truly satisfiable may representative Route-B canary/formal capture start.

Q1/Q2 must not wait for the two CUTLASS owner gaps. The CUTLASS gaps block final representative-kernel selection, not producer qualification.

## Producer defects that MUST be fixed before Q1

### 1. Multi-launch observed sequence

The device buffer is reset on each exact-kernel launch, so launch-local `observed_callback_sequence` starts again from zero. Raw JSONL must expose a stream-global monotonically increasing observed sequence.

Preferred implementation:

```text
serialized_observed_sequence = state.total_events_before_this_readback + launch_local_sequence
```

Do not change the meaning to hardware-global time. It remains `OBSERVED_CALLBACK_ORDER`.

### 2. Warp-instance identity is launch-scoped

`warp_instruction_instance_id` may restart from zero on each launch. Parser grouping must therefore use at least:

```text
(kernel_launch_id, warp_instruction_instance_id)
```

Never group the whole stream by `warp_instruction_instance_id` alone.

### 3. Terminal count closure

The terminal record must be checked against the actual parsed `LANE_EVENT` count. Required:

```text
terminal.event_count == parsed_lane_event_count
terminal.overflow_count == 0
terminal.drop_count == 0
terminal.status == COMPLETE
```

### 4. Actual serialized output bound

`host_output_cap_bytes` cannot be enforced using `count * sizeof(RouteBLaneEvent)` when the retained raw payload is JSONL. The actual serialized bytes must be bounded. For Q1 a tiny bounded capacity is sufficient, but before any larger capture the writer must fail-close before the JSONL exceeds the frozen byte cap.

No partial file may receive a successful terminal.

## Q1 tiny-CUDA gate

Q1 is independent of final Llama representative selection and may run as soon as the producer above is closed.

The Q1 fixture must include at least:

- one direct GLOBAL load;
- one direct GLOBAL store;
- predicated execution with a nontrivial executing mask;
- at least two launches of the same instrumented function, so sequence/instance reset bugs are exercised;
- if practical, one explicit multi-MREF case; otherwise retain a separate bounded fixture proving `(static_index,mref_ordinal)` insertion for every advertised MREF.

Q1 PASS requires:

- exact frozen function identity;
- nonzero valid GPU VAs only for predicate-true executing lanes;
- correct READ/WRITE/ATOMIC labels for exercised instructions;
- exact `(static_index,mref_ordinal)` whitelist membership;
- stream-global observed sequence monotonicity;
- launch-scoped warp-instance grouping closure;
- zero overflow/drop;
- exactly one valid terminal record;
- terminal event count equality;
- raw SHA and parse-manifest SHA closure.

## Q2 Llama bridge

After Q1 PASS, Q2 immediately uses the already-authorized Llama Route-A bridge functions. Prefer both existing anchors if bounded:

- Prefill `indexSelectLargeIndex` exact function;
- Decode `indexSelectSmallIndex` exact function.

For each function, freeze and instrument all statically mapped `GLOBAL && has_mref` rows, not only the old selected PC. This is the first new dynamic Llama Route-B address evidence.

Q2 checks:

- the old Route-A selected-PC subset is consistent in event/lane behavior and address-bucket cardinality within the expected cross-process limitations;
- the additional GLOBAL+MREF instructions are retained as new Route-B evidence;
- no absolute GPU VA equality across independent processes is required;
- zero overflow/drop and complete terminal closure are mandatory.

A Q2 PASS is producer qualification evidence, not yet representative-phase Route-B formal coverage.

## CUTLASS owner gap

Continue only bounded, evidence-producing owner resolution for the two unresolved CUTLASS functions.

Allowed evidence sources include actual runtime CUDA module/library/fatbin ownership callbacks and hash-closed actual backing files. Do not infer owner from kernel name, function spelling, neighboring kernels, or previous V1 `libtorch_cuda.so` assumptions.

For each attempt retain one terminal receipt:

```text
exact full function
exact observed mangled function
observed CUfunction/CUmodule identity
owner source/callback path
actual owner path if observed
actual owner SHA if closed
status=MAPPED_EXACT|CODE_OBJECT_IDENTITY_UNRESOLVED
```

Do not repeatedly rerun the same unresolved calibration without a new ownership-observation mechanism.

## Selection admission rule

Lane C must consume active-G `ROUTE_B_MAP_RESULTS_V2.json` through an explicit normalization layer. Do not manually rewrite evidence fields.

The final runnable selection MUST fail closed if a required full-census duration-prefix member is unmapped. In particular, do not emit a runnable `final_request_ids` list containing a failed CUTLASS request.

Memory-proxy coverage also remains unproven while an unresolved map can materially affect the full denominator. Failed rows may not be removed from the denominator to inflate coverage.

Expected terminal disposition while the Prefill CUTLASS remains unresolved:

```text
SELECTION_NOT_ADMISSIBLE_DUE_TO_FAILED_CLOSED_COVERAGE
```

This disposition does not block Q1/Q2.

## Branch integration discipline

The producer and active branches are divergent. Use a clean integration branch/worktree based on the exact active-G head, not a whole-branch merge.

Recommended CPU-only integration branch:

```text
hrl/vm-c16-g-routeb-q1-integration-v0
base = current origin/hrl/vm-c16-g-retry570-v0
```

Port only the Route-B producer/Q1-required files and focused tests. Preserve active-G scientific receipts and `ROUTE_B_MAP_RESULTS_V2.json` unchanged.

Lane A must not import the entire producer history. It should consume one reviewable integration checkpoint after CPU tests/build pass.

## GPU scheduling

- While Lane C is preparing Q1, Lane A may use the GPU only for bounded CUTLASS owner-resolution attempts or newly frozen independent GPU work.
- Once a Q1 integration checkpoint is published, Q1 outranks further CUTLASS debugging.
- Q1 PASS -> Q2 immediately.
- Q2 PASS -> if final selection is still blocked, retain Q2 raw evidence and resume owner resolution / other independently frozen GPU work; do not invent a representative formal capture.

## Copyback / Lane B

No change to GPU-first storage policy. With healthy remote free space, Lane B should not delay Q1/Q2 by bulk transfer. It may copy only during `MEASUREMENT_ACTIVE=absent` and a valid transfer slot. Lane B must not hold the shared remote-I/O exclusion lock while idle.

## Required checkpoints

Publish immediately when each boundary closes:

```text
ROUTE_B_Q1_INTEGRATION_READY
ROUTE_B_Q1_PASS|FAIL_CLOSED
ROUTE_B_Q2_PREFILL_PASS|FAIL_CLOSED
ROUTE_B_Q2_DECODE_PASS|FAIL_CLOSED
CUTLASS_PREFILL_OWNER_MAPPED|UNRESOLVED
CUTLASS_DECODE_OWNER_MAPPED|UNRESOLVED
ROUTE_B_FINAL_SELECTION_ADMISSIBLE|NOT_ADMISSIBLE
```

Raw GPU data stays outside Git; compact receipts/manifests and SHA evidence go to Git.
