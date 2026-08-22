# C2P+ adaptive confirmation-depth study

Status: Stage 1 is an observation-only experiment.  It is separate from the
canonical C2P paper16 aggregate and from the previous fixed-budget matrix.

## Question and scope

After the C2P+ separate target-tag port removes the first diagnosed bottleneck,
`budget1` is best for 2DConvolution while `budget4` is near-Ideal for Btree
and exhaustive confirmation remains best for ISPASS LPS.  A global fixed cap
is therefore not an acceptable default.

The minimum next question is not “what global cap is best?” but whether a
small predictor can decide after failed confirmations to keep probing or to
send the original miss to L2.  Stage 1 gathers the information needed to make
that choice without changing C2P timing or state transitions.

## Observation contract

The backend records, for every exhaustive C2P+ run:

- exact remote-hit and failed-probe counts at ordinal 1, 2, 3, 4, and an
  overflow bin;
- the same first-four ordinal counts partitioned by a 64-bucket hash of the
  request PC, **offline only**;
- the sampled requester lower injection readiness and selected target FIFO
  credit when a next candidate exists after one or more failed probes.

None of those counters is read by the model.  They create no queues, state,
latency, or arbitration dependency.  A paired NN replay proves that all
pre-existing C2P+ summary fields remain exactly equal to the previous
separate-tag-port result; NN also has zero new probe observations.

The lower-ready sample is specifically the requester memport admission test,
not a prediction of the eventual lower-cache latency.  It is retained only to
reject an obviously unimplementable gating idea.  Likewise, exact simulator
FIFO depth is an observational proxy; a plausible implementation would use a
one-bit target credit/busy indication rather than export arbitrary queue depth.

## Seven-workload Stage-1 matrix

Every row uses exhaustive confirmation (`max_candidate_probes=0`) and
`c2p-separate-target-tag-port.config`.

| Workload | Role | Falsifies |
|---|---|---|
| 2DConvolution | short-stop residual | a policy that always confirms deeply |
| ISPASS LPS | low candidate count / FP tail | a policy that mistakes candidate presence for value |
| Rodinia Btree | high candidate pressure | a policy that stops too early |
| ISPASS BFS | independent graph pressure | a Btree-specific explanation |
| Parboil SGEMM | dense compute / resolved port outlier | an interconnect-only explanation |
| Rodinia Gaussian s=256 | low but nonzero sharing | a policy that overprobes weak opportunity |
| Rodinia NN | no-op negative control | any unintended enabled-C2P+ behavior |

Run and analyze with:

```bash
export C2P_GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-c2p-cache
scripts/run_c2p_adaptive_observation.sh
```

The campaign creates `observation_summary.{csv,md}` and
`observation_pc_buckets.csv` below its output root.  The analyzer verifies:

1. ordinal hit totals equal `c2p_remote_hits`;
2. ordinal miss totals equal `c2p_peer_probe_misses`;
3. first-four PC-hash totals equal their matching ordinal totals.

## Decision gates

Only after Stage 1 completes normally and all counters conserve may an
adaptive behavior be added.

1. Start with a 3-bit saturating global `ordinal × outcome` table and a hard
   maximum of four confirmations.  First candidate is always attempted.
2. Use the PC-hash report only to decide whether the global table is clearly
   insufficient.  Do not add per-PC state merely because individual buckets
   differ at low sample counts.
3. Treat target credit as an optional one-bit cost gate.  Do not use raw
   simulator queue depth as architectural state, and do not infer lower-cache
   latency from `c2p_lower_ready()`.
4. A same-binary `C2P+ exhaustive control` versus `adaptive` pair must first
   pass on these same seven workloads: conservation, NN no-op, no deadlock,
   Gaussian non-regression, and expected opposite depth choices for 2D versus
   Btree/LPS.
5. Only then perform the full 16-trace paired generalization and update
   figures/audit reports.  No adaptive row is mixed into canonical paper
   C2P results.
