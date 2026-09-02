# M3 G3-2C + G3-3 — Generic Hierarchy-Prefix PTE Identity and PWC

Status: `AUTHORIZED AFTER G3-2 PASS`

## Objective

Close the remaining generic page-table locality ambiguity before PWC, then
implement and validate a finite page-walk cache (PWC) without claiming
Segmentation-paper exactness.

This task has two internal gates:

1. `G3-2C`: replace the flat `(level, full VPN)` synthetic PTE identity with a
   deterministic hierarchy-prefix identity and revalidate the already accepted
   real PTE L2/DRAM path;
2. `G3-3`: implement the finite PWC on top of that accepted hierarchy model.

If G3-2C PASSes, Codex may continue automatically into G3-3.  After G3-3 PASS,
STOP for ChatGPT review before G3-4 multi-page/timing work.

## Evidence boundary

The target Segmentation paper specifies a 49-bit VA assumption for its segment
descriptor design and gives TLB/walker parameters, but does not expose enough
page-table/PWC organization to reconstruct an exact hierarchy.  Therefore the
model below is a project `MODELING_DECISION`, not `PAPER_SPEC`.

CLAP is allowed only as `REFERENCE_OTHER_PAPER`: it uses a four-level page
table, 128-entry page-walk cache, and 16 walkers.  Those values may motivate a
generic default but must not be attributed to the Segmentation paper.

## Frozen inputs

- accepted G3-2 Core: `965bd8e188175731c31cabfef6c3bdeb7c59e1fd`;
- generic runtime SimVA width: 56 bits;
- retained paper-facing directed configuration: 49 bits;
- page sizes in current generic backend: 64KB and 2MB;
- levels: 4 unless separately configured;
- application mapping remains resident and identity-like: `SimPA == SimVA`;
- PTE requests remain physical, translation-bypassing, shader-L1D-bypassing,
  and use the accepted real L2/DRAM/interconnect path;
- current M3 is single address space / ASID 0 for claims.

Do not canonicalize/mask/truncate SimVA.

---

# G3-2C — Hierarchy-prefix PTE identity

## H1. Generic radix bit partition

For each page-size class independently:

```text
B = virtual_address_bits - log2(page_size)   # VPN bits
L = configured page-table levels
r = ceil(B / L)
top = B - r * (L - 1)
```

Require `B >= L` and `1 <= top <= r`.

Use level widths from root to leaf:

```text
width[0] = top
width[1..L-1] = r
```

Examples that MUST be directed-tested:

```text
56-bit, 64KB: B=40 -> [10,10,10,10]
56-bit, 2MB : B=35 -> [ 8, 9, 9, 9]
49-bit, 64KB: B=33 -> [ 6, 9, 9, 9]
49-bit, 2MB : B=28 -> [ 7, 7, 7, 7]
```

This is a balanced generic radix model, not a hardware page-table claim.

## H2. Prefix identity

For level `l` (root level 0), define:

```text
prefix_bits(l) = sum(width[0..l])
prefix(vpn,l)  = the upper prefix_bits(l) bits of the B-bit VPN
```

The PTE identity at level `l` is determined by:

```text
(ASID, page_size_class, level, prefix(vpn,l))
```

For current M3 claims ASID is 0, but keep ASID in logical keys where practical.
Do not claim multi-ASID PTE physical separation unless separately tested.

Consequences that MUST hold:

- related VPNs can share root/intermediate PTE identities;
- the leaf-level prefix covers all B VPN bits and remains unique per VPN;
- unrelated prefixes do not alias;
- 64KB and 2MB namespaces remain disjoint.

## H3. Physical PTE namespace

Within the already reserved PTE physical range, allocate deterministic,
non-overlapping subranges per `(page_size_class, level)`.

For a class/level, the number of possible PTE identities is:

```text
2 ^ prefix_bits(level)
```

Each PTE occupies 8 bytes.

The namespace base for each class/level must be computed by an overflow-safe
prefix sum of all preceding namespace sizes.  Then:

```text
PTE_PA = pte_physical_base
       + namespace_base(page_size_class, level)
       + prefix(vpn,level) * 8
```

Requirements:

- no application/PTE physical-range overlap;
- no class/level overlap;
- no arithmetic overflow;
- the configured PTE reserve must be at least the exact hierarchy requirement;
- keep the existing 56-bit configured reserve unless there is a compelling
  correctness reason to change it; do not shrink it merely for aesthetics;
- PTE addresses remain ordinary deterministic physical addresses and continue
  to exercise actual L2 cache-line locality.

## H4. G3-2C directed tests

At minimum:

1. exact bit-partition tests for all four configurations above;
2. two 56-bit/64KB VPNs with identical upper 30 bits and different low 10 bits:
   same level 0/1/2 PTE identity, different leaf PTE identity;
3. a pair sharing only the intended first one or two prefixes;
4. unrelated top-level prefixes differ from level 0 onward;
5. leaf PTE identity is unique for distinct VPNs;
6. all class/level physical namespace min/max ranges are pairwise disjoint;
7. 49-bit tests remain PASS;
8. former 56-bit BFS offender remains accepted with unchanged SimVA/SimPA;
9. PTE physical requests remain non-recursive and within the reserved range.

## H5. Revalidate real-memory plumbing

Because changing PTE identity changes L2 locality, rerun the accepted G3-2
suite.  PASS requires:

- `vm_pte_l2_hit`, `vm_pte_dram`, response identity, multi-walker and shared
  resource tests PASS;
- one-kernel LUD and complete BFS PASS;
- zero response misassociation;
- request/response conservation;
- final translation MSHR/PWQ/walkers quiescent;
- M1/M2 regressions PASS.

Do not require the old G3-2 L2-hit counts to remain numerically identical; the
hierarchy-prefix model intentionally changes valid PTE locality.  Any changed
count must be explainable by the new deterministic PTE identities.

Only after G3-2C PASS may G3-3 begin.

---

# G3-3 — Generic Page-Walk Cache

## P1. What the PWC caches

The PWC caches **intermediate/non-leaf PTEs only**:

```text
levels 0 .. L-2
```

The leaf PTE (`L-1`) is always resolved by the accepted real PTE memory path
when the TLB misses.  This avoids turning the PWC into a duplicate leaf TLB.

PWC key:

```text
(ASID, page_size_class, level, prefix(vpn,level))
```

A PWC hit represents a cached valid intermediate PTE and skips exactly that
level's lower-memory PTE request.

On a PWC miss, the walker issues the normal physical PTE request; after the
matching response, the intermediate entry may be inserted before progressing.

## P2. Generic default organization

Implement configurable modes:

```text
OFF      : zero entries; every walk level uses the real PTE memory path
FINITE   : default 128 entries, fully associative LRU
IDEAL    : diagnostic unbounded/no-eviction intermediate-PTE cache
```

`128 entries` is a generic baseline motivated by other recent GPU VM studies
(e.g. CLAP), not a Segmentation-paper parameter.

For G3-3, do not invent a new PWC throughput bottleneck.  The default PWC
lookup has a configurable one-cycle service cost and sufficient logical lookup
bandwidth for active walkers; finite-port contention is out of scope unless
separately justified.  Record this as `MODELING_DECISION`.

If implementation structure makes a zero-cycle functional probe materially
safer, Codex may keep the G3-3 functional lookup at zero cycles only if the
choice is explicitly documented and G3-5 is required to add/account for the
final configured PWC lookup latency before M3 closeout.  Do not silently mix
these interpretations.

## P3. PWC lifetime

- persists across ordinary kernels in the same simulated context, matching the
  existing TLB lifetime policy;
- no page remapping exists in M1-M3, so no mapping-driven invalidation is
  required yet;
- context reset/remapping invalidation remains future work;
- page-size class is part of the key; no cross-page-size PWC sharing in this
  generic baseline.

## P4. Required statistics

At minimum:

- accesses/hits/misses by covered level;
- inserts and evictions;
- occupancy and high-water mark;
- PTE requests skipped by PWC hits, by level;
- OFF/FINITE/IDEAL mode identity;
- PWC service cycles if nonzero latency is modeled.

PWC hit/miss counters must not be derived from L2 cache hit/miss counters.

## P5. Required directed tests

### `vm_pwc_zero`

Two cold related walks with PWC OFF issue all expected PTE requests:

```text
L requests per walk
```

### `vm_pwc_warm`

Use two 56-bit/64KB VPNs with identical upper 30 bits and different leaf 10
bits.  With a warm finite PWC:

- first walk: 4 PTE memory requests;
- second walk: PWC hits at levels 0/1/2;
- second walk issues only the leaf PTE memory request;
- total requests across the two walks = 5 rather than 8.

The exact hit counts must be asserted, not inferred from runtime.

### `vm_pwc_partial_share`

Choose VPNs that share only a known prefix depth and prove PWC hits only the
intended upper levels.

### `vm_pwc_capacity_lru`

Use a small finite PWC to create deterministic replacement and prove expected
LRU eviction/reaccess behavior.

### `vm_pwc_no_leaf`

Prove a repeated leaf PTE does not become a PWC hit merely because the upper
levels are cached.

### `vm_pwc_2mb`

Prove page-size-aware keys and expected prefix sharing for 2MB.

### Integrated tests

- `vm_pwc_warm` reduces PTE request count in a real-memory walk;
- PWC OFF reproduces the hierarchy-aware G3-2C full PTE request behavior;
- finite/ideal PWC never changes resolved SimPA/data semantics;
- response identity, waiter exact-once, no-recursion and M2 replay invariants
  remain PASS;
- one-kernel LUD plus at least one BFS run complete with quiescent state.

## P6. Acceptance and STOP

G3-3 PASS requires:

- G3-2C hierarchy tests and G3-2 real-memory regressions PASS;
- deterministic OFF/FINITE/IDEAL behavior;
- exact warm/partial/LRU/no-leaf tests PASS;
- structured PWC and skipped-PTE statistics;
- no new deadlock/request loss/response misassociation;
- M1/M2 invariants remain PASS;
- parameter/evidence ledger clearly labels hierarchy and PWC organization as
  generic `MODELING_DECISION` / `REFERENCE_OTHER_PAPER`, not target-paper fact.

After G3-3 PASS:

- commit/push Core and Framework evidence;
- update target progress and latest report;
- create/update the M3 review pack with hierarchy/PWC evidence;
- STOP for ChatGPT review before G3-4.

## Explicitly forbidden

Do not in this task:

- start G3-4 page-size policy/timing decomposition;
- implement Segmentation or L2-TLB sub-entry/coalescing;
- inject synthetic KV;
- add page fault/migration/UVM/MCM;
- rewrite/canonicalize generic SimVA;
- claim the generic hierarchy/PWC is exact NVIDIA hardware or exact target
  Segmentation-paper behavior.
