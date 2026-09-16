# Acceptance Requirements — SIM_COMPAT_CAPTURE_V1 + First Current-Model Simulation

## Current state entering node109

Already accepted and **not to be redone** on node109:

```text
174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1
consumer commit: 25aa29862239a408099639ae9d5f1a0ea4fee1e1
SIM_BASELINE_ID: SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
NEW_SIM_BASELINE_V1_QUALIFIED
scope = HASH_BOUND_FIXED_WINDOW_10000
```

The stale baseline control-plane repair was completed in the accepted consumer-preparation commit. Node109 must not rerun C12 or redo that cleanup.

## Gate A — Producer tool qualification

PASS requires:

1. tracer/source/build/binary identities frozen;
2. RTX4080/SM89 load/injection succeeds;
3. micro-canary generates simulator-native trace grammar;
4. actual traceg parser/grammar smoke succeeds;
5. required semantics including `sync_control` are demonstrably present;
6. terminal COMPLETE or an equivalent native terminal proof is mapped without invention;
7. drop_count = 0 and overflow_count = 0, or exact native equivalents are proven;
8. no C16WARP1 semantic reconstruction is used;
9. build/compatibility changes are narrow, reviewed and regression-tested;
10. repeated read/hash checks are stable.

## Gate B — Exact formal target binding

Before formal capture, PASS requires the producer to re-verify the frozen expected input and target authority from accepted files, including:

```text
Qwen/Qwen2.5-0.5B-Instruct
revision 7ae557604adf67be50417f59c2c2f167def9a775
S2_TEXT
PREFILL
batch 1
prefill_tokens 2048
decode_tokens 32
sdpa
float16
Q05_PREFILL_ATTN_FLASH
function occurrence 0
```

No retokenization, model substitution, backend fallback, dtype change, context shortening, target substitution or occurrence change is FORMAL.

## Gate C — Target canary / volume qualification

Before the formal run:

1. intended launch selector must match the frozen target;
2. capture start/stop scope must be understood;
3. simulator semantics/order must remain intact;
4. estimated output size and filesystem headroom must be recorded;
5. truncation/timeout/overflow behavior must be understood;
6. terminal/completeness logic must work for the target.

If the exact target is unsafe in volume, define a new narrower scientific ROI/target identity and stop for scientific review. Never silently truncate the frozen target and call it complete.

## Gate D — Formal target capture / producer PASS

`SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS` requires:

1. exact accepted workload/input/scenario identity;
2. exact target/launch-selector binding;
3. simulator-native ordered trace for the explicitly selected simulation target;
4. required artifacts: `kernelslist.g`, referenced `*.traceg.xz`, producer manifest, address/context sidecars, terminal/completeness receipt, source/build/binary/environment receipt, trace-member manifest and SHA256 closure;
5. deterministic list/payload/sidecar hash closure;
6. actual parser/grammar smoke on formal output;
7. required instruction/control semantics present;
8. formal terminal COMPLETE with zero drops/overflow or exact semantics-preserving native equivalents;
9. repeated hash/read stability;
10. capture scope/ROI explicitly recorded;
11. READY manifest published through the accepted 109->174/node164 pipeline;
12. producer report names exact READY path/run ID and all authority/hash roots;
13. no scientific fallback to another model/backend/dtype/context/target.

Producer PASS ends the active node109 Goal.

## Gate E — Consumer admission (later on 174-new)

`SIM_COMPAT_CAPTURE_V1_QUALIFIED` additionally requires:

1. independent transport hash verification;
2. consumer contract validation passes;
3. real traceg grammar/parser smoke passes;
4. stable `SIM_INPUT_ID` on repeated admission;
5. kernelslist member ordering and payload identities preserved;
6. address/context sidecars accepted;
7. no missing field inferred by the consumer.

Producer PASS alone is not full S1 qualification; S1 closes only after consumer admission.

## Gate F — First current-model bounded replay (later on 174-new)

`FIRST_CURRENT_MODEL_BASELINE_SIM_PASS` requires:

1. admitted current-model `SIM_INPUT_ID`;
2. unchanged qualified `SIM_BASELINE_ID`, or an explicitly new qualified baseline identity;
3. fixed-window policy recorded (`10000` cycles unless a new qualification changes it);
4. parser and runtime start without semantic/config fatal errors;
5. bounded run emits non-zero relevant VM/TLB/PTW/cache telemetry;
6. raw log + normalized telemetry hash closure;
7. deterministic `SIM_RUN_ID` from input/baseline/config/execution contract;
8. at least one repeat/equivalent determinism check;
9. immutable node164 SIM_INPUT/SIM_RUN/SIM_EVIDENCE catalog closure.

A stop caused solely by the frozen fixed-window maximum-cycle boundary is acceptable if the simulator reaches the required boundary cleanly. Assert/fatal/parser abort is not.

## Native↔Simulation relation

For this wave, only establish identity alignment:

```text
EXACT_WORKLOAD_TARGET_DIFFERENT_CAPTURE
```

Do not claim numerical agreement between Native counters and simulator metrics yet. Cross-view numerical calibration is a later stage.

## Allowed final states

Active node109 preferred state:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
```

After later 174-new continuation, preferred combined state:

```text
SIM_COMPAT_CAPTURE_V1_QUALIFIED
FIRST_CURRENT_MODEL_BASELINE_SIM_PASS
```

If producer qualification cannot preserve required semantics after bounded, documented recovery:

```text
SIM_COMPAT_CAPTURE_V1_NOT_QUALIFIED_<EXACT_REASON>
```

Do not use generic `BLOCKED` while an engineering recovery path remains.

## Review packs

Node109 producer pack:

```text
docs/vm_tlb/review_packs/AWMA_SIM_COMPAT_CAPTURE_109_V1/
```

Later 174-new integration pack:

```text
docs/vm_tlb/review_packs/AWMA_FIRST_CURRENT_MODEL_SIM_174NEW_V1/
```

Each pack must contain source anchors, execution context, manifests, hash receipts, tests, claim boundaries, open issues and `SHA256SUMS`.
