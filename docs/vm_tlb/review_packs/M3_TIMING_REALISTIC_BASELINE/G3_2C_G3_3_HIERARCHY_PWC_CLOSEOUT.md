# G3-2C / G3-3 hierarchy-prefix PTE identity and generic PWC closeout

Status: `PASS — STOP FOR CHATGPT REVIEW BEFORE G3-4`

Core implementation: `1b18b3c5da6e5ba22e4a03c20e3adce498311336`.
Framework source handoff: `6c73a24e433f0eab2b60ec26df597649aa1a60be`.

## Scope and semantic boundary

G3-2C adopts the frozen generic balanced radix partition for each page class:
`r=ceil(B/L)`, `top=B-r*(L-1)`, and root-to-leaf widths
`[top,r,...,r]`. The PTE logical identity is `(ASID, page-size class, level,
VPN prefix)`. PTE physical subranges are an overflow-checked prefix sum of
per-level prefix spaces. No raw/coalesced SimVA is rewritten; SimPA remains
identity-like; PTE requests remain physical, non-recursive and shader-L1D
bypassing.

G3-3 adds only a generic intermediate-PTE cache. Leaf PTEs always use the
accepted real PTE path. OFF has zero entries, FINITE is 128-entry fully
associative LRU, and IDEAL is unbounded/no eviction. Lookup is a configurable
one-cycle service with sufficient logical bandwidth. These hierarchy/PWC
choices are `MODELING_DECISION`s; the 128-entry seed is only
`REFERENCE_OTHER_PAPER` (CLAP-style), not a Segmentation-paper or NVIDIA claim.

## Directed acceptance

| Check | Result | Evidence |
| --- | --- | --- |
| Required 56/49-bit radix widths, prefix sharing/splitting, disjoint ranges, raw offender, non-recursion | PASS | `vm_m3_g3_2c_hierarchy_test` in `/tmp/g3-2c-unit/` |
| Existing M1, G2-1..G2-4, M2-RF, G3-1, G3-2, G3-2B directed suite | PASS | `/tmp/g3-2c-unit/` |
| PWC OFF exact all-level requests | PASS | `vm_m3_g3_3_pwc_test` |
| FINITE warm / partial sharing / LRU / no leaf / 2MB | PASS | `vm_m3_g3_3_pwc_test` |
| IDEAL no-eviction behavior | PASS | `vm_m3_g3_3_pwc_test` |
| Full release build | PASS | release build before `/tmp/g3-3/` runs |

The PWC test has exact assertions: two related cold OFF walks issue 8 PTE
requests; FINITE/IDEAL issue 5, with three intermediate hits and zero leaf-PWC
accesses. A 3-entry finite cache produces six deterministic LRU evictions and
13 requests across the directed A/B/C/B sequence. The controller instance is
not reset between these sequences, matching the ordinary-kernel persistence
policy; `gpgpu_sim` owns one controller for the simulated context.

## Real-memory revalidation

| Replay | Mode | Result |
| --- | --- | --- |
| isolated one-kernel LUD | PWC OFF | normal exit; PTE `4/4`, zero misassociation, final active state `0/0/0` |
| isolated one-kernel LUD | FINITE / IDEAL | normal exit; PTE `4/4`; first cold walk has 3 PWC misses/inserts |
| full LUD | disabled / ideal | both exactly 139,766 cycles; normal exit |
| full LUD | FINITE | normal exit; PTE `4/4`, PWC occupancy 3, zero misassociation, quiescent |
| complete BFS | OFF | normal exit; PTE `28/28`, L2-only/DRAM `12/16`, PWC all zero, quiescent |
| complete BFS | FINITE | normal exit; PTE `19/19`, L2-only/DRAM `3/16`, PWC accesses/hits/misses `21/9/12`, 12 inserts, zero misassociation, quiescent |

PWC OFF reproduces the hierarchy-aware G3-2C BFS PTE count (`28`) exactly.
FINITE skips nine intermediate PTE requests on the same trace; the request and
response counts remain conserved. No deadlock, request loss, duplicate wakeup,
recursive PTE request, or response misassociation was observed.

## Explicit exclusions and next action

No G3-4 page-size policy/timing decomposition, segmentation/sub-entry,
synthetic KV, page fault, migration, UVM, MCM, multi-ASID physical separation,
or virtual-address canonicalization was added. Stop for ChatGPT review before
G3-4.
