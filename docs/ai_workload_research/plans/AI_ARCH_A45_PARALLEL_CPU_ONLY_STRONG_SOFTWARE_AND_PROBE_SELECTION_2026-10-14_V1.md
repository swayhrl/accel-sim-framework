# Round A45｜CPU软件反证＋下一项GPU发现问题筛选：并行工作协调记录

**科学总控：ChatGPT／AI-ARCH Discovery；2026-10-14。**

## 0. 合同与执行状态

用户在A44正式审查后明确回复“同意，尽量并行、高效做”。在不重复已STOP实验、不启用GPU的范围内，A45落实为**两个并行、彼此独立的CPU任务**。本页与Goal发布是准备状态，**不是Codex已运行证明**。实际启动由用户发送启动指令，结果由对应执行者单独提交/发布并独立审查。本次没有命令连接109/174，也不访问GPU锁。

| 科学问题 | 执行Lane/节点 | 固定Goal起点提交 | 决定性输出 |
|---|---|---|---|
| CPUAdam软件与线程反证 | A45H／新109 Codex窗口，CPU-only | `7b59349979dc77ec0a671c0ca96d7ebaadf3d8dd`；[Goal](https://github.com/swayhrl/accel-sim-framework/blob/7b59349979dc77ec0a671c0ca96d7ebaadf3d8dd/docs/ai_workload_research/goals/AI_ARCH_A45H_CPUADAM_SOFTWARE_COUNTERFACTUAL_CPUONLY_109_V1.md) | 原CPUAdam synthetic组件更新/scan的线程和N/U敏感度＋数值证明；不能冒充真实step wall |
| Q-S vs Q-A下一GPU发现问题择一 | A45S／新174-new Codex窗口，CPU/source-only | `65130892533d92c04a704deee1f037865fee5367`；[Goal](https://github.com/swayhrl/accel-sim-framework/blob/65130892533d92c04a704deee1f037865fee5367/docs/ai_workload_research/goals/AI_ARCH_A45S_SPARSE_ANNS_MINIMUM_NATIVE_PROBE_SELECTION_174NEW_V1.md) | 一张可停止的probe投资决策：一个合法对象、强软件、平台和预算，或无合格GPU实验 |

两branch均从A44协调提交`8446f14595d2b084f5bcaea7b0ff4eac4d029a5d`独立创建，Goal各自唯一新增文件，均已验证相对parent ahead1/behind0，目标HEAD与固定提交identical。A45H和A45S只读共享文献和历史Git资产，不merge彼此工作区，也不写本协调分支。

**权限：** H仅在109复用原已验证CPUAdam隔离环境，禁止任何GPU/model/CUDA/新依赖、禁止重新进行15k训练；限CPU16有效OpenMP+少量Python监督、总运行线程≤24、RSS≤6GiB、≤20分钟、临时文件≤50MiB。S仅174 CPU/source，≤2 workers、RSS≤3GiB、≤2小时、≤40MiB文件，不下载科学输入或安装环境。节点资源不足合法defer/STOP。**新的109 GPU发现、CLM训练、CPU+GPU基准、模拟器、机制实现、holdout和新下载均没有授权。**

## 1. 本窗口新增的CLM直接代码反证（无训练）

已在固定作者源码 `nyu-systems/CLM-GS@1119a10198b8398a81d4fcad0d5d407f8a330543` 中直接读：

- `strategies/clm_offload/README.md`，blob `278d322dfb278d8e81aef9b22b7df2e348df2fd3`：CLM储存GPU几何属性11 FP32值/GS、CPU pinned SH属性48 FP32值/GS（与GS-Scale报告的10＋49及各自布局不同）；相机排序与finish_indices_filters用于分微批次逐步完成CPU Adam。此代码路径明确支持batch4/8/16/32/64的order_calculation，而不证明同一B1场景下的CLM速度。
- `strategies/clm_offload/engine.py`，blob `0d8c21567fd25bfe0ebe8ce2cb2bca49deb5a8c0`：`cpuadam_worker`与GPU stream并行；按通信CUDA event、GPU→host信号使CPU分阶段消费，CPUAdam线程等待gradient-ready；`send_shs2gpu_*`、`send_shs2cpu_grad_*`提供双stream传输；`order_calculation`明确承担状态复用与order设计。**因此“增加CPUAdam/GPU重叠、预取、DMA双buffer”不是当前可直接声称的原创能力。**
- `strategies/clm_offload/gaussian_model.py`，blob `413aaaa978f94c899ce4baf2182f545342ca6c8d`；`optimizer.py`，blob `20cb297df97eef08d2abb55a17407596da4ad306`：其CPU pinned参数和UnifiedAdam/CPU fused Adam体系已存在，不能以“cpu计算很多”证明缺少现有优化。
- GS-Scale本地A44身份：`SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`，B1、1K、OMP16、deferred Adam和parameter forwarding，与CLM不同batch/参数布局/optimizer策略，**不允许直接对比论文时间或假设两者bitwise相同**。A44后期诊断主线程阻塞并集14.084/14.746ms；CPUAdam同worker host完成顺序是45/49、50/50个正常步骤中更慢，仅说明执行分工压力，不能当优化性能上界。

**本次源审结论：** A45H最有价值的最小实验是“在原109 CPU软件中，仅改变CPU可用线程、单独检查full-N scan/update”，先排除强软件/线程因素。A45S则独立验证神经网络稀疏映射寿命或ANNS中的哪一个能合法得到新信息。二者不会在结果未出之前自动派发GPU。后期模型没有被证明存在可无损resume的完整训练optimizer与pipeline状态，禁止通过恢复部分checkpoints伪造late阶段。

## 2. 结果裁决

先独立裁决H是否有软件敏感性，S是否选出一个强软件/平台/真实输入合格的发现性对象。没有新增效应则各自STOP、不重复修复。若仍未定位“软件已覆盖之后的、与完整时间相关的资源服务限制”，不必让研究转成硬件工程；允许新的直接AI负载研究与A43框架并行。

原A26GR1、T/N、C16、AWMA所有历史结果保持冻结；协调记录不能替代它们的scientific authority。