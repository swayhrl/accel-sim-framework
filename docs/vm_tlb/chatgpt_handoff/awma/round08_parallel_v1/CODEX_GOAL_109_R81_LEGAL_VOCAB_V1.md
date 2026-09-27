# CODEX GOAL — R81 heterogeneous legal-vocabulary exploration V1

Enter Goal mode. Read START_HERE.md in this directory and follow its shared isolation/lock/publication rules. Run only R81, not R82.
Stage: `AWMA_R81_LEGAL_VOCAB_EXPLORATION_V1`.

## 1. Question, not assumed innovation

For real grammar-constrained greedy generation, requests i have different legal next-token sets A_i. A shared union head computes over U=union(A_i); per-request/ragged execution avoids some rows but may lose weight reuse and efficient matrix execution.

Ask whether that tradeoff leaves a useful, localized response after credible indexed and fused software baselines. This is not the first vocabulary-pruning, masked sampling, indexed-linear or dynamic-batching implementation.

Known capabilities to read before implementation:
- XGrammar-2: https://arxiv.org/html/2601.04426v4
- FlashSampling: https://arxiv.org/html/2603.15854v2 (Algorithm1 and all-invalid-group discussion; don't inherit older19% claim)
- VocabTailor: https://arxiv.org/html/2508.15229v1
- Kestrel `m87-labs/kestrel@f61d3c7c6a8380e705a984f1e1767693464e27bd`, `kestrel/models/moondream/text.py::lm_head`: indexed weight/bias selection before linear already exists.
- FlashRec0.1.0: https://pypi.org/project/flashrec/0.1.0/ (SID-range projection; inspect actual source before claiming arbitrary dynamic-support capability).

If an existing implementation already provides exactly the proposed intervention, use it as baseline and test its cost; do not relabel it a new mechanism. Missing source/compatibility means not verified, not no prior art.

## 2. Fixed assets

Reuse accepted Qwen/Qwen2.5-0.5B-Instruct:
revision `7ae557604adf67be50417f59c2c2f167def9a775`.
Weights SHA256 `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`.
Prior head weight shape `[151936,896]`; isolated-head weight hash `d74257dc547b48be5ae7b93f1c9af072c0c42dbbb85503078e25c59cd09e68d0`.
Identity source at accepted execution base:
`docs/vm_tlb/review_packs/AWMA_R51_R52_TASK_LIFECYCLE_QUALIFICATION_V1/TARGET_IDENTITY_RECEIPT.json`.

Do not use the old natural-text hidden state with an invented random mask as a model result. Generate new structured-decoding trajectories on this exact checkpoint and bind each hidden state, mask, previous tokens and weights. This is a new constrained deployment of an existing model, not a new model asset.

Pin XGrammar code/package and tokenizer after compatibility audit, before model execution. The official HF example uses this model; its inspected blob is `d32fff97628194a9cd2c878cc5092cc9479e7a89`. Do not blindly inherit its float32 example setting: retain one declared inference dtype consistently across all timing arms. No system/environment changes outside R81.

## 3. Freeze workload before seeing performance

Create one small local structured-task fixture file, explicit `AUTHORED_QUALIFICATION_FIXTURE_NOT_PRODUCTION_DISTRIBUTION`.

Two discovery B4 cohorts, all requests arrive together:
- C0: four requests share one JSON schema containing an enum-valued classification and a free-text reason.
- C1: four requests have different JSON schemas: enum+reason; string extraction+integer; bounded array of strings; object with boolean+free-text explanation.

Use four fixed ordinary records/questions per cohort; record exact prompts and schemas. These are grammar workloads, not tool calls to execute. Include free-text states; don't only test tiny finite vocabularies. Grammar validity is not task-answer accuracy.

Freeze one additional B4 cohort with different records and schemas as holdout, never inspect its model outcomes during design. Maximum12 logical requests across discovery+holdout,128 new tokens/request, normal EOS/grammar completion; report truncation. No model/grammar/prompt replacement based on sparsity or speed. No batch/threshold/context sweep. B1 is optional correctness sanity only, not an additional performance search.

Create PREREGISTRATION.json containing records/schema IDs+hashes, tokenizer+config vocab sizes, dtype, decoder settings, max tokens, backend versions, arm definitions, candidate tile/group configuration and holdout IDs.

## 4. Semantic contract

Use grammar-constrained greedy selection. Legality at step t must depend only on already committed tokens and the frozen grammar; never future outputs. Preserve all legal token IDs, tokenizer padding/EOS semantics and exact ID mapping. Illegal logits may be -inf by design; require legal logits finite.

Backbone batch structure, weights, cache policy, input and hidden state are identical across head comparisons. Do not alter the decoder or grammar to avoid numerical mismatch. The mathematical reference is masked argmax over the same row dot products. For ties use the reference's deterministic token-ID rule and record it.

Validate index lists, union/remapping, per-request masks, coverage and no duplicate/omitted legal rows with integer fixtures. For model runs require same selected token and full generated token sequence relative to the qualified dense reference on each fixed request. Non-selected top2/top8 ordering is diagnostic only, not an extra application contract.

If a changed kernel's rounding flips a masked winner, record first divergence, relevant scores/margins and implementation difference. One source-correct repair is allowed. If it persists, mark that arm NUMERICAL_COMPARABILITY_NOT_QUALIFIED, retain other qualified arms, and do not infer that legal support pruning is algebraically invalid. No repeated tolerance relaxation or replacement of inconvenient requests.

## 5. Four arms, maximum8 discovery configurations

A0 DENSE_VENDOR: qualified optimized dense head, grammar mask and greedy selection; semantic reference.

A1 DENSE_FUSED: efficient tiled head+mask+argmax without full logits materialization when feasible. Reuse/adapt FlashSampling's relevant capability, clearly label a greedy adaptation rather than full-paper reproduction. A kernel constrained to unavailable GPU ISA is not a fair SM89 baseline; record capability/compatibility and implement only a bounded legal equivalent.

A2 INDEXED_UNION: U is the union of current legal sets. Gather W[U] into reusable storage and run an efficient shared linear operation plus per-request masking and ID remapping. Include gather, metadata and output costs. This represents the concrete Kestrel indexed-head capability. Reuse an existing direct-index implementation instead when it supplies a stronger relevant baseline; preserve both capability and provenance.

A3 RAGGED_DIRECT: one small native prototype, fixed initial configuration. Compute each request's legal rows directly from original W with indices; coalesce identical-mask requests if legal. Avoid a full dense logits buffer. Charge all list formation, grouping, indexing, actual weight loads, reduction and token remapping. No architecture-specific nonexistent instruction; no GPU scheduler framework; no broad autotuning.

At most two source implementation strategies for this prototype; ordinary debugging within a strategy is not a new scientific round. The fastest qualified known-capability baseline among A0/A1/A2 is the comparison point, not automatically A0.

## 6. Measurements and attribution

First run untimed reference trajectories for C0/C1. Record per-step |A_i|, |U|, overlap, valid-token ranges, actual head invocation, and logical row work. `B*|U|` and `sum|A_i|` are work proxies, not DRAM bytes or speedup bounds.

All discovery timesteps are retained. Do not choose only the sparsest step. Singleton legal support must have the trivial software no-head shortcut represented fairly in every eligible baseline; do not claim singleton skipping as new. Empty support is a correctness/termination condition, not a timed winner.

First compare the full head region from availability of hidden state and current grammar information through ID selection. Include implementation-specific metadata/transfer/gather cost. If the grammar mask is produced concurrently with the backbone, preserve that overlap for a complete-generation comparison; don't charge serialized grammar time to only one arm.

Then run the eligible full-generation arms on the same two cohorts, maximum8 conditions. Use2 warmups+7 paired/interleaved repetitions with primary wall-clock from generation start to completion, valid token count, stop status and per-request completion. Kernel-only time is separately labeled. Do not claim masked-head improvement equals model throughput improvement.

One NSYS canary for each qualified arm on one frozen cohort is enough. At most2 focused NCU comparisons only if useful to distinguish weight traffic/compute occupancy versus metadata/packing. Available metric query and scope must be bound. No full NVBit tracing.

No exact claim that copy durations or CPU time sum to the full critical path. Compare a realizable grouped/direct alternative, not merely subtract separately measured components.

## 7. Conditional validation and decision

If an arm exposes a reproducible complete-region effect or an informative regression not already explained by known capabilities, perform one necessary ablation/control and the fixed holdout cohort in the same Goal. No tuning on holdout. A5% scale guides further investment; it does not gate the initial prototype or prove equivalence below it.

Possible final states:
- R81_KNOWN_SOFTWARE_SUFFICIENT_IN_SCOPE
- R81_LEGAL_SUPPORT_NOT_MATERIAL_IN_SCOPE
- R81_SOFTWARE_OPPORTUNITY_NO_ARCH_CLAIM
- R81_NUMERICAL_OR_BASELINE_NOT_QUALIFIED
- R81_GPU_ORGANIZATION_RESPONSE_REQUIRES_REVIEW

The final response state needs exact scopes, strongest baseline, natural mask evidence, qualified output, control/holdout and competing explanations. It is NOT architecture admission. If known software directly supplies the entire capability, report that even if it speeds up greatly.

## 8. Deliverables and STOP

Review pack:
`docs/vm_tlb/review_packs/AWMA_R81_LEGAL_VOCAB_EXPLORATION_V1/`.
Minimum: README/DECISION, SOURCE_CAPABILITY_MAP.md, PREREGISTRATION.json, INPUT_RUNTIME_BINDINGS.json, MASK_WORK_SUMMARY.tsv, SEMANTIC_RESULTS.tsv, TIMING_RESULTS.tsv, optional diagnostics/holdout, SOURCE_AND_TESTS, RAW_DATA_INDEX.tsv and SHA256SUMS. Explicit NOT_RUN for unexecuted phases.

Follow shared164/Git closure. Do not wait for R82; do not start an Accel-Sim model, another research topic or new model download. STOP after the bounded result is published.
