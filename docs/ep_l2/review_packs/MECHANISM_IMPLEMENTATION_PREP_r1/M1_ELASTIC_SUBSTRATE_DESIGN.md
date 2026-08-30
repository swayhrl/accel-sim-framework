# M1 Elastic Substrate Design

This is a proposed behavior-preserving refactor, not implemented work.

## Minimal shape

Replace the two role-indexed vectors with one `std::vector<slot> m_slots(1152)`. Make `slot` carry `role`, `status`, `owner`, `generation`, and pending-sector mask. Add a 1024-entry `tag_payload_id` sidecar indexed by tag-array cache index; `INVALID_PAYLOAD_ID` means that tag slot currently has no live EP-L2 payload identity. Keep the tag array authoritative for cache/tag validity.

Proposed APIs:

```cpp
enum payload_role { PAYLOAD_RESIDENT, PAYLOAD_BYPASS };
payload_handle reserve(payload_role, unsigned tag_index_or_invalid,
                       new_addr_type owner, mem_fetch *mf);
void rollback_reserve(payload_handle);
bool owner_matches(payload_handle, new_addr_type, unsigned generation) const;
void note_lower_read(payload_handle, sectors);
void complete_fill(payload_handle, owner, generation, sectors, dirty);
void release(payload_handle, release_reason);
request_result request(payload_handle, bool write, cycle, operation_class);
```

`payload_handle` is `{payload_id,generation}`. The mem-fetch carrier already holds this pair and does not need a second identity encoding. The cache-side `extra_mf_fields` remains the owner/address lookup for fill validation.

## Static-equivalent mode

`-gpgpu_ep_l2_payload_policy=static` (new, default when payload mode enabled) must allocate resident only from `[0,1023]` and bypass only from `[1024,1151]`. Initial `tag_payload_id[i]=i` is permitted only if reserve/rollback/replacement preserve today’s exact mapping; better is to initialize invalid and bind on the first reservation while requiring static mode to choose `i`. Bank mapping remains `payload_id % 4`; Legacy/Banked service mode is unchanged.

No M1 change may alter tag selection, cache policy, MSHR admission/lifetime, descriptor semantics, WAD, MissQ, lower traffic, or bank grant order. The D512 histogram generalization may be reused only for observation-vector sizing.

## Exact refactor sites

| site | M1 change |
|---|---|
| `gpu-cache.h:2052-2410` | unite storage, move role from vector identity to `slot`, make global-ID banking direct |
| `gpu-cache.cc:2416-2537` | obtain handle from tag-index sidecar; use reserve/rollback instead of direct resident vector access |
| `gpu-cache.h:2460-72` and `gpu-cache.cc:2561-73` | route fill via handle/global ID; preserve owner/generation/sector checks |
| `mem_fetch.h:133-145` | preserve ABI/fields; optionally name pair a handle in comments only |
| `l2cache.cc:1785-2063` | derive role occupancy from slot metadata, retain existing field names in static mode |
| directed payload tests | add equivalence tests for mapping, rollback, replacement, stale fill, and bank modulo |

## M1 assertions and acceptance gates

- `0 <= payload_id < 1152`, and `bank == payload_id % 4`.
- One live owner per `(payload_id,generation)`; owner map may not contain a duplicate live line unless an explicitly later multi-owner state is designed.
- A handle stored in a tag sidecar agrees with the live slot role/owner; no pending fill can be released/reassigned.
- Release increments generation or otherwise makes every old handle invalid before reuse; no double free.
- Static mode reports resident/bypass capacity and counts exactly 1024/128 and is cycle/counter identical to accepted baseline on directed tests and representative smoke.
- Terminal drain has zero live transaction resources and no arbitration retry.

Rollback boundary: a single M1 commit is revertible because `static` retains old capacities and policy. Do not enable a shared policy in that commit.
