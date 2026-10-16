# Round A73｜从真实主流模型工作量与GPU体系结构约束双向并行Discovery

**日期：2026-10-16；协调：ChatGPT／AI-ARCH Discovery；状态：PREPARED_AWAITING_USER_DISPATCH。** 这不是自动运行指令；只有用户将各Lane对应的固定HEAD及本Goal发送给Codex窗口才授权执行。首轮两个独立Codex；第三个measurement合同设计Lane需等本轮提出具体可区分问题后才考虑，不为保持满并行人为开空任务。

## 0. 背景、Goal identity和科学闭环

科学父提交：`adf6ab9467887f74b0b509c105977128663707a5`（A72四线综合/状态）。本Goal的固定发布HEAD从实际Git提交回执取得并由协调者派发；不要追随moving main。共同只读：
- `docs/ai_workload_research/CURRENT_STATE.md`；`reviews/AI_ARCH_A72_A70_M_AND_FOUR_LANE_DISCOVERY_SYNTHESIS_2026-10-16_V1.md`；
- `docs/ai_workload_research/COORDINATION_PROTOCOL.md`第1—8节；
- `docs/ai_workload_research/AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md`，旧C16/AWMA证据索引只按本题选读；
- A70四线原报告每条的第0、最后结论和最直接近邻即可，不再按83条证据全部重读。此前A70-N/O/P/M均NO_SURVIVOR_IN_SEARCH_SCOPE；这是限定source结果而非原生性能否决。

**本轮的变化不是再找vLLM/SGLang“尚未实现的功能”，而是从真实工作量变化或GPU资源约束出发，再用最强成熟软件否定／保留一个可证伪的问题。** 并行研究“新变量是什么”，而不是让两个Codex分别筛同一份调度代码。

核心原则：主流通用模型优先，真实任务和科学问题先于资产；GPU计算/存储/资源配比/CPU–GPU交接都可成为未来主题，但没有预定Cache/TLB/GreenContext机制。作者论文、源码能力、我们的推导、CPU诊断、native/模拟器、模型估算严格分层。已知软件机制属于约束，不能因为它存在就推该场景无真实GPU残余；反过来，不能以“没人发布wall”就宣布一个新硬件机会。

## 1. 两条相互独立的Codex Lane

| 本轮Lane | 宿主建议 | 独立分支 | 主责 | Git输出目录 |
|---|---|---|---|---|
| **W-A73** | **node109新Codex窗口** | `hrl/aiarch-a73w-mainstream-real-workload-109-v1` | 主流模型真实工作负载/输入与相位变化；可证伪的工作量变量 | `docs/ai_workload_research/discovery/A73_W_REAL_WORKLOAD/` |
| **H-A73** | **174-new新Codex窗口** | `hrl/aiarch-a73h-gpu-architecture-counterfactual-174new-v1` | 已发表GPU体系结构硬件研究的真实实验组与资源反事实；新问题约束 | `docs/ai_workload_research/discovery/A73_H_ARCH_COUNTERFACTUAL/` |

W不能做广泛硬件论文清单；H不去深入调vLLM服务队列优化。两者独立输出且无需互相等待。相同论文只可用于不同论点；不能把两份相同作者实验当成独立验证。对交叉问题仅登记请求协调复核，不改变对方任务。

## 2. 共同轻量资源与安全条件

- **CPU/source/text-only**，无GPU/CUDA初始化/JIT、PyTorch/vLLM/SGLang模型import或实机运行、模拟器、NCU/NSYS/NVBit、训练、权重或真实数据集下载、安装/构建包、删除旧资产或cache、数据条款接受。除GitHub/公开学术文献/官方模型config以及冻结历史文本外，不探索模型存储164。109上不锁GPU，因为本轮完全不接触GPU；不制造伪“无CUDA”证明。
- 每Lane任务工具单CPU worker、进程树RSS目标≤2GiB、新增盘≤128MiB、公开PDF/源文件下载≤64MiB；同机其它项目忙则只使用远端只读接口或合法RESOURCE_DEFERRED。不派生本地计算池/嵌套agent。OMP/BLAS和Git pack/index均1线程，独立worktree、output/tmp、终态release；不改全局Git配置，不对历史worktree执行reset/clean/gc/repack。
- 自发送指令起90分钟内收口，资料足够即提前结束。实现404或访问限制优先查原作者公开替代入口，有限次数后标SOURCE_UNAVAILABLE，不为了论文数量反复重试。CPU绝不为缓存计算完整语料或大量测试输入。SLO/质量/隐私/版权与合法许可需明确，未获取资产时不要声称已建立数据资格。
- 独立branch/worktree/output，**不得写本协调branch、CURRENT_STATE、共同manifest或对方目录**；不得更改AWMA/C16/ISCAS/AI-ARCH历史Goal/STOP。只发布文本、TSV、JSON和少量CPU静态计算结果，不提交论文PDF全文、数据或权重。

## 3. W-A73｜真实通用模型工作负载：从输入而不是已实现机制开始

**唯一问题：当前LLM推理的真实请求、状态复用及相位交错，在已发表论文与强软件结果中究竟有哪些输入分布和质量合同还没有得到可解释的GPU资源评估？**

1. 扫描真正主流的公开真实请求/任务来源（聊天、多轮工具调用/代码代理、长文档推理、必要时通用多模态），只从原论文和数据卡的已披露字段入手；**选择2个最值得检查、且有合法输入入口的实际场景**，不是多列15个模型。优先真实文本/长度/到达/回复对应信息的可复现性；若仅有合成Poisson到达或token长度trace、无真实内容，应如实标明，并记录这会限制什么结论。
2. 把实际模型家族与版本挂接到这些输入场景：如Qwen3 dense、Qwen3.5 hybrid、真正通用VLM中的一个（只在确有该类可合法输入且能区分变量时）；这不是要求全都做。不能以已经下载资产倒推选题。
3. 给每个场景一张**自然工作量变量卡**：上下文长度与已重用前缀、请求并发与到达、pre-decode交错、状态token/专家/视觉负载的自然变化；清楚哪些直接披露、哪些可由元数据构建，哪些必须运行后才知道。业务质量/精度/输出长度与SLO不能自由改变来制造差异；不能随机复制同一图像或让任意prompt变成生产流量。
4. 回到已发表Sarathi、DistServe、DuetServe、Marconi/SegLen、当前vLLM/SGLang等**直接同变量**的2—4组原文实验，核该工作量是否其实已经有公平强后端实测。若新变量只是在旧软件方法中已显式处理且没有更具体可区分条件，按SOFTWARE_NEARBY而不是假提硬件。
5. 提交最多**2个新工作量问题**，每题包括：实际自然输入候选、同模型语义、目标阶段、服务SLO/质量合同、已有控制、最小基准（自然）、诊断对照、与选参集不同的独立验证来源、明确否定结果，以及GPU资源限制的一个竞争解释。允许0，特别注意严禁只把“不同模型/更长上下文”当新变量；它必须改变可解释资源或准备/状态依赖关系。

交付：`REPORT.md`、`WORKLOAD_EVIDENCE.tsv`、`QUESTION_CARDS.json`、`RECEIPT.json`，全都存本Lane目录。每项证据披露模型/数据/许可/具体实验组/平台/precision/控制变量/指标分母、作者声称与我们推断分离、未披露字段。

## 4. H-A73｜GPU体系结构：论文实验组与资源反事实

**唯一问题：面对主流AI模型/真实执行阶段，在成熟软件之后，GPU资源配比、并发服务、工作集组织或资源供给中，有哪些值得通过架构反事实研究的约束？**

1. 范围覆盖2024—2026已发表的**ISCA/MICRO/HPCA/ASPLOS/MLSys/OSDI**等；不只查标题含LLM、也不只查访存，但最终必须与主流通用模型实际推理或训练（含后训练）的具体实验有联系。由论文事实而不是GPU部件名来选资源假说。目标先广看8—12项，再对最直接的**4—6个paper×具体实验组**精审；若原文可靠实验组不足，不为凑数量虚构。
2. 每组核：原模型（名字/scale/真实或作者定制）、输入/请求/训练状态来源、平台/GPU代际、算法与强软件、改变的硬件资源、如何控制变量、原生GPU/局部kernel/仿真/估算、作者可复算的幅度、完整应用占比、前人最近邻；没披露明确写未披露。训练与推理数字禁止混合。
3. 明确区分容量不足、带宽不足、服务并发不足、片上结构、执行粒度、设备间协同、CPU—GPU路径与模拟器模型误配；不能因为一个资源敏感就默认扩大它一定产生app speedup。尤其旧C16模拟器/原生定标仅能在适用配置内用作先验，不能外推H100/Blackwell。
4. 回查A70的四个0究竟排除了什么**同质机制**，哪些GPU资源变量根本未在相同科学对象验证；不能以“DuetServe已动态SM调配”推出所有资源配比、不同设备/模型/相位均已无问题。引用作者具体图表/平台，不拿摘要最高收益做我们的权威。
5. 只推荐至多**2个可以轻→重验证的体系结构问题**：先界定自然任务/强软件、两个相反预测，一个最小CPU或本机原生诊断、再到受控模拟器资源反事实/holdout/PPA的资格条件；若本质只是合理重排软件，明确认定软件机会。当前不发布任何模拟器或native执行Goal。

交付：`REPORT.md`、`PAPER_GROUPS.tsv`、`ARCH_QUESTION_CARDS.json`、`RECEIPT.json`，独立于W输出。

## 5. 终态、自审和停止

每Lane可选终态`SOURCE_QUESTION_READY_FOR_CROSS_REVIEW`（有范围的问题及最小可证伪probe设计，不代表GPU获准）、`NO_SURVIVOR_IN_SEARCH_SCOPE`、`SOURCE_INCOMPLETE`、`RESOURCE_DEFERRED`。禁止使用`HARDWARE_HEADROOM_PROVEN`或`GPU_NEGATIVE_MEASURED`，因为本轮没有任何native。审稿自检必须反向挑战自己最推荐的问题：是否仅换模型名？软件最强配置是否实际兼容？是否需要真实自然输入？可否在一次小实验明确归入软件/硬件竞争解释？预计资源是否超出现有平台而必须另审？若缺条件，标为PARKED而不是强推GPU。

正常工程入口/路径问题有界solve-and-continue；若需下载权重、新科学语义、重型执行、升级CUDA/依赖、更改硬预算等立即STOP。未取得第三方完整PDF时保留具体缺口和可核的HTML源，不以摘要推全部实验组。

Push一次自有branch，fetch-back exact commit/tree/四个blob SHA并确认无本Lanetracked未提交改动，报告成功/失败及真实资源收据，然后STOP。不要轮询另一Lane，不能自动开始GPU probe。

## 6. 之后的协调闭环

ChatGPT收到W或H任一结果就立即独审并交叉回查A70旧近邻，不等所有报告才开始。两条问题卡相遇时由ChatGPT只在协调分支综合，**不合并执行分支HEAD**。

如果有1—2个真正可证伪的新变量，接下来的Measurement-first（临时称`C-A73`）用其真实数据、模型与最佳合法软件后端反推最小native eligibility/资源预算（可以需要比4080更大的设备，但须证明必要性）。这时才为C单独写Goal，先CPU静态核资格，用户另行授权任何GPU/模型/下载。若W/H均为0，先讨论新的负载阶段/模型选择，不能再循环四个并行源码搜索。

**本文件只是CPU/source两Lane的准备Goal；没有自动启动任何新Codex、GPU、模拟器、下载或其它项目任务。**
