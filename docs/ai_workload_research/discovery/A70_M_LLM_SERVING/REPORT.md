# Round A70｜M-A70 通用LLM长上下文与Prefill/Decode混合Discovery

执行者：Codex Lane M / node109；日期：2026-10-16。固定启动`8f24af162ba37b4fa37f7a18d89b0fdb62697942`，科研基线`10f3a51ee39884bcec3d3180e81cc405872cccb1`。

**终态：NO_SURVIVOR_IN_SEARCH_SCOPE；推荐主候选0、备选0。** 本轮核查范围内没有形成足以晋升native的新剩余问题：普通分块混合、算子级重叠、长KV感知的动态单GPU分离都有直接软件近邻；当前运行时也继续补齐图与异步调度路径。未实测的软件剩余成本保持UNKNOWN，本结论不将LLM全域判为无空间，不以0候选伪装native负结果。

已完成Goal指定第0—4节、第5节M-A70、第9—10节，读科研基线CURRENT_STATE、COORDINATION_PROTOCOL1—8及证据索引相关项，回到C16固定原报告。独立sparse worktree/output/tmp；只写本M前缀。未读取其他Lane结果、等待或轮询其进展，不接管hybrid内部状态、MoE专家重排或视觉链。

## 1. 主流对象与判别边界

选定常规完整注意力`Qwen/Qwen3-8B@b968826d9c46dd6066d109eabc6255188de91218`配置作代表性与容量核对：36层、GQA8KVheads、head_dim128、无sliding window，官方BF16参数元数据8,190,735,360个。它是完整真实模型；本轮只有公开配置/文献，无权重、tokenizer运行或模型资格。

**并发请求、同一混合batch、同一GPU上同时执行的kernel，是三个不同事实。**

- 服务层：到达→admission/排队→scheduler选择；TTFT含排队，ITL也可能含未被调度的等待。变更chunk/token预算、请求排序、准入率就能改指标，不说明GPU同执行资源争用。
- 执行路径：同一batch的Prefill/Decode可通过统一forward执行不同attention路径，GEMM形状、padding、Graph模式也可能改变。这些是算法工作/软件执行成本；相同token数不保证相同attention工作。
- 真并发：只有证明P/D kernel时间实际重叠，才讨论同时竞争SM、带宽或其他共享资源。SM划分不等于带宽完全隔离。CPU调度与GPU重叠也不是P/D kernel同时执行。

统一指标应分别报告：`TTFT_r=t_first-arrival`；`ITL_i=t_(i+1)-t_i`；`TPOT_r=(t_last-t_first)/(Nout-1)`（Nout>1）；联合goodput为同一观测窗口满足预冻结TTFT和TPOT条件的已完成请求数/wall。排队、超时、拒绝、未完成请求和GPU数另报。按token汇总的尾ITL、按请求均值的TPOT、input+output tokens/s与requests/s不能互换。

## 2. 直接近邻与反证

以下只概括筛选意义，精确实验组/分母/未披露项见[EVIDENCE.tsv](EVIDENCE.tsv)，P01—P08。

| 原始工作 | 承载判断的内容 | 本轮处理 |
|---|---|---|
| Sarathi-Serve /OSDI24 | 分块与混合共同改善容量/尾TBT；Table4分开消融 | 分块混合本身已有成熟软件能力 |
| DistServe /OSDI24 | 按TTFT/TPOT与GPU成本进行跨GPU阶段部署 | 不是单4080资源竞争证据；其LongBench受OPT上下文上限截断 |
| NanoFlow /OSDI25 | 混合dense批次、算子级多stream/nano-batch与CPU异步；完整服务资源瓶颈取决于运行区间 | 简单“Prefill计算/Decode访存互补所以双流”不构成新题 |
| Nexus /arXiv2507.06608v5 | 直接研究长KV带宽相互影响和动态SM分配；单L20与双L20范围分开 | 最贴近的长KV竞争假说已经被提出并有作者实验；未在本机复验 |
| DuetServe /ICML26作者PDF | Qwen3-8B/14B、attention-aware模型、按需时空复用；CPU lookahead dispatch | 同预算不同上下文与按需SM复用不应再作为本项目新机制 |

各工作请求长度来自不同数据/长度trace，常用生成的Poisson到达；不能称已回放原生产到达。作者的dtype、模型精确revision、真实文本质量与尾goodput披露程度不同，缺项按NOT_DISCLOSED保留。DuetServe主要报告mean TTFT/TBT和完成req/s，不能凭此声称验证了P99或联合SLO goodput；这是复核限制，不自动生成一个硬件问题。NanoFlow的主组8xA100及DistServe多GPU收益不移植成4080预测。

### 当前软件源码复核

vLLM固定`fa75d3456d60a5ffe923818c4b495295675b38e1`，SGLang固定`9d394dfbd755759d3add89cfd0bc86d59b31f78c`。GitHub API另看到vLLM最新release tag为v0.31.0；未把该tag和main SHA当同一身份。

- vLLM Scheduler已有token/input预算、long-prefill cap及可选adaptive fair-share分支；前缀cache字段默认True，分块和async配置可用。字段和能力不证明部署最终默认、最优参数或成本为零。[S01/S04]
- V1 GPUModelRunner的batch descriptor与uniform_decode进入Graph dispatcher，选择FULL、PIECEWISE或NONE；要记录真实选中模式，不拿`enable_graph=True`字串当实际覆盖。[S02]
- 当前FlashAttention源码声明FA3/FA4为`AttentionCGSupport.ALWAYS`，其它FA路径为UNIFORM_BATCH。DuetServe旧实现描述“Prefill不能同样capture”不能作为当前所有后端缺口。也不反向声称任何hardware/shape都已FULL命中；本轮没有选后端或运行模型。[S03]
- SGLang存在mixed-chunk开关和CPU/GPU overlap event loop；2025论文中的SGLang默认模式不能替代今天的实际强路径。[S05]

未安装运行时、不import运行栈，没有测得这些能力在109的实际成本。直接近邻的artifact精确实现若未核实，保留缺口；不凭README最高倍数补造完整配置。

## 3. 旧C16证据究竟覆盖什么

[C01—C04]均从固定Git文本只读核对，未访问164、模型盘、trace或执行旧代码。

- Stage A MP02只形成合法B1 Graph/非Graph同点响应，MP03 B4缺合法formal配对；四问仍QUESTION_INCOMPLETE。这是观测/身份边界，不是“LLM没问题”。
- FFN V2在原分离AutoAWQ的D0—D3中双流整段74.215919→81.433918ms，为负且竞争归因不唯一；它控制兄弟投影的执行组织，没有控制真实请求到达、长KV、Prefill/Decode混合及联合SLO。
- merged gate/up、grouped Split-K属于必须保留的软件反证；不能靠恢复分离/弱映射制造增量，也不能把跨后端数值STOP当速度排名。

A70-M的新变量是请求/批次相位构成及已有KV长度，和旧B1 FFN不重复；但新的变量本身仍须通过当前外部近邻反证，不能因为旧C16没测就自动立项。C16/AWMA与本轮无权限继承。

## 4. 可复算的工作量/容量核查（DERIVED）

对上述Qwen3-8B，BF16 KV/token=`2×36×8×128×2=147456B=144KiB`。两份32768-token上下文仅KV为9GiB，加官方参数元数据的BF16 payload约15.256433GiB，总计24.256433GiB，尚未计workspace/Graph pool/分页padding。单4080不能作为该范围的等价平台；不以降精度、任意缩维或减少并发来伪造代表性。

同8192个新token，8×1024与1×8192的标准因果attention pair数分别4,198,400与33,558,528，比例7.99317。它只说明token预算不固定数学工作；不是新增DRAM请求、latency或GPU带宽实测。DuetServe已直接处理attention感知，因此该算式不是新的发现机制。

## 5. 筛选结果：为何CANDIDATES为空

| 筛过的问题 | 最强反证/缺口 | 处理 |
|---|---|---|
| 新增分块Prefill与Decode混合 | Sarathi及当前vLLM/SGLang已有实现 | 泛化能力已被软件覆盖 |
| 两phase分别划SM以躲争用 | Nexus、DuetServe直接研究并实现；NanoFlow另有算子粒度组织 | 不重命名已有机制；零候选 |
| 固定token预算未感知长KV | DuetServe已有attention-aware模型；更长上下文本身不创造独特增量 | 没有已知区别变量可晋升 |
| mixed失去Graph造成新硬件问题 | 当前backend-aware FULL/PIECEWISE能力；实际选中路径/成本未测 | 先是软件/观测问题，不能凭旧描述立硬件题 |
| 只改尾SLO/换新版模型 | 指标/验证范围可改进，但尚无成熟方案后稳定剩余证据 | 证据空白不等于新硬件机会 |

所以终态用NO_SURVIVOR_IN_SEARCH_SCOPE，而非宣称所有P/D延迟已为零或所有部署都被解决。本轮也不将单一artifact缺失放大成整个LLM领域无价值。

## 6. 最小可证伪判别模板：保留方法，不推荐现在执行

问题模板：**在相同合法真实请求与数值质量合同、自然KV状态、强cache/attention/Graph/async路径下，长KV混合的尾延迟变化，是否在分开排队、host dispatch与实际GPU路径之后仍存在不能由算法必需工作和成熟执行组织解释的GPU服务代价？** 这个模板当前没有足够新的区别变量，所以不是第1个候选或待启动native任务。

若将来有独立新证据而另获批准，最小对照应包括：

1. 正式基准为同一完整模型、同一请求集合/到达时间/输出要求及预冻结SLO的成熟混合服务。缓存有效命中、实际chunk/attention/Graph/async模式、排队/拒绝/抢占/重算、host准备分别记录；校准只用探索请求，不能在报告请求上选参。
2. 隔离Prefill、隔离Decode仅作阶段诊断，复用同token/position/合法KV状态，准备/状态复制另账；不能把隔离时删去另一phase或更换到达过程的时间当免费服务上界。若状态/数值不能匹配则取消该诊断，不虚报因果。
3. 按enqueue→schedule→GPU-ready→device-complete分界，统计未插桩正式wall与另行诊断。若只排队/CPU变化、只命中更强Graph/融合路径、只多做必需attention工作，归软件/工作量解释；只有实际kernel重叠并保留状态/质量后才讨论同时竞争。
4. 独立验证保留未选参请求来源；跨模型需另冻结真实同家族完整版本/revision，不能共享探索请求选择结果。长度trace未必含合法真实prompt，原数据许可、tokenizer与文本/输出质量合同必须先补，当前均未接受或下载。

模板估算需单卡至少32GiB做容量canary，48GiB更稳妥（24.256GiB只是weights+两32K KV逻辑下界）；host RAM32GiB、CPU4、下载模型/少量合法输入预算约20GiB、新盘32GiB、GPU锁20分钟可作为以后另案估算，不是当前授权或可行性保证。109当前4080仅16GiB，不能声称承担该BF16并发长KV范围。无候选就不为模板申请设备或部署；当前推荐下一步为协调方抽核本报告与其它独立Lane问题去重，本LaneSTOP，不等待它们结束。

## 7. 本轮执行与交付

实际只做公开论文/配置/固定源码、AST与整数容量计算。公开下载累计和少量文件SHA见[RECEIPT.json](RECEIPT.json)；PDF/版权全文只在独立私有output，Git只提交这四份轻量交付。HuggingFace在109超时后，使用官方网页固定revision读配置；不搜权重镜像。一次baseline SHA终端转录误多字符，通过派发HEAD的真实parent修正，未改科学起点。

没有GPU/CUDA/JIT、模型运行栈import、权重或数据集下载、安装、实际服务请求、Profiler、模拟器、164访问、模型盘扫描或清理。读合同后工具计算worker1、affinity0、OMP/BLAS/Git线程1；不重绑其他任务。启动固定分支fetch在完整阅读合同前曾设pack/index2及affinity0,2，实际并发未测，不能声明全会话严格单线程资格；该配置例外与随后的立即约束已如实入收据。没有子agent、本Lane没有循环或自动后续。

只提交M-A70指定前缀；不改CURRENT_STATE、图谱或共同manifest，不merge其他Lane。最终精确commit/tree与fetch-back四blob/SHA、clean另存私有回读收据，避免提交自引用。**完成后STOP。**
