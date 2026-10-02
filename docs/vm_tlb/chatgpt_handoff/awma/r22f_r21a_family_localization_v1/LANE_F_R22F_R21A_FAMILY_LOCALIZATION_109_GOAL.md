# Codex Goal — Lane F / node109
## AWMA R22F R21A kernel-family localization V1

Date: 2026-10-02

Repository:
`swayhrl/accel-sim-framework`

Execution branch:
`hrl/awma-r22f-r21a-family-localization-109-v1`

Scientific parent:
`62af34149d45e9862d5a1e255e2a51ca88a3c4c7`

Stage:
`AWMA_R22F_R21A_FAMILY_LOCALIZATION_109_V1`

Review pack:
`docs/vm_tlb/review_packs/AWMA_R22F_R21A_FAMILY_LOCALIZATION_109_V1/`

Read-only methodology authority:
- `origin/hrl/awma-chatgpt-literature-notes-v1@fc1351e9e62f2a1aa12c323823e24d30357a8a9d`
- `docs/vm_tlb/literature_notes/awma/methodology/KERNEL_FAMILY_FIRST_REVIEW_V1.md`
- `docs/vm_tlb/literature_notes/awma/plans/2026-10-02_POST_ROUND22_RESEARCH_PLAN_V1.md`

Do not merge that branch into the execution branch merely to read it.

This is one bounded solve-and-continue Goal.

---

# 0. Fixed scientific scope

Reuse exactly the accepted R21A authority:

Model:
`nequip.net:mir-group/NequIP-OAM-S:0.1`

Accepted package SHA256:
`63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa`

Input:
pinned `sitraj.xyz` frame 55 of 110.

Natural graph:
- 64 Si atoms
- 1394 directed periodic edges
- accepted natural graph/shift identity from parent
- receiver-major, sender not monotonic within receiver rows.

Numerics:
- float32
- TF32 OFF
- same OAM-S weights
- energy + forces
- `atol=rtol=5e-5`
- existing e3nn implementation reference.

Compiled mode:
same qualified NequIP AOTInductor ASE CUDA path used by accepted A0 and Dready.

Parent arms:
- A0 = natural graph + OpenEquivariance atomic
- Dready = source-backed composite receiver/sender sorted graph + deterministic OEQ, prepared representation resident before timing.

Historical R21A timing remains historical. Do not delete group 0, change the 5% gate, or relabel the old result.

---

# 1. Family taxonomy must be frozen before new profiling

From pinned NequIP/OEQ source and accepted compiled artifacts, write:
`FAMILY_CONTRACT.md`

Define semantic families before looking at new family timing:

## F_TP_FORWARD
All GPU work implementing tensor-product convolution / aggregation for the two OAM-S interaction layers in the energy forward.

## F_TP_FORCE_BACKWARD
All GPU work implementing the corresponding tensor-product / graph aggregation contribution required to produce forces by autograd.

Do not include parameter-training gradients or double backward.

## F_DET_AUX
Mandatory deterministic-path work that exists because deterministic OEQ is selected, including any fixup/reduction/initialization/reset work not present in the atomic path.

This is part of the **net target-family cost**. It may not be hidden in non-target.

## F_NON_TP
All remaining energy+force GPU work.

If a kernel fuses target and non-target semantics and cannot be separated, classify it as `F_MIXED` and keep it separate. Do not assign it to the favorable side by name.

Also freeze exact graph-node / launch / source attribution rules before reading family timings.

---

# 2. Aorder optional ordering-only diagnostic

Create one opt-in/default-OFF diagnostic arm if it can be implemented cleanly:

Aorder:
- exactly the accepted Dready sorted graph and edge-aligned periodic shifts;
- OpenEquivariance remains `deterministic=False`;
- same model weights, compiled mode, dtype and outputs as A0;
- no deterministic sender permutation is consumed by the atomic TP.

Purpose:
separate graph ordering effects from deterministic aggregation effects.

Aorder is NOT a deployment candidate.

At most two bounded engineering repairs.

If Aorder cannot use the same strong compiled mode without broad model rewrite:
- mark `AORDER_NOT_CLEAN`;
- omit Aorder;
- continue A0 vs Dready family localization;
- explicitly retain "ordering and aggregation effects not fully separated."

Aorder must not block the main Goal.

Before profiling, qualify Aorder numerically with the same five-evaluation energy/force contract if it exists.

---

# 3. OFF/source identity and lock discipline

All CUDA/JIT/profile/timing uses:
`/data/c16/locks/c16_gpu_campaign.lock`

Record acquisition/release timestamps durably in the runner.

Do not run formal timing while Lane G/E CPU tasks are compiling, hashing large trees or doing heavy I/O on node109.

Reverify:
- accepted model/input/artifact SHA
- CUDA/driver/PyTorch/NequIP/OEQ versions
- compiled artifact identity.

No environment upgrade unless the accepted parent environment is unavailable.
Ordinary path fixes may continue; scientific identity changes STOP.

---

# 4. One bounded profiler bundle

At most ONE new NSYS scientific job.

Purpose:
map compiled launches/graph nodes to the frozen semantic families and obtain a repeated **profiled family-response diagnostic**.

No NCU/NVBit/SASS.

The profiler job may contain multiple arm invocations inside one process.

Use NVTX to delimit:
- arm
- repetition
- complete energy+force invocation.

Preferred arm set:
A0, Aorder if qualified, Dready.

Use a fixed balanced sequence chosen before launch.
Run 3 blocks; each block contains 4 measured invocations per available arm after profiler warmup.

Preserve all samples.

If CUDA Graph node tracing is required to attribute families, enable it; record profiler overhead warnings. Do not treat profiled kernel-duration sums as uninstrumented wall contribution.

Family attribution passes only if:
- >=95% of GPU kernel duration inside each invocation is assigned to one frozen family or explicitly F_MIXED;
- target family membership is source-backed, not inferred only from timing;
- repeated invocations give internally consistent kernel membership.

If attribution cannot qualify:
`R22F_FAMILY_ATTRIBUTION_NOT_QUALIFIED`
STOP. Do not start NCU to rescue it.

Write:
- `PROFILE_RECEIPT.json`
- `FAMILY_MEMBERS.tsv`
- `PROFILED_FAMILY_TIMING.tsv`

---

# 5. Family-level calculations

For each arm, block and repetition compute:

- gross TP forward time
- gross TP force-backward time
- deterministic mandatory auxiliary time
- net target-family time =
  `F_TP_FORWARD + F_TP_FORCE_BACKWARD + F_DET_AUX + target-owned F_MIXED if any`
- non-target time
- complete profiled GPU time.

Comparisons:

## Ordering effect
A0 vs Aorder, if available.

## Aggregation effect
Aorder vs Dready, if Aorder exists.
Otherwise A0 vs Dready is a combined ordering+aggregation effect.

## Net target response
Always report the net target-family comparison including deterministic auxiliary work.

A "stable family response" means:
- all 3 block medians have the same direction, AND
- median absolute arm difference exceeds 3x the larger-arm block-MAD estimate.

This is a noise rule, not a universal performance threshold.
Report the actual percent and microsecond effect; do not require >=5%.

Do the same directional/noise check for F_NON_TP regression.

If the profiler perturbs absolute time but arm ratios are stable, keep the result at `PROFILED_FAMILY_DIAGNOSTIC` evidence level; do not call it uninstrumented latency.

---

# 6. Fresh uninstrumented complete-boundary timing

This round needs a new complete-region check because Aorder is new and old R21A group 0 was noisy.

No profiler during timing.

Available arms:
- A0
- Dready
- Aorder only if qualified.

Before reading timings freeze:
- one process/session
- compilation complete before timing
- 5 warmup invocations per arm
- 4 formal groups
- 6 formal samples per arm/group
- fixed Latin-style order rotation across groups
- same input and graph payload for each arm
- synchronization and output verification symmetric.

Record:
- wall
- CUDA event
- energy/force numerical pass
- raw sample values
- medians and MADs.

This timing answers complete energy+force behavior only.
It does not override the profiled family attribution.

No universal 5% gate.

Report:
- median complete-region response
- all four group directions
- group noise
- whether complete response is CLEAR / MIXED / NO_RESPONSE under the same sign + 3xMAD rule.

The prior R21A timing is retained as historical evidence and compared descriptively, not pooled into the new samples.

---

# 7. Decision matrix

Do NOT automatically run Donline.

## Case A — net target family has no stable positive response
Decision:
`R22F_R21A_TARGET_FAMILY_RESPONSE_NOT_ESTABLISHED`

STOP.
Do not switch model size/frame to find a positive result.

## Case B — gross TP improves but mandatory deterministic auxiliary work removes the net gain
Decision:
`R22F_R21A_DETERMINISTIC_AUX_COST_DOMINATES`

Identify the exact auxiliary family and nearest existing software capability.
STOP with at most one future diagnostic proposal.

## Case C — net target family has a stable positive response, non-target has no stable material regression
Decision:
`R22F_R21A_FAMILY_RESPONSE_PRESENT`

Preserve the family result even if complete energy+force is <5%.

Write one next-step proposal to charge actual graph preparation and validate on independent geometries.
Do NOT execute it in this Goal.

## Case D — target positive but non-target also regresses
Decision:
`R22F_R21A_RESPONSE_WITH_NON_TARGET_COST`

Localize the non-target family and state whether it is mandatory or avoidable.
At most one next-step proposal.
No hardware claim.

## Case E — attribution/timing remains mixed
Decision:
`R22F_R21A_FAMILY_RESULT_MIXED`

STOP. Do not extend samples or profile budget after seeing the result.

---

# 8. Scope limits

This Goal does NOT:
- run Donline graph preparation
- open old R21A holdouts
- change model size
- change discovery frame
- measure neighbor search
- run MD
- train
- add double backward
- use NCU/NVBit/SASS
- use node174/Accel-Sim
- design hardware.

A stable family-level positive is a **software/execution evidence result**, not automatic architecture admission.

---

# 9. Failure persistence

Before any real-model scientific STOP save:
- arm
- exact input/graph hash
- outputs
- first numerical mismatch
- family membership/attribution status
- environment and lock receipt.

Do not lose first failure outputs.

---

# 10. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R22F_R21A_FAMILY_LOCALIZATION_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- PARENT_AUTHORITY.json
- ENVIRONMENT_RECEIPT.json
- FAMILY_CONTRACT.md
- AORDER_CONTRACT.md
- AORDER_CORRECTNESS.tsv
- PROFILE_RECEIPT.json
- FAMILY_MEMBERS.tsv
- PROFILED_FAMILY_TIMING.tsv
- FAMILY_RESPONSE_SUMMARY.tsv
- FORMAL_COMPLETE_TIMING.tsv
- COMPLETE_RESPONSE_SUMMARY.md
- NEXT_STEP_PROPOSAL.md
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Mark unreached items NOT_RUN.

---

# 11. Closure

Publish one exact commit.
Push/fetch-back verify commit/tree.
Release GPU lock.
Terminate campaign GPU processes.
Clean worktree.
STOP.

Final Chinese report must lead with:
1. frozen family definitions;
2. target-family gross and net response;
3. deterministic mandatory auxiliary cost;
4. non-target median/worst response;
5. complete energy+force response;
6. Aorder separation if available;
7. whether one bounded next step is justified.

Do not lead with the old 4.7047% or a single fastest kernel.
