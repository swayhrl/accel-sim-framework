# Codex Goal — Lane F / node109
## AWMA R21A OpenEquivariance graph-readiness Native screen V1

Date: 2026-10-02

Repository:
`swayhrl/accel-sim-framework`

Execution branch:
`hrl/awma-r21a-oeq-graph-readiness-109-v1`

Expected scientific parent:
`0c6cda2f680fa93ed5ea7d4b098eef5044a8a0c4`

Stage:
`AWMA_R21A_OEQ_GRAPH_READINESS_109_V1`

Review pack:
`docs/vm_tlb/review_packs/AWMA_R21A_OEQ_GRAPH_READINESS_109_V1/`

This is one continuous solve-and-continue Goal.

If a gate passes, continue automatically.
Ordinary engineering issues may be repaired locally.
Scientific identity/contract changes or explicit STOP labels terminate the Goal.

---

# 0. Research question and anti-bias boundary

The generic Round21 idea "efficient geometric models require expensive dual-CSR preparation" has been rejected as too broad.

Strong current software provides an alternative:

- NequIP's OpenEquivariance integration uses
  `TensorProductConv(... deterministic=False ...)`;
- OpenEquivariance atomic mode accepts arbitrary receiver/sender edge order;
- deterministic mode requires receiver-major adjacency plus a sender transpose permutation and may avoid atomics.

The only question here is:

> Is the deterministic downstream benefit on a real NequIP energy+force workload large enough to justify the graph-readiness preparation it requires?

Do not:
- choose a slower e3nn baseline to create speedup;
- force an unsorted graph if the natural producer already emits receiver-sorted edges;
- sort once per interaction layer;
- change graph cutoff or edges;
- add training/double-backward;
- use dataset labels as the numerical reference for model implementation equivalence;
- tune model size, graph size, threshold or precision to find a positive result.

---

# 1. Frozen external source authority

Pin and receipt:

## NequIP
`mir-group/nequip@27d9d2182da918ab7be0017d8300e53278f5e00e`

Relevant facts to verify locally from the pin:
- S preset: 2 layers, l_max=1, num_features=[128,64]
- `InteractionBlock` uses uvu TP-scatter
- `OpenEquivarianceTensorProductScatter` uses `deterministic=False`
- official float32 model-level output tolerance = `5e-5`
- official similarity helper averages 5 evaluations.

## OpenEquivariance
`PASSIONLab/OpenEquivariance@dc9979099c65113adcc016977c5c60974f9ddafb`

Verify:
- atomic `deterministic=False`: arbitrary edge order legal
- deterministic `True`: receiver-major rows required plus sender transpose permutation
- forward/autograd consume the permutation.

## Model
`nequip.net:mir-group/NequIP-OAM-S:0.1`

No substitute size.
No training/fine-tuning.
No OAM-L.

## Real geometry input
`mir-group/nequip-tutorial@8f90935ba42fd9e03df323cf03428c456d87b881`

File:
`sitraj.xyz`

Git blob:
`baac4e23364d00d29b2410fa60a92ade0cbf35a3`

Expected file size:
784661 bytes.

Download/fetch exact bytes and compute SHA256.

The file is treated as a collection of real periodic Si geometries.
Do NOT assume the file order is a physical time sequence unless independent metadata proves it.
No neighbor-rebuild frequency claim is authorized.

---

# 2. G0 — environment / asset admission

CPU/network first where possible.

Record:
- node identity
- RTX4080 / SM89 identity
- driver
- Python
- PyTorch
- CUDA runtime/toolkit
- NequIP version/commit
- OpenEquivariance version/commit
- e3nn
- ASE
- torch-geometric if used.

Use an isolated environment if needed.
Do not modify a working system environment globally.

At most two bounded environment repairs.
Do not install a different GPU driver.

Model:
- fetch exact OAM-S:0.1 package through official NequIP path;
- locate actual package/cache file(s);
- compute SHA256;
- persist compact authority metadata and, where policy/storage permits, a durable copy on node164;
- verify the loaded object is the requested OAM-S model and not another package.

Input:
- fetch exact pinned `sitraj.xyz`;
- verify Git source identity/size;
- compute SHA256;
- parse every frame;
- record frame count N;
- require N >= 12;
- require each selected frame to be finite, periodic, all-Si, with nonempty positions/cell;
- record provided energy/force/stress labels as provenance only.

Freeze frame indices before any performance data:
- discovery = `floor(N/2)`
- holdouts =
  `floor(N/6)`,
  `floor(N/3)`,
  `floor(2N/3)`,
  `floor(5N/6)`

Require five unique valid indices.
If not unique, STOP rather than selecting by content.

Write:
- `PLATFORM_RECEIPT.json`
- `MODEL_AUTHORITY.json`
- `INPUT_AUTHORITY.json`

If model or input cannot be qualified:
`R21A_SOURCE_OR_INPUT_NOT_QUALIFIED`
STOP.

---

# 3. G1 — model and graph semantic admission

Use float32.
TF32 must be OFF for this first admission.

Do not use DFT labels as a reference for backend equivalence.

On the discovery frame:

1. Load the unmodified OAM-S model.
2. Confirm:
   - model supports Si;
   - actual model metadata/structure is compatible with the advertised S scope;
   - energy and forces are requested;
   - no training graph / parameter gradient is required.
3. Build the neighbor graph using the model's own frozen cutoff and standard NequIP data transform/interface.
4. Freeze the exact graph before performance comparison:
   - edge count
   - exact directed edge multiset
   - periodic image / cell-shift identity
   - graph tensor dtypes/shapes
   - natural producer ordering.

Do not shuffle edges.

Record whether the natural graph is already receiver-major sorted.

Persist graph/input hashes and compact tensors needed for reproducibility on node164.

## Reference model

Use the same OAM-S weights with the unmodified NequIP/e3nn tensor-product path as the implementation reference.

Reference is for numerical identity only, not performance.

Run the reference five times and save energy/force outputs.

## A0 strong baseline qualification

A0:
- official OpenEquivariance atomic path
- `deterministic=False`
- natural graph ordering
- same model weights and float32 settings.

Use the NequIP source-level model similarity convention:
- 5 evaluations
- compare energy and forces against the reference
- `atol=rtol=5e-5`
- no tolerance widening.

Also require:
- finite energy/forces
- exact graph identity/coverage
- no NaN/Inf
- stable output shapes.

If A0 fails:
`R21A_ATOMIC_BASELINE_NOT_QUALIFIED`
STOP.

---

# 4. G2 — build one deterministic graph-readiness path

This is an opt-in/default-OFF research patch.

No model-weight or model-equation change.

Create the minimal graph representation required by pinned OpenEquivariance deterministic convolution.

If the natural graph is already receiver-major:
- preserve that ordering;
- do not sort again merely to charge cost.

If it is not:
- stable receiver sort exactly once per rebuilt graph;
- apply the same permutation to every edge-aligned topology field required by the model.

Construct the sender transpose permutation exactly according to pinned OpenEquivariance semantics.

Validate:
- sorted graph edge multiset exactly equals A0 graph
- periodic shifts remain paired with the same directed edges
- receiver-major requirement holds
- sender permutation is a true permutation
- applying it represents the required transpose/column-major traversal.

Do not prepare separate permutations per interaction layer.

## Model integration

Use `TensorProductConv(... deterministic=True ...)` for the same NequIP TP-scatter modules.

The same prepared graph/permutation must be shared across both OAM-S interaction layers during one model invocation.

No host per-layer preprocessing.

At most two bounded engineering repairs to thread the prepared permutation through the model.

If deterministic OpenEquivariance cannot be integrated into the same model and same supported compiled inference boundary without broad rewrite:
`R21A_DETERMINISTIC_PATH_NOT_CLEAN`
STOP.

---

# 5. G3 — same strong compile mode

A0 and all deterministic arms must use the same strong inference compilation mode.

Preferred and required first choice:
NequIP AOTInductor / supported compiled ASE-style inference with OpenEquivariance.

Same:
- PyTorch/CUDA environment
- model weights
- dtype
- TF32 setting
- compile options
- graph shape for a given frame.

Compilation/JIT is outside timing.

Do not compare compiled A0 against eager deterministic candidate.

Do not downgrade A0 to rescue the candidate.

If the deterministic patch cannot use the same strong compiled mode after at most two bounded compilation repairs:
`R21A_DETERMINISTIC_PATH_NOT_CLEAN`
STOP.

---

# 6. G4 — Dready correctness

Dready:
- deterministic OpenEquivariance
- receiver-sorted graph and sender permutation already resident/prepared before timing.

Before any performance timing:

Run 5 Dready evaluations on discovery.

Against the same frozen reference require:
- energy allclose `atol=rtol=5e-5`
- forces allclose `atol=rtol=5e-5`
- finite values
- exact graph edge/shift identity.

Save all five outputs and max-abs / RMS differences.

No post-candidate tolerance adjustment.

If Dready fails:
`R21A_DETERMINISTIC_NUMERICS_NOT_QUALIFIED`
STOP.

---

# 7. G5 — Dready full-model headroom

This is the first performance gate.

Scientific timing boundary:

`graph representation required by the arm already resident on GPU -> energy + forces committed and synchronized`

A0 input:
- natural graph ordering resident
- no sort/permutation prep required.

Dready input:
- deterministic-ready sorted graph/permutation resident
- preparation cost intentionally outside timer.

This is an idealized readiness diagnostic, not deployment performance.

Timing protocol on discovery:
- 3 paired groups
- each arm/group: 2 warmups + 5 formal samples
- alternate arm order by group
- same frame and frozen graph
- compilation already complete
- wall time + CUDA event time
- every formal result must pass the frozen numerical contract.

For each group compute median and MAD.

Dready is MATERIAL only if:
1. all formal samples qualify;
2. all three groups favor Dready;
3. median relative full energy+force improvement >=5%;
4. gap >3x larger-arm MAD.

If stable <5%:
`R21A_READY_HEADROOM_NOT_MATERIAL`
STOP.

Interpretation:
even free deterministic graph readiness lacks enough whole-model headroom on this real scope; do not implement online prep or hardware.

If mixed/noisy:
`R21A_RESULT_MIXED_NEEDS_REVIEW`
STOP.

Only MATERIAL may continue.

---

# 8. G6 — Donline: charge the graph preparation

Only after Dready MATERIAL.

Starting state for both A0 and Donline:

`the exact natural unsorted-or-naturally-sorted COO graph for the rebuilt frame is resident on GPU`

Do not reuse a previously computed sender permutation across formal Donline samples.

Donline includes exactly the preparation actually required by the natural graph:

- receiver sort only if needed
- reorder every required edge-aligned topology field
- sender transpose permutation construction
- any synchronization/allocation/public helper overhead required by the path
- deterministic full model energy+force execution.

Do this once per full model call, not once per layer.

Precompile/JIT code, but not data-dependent permutation values.

If buffers can be legally preallocated without containing graph-specific results, preallocation is allowed and must be symmetric/frozen before timing.

A0 remains official atomic path on the natural graph.

Correctness:
same frozen reference, edge identity and `5e-5` energy/force contract.

Timing:
same 3 groups × 2 warmups + 5 formal per arm.
wall + CUDA event.
All formal samples semantically qualified.

Donline MATERIAL requires:
- all three groups favor Donline
- median whole-boundary improvement >=5%
- gap >3x larger-arm MAD
- exact graph and model semantics preserved.

If stable <5%:
`R21A_ONLINE_PREP_NOT_MATERIAL`
STOP.

Interpretation:
the deterministic kernel may have ready-state headroom, but graph preparation does not pay back on this real scope; software atomic baseline remains sufficient.

If mixed:
`R21A_RESULT_MIXED_NEEDS_REVIEW`
STOP.

No alternative sorting scheme or model-size sweep.

---

# 9. G7 — sealed independent-frame validation

Only if Donline is MATERIAL.

The four holdout indices were frozen from N before discovery timing.

For each holdout:
1. build graph with the same model cutoff / standard producer
2. freeze exact graph and hashes before timing
3. qualify A0 and deterministic numerical identity against the same e3nn reference rule
4. run the exact A0 vs Donline timing protocol.

No parameter change.
No frame replacement.

Holdout reproduction requires:
- all four frames qualify
- all formal samples qualify
- all three aggregate groups favor Donline
- median aggregate improvement >=5%.

If reproduced:
`R21A_OEQ_GRAPH_READINESS_RESPONSE_REPRODUCED`

This supports only:
a Native software response for paying one graph-readiness preparation to unlock deterministic OpenEquivariance on OAM-S / pinned Si geometry scope.

It does NOT authorize hardware.

If not reproduced:
`R21A_RESULT_MIXED_NEEDS_REVIEW`
STOP.

---

# 10. What this Goal does NOT test

This first R21A execution does NOT time:
- neighbor search from coordinates
- long-run skin/rebuild frequency
- MD integration
- a temporal trajectory
- training
- double backward
- MACE
- Sobek
- larger NequIP sizes
- other chemistry
- 174 / Accel-Sim
- hardware.

If R21A reproduces, a later separately reviewed step may connect the deterministic-ready consumer to a strong GPU neighbor producer and move the boundary back to coordinates-ready.

No such continuation is automatic.

---

# 11. Failure persistence rule

Before raising a scientific STOP after a real model execution, persist:
- exact input/frame reference
- graph hashes
- energy/forces
- relevant status
- first mismatch location/value
- source/environment receipt.

Do not repeat the R20 pattern where the first failed output array was lost.

---

# 12. Resource policy

All CUDA compilation/run work:
`/data/c16/locks/c16_gpu_campaign.lock`

Do not busy-poll or preempt another campaign.

Large model/input/raw:
node164 durable authority.

109:
active replica.

174:
no staging / no compute.

NSYS = 0
NCU = 0
NVBit = 0
SASS = 0
Accel-Sim = 0.

---

# 13. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R21A_OEQ_GRAPH_READINESS_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- SOURCE_BINDINGS.json
- PLATFORM_RECEIPT.json
- MODEL_AUTHORITY.json
- INPUT_AUTHORITY.json
- FRAME_SELECTION.tsv
- DISCOVERY_GRAPH_AUTHORITY.json
- REFERENCE_NUMERICS.tsv
- A0_ATOMIC_QUALIFICATION.tsv
- DETERMINISTIC_GRAPH_CONTRACT.md
- DETERMINISTIC_SOURCE_DIFF.patch
- DREADY_CORRECTNESS.tsv
- DREADY_TIMING.tsv if reached
- DREADY_DECISION.md
- DONLINE_CORRECTNESS.tsv if reached
- DONLINE_TIMING.tsv if reached
- DONLINE_DECISION.md
- HOLDOUT_GRAPH_AUTHORITY.tsv if reached
- HOLDOUT_TIMING.tsv if reached
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Unreached stages explicitly NOT_RUN.

---

# 14. Closure

Publish one exact commit.
Push/fetch-back verify commit/tree.
Release GPU lock.
Terminate campaign GPU processes.
Clean worktree.
STOP.

Final Chinese report should lead with:
- exact trained model and real frame authority
- natural graph ordering and what prep deterministic OEQ actually required
- A0 numerical qualification
- whether free-prep Dready had material whole-model headroom
- if triggered, whether Donline paid back preparation
- if triggered, whether sealed frames reproduced
- what result supports and what it does not.

Do not lead with internal PASS counts.
