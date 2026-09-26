# Negative and rejected cases

1. **Current pre-L1 coalescing as novelty.** Rejected pending a reasonable
   warp-instruction reference and closest-work closure. Aggregate count equality
   is not request-set equivalence.
2. **Same-warp VPN deduplication.** Existing capability in R1; Lane B reference,
   not a Lane E candidate.
3. **Generic completion-burst suppression.** MASK section 4.1 already identifies
   consecutive data requests after translation completion.
4. **Generic pressure-aware scheduling.** RPAWS already combines decoded
   compute/memory type with live ALU/LSU busy state; MASK schedules translation
   and demand traffic using translation awareness.
5. **“Prioritize stalled warps” without exact group state.** Too broad and too
   close to MASK. H1 survives only as the last-unresolved multi-page predicate.
6. **Demand-before-prefetch as an automatic innovation claim.** H2 is a
   diagnostic hypothesis; the principle is conventional, and LATPC's exact
   arbitration is unknown.
7. **Translation-ready equals progress-ready.** False in source. Address apply
   and L1D/interconnect admission occur later and may block independently.
8. **Scoreboard dependency equals translation dependency.** Unsupported: the
   scoreboard carries register hazards without producer-class provenance.
9. **Use of future trace/completion time.** Forbidden for both decisions. The
   fixture accepts only current state and arrival order.
10. **Unlimited result broadcast, extra ports, free cancellation, or hidden
    duplicate work.** Outside the scientific contract.
11. **A1/A2 as complete warm-context execution.** Their traces originate from
    different contexts, but each simulator receipt replays one kernel from a
    fresh process; complete preceding execution is absent.
12. **CAC/LATPC absence claims.** Rejected until their primary full text is
    obtained. Primary metadata/abstract is retained only as a known boundary.
13. **Reusing REDUCE or Pair C as a new holdout.** Forbidden; both are already
    seen evidence for this research line.
