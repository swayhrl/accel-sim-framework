# Line-MSHR state inventory

| State | Classification |
|---|---|
| line key (`m_data` map key) | must retain / lookup identity |
| `m_pending_sectors`, `m_issued_sectors`, `m_ready_sectors` | correctness until all sectors ready |
| `m_has_atomic` | correctness until terminal response retirement |
| requester list / descriptor IDs | must retain separately; descriptor pool owns request pointer, mask, response-queued bit |
| `m_current_response`, `m_current_descriptor_response` | response-tail ordering/retirement state |
| `pending_lines` | write/order correctness before terminal resolution |
| descriptor free-list/pool | separately accounted global metadata |

No field is proven discardable at A. At B, fill masks may be stable but requester response ordering and descriptor retirement must survive in a distinct object.
