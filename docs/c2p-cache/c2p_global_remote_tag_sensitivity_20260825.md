# C2P global remote-tag 7-to-14-cycle sensitivity

## Question and contract

This experiment asks a narrow question: what changes if every C2P remote
**target tag lookup** takes 14 cycles instead of the canonical seven? It is
not the earlier `d2`/`d4` experiment: those add delay only for the outer
4-SM-group path, whereas this point changes the common remote lookup path for
all peer targets.

Every replay uses the capacity-preserving paper-table configuration and holds
the following values fixed:

- remote return latency = 2 cycles;
- shared L2 path latency = 200 cycles;
- Snapshot geometry, target FIFO/timeout, Bloom hashes, and all C2P queue
  settings;
- 64 simulated SM endpoints and the fixed 64-KiB L1 configuration.

The `tag14` overlay contains only
`-c2p_cache_remote_tag_latency 14`. Thus a no-contention remote peer return
changes from 7 + 2 = 9 cycles to 14 + 2 = 16 cycles; it does not change L2
latency or the response leg.

## Audit gates

The runner reads each final `gpgpusim.config`, rather than assuming defaults,
and rejects a replay unless its final settings are remote tag = 7 or 14 as
named, remote return = 2, L2 = 200, and its named locality/policy mode. Every
completed row also satisfies `c2p_remote_hits == c2p_l2_requests_avoided`.
Outer-admission rows additionally satisfy the decision partition and the
training-count bound. All gates passed.

Backend provenance is `hrl/c2p-addr-observe-v0` at `35631982`; the runner and
resolved-default infrastructure are frontend commits `542f1fb`, `221b1ad`, and
`3cb1865` or newer.

## Stage 1: canonical C2P

| Workload | Tag7 cycles | Tag14 cycles | Cycle delta | Tag7 / Tag14 probes | Tag7 / Tag14 remote hits | Tag7 / Tag14 L2 accesses |
|---|---:|---:|---:|---:|---:|---:|
| Btree | 229,052 | 231,218 | +0.95% | 1,086,793 / 962,422 | 161,628 / 88,195 | 1,259,116 / 1,333,482 |
| 2DConvolution | 700,017 | 707,580 | +1.08% | 4,392,833 / 3,850,661 | 556,059 / 319,699 | 5,438,832 / 5,678,568 |
| c2p-ispass-bfs | 186,246 | 187,553 | +0.70% | 613,335 / 484,340 | 87,877 / 51,481 | 987,449 / 1,023,959 |
| c2p-ispass-lps | 102,272 | 104,598 | +2.27% | 186,728 / 167,195 | 62,919 / 42,351 | 348,281 / 368,849 |

The expected effect is visible in all four cases: longer lookup makes some
candidate lines disappear before the delayed probe reaches them, reducing both
completed probes and realised remote hits, while increasing L2 fallbacks. The
cycle impact is much smaller than the 7-cycle increment because the common
alternative remains a 200-cycle L2 path and the model overlaps some work.

## Stage 2: 4-SM local-first C2P

This phase keeps all candidates and merely orders targets in the requester's
`sid / 4` group first. It does not apply outer-tail admission.

| Workload | Local-first tag7 | Local-first tag14 | Tag14 delta | Tag14 local-first vs canonical tag14 |
|---|---:|---:|---:|---:|
| Btree | 228,926 | 230,284 | +0.59% | -0.40% |
| 2DConvolution | 697,202 | 700,528 | +0.48% | -1.00% |
| c2p-ispass-bfs | 184,842 | 187,909 | +1.66% | +0.19% |
| c2p-ispass-lps | 102,806 | 104,357 | +1.51% | -0.23% |

Local ordering therefore remains useful for Btree, 2DConvolution, and LPS
when the common remote lookup slows, especially 2DConvolution. It is not
uniformly positive: BFS becomes a small negative ordering point at tag14.
This is a timing/queue interaction, not evidence that locality counters are
incorrect; all candidate/probe/hit partitions conserve their base counters.

## Stage 3: outer-tail admission where prior evidence justified it

The paired policy matrix was run for 2DConvolution, BFS, and LPS. These are
the previous tag7 probe/queue-pressure positive cases. Btree was deliberately
not repeated here: it is already a stable admission negative under both t4 and
t3, and its modest local-order benefit does not establish outer-tail admission
value. This preserves Btree as a boundary case rather than silently treating a
locality benefit as a bypass benefit.

| Workload | Control 7 / policy 7 cycles | Policy delta 7 | Control 14 / policy 14 cycles | Policy delta 14 | Interpretation |
|---|---:|---:|---:|---:|---|
| 2DConvolution | 697,202 / 678,925 | -2.62% | 700,528 / 676,172 | -3.48% | Longer remote lookup increases the value of suppressing poor outer tails. |
| c2p-ispass-bfs | 184,842 / 184,142 | -0.38% | 187,909 / 187,950 | +0.02% | Becomes effectively neutral/slightly negative. |
| c2p-ispass-lps | 102,806 / 101,073 | -1.69% | 104,357 / 102,899 | -1.40% | Still a positive point, with reduced margin. |

For 2DConvolution, tag14 policy reduces probes from 3,831,378 to 609,756 and
remote hits from 313,527 to 89,661, while cycles improve by 3.48%. This makes
the central point explicit: a remote-hit count is not itself the objective;
the policy can profit by avoiding low-quality, queue-expensive tails. LPS has
the same qualitative tradeoff. BFS shows its limit: the tag7 probe relief is
insufficient once all remote lookup is slower, so there is no basis for an
always-on policy.

## Conclusion

The experiment supports keeping remote-tag latency, local ordering, and
outer-tail admission as separate knobs:

1. A global 7-to-14-cycle tag lookup sensitivity is modest in total cycles but
   substantially changes realised peer hits and L2 pressure; it cannot be
   inferred from the prior outer-only `d2`/`d4` points.
2. Local-first ordering has a more favourable tag14 effect for 2DConvolution
   and Btree, but not for every workload.
3. AddrTopo outer-tail admission remains workload-sensitive. It becomes more
   attractive for 2DConvolution, remains beneficial for LPS, and loses its
   small BFS margin. Btree remains excluded by established negative evidence.

An RTL-feasible policy should consequently retain local candidates, make one
decision per outer suffix, use bounded exploration, and expose remote latency
as a configuration/sensitivity parameter. It should not derive admission from
a global remote-hit rate or enable a universal bypass.

## Reproduction

```bash
export C2P_GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-c2p-addr-observe
cd /workspace/worktrees/accel-sim-c2p-addr-observe

scripts/run_c2p_remote_tag_sensitivity.sh \\
  --out-root hw_run/c2p-remote-tag-v2-YYYYMMDD --phase canonical \\
  --case btree,2DConvolution,c2p-ispass-bfs,c2p-ispass-lps --jobs 2
scripts/run_c2p_remote_tag_sensitivity.sh \\
  --out-root hw_run/c2p-remote-tag-v2-YYYYMMDD --phase locality \\
  --case btree,2DConvolution,c2p-ispass-bfs,c2p-ispass-lps --jobs 2
scripts/run_c2p_remote_tag_sensitivity.sh \\
  --out-root hw_run/c2p-remote-tag-v2-YYYYMMDD --phase admission \\
  --case 2DConvolution,c2p-ispass-bfs,c2p-ispass-lps --jobs 2
```

This campaign's raw outputs, resolved configs, trace/binary provenance, host
profiles, CSVs, and checked Markdown summaries are in
`hw_run/c2p-remote-tag-v2-20260825/{canonical,locality,admission}/`.
