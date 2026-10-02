# Codex Goal — Lane G / node109
## AWMA R27 varied-batch capacity stability V1

Date: 2026-10-03 (Asia/Shanghai)

Repository: `swayhrl/accel-sim-framework`
Stage: `AWMA_R27_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1`
Handoff branch: `hrl/awma-r27-varied-batch-capacity-handoff-v1`
Execution branch: `hrl/awma-r27-varied-batch-capacity-109-v1`
Exact code parent: R26 execution `1a2485011b300cddd5137bbccb91dd6d30cfc22f`, tree `cce37bbbd368b545bea92c7b86cb429d8da4f48b`
Accepted review: `097c2b6ed7905480ed72679f0cc79865087ae3c9`

The user authorized one **bounded solve-and-continue Goal** that combines R26 raw-evidence readback, frozen varied-input preparation, necessary component hardening, natural batch-capacity confirmation, and positive-only longer trajectory/recovery. Do not create separate GPU rounds for the gates. Each gate either permits the next phase or closes this Goal with its recorded negative/STOP outcome. The exact handoff HEAD in the launch instruction, not this parent SHA, is the execution branch base.

## 0. Scientific question and limits

R26 established C1 B70/B71 PASS/OOM versus S2 B71/B72 PASS/OOM, each 3/3, in five-step training on B identical copies of one accepted sequence. The B70 whole-step S2 peak was 3.828 MiB higher and timing was MIXED; C1 B71 reportedly failed on its third step in shared backbone/compact-lookup backward. The scientific question here is whether an **actual varied text stream** preserves a same-B complete-training-loop capacity distinction and whether the S2 passing endpoint survives 32 consecutive steps and fresh-process recovery.

This uses one model, one newly pinned *train* text source and one token bank. It is not a new independent model holdout, convergence experiment, all-parameter training, deployment, or speedup campaign. No 174/Accel-Sim, hardware/PPA, NSYS/NCU/NVBit/SASS. Keep C1 default and S2 explicit capacity opt-in.

## 1. Mandatory read order and exact authority

Read `START_HERE.md`, `ACCEPTED_R26_REVIEW.md`, `PARENT_AUTHORITY.json`, this Goal, and `R27_EXPERIMENT_CONTRACT.json` completely. Task-specific instructions supersede historical M4 root handoff text; preserve that history. Follow `AGENTS.md` worktree, ownership, staging, validation and review-pack rules.

The R26 source and model identities are frozen in `PARENT_AUTHORITY.json` and the execution review pack. Verify the R26 execution parent, source hashes, model six payload sizes/SHA256, revision, CCE source/meta, tied W identity, optimizer and common-start snapshot. The parent R25 W/m/v bit receipt was not reproduced in R26; do not rebootstrap or try to relabel R26 as exact R25. Use the **R26** CPU common start, logical step 1, SHA256 `09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55`, 2,626,691,315 bytes, from the node164 path in `PARENT_AUTHORITY.json`.

All CUDA/JIT operations, including diagnostic trials and source qualification, hold `/data/c16/locks/c16_gpu_campaign.lock` with an actual flock for the full lifetime. The parent and subprocesses must carry lock evidence. One GPU campaign process at a time; no competing job or artificial VRAM pressure.

## 2. Gate A — R26 raw evidence, CPU/read-only

Before a new input download or CUDA operation:

1. Read the Git R26 `RAW_DATA_INDEX.tsv`, node164 `R26_PUBLICATION_MANIFEST.tsv`, archive and common checkpoint. Validate the recorded archive/manifest hashes and the manifest's 207 entries against remote file bytes; do not infer success from the prior report alone.
2. Independently parse endpoint raw receipts/logs for C1 B70 PASS, C1 B71 OOM, S2 B71 PASS, S2 B72 OOM (three fresh confirmations each); use index paths and hashes, not guessed filenames. Verify B71 same-B identity, five complete S2 steps, finite state/counter, and C1's logged completed-step count, OOM exception/traceback, allocation request, phase and free/allocated/reserved bytes. Check B70/B71/B72 input binding hashes and absence of a different model/state/policy. Do not treat the CPU finalizer's hardcoded witness sentence as raw evidence.
3. Publish `R26_RAW_READBACK.json` with per-file SHA/size, parsed fields, discrepancies and a reviewer-friendly summary. If any required raw payload/checkpoint is missing, mismatched, ambiguous, or contradicts the 3/3 witness, classify `R27_PARENT_RAW_NOT_QUALIFIED` and STOP before GPU. No rerun may silently replace old evidence.

This gate verifies the old observation; it does not assert an allocator cause. A third-step OOM in the shared backward path and a higher B70 S2 peak motivate a *hypothesis* about allocation history, not a proved explanation.

## 3. Gate B — one fixed varied input bank and scoped code

The sole new text source is Salesforce `wikitext`, revision `8aaa8b27d493dba10b8553290236799e6dc57829`, config `wikitext-2-raw-v1`, **train split only**. Exact parquet file:
`wikitext-2-raw-v1/train-00000-of-00001.parquet`;
6,357,543 bytes; SHA256
`e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`.
Fetch only the URL in `PARENT_AUTHORITY.json` or use a byte-identical cached copy. This small input download is authorized; do not download model weights, use validation/test, switch corpus/revision, or choose a favorable text segment after GPU results. If the exact input is unavailable, STOP as `R27_INPUT_OR_SOURCE_NOT_QUALIFIED`.

Use only the accepted local Llama tokenizer, whose `tokenizer.json` SHA256 is in `PARENT_AUTHORITY.json`. Read the parquet `text` column in physical row order. Join **all** row strings with one LF between rows, retaining empty rows. Tokenize this string once with `add_special_tokens=False`; record tokenizer class/version, exact file hashes, flags, text SHA and token count. Take the first 540,672 IDs. In C row-major order reshape to CPU int64 bank `[33,128,128]`: 33 step indices, 128 disjoint windows/rows per step, 128 tokens per window. If insufficient IDs or any two of the 4,224 windows are byte-identical, STOP; do not shift the offset or choose another slice. Hash the entire bank and row/window bindings before CUDA and freeze them.

For step index k=0..32 and tested B, use bank[k, 0:B, 0:127] for input and bank[k, 0:B, 1:128] for labels, all-one attention, mean loss over B×127. The first B rows of the **same** precomputed bank are used by both policies and every trial; within-batch content and content across steps vary. Step k=32 is reserved for next-loss checks. Record per-step/B CPU tensor hashes. Keep only the current B batch on GPU; no full-bank GPU mirror. Reuse fixed-size input/label storage with per-step copy after graph release, and do not include CPU state restores within a trajectory. This new input is a capacity-validation stream, not a new holdout or training-quality benchmark.

Create the R27 code under `util/vm_tlb/awma/r27_varied_batch_capacity/`; retain old R26 source unmodified and document the diff from it. Reuse one integrated C1/S2 tied-W component and the accepted compact reducer/CCE path. The only necessary changes are per-step input binding, stream-aware checkpoint identity/cursor, leak-safe lifetime, and guardrails. Preserve BF16 tied W only, exact pointer/storage tie, full frozen backbone forward/dH backward, FP32 AdamW m/v, optimizer/meta, C1 one-full-gradient, S2 4096-row tiles without a full gradient, and explicit S2 opt-in. No dynamic policy, OOM retry, `empty_cache`/GC inside steps, offload, checkpointing, precision/attention/tile or optimizer tuning. Reject unsupported autograd consumers/configurations explicitly.

Import the **exact R26 CPU common state** without another B0 bootstrap. Verify checkpoint file and W/m/v/RNG hashes and logical step before migration. Its old token identity describes the R26 start, not the new stream; a narrow explicit migration may rebind only the input identity/stream cursor to the frozen bank hash. Do not alter W/m/v/step/RNG, reset optimizer moments, or call the old loader while silently bypassing a failed identity check. New checkpoints store W, FP32 m/v, logical step, stream cursor, CPU/CUDA RNG, model/optimizer and bank identities and policy metadata; CPU tensors only. Load into the existing tied storage and reject mismatched identities before CUDA execution.

### Numerical pre-freeze gate

From the same migrated start, use the first four bank steps at B1 for B0/C1/S2. Compare loss, dH, total gradient, W/m/v, exact step and next-bank forward loss at each step, fixed `rtol=atol=1e-2`, finite checks and first mismatch. Check a fresh-process checkpoint load and one policy switch on the new stream at B1; preserve moments, cursor and counter. Stream CPU comparisons in ≤64 MiB chunks; temporary diagnostic capture cannot contaminate capacity/formal paths. Any true numerical or identity failure is `R27_NUMERIC_OR_STATE_NOT_QUALIFIED` and STOP. Ordinary engineering defects may be fixed and all affected gates rerun **before freeze** within this same Goal.

Only after Gate A, CPU bank authority and B1 qualification pass, write `IMPLEMENTATION_FREEZE.json` with source/CCE bytes, runtime/backend, data/bank hashes, R26 start, model, optimizer, tile, per-step semantics, search/decision classifier and all contracts. Freeze **before any new capacity observation**. After freeze, no GPU-behavior, data, classifier or tolerance change; a required such change is STOP/review, not an implicit new attempt. CPU report/path fixes that cannot change observations are allowed.

## 4. Gate C — bounded natural capacity search

Run five actual continuous training steps on bank indices 0..4 per trial, with two designated warmups and three further complete steps, from the same CPU start. Fresh process per (policy,B), one process at a time. Require finite loss/W/m/v, exact counter 2..6, input hash per step, no retained graph/state growth, no restore between steps. Capture whole-step and phase allocated/reserved, post-step active state, failed request and full traceback on OOM.

The batch interval is [1,128]. For each policy in order C1 then S2, start B64. If PASS, test B96 then B128 until first OOM or B128 PASS (right censor). If B64 OOM, test B32,16,8,4,2,1 until first PASS; B1 OOM is qualification STOP. Once L PASS and U OOM are known, test integer floor midpoint and tighten until U=L+1. At most 12 distinct search B per policy. Preserve every trial. A PASS at B128 is right-censored, never extrapolate beyond it. A nonmonotone outcome or UNKNOWN (timeout, generic crash, CPU kill, device fault, numeric failure, conflicting job) is `R27_CAPACITY_BOUNDARY_UNSTABLE` or the appropriate qualification STOP, never converted to OOM.

Confirm each policy's passing endpoint and adjacent OOM in **three fresh processes each**, alternating policy when an endpoint B coincides; no majority vote. Confirm B128 three times if censored. Set B_common=min(confirmed PASS maxima). Select at most one forward witness B_witness=C1 maximum+1 if C1 confirmed OOM there and S2 confirmed PASS at the **same** B; reuse matching confirmations, otherwise run only the missing 3/3 witness trials. Handle reverse witness similarly. Any disagreement is UNSTABLE/STOP; no extra repetitions to manufacture a clean boundary. Search and finalizer classifiers must be generic, not hardcoded to observed B values or OOM step.

The same-B complete-loop 3/3 distinction is a *five-step* positive only. If S2 has no confirmed larger B, publish the negative/regression/censored outcome and STOP without a 32-step capacity claim or a new data/tile sweep. No formal timing campaign is authorized; report per-step latency and memory as descriptive feasibility observations only.

## 5. Gate D — positive-only 32-step and resume

Only after a stable C1-OOM/S2-PASS witness:

1. At B_common, compare one C1/S2 step from the common state on bank step 0, including loss, dH, total gradient and updated W/m/v, fixed tolerance, streaming CPU capture. No extra full GPU reference or gradient shadow at the boundary. If this changes feasibility, use existing tensor streaming hooks rather than changing B or semantics.
2. Run C1 and S2 for 32 consecutive bank steps 0..31 from the identical state. Compare loss and next-bank loss every step; full W/m/v at trajectory indices 1/4/8/16/32; exact counter/cursor each step. Avoid retaining all 2.6 GiB states: compare in chunks and keep only step-16/final CPU checkpoints needed for resume. After trajectory index 16 the logical counter is 17, and after index 32 it is 33. Fresh-process resume each mode from its step-16 state for the remaining 16 bank steps and compare final state/loss. From the same C1 step-16 state, run one next step under C1/S2 to verify policy switch without reset.
3. Independently run S2 at B_witness for 32 continuous varying-input steps, finite state/counter/input hashes and per-step whole-step/post-step memory. Fresh-process resume from its step-16 CPU checkpoint to step 33 and compare. C1 OOM at this B means there is **no matched witness numerical reference**; do not invent one.

A positive five-step witness followed by OOM, leak, mismatch or bad recovery at 32 steps is `R27_EXTENDED_CAPACITY_TRAJECTORY_NOT_QUALIFIED` (or numerical STOP if applicable). Report the five-step observation separately but do not claim the stronger result, shrink B to rescue, change allocator options, or retune S2. If all gates pass, classify `R27_VARIED_BATCH_CAPACITY_EXTENSION_32_STEP_SUPPORTED` with model/input/sequence/history scope.

If and only if the positive observation survives Gate D but allocation cause remains unclear, one separate **diagnostic** fresh-process pair at B_witness may collect bounded PyTorch allocator history/snapshot or `memory_stats` (one C1, one S2; maximum two). It is never an endpoint confirmation, timing sample, or permission to change allocator/backend. Record PyTorch-managed-memory visibility limits. Skip it if the existing receipts already explain the relevant allocation state. No GPU profiler.

## 6. Publication, interpretation and STOP

Use node164 for immutable raw, bank authority, checkpoints, logs and manifests. Git should hold compact code, one entry-point review pack under `docs/vm_tlb/review_packs/AWMA_R27_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1/`, `SHA256SUMS`, source/implementation freeze, R26 raw readback, every trial and endpoint, numerical/trajectory/resume summaries, first mismatch, decision, resource-lock receipts and a raw-index of byte hashes. The CPU finalizer must derive observed endpoints, OOM step and label from receipts; no observed-number literals in the result construction. Report model/input limitations, 32-step scope, no convergence/throughput inference, and any mismatch between execution receipt and independent review.

Write `docs/vm_tlb/codex_handoff/awma/r27_varied_batch_capacity_v1/LANE_G_FINAL_REPORT.md`. Archive/checkpoint readback by SHA, `git diff --check`, explicit-path staging, commit and push execution branch, fetch back exact SHA/tree, confirm clean worktree, no campaign CUDA processes and GPU lock released. Include commands, run times and artifact hashes. Then STOP. Do not begin production pilot, a second corpus/model, another context, a timing sweep or hardware work. User/ChatGPT review the result before any further stage.
