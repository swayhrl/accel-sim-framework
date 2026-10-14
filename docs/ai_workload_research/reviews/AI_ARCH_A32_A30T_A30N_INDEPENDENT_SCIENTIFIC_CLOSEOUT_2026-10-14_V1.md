# Round A32｜A30T/A30N独立科学审查：接受有范围的源码终态，不准入新GPU

**执行者：ChatGPT／AI-ARCH Discovery；日期：2026-10-14。**  
**审查起点：** 协调分支`425efec231fbc5fb88fc73aac6f6768eccbfd367`（A31）。本轮只读取GitHub固定的两个已交付报告、远端Git commit/tree/parent/ref，以及与结论有关的公开原文/API。未连接109/174/164，未运行模型、模拟器或profile，也未更新或重启任何Codex。原A26GR1 Lane M仍独立按用户已报告执行中处理，其状态未核验。

## 0. 科学裁决

- **A30N（DiT）：接受`EVIDENCE_INSUFFICIENT / NO_HARDWARE_PROBE_READY`作为本轮严格source-only完成和STOP。** 真实PixArt-Σ 1024软件/质量对象已具体化，但DiSC CTR+ST作者硬件模型不是本机GPU post-opt计时；缺同语义强稀疏GPU实现、逐层/逐step actual tile/完整时间/质量配对。报告不能被误读为“DiT没有硬件研究空间”，也不能自动转为“必须移植DiSC”的新工程。
- **A30T（MoE）：接受`SOURCE_QUALIFIED_PROBE_CANDIDATE / H200_SM90A_CONDITIONAL`作为有范围的发现实验设计完成和STOP。** 当前109 SM89/RTX4080不具备该MonoMoE FP8/SM90a公开API的同平台资格，不能把历史BF16 expert-loop替代强后端。**H200条件性设计不等于本机可执行任务，不构成新硬件机会已经存在。**
- **联合优先级：** 当前两Lane都没有具备资源/证据条件的`109 GPU HARDWARE PROBE READY`。N停止投入；T把候选作为需另行审查H200可得性和精确软件身份的候选，不为凑并行窗口重复做新文献Goal。A31 CPU–GPU协同MoE仍为source-only储备；Lane M原A26GR1继续，不抢锁、不重启。
- **关键方法边界：** 区分`软件相对于软件的已有加速`与`强软件之后仍有硬件可以改善的残差`。MonoMoE相对vLLM grouped的论文加速已属于作者软件结果；单凭其低tile利用率/带宽占比不能宣布我们的机制headroom。DiSC硬件模拟相对A100/H100 native的加速也不能等于CTR/ST在现成强GPU kernel上的收益。

## 1. GitHub exact identity和审计

| 字段 | A30N | A30T |
|---|---|---|
| 独立branch | `hrl/aiarch-a30n-dit-postopt-resource-174new-v1` | `hrl/aiarch-a30t-moe-complete-op-source-174new-v1` |
| parent/用户选定Goal commit | `cfdad590390f75ff56d7e263c233f7b1bcd4a554` | `6f4cd8bc1e2c9623cbc70053eba607d8c0484ec3` |
| submitted commit | [`6f78a2e1e9a2fdb04bc9468f4b2d5594bc3229a6`](https://github.com/swayhrl/accel-sim-framework/commit/6f78a2e1e9a2fdb04bc9468f4b2d5594bc3229a6) | [`1a8b9317de4c16e3dd19018f7f42cae1ebf5750e`](https://github.com/swayhrl/accel-sim-framework/commit/1a8b9317de4c16e3dd19018f7f42cae1ebf5750e) |
| tree（GitHub Git-data commit独立回读） | `d95d82afe8ec3d2760d80ce32e008f23d24b8481` | `11ce04902cc3b5abcda7c5c07722a898e2ec221f` |
| report blob（GitHub contents） | `5aeb3cbb7f02bc986855eae5939fea9c9028ec89` | `886d96796b94bf5d5653aebfb9f2a6c2c06874af` |
| report SHA-256（本窗口独立重算retrieved UTF-8 text） | `83c5e993f22107b4f251dab86db868cc3429666b2ea4ad2902532ab702674837` | `16496ae1fc6a98cf084a4984cccca28b1439cd5282bbcf520272035a4d897476` |
| GitHub compare | parent→branch=`ahead 1, behind 0`；branch HEAD等于提交，新增该报告一份 | 同左 |

固定文件：
- [A30N源审](https://github.com/swayhrl/accel-sim-framework/blob/6f78a2e1e9a2fdb04bc9468f4b2d5594bc3229a6/docs/ai_workload_research/reviews/AI_ARCH_A30N_DIT_POSTOPT_RESOURCE_DISCOVERY_174NEW_V1.md)
- [A30T源审](https://github.com/swayhrl/accel-sim-framework/blob/1a8b9317de4c16e3dd19018f7f42cae1ebf5750e/docs/ai_workload_research/reviews/AI_ARCH_A30T_MOE_OPERATOR_RESOURCE_DISCOVERY_174NEW_V1.md)

两Lane报告中都解释了父提交`b806777…`与任务Goal commit的差别。事实上Goal是在`b806777…`之上的一份新增文件；依用户实际发送的完整Goal commit作为运行起点是合法的，**不能因此认为发生branch污染或错源**。Git和GitHub回读可以支持报告内容完整、一份文件变更和提交树身份；“未使用GPU/模型”“峰值RSS”“现场工作区干净”仍属于各执行侧receipt，本窗口不能把Git核验伪装成远端进程追踪。

## 2. A30N：源码停在正确证据边界

**接受的科学事实：**
1. [DiSC v1原文 `III–V](https://arxiv.org/html/2605.25798)确实在图像DiT/PixArt-Σ里提出`Cached Token Reuse (CTR)`和`Softmax Thresholding / sparsity mask reuse (ST)`，并设计DPU/VPU、hash-bank分布与混合dense/sparse数据流。这对泛泛“跨步缓存、mask复用、bank冲突”的新颖性提出直接限制。
2. 原文`V-A把DiSC性能评估明确写为gem5＋Ramulator自定义cycle模型，以NVIDIA A100 80GB PCIe通过Nsight Systems获得native baseline；SystemVerilog/28nm综合为设计估算，不是制造的DiSC芯片。报告正确分开了`PAPER_AUTHOR_MODEL`和`PAPER_AUTHOR_NATIVE_BASELINE`。
3. PixArt-Σ 1024²的论文质量组确实为5k-output FID`14.32→14.86`；该值来自不同算法输出分布，而不是单个图像的bitwise同义，也不构成自然GPU runtime提升。报告的公开PixArt-Σ checkpoint、Diffusers`v0.28.0`、20-step pipeline是未来可固定入口，但**不等于DiSC作者实验的exact weight/seed/dtype/完整算法身份已复制**。
4. DiSC中CTR只有部分query被减，K/V仍全量；ST引入非结构化适中稀疏，需要实际有效kernel-tile与准备成本才可回答post-opt的GPU资源问题。报告没有把mask sparsity或FLOPs直接换算成速度。

**否定与停机原因：** 当前没有可审的`强dense vs 合法实现CTR+ST强sparse`同输入、同质量GPU pair及step/layer tile/时序。因此不能借用DiSC作者的专用硬件模拟和我们的默认SDPA源码拼出“通用GPU资源残余”。`NO_HARDWARE_PROBE_READY`是当前实验合同的合理科学STOP，而不是算法或领域负面结论。单纯因为缺作者仓库就立刻安排重型重实现，会使研究倒退成工具/复现工程；本轮不这样做。

**审稿补充限定（不要求返工）：**
- 1024部署/CFG的实际batch、Torch SDPA具体选择、性能中的全图/step分母必须在真实运行后确认，不能由Diffusers代码能力自动判为Native。
- 报告中“论文代码未找到”应一直保持“本次检索未取得”，不要外推为`绝对没有公开任何实现`。
- 未来如有被固定源/质量测试认可的实现出现，可重新审一个最小probe；当前不发续跑Goal。

## 3. A30T：正确的跨硬件证据边界，需进一步收紧硬件残余定义

**接受的科学事实：**
1. [MonoMoE原文arXiv 2609.04244v1](https://arxiv.org/abs/2609.04244)的重心是`weight-major persistent megakernel`，已把router top-k、两投影、激活、量化、归约和调度放在一次优化执行中；H200上相对于tuned vLLM Triton Grouped有作者原生完整routed operator增益。新研究不能只拿原始逐expert kernel当“最强软件”。
2. [FlashInfer Mono接口](https://docs.flashinfer.ai/generated/flashinfer.fused_moe.mono_moe.html)明确公开的SM90a、E256/N512/K2048、M≤8、BF16 activations/router_logits、block-FP8权重是硬平台/格式约束。入口已有`router_logits`，**不能把上游router projection也算成API内核功能**；T报告将同一operator的logits→output边界锁清是正确的。
3. T只把旧C16 Q30 M2048 BF16 expert-loop用作`HISTORICAL_SCOPED`参考，没有冒充Qwen3.5 FP8自然B1/4/8的实际route，且正确区分合成/自然route及算子/请求TPOT。
4. 本轮逐项独立重算FP8 source ledger：`H=2048, I=512, k=8`时每token–expert有用`3HI=3,145,728 MAC`；三个128×128块尺度阵列合计`768B/unique expert`，权重＋scale`3,146,496B/unique expert`；B=1/4/8分别为R=8/32/64，源报告的有用MAC及合法U/weight字节区间**全部算术匹配**。但这些只是条件性逻辑账，不是traffic或GPU真实耗时。

**核心审稿修正（写入未来probe，不能事后强加成这轮FAIL）：** 
- **MonoMoE相对grouped的1.17–1.54×是作者现有软件优化所得，不是强Mono之后剩余的硬件headroom。** 下一阶段必须先定义真正的“残余”是Mono单独执行的何种不可隐藏关键成本，及区别于权重最低服务、layout、schedule、launch与数值要求的counterfactual；“目前带宽低于峰值”或“理论padding多”单独都不够。
- 首个自然route完整operator对照可以作为**发现性测量**，但不能自动晋升“提出新GPU硬件结构”。H200两后端的测量身份应在未来批准中明确代码commit、形式上同一logits→output/precision/router、CUDA Graph、缓存初态、权重layout和数值门；API版与论文版不可默认等价。当前公开API文档站点版本标签可能变化，必须未来再用实际固定tag/source验ABI和feature。
- 即使未来获得H200，`mono vs tuned grouped`不能单凭相对差值证明硬件机会；最少还需要一个现实可比较的resource/critical-service诊断或符合模型约束的oracle敏感度。保留尚未观察到残余即`NO_HARDWARE_MECHANISM_READY`的负出口。
- **现有109/RTX4080不能直接运行SM90a的MonoMoE**；本轮不会因T留下一条H200 candidate就授权新设备租用、另写SM89弱化实现、GPU trace或模拟器。

## 4. 优先级与下一阶段

| Lane | 当前被独立审查接受的终态 | 下一步 |
|---|---|---|
| N／DiT | `ACCEPT_SCOPED_SOURCE_STOP / NO_HARDWARE_PROBE_READY` | 停止；不开N-R1、不主动移植DiSC，也不以像素/tile比例编造headroom |
| T／MoE | `ACCEPT_SCOPED_H200_CONDITIONAL_SOURCE_CANDIDATE`；`SM89_PLATFORM_NOT_QUALIFIED` | 保留在source候选池；只有明确H200可得、同语义强后端/自然route、额外科学价值后才讨论小型实验 |
| AI-ARCH A31 CPU–GPU协同MoE | `SOURCE_ONLY_DISCOVERY_QUESTION`，与T不同的共享主存资源轴 | 保留作备选，不马上增设第四Codex lane或在109做未经授权的协同测试 |
| M／109 3DGS | 用户最后报告A26GR1运行；未收到本轮结果 | **继续原合同**，有实际结果后单独审查，不打断当前执行 |

**科研管理判断：** 这次两条CPU source-only任务平均十几分钟完成并正常STOP，最主要的收益是低成本排除了两个不应立即占GPU的路径。下一轮不应为“并行填满窗口”重开T/N，也不应因为有一个H200候选就排队租设备。把发现层恢复到`真实可执行强基线＋一个未解决的有时间/容量/能耗分母的问题`，继续跨负载发现；M原生结果将是下一份优先审查的GPU证据。任何新GPU、simulator、新机制、holdout仍须独立科学合同、资源审查和用户明确批准。

## 5. 本轮审查范围与验证方法

- GitHub：直接读两个固定commit的完整报告，不只读用户摘要；分别读取Git Git-data commit parent/tree、报告blob；`base→branch ahead1/behind0`、`reported commit→branch identical`；以直接UTF-8编码重算报告SHA256。**这是本窗口亲自完成的GitHub证据核验。**
- 外部原文：重点复查DiSC `III–V及FlashInfer API的硬件/输入接口、MonoMoE的作者说明；本窗口未复现Mono全部Fig/Table，未验证vLLM的论文确切执行commit，也未核DiSC 10%数据子集的原始文件，因此保留T/N自己给出的scope和UNKNOWN，不扩大原文级别。
- node174 CPU资源与运行环境、无CUDA声明、工作区clean为执行侧回执；本窗口没有SSH重新检查。报告里引用的H200、A100、H100数字全部是`PAPER_AUTHOR`，不是当前服务器的Native。
- 只新增本协调审查文件及更新导航，不合并两个Execution HEAD，不改两个STOP结果，不改A26GR1或C16/AWMA scientific authority。