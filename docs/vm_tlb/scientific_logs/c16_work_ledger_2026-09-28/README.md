# C16 / AI负载工作总账：截至2026-09-28

**用途：回答“我们已经做过什么、得到了什么、哪些没奏效、哪些根本没有执行、以后应从哪里继续”。**

记录分支：`hrl/c16-work-history-audit-20260928-v1`。

这是C16项目的远端文档/证据入口审查，不是重新实验。本轮盘点Framework中282条、Core中9条C16相关分支，整理为**70条逻辑工作记录**。分支、记录、实验次数三者不同：同一实验的producer/consumer/coordination不算三个独立实验；host组合相对两个baseline的比较也不算两个独立机制。

## 1. 阅读入口

| 文件 | 用途 |
|---|---|
| `WORK_LEDGER.tsv` | 70条工作：节点、工作内容、原结论/状态、证据范围、限制、来源和后续处置 |
| `NEGATIVE_AND_SUPERSEDED.md` | 负结果、局部有效但系统无效、工程阻塞、排除证据、已被后继替代的状态 |
| `SOURCE_INDEX.md` | 已读remote文件的ref/path/blob，冻结交接与审查深度 |
| `BRANCH_INVENTORY.txt` | 全部分支名称快照，保留早期与仅协调分支，避免遗失入口 |
| `AUDIT_NOTES.md` | 本轮发现的重复/旧状态/证据缺口，以及没有做的审查 |

来源编号如S28指`SOURCE_INDEX.md`。本文件是总览，具体claim仍以原producer/consumer及其source authority为准。

## 2. C16实际走过的路线

### 阶段A：把真实AI执行变成可审计的数据

早期3090/租用GPU、retry570、Route-B、Llama支持、迁移与RTX4080 R1–R5构成基础设施历史。本轮全部登记分支，但没有把每次恢复、重试或handoff都包装成一个科学实验。R5明确排除了R4定量数据；Pipeline V1的synthetic资格和归档成功也不等于GPU性能成功。[B0/S03/S04]

随后建立了direct-global及LDGSTS等特殊路径的formal捕获与独立消费：Qwen0 decode的98-shard范围、LDGSTS的5个ACK target sets、AWQ fused路径资格、source/manifest/catalog/ACK和对象映射。其主要成果是**证据能够在特定范围内可信使用**，不是已经找到了cache优化。[S05–S08]

早期RAW/AWQ对比保留为semantic-module deployment comparison，因为自然部署输入不同；统一consumer也曾留下NCU durable export和tokenizer版本缺口。这些历史限制不会因后续成功而从记录中消失。[S09/S10]

### 阶段B：扩模型与访问对象，而不是凭一个kernel概括AI

Qwen3的执行、cross-lineage、attention/KV路径逐阶段推进，终局中出现`PASS_WITH_NCU_GAP`、`PASS_WITH_TYPED_GAPS`。V19的具体anchor是repeat-K；不能从一个PASS标签扩写成所有persistent KV行为。Qwen3 S3 V20/V21系列已登记分支，本轮没有完成其所有底层结果文件核读。[S11–S13a/B0]

MoE侧完成Q30、DeepSeek、OLMoE三条自然expert-down-proj anchor与统一per-shard分析。三者均有weight/input事件近半、output很小、OTHER=0，但都受到cuBLAS gemvx实现家族耦合，不能称为三种独立kernel验证，也不能从shard集合推全局时间顺序。[S02/S24]

DeepSeek MLA没有得到clean direct-read目标，保留的是mixed persistent-cache consumer；gpt-oss-20b在当时RTX4080/SM89 native MXFP4路径上阻塞，没有进行formal性能实验。[S14–S17]

OLMoE V32–V38连续遇到输入冻结、实际static selector、JIT variant和lifecycle问题。每一阶段分别保留“native已运行多少”和“formal是否运行”：例如V34 native/routing成功但formal静态资格未过，不能笼统当成模型失败。最终V40才形成actual-JIT A条件下243条静态路径、129执行/114零的正式admission。[S18–S24]

### 阶段C：E1把“低比特访存可能更好”收敛成具体驻留问题

Clean baseline在byte-identical FP16输入下建立operator×M×implementation interaction。Semantic NCU V2补上完整semantic范围与application-replay/cache-control-none观测；V1保留为cold-cache diagnostic，不与V2混用。[S26/S27/H0]

后续问题依次为：

`局部驻留是否有价值 → 完整自然间隔后还能否保留 → CUDA针对性保护是否有效 → 多目标共享 → 扩覆盖 → 扩算子族 → 系统收益究竟被哪里抵消`

这条链不是重复同一个实验。已冻结结论如下：

| 阶段 | 原结论 | 当前能保留的认识 |
|---|---|---|
| Controlled intervention | `RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED` | local timing/traffic敏感，但严格reversibility未全过 |
| Natural reuse | `CASE_B_WITH_CASE_D_ROLE_DEPENDENCE` | isolated warm行为不能直接代表自然上下文 |
| CUDA targeted persistence | producer/consumer规则分歧保留 | local timing有效不等于严格natural DRAM门槛通过 |
| Shared residency | `SHARED_RESIDENCY_LOCAL_ONLY` | 多目标局部收益没有形成material whole-decode收益 |
| Coverage scaling | `COVERAGE_SCALING_POSITIVE_BUT_SUBTHRESHOLD` | 扩到N28后仍不够 |
| Operator-family expansion | `OPERATOR_FAMILY_NOT_SUPPORTED` | 从up扩到完整gate→up→down并未解决系统门槛 |
| Cost/benefit closure | `RESIDENCY_OFFSET_LOCALIZED` | 局部收益被其他semantic work抵消；唯一微架构原因未确立 |

以上都应保留，包括没有系统收益的阶段。[S28–S34a]

成本闭合在B8/B16/B24/BFULL均保留28/28 up_proj局部material收益，并把run-aligned、非重叠top-level残差控制到绝对中位数小于0.10ms。BFULL代表L0 attention NCU没有复现aggregate attention slowdown，因此不能把抵消直接归因于该单kernel或唯一L2机制。[S34a]

### 阶段D：在模拟器中分开检验准入、存活和价值

已经完成bounded D1–D3 full-SASS trace、28个qweight区域sidecar、trace→sim L2数值命名空间资格，以及M1实现。trace包含4515个kernel，但与早期native timing不是逐byte同一输入，不能做逐run绝对毫秒/周期校准。SM89 opcode支持也只是parser/execution compatibility，不是完整Ada微架构拟合。[H0/S01]

Lane 1进一步完成：

- trace reuse/set-pressure分析：静态placement广且均衡；reuse-gap/reference pressure只能称proxy，不能称已测L2 eviction。
- target-class fairness限定结构分析：说明M1可能存在target间冲刷，不是Lane4的实测结论。
- M1F stable selector及真实trace激活：具备测试资格，不等于已有跨token存活或timing收益。
- P_all/P_stable/DRRIP/C16_SHIP_SW_STYLE_V1及exact-generation observer：unit、sector、bounded neutrality/activation准备完成；没有完整比较结果。[H0/S36]

**唯一尚在长跑的科学关键路径是Lane 4的R0/M1 B16/diagnostic。** 当前没有可接受的terminal timing结果；本次也未读取其partial数值。M1F是否值得运行仍取决于Lane4 project-level gate，不由“已经实现”决定。[H0/S37]

### 阶段E：尝试过host加速，但没有得到可采用的加速版本

Lane 2试过关闭部分统计、PTX统计guard、增大runtime-stat间隔、预解压、tmpfs、绑核及组合。源表中最好的单项名义改善是+1.7172%，低于5%门槛；组合相对当前authority反而-16.9899%。source candidate bounded行为exact但更慢，已回退。LTO/PGO只是考虑后未构建，不能记为做过且无效。[S35–S35b]

结论保持`HOST_ACCEL_NO_SAFE_MATERIAL_GAIN`。16-kernel测试prefix没有completed target，因此其exactness不应被扩大为所有target-victim决策的动态验证。

### 阶段F：等待长跑期间的独立探索

**E3已经完成，不再是待执行。** 固定Q30 Layer24场景中N/U差异低于离散、P等价，H是人工8-expert极端；结论仅为该范围下balanced代理足够，不推广为所有MoE无routing问题。[S25]

**Lane 5→Lane 7：低比特数据流到split-K A/B。** Lane5只保留一个fixed split8机会，109上的Lane7已实际完成split8对split1。结果只在up_proj M256得到28.88%改善，down_proj M256约0.90%，两个M1反而回退41.30%/413.32%。因此全局H1失败，结论为`OPERATOR_SPECIFIC_SPLIT_POLICY_ONLY`。这里存在一个bounded部署观察，但没有通用no-split方案，也没有新split-K算法或full-model加速主张。[S39/S41/S41a]

**Lane 6：MoE时间结构。** 从持久档案找回Q30全48层×4-step显式ID，OLMoE有单层32-step，DeepSeek只有单点。OLMoE相邻Jaccard 0.250659落在保持边际频率的shuffle区间0.171546–0.294940内；这只是否定当前检验中解析出的额外相邻信号，不排除其他lag。跨模型结论仍`TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL`。[S40]

随后174-new完成了明确标记为post-hoc的period11审计：OLMoE Layer1的lag11 mean Jaccard=0.928042，而同lag whole-step shuffle p95=0.313967；lag1–16中只有lag11高于各自shuffle p95。21组(t,t+11)中15组unordered exact-set repeat、5组7/8 near-repeat，19组next-token相同，但router-input/logits SHA相等均为0。结论限定为`POSTHOC_PERIOD11_SIGNAL_CONFIRMED` + `ASSOCIATED_WITH_TOKEN_REPETITION` + `ORIGIN_UNRESOLVED`；V1的`TEMPORAL_AUTHORITY_INSUFFICIENT_CROSS_MODEL`保持不变。V34没有durably保存实际generation runner/KV transition/sampling/seed/EOS/stopping细节，因此目前不能区分真实内容循环和capture/replay methodology，也不能据此推出cache机制。[S42]

## 3. 当前节点/Lane状态

这是最后已接受交付的状态记录，不是本轮SSH探测到的实时进程状态。

| Lane | 节点 | 当前角色/状态 |
|---|---|---|
| 1 | 174-new | baseline与survival observer准备完成；冻结，等待必要的后续授权 |
| 2 | 174-new | host加速负closure；关闭 |
| 3 | 174-new | Paper/Evidence V1冻结；terminal review prep完成；没有Paper V2结果 |
| 4 | 174-new | R0/M1/diagnostic继续原长跑；严禁停止、重启或替换 |
| 5 | 174-new | lowbit dataflow screen完成；其A/B已在Lane7执行 |
| 6 | 174-new | temporal V1与period11 post-hoc审计均完成；跨模型仍不可比，period11来源未闭合 |
| 7 | 109 | split-K A/B完成并释放锁；保留为后续RTX4080 GPU窗口 |

109未来实际CUDA工作仍必须持有`/data/c16/locks/c16_gpu_campaign.lock`。164仍为durable raw/catalog/provenance来源。109上的纯CPU工作可另开窗口；不得以“不计时”为由绕过GPU锁。

## 4. 最新关键代码/交付锚点

| 对象 | ref |
|---|---|
| Lane4 Framework | `8dfd9c0fdc98314c2aa11710da9b89f59e4c7a66` |
| Lane4 Core（gpgpu-sim） | `0271de82432db004beed43280ed01057246a0f2c` |
| Lane4 binary SHA256 | `6be0986958ffbb8a128ce19e8a88b53a4c4838f97202c2f3d1c9dec6e9a02186` |
| Lane1 closeout Framework | `013370ec4a0f37fcba2b2bd4329048c8113a30a3` |
| Lane1 closeout Core | `857abd0d071e301848b032bfbe30e8457b219e96` |
| Lane3 terminal prep | `4f45bf0aaec0d0fb63fb39adb835f89dcf5da1ef` |
| Lane5 screen | `dcbd60f98753ec678642bd4be745469409ffb734` |
| Lane6 temporal V1 | `0017527afba6861a4a0cfee95cce7b2a0397f284` |
| Lane6 period11 post-hoc | `72fdd0f89aa0d4d4ae8b0d55daea492fbae2f293` |
| Lane7 native A/B | `0e88faa28c9066b48e394dce657d7a16e6332a32` |
| 文献LR02–LR06 | `dc41de767b55f3ba1532627f1cb5dc176ea539ee` |

Lane1的Core线性继承0271→060e→857a，但其Framework准备分支不是Lane4 Framework的同一条线性后继。未来full timing要重新绑定最终framework/config/trace/source，不应直接把任一准备branch当成完整实验authority。

## 5. 后续如何维护

新增工作先检查`WORK_LEDGER.tsv`：已有相同问题且已关闭时，必须说明新的变量或证据是什么；不能只换一个任务名重做。新行保留节点、输入/实现范围、原始状态、直接证据和不能声称的结论。

历史文件不覆写。新closure更新总账的后继关系，明确旧结论是被取代、被限域，还是仍然成立。`PASS`与“有性能收益”分别记录；`NOT_RUN`、工程blocker、negative result、subthreshold、partial coverage也分别记录。

本总账不授权任何新GPU/simulator实验，不变更M1F gate，不把文献或静态推导升格成执行证据。
