# Payload-handle contract

Canonical identity is `{ payload_id, generation }`.

1. `payload_id` is in `[0,1152)`.
2. A live handle requires an occupied slot at that ID with the same generation.
3. A resident sidecar handle additionally requires resident role, owner match,
   and `payload_id == tag_index` in static policy.
4. Reassignment increments generation.  Bypass release clears ownership and
   increments generation before reuse, invalidating the old handle.
5. A fill validates handle generation and owner before clearing pending sectors
   or changing valid/dirty state.  A stale fill therefore cannot land in a new
   incarnation.
6. Resident slots may not be retired while their pending-sector mask is nonzero.

Storage accounting per slice:

| Data storage | Quantity | M1 impact |
|---|---:|---|
| Physical payload budget | `1152 x 128 B` | unchanged |
| Banks | `4 x 288` | unchanged |
| Resident tag entries | `1024` | unchanged |
| Added metadata | one role/status/owner/generation/mask slot record + 1024 handles | metadata only; no additional 128-B payload line |

The C++ layout deliberately retains existing owner/generation/pending-state
metadata and only consolidates its physical-ID representation.
