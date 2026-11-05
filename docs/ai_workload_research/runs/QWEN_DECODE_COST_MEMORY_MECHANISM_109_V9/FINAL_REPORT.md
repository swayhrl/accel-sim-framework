# V9: native Decode cost curve and partial GPU mechanism attribution

Scientific state: **native curve complete; timeline and B1 node counters retained; optional B2 profiling stopped by resource guard**.
Global bottleneck causality remains **not established**.

V9 completed18 native points with90 formal samples,36 native warmups,and no posthoc sample selection. It did not repeat V8's five-configuration matrix. Nsight Systems then completed four representative profiled requests. One B1 Decode-node counter report completed;B2 kernel replay crossed the16GiB charged-memory bound. GPU work stopped immediately and the numerical-boundary branch was not started.

A total143 generate calls returned193 real completions across native/warmup/profile roles. One B2 profiled call started but never returned;no completion,timing or counters were fabricated for it. Native data,profiled timing,hardware counters and model estimates remain separate.

## A. Output-length and Batch curve - OBSERVED

The same Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1,BF16/TP1/unquantized,strong VLLM_COMPILE/inductor/FULL_AND_PIECEWISE,FlashAttentionImpl and UnquantizedLinearMethod were used. Capacity remains544/1088/2. A00/A01 are the frozen natural512-token arrays. Prefix cache is off;logprobs=None is the official path.

Each table cell is CUDA-event median +/- unscaled MAD in milliseconds,using all5 formal observations. Full event/Host samples,drift,min/max and raw journals are delivered.

| Output N | A00 B1 ms | A01 B1 ms | A00+A01 B2 ms |
|---|---:|---:|---:|
| 1 | 35.5328 +/- 0.1812 | 35.4339 +/- 0.0065 | 69.0389 +/- 0.0348 |
| 2 | 45.5314 +/- 0.0382 | 45.5033 +/- 0.0103 | 79.6313 +/- 0.0874 |
| 4 | 65.9278 +/- 0.0199 | 65.8831 +/- 0.0771 | 100.6497 +/- 0.0507 |
| 8 | 106.2922 +/- 0.0728 | 106.4419 +/- 0.0123 | 142.2399 +/- 0.0480 |
| 16 | 187.4441 +/- 0.0532 | 187.1801 +/- 0.0869 | 225.8524 +/- 0.2222 |
| 32 | 349.4359 +/- 0.3031 | 349.2390 +/- 0.0345 | 392.9252 +/- 0.1219 |

Actual source mapping was independently rechecked from returned prompt IDs,not labels alone. B1/B2 sequences are exact for everyN;each shorter sequence is an exact prefix of its same-mode32-token sequence. N1/N32 outputs also match V8 LP_NONE references. Logprobs are **UNOBSERVED**,never numericalPASS.

Every N>1 request records exactlyN-1 fullgraph replays. Formal compiled model identity is active and no formal compile/capture counter changed. This verifies the real execution organization without treating a requested batch label as a kernel-shape measurement.

## B. Fixed and per-step costs - MODEL_CONSISTENT

Fit:T_mode(N)=a+(N-1)b. The table uses all formal observations in OLS;an independent point-median fit and every residual/adjacent slope are also retained.

| Mode | a ms | b ms/extra token | Paired-round bootstrap95% b | Max abs point-median residual ms |
|---|---:|---:|---:|---:|
| A00 | 35.48934 | 10.126004 | 10.118241 to 10.133768 | 0.0821 |
| A01 | 35.45993 | 10.124480 | 10.120636 to 10.129001 | 0.1318 |
| B2 | 69.20815 | 10.447678 | 10.443380 to 10.451977 | 0.1477 |

B2/mean-B1 slope ratio is1.0318447963,with a conditional paired-round bootstrap interval[1.0311910,1.0325907]. Bootstrap uses2000 prespecified seed0 resamples of complete formal rounds;n=5 and the interval is descriptive,not a causal confidence statement.

The measured adjacent slopes range9.999 to 10.198ms(A00),10.069 to 10.190ms(A01),10.398 to 10.592ms(B2). Point-median residuals stay below0.15ms overN1-32. Raw observation residuals include outliers up to1.466ms;none is discarded. The pre-frozen MAD/capture trigger did not request an extra block.

The intercepts separate roughly35.5ms single-request first-token cost from69.2ms dual-request first-token cost. Later steps are roughly10.125ms forB1 and10.448ms forB2. This reinforces V8's amortization over multiple output lengths instead of assuming that a single32-minus1 contrast is pure Decode.

These are full generate CUDA-event and Host measurements. They exclude initialization and between-call evidence persistence under the inherited timing definition. They are not pure kernel time or sustained HTTP-serving QPS. The fit is empirical in this model/context/N range;it is not extrapolated tolong contexts or larger batches.

## C. GPU timeline and node counters

### Nsight Systems - OBSERVED records; PARTIALLY_ATTRIBUTED cost regions

Installed Nsight Systems2024.6.2 collected CUDA/NVTX with node-level Graph trace,CPU sampling off and system GPU metrics off. Capture began only after engine initialization and two warmup rounds. Profiled calls were A00_N1,B2_N1,A00_N32,B2_N32.

**Compatibility limitation:**the tool reported that driver13.0 is unsupported by this build and used its12.8 tracing libraries. It also warned that not all CUDA/NVTX events might have been collected. The archive preserves those diagnostics. Therefore100% matching below refers only to collected records,not guaranteed whole-application completeness. The difference between generic CUPTI-produced and CUDA-collected event totals is not treated as a lost-kernel count.

All29436 collected kernel rows match collected CUDA runtime correlation IDs and an actual forward/sample NVTX phase. Four request ranges and62 fullgraph pushes were observed. Four extra forward markers are empty scheduler cleanup calls,not additional Decode computations. There are no unclassified collected kernel rows.

| Profiled point | CUDA-event ms | Collected GPU activity union ms | NVTX-window remainder ms | Prefill kernel union ms | Decode kernel union ms |
|---|---:|---:|---:|---:|---:|
| A00_N1 | 36.8004 | 33.9125 | 2.9627 | 33.8632 | 0.0000 |
| B2_N1 | 69.7163 | 67.5081 | 2.2604 | 67.4561 | 0.0000 |
| A00_N32 | 350.9453 | 348.0960 | 2.9004 | 33.9546 | 313.1316 |
| B2_N32 | 394.9817 | 391.8129 | 3.2229 | 67.5727 | 324.0914 |

The N32 profile/native event-time ratios are1.00432(B1) and1.00523(B2);these single-profile observations do not replace native formal medians. GPU busy time is an interval union,including overlap correctly. The remainder is time not covered by collected GPU activity;it may include CPU/control,untraced work and profiler overhead. Missing-event/driver-fallback uncertainty remains.

For B1 output32,dense GEMV groups contribute295.363ms out of313.132ms collected Decode kernel union. For B2,the WMMA/Tensorop GEMM group contributes301.495ms out of324.091ms. Thus about94.3%/93.0% of the observed Decode kernel region is in these dense groups. B1 has12836 Decode kernel rows;B2 has15068. The kernel family and organization change with Batch;this is not simply two identical GEMV streams.

CUDA Graph launch API durations sum6.929ms/31(B1) and8.270ms/31(B2),but overlap GPU execution. cudaEventSynchronize accounts for307.133ms and347.902ms of CPU API duration,largely waiting for concurrent GPU work. Adding these CPU durations to GPU kernel time would double count. The small roughly0.83%/0.82% uncovered N32 windows provide evidence against a dominant exposed no-GPU-activity interval in this trace;they do not bound every form of native control cost inside/overlapping kernels.

No cross-tool timestamp join is attempted. TIMELINE_ANALYSIS.json and the full selected activity-table archive preserve correlation/phase coverage,all kernel groups,step timing and warnings. Original .nsys-rep and .sqlite remain privately indexed and readable on109.

### Nsight Compute - OBSERVED B1 single-node events

The installed2025.1.1 tool successfully queried actual supported metric names and collected one filtered dense node inside the first A00_N32 Decode Graph. The explicit metric list covers duration,DRAM read/write,L2 read sectors,SM throughput,tensor-pipe active and active-warps occupancy. No full-metric-set collection was used.

Replay mode:kernel;Graph profiling:node;launch-count1;clock-control:none;cache-control:none;pipeline boost:dynamic. Actual tool output reports **7 passes**,above the preferred small-pass goal and fully disclosed.

Selected B1 GEMV observations,from base-unit CSV:

- DRAM reads10,505,728bytes;DRAM writes1,280bytes.
- Duration18,464ns;read-bytes/duration = 568.984GB/s **within this replayed node**,not full-application achieved bandwidth.
- L2 read sectors342,218;kept as sectors rather than silently relabeled bytes.
- SM throughput18.304659% of its stated sustained-elapsed metric.
- Tensor-pipe active0% for this node.
- Active-warps occupancy21.895085% under the metric's active-period denominator.

The10,485,760-byte packed-QKV weight model is close to this node's read count(ratio1.0019043). That is **MODEL_CONSISTENT**,not proof of matrix arguments or application-wide weight traffic. The actual kernel is a cuBLAS GEMV;its metadata/name,grid,block and every collected metric/unit are retained.

Crucially,the replay report says roughly14.714GB accessible/backed-up memory perpass,about103GB logicalsum across7passes. Those are **Profiler replay-backup metadata,not DRAM bytes for the model**. Kernel replay can disturb cache state despite cache-control:none. This one node cannot be multiplied by layer count and called the real whole-Decode traffic.

B2 collection reached its first WMMA kernel and warned that device memory was being backed up in system memory. The cgroup guard then fired before a complete counter report. B2 counters are RESOURCE_CENSORED,not zero and not a performance negative. There is no measured B1/B2 DRAM ratio.

## D. Competing explanations and unit-correct cost model

- **H_MEM - MODEL_CONSISTENT globally; partial node evidence.** Native per-step costs and near1 Batch slope ratio are compatible with shared weight supply. The selected B1 node has matrix-sized DRAM reads and low tensor activity. Whole-application DRAM bytes and a resource-response axis are still missing.
- **H_SM +/- unresolved globally.** Dense GPU kernels dominate the observed time and Batch changes GEMV to WMMA/GEMM organization. One B1 node's low SM/tensor metrics do not describe every kernel or the unmeasured B2 SM state.
- **H_CONTROL - PARTIALLY_ATTRIBUTED in the collected profile.** Exposed uncovered request intervals are small;Graph launch and CPU waiting overlap GPU execution. This does not imply zero control cost,or that all GPU bookkeeping lies outside the dense/other kernel regions.

An empirical native equation is T=a+(N-1)b. A trace decomposition is observed GPU-activity union plus its window remainder. Inside kernel activity,compute and memory overlap. They cannot be separated into additive elapsed terms from this evidence.

The inherited191.313GB/31-step model remains a conditional weight-streaming hypothesis. Inverting the native mean slope gives about609.5GB/s under that model;this is not a DRAM measurement. The only independently collected DRAM count is the single-node value above.

No global architectural claim is labeled CAUSALLY_SUPPORTED. SYNTHESIS.json assigns OBSERVED,MODEL_CONSISTENT orPARTIALLY_ATTRIBUTED per claim and lists remaining gaps.

## E. Numerical boundary branch and external validation

No new GPU boundary observation was executed:resource STOP occurred before the NUMERIC task. The V8 observation that hidden states and raw logits already differ before returned logprobs remains authoritative;the earliest native divergence layer is still unresolved.

The CPU source plan identifies embedding,decoder0/17/35 and final norm/head input as sparse last-query boundaries. Hidden and residual must be kept separately,and selected positions must bind to actual sampler row IDs. Compiled/PW/FULL replay bypasses Python hooks;an altered eager diagnostic would not establish where native first diverges. The planned altered path was explicitly labeled and was not silently substituted for native performance.

The most useful next questions are in NEXT_QUESTIONS.md:complete cost attribution without over-budget replay backup;whether independent memory versus SM supply changes the native slope;whether the dominant B1/B2 dense-family change matters beyond byte reuse;and a minimal independent accepted-model validation. No new model,data download,profiling window orGoal is started.

## F. Resources,engineering and archive - OBSERVED

The fixed V8 authority is b3e0adf450a563997717126fd1c1985e884855a3/tree304788b4233d429a154b528e5bb42e421062c9b8. V1-V8 raw,contracts and receipts remain unchanged. Inputs/model source were revalidated with12 unchanged SHA-qualified file fingerprints;no model download or dependency upgrade occurred.

One nonblocking shared flock acquisition succeeded. The actual RTX4080 UUID,Image-Lab loaded gate/process incarnation,common lock/reservation and quiescence were checked throughout. Profiler launcher PID and actual Python GPU PID were separately bound by nonce,birth,UID,executable,source SHA and own-tree ancestry. Each next GPU task required context drainage first. Image-Lab completed scopes stayed33,inflight0. Desktop per-process activity telemetry retains its known limitation;this is gated-resident shared observation,not a fully exclusive environment.

GPU held316.4546seconds. Sampled own NVML peak15146MiB stayed below15400. Live-tree RSS peak15.496GiB stayed below the16GiB sampled-RSS bound,but session charged-memory peak reached **19.343GiB**,exceeding the separate16GiB guard. Native,NSYS andNCU_B1 phase peaks were3.418,4.154 and14.992GiB respectively. The first over-limit sample was during NCU_B2;the controller stopped its own task without changing the limit or retryingGPU. Conservative new-disk peak352,887,738bytes stayed below3GiB.

The inherited raw status is NUMERIC_OR_RUNTIME_NO_GO with reason 'Session charged-memory peak exceeds16GiB';this is a **resource stop,not a model numerical FAIL**. The final observer also encountered an exited-PID /proc/exe read race. Its original receipt is retained byte-exact. Supplemental read-only process/NVML verification found all four actual workers absent and no own compute context remaining;no additional signals were needed. The lock and own reservation were released,Image-Lab returned IDLE withno own claim. That supplement does not pretend the original final observation was complete.

77 CPU tests and a real two-row sparse-boundary CPU tensor smoke passed before admission. Optional tool failure,resource failure and scientific gaps are separately represented. CUDA13/NSYS12.8 fallback,seven replay passes,B2 memory-backup failure and unexecuted numerical diagnostics are all preserved.

Raw journals and the full executed resource receipt use lossless gzip with exact SHA indices. The119117-name,78MB metric capability query is privately retained by exactSHA rather than duplicated as a hardware measurement. Public raw counter CSVs and selected full timeline activity tables preserve high-value measurement data;authoritative profiler binaries remain privately indexed. No synthetic sample or estimated application DRAM count was substituted.

No clock,power,persistence or system counter-permission setting was changed;no other project process was modified. No164,simulator orRTL was used. After Git publication and exact remote commit/tree/blob verification,this Goal ends. No V10 or hardware implementation starts automatically.
