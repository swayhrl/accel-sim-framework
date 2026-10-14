# A45H｜109 CPU-only原CPUAdam软件反证：一个有界连续Goal

**任务性质：CPU-only实测，不能称真实Rubble训练的另一轮。** 用户在A44独立审查后要求尽量并行高效；本轮批准范围是【复用冻结原软件和原有CPU环境，做少量CPU synthetic counterfactual及源码检查】，不是新GPU/大模型/训练/下载授权。执行者为新Codex窗口（与已STOP的Lane M不同），node109，独立worktree。

## 身份和输入

Repository `swayhrl/accel-sim-framework`；独立branch `hrl/aiarch-a45h-cpuadam-cpu-only-109-v1`，Goal起始提交以本Goal最终发布HEAD为准，协调parent `8446f14595d2b084f5bcaea7b0ff4eac4d029a5d`。

第一步读 `docs/ai_workload_research/CURRENT_STATE.md`、`COORDINATION_PROTOCOL.md`、`reviews/AI_ARCH_A44_A26GR1_NATIVE_THREAD_ATTRIBUTION_REVIEW_2026-10-14_V1.md` 和冻结M终态 `cf80f6ec07a31eccdaff264c3bce64e0511179f8` 的 `BUILD_AND_THREAD.json`、`FINAL_DECISION.json`、`MEASUREMENT_WINDOWS.json`、`tools/aiarch_a26gr1/cpu_adam_canary.py`。M使用作者 `SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`；原CPUAdam已编译隔离环境的模块SHA256 `c451fda99327e5969da9f0476ef3f4915815dc9ff314c22cce002e5551379a55`（必须现场read-only核验，版本/模块找不到即STOP，不重新构建/安装）。

## 科学问题

**Q-H45：** A44在OMP16真实late发现的CPUAdam处理分支/下一步参数前递成本，是否至少对线程供给或CPUAdam内部的global N扫描表现显著**CPU软件敏感性**？本次只提供CPU-only原生组件证据，不能推导真实训练step壁钟、PCIe瓶颈和硬件机制收益。

来源界线：M原真实窗口N约6.48/6.68million、CPUAdam调用57.75/64.78ms、下一步参数前递41.85/45.49ms，这些是诊断版记录，且CPU/GPU worker同时进行。**没有当前自然的N_visible、N_update及15k真实完整optimizer state bytes；synthetic U不能冒充它们。** 不能把A44的30–32ms跨线程union复活为headroom。

## 一个连续Goal：G0→G3

**G0｜执行隔离/预算：** 在109先只读确认旧M已STOP、CPU/内存/盘当前余量和正在使用的资源。新branch/worktree，所有输出/tmp单独存放；旧M worktree、源、编译产物、原raw、预算收据、GPU锁完全只读。**不读取/操作GPU锁，不运行nvidia-smi/NvBit/NCU/NSYS/Accel-Sim、不调用CUDA或任何model/train接口。** Torch CPU + IPEX2.2 CPU仅当旧完整隔离env存在才使用，禁止联网、pip/conda、重编译或驱动更动。旧IPEX2.2 yanked安全告警保持记录，不搬出隔离env。CPU总有效并行≤16 OpenMP线程（加少量Python监督，进程总体running线程≤24），Torch/BLAS=1；总RSS≤6GiB，新文件≤50MiB，CPU耗时≤20分钟；实际资源不安全则`RESOURCE_DEFERRED_STOP`。

**G1｜先验语义：** 直接参考旧canary的CPU-only导入法，`torch.cuda.is_initialized()`须前后为false；绝不调用`torch.cuda.set_device()`、`native_runner.py`或旧`control.py.check()`（旧预算已终止）。确认原CPUAdam源hash/模块hash和`OMP_THREAD_LIMIT`生效；建立固定seed、FP32、同输入更新的正确性fixture。前后参数/两个moment必须与既有numerical canary容差对应；仅有形状正确不算PASS。

**G2｜只做两个可反证的CPU实验，不添加新机制：**
(A) **全N索引/计数扫描：** 用原函数 `calculate_update_ids` 及可能的 `update_counter`，选择freeze N=200k和6,684,932（若函数需要其它明确输入先审原ABI），用明确标synthetic的合法独立ID集合（少量预选U/N比例，例如1%与10%，具体在任何测量前冻结），记录真实功能、扫描时间、线程数、RSS和是否真O(N)。缺合法CPU函数入口即`NOT_MEASURED`，不改数学来强凑数据。
(B) **有限原CPUAdam更新：** 优先复用与历史200k×48一致的CPU canary；最多再加一个不越RSS的shape，而不是全6.7m×48完整optimizer状态。分别在fresh process下OMP_THREAD_LIMIT=1/8/16运行3次warmup＋最多7次正式计时、保留每次值和中位/离散度；固定相同synthetic输入/seed、数值容差、缓存条件；必要时隔离扫描与更新，计时不得覆盖随机初始化/fixture构造。以process RSS/thread采样守护真实上限；开始前估计w/g/m/v/reference等完整活对象内存；若超预算缩小**预定义**第二shape或标skip而不是吃swap。

**G3｜直接判定并STOP：** 汇合已有A44线程边界+本轮CPU-only组件实测，输出一张`哪些CPU软件因素能改变组件时间／哪些尚不能归因`表及最小后续Strong-Software-Native对照（仅提案）。至少列: (i)作者OMP64并未被本轮测试，(ii)自然U/缓存/NUMA/完整训练wall未知，(iii)CLM和GS-Scale已经研究异步CPU Adam、camera reuse/参数前递，不能当弱基线，(iv)D2H和GPU关键路径未测。本轮不做GPU-only晚期或15k重训，也不通过CLM的不同batch/算法时间推本地加速。发现原始函数软件敏感性也不等于硬件新意。若无时间差/有观测问题，合法`NO_CPU_SOFTWARE_SIGNAL_OR_PARTIAL`停机。

唯一报告：`docs/ai_workload_research/reviews/AI_ARCH_A45H_CPUADAM_CPUONLY_SOFTWARE_REBUTTAL_109_V1.md`，可有一份≤1MiB measurements JSON和必要的小CPU脚本（完全独立），包括raw单次值、hash、limits与否定样本。每项状态实际标`CPU_COMPONENT_NATIVE`／`A44_HISTORICAL_NATIVE`／`SOURCE`／`UNKNOWN`。普通路径/包装/脚本小问题同Goal bounded solve-and-continue；关键身份、数值、内存/GPU边界不合格则STOP。完成commit/push/fetch-back exact commit/tree/blob、clean后STOP；**绝不创建A45H的GPU续Goal**。