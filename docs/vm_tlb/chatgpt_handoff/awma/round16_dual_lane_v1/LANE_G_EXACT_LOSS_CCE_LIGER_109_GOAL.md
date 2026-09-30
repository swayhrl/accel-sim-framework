# Codex Goal — Lane G / node109
## CCE / Liger exact-loss quick falsification V1

Date: 2026-09-30

This is a bounded side-lane experiment reusing **Lane G / node109** after R102 V2 has completed and stopped.

Execution branch:
`hrl/awma-cce-liger-exact-loss-boundary-109-v1`

Scientific intent:
quickly determine whether large-vocabulary final linear + cross-entropy forward/backward still contains a material **loss-head state/lifecycle residual** after current strong software implementations.

This is not a new mainline and does not authorize 174 or hardware design.

## 0. External strong-baseline authority

Freeze exact current source identities before execution.

Primary CCE:
- repo: `apple-aiml-research/ml-cross-entropy`
- expected current main during handoff: `3de376c106a1916bc5e1b619f9c77c87a461ee1c`
- use `cce_exact` / `cce_kahan_full_c_full_e` semantics: gradient filtering disabled for classifier and embedding/input gradients.

Primary Liger:
- repo: `linkedin/Liger-Kernel`
- expected current main during handoff: `6ad077c36379eb9c7950f5572cc713f4d38e21a7`
- use the standard Triton `LigerFusedLinearCrossEntropyLoss` path that is supported on Ada; do not use SM90-only CuTe/CuTile paths on RTX4080.

Do not silently update to newer commits after timing begins.

## 1. Real workload/input authority

Prefer reusing the already-accepted AWMA/R101 real next-token CE input and Qwen2.5-0.5B assets rather than downloading a new model.

Historical source identity to recover from accepted R101 receipts:
- model family: `Qwen/Qwen2.5-0.5B-Instruct`
- accepted model revision and weight hash from R101 authority;
- deterministic real text/token window previously used for one real next-token CE backward.

Before GPU work prove:
- exact model/token input can be recovered;
- labels are the natural shifted next-token labels from that input;
- final hidden states are produced by a real model forward, not random tensors;
- lm_head weight is the real checkpoint tensor;
- no model update is performed.

If the accepted R101 input/assets cannot be recovered without inventing a new workload, STOP:
`EXACT_LOSS_REAL_INPUT_NOT_QUALIFIED`.

Do not substitute random hidden states for performance evidence.

## 2. Freeze one shape only

This is a quick falsification, not a shape study.

Use the exact accepted token window length if it fits all three implementations on the 16 GiB RTX4080.

If the accepted window is too large for the dense baseline, deterministically take the longest prefix that:
- preserves whole natural token sequence prefix;
- fits B0 with at least 10% free device memory margin;
- is frozen before comparing arms.

Do not scan several sequence lengths.

Batch = 1.

Record:
- token count T;
- hidden size H;
- vocabulary V;
- storage dtype;
- dense logits bytes `T * V * element_size`;
- lm_head bytes.

## 3. Local operator boundary

The measured operator begins with a real final hidden tensor and real lm_head weight resident on GPU and ends when:
- scalar mean next-token CE loss is available;
- gradient w.r.t. final hidden is materialized;
- gradient w.r.t. lm_head weight is materialized.

This isolates the final loss head.
It does not include transformer forward/backward or optimizer step.

The hidden tensor must be detached from the transformer and re-enabled for grad so all arms see the same frozen input.

## 4. Arms

### B0 — strong PyTorch materialized-logits reference

Use an efficient:
`logits = hidden @ W.T`
followed by standard `torch.nn.functional.cross_entropy`, then backward.

No Python token/vocab loops.

This arm intentionally materializes full logits and is a correctness/reference baseline, not the claimed strong endpoint.

### B1 — CCE exact/no-filter

Use the pinned CCE implementation with gradient filtering disabled:
`cce_exact` (or exact alias at the pinned commit).

Do not use the default filtered CCE result as the primary scientific comparison.

### B2 — Liger fused linear cross entropy

Use pinned `LigerFusedLinearCrossEntropyLoss` on its Ada/Triton path.

Do not force SM90 backends.

No additional custom kernel is authored in this Goal.

## 5. Numerical contract

The three arms must use:
- exact same hidden tensor;
- exact same lm_head tensor;
- exact same shifted labels / ignore positions;
- same reduction (`mean`);
- same storage dtype.

Compare:
- loss;
- grad_hidden;
- grad_weight.

This is a full-gradient contract, **not bitwise identity across different accumulation orders**.

Before timing, freeze tolerances based on source/test authority and a CPU/FP32 reference sanity check.

Default upper bounds unless pinned project tests justify tighter:
- BF16 loss/grad relative and absolute comparison: `rtol <= 1e-2`, `atol <= 1e-2`;
- also report max abs, max rel, mean abs, and cosine similarity for gradients.

No gradient filtering, label smoothing, z-loss, or softcap differences are allowed.

If an implementation cannot satisfy the full-gradient contract without changing algorithm semantics, mark it unqualified; do not loosen tolerance after seeing timing.

## 6. Memory and timing

All CUDA work must hold:
`/data/c16/locks/c16_gpu_campaign.lock`

For each qualified arm:
- 3 paired groups;
- 2 warmups/group;
- 5 uninstrumented formal repeats/group;
- save each sample, median, MAD.

Primary timing:
`real hidden+W ready -> loss + grad_hidden + grad_weight committed`.

Reset/zeroing between arms must be identical and kept outside timing only if deployment can do so equivalently.

Required allocations/materialization intrinsic to the arm remain inside.

Report:
- peak allocated/reserved bytes above frozen input baseline;
- whether full `T x V` logits exist;
- saved tensor logical identities/bytes if inspectable;
- kernel launch count only if obtained from a valid profiler;
- no claim that allocator bytes equal DRAM traffic.

Compile/JIT startup separately recorded; steady-state exclusion allowed only after stable warmup.

## 7. Quick headroom logic

This side lane asks whether strong software already removes the obvious lifecycle problem.

Primary comparisons:
- B0 vs B1;
- B0 vs B2;
- B1 vs B2.

Do not claim B0 speedup as an architecture opportunity: B0 is intentionally materialized.

After B1/B2:
- identify the faster qualified strong arm;
- inspect whether it still materializes a large intermediate or incurs a clearly separable state/lifecycle phase.

If the best strong arm has no clearly separable >=5% complete local-operator state/lifecycle opportunity, decision:
`EXACT_LOSS_STRONG_SOFTWARE_SUFFICIENT`.

If B1/B2 disagree materially or numerical/performance behavior is unstable:
`EXACT_LOSS_RESULT_MIXED_NEEDS_REVIEW`.

Only if a best strong arm still shows a defensible >=5% removable state/lifecycle residual, without removing mandatory GEMM/softmax-gradient math:
`EXACT_LOSS_STATE_LIFETIME_RESIDUAL_PRESENT`.

No mechanism is authorized even in that case.

## 8. Profiling budget

Only if B1/B2 leave an unexplained material residual:
- at most one NSYS capture of the fastest qualified strong arm;
- at most one NCU exact target chosen from that valid timeline;
- query actual SM89 support first.

No NVBit/SASS trace.
No shape sweep.
No second model.
No full training step.

If timing already closes the problem, do not profile just because the GPU is available.

## 9. Decision labels

Use exactly one:
- `EXACT_LOSS_REAL_INPUT_NOT_QUALIFIED`
- `EXACT_LOSS_IMPLEMENTATION_CONTRACT_NOT_QUALIFIED`
- `EXACT_LOSS_STRONG_SOFTWARE_SUFFICIENT`
- `EXACT_LOSS_STATE_LIFETIME_RESIDUAL_PRESENT`
- `EXACT_LOSS_RESULT_MIXED_NEEDS_REVIEW`

## 10. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_EXACT_LOSS_CCE_LIGER_109_V1/`

At minimum:
- `README.md`
- `SOURCE_IDENTITY.json`
- `INPUT_RECEIPT.json`
- `SHAPE_CONTRACT.tsv`
- `NUMERICAL_QUALIFICATION.tsv`
- `TIMING.tsv`
- `MEMORY_ACCOUNTING.tsv`
- `HEADROOM_ANALYSIS.md`
- `PROFILE_SUMMARY.tsv` if triggered
- `FINAL_DECISION.md`
- `RUN_RECEIPTS.json`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

## 11. Closure

Release GPU lock.
Commit/push/fetch-back verify exact SHA/tree.
Clean worktree.
STOP.

Do not start 174, another loss implementation, another model, or a hardware mechanism automatically.
