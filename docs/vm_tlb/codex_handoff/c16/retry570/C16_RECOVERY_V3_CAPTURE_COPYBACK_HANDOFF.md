# C16 Recovery V3 — NVBit Capture and Rolling Copyback Handoff

## Purpose

Execute the frozen memory-target plan safely, validate every selected target, and ensure every required raw artifact is copied back to the local/control host before remote cleanup.

## Runtime contract

Default proven runtime:

```text
NVBit                 1.7.5
CUDA module loading   effective EAGER
CUDA                  12.4
Driver                570.124.04
PyTorch               2.5.1+cu124
GPU                    RTX3090 / SM86
```

Use exact per-deployment package/runtime receipts. Do not re-open NVBit 1.8 diagnosis.

## Per-target sequence

For each frozen target-plan class:

```text
1. no-trace prewarm
2. READY
3. assert prewarm trace count == 0
4. static-map / target revalidation
5. narrow canary capture
6. parse/schema/address validation
7. independent-process reproducibility capture
8. second-pass identity validation
9. formal bounded capture across required phase/steps
10. cleanup
11. immediate remote->local copyback
12. SHA closure
```

## Static-map requirements

Never reuse a static range from another model or implementation.

For each selected target record:

- full function/mangled identity;
- module/library hash;
- NVBit static vector index/range;
- instruction offset;
- opcode;
- memory space;
- load/store/atomic classification;
- address-bearing capability.

## Canary acceptance

For a target proven to launch:

```text
record_count > 0
address_record_count > 0
schema/parser = PASS
correct function/range = PASS
prewarm_trace_count = 0
measurement window = CLEAN
normal exit = PASS
```

If zero records occur, do not simply widen the range. First prove whether the target launched.

## Reproducibility

Run an independent process with the same frozen identity/input.

Require agreement in:

- exact target function;
- static range/opcode;
- phase/step;
- schema;
- structural record-count contract.

Do not require raw address equality or raw SHA equality across processes.

## Formal capture

For every plan row selected as required:

- capture all required occurrences within the frozen ROI/window;
- preserve prefill/decode and decode-step attribution;
- preserve target/run/kernel identity;
- retain output checksum/terminal correctness;
- apply 4 GiB or 20 min per-window hard bound;
- one GPU capture process at a time.

If a window reaches a hard bound, retain `BOUNDED_PARTIAL`, copy it back, and continue other rows. Never silently extend a bound to make the result complete.

## Rolling copyback

After every raw/large artifact set, do not wait for the end of the campaign.

### Required receipt fields

```text
run_id
deployment
scenario
phase/step
target identity
remote path
remote bytes
remote sha256
local path
local bytes
local sha256
sha_equal
capture terminal status
```

### Deletion rule

Remote raw data may be removed to reclaim disk only after:

1. local copy exists;
2. local size matches;
3. local SHA matches remote SHA;
4. local raw-artifact index is durably written;
5. no other required artifact references only the remote path.

The final campaign must have `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`.

## Storage control

Before formal capture:

- estimate bytes from canary;
- record free remote/local storage;
- reserve headroom for temporary files;
- if necessary, copy back and remove already-closed remote raw files first;
- do not start a window likely to exhaust disk before its hard bound.

## Cleanup

Every run must leave:

```text
ACTIVE_GPU_PROCESS_COUNT=0
ACTIVE_DIAGNOSTIC_PROCESS_COUNT=0
MEASUREMENT_ACTIVE=ABSENT
```

If cleanup fails, repair cleanup before launching the next capture.

## Acceptance

R5, R6, and R7 gates in `C16_FULL_AUTHORITY_RECOVERY_V3_STAGE_ACCEPTANCE.md` govern completion.
