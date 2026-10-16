# Round A72｜A70 M-A70与四线主流大模型Discovery综合独立科学审查

**日期：2026-10-16；执行者：ChatGPT／AI-ARCH Discovery。** 本轮使用GitHub固定Git报告/源码、DuetServe ICML2026作者PDF与PMLR正式页面、纯控制端整数计算。没有启动GPU、Node109/174/164作业、模型下载、编译或模拟器。

**最终裁决：M-A70的 \`NO_SURVIVOR_IN_SEARCH_SCOPE / STOP\` 接受，适用后缀 \`SOURCE_SCOPE_ACCEPTED_NOT_NATIVE_NEGATIVE\`。A70的M/N/O/P四线均已完成，同样是限定源码/论文搜索下0主＋0备；不是主流LLM、GDN、MoE和多模态四个领域的性能负结果或已证明没有硬件机会。**

## 0. 四线完整执行与审查identity

共同Goal \`8f24af162ba37b4fa37f7a18d89b0fdb62697942\`，科研基线 \`10f3a51ee39884bcec3d3180e81cc405872cccb1\`。

| Lane | Final commit | Git tree | 原报告/独立审查 | 证据 |
|---|---|---|---|---|
| M / 109｜Dense LLM混合服务 | \`f2d6324da298be26f39cda427f3e7db1a7e7031d\` | \`5cbb8f8eaa4fb00efcd51bc963bf68c6b3263d52\` | [M原报告](https://github.com/swayhrl/accel-sim-framework/blob/f2d6324da298be26f39cda427f3e7db1a7e7031d/docs/ai_workload_research/discovery/A70_M_LLM_SERVING/REPORT.md) | 21 |
| N / 174-new｜混合递归状态 | \`5076223db5db0256fd0ccacec50b5347a0cab8c5\` | \`592e12903c8fa029fb5108a967f8a00bb9cb9458\` | [N原报告](https://github.com/swayhrl/accel-sim-framework/blob/5076223db5db0256fd0ccacec50b5347a0cab8c5/docs/ai_workload_research/discovery/A70_N_HYBRID_STATE/REPORT.md) | 21 |
| O / 109｜MoE专家执行 | \`94ca01df352cf4cf707cd35e5f9f63d4eff014c6\` | \`b5b3d7f8f925c50aa845cebec2cb3057fe91b261\` | [O原报告](https://github.com/swayhrl/accel-sim-framework/blob/94ca01df352cf4cf707cd35e5f9f63d4eff014c6/docs/ai_workload_research/discovery/A70_O_MOE_EXECUTION/REPORT.md) | 24 |
| P / 174-new｜VLM视觉—语言交接 | \`f2399777a30f4fdafa26858b3cd418e497538db2\` | \`811616c50e4594e1884d4ee4e4c622a72fb953d1\` | [P原报告](https://github.com/swayhrl/accel-sim-framework/blob/f2399777a30f4fdafa26858b3cd418e497538db2/docs/ai_workload_research/discovery/A70_P_VLM_PIPELINE/REPORT.md) | 17 |

对于M，独立核固定Goal→final ahead1、只新增自身目录REPORT/EVIDENCE/CANDIDATES/RECEIPT四文件；final→执行分支HEAD identical；Git-data commit parent为固定Goal且tree与用户回报一致；四个远端blob回读，CANDIDATES.json=\`[]\`。M EVIDENCE.tsv 21条、11列、行结构完整、ID唯一。此前[A71 N/O/P独立审查](https://github.com/swayhrl/accel-sim-framework/blob/0c891b59e28177bfbff1ce6a6744a26fa6d30ad2/docs/ai_workload_research/reviews/AI_ARCH_A71_A70_N_O_P_PARALLEL_DISCOVERY_INDEPENDENT_REVIEW_2026-10-16_V1.md)分别对三条的Git树/报告/62条证据、关键源码和CPU推导完成范围内独审。**合计83条TSV记录**，但包含目标合同、源代码、旧项目条目与论文，多数并非83个独立实验组。

**验证层级限定：** M四blob的独立Git身份和报告内容已读；执行者报告远端四文件SHA和worktree clean。本审查未另行在109计算全部原始下载文件的本地SHA，也未进入109核实际进程峰值；执行者资源/线程记录以其RECEIPT为准。所有四条都不是新的GPU native负例。

## 1. M-A70：实际被排除的假说

主模型：[Qwen/Qwen3-8B fixed config](https://huggingface.co/Qwen/Qwen3-8B/raw/b968826d9c46dd6066d109eabc6255188de91218/config.json)，36层、8 KV heads、每头128维、BF16、标准完整注意力；官方模型参数元数据8,190,735,360个。这是合理的主流完整模型内容锚点，而非本机运行或已核权重revision。

**与旧C16不重复，但新近邻已经直接覆盖：**
- Sarathi-Serve原有chunked prefill＋混合batch；DistServe原有跨GPU阶段拆分；NanoFlow原有算子级/异步组织；Nexus用long-KV参与动态SM分配；DuetServe同时含attention-aware latency model、on-demand SM隔离与lookahead调度。仅凭把Prefill/Decode分流、依据KV长度调SM、新增异步双流，都不能称为全新机制。
- M的实际新变量是自然请求的阶段组合、上下文长短、排队/服务及GPU时间分解。C16 MP02仅B1 compiled Graph ON/OFF合法子结果、MP03 B4未准入；C16 FFN兄弟投影双流减速不等于Prefill/Decode并发已被否定。**所以M没晋升不是因为C16已经测负，而是直接近邻＋缺强路径后特定残余证据。**
- 当前vLLM固定\`fa75d3456d60a5ffe923818c4b495295675b38e1\`的\`vllm/v1/cudagraph_dispatcher.py\`实有\`dispatch(num_tokens,uniform_decode,...)\`，可返回NONE/FULL/PIECEWISE；\`vllm/v1/attention/backends/flash_attn.py\`区分FA3/FA4的\`AttentionCGSupport.ALWAYS\`与其它路径的\`UNIFORM_BATCH\`。**源码能力条件存在，并不意味着109或任何设备的每个混合batch真实命中FULL图，更不等于运行时免费。**

### DuetServe原始论文复核

独立读取了[正式PMLR ICML2026会议页面](https://proceedings.mlr.press/v306/gao26m.html)及[作者完整15页PDF](https://pages.cs.wisc.edu/~markhill/papers/icml2026_DuetServe.pdf)的正文，并视觉核PDF第一页。原文§4说明其attention-aware roofline、动态SM空间分配、lookahead CPU执行；作者明确提到通过libsmctrl控制每stream的SM集合，不能笼统称为我们需要首次实现Green Context。

原文§5.1：
- 96-core Intel Xeon Platinum 8480C，2×H100 80GB NVLink，CUDA13、driver580.95.05、PyTorch2.8；
- Qwen3-8B TP1与Qwen3-14B TP2；Azure-Code 19366 req/ISL2047/OSL28、Azure-Conv 8819/1155/211、Mooncake sample 1000/12035/343，按Poisson重新生成到达；
- vLLM v0.10.1、SGLang v0.5.0、Dynamo v0.5.1等作为当时对照，含FA3；报告mean TTFT、mean TBT、completed requests/whole wall。
- **作者PDF未将这些指标升级为P99 TBT/TTFT或预冻结双SLO goodput**；不把“已有模型”外推为旧新版所有工作形状零剩余。反之，缺P99也不能凭空让新架构方案成立。
- 论文实验组硬件/版本与M本轮固定的最新vLLM及109 RTX4080不同。没有相同代码和真实自然trace的合法配对结果，因此这是一项**成熟软件/研究机制的直接近邻**，不是“109强路径native已经没有性能空间”的证明。

### 两项独立整数复核

1. BF16 KV每token \`2*36*8*128*2=147456 B = 144 KiB\`；两条32K上下文KV内容\`9 GiB\`；BF16参数量\`8190735360*2B=15.256433 GiB\`；总内容\`24.256433 GiB\`，不计Graph、runtime、workspace、allocator等。16GiB RTX4080不能直接复现该**具体BF16双32K**完整模型服务内容，缺预算不是“LLM服务研究无价值”。
2. 无历史前缀的标准因果注意力，8个独立1024-token请求的总(Q,K)对数=4198400；1个8192-token请求=33558528，约7.99317×；因此相同token预算不等于相同attention必需算术量。**这是静态工作量差，不是测得GPU DRAM、stall或可节省的时间**。已有DuetServe attention-aware思路同样讨论它，不能把这个算式立为新机制。

M启动阶段首次fetch的Git pack/index配置2线程、实际活动并发未观测，后在合同阅读后改为单worker、单线程。此为收据明示的\`INITIAL_GIT_THREAD_OBSERVABILITY_GAP\`，不是科学数据门错误、GPU并发污染或发现证据失效；不可无依据将所有30分钟过程升级成严格单线程证明，也没必要让M重启工程收尾。

## 2. 四线横向综合：为什么四个0以及风险

| Lane | 这轮实际排除的直观方案 | 仍为UNKNOWN的性能/因果对象 |
|---|---|---|
| M 常规LLM服务 | 仅新增chunked Prefill、P/D资源动态SM拆分、普通长KV感知调度 | 真实长短请求+到达、最新强runtime下完整请求SLO/排队/实际GPU执行竞争 |
| N 混合attention／GDN | 认为混合页无法分配/复制或每token完整state写回无人研究 | 固定合法配置下state copy/flush与slot争用的实际wall，天然并发轨迹；ReplaySSM的fork与上游区分 |
| O MoE | 仅新增sorted-token、grouped GEMM、融合/共享专家重叠 | 固定实际router与支持的最优backend的同边界route-to-combine及请求wall；旧E3是Q30 Prefill expert loop |
| P 多模态 | 仅新增视觉Graph支持/embedding缓存/编码器分离 | 多图/视频自然输入、DeepStack交接、Graph预算与完整TTFT/ITL在真实当前强后端的影响 |

**四个0不是83条原生负证据。** 四线并发有价值：归档了固定模型/源码/原文具体实验组及软件反证，并收窄了弱动机。然而科研发现不能陷入“没有别人未解决的wall就不能提新问题；不做wall就永远没有证据”的循环。

本轮方法上的约束修订：
- Discovery早期允许提出一个**低成本、有真实任务、同数学语义、强软件且可证伪**的原生诊断提案，不须先有完整硬件机制上界；这不代表允许在A70的0候选上自动开GPU。
- 仅用别人已有解决方案否定**完全同质机制**，不要否定尚未控制的模型类型、阶段组合、容量/并发、任务质量或不同硬件资源扩展条件。要有独立变量，不能只换模型名字或追最新repo。
- 候选应按**发现真实计算阶段/部署约束**而非先找某部件bug；时间、容量、能耗、质量与GPU规模分开。局部family headroom可以有价值，但需写出在主流自然任务中的覆盖分母，不能以任意5%一刀切。
- Native与机制/PPA证据分级，不能以作者H100/H200/GB200结果自动命名109 SM89 stall/性能；当前共同Goal只批准source-only，新资源另行冻结。

## 3. 下一阶段具体方案：先换Discovery的组织方法，不发布下一波重复4份源码Goal

**建议Round A73采用三条互补而非四条重复“找新论文”的研究生产线，先并行CPU/source，待合同审核另行派发：**

A. **真实通用模型工作负载与输入分布（workload-first）**：优先固定可合法复现的真实自然请求/训练阶段，检查请求到达、上下文重复与更新、真实媒体/token/专家活动的原始分布。候选范围不预设并发SM划分，需要证明输入含足以区分问题的变动，不能用全合成极端热点。交付1—2个真实输入资格卡及具体有区别的工作量变量，首轮不下载数据。

B. **体系结构而非只看serving runtime（architecture-first）**：从近几年ISCA/MICRO/HPCA/ASPLOS/MLSys/OSDI已发表直接GPU AI架构工作回到实验组：模型/输入、真实/模拟、资源变化与oracle、近邻软硬件对照，重点回答哪些资源约束可能仍在主流模型中产生新的实验问题；不预设Cache。交付2—3个有明确结构变量与反证、能够轻→重验证的框架，不能照搬作者机制宣称新颖。

C. **低成本原生反证资格（measurement-first，仅CPU静态准备）**：以A/B真正提出的1—2个不同科学问题，反推一个真实模型/配置、当前强runtime与最小公平观察边界，核109 16GiB能够支持哪些真实尺度、哪些必须大显存／多卡；复用既有被接受输入/模型资产只作为后端映射而非选题起点，不能扫描164或进行GPU探针。交付有STOP的native科学合同草案，而非立即部署环境。该线科学上部分依赖A/B识别的新变量，可以在A/B的已选问题小表公开后进行下一阶段；其余工程与方法文本可并行。

真正的下一步不应是“再给四个Codex各读十篇文献”，而应当让**工作负载、架构约束、强软件最小验证**三个方向独立推进、随后交叉约束。A73的3个方向尚为协调方案，未建新的执行branch/Goal、未授权109/174 GPU或模型下载。若希望先无等待并行，可让A/B率先同时启动，C在得到第一批问题变量后开始；不是要求三方彼此等待完整报告。

## 4. 冻结与终态

- A70 M/N/O/P四条均正常STOP，0主0备；N/O/P原始独审在Round A71，M与综合在本文。
- 不为验证DuetServe“已做过”的结论再申请H100/H200；如果未来有真正不同的自然变量及公平基线，再单独审批不必被硬件品牌绑架的探针。
- A61/A65/A67 GNN原STOP、A69 ScanNet低优先级、C16/AWMA/ISCAS独立权限与164数据资产均不触碰。
- 本次协调只追加科学审查并更新导航，不merge四个执行HEAD，不将\`NO_SURVIVOR_IN_SEARCH_SCOPE\`重标为\`HARDWARE_NEGATIVE\`。

**Round A72终态：四线限定Source Discovery收口；当前无运行中A70 Codex。下一轮应改变发现方法与实验变量，而非重复原软件优化列表。**