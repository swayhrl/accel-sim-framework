# Sub-entry v1 equal-bit budget and semantics

标签：`REFERENCE_APPROX_SUBENTRY_16`。`EXISTING_MODEL_FACT`: C1 authorized a separable, 64KiB,
16-leaf group approximation; it is not paper-exact. `C9_MODEL_DECISION` makes its storage budget
fair and concrete without claiming the paper used this exact format.

## Accounting ABI

The C9 model ABI is explicit so `G_equal_bit` is reproducible, rather than hidden behind C++
`uint64_t` fields:

| Field | Bits | Label | Notes |
| --- | ---: | --- | --- |
| valid | 1 | `C9_MODEL_DECISION` | exact entry or group/leaf valid bit as applicable. |
| ASID | 16 | `C9_MODEL_DECISION` | matches Segment v1 context ABI. |
| 64KiB VPN/PPN | 33 | `C9_MODEL_DECISION` | 49-bit modeled byte address minus 16-bit page offset. |
| leaf attributes `Q` | 2 | `C9_MODEL_DECISION` | one access-right bit plus one protection/attribute class bit. |
| group base VPN | 29 | `C9_MODEL_DECISION` | `33 - log2(16)`. |
| page-size class | 0 | `C9_MODEL_DECISION` | constant 64KiB in this narrow comparison; a 2MiB alternative is separate. |
| replacement | 15/set | `C9_MODEL_DECISION` | 16-way tree-PLRU, not software `last_touch` or true LRU. |
| object labels | 0 | `EXISTING_MODEL_FACT` | telemetry-only and excluded from hardware state. |

An ASID invalidation generation is common controller state for both exact and sub-entry alternatives.
It is not charged per entry; if a future model charges it, the identical `B_context` term must be
added to both sides of every comparison.

## Baseline exact 64KiB L2 TLB

`PAPER_SPEC`: 64KiB pages and a 768-entry, 16-way L2 TLB are the baseline configuration.
`C9_MODEL_DECISION`: the comparable narrow exact entry stores valid, ASID, VPN, PPN and `Q`:

```
b_exact_entry = 1 + 16 + 33 + 33 + 2 = 85 bits
sets_exact    = 768 / 16 = 48
B_exact       = 768 * 85 + 48 * 15 = 66,000 bits
```

This is the shared L2 translation-state budget used by C9. It excludes unchanged L1 TLB state and
the common ASID generation controller. It is not a full physical SRAM macro budget.

## Sub-entry group accounting and `G_equal_bit`

Each group shares a base tag and has 16 independently valid leaf translations:

```
b_group_header = valid(1) + ASID(16) + base_VPN(29) = 46 bits
b_leaf         = valid(1) + PPN(33) + Q(2)          = 36 bits
b_group        = 46 + 16 * 36                       = 622 bits
B_sub(G)       = G * 622 + (G / 16) * 15
```

`G` must be a multiple of 16 because v1 retains a physical 16-way set-associative group table.
The largest valid `G` under `B_exact` is:

| groups `G` | group/table bits | relation to 66,000-bit baseline |
| ---: | ---: | --- |
| 96 | `96*622 + 6*15 = 59,802` | fits |
| 112 | `112*622 + 7*15 = 69,769` | exceeds |

Therefore:

```
G_equal_bit = 96 groups
leaf capacity = 96 * 16 = 1,536 translations
```

The remaining 6,198 bits cannot form another 16-way set. Equal **bit** budget intentionally does not
mean equal leaf capacity: sharing the 16 ASID/VPN tags is the hypothesis under test. It does mean the
candidate no longer receives 768 group arrays as if they cost 768 exact entries.

For historical clarity only, the frozen 768-group candidate costs
`768*622 + 48*15 = 478,416` accounting bits and can hold 12,288 leaves. It is 7.25x the baseline
array bits and must never again be called equal-cost or be used as C9/C10 fairness baseline.

## Lookup, fill and replacement contract

`C9_MODEL_DECISION` defines a 64KiB key as `(ASID, VPN)`. A probe does:

```
set/hash -> 16-way (ASID, VPN>>4) base-tag compare -> selected way
         -> leaf = VPN[3:0] -> leaf valid/PPN/Q select -> permission -> response
```

The future timing model must separately expose:

```
L_sub_hit = L_set_hash + L_base_tag_16way + L_leaf_mux + L_attribute + L_route
L_sub_fill = L_group_read_modify_write + L_leaf_write + L_replacement_arbitration
```

It may set a documented initial parameter, but it cannot silently declare these equal to exact L2's
80-cycle existing model point. `REFERENCE_APPROX_SUBENTRY_16` is preserved until independent evidence
changes that label.

Fill/invalidation rules:

1. base tag present + invalid selected leaf: fill that one leaf; no new group allocation;
2. base tag absent: select PLRU group victim, invalidate all 16 victim leaves, write new header, then
   write the requested leaf;
3. group replacement accounts all valid victim leaves; no telemetry object bit enters a replacement
   decision;
4. 64KiB VA invalidation clears the selected leaf; an empty group is invalidated to free its way;
5. ASID flush invalidates every matching group/leaf; global flush invalidates all;
6. every fill captures the ASID translation generation and may commit only if it still matches after
   any shootdown. A racing stale fill is discarded, not resurrected.

## Context and superpage scope

`C9_MODEL_DECISION`: v1 sub-entry remains 64KiB-only. Its profile must reject 2MiB keys/configuration
rather than silently treating them as 16 leaves. The normal exact TLB keeps its standard page-size
capability. The homogeneous 2MiB alternative is a separate fair-policy diagnostic with allocator,
promotion/demotion, fragmentation, migration and shootdown caveats. This is a scope decision, not a
claim that sub-entry is generally superior to superpages.
