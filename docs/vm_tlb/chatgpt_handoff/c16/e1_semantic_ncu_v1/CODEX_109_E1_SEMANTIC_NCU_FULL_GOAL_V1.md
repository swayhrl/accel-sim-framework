# CODEX 109 — C16 E1 Semantic NCU Full Goal V1

## Mode

GOAL MODE / solve-and-continue

Suggested branch:

`hrl/c16-e1-semantic-ncu-109-v1`

## Read first

Fetch and verify:

`hrl/c16-e1-semantic-ncu-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_semantic_ncu_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_semantic_ncu_v1/E1_SEMANTIC_NCU_DESIGN_V1.md`
3. this file
4. `docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

Accepted producer authority:

`hrl/c16-e1-clean-baseline-109-v1@8988d6108ff8bdca180a14cec2fe769df45b09f1`

Accepted independent consumer:

`hrl/c16-e1-clean-baseline-consumer-prep-174new-v1@59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca`

Selected semantic role is frozen:
`up_proj`

Do not reselect.

## Goal

Resolve the semantic NCU selector at the exact module-call boundary and, if qualified, collect bounded NCU evidence for exactly:

- up_proj M1 RAW_FP16
- up_proj M1 AWQ_FP16_INPUT
- up_proj M256 RAW_FP16
- up_proj M256 AWQ_FP16_INPUT

Do all foreseeable work in this one Goal.

## Stage 1 — standalone exact replay

Build/reuse one standalone replay capable of executing each selected point.

For each point:

- load exact canonical FP16 activation from accepted E1 authority;
- use exact RAW_FP16 or frozen AWQ module/runtime;
- warm up outside target range;
- wrap exactly one semantic module call in a unique NVTX range;
- synchronize to make range attribution unambiguous;
- record output SHA;
- require output SHA match accepted clean-baseline point;
- record lightweight kernel inventory.

Do not put another target call inside the selected NVTX range.

## Stage 2 — qualify selector contract

Inspect installed NCU version/help first.

Use only syntax supported by this installed NCU.

Prove:

- one requested NVTX semantic range occurrence;
- no warmup target call selected;
- no other semantic point selected;
- all kernels belonging to that one semantic module invocation are retained;
- output SHA and implementation path match accepted clean baseline.

Important:

AWQ semantic module may consist of multiple kernels.
Do not force one-kernel selection.

The scientific selection unit is the exact module-call range.

If NVTX-range filtering cannot be made reliable, use a standalone-process fallback only if you can prove the process contains one target semantic invocation and no launch-order ambiguity.

No launch-order guessing in a multi-target process.

## Stage 3 — metric availability

Query installed NCU metric availability.

Record exact names and units.

Collect only valid metrics relevant to:

- L1/TEX requested bytes
- L2 requested bytes
- DRAM bytes
- occupancy/active warps if available
- SM/tensor/math utilization if available

Do not invent names or normalize unitless display values as bytes.

## Stage 4 — profile all four points

Once selector is qualified, profile all four points in the same Goal.

Persist per-kernel:

- semantic point
- NVTX range
- kernel name
- launch geometry
- metric name
- unit
- value

For additive byte/event metrics, sum across every kernel in the exact semantic range into:

`SEMANTIC_MODULE_SUM`

Do not sum utilization percentages blindly.

## Stage 5 — normalize and compare

For each point compute:

- semantic L1/L2/DRAM traffic
- bytes/output-element
- bytes/input-element
- bytes/RAW_FP16 dense-weight bytes
- AWQ bytes/packed-weight-storage bytes if exact storage authority is available

Compare:

- M1 RAW vs AWQ
- M256 RAW vs AWQ
- M256/M1 scaling within RAW
- M256/M1 scaling within AWQ
- relation between accepted native timing interaction and measured traffic interaction

Do not infer cache/TLB causality.

## Stage 6 — closure

Create:

`docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_109_V1/`

with all deliverables in design.

Update:

`docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

If selector still cannot be proven after the bounded exact-module replay approach:
- record exact failure;
- status `SEMANTIC_NCU_SELECTOR_UNRESOLVED_V2`;
- no traffic fabrication;
- close Git and STOP.

If selector qualifies:
- finish all four points;
- complete scientific interpretation;
- do not start NVBit/full trace/mechanism.

Then:
SHA256SUMS → commit → push → remote verify → clean worktree → release GPU lock → STOP.

Ordinary NCU CLI/parser/NVTX/replay engineering issues are solve-and-continue.

STOP early only for:
- accepted point identity/output SHA mismatch;
- inability to preserve exact accepted backend;
- genuine GPU/runtime corruption;
- scientific contract change.
