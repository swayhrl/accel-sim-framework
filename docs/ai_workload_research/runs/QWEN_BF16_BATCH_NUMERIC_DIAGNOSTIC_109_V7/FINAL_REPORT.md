# V7: RSS lifecycle repair and BF16 Batch numeric diagnostic

Final execution status: **NUMERIC_OR_RUNTIME_NO_GO**, specifically the frozen numeric qualification gate. Performance conclusion: **INCONCLUSIVE**.

Both pre-frozen diagnostic groups completed in one real strong compiled BF16 engine. All6 requests and8 completions were persisted before numeric admission. A00 reproduced the V5 failure exactly in both groups. A01 passed the sampled-logprob tolerance. No six-point warmup or formal request was executed, and no performance ranking or hardware candidate is produced.

## Decisive independent numeric result

Both groups produced exactly the following values:

| Source | B1 selected logprob | B2 selected logprob | Absolute difference | Frozen allowance | Result |
|---|---:|---:|---:|---:|---|
| A00 | -0.9105782508850098 | -1.0132758617401123 | 0.10269761085510254 | 0.0591057825088501 | FAIL |
| A01 | -1.2801917791366577 | -1.335237741470337 | 0.0550459623336792 | 0.06280191779136658 | PASS |

Tokens were identical between B1/B2 for each source. For each corresponding point/source, the entire returned top20 dictionary was exactly identical between Group1 and Group2, not merely within tolerance. All returned logprobs were finite. The two A00 B1 records and two A00 B2 records also exactly match the entire corresponding preserved V5 top20 dictionaries.

The independent CPU recheck derives the source from the actual returned512-token prompt array's canonical hash, compares request_id and public/private hashes, checks selected-token dictionary lookup, and verifies all saved ranks/logprobs. It does not trust the source label alone. All8 completions pass those observation/identity checks. V5's missing P3 A01 remains missing; V7's newly observed A01 is not substituted into V5.

For A00, the20 common-token B2-minus-B1 deltas range from -0.22769784927368164 to +0.14730238914489746, span0.3750002384185791. For A01 they range from -0.0550459623336792 to +0.19495439529418945, span0.25000035762786865. These are nonuniform changes, not a common scalar log-normalization offset. Relative changes are almost multiples of0.125, with residuals at most2.384185791015625e-7(A00) and3.5762786865234375e-7(A01). This is a signature compatible with rounded score changes plus normalization, not proof of a particular operation.

A01 PASS refers to the frozen sampled-token gate; no new requirement that all20 token probabilities match tolerance was introduced. Full top20 values and ranks are retained and analyzed separately. Neither threshold nor precision was changed.

## Supported interpretation and missing evidence

The strongest supported classification is a **stable BATCH_EXECUTION_PATH-associated score-vector difference**, with the computational origin **UNRESOLVED**. Two matched groups and the independent V5 A00 records make a transient first-use observation or source-pairing mistake a weaker explanation. This remains an association with submitted B1/B2 execution, not proof of a specific model layer or kernel.

MODEL_FORWARD_NUMERIC and LOGPROB_OR_SAMPLER_NUMERIC remain competing explanations. V6's read-only installed-source review shows default raw_logprobs, FP32 log_softmax and token-keyed probability gathering. It also identifies a model-dtype lm_head default and an optional separate FP32-head path. V7 enables no alternate path. Source defaults cannot prove actual intermediate dtype or uniquely localize a difference.

A common raw-logsoftmax path would make token-pair log-odds differences cancel scalar normalization; the observed nonuniform vector would then require changed relative scores upstream or a nonuniform implementation effect. No hidden states, full-vocabulary pre-normalization logits, sampler intermediate tensors or per-kernel shapes were recorded. The allowed observations therefore cannot directly attribute this failure to BF16 kernels, model forward, lm_head or sampler.

OBSERVATION_OR_PAIRING_DEFECT: the old partial-capture problem is fixed and all actual returned prompt identities are verified. No observed pairing/lookup defect explains the V7 failure. No new profiler or precision experiment was added to resolve the remaining ambiguity.

## Actual scientific execution identity

Model:Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1;BF16,TP1,no quantization. One engine,capacity544/1088/2,VLLM_COMPILE/inductor/FULL_AND_PIECEWISE,FlashAttentionImpl and UnquantizedLinearMethod. Actual runtime:vLLM0.30.0,torch2.13.0+cu130. Source hashes match the accepted authority. Constructor completed once;initialization took60.1747266753seconds,inside the GPU budget.

Every diagnostic request has an active compiled and AOT Qwen2Model snapshot. All compilation counters remained unchanged across each generate and no new graph descriptor was added. Manager-level fullgraph replay count was0 for all output1 requests. These requests exercise prefill plus first-token return; this observation does not imply eager fallback or establish every internal piecewise/kernel shape. Both P3 submissions returned two requests with actual512-token prompt identities, correct source order and output1 each. Requested B2 is recorded separately from unmeasured per-kernel batch/tensor shapes.

The diagnostic order was exactly:
Group1:P1(A00 B1 output1),P2(A01 B1 output1),P3(A00+A01 B2 output1);
Group2:the same three points in the same order.
The second group ran despite the first A00 numeric failure because runtime/resources remained qualified. Both failures were retained. The worker stopped only after both fixed groups, without selecting passing samples or entering six-point warmup.

Sampling and the full-generate timing boundary are inherited unchanged. Private completion evidence includes returned prompt IDs,request_id,all completion token IDs,top20 logprobs/ranks,sampled-token logprobs and termination metadata. Public raw includes hashes,compiled/Graph counters and complete-generate CUDA-event/host times. All batch completions and execution-state snapshots are persisted before qualification. Diagnostic timings are not formal measurements.

The inherited scientific-field SHA remains:
8571824801bf46ae9f1c84c55470274e580fa7d8b9ff5491ded36e87172a5397.
No output32 request or full32-token historical check was reached in V7. The original historical reference is unchanged. No six-point medians,MAD,deltaA00,deltaA01,deltaB2 or R are calculated; their performance fields remain null.

## V6 RSS failure and explicit V7 resource-contract change

V6 authority29a86372d47f622afe1e1a53b675b8f1cd499a16/treec2f954519910af464548e5f4fc631437a318c12f is immutable. Its failed snapshot is copied into V6_RSS_RACE_EVIDENCE.json. PID3542974 was enumerated as an own descendant and disappeared before memory_info. V6 treated that missing RSS as a mandatory gap, stopped and released its only lock before any generate.

V7 adds a narrow resource observation rule, frozen before the GPU attempt:
1. The process object must come from the current successful own-tree enumeration with bound creation_time; no historical PID whitelist.
2. Fresh identity checks must not show reuse/conflict.
3. Only psutil.NoSuchProcess is eligible; two rechecks must show disappearance. A still-live process,AccessDenied or another exception remains fatal.
4. Root and actual worker must retain identity and be alive/nonzombie. Neither root nor worker can be an exited-child exception.
5. Both NVML inventories,process identity/memory,single actual GPU worker,external qualification,kernel lock,Image-Lab reservation/loaded gate/quiescence and runtime activity policy must remain valid.
6. A pending candidate is finalized as OWN_EXITED_CHILD_RSS_RACE only after all other mandatory checks/caps succeed. Another independent gap prevents finalization and causes STOP.

A missing exited-child RSS is null and censored, never0. Observed live RSS is explicitly a subtotal, not a complete process-tree peak. This is a V7 contract change, not a reinterpretation or edit of V6.

CPU-only investigation found root-owned,read-only dedicated SSH-session cgroup memory.current/peak. The actual GPU session was bound to session-88766.scope,device30/inode14824984;its initial members were only the supervisor and ancestors. Worker membership and cgroup identity were checked throughout. Kernel charged-memory peak retains charges from exited tasks and supplements the RSS snapshots. No privilege,cgroup setting or memory.max was changed.

The16GiB rule now applies to both sampled live-RSS subtotal and session charged-memory high-water, stopping at an observed exceedance. This is not a hard kernel-enforced limit and neither metric is exact continuous summed-process RSS. Shared-page charging and duplicate RSS accounting differ;brief wholly-between-sample RSS peaks are not reconstructed. The independent cgroup high-water observes charged-memory spikes including exited children,not their exact historical RSS. RESOURCE_OBSERVATION_CONTRACT.json freezes these guarantees and limitations.

## CPU tests and actual resource interval

65 CPU tests passed:49 inherited plus16 new tests covering natural/controlled rapid exit,NoSuchProcess,live AccessDenied,PID reuse,root/worker exit,unknown external compute,GPU identity change,legal race plus another gap,gate/activity failure,caps,session peak and cleanup. The initial3 telemetry-only mock errors caused by an absent test-config cap were repaired before freezing;the initial log remains preserved. No GPU had been attempted at that point.

The actual V7 interval had34 resource samples and no mandatory monitoring gap. No exited-child race candidate occurred in these snapshots,so the narrow acceptance path is CPU-tested but was not triggered in this GPU run. Normal child lifecycle and strict GPU identity checks remained active.

The sole common-lock acquisition used fcntl.flock LOCK_EX|LOCK_NB on /data/c16/locks/c16_gpu_campaign.lock. Device/UUID matched the RTX4080 authority. Image-Lab's accepted actual process incarnation,loaded code/profile,quiescence,child drain,reservation and real kernel holder were checked live. There was no Image-Lab deployment or new canary. Completed scopes remained18,inflight0 throughout. Unknown/unqualified compute tasks were not admitted. Existing desktop per-process NVML activity attribution remains unavailable and explicitly prevents treating the measurement environment as fully exclusive.

Condition label:VERIFIED_GATED_RESIDENT_CO_RESIDENT_NATIVE_OBSERVATION.

GPU held68.0138111664seconds. Available observed peaks:own NVML14314MiB;live-tree RSS subtotal4,233,228,288bytes;kernel session charged-memory3,671,056,384bytes;conservative whole sparse-worktree disk154,823,824bytes. All observed caps pass. Whole-Goal elapsed and final disk accounting are recorded in RECEIPT.

Own CUDA context cleared,the shared lock unlocked/closed,NVML client shut down,and only the own reservation was deleted. Post-release status:IMAGE_LAB_IDLE,inflight0,queue[0,0],no reservation or kernel lock holder. Other processes were not signaled. Downloads,installs,164,Profiler/NCU/NSYS/NVBit,simulator and RTL executions were0.

## Decision and archive

The numerical failure is reproducible under the frozen observations; the original six-point performance comparison is ineligible. H1 weight supply and H2 compute/scheduling are not separated. H3 is reduced by actual source/input/compiled identity evidence but internal score-path ambiguity remains. Conditional weight bytes are not measured DRAM,ordinary Batch reuse is not hardware innovation,and no hardware candidate follows.

V1-V4 resource/engineering STOPs,V5 numeric failure,V6 RSS STOP and V7 reproduced numeric STOP remain distinct. Old resource STOPs are not performance negatives. V1-V6 raw/contracts/receipts are unchanged. New paths alone contain V7 execution tools,tests,resource policy,actual raw,independent analyses,completion hashes and reports. Postrun CPU analysis is separately identified and changes no frozen execution source. Full completion/token data remains in the owned ignored private directory with SHA index,not redistributed as a dataset.

This Goal ends after exact Git publication and remote commit/tree/blob verification. No V8,Batch extension,tolerance change,profiler or hardware-development task starts.
