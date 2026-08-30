# M3 RO Pending-State Source Map

This is a dependency/safety map, not an eligibility claim.

## Current state that the traditional Line-MSHR owns

| state/function | anchor | why M3 must retain or replace it |
|---|---|---|
| line-keyed entry / full reason | `gpu-cache.cc:669-83` | governs line cap, per-address merge cap, descriptor-pool availability |
| requester descriptors | `gpu-cache.cc:695-716` | each requester holds `mem_fetch`, sector mask, response queued bit and lives until L2→ICNT enqueue |
| issued/pending/ready sectors | `gpu-cache.cc:686-91,824-49` | avoids duplicate lower sector request and schedules only satisfied requesters |
| read-after-write order | `gpu-cache.cc:736-48`; write handlers around `2035-57` | writes and reads cannot be reordered under a read-only shortcut |
| tag reservation/transitions | `tag_array::access/fill`, `gpu-cache.cc:507-72,1525-1617` | replacement, reserved state, fill and dirty/atomic behavior are separate from MSHR bookkeeping |
| lower request + identity | `gpu-cache.cc:1681-1750`, `2416-2537` | lower `mem_fetch`, payload generation and `extra_mf_fields` associate response with source state |
| response enqueue/release | `l2cache.cc:1065-1100`; `gpu-cache.cc:851-901` | descriptor is released only after ICNT accepts response, not at fill |

## Potential safe boundary

A future RO pending object could take over only after `send_read_request` has captured lower request identity and before/at `m_mshrs.add`; it must retain line address, issued/pending/ready masks, descriptor IDs/list, payload/tag generation and a response-ready queue. It cannot simply erase the MSHR at lower issue because `baseline_cache::fill` calls `m_mshrs.mark_ready` and the normal response path calls `peek_next_access`/`commit_next_access`.

## Exclusions and unresolved certification

Do not admit writes, write-allocate synthetic reads, atomics, `L1_WRBK_ACC`/`L2_WRBK_ACC`, any line with a pending write, or traffic whose access type/order cannot be proved read-only. `mem_fetch::is_write()` and `isatomic()` are necessary but not sufficient certification predicates: aliases, pending writers, sector merging, write-on-fill and cache-policy-specific synthetic requests matter. Current source has no authoritative `provably_read_only` property. M0 must therefore emit a shadow eligibility classification with exclusion reason before M3 is designed functionally.

Required later invariants: exactly one response per descriptor, no duplicate live payload generation, normal per-address ordering, no stale tag/fill validation, and terminal pending-object drain to zero.
