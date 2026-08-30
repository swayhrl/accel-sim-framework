# Sidecar lifecycle

```text
MISS(tag i) -> save {slot i, sidecar i}
            -> reserve resident physical ID i; generation increments
            -> sidecar[i] = {i,generation}; mem_fetch carries same identity
            -> data-cache admission
               -> fail: restore slot i AND sidecar[i]
               -> lower read: add pending sectors
               -> local write: complete no-fill
response   -> assert sidecar/owner/generation match
            -> complete matching pending sectors
HIT/sector -> use sidecar handle for the existing static ID
replacement-> new static incarnation overwrites the selected ID; stale sidecar
              handles are reconciled if their slot is no longer live
drain      -> no pending bank operations or resident pending sectors; every
              retained sidecar handle remains live and static-role consistent
```

WAD hazard/full and base `RESERVATION_FAIL` cases restore both saved objects in
the same branch.  No M1 path redirects a resident to an arbitrary free ID.
