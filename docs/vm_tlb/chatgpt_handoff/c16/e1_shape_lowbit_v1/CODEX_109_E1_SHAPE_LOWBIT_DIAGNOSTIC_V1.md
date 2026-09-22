# CODEX 109 — C16 E1 Shape × Low-Bit Diagnostic V1

## Goal

Execute the lightweight E1 extension on node109.

Do not rerun already accepted eight-point RAW/AWQ core measurements unless their authority cannot be re-audited.

Do not start deep profiling or mechanism work.

Suggested execution branch:

`hrl/c16-e1-qwen25-shape-lowbit-109-v1`

## Mandatory reads

Fetch and verify:

`hrl/c16-e1-shape-lowbit-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_shape_lowbit_v1/E1_SHAPE_LOWBIT_DIAGNOSTIC_DESIGN_V1.md`
2. `docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`
3. this file

Accepted upstream authorities:

- C16 RAW/AWQ pair:
  `hrl/c16-qwen25-7b-pair-closure-109-v10@57ca798c851a3b9d4a2c787c01f4e2b3a16fcdea`

- existing eight-point shape matrix:
  `hrl/awma-e1-shape-oracle-moe-harness-109-v2@56096d32bd5cd783286e1b5e5e612b6019f926d0`

## Stage A — re-audit, do not repeat

Verify:
- exact eight core points and raw samples;
- source/runtime hashes;
- shape-specific activation authorities;
- actual RAW and AWQ input/weight/output dtypes;
- AWQ path matrix.

If authority closes, reuse the eight existing points.

## Stage B — four-point RAW_FP16 bridge

Run exactly:

- q_proj M1 RAW_FP16
- q_proj M256 RAW_FP16
- down_proj M1 RAW_FP16
- down_proj M256 RAW_FP16

Use the same RAW semantic modules and shape-specific activation values, cast to FP16; cast dense RAW weights once to FP16; validate against a direct FP16 oracle.

Timing:
- 2 warmups
- 5 measurements
- retain all samples
- report median/min/max/CV

Record:
- input/weight/output dtype
- shape/stride
- lightweight path identity

No NCU/NVBit/NSYS/full trace.

## Stage C — unified interaction analysis

Build RAW_BF16 / RAW_FP16 / AWQ comparison for:

`{q_proj,down_proj} × {M1,M256}`

Report:
- timing
- CV
- AWQ/RAW_BF16
- RAW_FP16/RAW_BF16
- AWQ/RAW_FP16 only when dtype/timing boundary are sufficiently compatible; otherwise mark NOT_FULLY_MATCHED
- runtime path relation

Do not claim remaining difference is caused only by quantization.

## Stage D — up_proj holdout

If Stage B closes normally, run:

- up_proj M1 RAW
- up_proj M1 AWQ
- up_proj M256 RAW
- up_proj M256 AWQ

Same lightweight protocol.

If up_proj cannot be qualified without opening a large new engineering/capture problem, record HOLDOUT_NOT_QUALIFIED and continue.

## Stage E — CODE holdout

Preferred point:

`down_proj M1 × {RAW,AWQ}`

Run only if a matched semantic-module CODE input authority is already available or can be obtained by a small direct replay.

If not, record:

`CODE_HOLDOUT_NOT_RUN_NO_MATCHED_AUTHORITY`

Do not block the Goal.

## Output

Create:

`docs/vm_tlb/review_packs/C16_E1_QWEN25_SHAPE_LOWBIT_109_V1/`

with the artifacts required by the design.

Update:

`docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

Then:
- SHA256SUMS
- commit
- push
- remote verify
- clean worktree
- STOP

Do not automatically start any deep memory capture.

Ordinary dtype/oracle/path/timing/Git issues are solve-and-continue.
Stop for review only if accepted upstream authority cannot close or the controlled bridge requires changing the scientific comparison contract.
