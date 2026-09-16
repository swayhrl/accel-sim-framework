# Baseline Review and Compatibility Notes

## Accepted baseline state

The runtime stage is accepted as:

```text
NEW_SIM_BASELINE_V1_QUALIFIED
scope = HASH_BOUND_FIXED_WINDOW_10000
```

The accepted evidence is the successful historical trace recovery plus fixed-window C12 Prefill/Decode replay on the qualified VM-enabled runtime. This is sufficient to use the runtime as the consumer baseline for the first current-model simulator-native trace, but not to claim full-ROI or exact historical binary/numerical equivalence.

## Control-plane inconsistency to repair inline

The qualified review pack contains newer successful qualification evidence, but several older files in the same pack still describe the pre-recovery blocked state. In particular, check and reconcile at least:

```text
C12_PREFILL_CALIBRATION.tsv
C12_DECODE_CALIBRATION.tsv
SMOKE_LADDER_RESULTS.tsv
OPEN_ISSUES.md
EXTERNAL_BLOCKER.md
```

against:

```text
HISTORICAL_TRACE_RECOVERY_ADDENDUM.md
BASELINE_QUALIFICATION_DECISION.json
NEW_SIM_BASELINE_174NEW_REPORT.md
```

This is a **control-plane evidence cleanup**, not a new simulation round. The 174-new Goal must update stale summaries from already-produced successful raw/receipt evidence, regenerate pack `SHA256SUMS`, and preserve the fixed-window claim boundary. Do not rerun C12 solely to rewrite stale prose/TSV if existing receipts are sufficient.

## Consumer contract status

`SIM_COMPAT_CAPTURE_V1` already requires simulator-critical semantics including:

```text
pc
opcode
access_kind
memory_space
byte_width
warp_id
cta_id
active_mask
lane_addresses
event_order
sync_control
```

and requires COMPLETE terminal state with zero drop/overflow plus hash closure of kernelslist, trace payloads and address-context sidecar.

The next stage must additionally prove a **real parser/grammar smoke** on the producer output; merely checking that `.traceg.xz` decompresses to non-empty bytes is not sufficient for formal producer qualification.

## Baseline use in this wave

For every current-model bounded simulation run, freeze:

```text
framework/core source identity
qualified simulator binary SHA256
toolchain/build receipt
base config SHA256
VM overlay/config SHA256
telemetry schema/analyzer identity
fixed-window policy = 10000 cycles
```

If any of these change semantically, create a new `SIM_BASELINE_ID`; do not silently reuse `NEW_SIM_BASELINE_V1`.

## First formal current-model target

Preferred target:

```text
Qwen2.5-0.5B
accepted exact model revision already used by Native line
S2_TEXT
PREFILL
ATTENTION_CORE
accepted Q05_ATTN target identity / launch binding
```

Why this target:

- it already has accepted Native evidence and exact static/launch provenance;
- it is smaller and easier to close than the heavy GEMM target;
- it gives an immediate future Native↔Simulation identity relation without using Native trace bytes as simulator input.

The producer must resolve the exact accepted model/input/target authority from current accepted manifests instead of retyping or retokenizing it.

## Claim boundary for first current-model simulation

Allowed after successful closure:

```text
this exact target has an admitted simulator-native trace;
this exact trace executes on NEW_SIM_BASELINE_V1 for the fixed 10k-cycle window;
VM/TLB/PTW/cache telemetry for that bounded window is available and reproducible.
```

Not allowed yet:

```text
whole-model/full-ROI simulation equivalence;
whole-Prefill speedup;
mechanism benefit claims;
absolute calibration to Native NCU counters without explicit cross-view calibration;
representativeness of all Attention/GEMM/Decode behavior.
```
