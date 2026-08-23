# C2P+ confirmation-policy matrix

This campaign compares three C2P+ confirmation paths on every locally
compatible trace:

| Variant | First probe | Later confirmation | Predictor state |
|---|---|---|---|
| `control` | mandatory | exhaustive | none |
| `pc` | mandatory | bounded package through ordinal four | 64 PC-hash x 4 candidate-bin, 3-bit |
| `addr` | mandatory | bounded package through ordinal four | 64 address-region x requester-cluster-hash x 4 candidate-bin, 3-bit |

`pc` and `addr` have the same 256 3-bit entries (768 logical state bits),
threshold, update rule, exploration period, candidate-bin boundaries, and
four-probe hard cap.  They differ only in the package-table feature index.
The address policy first hashes the cache-line tag into 32 regions, combines
that region with the requester cluster, then folds the pair into 64 entries.
It therefore does not require an instruction PC at an RTL L2 interface.

## Qualification order

1. The read-only BFS/LPS/Btree address observation must show nontrivial
   feature separation.  Its audit is retained under
   `hw_run/c2p-addr-topology-observe-v1-20260823`.
2. Matched ISPASS BFS/ISPASS LPS/B+tree `control`/`pc`/`addr` pilot replays must exit
   normally and pass the strict analyzer before the 24-workload sweep starts.
3. The sweep runs 16 canonical traces and eight V100-generated extension
   traces in separate output tiers.  The canonical 16 are the primary
   aggregate; the eight extension traces are reported independently.  A
   combined 24-workload aggregate is explicitly an extension view.

## Retained pilot evidence

The original v1 pilot and its 24-workload continuation are retained as
**pre-clean diagnostic data only**. Their PC policy had an additional PC-hash
× ordinal side table for the two lower candidate bins; this violates the
later, stricter requirement that PC and AddrTopo use exactly one matched
64 × 4 × 3-bit table. The legacy results remain useful for locating the
ATAX/BFS/B+tree counterexamples, but they are excluded from every qualified
aggregate and final comparison.

The clean qualification sequence is rerun with the simplified package-only
implementation: first the exact three-case B+tree/ISPASS BFS/ISPASS LPS
pilot, then the full 16+8 matrix. The analyzer accepts a named manifest subset
only for that pilot and reports it explicitly as a subset; its default mode
still rejects any matrix that is not exactly the checked-in 16+8 manifests.

## Required invariants

- Each mode of a triplet has identical frontend/backend binary hashes and
  trace hash; only its named confirmation overlay differs.
- `c2p_remote_hits == c2p_l2_requests_avoided` for all three variants.
- Adaptive probe issue reasons partition `c2p_peer_probes`.
- Continuation, package decision, package outcome, stopped-tail, and package
  residual-opportunity counters each conserve independently.
- A `package residual opportunity` means a package exhausted its four probes
  while Snapshot candidates remained.  It records whether an exact peer was
  still reachable beyond that cap; it does not affect timing.

## Reproduction

```bash
export C2P_GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-c2p-addr-observe
scripts/run_c2p_confirmation_policy_matrix.sh \
  --out-root hw_run/c2p-confirmation-policy-v2-pilot-20260823 \
  --case c2p-ispass-bfs,c2p-ispass-lps,btree --jobs 1
```

After the pilot passes, omit `--case` to run both manifests.  `--jobs` is the
number of concurrent workload triplets; each triplet itself runs its three
matched variants concurrently.  The runner copies executable/config/
provenance into every run directory and invokes the strict analyzer at the end.
