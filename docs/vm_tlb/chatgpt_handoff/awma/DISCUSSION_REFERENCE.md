# AWMA Discussion Reference — Lookup Stream Identity

Date: 2026-09-19

## 1. What the previous stage ruled out

The simple fill-race explanation is not supported.

Across every bounded point:

`launch miss -> completion hit = 0`

So the changing L1/L2 hit/miss counts are not caused by a lookup launching before a fill and then becoming a hit during its own modeled service interval.

## 2. What still changes

Despite fixed Q05 instruction and CTA totals:

```text
P34 lookup completions
10/80 = 776915
5/80  = 779016
0/80  = 865036
0/0   = 872241
```

This is a large structural change in the translation requester stream.

It must be explained before lookup latency sensitivity can be interpreted cleanly.

## 3. Retry invocation counts are not the same issue

`vm_requests` drops dramatically as lookup latency falls because the pipeline polls/retries pending translation work.

That part is expected.

But `lookup launches/completions` count newly admitted/completed requester work.

Their increase requires a different explanation.

## 4. One mem_access_t does not retranslate after READY

The access object latches translated state:

`set_sim_pa() -> m_vm_translation_applied=true`

Therefore ordinary downstream cache/interconnect stalls do not send that same access object back through translation.

The changing count must arise before or at access-object creation/admission.

## 5. Why local memory is a plausible simulator-specific coupling

Local memory lane addresses are transformed into timing addresses using runtime SM/CTA/thread placement before coalescing.

Then coalescing generates `mem_access_t` objects.

Changing translation timing can change CTA progress and SM availability, which may change placement/order.

If different local mappings alter 32B/64B/128B segment grouping, the same trace instruction/lane stream can yield a different number of coalesced timing transactions.

This is plausible from source but not yet demonstrated.

## 6. The next stage measures the right unit

The next stage counts:

```text
trace/dynamic memory instruction
-> active lanes
-> generated coalesced mem_access_t objects
-> unique access UID
-> translation lookup launch
-> translation READY
```

split by:

```text
GLOBAL
LOCAL
PARAM_LOCAL
PC
SM
CTA
```

This lets conservation identify exactly where the requester-count delta enters.

## 7. Why this is useful even if 109 native reconnaissance is running

109 asks a hardware-side question:

> what latency/reach structures can be observed on RTX4080?

174 asks a simulator-semantics question:

> why does this accepted model change its translation requester stream when lookup timing changes?

Both are required before quantitative mechanism claims and can proceed independently.

## 8. No mechanism yet

The project is deliberately resisting a premature "fast TLB" proposal.

A mechanism is only justified after:

1. simulator stream semantics are understood;
2. native latency/reach evidence is reviewed;
3. the calibrated or bounded model still shows an opportunity.
