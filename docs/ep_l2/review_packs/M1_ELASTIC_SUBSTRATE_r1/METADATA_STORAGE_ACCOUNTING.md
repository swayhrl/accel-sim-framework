# Metadata and storage accounting

M1 does **not** add 128-B payload data storage beyond the fixed physical
payload budget. The modeled payload-data capacity is exactly:

```text
1,152 payload IDs × 128 B = 147,456 B = 144 KiB
```

This fixed capacity is partitioned only by identity range under the active
static substrate: resident IDs `0..1023` and reserved (dormant) bypass IDs
`1024..1151`. No M1 production path allocates or sends bypass traffic.

The following are simulator metadata, separate from the 144-KiB payload-data
budget:

| Metadata | Cardinality | Contents | Purpose |
| --- | ---: | --- | --- |
| `ep_l2_payload_store::slot` | 1,152 | role, status, owner, generation, pending-sector mask | Ownership/lifetime validation; not payload bytes. |
| `payload_handle` | 2 scalar fields per live reference | payload ID, generation | Detects stale/reused identity. |
| `m_ep_l2_tag_payload` sidecar | 1,024 handles | one handle per static L2 tag | Maps tag-index identity to canonical payload identity. |
| Bank queues/counters | transient / scalar | arbitration tokens and statistics | Preserves legacy service semantics. |

The sidecar and role/handle state therefore model bookkeeping and validation
only. They must not be interpreted as an additional 128 × 128-B data store or
as available Unified-Pool capacity.
