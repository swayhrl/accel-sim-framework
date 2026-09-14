# START — Lane C Route-B Q1 integration V12.2

Continue as the CPU/code-only Route-B producer owner. Do not run GPU workloads, nsys, NVBit captures, or NCU in this lane.

Read first:

```bash
git fetch origin hrl/vm-c16-g-retry570-v0 \
  hrl/vm-c16-g-routeb-producer-v0 \
  hrl/vm-c16-g-retry570-chatgpt-handoff-v12

git show origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v12:docs/vm_tlb/codex_handoff/c16/retry570/v12/V12_2_Q1_FIRST_AND_CUTLASS_OWNER.md
```

Reviewed heads:

```text
active G = 8f2e7cadf3f591548c5fbe5fe685d1d587fb6761
producer = 2b8ab6512ba60fd1c03144be5f6a3408834ef9bb
```

These branches are divergent. Do not merge the whole producer branch into active G.

## P0: create a clean Q1 integration branch from active G

Create a separate worktree/branch from the latest fetched active-G head, for example:

```text
hrl/vm-c16-g-routeb-q1-integration-v0
```

Base it on exact `origin/hrl/vm-c16-g-retry570-v0` and port only the minimal Route-B producer/Q1 files and focused tests from the producer branch.

Preserve active-G receipts, map results, campaign ledgers, and scientific status files unchanged unless a compact Q1 handoff/status addition is strictly required.

Do not rewrite `ROUTE_B_MAP_RESULTS_V2.json`.

## P0: fix producer multi-launch correctness before declaring Q1 ready

### A. Global observed sequence

Device launch-local sequence currently restarts after each buffer reset. Serialize a stream-global sequence, e.g.:

```text
global_sequence = events_already_serialized + launch_local_sequence
```

It remains labelled `OBSERVED_CALLBACK_ORDER`, never hardware-global order.

### B. Composite warp-instance identity

Parser grouping must use:

```text
(kernel_launch_id, warp_instruction_instance_id)
```

not `warp_instruction_instance_id` alone.

Add a CPU test with two launches reusing local instance id 0 and prove they remain distinct.

### C. Terminal event-count equality

Parser must reject unless:

```text
terminal.event_count == actual parsed LANE_EVENT count
terminal_status == COMPLETE
overflow_count == 0
drop_count == 0
```

Add negative tests for too-small/too-large terminal count.

### D. Actual serialized output-byte bound

Current retained format is JSONL. Do not estimate the retained-byte cap as `count * sizeof(RouteBLaneEvent)`.

For every serialized event line:

- determine actual encoded bytes before committing it;
- fail closed if appending it would exceed the frozen host-output cap;
- never append a successful terminal to a partial/truncated stream;
- after close, verify actual `stat().st_size <= host_output_cap_bytes`.

Q1 may use a deliberately tiny bounded capacity/file cap, but the implementation must already have correct semantics.

## P0: build the Q1 tiny-CUDA fixture and handoff

Prepare a deterministic tiny fixture with at least two launches of the same exact kernel and:

- direct GLOBAL load;
- direct GLOBAL store;
- a nontrivial guard predicate/executing mask;
- deterministic output/checksum;
- frozen exact function identity;
- frozen static map / whitelist;
- bounded event capacity and output bytes.

If practical, add a multi-MREF fixture. If that is awkward, create a separate tiny fixture proving every advertised `(static_index,mref_ordinal)` callback is inserted and independently address-bearing.

CPU-only lane may compile/build the fixture and NVBit tool, but must not execute it on GPU.

Publish a compact Q1 handoff containing exact commands/paths/SHA values Lane A needs. Terminal checkpoint should be clearly named:

```text
ROUTE_B_Q1_INTEGRATION_READY
```

Report the integration branch and exact commit SHA to Lane A immediately. Do not wait for final Llama representative selection.

## In parallel: consume active-G map results safely

Read active-G `ROUTE_B_MAP_RESULTS_V2.json` read-only. Add an explicit normalization layer mapping active evidence fields such as:

```text
full_mangled_function
actual_owning_code_object_path
actual_owning_code_object_sha256
global_mref_count
static_map_sha256
```

into the internal selection schema.

Do not manually rewrite evidence JSON.

## Fix selection fail-close semantics

Current terminal map set has 34 mapped and two failed CUTLASS rows. The Prefill failed CUTLASS is a top-duration row and prevents lawful >=70% Prefill duration coverage.

Selection must therefore distinguish:

```text
analysis result
vs
runnable representative selection
```

If a required full-census duration-prefix member is failed/unmapped, final disposition must be:

```text
SELECTION_NOT_ADMISSIBLE_DUE_TO_FAILED_CLOSED_COVERAGE
```

Do not emit runnable `final_request_ids` containing a failed request.

Do not drop failures from the full denominator to inflate either duration or memory-proxy coverage.

Memory-proxy coverage remains `NOT_PROVABLE` if unresolved rows can materially affect the denominator.

This selection blockage does NOT block Q1 or Q2.

## Prepare Q2 while Lane A runs Q1

After `ROUTE_B_Q1_INTEGRATION_READY`, continue CPU-only work immediately; do not pause the Goal.

Prepare Q2 handoff tooling for the frozen Llama bridge anchors:

- Prefill `indexSelectLargeIndex` exact function;
- Decode `indexSelectSmallIndex` exact function.

Q2 whitelist must contain all statically mapped `GLOBAL && has_mref` rows for each exact function, not just the historic selected PC. Preserve `(static_index,mref_ordinal)` and explicit `mref_count`.

Q2 checker should compare the old Route-A selected-PC subset in terms of event/lane structure and address-bucket cardinality, while not requiring absolute VA equality across processes.

Publish Q2 handoff as soon as Q1 passes or earlier if it can be prepared independently.

## Required focused tests before Q1-ready

At minimum test:

```text
multi-launch global sequence
launch-scoped instance id
missing/duplicate executing lane
predicate-false lane exclusion
zero VA fail-close
multi-MREF ordinal bounds
terminal count mismatch
overflow/drop fail-close
actual JSONL byte cap
missing terminal
bad whitelist SHA
bad map/code-object SHA
```

## Checkpoints

Push compact checkpoints without waiting for the whole Route-B project:

```text
1. producer multi-launch correctness
2. Q1 tiny fixture + Q1 handoff
3. active-map normalization + selection disposition
4. Q2 bridge handoff
```

Final report after Q1 handoff:

```text
INTEGRATION_BRANCH=
ROUTE_B_Q1_INTEGRATION_COMMIT=
PRODUCER_Q0=PASS|FAIL
MULTI_LAUNCH_SEQUENCE=PASS|FAIL
INSTANCE_SCOPE=PASS|FAIL
TERMINAL_COUNT_GATE=PASS|FAIL
ACTUAL_BYTE_CAP_GATE=PASS|FAIL
Q1_GPU_READY=YES|NO
Q2_HANDOFF_READY=YES|NO
SELECTION_DISPOSITION=
```

Continue Goal through ordinary engineering failures using observe -> narrow -> bounded fix -> focused validation. Do not stop for review merely because Q1 has not yet been executed; only Lane A may execute it.
