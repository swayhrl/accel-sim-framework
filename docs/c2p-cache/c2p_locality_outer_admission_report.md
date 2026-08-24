# C2P 4-SM locality and outer-tail admission report

## Scope

This experiment uses a logical `sid / 4` locality group.  It is independent
of the pre-existing eight-SM ATA/CCD comparator grouping.  `local-first`
orders an ordinary C2P Snapshot candidate list with group-local targets first;
it does not remove candidates.  The optional outer-admission policy makes one
decision only after the entire remaining candidate suffix is outer.  It either
admits that suffix as a normal C2P probe package or sends the request through
the normal lower path.  It never bypasses a local candidate or a request with
no C2P candidate.

The policy feature is a 64-entry address-region × requester-group hash times
four initial-candidate-count bins, with three-bit saturating scores (768 bits
total), threshold 4, initial score 4, and one periodic exploration package per
64 opportunities.  This is a simulator mechanism study, not a claim that the
`d2`/`d4` values below are measured GV100 wire latencies.

## Gates

- The default-off observer must preserve cycles and every base C2P counter.
- `local + outer` candidate/probe/hit/miss counters must conserve their base
  counterpart, and `remote_hits == l2_requests_avoided`.
- Policy decisions partition each eligible outer suffix into predictor
  continue, exploration continue, or predictor bypass.
- `outer-admission-always` has threshold zero, admits every suffix, and must
  be exactly equivalent to local-first C2P in cycle and base C2P counters.

All reported rows passed their applicable gates.

## Integration control

For Btree, `outer-admission-always` exactly matched local-first C2P:

| Workload | Cycles | Probes | Remote hits |
|---|---:|---:|---:|
| Btree local-first C2P | 228,926 | 1,086,806 | 162,087 |
| Btree always-admit | 228,926 | 1,086,806 | 162,087 |

This excludes observer/state-machine overhead as the source of policy results.

## Locality sensitivity

`uniform` is canonical C2P candidate order; `d0` is local-first with no extra
outer delay.  `d2` and `d4` add the stated delay to both outer request and
outer response.

| Workload | Uniform cycles | d0 | d2 | d4 | Interpretation |
|---|---:|---:|---:|---:|---|
| Btree | 229,052 | 228,926 | 228,937 | 227,914 | Small, stable order effect; hit count alone does not determine cycles. |
| 2DConvolution | 700,017 | 697,202 | 703,155 | 701,042 | Local-first helps at d0; modest outer latency erodes that benefit. |
| c2p-ispass-bfs | 186,246 | 184,842 | 185,956 | 186,852 | Local-first helps 0.75%; d4 loses the benefit. |
| c2p-ispass-lps | 102,272 | 102,806 | 103,100 | 103,722 | Ordering alone is a small cost for this workload. |

Default-off observer coverage additionally passed for GEMM: among 5,408,421
candidate queries, local candidates/probes/hits account for 9.82% / 14.11% /
21.86%, respectively.  Thus GEMM has a measurable local-quality skew, but
outer peers still supply the majority of potential hits; it was not used to
tune admission beyond the representative Btree/2D/BFS/LPS matrix.

The completed full-trace PolyBench ATAx observation also passed exact
default-off equivalence and all locality conservation checks.  Across
19,079,126 candidate queries, local candidates/probes/hits account for
15.64% / 15.86% / 26.04%, respectively.  Like GEMM, ATAx has a measurable
local-hit-quality skew without evidence that unconditional outer bypass would
be safe.

## Outer-tail admission

Policy results are relative to the corresponding local-first C2P control.
Positive cycle delta means slower.  The Btree `t3` row is the one conservative
threshold sensitivity point; it has the same predictor except threshold 3.

| Workload | Control cycles | Policy cycles | Delta | Probe change | Remote-hit change | Result |
|---|---:|---:|---:|---:|---:|---|
| Btree (t4) | 228,926 | 237,386 | +3.70% | 1,086,806 → 409,697 | 162,087 → 118,088 | Negative: useful outer hits outweigh probe pressure. |
| Btree (t3) | 228,926 | 237,754 | +3.86% | 1,086,806 → 431,343 | 162,087 → 123,252 | More conservative gating does not repair Btree. |
| 2DConvolution | 697,202 | 678,925 | -2.62% | 4,374,234 → 712,096 | 549,123 → 140,959 | Strong positive: lower-path/queue relief dominates lost hits. |
| c2p-ispass-bfs | 184,842 | 184,142 | -0.38% | 611,892 → 490,030 | 89,996 → 100,246 | Positive: different in-flight timing produces more realized peer hits. |
| c2p-ispass-lps | 102,806 | 101,073 | -1.69% | 189,209 → 85,235 | 62,866 → 44,042 | Positive despite fewer remote hits. |

The final Btree t3 source split is 579,289 initial outer-only opportunities
and 39,743 after-local opportunities.  BFS has 206,607 / 83,747 and LPS has
78,089 / 11,055, respectively.  Btree's 93.6% initial-outer fraction explains
why preserving the after-local tail cannot repair its result.

## Current conclusion

The data rejects an unconditional outer-probe bypass: Btree is a reproducible
negative case even when policy plumbing is proven equivalent under
always-admit.  It supports a bounded AddrTopo-driven admission mechanism only
as a workload-sensitive optimization: LPS, BFS, and 2DConvolution reduce
cycles, while Btree must retain ordinary C2P.  A practical RTL mapping should
therefore keep local candidates mandatory, make one decision per outer suffix,
and retain periodic exploration; it must not use global hit rate alone as a
bypass criterion.

## Reproduction inputs

Backend branch: `hrl/c2p-addr-observe-v0` at `35631982` or newer.
Frontend branch: `hrl/c2p-addr-observe-exp-v0`.

```bash
export C2P_GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-c2p-addr-observe
cd /workspace/worktrees/accel-sim-c2p-addr-observe

scripts/run_c2p_locality_observe.sh --out-root hw_run/c2p-locality-vX \
  --case btree,2DConvolution,c2p-ispass-bfs,c2p-ispass-lps,nn --jobs 1
scripts/run_c2p_locality_sensitivity.sh --out-root hw_run/c2p-locality-sensitivity-vX \
  --case btree,2DConvolution,c2p-ispass-bfs,c2p-ispass-lps --jobs 1
scripts/run_c2p_outer_admission.sh --out-root hw_run/c2p-outer-admission-vX \
  --case btree,2DConvolution,c2p-ispass-bfs,c2p-ispass-lps --jobs 1
scripts/run_c2p_outer_admission.sh --out-root hw_run/c2p-outer-admission-always-vX \
  --case btree --policy-config configs/c2p-cache/c2p-outer-admission-always.config \
  --require-control-equivalence
```

Raw run roots, resolved configs, trace provenance, and host profiles are kept
under the `hw_run/c2p-locality-*` and `hw_run/c2p-outer-admission-*` paths
named in the generated CSV/Markdown results.
