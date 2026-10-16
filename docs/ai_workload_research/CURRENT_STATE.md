# AI-ARCH｜当前科研协调状态

**最新快照：2026-10-16 / Round A70：主流通用大模型四线并行Discovery任务包已发布、四个独立分支已准备。** 用户已明确同意主流大模型优先，并要求发挥多个Codex并行发现的作用。当前状态是`READY_FOR_USER_DISPATCH`，不是已收到四个Codex运行回执；不得把文档或分支创建写成已启动节点进程。

## 1. 当前共同目标与执行范围

以主流通用LLM、MoE、通用视觉语言模型及其真实推理路径为对象，寻找成熟软件之后仍值得研究的GPU计算、存储、执行与资源协同问题。模型代表性与科学问题优先，再映射现有设备/资产；不因小众任务容易复现就继续投入，也不因旧局部负结果而否定整个LLM领域。

**A70首轮仅轻量CPU/source/原文/既有文本证据研究：四线可同时开始、互不等待，无GPU、模型加载、CUDA/JIT、训练、模拟器、环境安装、权重/数据集下载或清理。** 全部资源、方法、分支及停止条件见[完整A70 Goal包](goals/AI_ARCH_A70_MAINSTREAM_PARALLEL_DISCOVERY_GOAL_PACK_2026-10-16_V1.md)。

科学基线：`10f3a51ee39884bcec3d3180e81cc405872cccb1`。
**四线共同固定启动HEAD：`8f24af162ba37b4fa37f7a18d89b0fdb62697942`。** 该HEAD包含完整共享合同与四条独立任务。后续协调导航更新不改变已派发Goal身份。

## 2. 四窗口分工

| 本轮窗口 | 默认宿主 | 独立branch | 主责科学问题 | 状态 |
|---|---|---|---|---|
| M-A70 | 109 | `hrl/aiarch-a70m-llm-serving-discovery-109-v1` | 常规完整注意力LLM的上下文/并发/Prefill与Decode混合执行，区分排队策略与GPU资源竞争 | READY_FOR_USER_DISPATCH |
| N-A70 | 174-new | `hrl/aiarch-a70n-hybrid-state-discovery-174new-v1` | 主流混合注意力/递归状态的state形状、更新、复用、分配与执行代价 | READY_FOR_USER_DISPATCH |
| O-A70 | 109 | `hrl/aiarch-a70o-moe-execution-discovery-109-v1` | 主流MoE的自然每专家工作量、分派/排列、分组计算与合并 | READY_FOR_USER_DISPATCH |
| P-A70 | 174-new | `hrl/aiarch-a70p-vlm-pipeline-discovery-174new-v1` | 通用多模态模型视觉编码—语言Prefill—Decode交接及资源组织 | READY_FOR_USER_DISPATCH |

这些是A70逻辑窗口名，不接管其他项目同字母Lane。节点可用性以派发时CPU轻量预检为准；109/174-new各两个研究工具worker上限，不干扰原AWMA/C16/ISCAS。没有164访问任务。

M与N的区别：M围绕请求/批次混合，N围绕模型内多类型状态；O只深入expert侧，P只深入视觉输入与语言交接。不让四线分别搭完整vLLM环境，不重复所有历史核验。每Lane只写自己的`discovery/A70_<M|N|O|P>_.../`前缀、branch/worktree/tmp，不并发修改CURRENT_STATE、共同manifest或图谱。

## 3. 输出、资源与结果回收

每Lane交`REPORT.md`、`EVIDENCE.tsv`、`CANDIDATES.json`、`RECEIPT.json`。允许0—2个候选、最多1个推荐主候选，不强制阳性。对每项给出主流模型价值、具体原文实验组、现有强软件、旧证据是否覆盖、新变量、最小基准/诊断/独立验证和停止条件；全部native实验只提案，不执行。

每Lane最多1个CPU计算worker、任务工具RSS≤2GiB、新盘≤256MiB、公开论文/源码/配置下载≤128MiB；GPU、权重/数据集、安装均0。每节点两个Lane合计工具worker≤2、RSS≤4GiB、新盘≤512MiB；不把未测的Codex会话服务开销计作已控系统总量。单线程Git/BLAS，独立sparse worktree，不全盘hash、复制模型/trace或安装研究框架。研究收口上限90分钟，不要求占满；普通工程问题本Goal有界solve-and-continue，资源或科学范围变化STOP并保留已得结果。

各自完成即push/fetch-back/clean后STOP，不轮询等待其他Lane，也不自动启动后续任务。**ChatGPT收到哪条回执就先独立审查哪条**，跨线去重和抽核最强反证，最终最多收敛2—3个总体问题，也可以0个。不同窗口引用同一论文不等于独立验证。

有值得native验证的问题时，另行准备并批准有界GPU Goal；其他轻量研究可以继续。**同一109 GPU的性能实验仍须既有共享锁独占**，Codex数量增加不允许并发污染性能测量。无执行回执前不登记RUNNING；无独立审查前不登记科学accepted。

## 4. 强软件来源与证据规则

A70包给出vLLM优化/混合KV/前缀缓存、SGLang expert-parallel、Qwen3.5及Qwen3-VL官方模型卡作为起始入口；这不代表已经完成新论文普查或确认硬件瓶颈。各Lane须把最终论据绑定到论文版本和具体实验组、源码commit、模型revision。移动文档可能落后源码，旧WIP/TODO不是当前能力缺失的证明。

优先2—4项直接近邻精读而非凑数量；作者真实GPU结果、模型估计、source能力与本轮推导分别标记。发现阶段不强求完整机制上界，也不因缺native样本就自动否定候选，但未来输入/数值/资源资格必须明列。局部family、自然覆盖率与完整wall分层评价，不拿逻辑字节、tile填充率或峰值显存直接换算性能收益。

## 5. 历史结论与冻结边界

- **Q-S/ScanNet A69**：用户确认没有现有使用批准及场景资产，并要求聚焦主流通用模型；退出当前队列，不继续许可申请、镜像搜索或WarpConvNet环境建设。源码报告保留为低优先级方法储备，不是native性能负结果。
- **A61**：原生`37120f98186b83a946f4812755523f5d73245491`，eager FULL/ON资格通过、编译更新复合断言失败，STOP保持。
- **A65**：原生`3cdf0489b0b3a2cbbb4081e6dd13044f7ec70f79`，同batch A/B通过、C的1/665619更新元素超原门；微小梯度差经Adam放大，未证Torch bug；退出PID历史缺口保持。
- **A67**：原生`c425819d1f41e0cbd3053315cd5590697e808a3c`，`SCOPED_FULL_RESIDENT_SOFTWARE_ALTERNATIVE / STOP`；两seed的FULL/ON/OFF 12-step wall分别0.310875/1.788362/1.125985秒、0.435467/1.771150/1.100231秒。A68独立审查已接受该IGB-small/4080/eager范围软件反证，不恢复缓存调参、编译器或大图实验。
- **C16既有LLM结论**：E1驻留、Split-K软件吸收、FFN双流/融合、MoE E3和Stage A等从[跨项目证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)按题回查。不能换名字重跑已否定的相同问题，也不能将原数值/观测未闭合误记性能负结果。
- A62/A63稀疏权重训练、A26GR1/3DGS、A50G/CAGRA、A59数据门等原结论不变；AWMA、C16、ISCAS独立权限不继承、不合并实验HEAD、不改其任务。

## 6. 固定历史导航

[聚焦主流模型后的基线状态](https://github.com/swayhrl/accel-sim-framework/blob/10f3a51ee39884bcec3d3180e81cc405872cccb1/docs/ai_workload_research/CURRENT_STATE.md)；[A69源码阶段状态](https://github.com/swayhrl/accel-sim-framework/blob/b6e3a8323c295bc0cac74da1ba3aa0830e0772a3/docs/ai_workload_research/CURRENT_STATE.md)；[A68及以前详细状态](https://github.com/swayhrl/accel-sim-framework/blob/177dc378cd949ec9bfc45a244a6cb33251fadfd3/docs/ai_workload_research/CURRENT_STATE.md)。原始报告、raw、Goal和独立审查仍在原commit，不随本导航压缩而重写。

**当前已准备4条可并行的CPU/source发现任务；尚未收到A70各窗口执行回执。没有新增GPU/模拟器/数据资产作业。**
