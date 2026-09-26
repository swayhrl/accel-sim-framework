# Post-coalescing research-hypothesis screening

## Decision at this checkpoint

`PREP_COMPLETE_AWAITING_BASELINE`

There is not yet evidence for a new mechanism worth formal development. Two
specific, falsifiable residual questions survive source/literature screening,
but both depend on Lane B's matched `WARP_VPN_DEDUP_REFERENCE` request-set and
timing results. No candidate full replay is scientifically authorized before
that handoff.

## What is already established

- R1 directly includes intra-warp requests to the same virtual page being
  coalesced after address generation, separately from unique cache-line
  accesses. Warp VPN deduplication is therefore a necessary reference
  capability, not this lane's innovation.
- Frozen development aggregates satisfy
  `decision lookups - unique pages per dynamic memory instruction = pre-L1
  followers` on all seven development targets. This is a count equality only;
  it neither establishes request-set identity nor proves all followers are
  same-warp/same-instruction.
- Frozen pre-L1 suppresses L1 service on every measured target, while cycle
  response is positive, zero, or negative. Service suppression is not itself
  a remaining scientific problem or a monotonic performance model.
- MASK explicitly describes translation completion causing waiting warps to
  issue data requests consecutively. A generic completion-burst observation is
  prior work, not a candidate.
- RPAWS classifies decoded instructions as compute/memory and uses current
  ALU/LSU issue-queue busy signals. Generic pressure-aware warp scheduling is
  prior work, not a candidate.
- CAC and LATPC full text was not obtained. Their compiler grouping,
  warp-pattern, prefetch, MSHR-compression, and PTW-batching details remain
  unknown wherever the primary text is required.

## Source result

The frozen source separates at least four events:

1. the current access becomes the `accessq_back()` translation decision;
2. the controller lookup reaches READY;
3. the physical address/result is applied to the access;
4. L1D/bypass admission succeeds.

The resident prelaunch scan executes before the accessq-head path and calls the
same finite translation controller. L1D admission checks occur later and may
fail independently. Scoreboard collision state records register hazards, not
the memory/compute origin of the producer, so existing aggregate dependency
counts cannot alone identify translation-caused warp progress loss.

## Surviving questions

### H1: last-unresolved page-group criticality

After the reasonable warp-level VPN reference, does a multi-page dynamic
memory instruction spend cycles with exactly its head-required last page group
untranslated while less critical translation work occupies finite service?

This is narrower than “prioritize stalled warps”: it requires exact dynamic
instruction/group state and distinguishes the last unresolved group from
ordinary single-page demand. See card 1.

### H2: demand before resident prelaunch

Does the current ordering let resident non-head prelaunch consume the existing
one-per-SID L1-TLB port in a cycle where a baseline-eligible accessq-head demand
also needs it, and does demand-first arbitration improve progress versus Lane
B without increasing translation work?

This is an exact arbitration question, not generic pressure scheduling. It may
ultimately be only a conventional demand-over-prefetch control rather than a
new mechanism. See card 2.

## Work performed

- Read and visually checked primary PDFs for R1, MASK, and RPAWS.
- Reviewed the fixed gem5 Vega coalescer source functions at commit
  `56aca813700a6b107f2282f15af5e4d2cad0d0e2`.
- Read the complete frozen pre-L1 and passive-observer patches and accepted
  result/attribution tables.
- Audited request-ready, controller-READY, result-apply, cache-admission, and
  scoreboard source points.
- Added an executable online-only fixture and fourteen directed tests. It is
  not simulator mechanism code and produces no performance result.

## Experiment status

Candidate full replays: **0**.

No target has been selected for a candidate run. If Lane B later closes the
comparison semantics, target selection must be preregistered from its residual
symptoms before any candidate output is viewed. The combined budget remains at
most six full replays, with one fixed configuration per surviving hypothesis.

## Required next action

Fetch Lane B once its execution branch has a committed `CONSUMER_HANDOFF.json`.
Reject H1/H2 if the handoff does not expose their exact prerequisite event or
request set. Independently, obtain CAC and LATPC primary PDFs before making a
novelty distinction that depends on their detailed grouping/arbitration rules.
