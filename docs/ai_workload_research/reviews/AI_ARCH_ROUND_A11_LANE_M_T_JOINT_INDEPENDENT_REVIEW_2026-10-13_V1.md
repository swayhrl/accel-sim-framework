# Round A11｜Lane M V1R1原生结果与Lane T A10源码资格联合独立审查

**执行者：ChatGPT／AI-ARCH Discovery。日期：2026-10-13。**  
**本次审查结论：Lane M `ACCEPT_SCOPED_NATIVE_MIXED_RESPONSE`；Lane T `ACCEPT_SCOPED_SOURCE_ONLY_NO_VALID_SMALL_TRAINING_PAIR`；`NO_NEW_GPU_OR_HARDWARE_ADMISSION`。**  
**审查证据级别：`GITHUB_FIXED_COMMIT_REVIEW`（144行完整计时/配对数据由ChatGPT独立复算，7份Git小文件UTF-8 SHA256独立抽核；原生数值/164 raw仅审计执行侧证据链，并未登录109/164独立重跑）。**

## 1. 执行身份与合同继承

| Lane | 固定authority | 独立审查范围 |
|---|---|---|
| **M／109 GPU** | [`1f69559df4f51290589de72876f36a756c5439f0`](https://github.com/swayhrl/accel-sim-framework/commit/1f69559df4f51290589de72876f36a756c5439f0)，tree `88b04f379cb6db582164d9a6ccc601f9c460f75d`；parent `75cfac972a56b71c4b776ce87c8ab311732ec75b`（冻结runner） | [`FINAL_REPORT.md`](https://github.com/swayhrl/accel-sim-framework/blob/1f69559df4f51290589de72876f36a756c5439f0/docs/ai_workload_research/review_packs/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1/FINAL_REPORT.md)、`TIMING_SAMPLES.tsv`、`PAIRED_SAMPLES.tsv`、`STATISTICAL_SUMMARY.json`、`NUMERIC_AND_EDGE_CHECKS.json`、`TRIAL_MEANS_AND_RAW_RECOMPUTE.json`、执行runner、环境及归档收据 |
| **T／174-new CPU源码** | [`859eb16a51c7bf085d6e39a9000de198c0f4e710`](https://github.com/swayhrl/accel-sim-framework/commit/859eb16a51c7bf085d6e39a9000de198c0f4e710)，tree `5878f2ef782286b0d651305f7e203f06e78e5481`，parent `dbfb51c9504e10759c34ccb9df85bed739dfce4f` | [`AI_ARCH_A10_TRAINING_LIFECYCLE_SOURCE_FEASIBILITY_174NEW_V1.md`](https://github.com/swayhrl/accel-sim-framework/blob/859eb16a51c7bf085d6e39a9000de198c0f4e710/docs/ai_workload_research/reviews/AI_ARCH_A10_TRAINING_LIFECYCLE_SOURCE_FEASIBILITY_174NEW_V1.md)。Git compare确认仅新增该Markdown，ahead1/behind0；固定十处源码的必要事实交叉检查 |

两条执行分支HEAD均由GitHub read-only ref查证，分别与上述提交一致。T的旧A4 `a1a7018…` STOP不变；M的原V1 `06674a9…` ENVIRONMENT_BLOCKED/NOT_EVALUATED/STOP不变。V1R1授权修正只允许官方`antlr4-python3-runtime==4.9.3`同版本sdist本地wheel构建及原科学条件恢复。两条执行结果未合并到协调分支。

## 2. Lane M：从144行原始时序独立重算，接受限定原生响应

原科学对象：`NequIP-OAM-S:0.1`、实际32个固定Si静态几何（每帧64原子，共2048原子）、109 RTX4080/SM89、原生energy/forces/stress、TF32/AMP关闭的NequIP FP32模型。四条件：C2=CPU matscipy构图/B2，G2/G4/G8=GPU alchemiops构图/B2/B4/B8；所有条件使用同一batch AOT OEQ模型产物和同一32帧。四臂并不是物理SM、带宽或Cache资源单变量实验。

### 2.1 由本窗口独立复算的完成时间

逐行读取`TIMING_SAMPLES.tsv`的原始数字（非只读取Codex汇总），按`process:block`键分组，结果**144行、3 fresh processes×12 blocks=36个完整四臂block、每臂36样本、重复/缺项0**，每行固定frames32、atoms2048及批次数C2/G2=16、G4=8、G8=4。

| 条件 | 36样本整组中位wall | 12样本每进程中位wall（p0/p1/p2） |
|---|---:|---|
| N-C2 | **20.7581685 ms** | 20.7569975 / 20.6913860 / 20.7858085 ms |
| N-G2 | **26.0444535 ms** | 26.0011335 / 26.0314315 / 26.1130620 ms |
| N-G4 | **13.5481720 ms** | 13.5221745 / 13.4956025 / 13.5647585 ms |
| N-G8 | **7.6022135 ms** | 7.6072730 / 7.5794625 / 7.6170805 ms |

严格逐block配对、对**36个逐配对速度比取中位数**，而非用两个总体中位数相除：

| 方向 | 本窗口独立复算的配对速度比Tbase/Tcand | 本窗口独立复算配对中位时间减少率`1-Tcand/Tbase` | 判定 |
|---|---:|---:|---|
| C2/G2 | `0.7969678208267386` | **-25.4756%** | B2时GPU构图**更慢**，三进程均同向 |
| G2/G4 | `1.9254968919122029` | **+48.0654%** | 相同GPU构图后端，批量增大显著减少完整wall |
| G2/G8 | `3.4320423682633656` | **+70.8628%** | 同方向持续；该模型和32帧的强局部软件组织效应 |

核对`STATISTICAL_SUMMARY.json`中的三个逐进程方向与bootstrap配对区间，方向全部一致；其95% bootstrap区间**只能描述本次3个进程/36个重复block内的运行波动**，不能表述成跨真实MD轨迹、模型族、设备或科学负载分布的总体置信结论。极端但有效样本（如p1-block6 G2约27.55ms）保留不删。

### 2.2 时间边界和机制归因限制

直接阅读冻结runner `tools/ai_workload_research/nequip_static_batch_v1r1/observe.py@`[runner `75cfac972a56b71c4b776ce87c8ab311732ec75b`](https://github.com/swayhrl/accel-sim-framework/blob/75cfac972a56b71c4b776ce87c8ab311732ec75b/tools/ai_workload_research/nequip_static_batch_v1r1/observe.py)：`sweep()`每批进行从CPU字典准备、必要搬运、NequIP native构图、同compiled模型energy/force/stress再到CPU输出；每32帧整组正式wall的外层含CUDA前后同步。不把它误称GPU kernel-only latency，也不能声称覆盖初次编译、模型下载或整个MD轨迹。

可用诊断：C2/G2/G4/G8的instrumented邻居构图区间分别约**10.675/16.295/8.268/4.219ms**；G2/G4/G8的模型GPU事件区间约**7.402/3.823/2.383ms**。诊断仅在正式计时之后完成，**不能将各区间中位数相加当关键路径**。它提示构图与模型区间随批次数下降，且G2单独采用GPU构图并不保证更快；但批量变化同时修改每调用的原子数、launch/工作量形状、算子选择与缓存行为。**没有单变量SM、L1/L2、DRAM、硬件事件或反事实，因此硬件瓶颈归因不成立。**

C2只做B2，**没有CPU构图B4/B8**，故不能由本次结果宣称GPU backend总体最优或所有批量下CPU都慢。G8是所测的四条件最快，但只是本研究条件内的排序。原模型支持Si并不证明其预测相对于Si tutorial DFT标签具特定化学精度，本轮使用同包reference判定实现等价。

### 2.3 原生数值、边集合与编译身份

本窗口核`NUMERIC_AND_EDGE_CHECKS.json`的实际结构：初始模型reference重复性、原始eager→OEQ、编译canary通过；**3个formal process各有11组数值比对（共33组、132个字段比较）**全部`pass:true`且没有failed elements。其记录的**12组四臂有向周期边集合核查**均与基准44,388条多重边完全一致，最大邻居数26，低于128的预冻结容量。前后各有相同数值门；`TRIAL_MEANS_AND_RAW_RECOMPUTE.json`记录从45个源Tensor文件进行**执行侧CPU-only复算132项比较，失败0**，本窗口未读取164上的二进制tensor单独复算。

所有formal进程报告**同一个compiled产物SHA256** `6b4ceb69ebaa7670f5bfdb06e8d0648644b467eec28983fb3d436a18f4f953f7`，计时前后224个索引二进制缓存文件身份列表不变。不能由“同一compiled hash”推断每个batch的内部kernel操作序列相同。官方导出中的一次determinant proxy-executor fallback发生于冻结前，正式计时期间未观察新的fallback或JIT。

**精度口径**：模型`model_dtype=torch.float32`，TF32-off/AMP-off，5次均值`atol=rtol=5e-5`不变；包中8个Bessel权重原生存储为FP64，另有FP64 native energy scale/shift与物理常量，这是原模型组成部分，执行者未改权重/常量/输出。不能误写成“所有算子或参数均为FP32”；最大绝对差不直接等于allclose失败，因为判定还含相对容差。该数值资格是**同包软件实现相似性**，不是训练/化学精度资格。

### 2.4 包装、资源与归档边界

- 执行侧`PACKAGING_EXCEPTION_RECEIPT.json`记录：官方ANTLR4.9.3 sdist SHA `f224469b…77881b`，本地wheel派生SHA `d3869949…546423`，**仅构建一次**，未更改原82个发行版本，环境/依赖导入PASS；没有授权其它sdist例外。
- 原报告资源：两轮累计依赖下载保守计`7,469,008,867` bytes，低于累计8GiB；GPU锁约77.683s，形式上限90min；正式观察阶段约29.495s，15min上限；取样峰值主机RSS约6.77GiB、任务显存约460MiB。旧V1 resolver峰值RAM未补测，未将本次监测误当历史独立PASS。
- node164归档**执行侧**报告444个raw文件/30个closeout文件readback PASS，含相应SHA；本ChatGPT**未SSH接入164再次散列大文件**。
- **Git独立小文件校验**：本窗口逐个读GitHub UTF-8文本，重新计算`FINAL_REPORT.md`、`FINAL_DECISION.json`、`TIMING_SAMPLES.tsv`、`PAIRED_SAMPLES.tsv`、`STATISTICAL_SUMMARY.json`、`NUMERIC_AND_EDGE_CHECKS.json`、`TRIAL_MEANS_AND_RAW_RECOMPUTE.json`的SHA256，**7/7与原`SHA256SUMS`匹配**。其余项目的完成/归档哈希只保留producer声明，不假装独立验证28/28。

**M裁决：`ACCEPT_SCOPED_NATIVE_MIXED_RESPONSE`。** 同一真实输入及强编译模型路径上“GPU B2慢于CPU B2”和“GPU B4/B8因批量组织有稳定wall减少”成立于本环境/条件。**不是P13硬件资源扩展规律、不是跨模型通用规律、不是一个新的硬件机制headroom，也不是训练/MD端到端结论。**

## 3. Lane T：训练生命周期源码审查接受有限结论

直接审阅[Lane T报告](https://github.com/swayhrl/accel-sim-framework/blob/859eb16a51c7bf085d6e39a9000de198c0f4e710/docs/ai_workload_research/reviews/AI_ARCH_A10_TRAINING_LIFECYCLE_SOURCE_FEASIBILITY_174NEW_V1.md)。其10文件源码核查的关键事实已经由本窗口固定`pytorch/torchtitan@8a75afd90773fe410340e0709b0b1af427c4af58`必要符号交叉读取：

| 软件路径 | 当前源码已可证明 | 尚不能证明 |
|---|---|---|
| `none/default/full/eager/min_cut`激活保存/SAC/重算策略 | 有独立配置与tagging能力，强软件不缺此接口 | 不代表同一自然模型在109上实测正确或更快 |
| `sac_and_offload` | 先执行默认SAC，选择部分必须保存的激活实施CPU offload，已有异步`offload/reload/wait_tensor`、defer/prefetch、view handling与预算 | 外部8×H100 native结果不能转移为4080 PCIe吞吐与数值PASS |
| `sac_and_paged_stash` | 源码明确针对有静态capacity factor的MoE padded activation，live rows放到共享page pool，默认host spill关闭；基于Megatron-Core 0.19.0移植 | 不等于通用CPU activation offload；round-robin debug route不等于自然MoE |
| 自然C4输入 | 公开`allenai/c4`的streaming处理、BOS/EOS/token packing、分片与迭代恢复接口及8B recipe真实存在 | 此次选定代码默认C4配置未锁revision/具体token bank、tokenizer文件SHA和模型初始化；`c4_test`不能替代自然训练 |
| 小规模合法实验 | 主recipe的Llama3 8B、Qwen3 14B、DeepSeek分布式例子有明确源码入口 | 没有证据证明单RTX4080 16GB能完成相同强GraphTrainer模型、完整optimizer一步及必要数值质量；debug模型不应伪称真实8B缩放复现 |

2026-06-23的[PyTorch作者技术报告](https://github.com/pytorch/devlogs/blob/74462e4bd312dbd9763358dc528968754b7bc536/content/distributed/2026-06-23-cpu-offloading.md)在8×H100报告显存/吞吐前沿；源审代码快照是2026-10选定公开代码**并非作者该技术报告精确运行commit**。来源分层合理。

**T裁决：`ACCEPT_SCOPED_SOURCE_ONLY_NO_VALID_SMALL_TRAINING_PAIR`。** 现有强软件能力确实覆盖普通SAC、CPU offload和MoE paged-stash；在本轮特定公开实现和已核训练输入范围内，没有建立单4080合法整步训练pair，故不发训练Goal。它不表示全世界没有可用小模型，也不能据此否定训练资源生命周期的研究价值；保留`Q-T10-R`为问题卡而非执行资格。

## 4. 联合科研判断与后续最小行动

| 科研问题 | 本次得到的真正结果 | 继续投入的条件 |
|---|---|---|
| **P01：任务规模/执行组织** | **M原生真实工作量正反混合响应已成立**：相同32帧、强编译同包数值合格，GPU构图在B2慢于CPU，扩大批量在GPU路径明显缩短wall | 只在有明确跨输入/模型泛化问题或额外因果对照价值时考虑轻量新观察；无需为了“冲高加速”追加同结构大量GPU样本 |
| **P13：物理资源扩展规律** | 本次没有变SM数量、HBM/DRAM带宽、L1/L2资源或被校准的服务资源；只有工作分组、backend变化 | 未来需真正单变量资源对照/可校准模拟器，且强软件已选优的前沿需和固定策略响应分开；现在不能晋升机制 |
| **训练激活生命周期** | T源审确认强软件已有能力，DevLog外部8×H100的容量/吞吐权衡成立于作者条件 | 首先补合法真实token身份、可在目标平台完成整步的小真实模型、统一数值与同语义政策对照；若缺则`PARKED_INPUT_OR_FIT` |
| **跨项目C16/AWMA** | 原冻结结果仍只作为独立历史对照 | 不因M/T新结果而恢复Stage A、R27R3或其它已关闭实验 |

**建议下一轮 Round A12｜跨负载资源约束可辨识性与候选收敛（执行者：ChatGPT／AI-ARCH Discovery）。** 先用已接受M原生整组时间的成本构成及已有C16/AWMA限定证据，设计最多一项真正能够区分“软件批次数摊销”与“物理资源约束”的**source/literature-only**候选资格卡；不凭这4点要求更多GPU profiling/模拟器。与此并行，对训练公开输入及单卡合法小模型只做必要source核查，不为了调用新模型而执行下载/训练。是否有论文价值由跨负载性、强软件对照与因果控制决定，不能因为一次G8比G2快3.43×就宣布新硬件机会。

**本轮不向任何Codex发新Goal，不授权新109 GPU/174模拟器、NSYS/NCU/NVBit或新模型/holdout，也不向已STOP的Lane M/T/N发重启命令。**
