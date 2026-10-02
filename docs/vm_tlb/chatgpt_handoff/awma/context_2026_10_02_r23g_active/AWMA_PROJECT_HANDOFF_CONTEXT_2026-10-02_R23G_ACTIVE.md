# AWMA项目完整主上下文交接
## 2026-10-02｜Kernel-family评价已更新；R22F1收口；Lane G正在执行R23G

> **用途：交给新的ChatGPT窗口，直接继续当前AWMA研究。先完整阅读第0—4节，再按需读历史、方法与authority索引。**
>
> 当前唯一已授权的GPU任务是**Lane G / node109的R23G真实在线dense/direct-index分派验证**。用户确认G已在执行；本次远端核查时execution branch仍指向启动合同，没有新的完成报告。Lane F的R22F1已审定STOP，Lane E的R22E已审定STOP。**不要重发G启动指令、重跑F1，或恢复R20/R21A旧Goal。**
>
> 本文件是上下文迁移，不是新实验授权。本文汇总：长期目标、当前合同、已经完成的证据、下一步决策、文献/软件支线、节点交互与恢复入口。

## 0. 新窗口先知道的十五件事

1. 正式项目名是**AWMA（AI Workload Memory Analysis）**。C16是历史campaign与兼容路径名，不批量改名、不搬迁accepted数据。最终目标是有实际问题依据、相对最近邻有增量、成本可解释的GPU体系结构机制，不是维护越来越大的测量平台。[H01]
2. 研究已从TLB扩展到AI访存、计算/执行组织、数据准备、状态生命周期。**不预设一定是Cache/TLB瓶颈，也不要求问题必须AI独有。**
3. **Lane名称固定**：E在174-new；F、G是在109上的两个独立Codex窗口。F/G谁使用GPU由最新任务授权决定，G不是永久CPU窗口。
4. 最新实质状态是：**G/R23G ACTIVE（用户确认）；F/R22F1 STOP；E/R22E STOP；174/Accel-Sim无新执行授权。**[S01–S03]
5. G当前任务是`AWMA_R23G_R81_LIVE_DISPATCH_109_V1`，不是旧R22G离线审计，也不是重新研究R102。
6. R23G execution/handoff启动commit均为`f981039d9289368cc32f761d6e5a79f91a775266`，tree为`8008841642b207cdf5258f1aea534aa2c1519d0d`。完整任务见第3节。[S02]
7. 最新状态文件已经宣布R22F1结束、G接棒；但文献README首页仍有Round22时“全部无新授权”的旧句子。**不能仅凭README顶部判断当前状态。**[S01、S04]
8. R21A/OEQ目标族线已STOP。F1同输入replay合计仅快约0.062µs，五组变号；没有稳定正/负局部响应。**不做Donline、不打开旧holdout、不再加profile或换模型/帧挽救。**[S05、S06]
9. R20 active-world线维持CLOSED。always-worklist慢约66.6%是合法负例；最终hybrid因formal B0的exact niter失败没有合法性能结论。两者不能混写。[S12、H02]
10. 当前默认评价已改为四层：**目标族直接响应→计入必要配套工作的净成本→覆盖率/非目标影响→完整operator/应用**。完整应用5%不是所有机制的统一否决门槛。[S07]
11. 局部positive不自动是硬件创新；“强软件可解决”也不等于成果为零。CCE、FP8融合、fast-weight、S128融合保留为软件/局部正结果，原特定硬件动机可同时关闭。[S08]
12. 发现顺序不必等于论文证明顺序。允许“现象→机制”和“文献→小原型→响应→归因”并行；不强制先把瓶颈完全解释完、证明整应用≥5%才准做小原型。[H04、S07]
13. 109只有一张RTX4080/SM89，所有CUDA/JIT/生成/profile均持有`/data/c16/locks/c16_gpu_campaign.lock`。正式GPU实验互斥；CPU分析可以在不干扰测量时并行。
14. 大型资产/raw的长期authority是164；109保留活跃副本；174-new只保留代码、binary、轻量evidence和有限scratch，**不得把本地stage大trace设为前提**。[H03]
15. 用户已授权当前冻结合同内solve-and-continue，不需逐gate再问。小工程修复直接并入，不单独开大Goal；科学身份/数值合同/预算越界才STOP。**这不等于无限授权新机制、重启关闭线或改正在执行的合同。**

## 1. 本次核查范围、证据层次与优先级

### 1.1 本次实际做了什么

2026-10-02通过GitHub connector读取：

- 文献/状态分支的最新HEAD与新增状态文件；
- R23G当前execution branch、`START_HERE.md`和完整Goal；
- R22F1最终决策、运行receipt及执行ref；
- R22G、R22E最终决策；
- 最新kernel-family方法规则、README与历史README快照。

旧R101/R20/R19等详细历史来自本会话已接受报告、此前审查及用户上传的2026-09-29主handoff；**没有在本次重新执行实验、重读全部论文、重算node164全量raw或SSH核进程。**

“335项raw/tensor哈希通过、锁释放、clean worktree”属于执行节点发布的receipt。本次核读receipt，不冒充ChatGPT亲自重跑节点校验。G“正在执行”来自用户最新确认；远端只证明启动合同与分支存在，不证明此刻具体运行到哪一阶段。

### 1.2 怎样处理旧文件与新状态冲突

当前操作权限按**最新用户约束＋最新已授权任务**判断；某项历史结果按其**原冻结合同＋exact execution commit＋raw/receipt**判断。新的解释或方法规则不能改写旧实验是否通过。

同一问题的当前解释优先读：

```text
最新已发布状态/收口文件
  → 对应execution最终报告、关键表与receipt
  → 该轮冻结Goal
  → 本交接的范围化总结
  → 历史handoff/README/旧助手预测
```

本文件第3节概括G合同便于接手；**运行细节以[S02]原Goal为准**。如总结与Goal不一致，保留原合同并登记，不修改正在跑的实验。

### 1.3 当前读取快照

| 对象 | 读取到的commit | 用途 |
|---|---|---|
| 文献/状态分支 | `a5f069109ff3b72fd9754ded48ebdddc145cd89c` | F1收口＋R23G授权；本交接的状态来源 |
| R23G execution | `f981039d9289368cc32f761d6e5a79f91a775266` | 新G任务启动合同；本次未见完成commit |
| R22F1 execution | `bb5c66c674007cc6c9a77549fb0f81528be30056` | F最新已完成结果 |
| R22G execution | `296263043f4949467b33c6c99a695ac5c139104d` | G上一轮CPU审计结果、R23G parent |
| R22E execution | `4fbef16c342fb409918aef7a3922c4f5334761ac` | E上一轮CPU审计结果 |

文献状态分支的tree为`0f4f3c9e0fad95adc99e7709352c9ee902c91c55`。本交接自身的发布commit另见随包`PUBLICATION_RECEIPT.json`；不要混淆文档commit、启动commit和执行结果commit。

## 2. 主线目标、已完成基础与当前组织

### 2.1 长期研究目标

从真实AI执行行为出发，识别某类计算在强软件基线之后仍存在的具体限制；用最小对照/有限原型建立作用路径、必要成本、适用边界和独立验证，最终形成新的体系结构能力或有价值的软件/数据流成果。

不是：下载尽可能多模型；抓所有kernel；反复把Cache/TLB/队列翻倍；一定把某个既有候选救成论文；或把“有metadata/重复/等待”直接等同于硬件瓶颈。

### 2.2 已经有的基础，不重新搭

- 真实模型状态、token、权重、路由、kernel实现与输入hash绑定。
- RTX4080上的Native计时、NSYS/NCU、选择性NVBit、SASS地址路径核验。
- LDGSTS地址与control指令区分，EXECUTED与ZERO_EXECUTION闭合。
- 普通memory-only/C16WARP1与simulator-native SASS trace分开。
- 连续前序＋目标的contextual replay，VM逐访问UID/coverage/exactly-once、terminal drain。
- 164大数据发布、immutable索引、跨节点独立consumer、Git控制面。
- 有范围限制的RTX4080/Ada Accel-Sim基线；不是所有Ada路径的完美复现。
- 文献/源码/实验组证据库及历史正负结果账本。

这些能力可复用，**它们本身不使新的模型、shape、kernel或测量边界自动资格化**。[H01、H03、H04]

### 2.3 当前任务表

| 主体 | 地点 | 当前状态 | 下一件事 |
|---|---|---|---|
| Lane G | node109 | 用户确认正在执行R23G；唯一已授权GPU任务 | 按原Goal到科学终点，发布结果；不重启 |
| Lane F | node109 | R22F1已完成STOP | 无新GPU任务；不继续OEQ Donline |
| Lane E | 174-new | R22E已完成STOP | 无新GPU、模拟或C16诊断 |
| ChatGPT | 当前/新对话 | 研究设计、文献、审阅与交接 | 等G报告后按第4节审，不预判结论 |
| node164 | 长期存储 | models/raw/receipt authority | 既有数据面按需读写，不全盘扫描 |

**F停止并不意味着109空闲：当前GPU使用者已切换成G。**文献支线可做针对性最近邻/写作，不因窗口空闲给E/F凑新任务。

## 3. 当前执行合同：R23G真实在线RULE_U01分派

### 3.1 精确入口与研究问题

```text
Repository: swayhrl/accel-sim-framework
Lane / Node: G / node109
Stage: AWMA_R23G_R81_LIVE_DISPATCH_109_V1
Execution: hrl/awma-r23g-r81-live-dispatch-109-v1
Handoff:   hrl/awma-r23g-r81-live-dispatch-handoff-v1
Starting HEAD: f981039d9289368cc32f761d6e5a79f91a775266
Starting tree: 8008841642b207cdf5258f1aea534aa2c1519d0d
Scientific/audit parent: 296263043f4949467b33c6c99a695ac5c139104d
Original R81 runtime authority: 69e74fe74e18d1f3a71bfac0d097ce49234327a9

必读：
docs/vm_tlb/chatgpt_handoff/awma/r23g_r81_live_dispatch_v1/START_HERE.md
docs/vm_tlb/chatgpt_handoff/awma/r23g_r81_live_dispatch_v1/LANE_G_R23G_R81_LIVE_DISPATCH_109_GOAL.md

结果目录：
docs/vm_tlb/review_packs/AWMA_R23G_R81_LIVE_DISPATCH_109_V1/
```

问题是：**对未参与原R81方案设计的公开结构化生成输入，固定在线策略在计入精确union计算、分派和真实A0/A3切换后，能否保留净head区域收益，同时避免明显完整生成退化？**这是软件执行组织验证，不是硬件试验。[S02、S03]

### 3.2 固定不改的对象

- 沿用R81的Qwen2.5-0.5B model/tokenizer/head身份；具体权重与运行环境以R81/当前receipt为准，不拿R101或OEQ环境替代。
- A0：BF16 vendor dense强基线。
- A3：原固定direct-index ragged实现；不调kernel。
- XGrammar 0.2.8，greedy生成，原persistent scratch lifetime。
- 词表大小151936。
- `RULE_U01`: **`legal_union_fraction < 0.01`时A3，否则A0**。严格小于，等于1%走A0。
- 不扫描阈值、不更换union算法、不训练分类器、不使用事后最快arm。
- 旧C0/C1/H0都已被审过，不能当这轮新holdout。

### 3.3 新公开输入及选择规则

唯一数据源：`korotkov/glaive-function-calling-v2-parsed`的`test` split。它是Glaive Function Calling V2的解析衍生集，**不是独立生产到达分布**。

先冻结dataset repo revision、实际文件SHA和split fingerprint。当前交接时这些执行期字段尚未发布，不能补猜。该数据源不可用则按合同停止，不自行换数据集。

结构性资格：恰好一个函数；`parameters`是object-like JSON schema；首次function-call之前有user消息；可确定性提取首次user消息及函数名称/说明；XGrammar可编译参数schema。

固定prompt：

```text
You may call function <NAME>. <DESCRIPTION>
User request: <FIRST_USER_MESSAGE>
Return only the JSON arguments object for this function.
```

按包含dataset revision、原行号、函数定义、首次user消息和template版本的canonical JSON计算SHA256；按SHA排序，取前24个结构合格记录为qualification pool。

随后**只运行A0语义检查，忽略计时**：按排序依次取前12个在128新token内自然终止、无截断、JSON可解析且满足原schema的记录。不得根据union稀疏率、输出长度或性能改变排序/选择。少于12个则停止。

12个hash冻结后，按顺序每4个构成V0/V1/V2三个B4 batch。不按schema、稀疏度或长度重新分组。这里的baseline正确性筛选是预注册的选择偏差来源，报告时需要披露，不能宣称覆盖整个test split。

### 3.4 唯一在线union实现

当前CPU XGrammar bitmask已在head前产生；不能复用head后ledger中的union数。

固定步骤：

1. 将active request的mask按相同32-bit packed vocabulary bitset解释。
2. NumPy按位OR/reduce到persistent预分配union buffer。
3. 用固定256项uint8查表，对union buffer的byte view做popcount。
4. 除以151936，严格应用RULE_U01。

单列OR、popcount、branch及其合计时间；**这些成本必须实际包括在M1的head边界内**。mask已在CPU，不需要为此新增D2H。不能用Python set或GPU union作为另一候选，也不能只给M1去掉原head内部的重复unpack/materialization。

### 3.5 两个真实运行arm

**B0_STRONG**：原mask路径＋原A0 dense head，不计算union，始终A0。

**M1_RULE_U01**：同mask路径；mask ready后实际计算union、分派，再调用原A0或A3；原head内部解包、grouping、metadata与传输保持；不改backbone。

一个persistent runner内真实执行混合路径，A0/A3 scratch按原合同共存。不能从两条独立轨迹的逐步最小时间拼出“线上hybrid”。

### 3.6 正确性与canary

一个旧R81 fixture仅作工程canary：在线union必须逐步等于parent ledger，arm选择匹配RULE_U01，token/stop语义不变。旧fixture不算新验证数据。

新V0/V1/V2先做非计时B0/M1配对语义资格，要求：每个aligned timestep选中token ID完全相同、stop位置相同、相同生成文本；12个JSON均满足各自schema、无128截断、matcher干净终止。

保留逐步union、A0/A3选择、切换次数、最长连续arm段。它们只是描述，不能反馈调阈值。JSON/schema合法与“答案正确/函数参数符合用户意图”不同，本轮不做task-accuracy声明。

### 3.7 计时与判定

**主边界LIVE_HEAD**：

```text
B0: mask ready → A0结果和选中token提交
M1: mask ready → union OR＋popcount＋分派＋A0/A3结果和选中token提交
```

包括内部解包、A3 grouping/metadata/H2D、A0 mask H2D、compute、候选归约、winner D2H/同步、launch，以及真实arm转换的cache/transition效应。测完不能减去union成本再叫净收益。

**次边界COMPLETE_GENERATION**：沿用R81完整生成wall边界，保留相同prompt/prefill策略、完整受约束续写和matcher/backbone效应。

每个B4 batch：3个paired group，每arm每组2次warmup generation＋5次formal generation，组间交替arm顺序；每次恢复prompt/grammar state，全样本保留。若全部触发完成，总formal计划是90次完整generation run；这是计划数，不是已完成数。

每batch稳定local positive：全部语义合格；三组LIVE_HEAD中位数都偏向M1；中位绝对gap超过较大arm的group-MAD估计3倍。

跨batch晋升：**至少2/3 batch稳定local positive；剩余batch不得稳定local退化**。

完整生成安全门：**若至少两个batch稳定退化超过2%，即使head局部正也判system regression**。2%是该轮安全退化界，不是新的普适晋升门槛。没有统一5%收益要求。[S02]

### 3.8 合法终点与禁止事项

| 终点 | 解释 |
|---|---|
| `R23G_R81_LIVE_DISPATCH_LOCAL_RESPONSE_PRESENT` | 跨batch净LIVE_HEAD规则通过、exact语义成立、无完整生成安全退化；仅软件结果 |
| `R23G_R81_LIVE_DISPATCH_NOT_BENEFICIAL` | union/分派/切换成本消掉收益或发生退化；停止当前R81优化候选，保留旧稀疏状态正结果 |
| `R23G_R81_LIVE_DISPATCH_RESULT_MIXED` | 重复或batch结果不稳定；不换阈值、union算法、batch或输入分组救结果 |
| 输入/union/语义资格失败标签 | 仅说明对应资格未成立，不冒充性能负例 |

禁止新NSYS/NCU/NVBit/SASS、174/Accel-Sim、硬件设计、模型/词表/批大小变化、A3调优、旧H0再当holdout和task-accuracy声明。

## 4. 新窗口接手后应该做什么

### 4.1 首次接手

完整阅读本文第0—4节，并用GitHub connector读取[S01]状态文件与[S02]G Goal。读取G execution ref一次；如果已经出现新结果commit，先读新结果；如果仍为启动commit，记录“尚无新远端结果，用户确认运行中”。

**不要因为开始了新ChatGPT对话，就给G重新下发Goal、reset工作区、重新fetch后覆盖本地变更或重启进程。**本轮也不需要重新审一遍F1是否值得Donline——已有明确收口。

### 4.2 收到G报告时的审查顺序

1. 核exact commit/tree、branch及review-pack；区分reported node closure与ChatGPT实际GitHub核查。
2. 核dataset revision、24→12筛选过程、canonical顺序、V0/V1/V2，确认未按稀疏率或性能换样。
3. 核CPU OR＋LUT popcount确实在head前算，词表尾bits/active-request语义与parent一致，统计不是事后ledger回填。
4. 核B0未被削弱，A3未调优，只有新增union/分派/实际切换；两个arm的必要传输、解包和同步边界公平。
5. 先看token/stop/schema与失败输出，再看净LIVE_HEAD的各组原始值、MAD与各batch方向。
6. 检查完整generation退化门；没有显著退化不等于已经证明所有非目标kernel零副作用。
7. 先给清楚中文结论，再更新状态/软件结果库；不由一个局部positive自动进入硬件。

### 4.3 G之后的条件规划，不是新授权

- 若净局部收益复现：保留固定策略的软件成果，再判断是否有真实未解决的成本、部署集成或独立workload验证价值；不要求为软件positive编造硬件动机。
- 若净收益消失或mixed：按原合同停止，不换第二个union实现/阈值/分组挽救。旧R81稀疏head正结果仍保留为有适用条件的证据。
- 若输入或语义不资格化：区分工程路径与科学实质问题，不用synthetic替代公开验证输入；是否新立题需新设计。
- 文献/问题发现可继续，但先读既有边界账本，避免换名重新试同一已关闭机制。需要新执行时，明确问题、最近邻、输入、测量边界和最小反证，再发布新Goal。

用户期望“后续直接做、不逐阶段再问”，指在批准范围内连续推进及明确的后续准备；**不允许隐式扩大矩阵或违背科学STOP**。本次只做交接，不批准第4.3节任何新节点实验。

## 5. R21A→R22F→R22F1：最新已关闭目标族线

### 5.1 从问题发现到固定实验

Round21最初检查“高效GPU邻居构建之后，双向索引/执行计划是否仍形成动态图准备成本”。源码核查收窄了这个动机：Sobek式双CSR不是所有高效等变模型必需；NequIP官方OpenEquivariance atomic路径可消费任意edge顺序。因此真正执行的问题是：**为deterministic OEQ准备排序/transpose permutation，是否值得相对强atomic路径支付成本？**[S10、H02]

固定模型/输入/代码：

```text
model: nequip.net:mir-group/NequIP-OAM-S:0.1
model package SHA256:
63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa
NequIP: 27d9d2182da918ab7be0017d8300e53278f5e00e
OpenEquivariance: dc9979099c65113adcc016977c5c60974f9ddafb
input repo: mir-group/nequip-tutorial
input commit: 8f90935ba42fd9e03df323cf03428c456d87b881
sitraj.xyz Git blob: baac4e23364d00d29b2410fa60a92ade0cbf35a3
input: 110帧中的第55帧；64 Si；1394有向周期边
numeric: float32，TF32 OFF，energy/forces atol=rtol=5e-5
mode: 同一AOTInductor ASE CUDA编译边界
```

这些几何帧没有被证明是连续物理时间序列；不得从frame次序推邻居重建频率或MD长期摊销。DFT标签是来源信息，不是两个实现等价性的reference。

### 5.2 R21A初轮

execution：`62af34149d45e9862d5a1e255e2a51ca88a3c4c7`。

A0为natural graph＋atomic；Dready为prepared sorted graph＋deterministic。natural graph已按receiver分组，但组内sender不单调；仅生成transpose permutation的最初实现energy过、forces失败。采用固定源码的receiver/sender复合排序、同步重排边和periodic shifts后，恢复原数值合同。两层共享准备结果。

三组完整energy＋force计时：

| 组 | A0 median ms | Dready median ms | 耗时减少 | 3×MAD判据 |
|---|---:|---:|---:|---|
| 0 | 0.591520 | 0.455464 | 23.0011% | 未过，A0离散大 |
| 1 | 0.481776 | 0.459110 | 4.7047% | 通过 |
| 2 | 0.475401 | 0.455085 | 4.2734% | 未过 |

原结论`R21A_RESULT_MIXED_NEEDS_REVIEW`保留。不能删第一组、把5%改成4%或只引用23%。Donline和原四个holdout没有运行。[S08、H02]

### 5.3 R22F分族定位

execution：`df0e8edd009ee1a56ba65b25b319e8a852f74d27`。

新增Aorder＝Dready相同sorted graph＋atomic，用于结构性分离ordering与聚合实现。冻结TP forward、TP force backward、deterministic mandatory aux、non-TP及mixed family；aux计入目标族净成本。

NSYS插桩诊断中的Aorder→Dready：

- forward约节省1.792µs；backward约节省1.616µs；gross合计节省3.392µs。
- 直接TP主kernel只节省约0.529µs，其余gross差主要对应atomic空fixup launch消失。
- deterministic实际fixup增加约30.160µs；净目标族多耗约26.752µs。
- 即使把无法拆分mixed-family优势都计入目标，仍多耗约19.792µs。
- non-target中位节省0.415µs（约0.198%）；最差block仍节省0.385µs，未观察稳定退化。

未插桩完整energy＋force：Aorder→Dready快13.955µs/2.878%，通过该轮噪声规则；A0→Dready中位快14.845µs/3.065%，wall噪声门槛未过；A0→Aorder接近零且mixed。

结论`R22F_R21A_FAMILY_RESULT_MIXED`。**插桩kernel时间和未插桩wall方向不一致，没有完成归因。**不能从Aorder完整差不显著证明sorting永远没有影响，也不能把“额外fixup约30µs”直接当自然执行成本。

### 5.4 R22F1低开销同输入replay（最新已接受）

execution：`bb5c66c674007cc6c9a77549fb0f81528be30056`。

真实frame55 energy→forces捕获两个TP callsite：layer0和layer1各一次forward、一次force backward；X/Y/W、rows/cols、配置和真实upstream gradient均保存hash。同输入atomic/deterministic的forward与所需梯度通过原5e-5合同。

无新profiler；32-replay CUDA-event bundle测量：

| 范围 | Aorder−Dready差值 | 含义 |
|---|---:|---|
| 合计forward | −0.272µs | Dready略慢 |
| 合计backward | +0.334µs | Dready略快 |
| 按真实multiplicity合计 | +0.062µs，约0.029% | 未建立稳定方向 |

五组合计gap（µs）：`−15.4705, +3.2240, +0.0615, −3.8785, +12.7885`；较大arm MAD约7.7315µs，未过原3×MAD门槛。receipt记录160 forward＋160 backward正式bundle，共320项数值检查通过；这不是320个独立模型样本。[S05、S06]

OEQ无可直接调用的exact fixup-only接口，未插桩fixup单独时长仍UNKNOWN。不得用NSYS的30.160µs回填，也不能把不同上下文的三层证据相加：

```text
NSYS profiled family：Dready净TP族约慢26.752µs
真实输入standalone replay：合计方向不稳定
未插桩完整模型ready-graph：Aorder→Dready快13.955µs
```

原助手曾据量级相近怀疑trace/fixup扰动；那只是待检解释，**F1没有证明唯一根因是Nsight**。张量/梯度相同不等于恢复完整模型的缓存、并发和launch上下文。

已接受终点：`R22F1_FAMILY_GAP_UNRESOLVED`。当前操作上R21A/OEQ目标族线STOP，不做Donline、不加样本或profile、不换模型/帧、不打开旧holdout。[S01]

F1 durable路径：

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r22f1_oeq_lowoverhead_replay_109_v1
335 files；115798154 bytes（执行receipt）
manifest SHA256: e3789915157e9b4a1efbeb119a96aecae57732ab0409c2b315acb3cd7d372c52
```

经`hrl174new`作storage/SHA gateway不等于174执行科学计算。详细文件先查pack的`RAW_DATA_INDEX.tsv`，不全盘找tensor。

## 6. R81→R22G：当前R23G的历史依据

### 6.1 R81原始分层结果

execution：`69e74fe74e18d1f3a71bfac0d097ce49234327a9`；`R81_SOFTWARE_OPPORTUNITY_NO_ARCH_CLAIM`。

12个author-crafted请求/B4 fixture，C0/C1为发现、H0当时为内容验证；全部207 timestep保留。合法union中位约96.8%词表，说明不能只挑很稀疏状态讲故事。[H01、S08]

| 状态 | C0 | C1 | H0 |
|---|---:|---:|---:|
| union<1%时A3 head耗时下降 | 53.4% | 45.3% | 44.8% |
| union>50%时A3 head耗时增加 | 27.5% | 7.1% | 6.7% |
| 完整生成变化 | 慢3.62% | 慢0.98% | 快0.73% |

这是真实的适用条件相关的软件结果；不是“局部全部无收益”，也不是“其他状态基本不退化”。最近邻已有XGrammar在线mask、Kestrel indexed head、FlashSampling式融合选择等能力；不能仅以换一个名字主张新硬件。

### 6.2 R22G的CPU-only固定规则账本

execution：`296263043f4949467b33c6c99a695ac5c139104d`；tree `a76e3979d32c586ead67a29feb44bf80156f515d`（执行报告）。

固定RULE_U01、不扫阈值，在matched per-step数据中重算：

| cohort | 未计新增dispatch成本的head-region中位降时 | A3/A0 steps |
|---|---:|---:|
| C0 | 7.17% | 15 / 63 |
| C1 | 4.37% | 9 / 63 |
| H0 | 6.09% | 10 / 47 |

H0有1/7 repetition略负向。逐步`min(A0,A3)`仅标为不可部署best-of oracle；未用cohort median拼造逐步hybrid。[S09、H02]

真正缺口：head前没有已经产生的union fraction；需新CPU union/unique或mask OR/popcount。该统计成本及真实混合轨迹切换效应均未测，不能取零或从A2复合计时推定。

因此R22G STOP为`R22G_R81_DISPATCH_NOT_JUSTIFIED_FROM_EXISTING_EVIDENCE`，**不是证明固定规则净负**。它留下一个可直接测量的成本缺口与唯一未来验证提案；F1结束后，最新状态明确授权了R23G去测这个缺口。[S01]

历史Goal的methodology authority曾出现无效41位字符串；G记录了确定性解析为`fc1351e9e62f2a1aa12c323823e24d30357a8a9d`。以后先检查SHA格式，再结合已知branch、tree、内容确认；不能对任意坏SHA直接截取40位。

## 7. Lane E / R22E：C16与E1复审终点

execution：`4fbef16c342fb409918aef7a3922c4f5334761ac`；CPU-only，无新采集/GPU/模拟。

### 7.1 跨CTA conversion

M64严格转换重复75%、M32 50%属实；强fused kernel已做CTA内unpack/dequant到private shared并供多个warp消费，剩余是跨CTA共享。

旧范围encoded tile约2.3KiB、decoded FP16 8KiB；整个operator encoded约24.94MiB、decoded 96MiB。不能把逻辑重复比例当physical traffic或时间节省，expanded storage、发布、同步、fanout和后续读取都要算。[H05]

R22E明确发现：**没有accepted M32/M64的同输出完整算子有限共享净成本对照**。另一个M256 conversion-removal oracle输出无效且更慢（1.538048 vs 1.270784ms）；correct predecoded arm更快（1.162752ms），但更换表示/kernel并排除了materialization。两者都不能补出缺失的有限共享净性能。[S11]

新family方法仅取消“已绑定up-projection应用占比1.74%低，所以局部无需研究”作为唯一否决理由；不自动使原反事实合格，不自动恢复dequant cache。

### 7.2 E1形状/实现轴

已存在18点完整算子矩阵。R22E重新记录同activation下：

| operator/shape | AWQ ms | RAW_FP16 ms | 描述 |
|---|---:|---:|---|
| up_proj M1 | 0.088424 | 0.220928 | AWQ较快 |
| up_proj M256 | 0.677573 | 0.362578 | 方向翻转 |
| down_proj M1 | 0.111420 | 0.222373 | AWQ较快 |
| down_proj M256 | 0.500564 | 0.392341 | 方向翻转 |

q_proj M1近似持平且噪声较大，M256 AWQ较慢。M1023→1024时AWQ从quantized GEMM＋reduction转成dequantize＋matmul。up-proj有NCU bytes，但不是tensor归属或时间分解；down-proj clean-point NCU缺失。[S11]

RAW/AWQ同时改变权重、量化/布局、dequant融合、split-K scratch/reduction与kernel，**不能称纯bitwidth因果**。当前没有一个干净的新有限干预提案，所以`R22E_EXISTING_EVIDENCE_DOES_NOT_JUSTIFY_NEW_DIAGNOSTIC`，E继续STOP。

## 8. 已有软件/局部正结果：不要因为硬件线关闭而丢掉

| 工作 | 已接受局部结果 | 解释边界/当前状态 |
|---|---|---|
| CCE zero-init removal | 同轮C0 8.171520→C1 7.202816ms，减少11.85% | 原dC全量zero-fill消失；first-contributor重用66472B锁数组，all-ignore保原zero语义；完整训练step未测 |
| R19F2 FP8软件融合 | 完整MLP S1 0.187174→S2 0.154272ms；ready D0 0.148045ms | exact FP8数据/inverse scale/consumer；不是stock TE能力；S2-D0残差4.04%且组间不稳定 |
| R19 fast-weight | 2.079488→1.592320ms，减少23.43% | 第三方Gemma-3-1B TTT artifact、五层两chunk局部；consumer state-read残差未观测，非完整TTT请求 |
| R101 S128融合 | F128 0.493408 vs K128 0.623488ms，减少20.86%；layer12约20.09% | 同有限五步tile-map但改变指令、CTA/kernel分解及访存；非纯cache收益 |
| R81稀疏合法词表 | head-region减少44.8%–53.4% | 宽状态退化，完整生成未稳定；当前仅R23G检验在线分派 |

对应execution：

```text
CCE: ec1ccad7bbcead8853cd97840a2007d96f325aa3
FP8 F1: 7375abd8e86c1523c1873913e8fffccf0b4e3a96
FP8 F2: 7b87638e74164cdffc21c0d280324bcb048b6a8d
fast-weight: 4ef10349b198d6989ab666309fbe95ce8993bc56
R101 Native: cfbe6503585fa1b10d979db5d26fb9be3a80e563
```

CCE first-contributor让zero-fill消失，不能把全部0.968704ms配对差逐一归于旧0.751779ms memset；锁/执行组织也变化。FP8原BF16↔FP8 allclose失败没有被表示匹配后的新合同改写。fast-weight模型是PUBLIC_REPRODUCTION_ARTIFACT，不是官方paper checkpoint。[H02、H06、S08]

Round22还从FP8 projection表重算S1→S2三组降时约18.55%–24.00%；融合后S2→D0约−0.66%、4.89%、4.56%，没有稳定“总模型稀释掉的强硬件残差”。这些是回顾性复算，不是新独立验证。

软件positive可进入写作、经验库和强基线；未来只有出现独立新限制和明确成本优势，才讨论新硬件，不为每个positive强行硬件化。

## 9. R101的后续历史：从大Oracle到Native不支持，不能停在09-29快照

### 9.1 输入与旧基础

真实Qwen2.5-0.5B首步梯度导出的HiMuon microstate，不是随机矩阵或长期训练状态。固定五轮Newton–Schulz：XXT→BA→BMM-add，系数`(3.4445,-4.7750,2.0315)`；S128与L512是不同tile-local映射，不能当等价shape互换。[H01]

FULL5 producer为`bb902283b7ce9e1902b460383fbd3e0bedbd884d`，18 kernel＝3 normalization＋5×3算术；L512有44 tile。A/B/X0/X1各22MiB；同源lifetime与地址sidecar保留。

M1 FULL5：writeback降低92.09%，cycles仅降低0.5027%；B0 15,374,861、M1 15,297,575 cycles。只关闭该有限retention/dead-drop性能方案，不证明所有访存服务无关。不要重跑FULL5、扫M1 cache容量或优先级。

### 9.2 CONTEXT2服务位置诊断链

同源六kernel CONTEXT2；第一轮恢复context，第二轮measured ROI；context精确恢复2,976,829 cycles。

| arm | ROI cycles | 相对B0周期减少 | 支持范围 |
|---|---:|---:|---|
| B0 | 2,985,319 | — | 冻结模拟ROI |
| O2理想pre-L1服务 | 1,130,670 | 62.1257% | 无界队列/服务的model-relative headroom |
| P0 finite pre-L1 | 1,130,670 | 62.1257% | scheduled=1/ready=16仍保持响应，排除该无限队列容量依赖 |
| P1 post-L1 | 2,737,282 | 8.3086% | 正常L1 lookup/reservation/merge/miss/fill/MSHR-release保留 |
| S1 partition-side | 2,963,656 | 0.7257% | 有效transient服务大降，周期弱响应 |

关键execution：

```text
O2: 97d5be184b7f7f35c06d3ee111a8c5ba6efad896
R101R3 S1: 364998600d9f49953752fbec982233d5b8c5895a
R101R4 P0/P1: d96a64da8311c1bdee8f23f3d83ce665395060d1
R101R5 Native: 48f5bf24a2136521e272ed4d1da18ba5aa5f798e
```

S1闭合29,937,568个事务、L2 misses/DRAM reads降至3209，仍仅0.7257%，原5% gate下没有实现H1。P0/P1后把响应定位到L1 miss之后、S1位置之前/跨越的downstream path；**不能相减成可加时间组成，不能进一步唯一归因于ICNT/L2/cache latency**。

R4首次P1 generic hook缺L1-instance gate，修成`m_level==L1_GPU_CACHE`后完整重资格化。后处理移除非预注册检查的recovery不等于改raw或放宽性能阈值；失败版本与receipt保留。[H02]

### 9.3 Native检查终点

R101R5对冻结第二轮L512的三个exact kernel补NCU：math-pipe throttle约51%–71%，LG低于1%，long-scoreboard PC样本不能归因于ordinary LDG/ST post-L1服务。

最终`NATIVE_POST_L1_DOWNSTREAM_SUPPORT_NOT_OBSERVED`：没有在RTX4080上观察到相匹配主导压力；**不推翻模拟内响应，也不等于真实GPU完全没有访存成本**。没有有限硬件收益或完整训练收益成立。

09-29交接中的“下一步设计有限服务”已经被R3/R4/R5执行覆盖，不再恢复。S128约20%软件融合结果仍保留，不能由L512 Native不支持反向抹除。

## 10. R20 active-world全过程：保持关闭

真实G1 hfield/shuffle_dance，B1024，固定MuJoCo Warp source `3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`，sparse Newton/pyramidal/conditional graph，outer10/line-search20，tolerance不改。世界active集合收缩真实，旧窗口平均active-slot比例0.3733只是结构事实，不是可实现speedup。

| 阶段 | 主要结果 | execution |
|---|---|---|
| R20 | 完整32步同输入B0轨迹分叉，contact集合相同但顺序不同；无S1 | `50f8608898ec37a7e265bf3761d7bb236cdb3e88` |
| R20R1 | 冻结solver entry；t152/world413的LS位一次变化触发exact gate | `8a1a8baf6ac5b6eff0c32f04b572eb1d34873d24` |
| R20R2 | LS flip在固定入口属diagnostic threshold差异；最终有效输出合格 | `e645b5e011c18f1e44b7a1509fb55c49486adff5` |
| R20R3 | 四入口B0过；NSYS未产报告，不能按规则选stage | `fa292a11dbc196b65ebe1f3a67f39a7837046995` |
| R20R3P1 | profiler修复，选增量梯度；304-worker S1遇历史gradient包络失败，fresh B0自身也失败 | `53837e8366f0d96a636c89365b782aa411e7bc63` |
| R20R3P2 | 新source-semantic stop合同32次B0过、负例有判别力；固定S1完整solver慢约66.6% | `3f4e3409ad629d5302a54e9c3a0f356bdc190456` |
| R20R4 | CPU-only按iteration拆分闭合；late≤304的H+Cholesky零成本O2估计11.77% | `769ea5f3592976b2035beb76947b0d934d6efabf` |
| R20R5 | late-only hybrid工程与四入口正确性过；第91个formal的B0 exact niter失败，未形成合法aggregate | `57ffbd4a8c8fedb1f050913bd2801c76eb1a4e7c` |

原always-worklist每个304 worker在active>304时循环处理多个world，结构上有跨world串行；未profile S1，不能说它解释全部66.6%退化。

最终hybrid按device nsolving：>304走baseline且不建list，≤304才建list并用304-worker；nested conditional可实现。但第三组t136 B0 formal首个样本违反exact niter，前90个合格不满足原120全合格协议；失败数组未保留，world和具体原因未知。不能删失败、重新拼完整三组、或推断H1数值错误。

**R20关闭是预算/候选与科学合同终点，不是整个active-world领域无机会的证明。**不改outer-niter合同重跑，不扫阈值/worker，不重新打开holdout；跨run O2=11.77%不是hybrid实测收益。

收口authority：`0c6cda2f680fa93ed5ea7d4b098eef5044a8a0c4`，路径：
`docs/vm_tlb/chatgpt_handoff/awma/r20r5_hybrid_native_v1/STATUS_AFTER_R20R5_FINAL_CLOSURE.md`。[S12]

## 11. 更早探索与基础资格：历史不是待执行清单

### 11.1 平台与translation基线

冻结名称与关键authority：[H01]

```text
AWMA_RTX4080_SIM_BASELINE_V1
AWMA_RTX4080_SIM_BASELINE_V1_PROMOTED_WITH_SCOPE
RTX4080_ADA_ACCELSIM_BASE_V1
baseline authority: 8d1f14a32f5538660d74da86ccb03a2c504c5735
GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH=1
GPGPUSIM_READY_APPLICATION_V2=0
```

早期accessq_back串行launch放大hit-path/HOL敏感性，V1修正；V2/V2R1 READY application没有额外Native alignment收益。VM逐访问、UID、权限、physical mapping、coverage与controller quiescence修复已完成，不能退回旧默认实现。

`10/80`是模型TLB查询延迟，不是RTX4080已知硬件参数；`10/80→0/80`只去一部分查询成本，不是所有translation优化上界。完整理想翻译仍需保持数据物理地址与访问语义。

旧RTX3070/SM86衍生配置固定窗口内“多执行指令百分比”不是当前4080完整kernel耗时减少。SM89 opcode映射资格也不是完整Ada硬件支持。校准、独立验证、机制评估集要分开；不为做成曲线而调当前workload下的模拟器。[H01、H04]

### 11.2 早期问题索引与限制

| 问题 | 结果及边界 | 关键authority |
|---|---|---|
| PREL1同页合并 | 部分局部有效；classic intra-warp能力覆盖主要收益，不能换名救新颖性 | `9efe8236e0c6338addfef5480e1da91bffb504eb` |
| resident translation收口 | 当前已测resident场景未形成新的translation问题；不是整个AI翻译领域否定 | `3e29f234a971e2be68076eef22a05391cf9e4b67` |
| resource map | 多项资源干预未留下actionable新问题；Tensor/SFU参数耦合失败不是科学negative | `d116e64b6c2d7faab1babc56c966ff4c1d628904` |
| model-derived UVM | Llama KV容量迁移边界、prefetch更慢；OLMoE可驻留；fault/TLB/PPN等未可观测 | `f25312635dae33342d6540be92467c6ed67fdb0d` |
| P1 batch-invariant reduction | fixed-split-256保持bitwise，指定范围成本约+0.887%；已有软件接近 | `ce5918d837b76e95ad4000c50bbe1465707a2ebd` |
| P2 online selector | ONLINE→READY差主要由selector计算解释；必要评分不能叫发布浪费 | 同上 |
| R51 lm_head交接 | V1 bitwise失败；V2 greedy通过但交接增量不足且chunking有开销 | `db2000f7222030282f788bd009243ab1a43ed867`（V2） |
| R52 invalidation | 没有真实在线失效authority；synthetic cancel不可冒充真实证据 | `R52_NO_REAL_INVALIDATION_AUTHORITY` |
| R53 diffusion workset | 已实际执行！省行数改变token/cache轨迹；safe bucket恢复轨迹后合法减工0 | `843ad43ad33153bf73a0e51aed6d8ac309356cae` |
| R54 recurrent checkpoint | greedy资格；主要开销在host/runtime，GPU copy不能解释总差；top2不完全同序 | `d6ef29505de75985181afc74dffc3cf1b652afc2` |
| R82 layout | C1约慢0.239%且低于噪声；C2无合法warp-only方案；不是所有layout已最优 | `385f38271466a01e7f9cedfe638355195057b7c8` |
| R102真实更新链 | V1/V2未取得合格相邻真实权重链，CUDA0；输入缺口不是GPU负例 | `c0839c11198e88ea0d3d6f7e62a4a8f4d117b82a`（V2） |
| VLA RTC/VJP | 真实SmolVLA反向执行成立；buffer复用完整chunk无material收益；必要math与state成本未分离 | `f8e6e2598e51dae115008a52c9a80110cdf14d83` |
| R17 CAGRA | V1质量未过；R1质量/强软件基线建立，未定位GPU-local残差 | `29ecc6e5e37005046b1a563c830bed9ae58af656` |
| R19 IBP | dense stage/copy真实；P1/P2/P3改变训练层、GEMM拆分或前后向，因果对照未资格化 | `a758be1017f35caa55dda6ad529d1b6c5f141553` |

R17“Q1约0.215ms小于整个Q32约0.531ms”不证明无Q1优化空间，不能除以32冒充单query延迟。V1 recall gate失败也不是性能负例。R102公开bucket有anchor/delta不等于有base hash、target hash和wrong-base拒绝闭环。IBP没有合法D1不等于dense materialization成本为零。[S10、H01、H02]

### 11.3 C16三lineage与Problem Discovery V2

Q30、DeepSeek、OLMoE积累了真实路由/输入、指定expert/kernel、243 static GLOBAL-path及memory trace证据。工程loader/state/materializer可以复用，科学target、kernel、地址与路由结果不可跨模型继承。

DeepSeek/OLMoE某些gemvx目标有same-CTA/same-warp/same-static-MREF两次访问，exact BF16逻辑字节重复50%；两者K分别1408/1024。**50%不是性能headroom**，L1/L2吸收、load instruction、scoreboard和上下文权重未知。

C16 V2终态：`9759c08f3bb6e9abd134591007a27ed5bf8c23b1`，入口：
`docs/vm_tlb/chatgpt_handoff/c16/C16_PROBLEM_DISCOVERY_V2_CURRENT_STATE.md`。

此前已关闭selected-shard继续找故事的路线；不能从独立static-MREF replay拼whole-model关键路径、跨expert chronology或真实TLB stall。Round22只是重新区分未知/低coverage/软件已解决，没有重开C16大型采集。**R22E完成后仍没有新的C16诊断授权。**[H07、S11]

## 12. 最新方法规则：必须继承，不退回“整应用5%一票否决”

### 12.1 四层评价与两个独立决策

对每个机制/软件候选，同时记录：

1. **直接目标族**：全部同语义工作集合的响应，不只挑一个最快kernel。
2. **净族成本**：排序、conversion、初始化、list、fixup、同步、metadata、输出提交全部计入；共享准备只计一次，说明摊销范围。
3. **覆盖率/非目标影响**：baseline时间权重、调用频率、其他族中位/最差退化；未测就UNKNOWN。
4. **完整operator/应用**：实际完成时间、系统价值和对局部模型的约束。

“局部有效”和“当前完整应用值得追加多少工程”分别判。局部净收益稳定且其他部分中性，即使应用<5%也能保留；反之，即使完整应用>5%，也不能跳过身份、配套成本和归因。[S07]

family key按研究需要包含：phase×语义operator×implementation×shape/regime×dtype×forward/backward×必要context。相同函数/shape不保证入口cache状态相同；不同模型名不保证有不同kernel行为。fusion改变kernel数时按相同语义工作集合比较。

### 12.2 不能混用的证据与分母

- 逻辑重复/张量bytes不等于物理traffic、cache miss或时间。
- 静态SASS count不等于dynamic warp instruction，更不等于active-lane总事件。
- NSYS kernel duration sum不等于应用wall；并发下还会重叠。
- profile可能扰动小kernel/launch；profiled族时间、未插桩完整时间、standalone replay不可直接相加。
- NCU replay/cache-control条件需绑定；不把清data cache声称为清全部TLB。
- 固定cycle窗口指令进度变化与完整kernel时间变化不同。
- 理想ready/服务干预通常只是限定假设的诊断，不自动是普适数学上界；不同干预差值不是可加时间组成。
- 保存tensor/gradient与保存cache/TLB/PWC状态不是一回事。

简单无重叠模型下，目标原占比f、目标耗时减少g、非目标增加r、共享额外成本占原整体h，则整体耗时减少约为`f*g-(1-f)*r-h`。这是说明量纲的估算，不是替代真实端到端测量。

“目标耗时减少30%”与“目标speedup=1.3x”不同。前者f=15%时理想整体降时4.5%；后者对应整体降时约3.4615%、整体speedup约1.03586x。旧回答中的约3.6%是speedup百分比近似，不能再与耗时减少混用。

### 12.3 数值合同与错误处理

数学等价、同有限步骤、同归约顺序、逐bit相同、近似allclose、同greedy轨迹、JSON合法是不同要求。采用真实应用/作者已有的合理合同，不人为加无人需要的exact限制制造创新；但冻结后不因看到candidate失败就扩大容差。

若fresh B0自己失败，只说明当前基线/合同未资格化，不单独归因candidate。需要修订必须作为新、来源有依据的合同，保留历史FAIL。**新运行第一次失败先保存完整输入引用、输出、首差异、环境与状态，再退出。**

3×MAD是已选工程噪声判据，不是通用显著性检验或某个固定置信水平。重复次数、arm顺序、warmup与门槛在看新结果前冻结，不无限追加到通过；同一次模型内很多call也不是很多独立run。

### 12.4 探索、独立验证与新颖性

允许有限原型作为发现工具；冻结baseline不等于禁止candidate改变明确结构/策略。需要的是声明改了什么、保持什么、计入哪些成本和怎样反证，不是机械要求所有有价值系统优化只能改变一个物理微参数。

回顾性分层标RETROSPECTIVE；被用来调阈值/选样/构造解释的旧holdout不能继续称独立。新验证要选择不同未参与设计的实例，并明确“不同内容/层/shape/模型”代表性强度不同。

软件已解决某个现象不是零成果；硬件新方案还需额外能力、范围、吞吐/能效或成本优势。“前人也做稀疏/确定性”不等于全领域已解决，“换成AI”也不等于创新。无需完整复现多篇论文才准探索，但最近邻相关能力必须比较。

## 13. 文献与写作支线：当前入口与已做范围

### 13.1 存放位置与责任

```text
Repository: swayhrl/accel-sim-framework
Branch: hrl/awma-chatgpt-literature-notes-v1
研究材料根: docs/vm_tlb/literature_notes/awma/
子目录: rounds/ empirical/ problem_cards/ methodology/ plans/
```

由ChatGPT维护文献、固定源码、证据表、勘误、计划和review，不占用GPU。Git中的文献记录不是execution receipt。当前最新状态从`plans/STATUS_AFTER_R22F1_AND_R23G_AUTHORIZATION_2026-10-02.md`进入，不从旧README的“当前任务”恢复。[S01、S04]

### 13.2 已完成轮次导航

| 轮次 | 主要内容 | 当前用途 |
|---|---|---|
| Rounds 01–03 | GPU translation近邻、实验context/负载条目、MPW/Avatar等 | 历史能力基线 |
| Round04 | 数值一致性归约、在线selector、MoE/SSM/线程寄存器 | P1/P2等设计来源，不是新任务 |
| Rounds05–08 | R51/R52交接、R53扩散、R54状态、R81合法词表/R82布局 | 解释已执行问题的研究选择 |
| Rounds09–11 | 编译/通信/稀疏/优化器/压缩/RTC/VJP/CCE等横向阅读 | 问题发现与最近邻库 |
| Rounds12–14 | R101 L2 lifetime/有限机制/服务oracle、L1-L3分级 | 历史R101合同来源 |
| Round15 | R101等横向收口与frontier | 旧候选导航 |
| Round16 | R102、RTC/VJP、CCE两线及旁路 | 三种不同终点，不混成领域negative |
| Round17 | graph search、CAGRA/FlowANN/ALGAS/Jasper等 | 已有强软件/最近邻边界 |
| Round18 | 全面横审、来源登记、60条证据与边界账本、R53勘误 | 不重新造旧问题 |
| Round19执行链 | FP8、fast-weight、IBP | 三方向范围化收口 |
| Round20 | MuJoCo Warp active-world | 已关闭实验的背景 |
| Round21/21A | 几何图准备→OEQ atomic/deterministic；3DGS/Muon/HSTU排雷 | R21A起点，当前已STOP |
| Round22 | 34行历史边界复审、family-first规则、F/G/E设计 | 当前评价方法与R23G前序 |
| R23G | 新公开结构化生成在线分派 | 当前执行，不是已完成文献/结果 |

重要文件（相对文献根）：

```text
rounds/2026-10-02_ROUND_22_RETROSPECTIVE_KERNEL_FAMILY_AUDIT.md
empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv
methodology/KERNEL_FAMILY_FIRST_REVIEW_V1.md
empirical/R21A_RECOMPUTED_GROUP_TIMING.tsv
empirical/R19F2_PROJECTION_RECOMPUTED.tsv
plans/2026-10-02_POST_ROUND22_RESEARCH_PLAN_V1.md
plans/STATUS_POST_ROUND22_EXECUTION_AUTHORIZED_2026-10-02.md
plans/STATUS_AFTER_R22_FGE_RESULTS_AND_R22F1_AUTHORIZATION_2026-10-02.md
plans/STATUS_AFTER_R22F1_AND_R23G_AUTHORIZATION_2026-10-02.md
README_BEFORE_ROUND22_2026-10-02.md
README_BEFORE_ROUND21_2026-10-02.md
README_PRE_ROUND18.md
```

README快照逐层保留旧导航。Round18记录41项原始来源，15项关键正文、26项原始摘要及额外作者文档；Round22的34行是边界条目而非34个独立实验。更早workload审计的22篇/83条是按实验组拆分，不要把各轮篇数相加作为去重全文数量。[S10、S13、H04]

### 13.3 文献解释与近期写作

- 按“原文版本→具体实验组→对象/输入→变量→平台→测量层次→作者陈述/我们的推断”记录，不只列模型名称。
- KEY_SECTIONS不称全文逐字审计；ABSTRACT不称完整实验已核；源码存在不等于109 runtime已验证；未获取不自动说作者未公开。
- R21已排除把Sobek的dual-CSR当通用必需；3DGS延迟Adam已有GS-Scale等近邻；Muon Gram算法和HSTU已有强软件，不换名立项。
- R81继续比较XGrammar/Kestrel/FlashSampling具体能力，不重做一个泛泛“稀疏head”故事。
- 现阶段可写软件正结果、评价方法和局限；不能预写最终硬件贡献或宣称找到普遍GPU瓶颈。
- G运行间隙不需要另一轮无边界广泛survey。只补与当前问题直接相关的能力、数值语义和成本解释；以后换题先查历史账本。

## 14. 174-new、109、164的实际协作方式

### 14.1 角色和数据面

| 节点 | 职责 | 禁止的误用 |
|---|---|---|
| 109 / F、G | RTX4080/SM89真实运行、输入生成、Native/profile/trace；按授权共享一张卡 | 不跑Accel-Sim替174；不并行两个正式GPU测量 |
| 174-new / E | 独立consumer、CPU分析、合格时的模拟/机制工作 | 不因CUDA不可见当阻塞；不保存大模型/大trace本地副本 |
| 164 | durable模型、原始数据、receipt、派生数据authority | 不是科学计算节点；mount存在不代表payload完整 |
| ChatGPT | 读远端、文献/源码/结果审查、设计、协调handoff | 没有SSH就不声称检查了GPU进程/磁盘；写合同不等于节点已执行 |

当前阶段没有模拟授权；这不改变E长远可承担模拟器的角色。

### 14.2 控制面与报告循环

```text
用户贴Codex报告 / 告知正在执行
  → ChatGPT读exact GitHub ref、Goal、关键表与receipt
  → 得出范围明确的判断
  → 必要时发布ChatGPT-owned handoff并给一个完整代码块
  → 用户转发对应既有Lane窗口
  → Codex在节点执行
  → 小代码/报告/索引进GitHub，大raw进164
  → push/fetch-back/remote tree＋节点closure
  → 报告回到ChatGPT
```

本次只迁移ChatGPT，不迁移Codex进程，不重新发布G运行命令。除当前任务明确要求，不自动merge实验分支，也不改其他lane工作区。

### 14.3 路径和SSH（历史alias，仅供查找）

```text
109工作/活跃数据根常用: /data/c16/
109旧主仓库: /home/huangrulin/workspace/accel-sim-framework
174-new仓库/worktree根常用: /root/workspace/
164挂载: /root/share/mnt164
长期C16根: /root/share/mnt164/huangrulin/c16_ai_workload/
常见AWMA raw根: .../c16_ai_workload/provenance/awma/<campaign>/
另有合法历史根: /root/share/mnt164/huangrulin/awma_<campaign>/
GPU锁: /data/c16/locks/c16_gpu_campaign.lock
```

109→174-new历史使用`ssh hrl174new`；174-new→109使用`ssh gpu109`；其他控制host曾用`hrl-174-new`/`hrl174-new`。109曾是`loongson@10.156.120.109`，174-new容器旧资料端口2239；164旧底层地址`10.208.130.164`。

**这些不是所有环境通用连接参数。**实际以节点本机`~/.ssh/config`、execution receipt和现有可用连接为准，不猜端口/用户名，不因统一名称改密钥、remote或数据目录。本文件不含密码、token或私钥。

新G物理worktree/当前dataset revision等执行期信息尚未在读取快照发布；不从branch名称推造路径。E上一轮报告中出现的`/root/workspace/.../FINAL_DECISION.md`是节点文件路径，不是用户可下载链接。

### 14.4 大数据发布与保留

复用既有：

```text
109 active/staging
 → 本地manifest＋SHA闭合
 → 164 inbox/<run>.partial（可经174作为通道）
 → resume/size/SHA核验
 → admit/原子发布
 → receipt＋ACK
 → 109标transferred，是否清理另按政策
```

`rsync exit=0`不等于科学交付完成；缺ACK不删除109副本。不改accepted原始路径，不为目录整洁迁移数十GB。164大文件按既有raw index访问，避免全盘扫描/反复hash所有模型。[H03]

174本地曾空间紧张，用户明确暂不改共享挂载方式；不能自动要求本地NVMe staging。曾有FULL5排查显示sim/parser为主耗时，不应无证据把长时延全归SSHFS。

### 14.5 Git与分支处理

每个新科学任务用独立execution branch/worktree、output/config/tmp/build；immutable输入可只读共享。起始HEAD是合同，不是执行完毕后强制reset回去的目标。

发布故障只修传输，不重跑实验、amend/rebase改变科学commit：

```text
现有HTTPS → 有界HTTP/1.1/askpass → GitHub SSH → gh/API
 → push同一exact commit → fetch-back/ls-remote/tree → clean
```

GitHub SSH历史已配`~/.ssh/id_ed25519_github`，不要输出密钥内容，不必改`origin`才能走SSH。旧Goal无效41位SHA须按branch/内容确定性解析并登记，不盲目截断。

### 14.6 新ChatGPT工具恢复

先发现当前可用GitHub connector action，再用exact repo/path/ref读取。旧会话的`functions.exec/tools.mcp__GitHub__...`只是历史调用方式，**不保证新窗口有该工具**；当前可通过`api_tool.list_resources(paths=["GitHub"], query="fetch_file")`发现并直接调用GitHub命名空间。

`search`通常只覆盖默认分支；已知文件优先`fetch_file(ref=<exact SHA>)`。用`compare_commits(base=<expected>,head=<branch>)`检查branch是否变化。仓库来源不要用公开web搜索替代。没有节点SSH工具时，把节点动作交Codex，不模拟“已在服务器执行”。

## 15. 工程提效、授权与恢复规则

### 15.1 小问题直接修，科学变更明确停

输入缺失先分：

| 类型 | 例子 | 正确处理 |
|---|---|---|
| P1 scientific payload | tensor、权重、trace | 找accepted replica；实质信息不可恢复才阻塞 |
| P2 derived control | kernelslist、runner index、派生config | 从accepted authority确定性重建 |
| P3 provenance wrapper | manifest、receipt、catalog | 从surviving证据恢复；唯一identity证据丢失才可能真实阻塞 |
| P4 runtime ephemera | cache/tmp/build/output | 隔离重建，不当科学输入丢失 |

重建标DERIVED/RECONSTRUCTED，存在旧hash则匹配，否则绑定生成算法/输入/new hash。路径坏了不等于科学payload丢失。后处理失败但raw完好可以hash-bound recovery，不擅改raw，不为解析目录错误重跑长模拟。[H03]

小字段/路径/manifest修复不单独新建长Goal或新机制名；合并到真正任务，十几行说明即可。新identity、数值合同、authority或多节点流程才用完整handoff。

### 15.2 并行不改变准入

先看依赖与CPU/RAM/IO/GPU/存储；无实际执行依赖且资源足够的任务可并行。科学gate依赖与执行依赖不同，允许的speculative计算必须标`SPECULATIVE_PRE_GATE`，上游失败则quarantine，不能混入正式结果。

**例外以当前Goal为准**：明确“survivor才运行”“holdout不得提前打开”的科学遮盲/投资约束不可由一般并行规则覆盖。正式109测量仍按单卡锁串行，不能以CPU充足为由并行GPU。

### 15.3 功能与observer隔离

新机制opt-in/default OFF，观测与行为开关分离。OFF恢复accepted comparator；telemetry应有neutrality依据。不能为方便观测改仲裁/时序再宣称只加counter。

CPU-only任务不需要GPU锁，也不能为runtime探测偷跑CUDA。profile工具canary与科学测量预算区分；不把“报告没生成”当零耗时或无收益。

### 15.4 汇报与指令偏好

给用户用中文先讲：观察到什么、支持什么、不能说明什么、下一步是否值得。内部标签留在状态/receipt，不用大段PASS替代科学判断。

给Codex每个Lane一个完整代码块，一键复制，包含repo/branch/HEAD、必读路径、任务、资源/停止边界。续跑尽量短且自包含，新窗口才补完整背景。

用户偏好合并轮次、资源允许时并行、少人工往返；不要求无人值守必须耗满预算，不要高频轮询/重读巨大上下文。对小工程问题solve-and-continue，但不要用“用户同意继续”解释成无界改研究问题。

## 16. Authority与精确复查索引

共同repository为`swayhrl/accel-sim-framework`。下列[S]使用**commit＋path**恢复，不依赖旧聊天sandbox。D＝本次直接读过；I＝历史已读/本次继承。文件链接仅供导航，科学结果仍以对应冻结合同和raw/receipt为准。

| ID | 深度 | commit | path |
|---|---|---|---|
| S01 | D | `a5f069109ff3b72fd9754ded48ebdddc145cd89c` | `docs/vm_tlb/literature_notes/awma/plans/STATUS_AFTER_R22F1_AND_R23G_AUTHORIZATION_2026-10-02.md`（本次从commit diff读取） |
| S02 | D | `f981039d9289368cc32f761d6e5a79f91a775266` | `docs/vm_tlb/chatgpt_handoff/awma/r23g_r81_live_dispatch_v1/LANE_G_R23G_R81_LIVE_DISPATCH_109_GOAL.md` |
| S03 | D | 同S02 | 同目录`START_HERE.md` |
| S04 | D | 同S01 | `docs/vm_tlb/literature_notes/awma/README.md`（顶部状态已过时） |
| S05 | D | `bb5c66c674007cc6c9a77549fb0f81528be30056` | `docs/vm_tlb/review_packs/AWMA_R22F1_OEQ_LOWOVERHEAD_REPLAY_109_V1/FINAL_DECISION.md` |
| S06 | D | 同S05 | 同目录`RUN_RECEIPTS.json` |
| S07 | D | 同S01 | `docs/vm_tlb/literature_notes/awma/methodology/KERNEL_FAMILY_FIRST_REVIEW_V1.md` |
| S08 | I | `e34fe23503bd4d30acb4b3a33f79cd67ab0fe018` | `docs/vm_tlb/literature_notes/awma/rounds/2026-10-02_ROUND_22_RETROSPECTIVE_KERNEL_FAMILY_AUDIT.md`及`empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv` |
| S09 | D | `296263043f4949467b33c6c99a695ac5c139104d` | `docs/vm_tlb/review_packs/AWMA_R22G_R81_DISPATCH_AUDIT_109_V1/FINAL_DECISION.md` |
| S10 | D | 同S01 | `docs/vm_tlb/literature_notes/awma/README_BEFORE_ROUND22_2026-10-02.md` |
| S11 | D | `4fbef16c342fb409918aef7a3922c4f5334761ac` | `docs/vm_tlb/review_packs/AWMA_R22E_C16_E1_FAMILY_AUDIT_174NEW_V1/FINAL_DECISION.md` |
| S12 | I | `0c6cda2f680fa93ed5ea7d4b098eef5044a8a0c4` | `docs/vm_tlb/chatgpt_handoff/awma/r20r5_hybrid_native_v1/STATUS_AFTER_R20R5_FINAL_CLOSURE.md` |
| S13 | D | 同S01 | `docs/vm_tlb/literature_notes/awma/README_BEFORE_ROUND21_2026-10-02.md` |
| S14 | I | `df0e8edd009ee1a56ba65b25b319e8a852f74d27` | `docs/vm_tlb/review_packs/AWMA_R22F_R21A_FAMILY_LOCALIZATION_109_V1/` |
| S15 | I | `62af34149d45e9862d5a1e255e2a51ca88a3c4c7` | `docs/vm_tlb/review_packs/AWMA_R21A_OEQ_GRAPH_READINESS_109_V1/` |
| S16 | I | `69e74fe74e18d1f3a71bfac0d097ce49234327a9` | `docs/vm_tlb/review_packs/AWMA_R81_LEGAL_VOCAB_EXPLORATION_V1/DECISION.md` |
| S17 | I | `ec1ccad7bbcead8853cd97840a2007d96f325aa3` | `docs/vm_tlb/review_packs/AWMA_CCE_ZERO_INIT_REMOVAL_109_V1/FINAL_DECISION.md` |
| S18 | I | `7b87638e74164cdffc21c0d280324bcb048b6a8d` | `docs/vm_tlb/review_packs/AWMA_R19F2_FP8_SOFTWARE_COUNTERFACTUAL_109_V1/` |
| S19 | I | `4ef10349b198d6989ab666309fbe95ce8993bc56` | `docs/vm_tlb/review_packs/AWMA_R19_FASTWEIGHT_109_V1/FINAL_DECISION.md` |
| S20 | I | `48f5bf24a2136521e272ed4d1da18ba5aa5f798e` | `docs/vm_tlb/review_packs/AWMA_R101R5_NATIVE_POST_L1_DOWNSTREAM_109_V1/FINAL_DECISION.md` |
| S21 | I | `9759c08f3bb6e9abd134591007a27ed5bf8c23b1` | `docs/vm_tlb/chatgpt_handoff/c16/C16_PROBLEM_DISCOVERY_V2_CURRENT_STATE.md` |

实际读取GitHub URL可按`https://github.com/swayhrl/accel-sim-framework/blob/<commit>/<path>`构成。目录用tree而非blob。GitHub不能访问时保留这里的摘要和来源边界，不声称已核远端最新进展。

上传/会话历史来源：

- **H01**：`01_AWMA_MAIN_HANDOFF_2026-09-29_R101R2_O2_COMPLETE(1).md`；附`02_R101R2_O2_REVIEW_2026-09-29(1).md`。其“当前O2之后待设计”已由本文件覆盖；保留早期平台/模型/方法资料。
- **H02**：本会话用户给出的R101R3/R4/R5、Round16、R17、R19、R20、R21A/R22F/G/E报告及此前已发布审查。没有把会话摘要冒充这次全量raw重算。
- **H03**：`4090-174交互.txt`、`分支 · 审查并生成实验目标.txt`、`git提交配置.txt`、`AWMA-3.txt`、`同步主线状态.txt`等节点/存储/并行/恢复规则。文件名含4090不改实际RTX4080身份。
- **H04**：`大模型调研与申请.txt`、`AI-trace-L1-轮次推动.txt`、`AWMA-4.txt`、`AWMA-5.txt`、`AWMA-6.txt`及用户已提供方法条目：问题先行、分层采样、前序状态、现象与机制双轨、kernel族评价。
- **H05**：`真实trace分析5.txt`中conversion reuse、Split-K与交接探索历史；旧“低系统占比单独否决”解释以Round22方法与R22E最新边界为准。
- **H06**：R19F2最终收口与本会话FP8/CCE/fast-weight报告；旧F2协调文档tree有笔误，文献勘误记录实际tree为`0170bcf4b1d0ab75fe4a60fcb0cef5d940c27957`，需要精确使用时再核Git对象。
- **H07**：C16 Problem Discovery V2终态及Q30/DeepSeek/OLMoE历史材料；没有授权本次重新采集或重做平台。

其他项目DTC-L1/ISCAS、Elastic Payload L2、跨SM L1/TLS-Cache等不在本交接执行范围，不合并其结果或修改其worktree。

## 17. 给新ChatGPT窗口的接手提示

下面是**给新ChatGPT看的提示，不是发给Codex的重启命令**。只需上传本主文件并附此段；第3节已包含当前任务足够上下文，精确执行时仍回读原Goal。

```text
这是AWMA截至2026-10-02的完整主上下文，请先完整阅读第0—4节，再按需读后续历史与authority索引。

当前唯一正在执行的任务是Lane G / node109的R23G真实在线RULE_U01分派验证；用户已确认运行中。不要重发启动指令、reset分支或重启它。

R23G execution branch:
hrl/awma-r23g-r81-live-dispatch-109-v1
启动commit:
f981039d9289368cc32f761d6e5a79f91a775266
对应Goal:
docs/vm_tlb/chatgpt_handoff/awma/r23g_r81_live_dispatch_v1/LANE_G_R23G_R81_LIVE_DISPATCH_109_GOAL.md

最新业务状态来源（不是旧README顶部）:
a5f069109ff3b72fd9754ded48ebdddc145cd89c
文献分支:
hrl/awma-chatgpt-literature-notes-v1
状态文件:
docs/vm_tlb/literature_notes/awma/plans/STATUS_AFTER_R22F1_AND_R23G_AUTHORIZATION_2026-10-02.md

Lane F的R22F1已审定STOP:
bb5c66c674007cc6c9a77549fb0f81528be30056
同输入低开销TP-family replay未建立稳定正/负响应；不继续Donline、旧holdout或OEQ测量挽救。
Lane E的R22E也已STOP；R20保持CLOSED；174/Accel-Sim没有新任务。

请先通过当前可用GitHub connector核最新G分支和状态。若G尚无新完成报告，只确认恢复上下文，不新增节点实验；若已有新报告，按主文第4节和原冻结Goal审阅，不重写合同。

后续遵循kernel-family→必要配套净成本→非目标/覆盖率→完整边界四层评价。完整应用5%不是所有机制的一票否决；局部positive也不自动是新硬件。未知/输入或数值未资格化不能当性能负例。

用户已授权当前合同内连续推进。普通工程小问题直接修；新科学identity/数值合同/预算改变才STOP。不要为几十行包装修复单独开长Goal。

F/G仍是109两个窗口，E在174-new，不改lane名。所有CUDA活动共用/data/c16/locks/c16_gpu_campaign.lock；164是大型数据authority，174不stage大trace。
```

**交接一句话：不恢复旧TLB、R101、R20或OEQ路线；当前让G完成固定RULE_U01在新公开输入上的真实净成本验证，随后区分软件局部价值、系统副作用与是否真有新的硬件限制。**
