# Design rationale

The selected placement is the earliest point at which frozen V1 has committed
to a real physical L1 request but before that request consumes L1 service. It
therefore avoids proactive speculation and removes a population unavailable to
miss-side MSHRs. Exact identity and bounded fallback preserve legality and
liveness. Prior project evidence rules out blocking result sharing, fanout-only
repair, proactive no-opportunity ownership and post-result forwarding as clean
solutions for this specific duplication population.

The choice does not claim optimality against untested larger TLB/MSHR designs.
`DESIGN_SPACE_COMPARISON.tsv` is structural, not fabricated performance data.
