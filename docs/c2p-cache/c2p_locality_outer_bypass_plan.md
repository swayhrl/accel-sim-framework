# C2P locality and outer-probe admission experiment

## Scope and non-goals

This experiment partitions the simulator's 64 logical SM endpoints into
`sid / 4` locality groups.  It is intentionally independent from the existing
eight-SM ATA/CCD comparator grouping.  The canonical C2P configuration,
candidate ordering, and remote latency remain unchanged unless a sensitivity
overlay explicitly enables them.

The purpose is to determine whether an address/topology policy should avoid
*outer* C2P probes.  It is not an all-request C2P bypass experiment: a local
candidate is never discarded by the policy.

## Staged evidence

1. **Default-off observation.**  Run matched C2P control and observation
   replays.  They must have identical cycles and all base C2P counters.  The
   observer partitions Snapshot candidates, issued probes, and completed peer
   results into local and outer classes.
2. **Two-tier latency sensitivity.**  Compare canonical uniform timing with
   local-first order and explicit `0`, `2`, and `4` cycle outer additions on
   both probe and return.  These values are sensitivity points, not a claim
   about a particular Volta physical topology.
3. **Admission policy only if stages 1--2 support it.**  A candidate list with
   a local member starts with that local member.  Once all untried candidates
   are outer, that complete remaining outer tail is either admitted as one
   package or sent directly to the ordinary lower path.  Exploration is
   mandatory because a bypassed request has no online peer-hit label.

## Planned policy contract

The candidate feature is a fixed-size address-region × requester-group4 hash
and initial candidate-count bin.  It must have the same three-bit counter
budget as the comparison policy.  A remote hit reinforces continuation;
a completed outer package with no peer hit weakens it.  The first outer
candidate remains periodically explored, and every policy decision is
accounted as either predictor continuation, exploration, or direct fallback.

Correctness and accounting invariants for a behavioral variant are:

- `remote_hits == l2_requests_avoided`;
- issued local plus outer probes equals `peer_probes`;
- completed local/outer hit/miss accounting is separately reported (a probe
  can be outstanding only before the simulator drains at exit);
- an outer-bypassed accepted transaction reaches exactly one normal lower
  request through `WAIT_FALLBACK`, never a synthetic fill;
- policy decisions partition every eligible outer opportunity; and
- the policy does not bypass a no-candidate request, which already uses the
  normal lower path without a C2P probe.

The final report records the fixed binary commit, resolved configs, trace
checksums, host profiles, and per-workload results.  A policy will be rejected
if locality observation does not show stable outer false-probe pressure or if
the policy fails to improve its explicitly stated latency/cost objective.
