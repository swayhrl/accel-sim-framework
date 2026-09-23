# AWMA dual-track research / literature-guided mechanism exploration V1

Date: 2026-09-23
Stage: `AWMA_LITERATURE_GUIDED_MECHANISM_EXPLORATION_V1`
Node: 174-new, NEW independent Codex window/worktree
Mode: bounded exploratory Goal / solve-and-continue

## 1. Research-method update and execution boundary

The user authorizes two complementary discovery directions:

- Lane A: characterize behavior, then propose mechanisms.
- Lane B: try literature-inspired mechanisms, then investigate why successful or unsuccessful interventions change behavior.

Complete bottleneck attribution, or a measured >=5% headroom, is NOT a prerequisite for Lane B. Mechanism trials may themselves be diagnostic interventions. Discovery and confirmatory validation remain distinct.

Do not change or interrupt the running Lane A task:
`AWMA_RTX4080_V1_AI_TRANSLATION_BOTTLENECK_CHARACTERIZATION_V1`.
Its current no-mechanism instruction still applies within that worktree/Goal. It is not a project-wide ban on this separately authorized exploration lane.

Do not run Accel-Sim on 109, start Native recapture, resume unrelated C16/E1/MoE tasks, or download models in this Goal. node164 remains durable asset/evidence authority.

## 2. Read-only baseline and exact authorities

Repository: `swayhrl/accel-sim-framework`.

Baseline publication:
`hrl/awma-174-rtx4080-v1-baseline-promotion-v1 @ 8d1f14a32f5538660d74da86ccb03a2c504c5735`.

Read its pack:
`docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/`.
In particular: baseline JSON, baseline.env, both VM overlays, AI_TRACE_AUTHORITY.tsv, AI_MATRIX_CONFIG_AUTHORITY.tsv, AI_PROMOTION_MATRIX.tsv, KNOWN_LIMITATIONS.md, SOURCE_ANCHORS.md.

Frozen definition:
- `AWMA_RTX4080_SIM_BASELINE_V1`, promoted with scope;
- platform config SHA256 `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`;
- baseline binary SHA256 `a866c219b7d71a3075e032c9179bcd679074d6f2e9f1750b435170aabb413b24`;
- primary VM overlay 10/80 SHA256 `ac969a49721f94010accd9b51130bcf7a6d4305500791ecafabd906cbfe4fe71`;
- diagnostic 0/80 SHA256 `5f2d22fd07954fbb8fcb22480cb618a997a3a6aa2f9667265c2ca9b8765bc685`;
- V1 launch ON, V2 READY application OFF;
- V1 semantic source `ad6f38878bc1e7c268b17e65fdb3793a3899a84d`;
- V2R1 diagnostic reference `dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8`;
- Segment F0 stays dormant in the baseline and in the first Lane B candidates.

The running Lane A handoff was independently read at:
`hrl/awma-post-baseline-characterization-handoff-v1 @ 5ec8c41e4fa1a657bece805c13b792affe84a9ab`.
Do not import its unreviewed working-tree modifications or wait for its results to start independent work.

Baseline frozen means the COMPARATOR is immutable. It does not forbid explicitly named candidate mechanisms from changing the translation policy, adding finite metadata, or reducing physical lookup traffic. Every candidate delta must be explicit, charged, and opt-in; unrelated platform parameters remain unchanged.

The 10/80 versus 0/80 delta is a sensitivity to one modeled latency parameter, not a strict upper bound on all translation mechanisms. T1 is not excluded simply because its current delta is small. Summed stall cycles across overlapping warps are not recoverable kernel cycles.

## 3. Primary-source reading and candidate cards

Start with a bounded primary-source survey. Reuse previous reading rather than creating another large literature project. Initial sources checked by ChatGPT:

1. LATPC, MICRO 2025: Ha et al., DOI `10.1145/3725843.3756069`.
   Author-institution abstract: https://yonsei.elsevierpure.com/en/publications/latpc-accelerating-gpu-address-translation-using-locality-aware-t/
   Its stated components include warp-level VPN regularity, TLB prefetching, compressed MSHR representation, and batched walks. This handoff has NOT verified its full implementation. A simplified derivative must not be called a faithful LATPC reproduction.
2. DEPOT: Anik et al., `Dead on Arrival: Characterizing and Protecting Against Dead-Entry TLB Misses in GPU Microarchitectures`, arXiv:2606.00486v1, 2026 preprint.
   https://arxiv.org/html/2606.00486v1
   Especially Sections 4-7. Eviction-history protection distinguishes interference-driven from capacity-driven misses. Do not import its workload-specific benefits or original platform assumptions into AWMA.
3. SnakeByte, HPCA 2023, DOI `10.1109/HPCA56546.2023.10071063`.
   Author-institution abstract: https://pure.korea.ac.kr/en/publications/snakebyte-a-tlb-design-with-adaptive-and-recursive-page-merging-i/
   Recursive page merging relies on contiguity and associated mapping/allocation support. It is reading/novelty context, not an authorization to rewrite accepted maps.
4. Towards Segmentation-Based Address Translation for LLM Inference, CAL 2026, DOI `10.1109/LCA.2026.3693796`.
   Author-institution abstract: https://pure.korea.ac.kr/en/publications/towards-segmentation-based-address-translation-for-llm-inference/
   Weight-specific segmentation assumes suitable virtual AND physical contiguity. Do not infer those from VA adjacency or re-enable frozen Segment machinery indiscriminately.
5. cuPTW, 2026: https://maxkev1n.github.io/publications/sigmetrics-2026/
   Uses otherwise-idle compute resources for page walks. Review for design-space context; full compute-assisted PTW is not a first-pass low-cost prototype.

Read full original method sections before claiming reproduction. If full text is unavailable, record the limitation and keep the prototype explicitly paper-inspired. Do not reconstruct undocumented algorithms from a title or an AI summary. Do not claim novelty based on this initial list; broaden closest-prior-art search for any survivor.

For each candidate write one short card BEFORE performance screening:
- original source and what it actually supports;
- our distinct change versus frozen V1;
- why worth trying (hypothesis, not established fact);
- bounded state, ports, lookup/notification cost;
- expected observable mediators and useful negative controls;
- what is reproduction, adaptation, or newly hypothesized;
- one fixed first configuration, chosen without consulting its performance results.

## 4. First-pass candidate portfolio

Prefer two local prototypes from the three below. A third is allowed only if genuinely inexpensive or replacing a candidate already implemented by the baseline. Do not require Lane A to prove the bottleneck first. If a candidate has zero opportunity on the screen, record that result rather than creating a workload solely to make it win.

### C1: same-page translation-result sharing

Question: can multiple sector accesses of one resident warp memory instruction share one legal translation service/result instead of independently paying redundant lookup work?

This is an AWMA exploratory adaptation inspired by warp-local translation regularity, not a claim of novelty or a complete LATPC reproduction. It is distinct from V1's early launch if it reduces distinct physical lookup services, rather than merely launching them earlier. First inspect accepted source to ensure that this exact service-level sharing does not already exist. Existing same-VPN miss merging alone is not proof that hit-path/READY-result sharing exists.

Use a finite, instruction-scoped cohort or similarly bounded representation. Charge grouping/notification cost and finite delivery bandwidth. No instantaneous unlimited broadcast, no future trace information, no infinite CAM/cache.

Only legally equivalent translations may share: address-space identity, page granularity, mapping generation where supported, access permissions/type, and page-boundary checks must agree. Preserve each logical access UID, per-access PA/offset validity, admission ordering and exactly-once data effects. Distinguish physical translation service count from logical translated access count.

The accepted V1 `consume_ready` ownership API is a hard constraint for baseline mode. Its patch is in the accepted V1 pack as `READY_OWNERSHIP_REPAIR.patch`. Candidate sharing needs a consistent owner/member completion protocol; do not strand READY entries or simply mark unobserved members translated. All candidate-owned tables must drain. Off restores accepted V1 exactly.

### C2: bounded eviction-history refill protection

Question: does temporarily protecting a recently evicted and subsequently refilled translation improve progress without expanding TLB reach?

Use DEPOT's original method as the reading basis; specify any simplified adaptation explicitly. Keep baseline translation capacity and latency unchanged. Bound history metadata and protection lifetime; publish total bits, not just the filter. Define wrap/reset behavior and an unprotected/LRU fallback so all-protected sets cannot deadlock. Never pin all entries indefinitely.

Record useful/protected refills, avoided rewalks if source-supported, extra misses/pollution, and fallback activity. No effect under little eviction is a valid result, not a broken experiment.

### C3: bounded history-based translation prefetch (reserve)

Question: can a small, past-access-based lookahead hide a recurring translation delay?

This is a simplified exploration inspired by translation prefetching work, not LATPC reproduction. Use only information available by the simulated decision time. Never read future trace addresses, preinstall arbitrary PAs, or treat a map lookup as a free PTW. Predictions must traverse the appropriate modeled service path with finite queue/MSHR/walker/port cost, demand priority, and bounded pollution. Unsupported fault/permission behavior must fail safely without generating demand side effects. Record useful, late, unused, dropped and interfering prefetches.

If implementing legal prefetch requires a large controller redesign, defer C3 instead of expanding infrastructure.

Do not implement all literature families, combine candidates, add a large hyperparameter sweep, or start cuPTW/wafer-scale/multi-GPU reconstruction in this pass.

## 5. Isolation and resource policy

Suggested execution branch: `hrl/awma-174-literature-guided-mechanism-exploration-v1`.
Create independent worktree, private build/library paths, executable outputs, config copies and run directories. Never relink or overwrite a binary being used by Lane A.

Inspect CPU, RAM/swap, I/O, node164 health and existing jobs before launching. Lane A keeps its existing allocation. Use spare capacity for Lane B and cap concurrency if contention becomes material. No kill/pause/restart of Lane A. Development, literature work, candidate-local tests and independent replays can overlap; no need to wait for scientific admission when all execution inputs are already fixed.

All candidate functionality is opt-in, default OFF, preferably one centralized mode selector with `none` plus mutually exclusive first-pass modes. New diagnostic switches are separate and observational-only. Do not globally enable a candidate. Off-equivalence is against accepted V1, not Legacy.

Allow local candidate changes, not comparator tuning. Added capacity/ports/storage must be declared and costed; a survivor needs a resource-matched simple comparator later. Preserve the baseline's known concurrency limitation rather than silently repairing it inside a candidate.

## 6. Cheap testing and initial screen

Before expensive runs, use small directed tests for the actual new code: hit/miss, same/different key, incompatible permissions, cross-page access, backpressure, repeated observation, exactly-once completion and terminal quiescence. Reuse existing tests. Candidate-local ordinary failures are solve-and-continue; isolate/discard a costly or invalid candidate rather than blocking the entire portfolio.

Use accepted T0/T1/T2 payloads from the frozen AI trace manifest. These are DISCOVERY data, not holdouts. Keep all three in the initial portfolio regardless of their observed sensitivity. Prioritize fast execution when scheduling, not selective reporting. M0-M3 and A1/A8/A32/A32_W8 may serve as cheap positive/negative opportunity controls, not substitutes for AI evidence. In particular A1 has four 32B sector entries, not one accessq entry.

First screen: two prototypes x T0/T1/T2 x primary 10/80 = six candidate AI points. Baseline results may be reused only if exact source/runtime/config/input/initial-state compatibility is established; otherwise rerun necessary baseline controls once and share them across candidates. Do not reuse an incompatible scalar just to avoid runtime. Do not compare partial progress with a terminal kernel result.

For a promising candidate, add matched 0/80 diagnostics and at most one informative ablation on the target showing the effect. Do not automatically expand every losing candidate to a full matrix. Do not assume a gain that survives 0/80 must be invalid; the diagnostic removes only modeled L1 lookup delay. Equally, don't infer PTW causality solely from that gain.

Reuse accepted initialization/trace-context policies. When contextual comparisons are used, execute the same prior instruction sequence under each candidate to generate its own legal state; do not transplant baseline microarchitectural state or use future information. Report isolated versus contextual scope honestly without redoing frozen context qualification.

For each result retain cycles, instruction/CTA identity, logical unique translation coverage, physical lookup/service counts, queue/walk/traffic indicators relevant to that candidate, no untranslated/unobserved, side-effect correctness and full terminal drain including lookup/READY and candidate-owned state. No missing diagnostic may silently parse as zero/PASS.

One fixed configuration per candidate first; no speculative combinations or tuning to the Native ratios. A lower service count without time improvement is still useful structural evidence, not automatically a performance success. Keep negative results and regressions.

## 7. Selection, explanation and later independent confirmation

Report promising / no material effect / regression / inactive on this screen / invalid implementation separately. No universal percent threshold determines paper worthiness. Rank by reproducible kernel-level benefit, relevant mediator changes, overhead and distinctness from prior work. Huge synthetic-only gains, unlimited-resource gains, or gains concentrated only in the known concurrency mismatch require qualification before any paper claim.

For a survivor, freeze its version before proposing confirmatory tests. Explain using intervention/ablation rather than retrospectively asserting that the original hypothesis was known. For example, enable grouping while retaining a matched service-cost control, or remove refill protection while retaining metadata, as appropriate to the actual mechanism. Resource and timing ablations must be described honestly.

Prepare one small validation plan with an unseen invocation/input/operator or independent model-family anchor selected from accepted assets by a written criterion. T0/T1/T2 and all already-consulted calibration probes are not independent validation. If no admissible held-out input is currently available, record the needed follow-on capture; do not automatically start 109.

Review closest prior art for any survivor. A prior mechanism working on AI workloads is a useful baseline/result, not automatically a novel mechanism. Distinguish new insight, AI-specific adaptation and new architecture contribution.

Lane A and B meet at scientific review. A negative characterization on three current targets does not ban bounded trials on other justified workloads. A positive exploratory speedup does not establish broad LLM benefit. Baseline promotion and paper conclusions are NOT automatic.

## 8. Lean publication and STOP

Do not create a new framework or dozens of audit documents. Publish executable prototype code/tests plus one small review pack:
`docs/vm_tlb/review_packs/AWMA_LITERATURE_GUIDED_MECHANISM_EXPLORATION_V1/`.

Required content can fit in:
- `REPORT.md`: source-backed candidate cards, exact delta/cost, reading limitations, findings/negative results and next discriminating test;
- `EXPLORATION_MATRIX.tsv`: all admitted and rejected trials, source/config/input hashes and status;
- `RUN_RECEIPTS.json`: executable authority, commands, gates and raw references;
- `RAW_DATA_INDEX.tsv`: node164 durable evidence references;
- `SHA256SUMS`: all published evidence members.

Full runtime/large raw stays on node164; working scratch is bounded. Preserve existing accepted evidence. Fix obvious harmless wording/derived-wrapper issues in this same publication, not a separate repair Goal. Follow EXECUTION_PRIORITY_POLICY_V5: distinguish P1 payload, P2 derived controls, P3 provenance and P4 runtime artifacts; reconstruct deterministic wrappers before declaring BLOCKED.

Commit/push, fetch-back, exact remote HEAD/tree/hash and nonempty/schema checks, clean worktree, then STOP. Use the existing HTTPS-to-SSH fallback without regenerating scientific results for a transport failure.

Do not merge candidates into the promoted baseline, change Lane A, or begin a larger mechanism campaign automatically. The end product is a small tested portfolio plus evidence-backed explanations to review, not a claim that a publishable invention has already been found.
