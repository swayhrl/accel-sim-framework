# Baseline Review and Compatibility Notes

## Accepted baseline state

The runtime stage is accepted as:

```text
NEW_SIM_BASELINE_V1_QUALIFIED
scope = HASH_BOUND_FIXED_WINDOW_10000
```

The accepted evidence is the successful historical trace recovery plus fixed-window C12 Prefill/Decode replay on the qualified VM-enabled runtime. This is sufficient to use the runtime as the consumer baseline for the first current-model simulator-native trace, but not to claim full-ROI or exact historical binary/numerical equivalence.

## Upstream control-plane cleanup is complete

The previously stale baseline review-pack summaries were already reconciled during the accepted 174-new consumer-preparation stage:

```text
consumer commit:
25aa29862239a408099639ae9d5f1a0ea4fee1e1

accepted state:
174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1

SIM_BASELINE_ID:
SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
```

That cleanup used already-produced successful evidence and did **not** rerun C12. Node109 must treat it as completed upstream work and must not reopen or redo it merely for this producer stage.

Historical note: the inconsistency had involved older blocked-state summaries such as `C12_PREFILL_CALIBRATION.tsv`, `C12_DECODE_CALIBRATION.tsv`, `SMOKE_LADDER_RESULTS.tsv`, `OPEN_ISSUES.md` and `EXTERNAL_BLOCKER.md`, which were reconciled against the successful trace-recovery and qualification evidence. This note is retained only to explain provenance, not as an active task.

## Consumer contract status

`SIM_COMPAT_CAPTURE_V1` requires simulator-critical semantics including:

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

The producer stage must prove a **real parser/grammar smoke** on its formal output; merely checking that `.traceg.xz` decompresses to non-empty bytes is not sufficient for formal producer qualification.

## Baseline use in this wave

For every later current-model bounded simulation run on 174-new, freeze:

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

Node109 does not run this bounded simulation in the producer stage. Its responsibility ends after the READY/hash-closed simulator-native bundle is transferred through the accepted pipeline.

## First formal current-model target

Frozen target:

```text
Qwen/Qwen2.5-0.5B-Instruct
revision 7ae557604adf67be50417f59c2c2f167def9a775
S2_TEXT
PREFILL
batch = 1
prefill_tokens = 2048
decode_tokens = 32
backend = sdpa
dtype = float16
TARGET_ID = Q05_PREFILL_ATTN_FLASH
function occurrence = 0
```

Why this target:

- it already has accepted Native evidence and exact static/launch provenance;
- it is smaller and easier to close than the heavy GEMM target;
- it gives an immediate future Native↔Simulation identity relation without using Native trace bytes as simulator input.

The producer must resolve and verify the exact accepted model/input/target authority from current accepted manifests. It must not retype-and-assume, retokenize, substitute the implementation, or infer missing authority from directory names.

## Claim boundary for first current-model simulation

Allowed only after the later 174-new consumer/replay stage successfully closes:

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
