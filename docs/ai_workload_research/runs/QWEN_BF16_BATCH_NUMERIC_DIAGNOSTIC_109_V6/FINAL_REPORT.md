# Qwen BF16 Batch numeric diagnostic V6

Execution status: **GPU_RESOURCE_DEFERRED**. Scientific result: **INCONCLUSIVE**.

V6 independently verified V5 authority 065b3e91eb8b29db215b3e82b06624e3f2df94b0 / tree133854121895b8bb9a418082fdf74800a914fb40, analyzed its preserved private outputs, fixed whole-batch evidence persistence, and passed49 CPU tests. The sole nonblocking common lock acquisition and V5 shared-resident admission succeeded. During model initialization an own descendant exited between process enumeration and RSS collection. The inherited monitor stopped, and the sole lock was released. No diagnostic generate returned and no six-point request ran. No second GPU attempt follows.

## Original numeric facts

| Quantity | Preserved V5 observation |
|---|---:|
| A00 B1 P1 selected first-token logprob | -0.9105782508850098 |
| A00 B2 P3 corresponding logprob | -1.0132758617401123 |
| Absolute difference | 0.10269761085510254 |
| Frozen allowance | 0.0591057825088501 |
| Common top-20 tokens | 20 of20 |
| Minimum B2 minus B1 common-token delta | -0.22769784927368164 |
| Maximum common-token delta | +0.14730238914489746 |
| Delta span | 0.3750002384185791 |
| Residual from relative0.125 lattice | at most2.384185791015625e-7 |

The selected token is identical and present in each token-keyed returned logprob dictionary. Independent CPU recomputation matches V5 public token/logprob hashes. V5 asserted each returned prompt array equals its expected frozen source before saving; the recorded source order was A00 then A01. V5 did not independently preserve returned prompt arrays or request IDs, so that mapping is supported by the executed assertion and saved source record, not a separately captured input echo.

A00 P1 and P4 first-token logprobs are identical. P4's32 tokens and sampled logprobs exactly match the historical reference. No selected-token lookup, rank-position confusion or source-swapping error was found. The preserved A00 failure remains valid under the frozen tolerance.

The common-token difference vector is nonuniform; a scalar normalization offset alone cannot explain it. Nearly0.125-spaced relative changes are consistent with rounded score changes plus a normalization term. This signature does not prove a particular BF16 operation or kernel. Under a common raw-logsoftmax path, token-pair log-odds differences cancel normalization and would imply altered relative scores upstream. Effective V5 sampler mode/intermediates were not independently captured, so that inference is conditional.

Read-only installed-source inspection finds default raw_logprobs, FP32 log_softmax and token-keyed sampled/top-k gathering. The lm_head defaults to model dtype and offers a separate optional FP32-head path; V6 does not enable it or alter precision. SAMPLER_SOURCE_REVIEW.json preserves paths, hashes and excerpts. No logits, hidden states, actual sampler-input dtype or per-kernel trace was captured. Source defaults do not replace runtime evidence.

## Competing explanations

- MODEL_FORWARD_NUMERIC: possible shape-dependent hidden-state or lm_head effects; no tensor evidence localizes them.
- LOGPROB_OR_SAMPLER_NUMERIC: possible; source inspection does not prove actual normalization/backend behavior.
- BATCH_EXECUTION_PATH: submitted B1/B2 request count differs. V5 P3 final compiled/Graph snapshot was not saved. A two-request submission is not a measurement of every internal kernel shape.
- OBSERVATION_OR_PAIRING_DEFECT: the partial-batch persistence defect is confirmed; it does not negate saved A00. No observed pairing defect explains that difference.
- UNRESOLVED: no unique forward/sampler/kernel cause and no V6 completion to assess repeatability.

V5 B1 snapshots show active compiled Qwen2Model; P4/P5 each show31 fullgraph replays. P3's missing snapshot must not be interpreted as eager fallback. Its A01 completion is unavailable and has not been reconstructed, substituted from B1 or regenerated.

## V6 engineering and frozen plan

The new capture helper converts every returned request and completion, returned prompt IDs, request ID, tokens, top20 logprob/rank metadata and completion termination metadata. It persists the full private batch, public hashes and available compiled/Graph state before numeric gates. CPU tests demonstrate first-completion failure still preserves the second completion and graph/compiled evidence; multiple returned completion alternatives are also saved before rejection.

AST checks preserve LLM, SamplingParams and CompilationConfig calls and the exact CUDA-event/host timing operation sequence. Thresholds remain abs(actual-reference)<=0.05+0.01*abs(reference), exact tokens/lengths and all returned logprobs finite.

The inherited science-field SHA is unchanged:
8571824801bf46ae9f1c84c55470274e580fa7d8b9ff5491ded36e87172a5397.

A separately frozen V6 extension specifies exactly two groups, each P1(A00 B1 output1), P2(A01 B1 output1), P3(A00+A01 B2 output1). Both fixed groups would be retained for repeatability even after numeric-only failure, with no passing-group selection. Runtime/backend/resource failure stops immediately. Only all gates passing permits the same engine's original two warmup rounds and five formal rounds. Diagnostics never enter formal statistics. No generate was reached.

Model revision,BF16/TP1/no quantization,A00/A01 natural512-token inputs,strong Mode A,544/1088/2,sampling,P1-P6 matrix,interleaving,historical reference and timing are unchanged. Twelve SHA-qualified assets retained exact inode/size/mtime/ctime fingerprints; small source/package/input/reference identities were rechecked. New full-model hash bytes=0. No download or dependency change occurred.

## Actual admission and STOP

Common lock:/data/c16/locks/c16_gpu_campaign.lock;fcntl.flock LOCK_EX|LOCK_NB;dev66306/inode8269816. Exactly one attempt and one acquisition. Actual RTX4080 UUID matched GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59.

The V5-approved Image-Lab incarnation,build/run nonce,loaded hashes,live profile,kernel lock holder,own authenticated reservation,quiescence and child-drain proof were revalidated. V5's deployment/source audit and real parent/child canaries were reused; no new Image-Lab GPU work was triggered. Three bounded pre-model utilization samples were0%,within1.303seconds. Across16 snapshots Image-Lab completed scopes remained18,inflight0. Unknown and unqualified external GPU PID lists stayed empty.

Snapshot14 records RSS_PID_3542974:NoSuchProcess. That PID had just been enumerated as an own descendant while compilation/initialization was active. Worker3542763 had valid14290MiB NVML memory; all external GPU processes were qualified. Thus generic error ?Unknown GPU PID/memory or incomplete resource observation? specifically arose from an own process-tree RSS race, not unknown external compute,Image-Lab execution or lock conflict.

The inherited strict policy maps any RSS gap to STOP and was not relaxed after the fact. Only the own worker group was terminated. Own CUDA context cleared,common lock unlocked/closed,NVML client shut down,own reservation removed. Post-release status:IMAGE_LAB_IDLE,inflight0,queue[0,0],no reservation or kernel holder. Other projects were not signaled.

One model constructor was attempted; the log reached graph capture. Constructor completion and subsequent complete strong-runtime assertions were not observed. raw/PROBE.json remains its genuine last checkpoint RUNNING,model_initializations1,samples[]. Supervisor SIGTERM prevented final Python status persistence. RESOURCE_RECEIPT and ANALYSIS carry the terminal resource STOP; raw is not rewritten.

Desktop per-process activity attribution was unavailable under the accepted V5 interpretation policy. This is separate from the later mandatory RSS-gap STOP. The condition is VERIFIED_GATED_RESIDENT_CO_RESIDENT_NATIVE_OBSERVATION,not exclusive or proven free of interference.

## Resources and decision

Lock held25.0024966234seconds<1500. Available sampled peaks:own NVML14290MiB,tree RSS2,621,706,240bytes,conservative whole sparse-worktree disk66,353,716bytes. These meet available-sample caps but are not continuous whole-Goal high-water measurements; exited-child RSS is precisely the missing observation. Final elapsed/disk accounting is in RECEIPT.

Actual diagnostic requests0,groups0,warmup0,formal0. All three TSVs contain headers only. Medians,MAD,deltaA00,deltaA01,deltaB2 and R remain null. No numerical replication claim,performance ranking or hardware candidate is produced.

H1 weight supply and H2 compute/scheduling remain unseparated; H3 execution identity remains an evidence requirement. The inherited bandwidth model is conditional,not DRAM measurement. Ordinary Batch sharing is not hardware innovation. SOFTWARE_EXCLUSION.md is inherited authority,not repeated literature research.

V1:pre-model NVML API defect. V2:strict external-process resource rejection. V3/V4:ungated ordinary compute rejected. V5:shared admission passed; actual numeric failure plus partial capture. V6:shared admission passed; own RSS-monitor race before any diagnostic generate. These resource STOPs are not performance negatives.

All executed source hashes match the prelock freeze. Raw logs,snapshots,source copies,tests,numeric analysis and private-data hashes are preserved under V6. independent_analysis.py is post-STOP CPU-only analysis. No V7,Batch extension,tolerance change,profiler or hardware task is started.
