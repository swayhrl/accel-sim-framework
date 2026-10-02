# Codex Goal — Lane F / node109
## AWMA R22F1 low-overhead OpenEquivariance family replay V1

Date: 2026-10-02

Repository:
`swayhrl/accel-sim-framework`

Execution branch:
`hrl/awma-r22f1-oeq-lowoverhead-replay-109-v1`

Scientific parent:
`df0e8edd009ee1a56ba65b25b319e8a852f74d27`

Stage:
`AWMA_R22F1_OEQ_LOWOVERHEAD_REPLAY_109_V1`

Review pack:
`docs/vm_tlb/review_packs/AWMA_R22F1_OEQ_LOWOVERHEAD_REPLAY_109_V1/`

One bounded solve-and-continue Goal.

The only question:

> When the exact TP call inputs and upstream gradients are held fixed, is deterministic OpenEquivariance actually faster or slower than atomic on the real OAM-S TP family when measured without NSYS?

This is a diagnostic of the existing R22F discrepancy.
Do not run Donline or change the model/input.

---

# 0. Frozen authority

Reuse exactly parent R22F/R21A:
- OAM-S:0.1 package SHA
  `63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa`
- sitraj frame 55
- 64 Si
- 1394 directed periodic edges
- accepted source-backed sorted graph
- accepted sender transpose permutation
- float32
- TF32 OFF
- `atol=rtol=5e-5`
- pinned NequIP / OEQ versions
- same Aorder atomic and Dready deterministic TPProblem / weights.

Historical parent measurements are read-only:
- R22F NSYS family table
- R22F uninstrumented complete timing.

Do not pool new replay timing into historical full-model timing.

---

# 1. Source/launch audit before GPU timing

From pinned OEQ source and parent family members, freeze:

- number and order of TP convolution calls in the two interaction layers during one energy+force evaluation;
- atomic forward/main/fixup launch structure;
- deterministic forward/main/fixup launch structure;
- backward/main/fixup launch structure;
- parent NSYS per-call/aggregate fixup durations;
- parent uninstrumented Aorder->Dready complete-region delta.

Record:
`PARENT_DISCREPANCY_CONTRACT.md`

Important source fact:
atomic OEQ still launches empty `fixup_forward` / `fixup_backward`; deterministic uses nonempty fixup kernels. This alone does not establish uninstrumented fixup cost.

---

# 2. Capture exact semantic TP records

Under GPU lock, use one diagnostic-only non-timed real OAM-S energy+force execution.

Use the accepted sorted graph for both implementations.

Canonical capture source:
Aorder / atomic on the sorted graph.

For every TP convolution call participating in the two interaction layers, capture the exact inputs needed to replay:
- callsite/layer identity
- TPProblem / kernel configuration identity
- X/node features
- edge attributes Y
- weights W
- receiver rows
- sender cols
- any shared/static metadata.

For force backward, capture the exact upstream gradient presented to that TP output during the real energy->forces autograd traversal.

Capture all actual callsites observed; do not assume exactly two if source/runtime shows more.

Persist compact tensors/hashes on node164.

The capture run must still pass the parent energy/force numerical contract.

Write:
- `TP_CALL_RECORDS.tsv`
- `TP_CAPTURE_AUTHORITY.json`

If exact backward upstream gradients cannot be captured without changing the force computation:
`R22F1_EXACT_FAMILY_REPLAY_NOT_QUALIFIED`
STOP.

No synthetic/random tensors.

---

# 3. Reconstruct exact Aorder and Dready replay arms

For each captured call record instantiate/use the exact pinned OEQ implementation corresponding to:

Aorder:
- sorted rows/cols
- atomic `deterministic=False`
- no sender permutation consumed.

Dready:
- exact same sorted rows/cols
- deterministic `True`
- accepted sender transpose permutation.

Prefer reusing the model's actual OEQ module/TPProblem objects or exact source-backed configuration rather than constructing an approximate problem.

Record for each arm/callsite:
- OEQ problem/config identity
- workspace size
- kernel/JIT hash or strongest available implementation identity
- tensor shapes/dtypes.

Do not include module construction, JIT compilation or workspace allocation in timing.

---

# 4. Standalone numerical qualification

For each callsite, using exactly the same captured input tensors:

## Forward
Compare Aorder vs Dready output at `5e-5`.

## Backward
Using the captured real upstream gradient, compare gradients required by the model for:
- X
- edge attributes if differentiable/used
- weights if required by the force path.

Do not request training-only parameter gradients that were not part of the captured force traversal.

Require finite outputs/gradients.

If same-input standalone atomic/deterministic semantics do not qualify:
`R22F1_EXACT_FAMILY_REPLAY_NOT_QUALIFIED`
STOP.

---

# 5. Low-overhead timing protocol

No profiler.

Primary measurement uses CUDA events on the same stream.

Avoid timing Python/model construction.

For each callsite and arm:

## Forward-only
- 10 warmup replays
- 5 formal groups
- each formal sample brackets a fixed bundle of 32 identical forward replays with one start/end event pair
- divide elapsed time by 32
- 8 formal bundle samples per group
- alternate arm order by group.

## Backward
Primary backward measure:
- prepare the required autograd forward state outside the timed interval for each replay;
- bracket only the backward/autograd execution that consumes the captured upstream gradient;
- 10 warmups
- 5 groups
- fixed bundle/repetition plan chosen before reading timings
- alternate arm order.

If bundling backward graphs materially changes memory behavior or cannot be done cleanly, use one backward replay per event pair with 20 formal samples/group; freeze this fallback before reading arm timing.

Also compute a **combined semantic family cost**:
sum the measured forward and force-backward costs according to the exact call multiplicities from Section 2.

This combined cost is the primary family result.

Record wall launch/submit time only as secondary diagnostics.
CUDA-event semantic-family elapsed is primary.

---

# 6. Optional exact fixup micro-control

Only if the pinned OEQ internal API exposes the already-compiled exact fixup kernels without source modification or broad plumbing:

time:
- atomic empty fixup_forward/backward
- deterministic nonempty fixup_forward/backward

using the exact captured workspace/output shapes.

Use CUDA events and the same bundled protocol.

This optional micro-control must not block the Goal.

If unavailable, mark `FIXUP_DIRECT_TIMING_NOT_AVAILABLE`.

Do not write a new fixup implementation.

---

# 7. Compare with parent evidence

Create:
`EVIDENCE_RECONCILIATION.md`

For each semantic family/callsite report:

- parent NSYS duration
- new low-overhead replay CUDA-event time
- ratio/difference
- parent complete-region Aorder->Dready response.

Classify:

## A. Low-overhead net family is consistently faster for Dready
`R22F1_LOWOVERHEAD_FAMILY_RESPONSE_POSITIVE`

Requirements:
- all callsites numerically qualify
- aggregate combined family has all 5 group medians favor Dready
- median gap >3x larger-arm group-MAD estimate
- no callsite shows an unexplained large opposite response.

Interpretation:
the parent NSYS net-family regression is not representative of low-overhead family elapsed on this scope.
Do not overstate exact cause unless optional fixup or launch evidence proves it.

Output one future proposal to measure online graph-preparation net cost.
Do not execute Donline here.

## B. Low-overhead net family is consistently slower for Dready
`R22F1_TARGET_FAMILY_NET_NEGATIVE`

Then the uninstrumented full-model improvement cannot be attributed to a positive standalone TP-family cost.
Use source/launch evidence to identify the most likely broader scheduling/context explanation if possible, but keep unproven causes explicit.

STOP R21A as a target-family mechanism candidate.
Do not run Donline.

## C. Low-overhead replay remains mixed/uncertain
`R22F1_FAMILY_GAP_UNRESOLVED`

STOP.
Do not add more samples, another profiler, larger model, frame, or holdout.

---

# 8. Scope limits

Forbidden:
- new NSYS
- NCU/NVBit/SASS
- Donline graph-preparation timing
- old R21A holdouts
- model-size sweep
- new frame
- neighbor search
- MD
- training/double backward
- node174/Accel-Sim
- hardware implementation.

This Goal resolves a measurement discrepancy only.

---

# 9. Resource / failure policy

All CUDA/JIT/replay:
`/data/c16/locks/c16_gpu_campaign.lock`

Persist lock acquire/release timestamps.

Large captured tensors/raw -> node164.

Before scientific STOP preserve:
- exact call record hashes
- outputs/gradients
- first mismatch
- timing raw
- environment.

---

# 10. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R22F1_OEQ_LOWOVERHEAD_REPLAY_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- PARENT_AUTHORITY.json
- PARENT_DISCREPANCY_CONTRACT.md
- TP_CAPTURE_AUTHORITY.json
- TP_CALL_RECORDS.tsv
- REPLAY_IMPLEMENTATION_IDENTITY.tsv
- REPLAY_CORRECTNESS.tsv
- FORWARD_TIMING.tsv
- BACKWARD_TIMING.tsv
- COMBINED_FAMILY_SUMMARY.tsv
- FIXUP_TIMING.tsv
- EVIDENCE_RECONCILIATION.md
- NEXT_STEP_PROPOSAL.md
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Unreached items marked NOT_RUN.

---

# 11. Closure

Publish one exact commit.
Push/fetch-back verify SHA/tree.
Release GPU lock.
Terminate GPU processes.
Worktree clean.
STOP.

Final Chinese report must lead with:
1. exact captured TP callsites and multiplicities;
2. same-input atomic vs deterministic forward result;
3. same-input force-backward result;
4. combined low-overhead family response;
5. whether deterministic fixup cost matches or diverges from NSYS;
6. reconciliation with the parent +2.878% full-region response;
7. whether online-prep validation is now justified.

Do not lead with historical 4.7% or another complete-model gate.
