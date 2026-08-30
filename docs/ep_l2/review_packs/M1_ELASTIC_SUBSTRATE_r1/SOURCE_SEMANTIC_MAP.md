# Source semantic map

`ep_l2_payload_store` is now one vector of 1152 metadata slots.  A slot stores
allocation role, coarse status, owner line address, incarnation generation and
pending-sector mask.  It stores no extra 128-B payload data.

The static policy is fixed:

```text
resident tag cache-index i -> physical payload ID i       (0..1023)
bypass directed local ID j -> physical payload ID 1024+j  (0..127)
bank                       -> physical payload ID % 4
```

`l2_cache::access` continues to obtain cache-index selection from the existing
tag array.  On a miss it reserves exactly that static resident slot and stores
the live handle in a 1024-entry tag-index sidecar.  On a hit or a sector/MSHR
continuation it consumes the sidecar handle.  `fill` validates the carried
`mem_fetch` identity against both sidecar and owner before state completion.

The existing tag array, sectors, MSHR/descriptor structures, WAD, MissQ, lower
request construction, response routing, and native bank arbitration are not
made policy inputs by M1.  The only access-path edits are handle plumbing and
atomic restoration of a saved sidecar with a saved speculative resident slot.
