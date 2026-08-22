# C2P+ adaptive confirmation-depth study

Status: Stage 1 is complete. Stage 2 implements and evaluates the small
adaptive policy below. It remains separate from the canonical C2P paper16
aggregate and from the previous fixed-budget matrix.

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

## Stage-2 online policy and diagnosis contract

Stage 1 completed normally: ordinal, PC-hash, and remote-hit counters all
conserve on the seven-workload matrix. Strong PC-bucket variation for
2DConvolution, Btree, and SGEMM justifies the smallest useful online state:
a PC-hash rather than a global-only policy.

Adaptive mode is C2P+ only: it retains the separate target-tag port and uses
the exact same binary as the exhaustive control. It changes only the choice to
issue a later candidate probe after an earlier miss.

- Candidate ordinal 1 always probes.
- Ordinals 2--4 have one 3-bit saturating utility score per
  `PC-hash[6:0] x ordinal` entry (64 x 4 entries), initialized to 4.
- A remote hit adds 2; a failed peer probe subtracts 1; scores saturate at
  0 and 7. Score >= 4 continues probing. This is a utility threshold near the
  one-third hit-rate break-even point, not a 50%-accuracy classifier.
- A low-score entry is still forced to continue once per 64 continuation
  opportunities. This bounded exploration avoids permanent censorship of a
  cold or unlucky PC bucket.
- A hard cap of four probes is unconditional. There are no new queues, ports,
  arbitration dependencies, or timing stages.

The backend additionally records the information needed to distinguish a bad
policy from an inherently unhelpful candidate tail:

| Counter family | Diagnosis it enables |
|---|---|
| `c2p_adaptive_{first,predictor,exploration}_probe_{hits,misses}` | Value of compulsory first probes, learned probes, and exploration separately |
| `c2p_adaptive_continue_{predictor,exploration}` | How much depth is policy-selected versus forced for learning |
| `c2p_adaptive_stop_{predictor,hard_cap}` | Whether the policy stops early or simply reaches the architectural cap |
| `c2p_adaptive_stop_{later_peer,no_later_peer}` | At an adaptive stop, whether a remaining exact candidate could have produced a remote hit (lost opportunity) or would only have been a false-positive tail (saved work) |
| `c2p_adaptive_stop_next_peer_distance_total` | How far the first missed opportunity is from the stop point |
| `c2p_adaptive_score_[0..7]_samples` | Score-table occupancy; detects collapse to a single threshold side |

The later-peer scan is diagnostic only. It uses the simulator's existing
read-only tag lookup after the policy has already stopped; it does not reserve
a target port, change fallback timing, or make architectural state visible.

Run the same-binary seven-pair matrix with:

```bash
export C2P_GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-c2p-cache
scripts/run_c2p_adaptive_pairs.sh
```

`pair_summary.{csv,md}` rejects a run unless all of the following hold:

1. every control exactly matches the already-recorded exhaustive observation
   result for all non-adaptive C2P counters;
2. remote-hit/avoided-L2 and ordinal conservation hold for both variants;
3. issued probe reasons partition into first, predictor, and exploration;
4. continuation and stop classifications each conserve; and
5. NN is bit-for-bit a no-op: cycles, normal C2P counters, and all adaptive
   activity counters stay unchanged/zero.

## Decision gates

Only after Stage 1 completes normally and all counters conserve may an
adaptive behavior be added.

1. Start with a 3-bit saturating `PC-hash × ordinal` utility table and a hard
   maximum of four confirmations. First candidate is always attempted.
2. The table must remain small enough to avoid new timing or queue structure;
   do not add per-PC state beyond the selected hash merely because an
   individual bucket differs at low sample counts.
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
