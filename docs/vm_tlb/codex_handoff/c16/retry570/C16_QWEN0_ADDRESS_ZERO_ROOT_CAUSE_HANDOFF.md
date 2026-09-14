# C16 Qwen0 S0 corrected-tracer address-zero root-cause handoff

## Scope

This handoff addresses the current Qwen2.5-0.5B S0/PREFILL corrected-tracer canary after the output-root fix at active commit `11bf42e64c96ec2c7f771fa12fab912845963b91`.

Do not broaden the experiment, change the workload, change the exact function, or start formal R6 capture until this diagnostic closes.

## Current facts

The current sequence has already separated three different failure classes:

1. backend spelling normalization mismatch — fixed;
2. tracer output-root/parser-root mismatch — fixed by `11bf42e6...`;
3. latest canary now reaches model completion, READY, MEASUREMENT_ACTIVE, CAPTURE_END and produces exact-function trace files, but all target address fields are zero.

Therefore the remaining issue is no longer general NVBit startup, model loading, measurement lifecycle, or output discovery. It is now specifically the dynamic execution / predicate / MREF-address path for the selected static target, or an equivalent trace-parser interpretation issue.

The existing full tracer receives the memory address through `nvbit_add_call_arg_mref_addr64(...)`; its injected device function records active and predicate masks separately. A row can therefore exist even when the selected instruction is predicated off. The known-good Llama path proves that the general tracer can produce non-zero addresses on this runtime, so the Qwen0 result must be localized rather than treated as a global tracer failure.

## Immediate rule

Do **not** proceed directly to independent scientific repro or R6 just because trace files now exist.

The zero-address canary is `NON_SCIENTIFIC_DIAGNOSTIC` until the cause is classified.

If an already-started exact same-target repro is currently running, allow that one bounded process to finish and SHA-close it, but do not launch additional same-target repros before D0-D3 below.

## D0 — preserve the current canary

Retain and SHA-close the current exact-function canary tree under `/root/share/c16_recovery_v3`.

Record:

```text
run_id
exact model/revision/input
exact full function identity
target static index/range/opcode
trace file count
raw bytes
model checksum
READY/CAPTURE_BEGIN/CAPTURE_END evidence
remote/local SHA closure
```

Do not overwrite or reclassify earlier failed canaries.

## D1 — zero-GPU raw trace forensic pass

Before another GPU run, inspect the already-returned raw files and produce one receipt with, at minimum:

```text
TRACE_FILE_COUNT
TRACE_ROW_COUNT
TARGET_OPCODE_OBSERVED
TARGET_INSTR_IDX_OBSERVED
ACTIVE_MASK_NONZERO_ROWS
PREDICATE_MASK_NONZERO_ROWS
PREDICATE_MASK_ZERO_ROWS
NONZERO_ADDRESS_LANE_COUNT
ZERO_ADDRESS_LANE_COUNT
WIDTH_VALUES
FIRST_NONZERO_ADDRESS_IF_ANY
```

For address accounting, distinguish:

- all active lanes;
- predicate-true lanes;
- predicate-false lanes.

Confirm that each trace row actually corresponds to the intended target static index/opcode rather than merely to the exact function.

### D1 decisions

- If the recorded instruction/index/opcode does not match the frozen target: this is a selector/index-semantics bug. Fix it and rerun one canary.
- If `PREDICATE_MASK_NONZERO_ROWS == 0`: the target is dynamically reached only as predicated-off in this workload. Do not call this a tracer failure; requalify one evidence-backed, predicate-true GLOBAL MREF target in the same exact phase/function or update the frozen target-plan version.
- If predicate-true rows exist but all predicate-true lane addresses are zero: continue to D2/D3.
- If nonzero addresses actually exist but the validator reports zero: fix parser/validator only; do not rerun GPU until the fixed parser passes the retained raw.

## D2 — compare with the direct targeted-memory path

Use the existing `retry570_targeted_memory_tool` only as a bounded diagnostic discriminator. Do not substitute it as the final scientific tracer.

For the same exact model/input/function/static instruction, add/retain counters sufficient to distinguish:

```text
EXACT_FUNCTION_LAUNCH_COUNT
TARGET_STATIC_INSTRUMENTED
TARGET_CALLBACK_COUNT
TARGET_PRED_TRUE_COUNT
TARGET_ACTIVE_LANE_COUNT
TARGET_NONZERO_MREF_COUNT
TARGET_ZERO_MREF_COUNT
```

The current helper returns before recording when the guard predicate is false, so add counters carefully before/after the predicate gate without changing the workload.

Run one bounded diagnostic only after D1.

### D2 decisions

- callback count = 0: instrumentation/static-target dynamic reachability mismatch; re-open the exact NVBit-native map/binding.
- callback > 0, pred_true = 0: selected instruction is predicated off; select a better evidence-backed target.
- callback > 0, pred_true > 0, nonzero_mref = 0: NVBit MREF extraction is capability-limited for this exact instruction/path. Continue D3 once.
- direct tool yields nonzero MREF but full tracer raw remains zero: isolate a full-tracer argument/serialization/parser defect using the retained canary; do not change target.

## D3 — at most one evidence-backed alternative target

If D2 proves an instruction-specific MREF limitation, choose **one** alternative direct GLOBAL MREF instruction from the same exact function/phase using the NVBit-native static map.

Selection must be deterministic and documented, preferring a statically direct `LDG`/`STG` with MREF and, where D1 evidence permits, a dynamically predicate-true instruction.

Create a new target-plan version/hash before executing the alternative. Never silently mutate the frozen R4 plan.

Run one narrow direct diagnostic/canary.

- If nonzero address records appear: freeze the new target, run independent R5 repro, then formal R6.
- If the second evidence-backed target also has `callback>0`, `pred_true>0`, and zero MREF addresses: close this **Qwen0 S0 phase target path** as capability-limited, retain evidence, and immediately move the GPU to another ready row. Do not blind-scan static indices.

## D4 — tiny known-good control only if needed

Only if D2 suggests a global tracer regression, run a tiny previously qualified known-good control using the same built tracer binary/runtime. Prefer a minimal fixture or the smallest retained Llama-style control; do not rerun a long Llama model scenario.

The purpose is only to distinguish global tracer regression from target-specific MREF behavior.

## GPU-time rule

This diagnosis must be GPU-frugal:

- D0/D1 are local/offline;
- D2 is one bounded run;
- D3 is at most one alternative-target run;
- D4 only when logically required.

While D0/D1/code edits/tests are running, another GPU-ready scenario should run if it does not conflict with the active tool deployment. Do not leave the rental GPU idle merely because Qwen0 diagnosis is CPU-side.

## Required closeout

Report:

```text
QWEN0_ZERO_ADDRESS_ROOT_CAUSE=
RAW_TRACE_INSTRUCTION_MATCH=
PREDICATE_TRUE_ROWS=
DIRECT_CALLBACK_COUNT=
DIRECT_PRED_TRUE_COUNT=
DIRECT_NONZERO_MREF_COUNT=
ALTERNATIVE_TARGET_ATTEMPTED=
FINAL_QWEN0_S0_PREFILL_STATUS=
NEXT_GPU_ROW=
```

Valid final classifications include:

```text
PARSER_VALIDATION_BUG_FIXED
STATIC_TARGET_BINDING_BUG_FIXED
TARGET_PREDICATED_OFF_REQUALIFIED
FULL_TRACER_MREF_SERIALIZATION_BUG_FIXED
TARGET_PATH_MREF_CAPABILITY_LIMITED
R5_CANARY_REPRO_PASS_READY_FOR_R6
```
