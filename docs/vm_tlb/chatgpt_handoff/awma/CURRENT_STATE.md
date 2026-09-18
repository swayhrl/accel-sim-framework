# AWMA Current State

Date: 2026-09-18

## Coordination stage

`AWMA_Q05_CONTEXT_EFFECT_DECOMPOSITION_174NEW_V1`

Node174-new owns the active scientific mainline.

Node109 remains on the separately authorized unattended capture side lane and must not delay any future mainline GPU requirement.

## Accepted contextual replay result

Execution:

```text
hrl/awma-q05-contextual-warm-prefix-replay-174new-v1
2640c4368aea1dc44eb6c34fdc9bb5f738ec3fb2
```

Status:

`AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1_COMPLETE_WITH_SCOPE`

Formal 35-member context bundle independently rehashed/validated on 174. All six fresh-process rows completed naturally under unchanged F0.

### Main Q05 result

```text
row       cycles    L2-TLB miss   walks
isolated  885681    633           240
P1        895312    510           184
P2        848511    415           128
P4        872569    450           128
P8        835145    292            16
P16       862623    241            16
P34       871835    249            15
```

Full-context P34 vs isolated:

```text
cycles      -1.56%
walks       -93.75%
L2-TLB miss -60.66%
PWC misses  70 -> 3
PTE req     310 -> 18
```

Interpretation:

- isolated replay substantially inflates cold PTW/walk activity;
- real predecessor history makes Q05 translation state mostly warm;
- removing most walks does **not** translate into a proportional total-cycle reduction;
- longer prefix history can worsen total cycles even while translation metrics improve.

The strongest natural contrast is P8 -> P16:

```text
walks                         16 -> 16
L2-TLB misses                292 -> 241
translation requester latency 8466455 -> 8371120
L2 data misses           1183770 -> 1181047
cycles                    835145 -> 862623
```

Therefore a non-translation context effect is definitely present.

## F0 state semantics

Accepted:

```text
L1 data cache  = flushed at kernel completion
L2 data cache  = persists under F0
L1 TLB         = persists by source lifetime
L2 TLB         = persistence runtime-demonstrated
PWC            = persists by source lifetime; direct residency not dumped
MSHR/PWQ/walkers = quiescent at clean kernel completion
```

## Page-overlap result

174 recomputed translation-relevant overlap using the actual VM-entry address spaces.

64 KiB Q05 coverage:

```text
P1  24.67%
P2  49.34%
P4  49.34%
P8  98.68%
P16 98.68%
P34 99.12%
```

Page overlap is not TLB residency.

P4/P16/P34 remain scientifically necessary despite little/no extra coverage because they test pollution/history.

## Mainline question now

The project must no longer ask only:

> How many walks disappear under real context?

It now asks:

> After realistic prefix warmup, how much Q05 performance sensitivity remains attributable to the modeled translation path itself?

This is required before choosing any TLB/PTW mechanism.

## Active mainline

Execute:

`CODEX_NEXT_STAGE_174NEW_Q05_CONTEXT_EFFECT_DECOMPOSITION_V1.md`

Core experiment:

```text
natural R0 prefix
-> preserve context state
-> Q05 only: ideal-identity translation bypass
-> compare target Q05 cycles/counters
```

Run at least P2/P8/P34 Q05-only ideal-translation counterfactuals after neutrality gates.

Do not globally run the prefix under I0.

## Baseline policy until next review

- P34 = realism reference.
- P8 = screening-prefix candidate only.
- isolated Q05 = historical diagnostic/reference, not sole future mechanism baseline.
- no new mechanism is authorized yet.

## Frozen workload

```text
Qwen/Qwen2.5-0.5B-Instruct
revision 7ae557604adf67be50417f59c2c2f167def9a775
S2_TEXT / B1 / Prefill2048 / Decode32 / FP16 / SDPA
Q05_PREFILL_ATTN_FLASH
occurrence 0
```

Existing isolated and contextual identities remain immutable.

## Storage

164 remains durable authority.

174 local disk is source/worktree/bounded scratch only.

109 may retain active-model replicas and continue its separately authorized unattended producer campaign.

## STOP boundary

No TLB/PTW/cache mechanism starts automatically after decomposition. Return the causal result to ChatGPT for review.
