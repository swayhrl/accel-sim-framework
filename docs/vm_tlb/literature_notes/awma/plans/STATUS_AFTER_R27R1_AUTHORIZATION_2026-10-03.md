# Status after R27R1 continuation authorization

Date: 2026-10-03 (Asia/Shanghai)

This supersedes `STATUS_AFTER_R27_REVIEW_2026-10-03.md` only for current AWMA task authorization. The accepted R27 review and R26 scientific result remain unchanged.

## Why a new continuation is authorized

R27 closed correctly as `R27_INPUT_OR_SOURCE_NOT_QUALIFIED` before tokenization/CUDA because the exact pinned WikiText-2 train parquet could not be obtained from the bounded execution environments.

A post-review public-source check found that:

- the original Salesforce/wikitext commit `8aaa8b27d493dba10b8553290236799e6dc57829` records `wikitext-2-raw-v1/train-00000-of-00001.parquet` as 6,357,543 bytes with SHA256 `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`;
- the current official Salesforce/wikitext main pointer publicly reports the same SHA256 for that file.

This is evidence that the intended scientific payload still exists, not evidence that any node has downloaded or admitted the bytes. Therefore continuation uses a new reviewed handoff and first requires byte-level acquisition/admission.

## Current authorized AWMA task

Lane G / node109:
`AWMA_R27R1_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1`

Handoff branch:
`hrl/awma-r27r1-varied-batch-capacity-continuation-handoff-v1`

Exact handoff HEAD:
`ad361be589de85787c3f724582ae1862cb3c3539`

Exact handoff tree:
`aa0acb61acd0e1a2fa16fedd75cf8d69d314f06e`

Fresh execution branch to create:
`hrl/awma-r27r1-varied-batch-capacity-109-v1`

The handoff branch is based on the closed R27 result commit `4dca1cd713df8315b9e04f702d7f3b990c8f4b88`, but the old execution branch remains STOP and must not be resumed or amended.

Handoff directory:
`docs/vm_tlb/chatgpt_handoff/awma/r27r1_varied_batch_capacity_continuation_v1/`

Read from `START_HERE.md`.

## Gate structure

1. **Gate A — accepted-parent identity recheck**  
   Reuse the accepted R27 Gate-A raw qualification after bounded identity/checkpoint checks. Do not repeat the full 207-item historical readback unless a mismatch appears.

2. **Gate B0 — exact input acquisition/admission, CPU-only**  
   Acquire the exact 6,357,543-byte payload with SHA256 `e83889ba...0c9f7`, admit immutable bytes to node164 and read back size/SHA. Official pinned/current-main transport or a user-provided/local copy is acceptable only if bytes and SHA match exactly. No tokenization or CUDA before admission.

3. **Gate B1 — bank/numerical/freeze**  
   Build the fixed 33×128×128 bank using the accepted tokenizer, qualify B1 B0/C1/S2 for four steps, checkpoint/resume/switch, then freeze implementation before capacity observation.

4. **Gate C — bounded natural capacity**  
   Same frozen search/confirmation logic as the accepted R27 contract.

5. **Gate D — positive-only 32-step/resume**  
   Only after a stable same-B C1-OOM/S2-PASS witness.

6. **Publication / STOP**  
   One execution commit/review pack/node164 raw closure; no automatic next stage.

## Boundaries

- R27 itself remains COMPLETE / STOP and is not rewritten.
- R26 remains the latest accepted capacity result until R27R1 produces independently reviewed evidence.
- No formal timing campaign, profiler, node174/Accel-Sim, hardware/PPA, production/default change, second model/corpus or all-parameter training is authorized.
- C16 Stage A and DTC-L1 remain separate lines.
