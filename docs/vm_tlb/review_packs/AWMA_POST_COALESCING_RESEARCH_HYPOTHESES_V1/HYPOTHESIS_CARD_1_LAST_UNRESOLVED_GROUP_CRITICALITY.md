# Hypothesis card 1: last-unresolved page-group criticality

Status: `CONDITIONAL_PREPARED`, not an innovation claim.

## Problem

After same-dynamic-warp-instruction VPN deduplication, a dynamic memory
instruction can still contain multiple unique page groups. Its progress may be
determined by the final untranslated group rather than by total translation
service volume.

## Existing ability

- R1 groups same-page intra-warp translations.
- Lane B is responsible for the matched finite `WARP_VPN_DEDUP_REFERENCE`.
- Existing TLB MSHRs merge equal miss-side translations.
- Frozen pre-L1 merges exact overlapping physical requests without selecting
  instruction criticality.

## Explicit remaining difference

The proposed predicate recognizes only a currently head-required group of a
multi-page dynamic instruction when every other page group of that instruction
is already translation-ready. It neither groups additional requests nor
predicts future completion.

This differs from MASK's translation-aware memory scheduling, which gives page
walk requests priority and tracks stalled warps, but does not define the
last-unresolved exact page group of a dynamic instruction. RPAWS selects
compute/memory warps from instruction type and global unit pressure, not page-
group completion state. LATPC full-text differentiation remains unknown.

## Online information

- stable dynamic instruction identity;
- exact legal translation group identity;
- current accessq-head group;
- current ready/not-ready bit for every group of that instruction;
- current baseline eligibility and finite service request.

No baseline future timestamp, future trace entry, oracle latency, or future
cache outcome is permitted.

## Fixed finite rule prepared by the fixture

Priority is true iff:

1. the instruction has at least two legal page groups;
2. the candidate is the current accessq-head group;
3. it is baseline-eligible and not ready; and
4. every other group of that same instruction is ready.

A later prototype may use at most the existing service slot and must use stable
arrival order/round robin among equal-priority groups. It may not cancel
already-issued work or add ports.

## Possible cost

- reordering can delay translations for other warps;
- per-live-instruction group/ready bookkeeping;
- priority inversion or starvation unless bounded fairness is retained;
- no benefit if a different downstream dependency dominates progress.

## Minimum counterexample

An instruction with two page groups where both are untranslated is not an H1
opportunity. A single-page instruction is ordinary demand and is also not an
H1 opportunity.

## Required metrics

- multi-page instruction count and group histogram;
- cycles with an accessq-head last-unresolved untranslated group;
- competing finite-service requests in those cycles;
- time from last-group request-ready to translation-ready;
- time from translation-ready to address application and cache admission;
- instruction/warp progress, service counts, and fairness delay to displaced
  requests;
- all existing correctness and quiescence gates.

## Falsification

Reject H1 if any of the following holds:

- Lane B finds no residual request set after the warp reference;
- no measured cycle has the exact last-unresolved condition with competing
  finite service;
- prioritization does not shorten last-group delay or target cycles relative
  to Lane B;
- benefit requires future information, extra ports, cancellation, or an
  unbounded group table;
- a preregistered target regresses by more than 1% without a scoped tradeoff
  that preserves the hypothesis.

## Nearest-work gate

CAC and LATPC full text is still required before claiming the exact
last-unresolved rule is absent from prior compiler/warp-pattern mechanisms.
