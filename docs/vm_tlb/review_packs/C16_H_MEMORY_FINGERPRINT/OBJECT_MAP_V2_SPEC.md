# Runtime Object Map V2 Specification

Schema: `c16-runtime-object-map-v2`. Evidence tier: `NATIVE_ADDRESS_CAPTURE` for direct runtime-hook records; downstream address results are `TRACE_DERIVED_STRUCTURAL`.

## Allowed classifications

| Class | Boundary |
|---|---|
| `WEIGHT` | Directly observed live parameter/storage generation only. Tied parameters and views reference the same storage/generation and never become duplicate payload. |
| `QUANT_METADATA` | Directly observed scales, zero points, group indices, or equivalent quant side-storage. It is not silently folded into Weight. |
| `KV_CACHE` | Directly observed current KV storage/generation. `architecture_attention_representation` and `runtime_kv_representation` are independent root fields. |
| `UNKNOWN_RUNTIME` | Any absent, released, ambiguous, overlapping, or boundary-spanning range; never inferred to be Activation or Workspace. |

`ACTIVATION` and `WORKSPACE` are rejected by this V2 schema. Adding either needs direct runtime evidence and a separately reviewed schema revision.

## Required event fields

Every event carries `event_type`, `event_ordinal`, `storage_id`, `generation`, `stream_id`, `context_id`, `timestamp_ns`, `order_evidence`, and non-Python `allocation_evidence`. Event ordinal is strictly increasing. `order_evidence` is `HOST_ISSUE_ORDER`, `CUDA_EVENT`, or `UNKNOWN_ORDER`; unknown order remains unknown.

| Event | Additional fields | Contract |
|---|---|---|
| `ALLOCATE` | `object_class`, `range_start`, `range_end_exclusive` | Starts one directly observed storage generation. |
| `VIEW` | `view_start`, `view_end_exclusive` | Must be contained in its allocation. Views preserve aliases and are not independent payload. |
| `GROW` | full new `range_*` | The new allocation range must contain the prior range. |
| `REPLACE` | new allocation fields; `replaces={storage_id,generation}` | Adds a new generation/storage. It does **not** release the predecessor. Without a direct release the predecessor state is `UNKNOWN_ACTIVE`. |
| `RELEASE` | `release_evidence` | Only `CUDA_FREE`, `RUNTIME_RELEASE`, or `ALLOCATOR_RELEASE` end a generation. Python destruction/GC is rejected. |

## Attribution rule

An address access maps to a class only if its full `[address, address+width)` interval is contained by exactly one live storage/generation and no other live storage overlaps any part of that interval. Otherwise the result is `UNKNOWN_RUNTIME`, with an audit reason such as `RANGE_BOUNDARY_CROSSING` or `MULTIPLE_OR_OVERLAPPING_STORAGE`.

## Temporal window binding

Allocation history and views are evaluated at an event-ordinal cutoff; grow/view evidence observed after a cutoff cannot leak backwards. A real window manifest must bind all of:

- `object_map_sha256` — exact JSON used by the parser;
- `object_map_snapshot_id` — a map-defined snapshot;
- `object_map_event_ordinal_cutoff` — exact snapshot cutoff;
- `object_map_temporal_status=BOUND`.

Each map snapshot carries `temporal_order_evidence` (`CUDA_EVENT` or `RUNTIME_EVENT_SEQUENCE`) and a nonempty evidence receipt. If that relation cannot be proven, the manifest declares `object_map_temporal_status=UNPROVEN`, supplies no cutoff, and the fingerprinter forces every GLOBAL access to `UNKNOWN_RUNTIME`; it does not infer from the final allocator state.

Fixtures cover tied storage, pointer generation reuse across release (early WEIGHT, late KV_CACHE), KV grow/replace across cutoffs, unknown release, cross-stream uncertain order, quant payload/scales/zeros, and MLA architecture-vs-expanded-runtime-KV differences. The policy intentionally favors an unknown bucket over a false semantic classification.
