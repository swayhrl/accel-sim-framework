# Round20｜从神经网络算子转向具身学习的批量环境计算

日期：2026-10-01。类型：ChatGPT问题发现、原始文献/固定源码核查。**不是execution Goal；不启动109、174、CUDA、训练、trace或Accel-Sim。**

## 0. 本轮决策

优先准备一个问题：**MuJoCo Warp已有逐world收敛掩码、条件图循环和求解器优化之后，收敛world集合不断缩小，是否仍带来可避免的发射/调度成本或批尾开销？**

同平台备选：**已有contact池、稀疏Jacobian、active-DOF compaction之后，逐world约束容量上界是否仍把少数复杂world的峰值变成整批工作区与发射成本？**

二者均为假设，尚无新Native性能证据、新颖性结论或硬件准入。优先级由已发现的具体源码边界、真实输入入口和可证伪性决定，不因某个模型已下载。

这是AI训练所需的环境计算，不是神经网络推理；MuJoCo物理仿真与Accel-Sim微架构模拟是两个完全不同的层次。需要明确扩展研究对象，不能把物理引擎step的加速写成LLM或RL端到端加速。

## 1. 继承哪些已完成结果

- R19F2：`7b87638e74164cdffc21c0d280324bcb048b6a8d`。同一真实Qwen/SM89/E4M3边界，精确软件诊断回收大部分readiness差距。该软件不是stock TE产品能力；只关闭这次测试的硬件动机，不外推所有低比特问题。
- R19G：`4ef10349b198d6989ab666309fbe95ce8993bc56`。第三方TTT artifact上的两chunk软件重组与state-read对照；不是所有推理期学习的排除证据。
- R19E1：`a758be1017f35caa55dda6ad529d1b6c5f141553`。IBP/GraphSAGE两臂诊断会混入计算/复用/进程变化，未资格化；不等于dense staging零成本。
- R53：`843ad43ad33153bf73a0e51aed6d8ac309356cae`已有执行，合法workset变化未形成保持原解码轨迹的mapping收益。不能换名重跑。
- R17保留既有解释修正：Q1时间小于整个Q32 batch不是单query无优化空间的证明。STOP可以是投入决策，不等于全局最优性证明。

核查深度：本轮回读文献README、Round18来源表和R19协调收口；近期其它结果继承对话与已引用authority，没有重新遍历所有raw。所核账本未见MuJoCo批量收敛/约束容量的已完成Native边界，不能据此声称穷尽全部历史。

**小型原型可以帮助发现问题。** 不要求先证明5%上界才允许提出干预，也不允许用一次正向speedup直接宣布机制因果。结构计数、时间敏感性、软件反证和独立验证各自承担不同证据。

## 2. 阅读范围与来源层级

本轮重点阅读mjlab、GATO、TurboMPC、Spira的正文关键部分；UniLab读取架构及评估边界；ComFree-Sim、TorchSparse++采用原始摘要；Madrona采用作者项目页。另核MuJoCo/Warp与CUDA官方文档及固定源码。没有运行作者实验，不称全文逐字审计或完成论文复现。

12条来源登记见`../empirical/ROUND20_SOURCE_REGISTER.tsv`，其中论文、文档、源码记录混合，**不是12篇论文**。16条证据记录见`../empirical/ROUND20_EXPERIMENT_EVIDENCE.tsv`；SOURCE_PATH等记录不是实验结果。

## 3. 为什么看环境计算，而不再换一个LLM中间张量

mjlab把GPU物理与PyTorch训练连接起来，并把物理step捕获成CUDA Graph；发布任务包含行走、动作模仿和操作。其框架描述证明环境计算是具身学习流程的真实组成，但没有给我们在4080上的瓶颈占比。[S04]

因此本轮不假定“更多小kernel必然慢”，而是将研究变量改成：**批内独立实例的有效集合如何变化，以及既有固定执行布局怎样响应这种变化。**这与FP8先生成表示再GEMM、R53改变离散解码轨迹或R101跨kernel服务都不是同一个问题。

## 4. 主问题：逐world早退之后，整批发射成本是否仍存在

### 4.1 当前源码给出的确定事实

固定来源：`google-deepmind/mujoco_warp@3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`（2026-09-30提交）。

`mujoco_warp/_src/solver.py`，blob `090061796792f4d11408eaa69b4ef3c44465c705`。本次读取1–220、3200–3450、3670–4022、4020–4370行。

- `_solve_done`对已完成world直接返回；对未完成world根据步长、改善量、梯度、模型改善等判断收敛，更新`solver_niter`，将`ctx.done[worldid]`置位并递减`nsolving`。
- `_solve`以单元素`nsolving`驱动`wp.capture_while(... _solver_iteration ...)`。支持条件图时，不需要每轮交给Python判定；JAX兼容性相关固定循环分支不能偷当唯一强基线。
- `_solver_iteration`及多个下游kernel仍按`d.nworld`或`(d.nworld,m.nv,...)`发射，传入`ctx.done`跳过相应工作。
- 非椭圆Newton已有约束变化跟踪和stable-state fast path；没有状态翻转时可以跳过部分更新。也已有稀疏/compact处理和空任务发射限制。

**不能说完成world仍在完整重复求解。**确切区别只是：逻辑工作已经用mask抑制，多个kernel的发射几何仍包含原批world维度。[S02]

### 4.2 待验证假设

若自然batch中各world需要的求解迭代次数不同，后段可能只剩少量活跃world。此时全world发射、完成标记检查、迭代边界或状态布局是否成为完整物理step的可避免成本？

竞争解释至少有四种：
1. mask和现有优化已经足够，空slot非常便宜；
2. 慢world的必要数值求解本来就在关键路径，删除其它world不能加快它；
3. 仍有未隐藏的空发射/索引/同步成本；
4. 现有执行路径没有正确使用条件图、buffer复用等，首先是软件配置问题。

这四种都允许成为终点。不能把“batch完成要等最后一个world”本身叫可消除浪费。

### 4.3 已有能力和最近邻

CUDA Graph已有device-side WHILE条件节点。[S12] MuJoCo Warp已直接利用它。[S02] Madrona已有many-world GPU ECS和数据导向执行体系，通用world worklist与persistent执行不是新想法。[S05]

GATO的PCG部分已用一block求解一个线性系统，减少跨block迭代同步；但不能把PCG部分描述成整个SQP只有一个kernel。[S06] TurboMPC将ADMM循环移入CUDA/C++路径、复用符号分解，不能重新以每轮Python往返作唯一对照；其“融合”也不等于所有计算只发一个kernel。[S07]

因此未来创新比较必须落在**这个真实物理求解器、这个活动集合/数据布局、有限资源与代价**，而不是“GPU也可以动态调度”。本轮尚未完成所有通用active-set compaction/persistent work queue的逐项新颖性排除。

## 5. 输入入口不是缺一个大checkpoint

官方benchmark已确认以下具体入口：[S03]

- `benchmarks/unitree_g1/__init__.py`：`unitree_g1_flat`与`unitree_g1_hfield`，分别绑定`scene_flat.xml`/`scene_hfield.xml`，控制回放文件`shuffle_dance.npz`，Menagerie资产revision `affef0836947b64cc06c4ab1cbf0152835693374`。
- 官方G1设置为`nworld=8192,nconmax=48,njmax=192`。这是作者配置，不是本轮4090/4080容量或性能验收。
- 其warning override涉及ITERATIONS/LS_ITERATIONS。未来必须记录实际迭代上限到达与收敛情况，不能因为没有warning打印就说全部收敛。
- `benchmarks/humanoid/__init__.py`也提供单/三个humanoid；Franka基础场景的contact/constraint容量很小，不能因为容易运行就默认适合接触求解问题。

本轮未下载NPZ/网格字节，未捕获真实batch状态，也没有109 runtime验证。公开路径不是数据hash已闭合。

首选从一个官方scene与控制回放建立状态，不训练新policy。若所有world只是同一轨迹/同一状态的克隆，它只能是工程canary，不能证明批内差异。可以从同一合法物理回放中按**计时前固定的相位规则**取不同完整状态组成诊断batch；必须标为“轨迹状态构造batch”，不能称自然RL到达/训练分布。更强的真实策略rollout留给独立验证，不得假装已有。

## 6. 建议的最小下一步（未授权）

### 6.1 一套环境、一段回放、一个工作点

先绑定版本、scene、控制序列、solver类型、容差、warmstart、步长、约束容量、graph模式和状态恢复字段。只选择一个显存可容纳的batch工作点；容量检查不能变成按性能搜batch。官方8192不是强制。

前一段状态用于探索；后一段在方案冻结前封存。JIT/capture setup单列；必须支持的conditional path、buffer复用等作为正常基线。记录实际稀疏/compact路径，不凭文档标题推断。

### 6.2 先观察，允许小原型帮助区分原因

记录每world实际迭代数、逐迭代未完成数、约束数/active DOF、overflow、完整solver与完整step时间。统计插桩与正式计时分开；尽量使用已有计数和trace接口，不先抓SASS。

可计算无权重结构指标：

`U_iter = sum_i(k_i) / (B * max_i(k_i))`。

它只表示“迭代槽位中多少逻辑上活跃”，不反映每world工作量差异，不是GPU利用率、浪费周期或speedup上界。

若同源状态确有明显活动集合收缩，且存在一个能覆盖完整目标阶段的简单干预，可以用一个opt-in活跃world-ID组织/有限worker诊断帮助发现成本；不要求先完成所有归因。但需要保持world内方程、收敛条件、状态和算术工作，计入活跃列表生成、索引、scatter及同步成本。单个kernel调度微实验只作诊断，不能冒充完整step候选。若实现必须重写整个求解器，则退回设计审查，不把小screen膨胀成新仿真引擎。

主要区间：**相同批所有world的当前状态和控制已就绪 → 同一物理step全部结果提交**。不能只报最后一个kernel或每world吞吐摊销；不能让先完成world提前采用下一policy动作，从而改变训练/闭环算法。

### 6.3 正确性和停止条件

物理容差由baseline重复性、solver残差/收敛和所需物理状态精度确定，不能照抄LLM的`rtol=atol=1e-2`。固定场景/控制/步长/约束coverage；原路径若有原子非确定性，先记录repeat envelope，再冻结候选判定规则。不得通过丢约束或提前收敛制造快。

以下任何一个结果都足以停止当前硬件方向：自然/明确标注的轨迹状态batch没有相应异质性；空slot开销很小；强软件路径已解决；必要慢world求解主导；干预代价抵消收益；或数值/状态合同无法保留。未知单列，不写成零成本。

只有完整step出现稳定、有解释线索的增量，才打开留出窗口，再查对应具体机制近邻。依然不自动进入174。

## 7. 同平台备选：逐world约束容量的实际代价

官方文档明确区分：contact容量可以跨world池化（naconmax或nconmax*nworld），而njmax是逐world约束上界。[S01] 因此“把contacts集中成池”不是新方案。

源码仍存在多份`(nworld,njmax)`工作区，含Jaref/jv/quad/变化索引等；这不等于它们每步全部访问。[S02] 同时`_jtdaj_groups_per_world`已有“容量经常为空，发射限制到几轮resident wave”的优化，不能忽略后重做。[S02]

真正未知的是：真实contact变化下，峰值约束是否仍限制可容纳world数，或让非热点world多付出实际执行成本？

这一项先复用主问题的相同回放做容量、活跃量和访问路径账本，不另开GPU环境。基线应是对冻结状态足够且不过界的合法容量，而不是人为超大buffer。若只有预留字节减少、完整step/可行工作点无收益，保留内存事实即可；若已有sparse/compact足够则停止。不能降低容量到溢出后静默丢contact/constraint。

本轮仅保留为备选，尚无ragged allocator或新缓存设计，更无跨scene结果。

## 8. 为什么其他方向暂不进入本轮执行

| 方向 | 直接强能力/反例 | 本轮决定 |
|---|---|---|
| 通用点云稀疏卷积mapping | Spira已有packed坐标、one-shot mapping、双dataflow和全网络map并行；TorchSparse++有生成/调优路径 | 不从不规则地址或gather开销重新立项；动态拓扑若新立题需独立真实输入 |
| 一block解一个机器人优化问题 | GATO PCG已具备 | 不把既有映射当创新；其数值/控制合同不能与MuJoCo互换 |
| GPU可微MPC去掉每轮host往返 | TurboMPC已有CUDA循环/符号复用 | 不另搭一套求解器复现这个已知能力 |
| 改为闭式接触求解 | ComFree-Sim原始摘要给出不同接触模型 | 是算法/物理模型替代，不是本轮同方程调度干预 |
| 全部环境计算都应放GPU | UniLab提供CPU仿真/GPU学习解耦系统反例 | 不预设GPU必优；系统time-to-learning与局部同语义GPU比较分开 |
| 再跑R19 FP8/fast-weight/IBP | 近期分别为软件反证、窄scope充分、因果诊断未资格化 | 保留不同结论，不救旧Goal |

## 9. 版本与证据边界

MuJoCo网页仍有“稀疏Jacobian进行中”的描述，但本轮固定solver源码已含`m.is_sparse`和相关路径。它们不是同一版本状态；未来以冻结runtime及实际分支为准，不能静默采用过时文档来制造能力空缺。[S01,S02]

当前源码主分支可读，也不等于对应发布包、Warp/CUDA及SM89运行通过。未来若稳定包没有某个已公开强能力，应明确使用源码版/有限移植或缩小结论，不能换回更弱路径却省略最近邻。

本轮还核出ChatGPT-owned R19收口的一个元数据笔误：R19F2 commit的真实tree是`0170bcf4b1d0ab75fe4a60fcb0cef5d940c27957`，不是沿用F1的`7b47b1d...`。以Git commit对象为准；这不改变任何结果或raw，不要求节点重跑。

## 10. 当前状态

Lane E/F/G与Accel-Sim均STOP。只发布Round20文献/源码记录、问题准备卡和README。下一步最多形成一条以主问题为中心的资格+轻量Native合并合同，备选从同一数据的容量账本并行准备；不是现在自动执行。

## 原始来源导航

[S01] https://mujoco.readthedocs.io/en/latest/mjwarp/
[S02] https://github.com/google-deepmind/mujoco_warp/blob/3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5/mujoco_warp/_src/solver.py
[S03] https://github.com/google-deepmind/mujoco_warp/tree/3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5/benchmarks
[S04] https://arxiv.org/html/2601.22074v2
[S05] https://madrona-engine.github.io/
[S06] https://arxiv.org/html/2510.07625v2
[S07] https://arxiv.org/html/2606.24039v1
[S08] https://arxiv.org/html/2605.30313v3
[S09] https://arxiv.org/abs/2603.12185
[S10] https://arxiv.org/html/2511.20834
[S11] https://arxiv.org/abs/2311.12862
[S12] https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cuda-graphs.html
