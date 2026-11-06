# 近期论文与强软件排除 V1

本轮我方新增GPU／模型实验为0。以下“作者结果”只表示原文对应实验组；我们的归纳单列，不把作者加速比、模拟器或PPA估计写成109测量。没有复制整篇论文，详细字段／定位／PDF SHA见本目录evidence，原PDF仅私存用于审计。

## 使用规则

- 按论文版本×模型/输入×硬件×变量×计时/质量边界区分实验，不把同一论文多个图当独立复现。
- AUTHOR_REAL_GPU、AUTHOR_SYNTHETIC_GPU、AUTHOR_SIMULATION、AUTHOR_ESTIMATE与我方HISTORICAL_NATIVE分别标记。
- 软件“能做”不是当前已启用。语义有变化的优化只是创新碰撞，不能无条件作为same-contract性能基线。
- 原文未披露revision、数据SHA、GPU数量、precision、质量阈值或完整资源账时保留UNKNOWN，不补造。
- GSArch全文未能从核查的primary入口取得，只有正式出版／摘要。它的具体模拟、RTL／silicon、场景和PPA方法均保持SOURCE_INCOMPLETE；不借第三方转存补成已核事实。

## 3DGS：逐实验组


### GS_SCALE: GS-Scale: Unlocking Large-Scale 3D Gaussian Splatting Training via Host Offloading

Primary: [https://99dhl.github.io/assets/pdf/asplos26_gsscale.pdf](https://99dhl.github.io/assets/pdf/asplos26_gsscale.pdf), [https://arxiv.org/abs/2509.15645v1](https://arxiv.org/abs/2509.15645v1)

Version: Author final PDF; distinct from arXiv2509.15645v1 dated2025-09-19

Evidence: AUTHOR_NATIVE_SOFTWARE_MEASUREMENTS_NOT_OUR_MEASUREMENTS

Hardware/workload: Table 1/p8, section 5.1/p9: i7-13620H/4070 Mobile 8GB/32GB host; i9-13900K/4080 Super 16GB/64GB host; dual Xeon 6530/H100 PCIe 80GB/1TB host. PyTorch 2.2/CUDA 12.4/gsplat 1.5. Table 2/p9: Mill19 Rubble/Building 1152x864; GauU LFLS/SZIIT/SZTU 1600x1064; MatrixCity Aerial 1600x900. Batch 1; densification adjusted; mem_limit 0.3.

| Group / locator | Controlled author experiment | Author finding / limit |
|---|---|---|
| GS_SCALE_1 / sections 5.2-5.4/Figs 11-12,p9-10 | Offload/forwarding/deferred-update variants; small/full scenes; laptop/desktop | Peak-memory geomean 3.98x reduction. Versus GPU-only throughput 1.22x/0.84x, excluding OOM; versus naive 4.47x/4.57x. |
| GS_SCALE_2 / section 5.5/Tables 3-4,p10 | Original/deferred optimizer; epsilon/beta2 | Quality evaluated; epsilon term is approximated, not bitwise-equivalent Adam. |
| GS_SCALE_3 / section 5.6/Fig 13,p10-11 | Gaussian scale | 4070 Mobile: 4M -> 18M Gaussians; 4080 Super: 9M -> 40M Gaussians. |
| GS_SCALE_4 / sections 5.7-5.8/Fig 14/Table 5,p11 | H100 testbed; GCP Aerial singleL4 vs2/4L4 Grendel | SingleL4 7.05h;2L4 4.46h;4L4 2.46h. Cost advantage is not faster wall-clock. |
| GS_SCALE_5 / section 5.9/Figs 15-16,p11-12 | mem_limit;resolution;GPU;CPU memory channels | Explicit memory-capacity/throughput tradeoff and NUMA sensitivity. |
| GS_SCALE_6 / section 5.10/Table 6/Fig 17,p12-13 | CityGaussian;pruning/compression | Different quality/memory operating points; not a pure hardware-control study. |

Our inference: Already absorbs host culling bottleneck via GPU geometry, CPU-optimizer overlap and zero-gradient memory suppression. OpenMP extension exists (section 5.1); exact OMP thread/affinity setting is not specified in reviewed methods.

Limits: No our speedup; no residual CPU stall after fully qualified local replication. No permission to label optimization mathematically identical: deferred update drops epsilon.

### CLM: CLM: Removing the GPU Memory Barrier for 3D Gaussian Splatting

Primary: [https://cs.nyu.edu/~apanda/assets/papers/asplos26-cvm.pdf](https://cs.nyu.edu/~apanda/assets/papers/asplos26-cvm.pdf), [https://github.com/MachineLearningSystem/25ASPLOS-CLM-GS](https://github.com/MachineLearningSystem/25ASPLOS-CLM-GS)

Version: 17-page author final PDF; project repository title adds CPU Offloading, paper title does not

Evidence: AUTHOR_NATIVE_SOFTWARE_MEASUREMENTS_NOT_OUR_MEASUREMENTS

Hardware/workload: Section 6.1/p7: 5955WX 16 cores/128GB/4090 24GB/PCIe 4; E5-2660v3 listed 20 cores/256GB/2080 Ti 11GB/PCIe 3. Grendel single-GPU with gsplat CUDA. Table3/p8:Bicycle200images4K BS4;Rubble1600/4K BS8;Alameda1700/2K BS8;Ithaca8200/1K BS16;BigCity60000/1080p BS64.

| Group / locator | Controlled author experiment | Author finding / limit |
|---|---|---|
| CLM_1 / section 6.2/Figs 8-10,p8-9 | Maximum trainable scale and model-state memory | Up to 6.1x enhanced-baseline capacity; BigCity 102.2M Gaussians; 500k-step quality scaling. |
| CLM_2 / section 6.3/Figs 11-13,p10-11 | Naive,enhancedGPU-only,CLM throughput and exposed components | Throughput 86-97% of enhanced GPU baseline on 2080 Ti, 55-90% on 4090; 1.38-1.92x naive offloading. Pipeline intervals include overlapping compute+communication. |
| CLM_3 / section 6.3/Fig 14/Tables 4-5,p11-12 | NoCache,Random,Camera,GaussianCount,TSP ordering | TSP minimizes communication;GaussianCount usually minimizes Adam tail. Faster transfer can increase visible optimizer tail; tail alone is not end-to-end benefit. |
| CLM_4 / section 6.4/Table 6/Fig 15,p12-13 | Pinned memory;SMsActive distribution | Pinned memory up to37.8GB on4090,17.5GB on2080Ti. SMsActive sampled10kHz over>100batches. |
| CLM_5 / Appendix A.4/Table 7,p16-17 | CPU scheduling andGPU/PCIe bandwidth utilization | CPU core occupancy from SCHED_EVENTS; bandwidth metrics10kHz. This is not a complete OMP/affinity-control experiment. |

Our inference: Already includes camera/visibility reuse, reduced SH/appearance transfer, optimizer overlap, working-set selective loading and scheduling. Q1 cannot claim these broad mechanisms new.

Limits: Paper says batch-internal reordering preserves mathematical gradient update; FP sum order still needs a local numerical contract. CPU thread count/affinity and local physical-vs-logical core mapping remain replication questions.

### TIDEGS: TideGS: Scalable Training of Over One Billion 3D Gaussian Splatting Primitives via Out-of-Core Optimization

Primary: [https://arxiv.org/abs/2605.20150v2](https://arxiv.org/abs/2605.20150v2), [https://arxiv.org/pdf/2605.20150v2](https://arxiv.org/pdf/2605.20150v2)

Version: arXiv2605.20150v2,2026-05-26;18-page downloadedPDF

Evidence: AUTHOR_NATIVE_SOFTWARE_MEASUREMENTS_NOT_OUR_MEASUREMENTS

Hardware/workload: Section 4.1/p6: A5000 24GB, EPYC 7532 32 cores, 256GB DDR4, PM9A3 SSD measured 3.3GB/s, PyTorch 2.6/CUDA 12.4. Appendix adds 3090/A800. MipNeRF360 BS4/30kiterations;MatrixCity BigCity/AerialRGB-D51623trainingimages,fixed25M/102M/1.1B initializations,no densification/pruning for scale test. Default throughputBS64/16GB CPUcache;conservativeBS16/32GB.

| Group / locator | Controlled author experiment | Author finding / limit |
|---|---|---|
| TIDEGS_1 / section 4.2/Table 1,p7 | 24GB scalability frontier | Native~11.5M measured;naive~50M partly extrapolated from25M/12.13GB,not all measured maximum;CLM~105M;Tide>1B. |
| TIDEGS_2 / Tables 2-3,p8 | In-memoryNative/naive/CLM/Tide shuffle/trajectory | 253.5/305.3/304.3/309.1/285.8ms. Native remains faster;utilization is nvidia-smi1Hz,not CLM10kHz SMsActive. |
| TIDEGS_3 / Table 4/Fig 4,p8-9 | MatrixCity102M/1.1B | 102M:CLM100.8ms,0.41GB/iter;Tide90.7ms,0.10GB/iter.1.1B:Tide525.6ms,0.97GB/iter;CLMOOM. |
| TIDEGS_4 / Tables 5-6,p9 | NoTide/noOverlap/noMorton,102M,1080p,500iters | Full90.7ms;noDifferential145.3;noOverlap210.5;noMorton115.8. Author ablation, not our causal result. |
| TIDEGS_5 / Appendices A.2-A.3/Table 7/Figs 5-7,p14-16 | Shuffle/trajectory;bicycle/bonsai fixed initialization vsdensification | Order changes latency andquality;not purely same optimization trajectory. |
| TIDEGS_6 / Appendices A.4-A.5/Tables 8-10/Figs 8-9,p16-18 | 3090/A800;optimizer churn;single-vs4GPU capacity/cost/convergence | Additional measured hardware;resident Adam cold-restart0.6/0.9%updates at102M/1.1B. Cost operating point not universal superiority. |

Our inference: Trajectory reuse, incremental cross-tier transfers, overlap and budgeted working sets directly preempt broad Q1 cache/prefetch/hide-wait novelty.

Limits: Section 3.5/p6 discards optimizer moments on eviction and cold-restarts admission; trajectory replaces random order. Current repo README says release Torch 2.4+cu124, paper 2.6. Repo BS16/32GB default differs from default paper throughput BS64/16GB; do not silently mix.

### GSARCH: GSArch: Breaking Memory Barriers in 3D Gaussian Splatting Training via Architectural Support

Primary: [https://ieeexplore.ieee.org/document/10946749/](https://ieeexplore.ieee.org/document/10946749/), [https://hpca-conf.org/2025/main-program/](https://hpca-conf.org/2025/main-program/)

Version: IEEE DOI10.1109/HPCA61900.2025.00037,record10946749

Evidence: PRIMARY_PUBLISHER_ABSTRACT_ONLY_FULLTEXT_SOURCE_INCOMPLETE

Hardware/workload: Baseline GPU names only frompublisherabstract;actualproposedhardwaremeasurementNOT_ESTABLISHED NOT_ESTABLISHED

| Group / locator | Controlled author experiment | Author finding / limit |
|---|---|---|
| GSARCH_1 / IEEE abstract | A100/JetsonAGXXavier comparisons | Author maxima 6.49x/15.42x; not our measurements. Fulltext was not accessible through primary URLs, so simulator/RTL/silicon methodology, scenes, figures/tables and PPA not verified. |

Our inference: Training backward reuse/atomic-gradient/bank-conflict hardware design is prior art. This differs from host optimizer/CPU-GPU exposed wait;cannot transfer its speedup denominator to Q1.

Limits: Do not call speedups silicon measurements or establish simulation details from third-party reproductions. Secondary Scribd/search snippets were excluded as evidence.

## Long-context and MoE: actual experimental groups

### STRATA_OSDI26: Strata: Hierarchical Context Caching for Long Context Language Model Serving

Primary: [paper](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf), [official/version page](https://www.usenix.org/conference/osdi26/presentation/xie-zhiqiang)

Version: OSDI 2026; official proceedings pp.1-16; Use OSDI final. arXiv2508.18572v1 is 2025 preprint; its abstract describes a TTFT5x claim while final abstract reports throughput. Do not mix.

Model/input: Llama3.1-8B/70B-Instruct; Qwen2.5-14B-Instruct-1M. LooGLE-Wikipedia/NarrativeQA/ReviewMT/ShareGPT; Poisson arrivals, concurrency cap128.

Precision: NOT_EXPLICITLY_PINNED_IN_REVIEWED_METHODS

| Group / locator | Evidence / hardware | Control / baseline | Author result / measured scope |
|---|---|---|---|
| S_E2E / sec5.1-5.2; PDFpp9-11, Fig8-10 | AUTHOR_REAL_GPU; H200:8GPU platform/1.6TB CPU RAM; models8B/14B use1GPU,70B TP4. H20-storage and GH200 separate. | Engine/cache policy; baselines vLLM0.8.5+LMCache0.2.1,TRT-LLM0.17,SGLang0.4.5-HiCache. | Llama70B LooGLE: up to5x vs vLLM-LMCache,3.75x vs TRT-HiCache at equal TTFT. Serving throughput/TTFT; warm hierarchy separately precomputed; not pure decode. |
| S_IO_ABLATION / sec4.2/5.3; PDFpp6,11-13 | AUTHOR_REAL_GPU_PLUS_SEPARATELY_LABELED_SIMULATION; H200 transfer/compute co-run; H20+P5510 disk. Cache-distance study uses simulated arrivals/execution. | Copy layout/pages, IO-only vs scheduling, transfer-block quota,cache distance/disk layout. | 2x1024-thread blocks:48GB/s, <5% prefill/<10% decode interference. Kernel resources matter; cache-distance simulation is not a realGPU performance run. |
| S_GH200 / sec5.3/Fig14-15; PDFp13 | AUTHOR_REAL_GPU_WITH_ORACLE_ESTIMATE; GH200 H100+Grace vs H200 PCIe5; Llama8B/LooGLE. | Standard DMA vs StrataIO; scheduler; infinite-bandwidth oracle. | Sustained StrataIO ~40.3GB/s PCIe,150.5GB/s GH; scheduling still necessary. Oracle is estimate; faster link alone does not establish useful app speedup. |

Our inference: Direct collision: KV placement/migration/layout and overlap already strong software. Residual must survive current HiCache, batchedDMA and IO-kernel interference controls. Indirect only: KV tiering is not expert routing/weight residency.

Missing: No model revision or frozen input-byte SHA.; No authors' GPU-hours/complete benchmark resource receipt.

### HYBRIDKV_ACL26: HybridKV: Hybrid KV Cache Compression for Efficient Multimodal Large Language Model Inference

Primary: [paper](https://aclanthology.org/2026.acl-long.594.pdf), [official/version page](https://aclanthology.org/2026.acl-long.594/)

Version: ACL2026 long.594; pp13018-13034; ACL final read via web. Final PDF SSH fetch timeout; SHA pins arXivv1 only. Do not confuse with AdaptFM2026 same-name head-reconstruction paper.

Model/input: Qwen2.5-VL3B/7B,LLaVA-OneVision7B;8image+3video tasks;64frames/video.

Precision: NOT_EXPLICITLY_PINNED; pruning/retrieval changes attention contents, not bit-exact full cache.

| Group / locator | Evidence / hardware | Control / baseline | Author result / measured scope |
|---|---|---|---|
| H_QUALITY / sec4.1/Tables1-2; ACLpdfpp6-7; pinnedarxivpp6-7 | AUTHOR_REAL_GPU; NVIDIA L40S;count not stated. | 10%KV vs fullcache,SnapKV,LOOK-M,MadaKV,SparseMM. | Quality mostly maintained; not exact output equivalence. Multimodal task scores; not dense text decode contract. |
| H_EFFICIENCY / sec4.2/Table3; pinnedarxivpp6-7; finalwebTable3 | AUTHOR_REAL_GPU; L40S+FlashAttention;QwenVL7B,20random VideoChatGPT entries,max128output. | Full/20%/10%cache. | KVGB1.73/.40/.22;ms/token58.94/42.08/38.65;quality2.93/2.88/2.85. 7.9xKV reduction/1.52xdecode;20sample selectionSHA not supplied. |
| H_ABLATION / sec4.3-4.4/Tables4-5; pinnedarxivpp7-8 | AUTHOR_REAL_GPU; SameL40S;WebQA/VATEX,STD/NextQA. | Budgets5%-40%;all-static/all-dynamic;remove head/head-type allocation. | All-static34.13 vs hybrid38.65 vs all-dynamic48.15ms/token;quality differs. Shows retrievalIO vs quality tradeoff; no full-software end-to-end residual proof. |

Our inference: Direct capacity/migration collision, but lossy semantic change needs a separate quality contract. Compare retained-KV residency,CPU traffic,index cost,not advertised memory ratio alone. No expert-routing claim.

Missing: Model/data revisions, byteSHA, GPU count/hours not disclosed in reviewed sections.; No verified author implementation snapshot.

### MONOMOE_V1: MonoMoE: An Efficient Fused Mega-kernel for Quantized MoE Decoding

Primary: [paper](https://arxiv.org/pdf/2609.04244v1), [official/version page](https://arxiv.org/abs/2609.04244)

Version: arXiv2609.04244v1; submission metadata19Aug2026; no conference acceptance established; Paper claims FlashInfer integration; linked directory fetch restricted and guessed README404; do not assert installed implementation availability.

Model/input: Qwen3.5-35B-A3B/122B-A10B TP1;DeepSeekV3.1/GLM5.2 TP8;256experts/top8.

Precision: E4M3FP8 W/A;W128x128scales,A128element scales;BF16 inputs quantized internally.

| Group / locator | Evidence / hardware | Control / baseline | Author result / measured scope |
|---|---|---|---|
| M_SYNTHETIC / sec4.1-4.3/Table2/Fig8; PDFpp10-11 | AUTHOR_REAL_GPU_SYNTHETIC; H200141GB,132SM,4.8TB/s;20warmup+200graph replays. | Generated weights/inputs/routerlogits;B1/2/4/8;tunedvLLMTrition;FlashMoEFP8adaptation. | Up to1.54x vs tunedvLLM. Complete local operator;FlashMoE dispatch/combine disabled here;not natural-routing data. |
| M_E2E / sec4.4/Fig9; PDFpp11-12 | AUTHOR_REAL_GPU_NATURAL_TEXT; H200TP1/8;vLLM CUDAgraphs. | Sonnet50prompts,1600in/200out,200prefix;APCoff,chunkedprefillon;concurrency1/2/4/8. | Qwen35B TPOT reduction18.7/13.0/12.3/9.9% vs tunedvLLM. Natural workload;communication dilutes TP8gains;not DRAM causal partition. |
| M_ACCURACY / sec4.5/Table3; PDFp12 | AUTHOR_REAL_GPU_TASK_QUALITY; Same modelset,B1. | GSM8K5shot/HumanEval0shot;FP32same-operator synthetic validation separate. | Reported score differences within combined SE when lower. Statistical task accuracy,not token/logprob or BF16bitwise equivalence. |

Our inference: On-device expert streaming,not CPU capacity tiering. Strong direct collision: lowtokenMoE fusion/padding/bandwidth recovery already software. Residual needs natural routing under compatible precision and backend; synthetic microbench cannot replace it.

Missing: Model revisions/checkpointSHA/runtime commit not established.; Official code snapshot not independently verified.

### PATTERNS_ISCA26: Patterns behind Chaos: Forecasting Data Movement for Efficient Large-Scale MoE LLM Inference

Primary: [paper](https://arxiv.org/pdf/2510.05497v5), [official/version page](https://ieeexplore.ieee.org/document/11617553/)

Version: ISCA2026; DOI10.1109/ISCA66397.2026.00021;author preprintv5 12May2026; v3 Orders in Chaos is superseded. ArtifactREADME currently names DeepSeekR1AWQ/KimiK2Thinking vs paperV3/KimiK2: identity drift,not silently equivalent.

Model/input: DeepSeekV3 671B,Llama4Maverick402B,Qwen3-235B,KimiK2 1T;>24000requests;MMLU/Pro/ChineseSimpleQA/LiveCodeBench.

Precision: Simulator H100like FP16compute model;actual trace-source precision varies/unpinned;realGPU checkpoint precision not explicitly fixed here.

| Group / locator | Evidence / hardware | Control / baseline | Author result / measured scope |
|---|---|---|---|
| P_ROUTING / secIII/V-A; PDFpp3-6,9-10 | AUTHOR_REAL_GPU_ROUTING_COLLECTION; SGLang,8H100DGX+8H200AWS. | Layers,tokens,prefill/decode,tasks,languages,expertpairs. | Reports temporal/spatial correlations across4models. Trace characterization,not universal caching speedup;datasetorder matters. |
| P_SIM_PPA / secIV-V/Fig12/TableI-II; PDFpp7-12 | AUTHOR_EVENT_DRIVEN_SIMULATION_AND_PPA_ESTIMATE; 24/25H100like dies;Dojo/TSMCtopologies;Yosys+CACTI5nm. | Baseline/EP/allocation/predictor/combined. | Mean6.6x MoE throughput;area/power~0.04% estimated. Not measured waferGPU/PPA;local validation<5% does not validate everyfutureinteraction. |
| P_REAL_PLACEMENT / secVI/Fig17; PDFpp12-13 | AUTHOR_REAL_GPU; Qwen235B,8H100NVLink;SGLang+DeepEPdynamic. | MMLU/GlobalMMLU,B64..16384;contiguous/default vs Remap/Dup;oracleBest/Worst separate. | Remap15.5%,Dup12.5% improvement;abstract max1.25x. Three expertlinears only;excludesattention/alltoall/topk;not fullrequest;Dup adds1slot/GPU. |

Our inference: Expert replication/migration already contains capacity-vs-traffic tradeoff;predictor bookkeeping and replication must be charged. Direct collision for prefill-derived natural expert heatmaps. Need post-strong-placement residual,not generichotexpertcache. Results are multiGPU/wafer scoped.

Missing: Model/tokenizer revisions and request-byteSHA not supplied in paper.; MutableAE trace names differ;repositoryclaim cycle-accurate conflicts with paper event-driven;paper classification retained.

### NOTALL_ICLR26: Not All Models Suit Expert Offloading: On Local Routing Consistency of Mixture-of-Expert Models

Primary: [paper](https://arxiv.org/pdf/2505.16056v4), [official/version page](https://openreview.net/forum?id=2XMAUP74ig)

Version: ICLR2026; arXiv2505.16056v4 28Feb2026;official repo citesOpenReview2XMAUP74ig; OpenReview forum browserchallenge;published ICLR header and authorrepo provide venue confirmation.

Model/input: 20baseMoEs3B-57B inclOLMoE,Qwen3-30BA3B,Mixtral;22528inputs,512tokens,11domains.

Precision: GPUtype/count/precision/hours not explicit in reviewed paper methods;do not invent.

| Group / locator | Evidence / hardware | Control / baseline | Author result / measured scope |
|---|---|---|---|
| N_REAL_ROUTES / sec3-5/AppendixD1,D3; PDFpp5-10,16-18 | AUTHOR_MODEL_ROUTING_OBSERVATION; NOT_DISCLOSED | 7RedPajama+4applicationdomains;segments4/16/64/256;models/base-vs-posttrained. | Model-dependentlocality;~2xactiveexpertcacheoftenknee. Routing statistic,not actual offloading TPOTorDRAMbytes. |
| N_TOY / sec3.1/3.3/AppendixD2; PDFpp5-8,17 | AUTHOR_TRAINED_CONTROLLED_MODELS; NOT_DISCLOSED;20Btokens/10000steps. | OLMoElike1.43B;change sharedexperts/granularity/activecount/LBloss oneatime. | Localbalance/localitytradeoff;sharedexpertarchitectureassociation. Trainingintervention;not permissible runtime tweak to frozenQwen. |
| N_CACHE / sec5.2/AppendixF; PDFpp10,27-29 | AUTHOR_TRACE_CACHE_ANALYSIS_PLUS_NAIVE_RUNTIME; NOT_DISCLOSED | OracleSCH/BeladyvsLRU/LFU;TOYnaiveon-demandLRUvsfullGPU. | Throughputoverhead correlation ~+0.2prefill/-0.3decode. Oraclefuturefrequencyisnotimplementableprediction;no strongenginecausality. |

Our inference: Locality depends on model/domain/cache size;capacity target alone cannot predict migration costs. Natural per-layer routing identity first;do not manufacture hotexperts or infer latency from repetition/SCH. Compare strongprefetch/eviction/fusion,not naiveLRU.

Missing: No modelrevision/requestSHA in paper.; Natural corpuspass != exact freeze of generated autoregressive routes;naiveLRU is not strongoptimizedserving.


## 直接创新碰撞与适用范围

| 问题 | 直接被已有工作覆盖的宽泛想法 | 不能据此排除的窄问题 |
|---|---|---|
| Q1 | GS-Scale forwarding/deferred overlap；CLM camera reuse、选择性appearance传输、optimizer finalization；TideGS跨层次working set与差分异步 | 固定Rubble算法、真实自然U、强线程/placement后，是否仍有可确认的完整应用暴露等待；CPU服务与GPU/传输竞争如何区分 |
| Q2 | Strata的hierarchical cache、GPU-assisted IO、layout及scheduler；A70N的混合allocator/checkpoint/Replay | 某一实际兼容hybrid配置下，真实分支/恢复/flush压力与allocated-versus-content差距是否形成完整请求成本 |
| Q3 | MonoMoE weight-major persistent融合；Patterns自然路由预测/placement/duplication；LRC的模型与域相关性 | 同格式、同自然route、最强可用软件后，仍暴露的专家权重/元数据/通信成本，及其应用分母与可控资源响应 |

### 数值和任务语义不能拼接

TideGS会在eviction时丢弃optimizer moments并cold restart，trajectory次序也不同；GS-Scale deferred Adam包含近似；CLM批内数学更新论证不自动保证FP求和次序逐bit一致。它们是容量/吞吐/质量的不同点，不是可直接相乘的加速。

ACL HybridKV是多模态KV压缩：static pruning与dynamic retrieval改变保留attention内容，不是A70N的GDN+full-attention混合状态管理，更不是exact full-cache替代。同名AdaptFM论文不混入。

Patterns的预测/placement/重复slot需计元数据、额外容量和通信；其真实GPU组不包含完整attention/all-to-all/top-k分母。Not All Models的oracle/naive LRU不是强serving性能基准。MonoMoE的随机router算子组和自然Sonnet端到端组分开；公开API从router_logits开始，不含其上游线性投影。

## 版本与可复核性裁决

1. GS-Scale使用ASPLOS2026作者final，不把2025 arXiv年份当会议年；TideGS锁v2及项目ICML身份，paper与当前repo的Torch版本、batch/cache默认不同。
2. Strata使用OSDI正式版；旧preprint的TTFT摘要与final throughput不混。Patterns锁v5/正式ISCA身份；v3旧题名/旧模拟结果不替代final，mutable AE模型名漂移另记。
3. MonoMoE本轮确认为preprint，不补造会议接收。补充source freshness检查已取得FlashInfer当前HEAD 8af51e46aaecb6d0002f096f13f8f2465133dcb0的wrapper；与历史pin字节相同，仍声明Hopper/SM90a和E256/N512/K2048/M≤8。这个补充只解决wrapper可读性，不是已安装、JIT或H200数值资格，绝未调用has_monomoe。
4. HybridKV正式ACL正文经web核查；本地精确PDF SHA对应arXiv v1，不能把它伪标成正式ACL二进制SHA。
5. GSArch primary全文方法缺口不阻止本规划交付，但禁止据摘要声称实物、cycle model或PPA已复核。

## 本轮文献结论

新颖性排除必须与性能排除分开。上述论文足以否定“通用camera reuse／KV分层／低token MoE融合没人做”，不能证明所有适用部署的残余为0。下一步应执行有真实输入、同语义强基线和一个独立诊断变量的最小发现合同；若资格不足，NO_GPU_PROBE_READY是有效决定，不再为凑正候选扩大范围。
