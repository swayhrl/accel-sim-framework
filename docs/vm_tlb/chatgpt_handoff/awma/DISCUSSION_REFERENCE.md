# AWMA Discussion Reference — storage governance, GPU side lane, and consumer audit

Date: 2026-09-17

## 1. Scientific state after Q05 translation timeline closure

The Q05 timeline stage has completed with timing-neutral diagnostic telemetry.

The diagnostic run preserved the accepted R0 10k science exactly while exposing the actual translation key:

`{asid, vpn, page_size}`

Observed timeline facts:

```text
10k:
19 keys / 19 fills / 106 merges / 8,730 post-fill REQUEST invocations

50k:
104 keys / 104 fills / 374 merges / 474,414 post-fill REQUEST invocations

full natural R0:
885,681 cycles
224 CTA
240 keys / 240 fills / 393 merges
8,747,322 post-fill REQUEST invocations
max waiter depth = 35
```

The result remains `MIXED`.

What is now supported:

- burst fanout before fill is real;
- substantial activity continues after fill;
- the behavior is not explained by a simple TLB-capacity/thrashing story.

What is still deliberately not claimed:

- `REQUEST` is not memory-instruction coverage;
- post-fill L1/L2 outcome was not directly logged;
- no mechanism speedup follows from the timeline alone.

Therefore the timeline stage is complete, but it does not authorize automatic TLB/PTW mechanism experiments.

## 2. Why storage governance is now an infrastructure priority

AWMA already produces large artifacts:

- model weights;
- NSYS inventories;
- Native/NVBit traces;
- simulator-native trace bundles;
- full simulator raw output;
- cycle-keyed diagnostic timelines;
- future cross-model derived datasets.

The long-term node role is:

```text
109 = GPU producer
174-new = simulator / analysis
164 = durable large-data authority
```

The accepted Q05 simulator-native trace, full Q05 simulation raw evidence and the new translation-timeline raw evidence are examples of data that should remain durable on node164 rather than depending on 174 local disk.

Existing accepted historical paths are provenance and are not mass-moved merely for neatness.

## 3. Why producer-side qualification alone is not enough

Node109 is responsible for finalizing and publishing producer data, but node174-new is the long-term consumer/simulator.

If only node109 validates the data plane, the project could still miss consumer-side failures such as:

- an admitted path that is visible only through producer-local assumptions;
- stale `.partial` state mistaken for durable data;
- catalog entries that point back to 109 staging instead of node164 authority;
- accepted large artifacts that exist only on 174 local disk;
- mount/permission/read-back differences seen from the simulator node;
- ambiguous ACK or retention state.

Therefore storage closure has two complementary views:

```text
Track C / 109
producer finalize -> publish -> destination receipt -> ACK

Track D / 174-new
independent durable-consumer read-back -> provenance/catalog audit
```

This is not duplicate work. It is producer/consumer separation of trust.

## 4. Required storage data-plane closure

Producer-side Track C first performs a deterministic 1-2 GiB canary:

```text
109 local source
 -> transport via hrl174new
 -> node164 .partial
 -> resume
 -> size closure
 -> SHA256 closure
 -> promotion/rename
 -> read-back hash
 -> ACK
```

Success marker:

`AWMA_164_DATA_PLANE_QUALIFIED_V1`

Track D independently verifies the admitted result from 174-new and audits existing durable AWMA artifacts. It should reuse accepted hash ledgers where appropriate rather than recursively rehashing unrelated terabytes.

No accepted scientific artifact is deleted in either track.

## 5. Why node174 should not become the data disk

174-new should contain:

- source/worktrees;
- simulator binaries;
- small Python environments;
- small indexes/summaries;
- bounded scratch.

Node164 should contain:

- simulator-native traces;
- NVBit/NSYS/NCU raw;
- full simulation raw;
- cycle timelines;
- large parsed/features/datasets;
- durable manifests/receipts/catalogs.

A large file on 174 local disk is a working copy only, never the sole authority.

## 6. Why node109 may now use the idle RTX4080

Target selection is complete and accepted.

Authorized candidates are:

```text
PREFILL_GEMM_PRIMARY_1
DECODE_GEMV_PRIMARY_1
DECODE_FLASH_PRIMARY_1
DECODE_FLASH_PRIMARY_2
```

These represent missing execution families relative to Q05 and were selected by exact implementation, launch shape, recurrence and GPU-time contribution.

The selected primary Prefill GEMM covers 38.10% of total Prefill GPU time. The selected primary Decode GEMV covers 20.22% of total Decode GPU time. Decode Flash contains two materially distinct shapes and both are retained.

The reference NSYS launch number is only a navigation aid. Every producer capture must re-close:

```text
frozen workload
+ phase
+ exact function
+ grid/block
+ deterministic occurrence
+ decode step when applicable
```

A candidate that fails identity requalification is skipped rather than guessed.

## 7. Why storage qualification precedes new capture

The project should not intentionally create new large raw data before proving where it will be durably stored.

Track C is therefore strictly sequential:

```text
Phase A
storage governance / data-plane canary / catalog

PASS:
AWMA_164_DATA_PLANE_QUALIFIED_V1

then Phase B
bounded selected-kernel simulator-native producer capture
```

Track D can run in parallel from 174-new because most of its audit is read-only. If the producer canary is not yet available, it completes all independent mount/inventory/catalog work and records only that final canary verification is pending.

## 8. Capture side-lane guardrails

GPU idle time is not a reason to generate unbounded traces.

Each selected target follows:

```text
identity requalification
 -> bounded capture canary
 -> size/time guard
 -> whole-kernel capture only when feasible
 -> durable publish to node164
```

Current bounds:

```text
8 GiB per target
30 minutes per capture attempt
32 GiB aggregate new durable raw
```

A guard-triggered partial capture is diagnostic only and is never admitted as a complete simulation input.

The side lane uses the accepted simulator-native producer and preserves terminal/drop/overflow/formatter/grammar contracts. It does not substitute C16WARP1 for a whole-kernel simulator trace.

## 9. Current STOP boundary

Neither Track C nor Track D may automatically start:

- TLB/PTW/cache mechanisms;
- latency/walker/capacity/page-size/Segment sweeps;
- NCU or C16WARP1 campaigns;
- Qwen3/DeepSeek campaigns;
- SIM_INPUT admission or Accel-Sim replay of newly captured candidates;
- deletion or physical reorganization of accepted durable evidence.

After producer-side storage/capture and consumer-side storage audit both close, ChatGPT should jointly review:

1. Q05 dynamic translation behavior;
2. which complementary target bundles were successfully captured;
3. whether node164 storage/provenance is independently closed from both producer and consumer views.

Only then should the next simulation/admission/mechanism stage be issued.
