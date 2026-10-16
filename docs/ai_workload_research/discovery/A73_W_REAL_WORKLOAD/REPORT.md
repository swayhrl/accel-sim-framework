# Round A73｜W-A73 真实主流模型工作量 Discovery（109）

日期：2026-10-16；执行者：Codex／W-A73。固定起点`9afcdf6faa5b8351b56c9cbbefd3530c19c89537`，科学父提交`adf6ab9467887f74b0b509c105977128663707a5`。

**终态：SOURCE_INCOMPLETE / STOP；2个重点自然场景，0个可晋升问题，1张PARKED问题卡。** SOURCE_INCOMPLETE只指“用于新问题的同内容、同依赖目标模型输入资格”尚未闭合，研究交付已完成；不是没有公开工作量来源，不是GPU负结果，也不意味着未读完Goal。原文、固定source、反证、最小后续与边界连续收口，无H-A73依赖。

## 0. 本轮获得什么，仍缺什么

这轮从实际输入查到两个值得保留的对象：真实聊天提交序列，以及真实日常编码agent的跨请求/工具会话。它们公开字段的含义和可复现边界不同，不能拼成一条不存在的“生产trace”。自然的会话间隔、上下文变化及工具依赖，确实改变状态的保留与再次就绪条件；**仅有token计数不能决定实际词法前缀，原服务的缓存命中也不是新的目标服务应当继承的输入条件。**

本轮最具体的发现是输入口径：TraceLab文档将`prefix_tokens`定义为提供方缓存读量，其导出器映射到`prefix_len`，`input_len`来自含cache miss的append统计；作者runner再用合成语料构造prompt。它明确是一种shape replay，不是原私有请求重建（W05—W08）。这不是宣称作者有bug，也不从缺少原文推出硬件机会。现有XPerf已经研究exact-token、依赖守恒的回放；Marconi/SegLen已经研究多轮复用和重算距离。因此保留的WQ01是**输入与资源归因的待资格问题**，而不是新缓存/调度机制。

完整读取本次Goal第0—6节，重点执行0—3与5—6；共同CURRENT_STATE、A72综合、协调协议1—8、问题图谱及A70四线开头/结论/直接近邻已读。图谱P03/P06/P11/P12及A72用于边界；不扩成Architecture-first，不改协调文件，不重启C16/AWMA/ISCAS/GNN旧STOP。

## 1. 输入筛查与两个场景的选择

先看来源字段与许可，再选场景，而非从已下载模型反推。扫描范围限定聊天/多轮agent，不铺模型名单；真实内容备选只核官方元数据。

| 入口 | 已披露与限制 | 本轮用途 |
|---|---|---|
| BurstGPT官方Release v2.0，README@`d895a53bb7b8ec137d0d2fe203b335835a78c10a` | 真实时间/会话/输入输出长度，CC-BY4.0；未提供文本 | 选中场景A，资格卡明确长度/时间可复现而语义不可直接重放 |
| TraceLab v0.0.1，source@`37402b4098dc65de56727b4c204fb71c8a59ddac` | 日常开发者会话的时间、调用、usage；发布数据CC-BY4、代码Apache2；原文移除 | 选中场景B的自然分布与字段证据；不把合成回放当真实内容 |
| SWE-chat官方含内容入口，README@`8465db2a234dffd02be2e118bf3437771963b095` | ODC-BY数据卡标签；作者要求申请访问，完整分析约4GB RAM/7GB盘 | 同一场景B的有界内容补充入口；未申请/接受条款、未下载，也不改去第三方副本 |
| SWE-bench官方真实issue任务 | 可作为独立质量输入入口；代码MIT不替代各repo/数据许可；无生产到达 | 未来独立任务验证；本轮只读README |
| LMSYS-Chat-1M / WildChat官方数据卡 | 前者要求接受专门协议，后者标ImpACT-LR；文本存在不代表已有权限；时间与其他trace不可任意配对 | 不作为本轮主输入，未点击同意或获取payload；不为此改预算 |

上述许可均为作者公开标注和使用入口的记录，不宣称用户已经取得payload资格。没有下载CSV、JSONL数据、DuckDB、Parquet、`.traj`、真实转录、权重或tokenizer。公开README中的版本/哈希只是元数据，未冒称已核数据文件SHA。

## 2. 自然工作量变量卡A：真实多轮聊天提交序列

**科学对象**：BurstGPT原Azure ChatGPT/GPT-4的Conversation log/API log（W01—W02）。拟挂接的真实新部署是[Qwen3-8B固定配置](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/config.json)（W18），不是声称原trace来自Qwen。该模型的default config为BF16、36层、GQA8KV heads、40960位置、无rope scaling；超过范围不可静默截断或扩RoPE后仍称同配置。

| 自然变量 | 直接披露 | 获批元数据后可构建 | 必须另获内容/运行才知道 |
|---|---|---|---|
| 请求/会话时间 | Timestamp是提交时刻；Session ID仅对Conversation log有意义 | 同一自然窗口的到达—长度—会话联合序列、间隔、突发、失败分母 | 目标服务的enqueue/device-ready、TTFT/ITL、实际P/D交错 |
| 输入与输出 | Request/Response/Total tokens；response0包含失败 | 原提供方长度与输出长度条件分布，不混失败/无失败release | Qwen重tokenize后的长度、stop/quality、精确原prompt |
| 前缀/状态复用 | 同一session标识，不是前缀身份 | 只能标“可能共享历史”，不能填真实prefix hit | 实际LCP、编辑/压缩/隐藏模板、实际保留状态 |
| 并发与SLO | Elapsed是提交到完整回复的远端端到端时间；不是TTFT | 可构建原系统未完成请求数，不能叫GPU活动并发 | GPU wall、队列/网络分解、业务SLO和答案质量 |

公式`C_observed(t)=Σ1[submit_i≤t<submit_i+elapsed_i]`只描述原服务端到端未完成数。本轮未计算整个trace。缩放RPS、换Poisson、把失败去除都改变工作量；可在未来作为明确诊断，不能把它们称原自然主体。

**判断**：有真实时序入口，但没有同语义Qwen请求，不能把独立聊天文本与这些timestamp拼接后宣称自然服务。DuetServe等已有P/D及attention-aware强对照；“更长/更突发”本身不是新问题。这一场景暂不提交独立可晋升问题，保留为后续输入资格参照。

## 3. 自然工作量变量卡B：日常编码agent会话

**科学对象**：人发起request，agent在同session内交替产生LLM steps和工具调用；下一次人类request又继承/改写历史。TraceLab固定发布README列357161 rounds、432510 tool records、43 users；论文v1 Table3的合格子集计数另列于W17，不能将live README总数替换成论文各图分母（W03/W17）。该来源是实际开发使用，不等于全部生产用户。

拟研究的新部署为[Qwen3.5-4B固定text_config](https://huggingface.co/Qwen/Qwen3.5-4B/blob/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a/config.json)（W19）：24 GDN＋8 full-attention层、BF16、SSM FP32、262144位置。只取真实文本通用模型，不研究其视觉输入，不把GDN与Jamba的Mamba当同算法。原Claude/Codex计数不能直接当本模型token IDs或精确KV/state成本。

| 自然变量 | 直接披露/来源 | 元数据可构建（未来获批后） | 不可从当前字段补造 |
|---|---|---|---|
| 触发与时间 | session/request/round，用户/工具事件，timestamps，工具记录 | 用户恢复和工具连续追加分层的间隔、上下文变化联合分布；带missingness的依赖DAG | 原provider调度、cache TTL、单个事件timestamp就是精确server-arrival |
| 上下文增长/缩短 | usage与观察到的context change | provider口径的增减；不能假定每轮都append-only | 原prompt完整字节/token、缩短发生在哪个位置、是否隐藏system/tool模板变化 |
| 缓存与新增 | `prefix_tokens`是实际cache read；append含miss/cache creation（W05） | 分开报告input总量、服务端cache读量和语义增量待测 | hit-rate大即GPU成本小；cached prefix长度即语义可保留prefix |
| 工具依赖 | 导出器汇总工具耗时，runner等完整回复再等待（W06—W08） | 时间字段足够时核串并行/critical-path等待；会话外部起点保留 | 工具耗时之和一定是wall；把synthetic session arrival叫原真实到达 |
| 输出与质量 | 原模型输出/usage计数；hidden reasoning可能不在可见转录 | 披露每个provider的缺项与stop方式 | `max_tokens`等于实际输出长度；强制旧输出证明新模型完成任务；API价格节省等于GPU时间 |

该公开数据的价值是自然变量，不是给每个目标模型提供可执行原prompt。当前runner保留constructed history的前`prefix_len`，加合成pool token，并携带本次模型真正生成token；它对合成序列的身份有处理，但**没有恢复已移除的私有原文**。同一作者还把human-idle token/cost counterfactual明示为估算（W09）。本轮没有执行runner、导出器、分词或任一模型导入。

已有含内容补充SWE-chat，说明并非天然无法取得自然文本；但官方README要求access，且完整分析超本Goal预算，不能通过安装/下载或第三方副本补齐。其文本也不必然等于提供方完整model-facing prompt：隐藏模板、reasoning及工具并行就绪仍需逐项核验。这个差距是PARKED理由，而不是新硬件收益的证据。

## 4. 对同变量的4组直接近邻复核

其中Marconi为MLSys2025正式论文，DuetServe为ICML2026正式论文；SegLen是作者实验博客/实现PR，XPerf是固定v1预印本，证据等级分开。没有把它们拼成四个同平台原生实验，更没有做Architecture-first论文普查。

| 具体实验组 | 原输入/部署与控制 | 指标分母及能否覆盖W变量 |
|---|---|---|
| [Marconi §5.1—5.3/Fig7—10](https://proceedings.mlsys.org/paper_files/paper/2025/file/7c180af017258d239bac6248d1eb26ac-Paper-Conference.pdf)（W10—W12） | LMSYS/ShareGPT/SWE-agent traces；7B Hybrid，Jamba profile，FP16/A100；vLLM+/SGLang+；源码有合成间隔和历史观察折叠 | token hit rate与P95 TTFT；artifact所核时间绘图从profile映射miss长度，不当完整并发请求wall；直接覆盖多轮复用，不证明当前自然人类恢复边界 |
| [DuetServe §5.1/Table1/Fig6](https://pages.cs.wisc.edu/~markhill/papers/icml2026_DuetServe.pdf)（W13） | Qwen3-8B TP1/14B TP2，H100，Azure/Mooncake长度组，Poisson到达；FA3及当时vLLM/SGLang/Dynamo强对照 | mean TTFT/TBT、完成req/whole wall；已有phase multiplexing，不等于自然session时间与精确前缀/质量联合SLO |
| [SegLen SWEbench组](https://abdelfattah-lab.github.io/blogs/seglen/)（W14—W15） | Qwen3.5-9B/H100，固定`sps=10_art=5_nums=100`；LRU/Marconi/SegLen、cache预算变化 | mean TTFT/queue/hit；直接replay-distance软件近邻；blog与PR不同表不混；PR Closed不能声称已merge或109可用 |
| [XPerf §3.3—3.6/§5.1—5.5](https://arxiv.org/html/2608.20370v1)（W16） | 真agent应用的token-ID/DAG回放；vLLM0.19修改版、gpt-oss-120b等、H100NVL | 已有依赖/输出身份回放与queue/GPU分解；不能声称此前都只做独立请求；强制token性能回放不替代自由生成质量 |

作者声称与本轮推断、精度/许可/版本缺项均逐行在[WORKLOAD_EVIDENCE.tsv](WORKLOAD_EVIDENCE.tsv)。正式PDF在私有output只读，用现有pdftotext抽取相关完整方法页；不将PDF全文入Git。未重新验证Marconi全部曲线与当前artifact的生成链，也不将其profile-linked数字全部写成服务原生wall。SegLen fork/current upstream兼容性未知，未来不能为追求“最强”而假装已有兼容基线；也不能拿无缓存fallback替代强基线。

## 5. 小型CPU诊断与计数恒等式

只做3项常数大小的stdlib检查，不读语料、不生成自然分布、不执行simulator：

1. 相同输入长度4可以对应LCP=3或0（整数符号示例）。长度不足以恢复前缀身份；这不是实际模型token，也不是自然样本。
2. 串行工具链中`next_ready = previous_completion + tool_gap`。当完成时刻为1或3且gap=2，就绪为3或5。固定所有step提交时刻无法同时保留两个后端的闭环因果；XPerf/TraceLab已处理此类方法问题，不能把这个恒等式称新机制。
3. 两个独立工具耗时2与3，work总和5而并行wall3。只有实际时间/DAG才能决定应使用哪个分母，不能以这个示例断言TraceLab自然数据一定并行或其导出器实际高估。

另区分三个量：`L_semantic = LCP(previous_model_visible_context, current_prompt)`，`H_observed = provider_cached_input_tokens`，`N_prefill = total_input - H_observed`。通常不能将`N_prefill`全部解释为新内容，也不能把`H_observed`当与替换缓存策略无关的外生负载。真正恢复/复制、必要attention读取及暴露wall均要运行才能知道；不由上述计数换算GPU stall或加速。

## 6. 问题筛选、最强反证与WQ01

| 筛查问题 | 裁决 |
|---|---|
| 真实突发＋更长context，所以要重新划SM | DuetServe等已直接处理；缺少独立条件，SOFTWARE_NEARBY，不重复A70M |
| agent steps有依赖，应该闭环回放/跨turn保留KV | XPerf、TraceLab runner及既有复用策略是直接近邻；不是新问题 |
| 提供方cache-conditioned统计与语义内容变动分开后，用户恢复/上下文改写边界的GPU准备代价是否与工具追加不同 | WQ01：PARKED_SOURCE_INCOMPLETE。自然触发与口径有来源，但缺可核target-token ledger；不能仅凭作者推荐研究方向或缺wall就晋升 |

WQ01既不是“所有cache hit都免费”，也不是“GDN checkpoint无人做”。A70N已有exact-state checkpoint/reuse实现，A70M已有混合调度；Marconi甚至已折叠历史观察。新增关注点是**真实人/工具触发、语义内容改写和原服务cache失效的联合关系是否被保留进目标输入**。当前不能证明这一关系在Qwen同语义输入中形成区别于已有工作的新资源残余，故不列推荐主问题。

自我反向挑战：若exact-token依赖回放加当前最强合法缓存/调度后，差异完全由请求组成、原服务TTL、工具等待或GPU外排队解释，则该问题结束；若仅需修正导出/计费口径，归测量/软件；若必须改prompt、截断、压缩、强制输出长度才能制造收益，取消同任务性能声明。这并不要求source阶段先测出硬件上界，只要求新问题确有可资格的自然对象。

## 7. 条件式最小后续（仅设计，未启动C/native）

完整字段见[QUESTION_CARDS.json](QUESTION_CARDS.json)。第一步应是**CPU输入资格，先于任何GPU**：另获小样本数据授权后，从官方含内容会话冻结少量探索bank，保留许可、repo/task、session/user-request/step、model-visible prompt、实际输出token与tool DAG；先核隐藏模板、缓存读/新内容、上下文改写位置及时间缺项。不能为本轮补材料而接受协议或下载全库，也不能扫描本机用户历史。

- **自然基准**：同一完整Qwen3.5-4B、同template/dtype/state语义、同请求内容；仅把来源清楚的真实会话作为主体。会话外部起点、内部response-dependent就绪均固定定义，不用合成热点/复制prompt。原始提供方日志重tokenize后应标“新目标部署”，不能仍称原模型生产回放。
- **诊断与相反预测**：若保留/恢复状态与重复prefill为主，用户恢复边界应呈可解释准备wall与容量响应；若主要是provider计费缓存、工具等待、CPU排队或长KV必要attention，则校正输入/依赖后差异应消失或改变归因。同ledger的exact-token和shape replay只诊断测量失真，不称硬件加速。GPU-ready、状态准备、必要prefill/decode、queue与工具wall分别记录，不能把并行stage时间相加。
- **强软件**：当前固定版本兼容的vLLM/SGLang prefix caching、chunked prefill、graph；如比较SegLen/Marconi必须先核fork与模型/状态接口。不得把2024年“无hybrid缓存”句子当当前事实；XPerf的token enforcement也须逐项证明目标兼容，不能默认支持。
- **质量/SLO**：来源没有可继承的业务阈值。未来在选择结果前冻结TTFT/ITL/job阈值；没有合法业务SLO就只报曲线，不报生产goodput。强制旧输出是性能回放，必须另用同模型自由生成及原测试核任务质量，不能把原Claude/GPT输出当Qwen质量证明。全部失败、timeout、超context和未完成任务保留分母。
- **独立验证**：未参与选参的用户/repo会话，另用SWE-bench Verified官方真实issue任务核质量并检查实例/repo重叠；它是不同任务入口，不代表生产到达。当前只列入口，未获payload、未构建benchmark，更未把两个provider分组当独立native验证。
- **资源与停止**：本轮没有GPU资格申请。先做静态容量与样本覆盖；不能凭“4B”断言10916GiB支持全部长context/并发。如确需24/48GiB单卡，另给完整工作集下界及Goal；没有多GPU必要性证据。缺合法原文/model-facing上下文、身份/数值失败、强软件消除新差异、独立验证失败或scope需改变即STOP，不自动迭代新native任务。

## 8. 交付与资源收口

独立sparse worktree/branch/output/tmp，仅新增本W目录四份文件：REPORT、WORKLOAD_EVIDENCE、QUESTION_CARDS、RECEIPT。任务工具串行单CPU worker，继承并确认affinity7（原允许集合0—23），OMP/BLAS、Git pack/index线程1，地址空间上限2GiB；轻量RSS记录见收据，不把主机可用内存或一次snapshot写成进程树连续峰值。

公开材料只有README/源码/API目录、官方模型config/数据卡元数据和2份论文PDF；109累计成功HTTP响应约4.11MB，最终精确值见RECEIPT。没有真实数据集、权重、模型运行栈import、CUDA/JIT/GPU、Profiler、模拟器、安装/构建或清理；源码只AST parse，不执行其GPU/多进程入口。私有快照保留于`.private/`并由本worktree独立excludesFile排除，不删除旧文件或执行git clean/gc/repack/reset。

终态前校验JSON/TSV结构、问题引用、来源Git blob/SHA256、路径白名单和diff检查；只push一次自有branch，单次fetch-back比对commit/tree/四个blob，确认tracked与未忽略untracked均clean后STOP。精确最终Git身份记录私有readback及用户回执，避免RECEIPT commit自引用。未读取、等待或轮询H-A73结果。
