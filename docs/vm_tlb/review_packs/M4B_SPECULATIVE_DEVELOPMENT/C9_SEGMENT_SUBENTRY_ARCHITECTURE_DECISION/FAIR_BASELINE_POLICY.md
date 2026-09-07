# C9 fair baseline policy

## Rule zero: one charged translation-state budget

`C9_MODEL_DECISION`: fairness uses a GPU-scope shared L2 translation-state budget
`B_total = B_exact = 66,000 bits` from `SUBENTRY_EQUAL_BIT_BUDGET.md`. Unchanged L1 state and
common controller generation state are excluded from every arm. Any new state, including all 35
local Segment replicas, is charged. Results report both the budget limit and actual occupied array
bits because 16-way set granularity can leave unusable remainder bits.

This is a transparent bit-accounting policy, not a claim that local replica bits and shared SRAM bits
have identical physical area, routing or energy. No C9 result reports PPA.

## Frozen comparison classes

| ID | Arm / purpose | Charged state and arithmetic | Capacity / status |
| --- | --- | --- | --- |
| F0 | baseline exact 64KiB L2 | `768*85 + 48*15 = 66,000` | 768 exact translations; official baseline. |
| F1 | equal-bit standalone sub-entry | `G=96`: `96*622 + 6*15 = 59,802` | 96 groups / 1,536 leaves; official fair sub-entry candidate. |
| F2 | exact-L2 bit-matched comparator for F1 | `E=688`: `688*85 + 43*15 = 59,125` | Must accompany F1 when matching its actually instantiated bits. |
| F3 | expanded exact L2 capacity sweep | `B_exact(E)=E*85+(E/16)*15` | Every `E>768` point is charged; no expanded exact capacity is free. |
| F4 | leaf-capacity-matched exact diagnostic | `E=1,536`: `1,536*85 + 96*15 = 132,000` | 2x F0 bits; diagnostic only, never equal-cost. |
| F5 | equal-budget PWC alternative | `B_PWC(120)=8,370`; remaining exact `E=656` costs `56,375`; total `64,745` | Official PWC alternative, described below. |
| F6 | homogeneous 2MiB exact diagnostic | `848*76 + 53*15 = 65,243` | Requires separate allocator/page-policy contract; not a free page-size improvement. |
| F7 | charged Segment + exact | `B_seg(N=8)=35*8*135=37,800`; exact `E=320` costs `27,500`; total `65,300` | Official fair Segment-only arm. |
| F8 | charged Segment + equal-bit sub-entry | `37,800 + B_sub(32)=37,800+19,934=57,734` | Official fair combined arm: 32 groups / 512 leaves. |
| F9 | bit-matched exact comparator for F8 | `E=656` exact costs `56,375` | Same no-Segment shared-state level as F8; label topology difference explicitly. |

`F2` is called “bit-matched exact” rather than falsely promising it will always be larger; tag-sharing
can legitimately make a compression candidate support more leaf translations at the same bits.
`F3` is the required expanded-exact policy: it is a charged capacity sweep and must be reported when a
claim depends on giving exact L2 more state. `F4` separates leaf provisioning from compression.

The historical `768 groups * 16 leaves` state is neither F1 nor F8. It is a historical
`SPECULATIVE_CANDIDATE` artifact only and cannot be an official comparison arm.

## Equal-budget PWC definition

`EXISTING_MODEL_FACT`: the frozen 128-entry PWC is a generic M3 functional prefix cache with
sufficient logical walker bandwidth; it stores logical prefix identity rather than a physical hardware
payload. It cannot be treated as a bit-equal hardware baseline by raw entry count.

`C9_MODEL_DECISION`: F5 uses a physically interpretable accounting proxy and C10 must expose it:

```
PWC entry = valid(1) + ASID(16) + level(2) + VPN_prefix(p_l)
          + next_table_PPN(33) + attributes(2)
          = 54 + p_l bits
```

For the 33-bit VPN, 4-level balanced v1 radix model, non-leaf prefix widths are 6, 15 and 24 bits.
F5 reserves 40 entries per non-leaf level in 4-way banks:

```
array bits = 40*(60 + 69 + 78) = 8,280
PLRU bits  = 3 levels * 10 sets/level * 3 = 90
B_PWC(120) = 8,370 bits
```

The remaining budget admits 656 16-way exact entries:

```
B_exact(656) = 656*85 + 41*15 = 56,375
B_PWC + B_exact(656) = 64,745 <= 66,000
```

F5 is a **modelled fair alternative** only after C10 represents the pointer payload, per-level banks,
one-port/queue behavior and timing. Until then, existing 128-entry PWC outputs remain historical
standard-mode evidence, not F5 results.

## 2MiB page alternative

`PAPER_SPEC`: the project baseline is 64KiB, and the paper discusses reach scaling rather than a
free direct large-page simulation. `EXISTING_MODEL_FACT`: C1 sub-entry is 64KiB-only.

`C9_MODEL_DECISION`: F6 is a homogeneous 2MiB exact-TLB diagnostic. It stores
`valid(1)+ASID(16)+VPN(28)+PPN(28)+Q(2)+page_class(1)=76` bits/entry. Under 16-way PLRU, 848 entries
fit; 864 exceed the base budget. F6 must state allocation contiguity, promotion/demotion, fault,
migration, fragmentation, shootdown and workload page-policy assumptions. It is not silently combined
with F1/F8 and cannot establish a general superpage conclusion without those inputs.

## Segment and combined charging

`C9_MODEL_DECISION`: selected local Segment table capacity is `N=8`, descriptor size is 135 bits, and
35 replicas cost 37,800 bits. This state is charged even though it is local while F0's L2 array is
shared. The deliberate conservative accounting avoids claiming that replication is free.

For F7, 320 exact entries fit the remaining state. For F8, only 32 physical 16-way groups fit after
charging Segment state; 48 groups would cost 67,701 total bits and exceed the budget. F8's unused
8,266 bits cannot make a further 16-way group set. A future topology/associativity change requires a
new accounting decision; it cannot quietly consume this slack.

## Required reporting discipline

Every future comparison must state: arm ID; actual bit formula/value; exact/group/PWC capacities;
associativity; ASID/page-size scope; Segment replica count; `Lseg` sensitivity point; lookup ports,
queue/backpressure and stall telemetry. Results must not pool Window A/C metrics, call F4 equal-cost,
or compare the old 768-group C2/C4 artifact against F0 as a fair architecture baseline.
