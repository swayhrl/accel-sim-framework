# W/V、缓存保留机会与容量替代：Agent C结论

本交付只复用接受台账和封存的小型JSON。科学启动0、预算消费0；没有读取Trace/raw正文、修改旧Source/Spec/台账或执行模型。286份既有验证JSON的本轮投影共约147.8 MB，输入文件和SHA见SOURCE_READ_MANIFEST.json。Source78两份生产源文件另作只读git对象/工作树字节核对，共33,033 B；未重复构建或资格测试。

## 人口及分类覆盖

原103行完整保留：96内容组，35代表输入，42程序/槽位，7未决槽位；这些不是同一人口。本轮关联当前286个接受端点和5个未接受端点，不把旧222数当最新总体。

28行有接受结果。151个接受端点具备完整64-slice最终累计Victim统计；27行至少有一个明确正/零Victim服务上下文。其中15行在至少一种精确配置下有实际Victim服务，17行在至少一种配置下明确为零，两者非互斥。例如GEMM/FWT在G32×8有服务，在G64×8为零。其余只能写UNKNOWN，不能把缺失或禁用写成零。

上述是“实际EP利用覆盖”。所有103行的**完整程序sector时间复用分布、post-eviction距离/年龄分布仍UNKNOWN**。已有实际retained-sector服务证明程序存在至少这些可兑现重访，但不能说明程序机会全貌或未利用机会的数量。

## 标签、阈值与置信度

标签只用结构及事件，未用加速比定义“友好”。

- RETAINED_SECTOR_SERVICE_OBSERVED：完整接受端点、64份最终slice记录，read_responses>0。
- VICTIM_RESPONSE_ZERO_OBSERVED：同样条件下明确read_responses=0；只适用于该Source、输入、几何和模式。
- WB_WORK_OBSERVED：wb_created>0。WB流量多不等于WAD资源饱和。
- WAD_CAPACITY_REFUSAL_OBSERVED：同一端点真实head原因WAD_FULL观察>0。不能把跨请求分母拼成发生率。
- DIRECTORY_QUERY_COST_OBSERVED、V_BANK_SERVICE_WAIT_OBSERVED分别表示确实发生相应操作/等待，不表示应用关键路径损失。
- S/W_ONLY的V为NOT_APPLICABLE，未发射/未采指标为UNKNOWN，未接受端点为UNACCEPTED。

0阈值是可观察事件存在性边界，不是人为拟合的性能阈值。本交付没有给所有程序强制划分high/low重用。每个端点携带inputSHA、Source5、ELF、ordered-command SHA、全部options摘要、几何、时钟和原Spec/验证引用；不同上下文数值不合并。

Source78生产路径只在requested sectors已在retained row全部有效、incarnation/payload匹配、真实bank服务并且response enqueue成功后增加read_responses，故不是line首次新sector的空间延续计数。源码证据见SOURCE78_VICTIM_METRIC_SEMANTICS.json。它仍不等于“避免的DRAM请求”：另外一份S运行的miss变化包含时序、容量、W/RO等影响，没有逐请求counterfactual配对。

## 核心输入与已接受效果

以下实际服务数均为各端点独立的最终累计值，全部Source78，850MHz、L100；不得与Source7b4/812的结果拼成匹配对照。

| 输入 | G32×8 WV实际V响应 | G64×8 WV实际V响应 | G32×8 S→WV cycles | G64×8 S→WV cycles |
|---|---:|---:|---|---|
| Stencil bd0309df… | 4,930,426 | 2,547 | 5,242,939→4,768,893 | 4,299,729→4,282,418 |
| 3MM f9f80028… | 1,176,490 | 177,467 | 1,696,618→1,671,121 | 1,666,917→1,662,803 |
| FWT fc3a9062… | 88,069 | 0 | 181,827→178,951 | 170,266→170,105 |
| GEMM 140f6ed3… | 609,858 | 0 | 558,588→550,642 | 548,988→548,988 |

G64×8相对G32×8将Tag从256增至512项/slice，Payload1168、四Bank/P1等背景按原精确options保留；不作等面积或免费扩容判断。上述匹配几何对只差实际L2几何字段，不差Source、输入或时钟。Stencil的WV相对S改善9.04%缩至0.40%，3MM的1.50%缩至0.25%；这是容量与机制替代的重要实证，不能因此删除它们的Victim机会标签。

已存在三组更直接的W_ONLY→WV_ZERO_RO对照，实际完整options仅tvd_clean/dirty由0→1：

| 输入 | W_ONLY cycles | WV cycles | 条件V改善 |
|---|---:|---:|---:|
| Stencil | 5,240,684 | 4,768,893 | 9.0025% |
| FWT | 181,635 | 178,951 | 1.4777% |
| GEMM | 558,957 | 550,642 | 1.4876% |

这些是同Source、同输入、相同W背景下打开有限V路径的应用结果，包含其真实目录和服务成本。无需新采W_ONLY、重复上述模型或用S/WV联合差额冒充孤立V收益。三对精确option delta见机器comparisons的CONTROLLED_V_ENABLE_OVER_W_ONLY。

## 正、负验证与下一步决策

**Victim结构主正例：Stencil。** G32×8具有大量真实retained-sector响应和约150万WB；以已有长运行结果为设计证据，关注optional retention与mandatory WB共享Payload/Bank下的合法保留。G64缩小响应数与收益体现容量替代，不否定输入本身的可利用重访。

**独立clean服务验证：GEMM。** G32×8 WV有609,858次服务、clean installs8,431、dirty installs9；W_ONLY为558,957，WV为550,642。它与Stencil的dirty/WB背景不同，且不是本次cold-filter主开发输入。G64响应和增量为零，应保留容量背景，不能无条件把GEMM叫作所有几何都V友好。

**第二个长输入：3MM。** G32和G64均有真实服务，G64降低实际服务但没有消除；作为容量替代与较弱EP增量长族有价值。新V候选若改变Source，必须另测同新Source baseline和candidate，旧Source78只作为历史参照。

**短机制对照：FWT。** 存在dirty forward3,312、WB等待观察89,726和真实服务88,069，仍不能把这些等待相加解释关键路径。新Source7b4上cold OFF178,951→ON180,074，ON慢0.63%；已测负结果保留，不再把cold过滤当已证有效的主方向，也不为凑次数继续泛化它。

**WB多、V兑现少反例：Scan。** Source78 F的WB5,312,352，但V响应5,584、directory queries9,466,255；有WAD_FULL真实观察6,650（257个first-block requests）。它不是“完全无重访”，却明显不能仅凭WB量宣称当前V收益强。S2,162,540、F2,224,142为同Source历史负性能，F含W/V/M/T联合变化，不归因到单一V。Scan长约8.1–8.9小时，现有证据已足以纳入反例，暂不为确认同一事实重跑。Conv、2DCONV/3DCONV也保留WB与V机会独立分类，交B综合RO真实压力。

## 科学申请及成本建议

本次不批准、不启动任何点。现有Source78容量对比、上述W_ONLY/WV及V3–V5结果全部复用，不新增测量消耗。

新的Victim保留/回收策略尚未形成有完整生产资格的Source，CLEAN私有partial Core也不能当作已资格化候选。应先完成有限CPU结构工程；若候选有增量价值，再以**同新Source的WV原策略和WV新策略**各1点，GEMM短族2点、Stencil独立长族2点；3MM另立2点长族、可后置。每个族独立释放，不为等长族阻塞短族。禁止把旧Source78或跨Source S当新结构性能参考。

历史实际Host用时仅作调度参考：GEMM G32约0.84–1.42h/点；Stencil W_ONLY3.21h、WV3.71h、G64两点各3.26h；3MM V5约3.42–3.88h/点；FWT约9–15min/点。硬件/并发背景不同，不能据此承诺硬截止或实际RAM。精确已签limits与elapsed逐端点保存在机器表，实时准入仍由Main负责。

最值得先提交的新科学应由B/D选出**可真实触发RO压力而且已经有生产Source资格**的短输入；V方向此刻先停止重复测已有事实，保留有用的结构工程待办。任何新Source或Consumer资格缺口不能用工程PASS代替完整应用接受。

## 已知未知和边界

历史Motivation/Streaming缺少精确输入及ordered commandlist绑定，维持单独历史特征资料，未接入Source78统一指标。没有扫描raw/Trace来补这些缺口。

Victim install/query/response不同分母不拼成命中率；lower准入字节不是已完成DRAM带宽；slice/request等待不是应用critical-path cycles；occupancy终态不是峰值或饱和。应用NI未测、数值输出资格及PPA缺口继承各原点，不因本分类解除。

WV_CLASSIFIER_QA.json记录32个有限反例与边界检查，覆盖未知不补零、Source/ELF/input/ordered-command不匹配拒绝、隐藏硬件差异拒绝、缺slice拒绝完整零统计、G32正/G64零同时保留及cold过滤负结果保留。
