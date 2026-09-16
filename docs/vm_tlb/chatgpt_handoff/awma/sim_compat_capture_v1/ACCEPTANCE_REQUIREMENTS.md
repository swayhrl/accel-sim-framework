# Acceptance Requirements — SIM_COMPAT_CAPTURE_V1 + First Current-Model Simulation

## Gate A — Producer tool qualification

PASS requires:

1. tracer/source/binary identity frozen;
2. RTX4080/SM89 load succeeds;
3. micro-canary generates native simulator trace grammar;
4. required semantics including `sync_control` are present;
5. terminal COMPLETE, zero drops/overflow;
6. no C16WARP1 semantic reconstruction is used;
7. build/compatibility changes are reviewed and regression-tested.

## Gate B — Formal target capture

`SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS` requires:

1. exact accepted workload/input/scenario identity;
2. exact target/launch-selector binding;
3. full semantics for the explicitly selected simulation target;
4. deterministic list/payload/sidecar hash closure;
5. formal target terminal COMPLETE with zero drops/overflow;
6. capture scope/ROI written explicitly;
7. READY manifest published through the accepted data pipeline;
8. no scientific fallback to a different model/backend/dtype/context.

## Gate C — Consumer admission

`SIM_COMPAT_CAPTURE_V1_QUALIFIED` additionally requires on 174-new:

1. independent transport hash verification;
2. consumer contract validation passes;
3. real traceg grammar/parser smoke passes;
4. stable `SIM_INPUT_ID` on repeated admission;
5. kernelslist member ordering and payload identities preserved;
6. address/context sidecars accepted;
7. no missing field is inferred by the consumer.

Producer PASS alone is not full S1 qualification; S1 closes only after consumer admission.

## Gate D — First current-model baseline replay

`FIRST_CURRENT_MODEL_BASELINE_SIM_PASS` requires:

1. admitted current-model `SIM_INPUT_ID`;
2. unchanged qualified `NEW_SIM_BASELINE_V1` identity, or an explicitly new baseline identity;
3. fixed-window policy recorded (`10000` cycles unless changed by a new qualification);
4. parser and runtime begin without semantic/config fatal errors;
5. bounded run emits non-zero relevant VM/TLB/PTW/cache telemetry;
6. raw run log + normalized telemetry are hash-closed;
7. `SIM_RUN_ID` is deterministic from input/baseline/config/execution contract;
8. at least one repeat or equivalent determinism check closes required output invariants;
9. node164 SIM_INPUT/SIM_RUN/SIM_EVIDENCE catalog entries are written immutably.

A timeout caused solely by the frozen fixed-window wrapper is not a failure when the exact qualification policy expects it and the run reaches the required cycle boundary cleanly. Any assert/fatal/parser abort is a failure requiring diagnosis.

## Gate E — Native↔Simulation relation

For this wave, only establish identity alignment, not final calibration.

The accepted relation may be:

```text
EXACT_WORKLOAD_TARGET_DIFFERENT_CAPTURE
```

because Native and Simulation evidence come from separate real-GPU capture passes of the same exact workload/target.

Do not claim numerical agreement between Native counters and simulator metrics yet. S3 calibration remains a later stage.

## Mandatory control-plane repair

Before final stage closure, 174-new must reconcile stale pre-recovery files in `AWMA_NEW_SIM_BASELINE_174NEW_V1` with the already-accepted qualification evidence and regenerate `SHA256SUMS`.

This repair must not alter raw replay evidence or broaden baseline scope.

## Allowed final states

Preferred combined success:

```text
SIM_COMPAT_CAPTURE_V1_QUALIFIED
FIRST_CURRENT_MODEL_BASELINE_SIM_PASS
```

If producer qualification succeeds but current-model replay has a genuine consumer/runtime semantic incompatibility:

```text
SIM_COMPAT_CAPTURE_V1_QUALIFIED
FIRST_CURRENT_MODEL_BASELINE_SIM_BLOCKED_<EXACT_REASON>
```

If producer cannot preserve required semantics after bounded recovery:

```text
SIM_COMPAT_CAPTURE_V1_NOT_QUALIFIED_<EXACT_REASON>
```

Do not use generic `BLOCKED` when an engineering recovery path remains.

## Review packs

109 producer pack:

```text
docs/vm_tlb/review_packs/AWMA_SIM_COMPAT_CAPTURE_109_V1/
```

174-new integration pack:

```text
docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_SIM_174NEW_V1/
```

Each pack must contain source anchors, execution context, manifests, hash receipts, tests, claim boundaries, open issues, and `SHA256SUMS`.
