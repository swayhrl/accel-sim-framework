# V8 BF16 Batch performance, numerical sensitivity and strong software controls

Final execution status: **V8_STUDY_COMPLETE**.
Performance result: **complete native descriptive measurements under verified gated-resident sharing**.
Numerical result: **historical logprob threshold still FAILs;role explicitly changed to observation**.
Architectural result: **MEMORY_SUPPLY_CONSISTENT_NOT_CAUSALLY_PROVEN**.

V8 completed255 real generate calls,340 completions and150 formal samples across five separate configurations. Two engines ran serially under one common-lock acquisition;GPU ownership never overlapped. Main required six points completed first,then time-interleaved logprobs controls,post-formal tensor observation,and controlled prefix-cache experiments. No adaptive extra block was triggered by the pre-frozen MAD/capture rule. All samples,including outliers and token divergences,are retained.

## A. Actual strong full-request performance

Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1,BF16,TP1,no quantization. A00/A01 are the accepted natural512-token arrays. Actual vLLM0.30.0 uses VLLM_COMPILE/inductor/FULL_AND_PIECEWISE,FlashAttentionImpl and UnquantizedLinearMethod,capacity544/1088/2.

The table contains all five formal samples' median and unscaled MAD. Formal raw rows are in FORMAL_SAMPLES.tsv;full per-request execution records are indexed under raw/BASE.json and raw/PREFIX.json.

| Point | Request | CUDA-event median ms | MAD ms | Synchronized Host median ms |
|---|---|---:|---:|---:|
| P1 | A00 B1 output1 | 36.295681 | 0.039040 | 36.360249 |
| P2 | A01 B1 output1 | 36.332703 | 0.136127 | 36.384041 |
| P3 | A00+A01 B2 output1 each | 69.971649 | 0.128418 | 70.020533 |
| P4 | A00 B1 output32 | 353.995789 | 0.019562 | 354.055923 |
| P5 | A01 B1 output32 | 354.095276 | 0.310547 | 354.163545 |
| P6 | A00+A01 B2 output32 each | 397.706573 | 0.091125 | 397.767042 |

The original formulas give:

- deltaA00=317.7001075744629ms.
- deltaA01=317.7625732421875ms.
- deltaB2=327.73492431640625ms.
- denominator=317.7313404083252ms;R=1.031484410367656.

The denominator is positive and roughly1258 times the simple summed-MAD envelope. All primary point MAD/median values are below0.4%. These are descriptive stability checks,not confidence intervals or proof of no external interference. Minimum,maximum,all values and first/last drift diagnostics are retained in PERFORMANCE.json.

Two requests add only about3.15% to the mean single-request32-minus1 increment. Their incremental aggregate amortization factor is1.93895. Full32-token aggregate throughput is90.40tok/s for A00 B1 and160.92tok/s for B2. Two separate B1 request medians sum to1.78044 times the B2 median. B2's full32 request time is12.33% above the mean B1 request;its first-token request time is92.68% above mean B1. Thus prefill/first-token and incremental-generation behavior differ substantially.

These are complete generate measurements:pre-sync,eventstart,generate,eventstop,post-sync. Host call and synchronized Host wall are independent columns. CUDA-event elapsed includes the complete request's device timeline,including gaps caused by host/control work;it is not isolated GPU busy time or pure Decode-kernel time. The32-minus1 differences are not pure Decode measurements and do not establish DRAM bytes.

All MAIN B1/B2 sequences are exactly equal at both output lengths,and same-point repetitions are exact. This supports strict generated-token-sequence comparability for MAIN under the new contract. It does not relabel old logprob failures or prove model-quality equivalence to higher precision.

## B. Numerical behavior and source localization

The original allowance abs(delta)<=0.05+0.01*abs(reference) is unchanged. It remains FAIL for A00's first token,0.10269761085510254>0.0591057825088501. A01's original first-token difference0.0550459623336792 remains inside0.06280191779136658.

For every MAIN formal round,the output32 comparisons fail that old sampled-token threshold at A00 steps0,8,23 and A01 step22. All32 output tokens remain equal. MAIN repetitions have exactly identical selected logprobs across formal repeats. Across the output1 and32 comparisons there are25 old-gate same-token failures in330 sampled comparisons. They are reported as numerical sensitivity,not silently changed toPASS and not used to delete timings.

LP_NONE requests do not expose logprobs;their sensitivity field is UNOBSERVED,notPASS. LP_NONE sequences equal MAIN/LP20_CONTROL sequences.

The post-formal local observer issued only P4,P5,P6 and captured steps0,1,15,31:12 tensor files,16 actual request-rows. It was never installed during formal timing. All observed-step top20 dictionaries and full returned sequences exactly match corresponding uninstrumented MAIN records. The observer stores actual selected hidden states,raw full-vocabulary logits,actual batch/position metadata,sampler output,and a small selected subset of head weights in the owned private directory.

The actual runtime sampler is vllm.v1.worker.gpu.sample.sampler.Sampler,sourceSHA832c9945d201a1e730ff9b4b52076aa83bd4a5064e1e4cfea952cf84d4a8d1f0. It uses compute_topk_scores and the Triton top-k log-softmax path. The older generic v1.sample.sampler source discussed in historical evidence is not this runtime identity. SOURCE_PRECHECK and actual runtime receipts distinguish them without editing history.

Captured hidden states and logits are BF16;actual head/weight dtype is BF16,sampler mode raw_logprobs and needs_logits_processing is false. First-token prefill has512 scheduled tokens and selected hidden shape[1,2048] for B1,1024 scheduled tokens and[2,2048] for B2. Logits have shapes[1,151936] and[2,151936]. Later captured Decode steps schedule1 or2 tokens. This is direct diagnostic batch evidence,not inferred from a requested B2 label.

Before the head,A00 first-token hidden states differ by maximum1.0 and relativeL2 about1.728%;A01 differs by maximum3.0 and relativeL2 about5.712%. Raw sampler-input logits also differ. These facts locate an already-existing difference upstream of returned top20 normalization;they do not identify the first divergent layer or a particular BF16 kernel.

For A00,the selected raw logit is27.25 in both B1 andB2. CPU FP64 logsumexp changes by0.1026978614,which predicts the observed selected-logprob delta to about2.5e-7. For A01,the selected raw logit changes24.375to24.5,while logsumexp changes0.1800459838;their difference predicts -0.0550459838. Over all captured pairs,the returned B1/B2 top20 changes agree with full-logit CPU normalization to approximately1.1e-6. Absolute CPU FP32 normalization versus returned values has maximum3.10e-5;that error is far smaller than the original0.1027 difference.

Consequently,a pure top20-return/pairing or scalar normalizer arithmetic defect does not explain the measured discrepancy. Last hidden states and pre-normalization score vectors already differ. The0.125 pattern is compatible with the directly observed BF16 score representation;it is not proof that a specific BF16 kernel is the origin. Earlier attention/MLP/reduction choices and head rounding remain to be localized.

Selected CPU FP64 head-dot references use captured BF16 hidden states/weights as exact inputs. They are diagnostic mathematical references,not a GPU FP32-head performance or accuracy result. At some later steps,top20 boundary ties cause a returned token not to be in the separately captured CPU-topk weight subset;those head-dot fields are explicitly unavailable. Full-vocabulary logits and normalization comparisons still cover every returned top20 token.

The observer's internal request IDs contain the documented8-hex suffix,whereas RequestOutput returns the external ID. CPU analysis validates the official input/output processor mapping,unique IDs,returned prompt source and sampled token at every captured step. No raw ID was rewritten and no additional GPU replay was needed. OBSERVER_REQUEST_ID_BINDING.json preserves the source proof.

## C. Controlled strong-software experiments

Each pool contains six points with2 warmup rounds and5 formal samples/point. LP20_CONTROL/LP_NONE pairs alternate order within each point;APC reset/warm pairs likewise alternate. Each has its own raw identities and statistics.

| Configuration | deltaA00 ms | deltaA01 ms | deltaB2 ms | R |
|---|---:|---:|---:|---:|
| MAIN | 317.700108 | 317.762573 | 327.734924 | 1.031484 |
| LP20_CONTROL | 317.813332 | 317.778046 | 328.239906 | 1.032865 |
| LP_NONE | 313.495766 | 313.576344 | 323.767570 | 1.032633 |
| APC_COLD | 318.057419 | 317.652237 | 327.339775 | 1.029841 |
| APC_WARM | 318.121344 | 319.294182 | 330.085379 | 1.035699 |

**Logprobs.** The official logprobs=None path removes about4.2-4.5ms from the32-minus1 contrasts but leaves R near1.033. Paired output32 median savings are4.276ms(A00),4.236ms(A01),4.409ms(B2). This is an end-to-end optional-software bundle,including return/normalization/processing effects,not an isolated kernel cost. Several paired samples have negative savings due to retained latency outliers;all5 are included. Individual point MAD is small even where one outlier exists. No extra block was triggered because the pre-frozen criterion was MAD/median or formal compile/capture,not a posthoc best-sample criterion.

**Prefix cache.** APC_COLD means successful reset before each generate,not a promise of zero hits inside that generate. B1 reports0 cached tokens;B2 reports0 for A00 and16 for A01. The natural prompts share23 initial tokens;16-token reuse is consistent with within-call common-prefix block reuse after reset. No independent cache-event trace was collected. This is not mislabeled cross-round weight sharing.

APC_WARM resets,issues and preserves an untimed output1 prime for the same sources,then times the original point. All42 primer requests are excluded from formal statistics. Each timed request reports496 cached prompt tokens. Warm-cache first-token median savings are about23ms per B1 and55.5ms for B2;full32 savings are about21-23ms for B1 and52.5ms for B2. The32-minus1 contrasts change by roughly0-2.75ms,illustrating cancellation of much prefill cost under these controlled states. It does not make the difference a pure Decode kernel measure.

Warm caching changes A01's first token relative to reset cold;within APC_WARM,A01 B1/B2 output32 sequences diverge at generated position10. Full sequences,first divergence and common prefix are retained. APC_WARM timings are valid fixed-length native descriptive observations,but are not strict same-token semantic speedup measurements against cold or for A01 B1/B2. These data remain separate from MAIN and LP controls. No precision or threshold was changed to make them pass.

All five formal pools retain active compiled Qwen2Model,unchanged compilation/capture counters and31 fullgraph manager replays per output32 request. Output1 has no fullgraph replay;that does not imply eager fallback. Actual internal full-prefill shapes are independently captured only in the post-formal observer. No weak-backend substitution occurred.

SOFTWARE_EXCLUSION.md updates the live strong-software table. The original paper table is retained as INHERITED_SOFTWARE_EXCLUSION.md;its old 'not initialized' row is explicitly historical. Generic Batch weight reuse,Graph execution,logprob elision and prompt-cache reuse are existing software capabilities.

## D. Architectural interpretation and next falsifiable questions

The inherited conditional model assumes about191.313GB for31 extra dense BF16 weight passes. At rated716.8GB/s it gives266.899ms,or263.997ms with the historical64MiB L2 capacity credit assumptions. MAIN's measured mean single increment is317.731ms. Dividing assumed bytes by that interval gives602.123GB/s,84.0% of rated bandwidth.

That last number is **conditional model inversion**,not profiler-measured DRAM throughput or evidence of84% physical utilization. No actual DRAM byte count,achieved memory clock or independent memory-versus-compute axis was measured. R near1 is compatible with shared weight supply,but shared launch/control,GEMM shape/occupancy,Graph dispatch,scheduler and sampling costs can also yield near1. Strong software controls remove specific alternatives only in part.

The measured result supports a concrete remaining question about roughly318ms of31-step native incremental cost under compatible strong software. It does not by itself support a new compression/cache/scheduler hardware mechanism or PPA claim. NEXT_QUESTIONS.md specifies memory-versus-SM supply response,per-token Graph/control residual,earliest numerical divergence,and prefix-cache numerical contract tests. None is started here.

## E. Execution,resources and archive

V7 authority a43a44a49da80496547dc29c68a3030730fd9adb/treec707f1f18abe8f17fca03007d37b1074f91d8f01 is unchanged. V8 explicitly changes the scientific role of the old numerical gate;the prior FAILs and original science SHA remain historical authority. V8's contract and configuration differences are frozen separately. Twelve SHA-qualified assets retain exact inode/size/mtime/ctime;no new model hash stream,model/data download or dependency installation occurred.

One nonblocking common flock acquired /data/c16/locks/c16_gpu_campaign.lock. RTX4080 UUID GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59,live Image-Lab incarnation/code/profile,lock inode/kernel holder,own authenticated reservation,quiescence and child drain were checked. Completed Image-Lab scopes stayed33,inflight0 across112 resource snapshots. Unknown compute was never admitted.

The BASE engine took60.096s to initialize and PREFIX60.511s. They used independent V8 private cache/log roots and ran serially;prior CUDA context drainage was observed before the second owner. Held time250.766s is below1800. Available peaks:own NVML14314MiB,live-tree RSS subtotal4,247,216,128bytes,session charged-memory peak3,706,331,136bytes,conservative full-worktree disk210,795,368bytes. V7's narrow exit-race/censored rules and cgroup limitations are retained;no censored race or independent mandatory gap occurred in this interval. These are sampled RSS plus kernel charged-memory observations,not an exact continuous summedRSS guarantee or writable hard memory.max enforcement.

The condition is VERIFIED_GATED_RESIDENT_CO_RESIDENT_NATIVE_OBSERVATION. Desktop per-process utilization telemetry remains unavailable. The inherited monitor text says retainINCONCLUSIVE;under V8's explicit separated layers,this remains an attribution/exclusivity limitation rather than deletion of finite genuine request measurements. No claim of complete isolation or no interference follows from low MAD.

The final owner context cleared,the lock unlocked/closed,NVML client shut down and only the own reservation was removed. Post-release Image-Lab was IDLE,inflight0,queue[0,0],no reservation or kernel holder. The worker's NCCL process-exit warning is retained;actual CUDA context drainage was observed. No other project's process was signaled.

CPU testing:77 unit tests plus a real CPU tensor observer smoke and sharded-checkpoint smoke passed before GPU admission. The GPU execution sources still match their frozen hashes. Post-run CPU analysis resolved internal/external request-ID wrapping and partial weight-subset ties without changing raw data or executing GPU again.

The executed full resource receipt is losslessly archived in raw/RESOURCE_RECEIPT_EXECUTED.json.gz. RESOURCE_RECEIPT.json is an index with every non-sample field and exact uncompressed/archive SHA;decompression reproduces the actual1081511 bytes. Per-request raw shards and full private completion/tensor SHA indices preserve all evidence. No failure sample was hidden or removed.

No external Profiler/NCU/NSYS/NVBit,simulator or RTL was used. This Goal ends after Git publication,remote fetch-back commit/tree/blob verification and clean worktree. No next Goal,clock sweep,profiling or hardware-development task starts automatically.

Large NUMERIC_* comparison/repetition tables are likewise archived losslessly as raw/NUMERIC_*.json.gz;their named JSON files retain summary fields and exact archive SHA/byte metadata. Decompression recovers every original derived row. This transport packaging changes no raw request,number,FAIL or sample pool. pack_derived_evidence.py makes the post-analysis packaging reproducible.
