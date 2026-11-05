# V11: dominant Decode memory mechanism convergence and opportunity screening

Final scientific state: **NO_HARDWARE_CANDIDATE_PROMOTED**.
Archive this Qwen subdirection as a validated load-analysis baseline. Prioritize higher-value, legally qualified AI workloads before more hardware-mechanism development. No V12 starts automatically.

V10 authority94cbc8197cc3a5ec22669a55e7ccfb1a3df16962/tree56c90b40360d9f7c555534f44411d2b1d5a28752 was fetched and verified. V1-V10 data/contracts/receipts remain read-only. No V8 five-configuration matrix,V9 native curve,V10 QKV measurement or Image-Lab infrastructure construction was repeated.

## 1. Dominant modules and selected native evidence

V9 remains the native latency authority: B1approximately10.125ms/extra token,B2approximately10.448ms,ratio1.0318448. CPU reconstruction places gate/up and down at78.13%/78.31%of B1/B2 Dense kernel time in the collected V9 trace. That trace retains the CUDA13-driver/CUPTI12.8 fallback and missing-event warning,so its shares and copy bounds do not guarantee whole-application trace completeness. Adding O-projection covers approximately83.6%of Dense time. Down accounts forapproximately0.13094ms of the observed0.19779ms B2 Dense increment per step.

V11 selected O/gate-up/down at layers0 and17 in B1(A00) and B2(A00+A01). Frozen512-token inputs,Qwen2.5-3B revision aa8e72537993ba99e69dfaafa59ed015b17504d1,BF16/TP1/no quantization,strong VLLM_COMPILE/inductor/FULL_AND_PIECEWISE,FlashAttentionImpl,UnquantizedLinearMethod,544/1088/2,prefix cache off and LP_NONE remain unchanged.

All12 targets returned actual one-pass measurements:

| Layer / module | B1 read bytes | B2 read bytes | B1 time us | B2 time us |
|---|---:|---:|---:|---:|
|0 O|8,389,760|8,390,656|18.208|18.048|
|0 gate/up|90,185,984|90,186,752|139.520|150.080|
|0 down|45,112,832|45,099,520|71.744|75.584|
|17 O|8,389,760|8,407,040|16.896|18.304|
|17 gate/up|90,185,472|90,186,240|138.880|148.736|
|17 down|45,092,864|45,100,288|71.584|75.744|

Corresponding BF16 weights are8,388,608/90,177,536/45,088,768bytes. Reads are within approximately0.22%of one logical payload across these nodes. B2 does not double the reads. Gate/up duration rises7.10-7.57%;down5.35-5.81%. O varies between-0.88%and+8.33%,with one observation per layer/mode;this is not a confidence interval.

EVIDENCE_MATRIX.tsv and DOMINANT_DENSE_COUNTERS.json retain every node,kernel,grid/block,logical M/K/N,SM-cycle-rate proxy,tensor activity,weight size and pairing grade. No selected node is multiplied by36 or called whole-application DRAM traffic.

## 2. Identity and actual profiling scope

A CPU replay caught a real selection trap before GPU execution: the old regex gemv|gemm|cutlass also matches72 Attention kernels through cutlass::bfloat16_t. The new native filter selects actual GEMV/Kernel2-GEMM function identities. Global matching-kernel skip1/count3 selects layer0 O/gate/down;skip69/count3 selects layer17. The only active profiling range is the first warmed Decode Graph. This avoids remeasuring QKV.

All targets match compiled source order,actual model module weight shapes,dtype,Graph descriptor and grid/block. B2 O/down share names and launch geometry,so order and the compiled K contract are essential. This is runtime-contract/source-order pairing,not a raw-kernel-argument pointer capture. Logical M1/M2 must not be confused with the WMMA tile shape. Unmatched launch contracts would have remained unpaired;all12 passed this check.

An initial small DOWN pilot verified four metrics in one pass: actual DRAM reads,duration,SM elapsed-cycle average and tensor-pipe active percentage. Every result row was independently audited;the former first-row-only audit was replaced. Both native layers and all local rows were one pass. Backup statistics were not emitted and remain null;actual one-pass logs plus the installed guide's no-save/restore rule justify the interpretation,not a fabricated backup0.

NCU2025.1.1 used Graph node/kernel replay,clock-control none,cache-control none and no full set. Each native target block had a fresh serial engine,twoN32 warmups and one profiled request. Profiled node duration and full-generate event times do not enter the V9 native formal pool. NCU isolation/serialization and shared-desktop limits remain.

B1 nodes report tensor activity0;B2approximately3.39-4.44%for these nodes. This deprecated but supported metric is only the specified tensor-pipe activity fraction,not proof of SM/tensor throughput saturation. SM cycles divided by duration is an elapsed-cycle-rate proxy,not independent physical-clock telemetry or fixed-frequency proof. No clocks,power or permissions changed.

## 3. Measured local data-state controls

Independent synthetic BF16 F.linear DOWN proxies use the actual K11008/N2048 dimensions,B1/B2 and the corresponding observed kernel name/launch organization. Within each process,the same W/X,CUDA Graph,FLOP count and exact output bits are held fixed. Five interleaved paired rounds retain all observations. These are not real model tensors or application-performance measurements;B1/B2 local random tensor streams are not claimed to be identical across processes.

Initial preconditions were two weight reuses versus a512MiB write/add buffer. A final bounded refinement used a read-only512MiB sum and added actual DRAM-write counters. Preconditioning time is outside the target-node counters.

Read-only refinement medians:

| Local mode / state | Read bytes | Time us |
|---|---:|---:|
|B1 REUSE|45,092,352|70.688|
|B1 READ_EVICT|45,117,568|70.560|
|B2 REUSE|384|48.896|
|B2 READ_EVICT|45,143,552|76.832|

All target write counters in the refinement are small(max92,544bytes,approximately0.21%of the weight);most are0 as genuinely returned counters. The B2 contrast passes the frozen actual-read criteria,with the same function/grid/block and exact output bits;latency ratio1.571335. This partially attributes local latency to data state. It does not isolate every memory-system state,measure physical clocks,or prove full-native Decode is DRAM-bound. On-chip reads still cost time;REUSE is not a compute-only baseline.

B1 fails the reuse-read criterion:even repeated use reads the full45MB. That negative result is retained. The earlier write-buffer controls showed approximately1.357x/2.160x B1/B2 time ratios,whereas the read-only controls show0.998x/1.571x. Thus the larger write-precondition delay cannot be assigned solely to extra read bytes. Writeback/bank/power/history are possible coupled states;the original write counters were not measured and are never backfilled.

Completed local reports also allowed CPU-only SASS inspection. B1 includes LDG.E.EF.U16 and LDG.E.U16.STRONG.SM;B2 includes LDG.E.LTC128B.128. Each first REUSE/EVICT pair has identical normalized SASS. These are instruction-string observations. Weight-pointer mapping and modifier semantics are not established,so no eviction-policy root cause is claimed.

## 4. Strong-software and copy checks

A single isolated process set the official preferred_blas_library hint from Cublas to Cublaslt before compilation/Graph capture. All three selected layer0 B1 kernels,grid and block remained unchanged. Result:NO_OBSERVED_PATH_EFFECT. The pre-frozen rule therefore skipped B2,formal performance and further local backend sweeps. This is not proof that baseline already uses a particular cuBLASLt API,or that all compatible software kernels are exhausted. All32 output tokens still match the reference;logprobs were not observed.

No production vLLM,Image-Lab or third-party library was edited. The process preference is not a system GPU setting. No end-to-end software speedup is claimed.

The72 attention-adjacent copies remain tied to cache-update/splitKV and splitKV-combine/O-projection. Actual source/destination pointers,strides and internal FA2 transform are unavailable. Installed Torch/vLLM use a default Graph capture that does not retain the queryable graph object;the formal introspection path would change capture retention or requires unavailable support. Shape profiling can itself retain tensors or add copies. An unsafe deletion would not be a valid counterfactual.

Consequently exact copy necessity/removability remains UNRESOLVED. The same-profile ideal request-time ceiling0.809538%for the collected copies from V10 is retained;it is not an observed speedup and inherits that trace-coverage limitation. Close this copy-specific hardware direction for the present Qwen scope,without claiming the copies are universally necessary.

## 5. Competing mechanisms and opportunity ranking

H_MEM is MODEL_CONSISTENT on the dominant selected modules:nearly one weight payload is read,larger batches reuse that payload,and the measured local B2 data-state contrast affects latency. The conditional6.171GB/step or191.313GB/31-step model remains an assumption,not actual whole-application traffic.

H_SM remains INCONCLUSIVE as a global limiting resource. B1/B2 use different organization;near-equal bytes take different time,while Tensor activity and cycle-rate proxies cannot independently separate SM supply from memory behavior. Early/middle-layer agreement improves coverage,not causality.

H_SW has two concrete limits:the tested backend hint did not change selected kernels,and copy semantics lack a responsible minimal patch. Necessary weight streaming,ordinary batching and strong library dispatch are already present. No observed large redundant DRAM payload suggests a simple deduplication hardware opportunity.

Unpromoted directions,with full problem/variable/falsifier/cost cards in HARDWARE_OPPORTUNITY_RANKING.json:

1. Weight-service bandwidth/latency:could help only if a true native supply-response axis supports it. PHY,packaging,pins,power,interconnect and timing costs are unknown;more bandwidth is not itself a novel mechanism.
2. Cache capacity/policy:local B1/B2 reuse differs,but the native whole-model reuse interval is far larger than nominal L2 under the inherited capacity model. Large retention storage has area,leakage,latency and KV/activation-pollution costs;no native removable traffic is proven.
3. Low-M dispatch/packing:software-first until a specific compatible kernel improvement and native gain are demonstrated. Extra datapath/register/control complexity has no PPA evidence.
4. Attention copy hardware:deprioritized/closed here due the tiny ideal application bound and missing transform identity.

No global claim reaches CAUSALLY_SUPPORTED. The measured evidence does not justify a new compute unit or cache design. FOLLOWUP_APPROVAL_PLAN.md records what an independently controlled memory/SM supply experiment would require,including unsupported-control checks,owner approval,exact saved-state restoration and watchdog/read-back. No setter is run.

## 6. Independent workload and numerical limits

NOT_AVAILABLE for a qualified independent Dense decoder. The bounded accepted assets contain Qwen BF16 and same-lineage AWQ,not an independent accepted workload with verified natural inputs. C16's historical Llama training/reference evidence is not such a Decode candidate;164 was not accessed. No download was made.

CPU source review maps V8 native endpoint observations and V10 altered-eager sparse boundaries semantically,but cannot establish equal fusion,kernels,reduction order or earliest native divergence. No new large tensor dump was made. V11 independently checks15 real generate calls/21 completions against actual returned prompt IDs,source mapping,hashes,32-token lengths,fullgraph count31 and V9 token references. LP_NONE is UNOBSERVED numerically,not an old numerical PASS;historical FAILs remain unchanged.

## 7. Resources and archive

Three successful nonblocking shared-flock windows ran serially,with a maximum of one GPU owner and no failed-acquire retry. Main work held309.8088s,software71.4637s,read-only refinement12.3913s,total393.6638s(<1800). Each window rechecked GPU UUID,Image-Lab loaded gate/instance,reservation,quiescence,lock inode and other GPU processes.

Observed maxima across supervised windows:own NVML14,374MiB,sampled live RSS5,413,617,664bytes,session charged-memory4,098,990,080bytes,conservative worktree disk334,935,610bytes. All were below their frozen caps. Reported CPU helper HWM/read bounds are separately retained;short unobserved process peaks are censored and not0. No complete combined Goal-wide kernel RSS peak is claimed. Desktop per-process activity telemetry retains its inherited gap:these are gated-resident shared observations,not fully exclusive GPU measurements.

All windows ended normally with no monitor gap,own contexts cleared and lock/reservation released. Nonfatal skip-tokenizer chat-template warmup warnings remain in exact logs;the accepted direct token-ID generate path is independently validated. Final cleanup supplement verifies all11 actual workers absent and no own NVML compute context. No further GPU task follows the read-only refinement.

93 CPU tests passed before admission,including multi-row pass/finite-value audits and the narrow filter. Two inherited static test expectations were adapted before freeze and their initial log is preserved. All executed source sets are SHA-frozen;post-run CPU analysis is separately identified.

No downloads,installs,driver/profiler-permission changes,global clocks/power changes,164,simulator/RTL or interference with other projects. Large raw journals/resource snapshots are exact lossless archives;original NCU reports and token data remain privately indexed. Shared old raw is referenced by SHA rather than duplicated. Git publication verifies commit/tree/every file blob and clean worktree before STOP.
