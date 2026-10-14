# AI-ARCH｜当前科研协调状态

**快照：2026-10-14，A47已获用户授权并发布。维护者：ChatGPT／AI-ARCH Discovery。**

本页是研究导航，不是节点实时监控。用户对明确A47预算回复“做吧”是本次授权来源，不能把协调文档本身当成无限执行许可。遵循[协调协议](COORDINATION_PROTOCOL.md)、[问题图谱](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)及[证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。AWMA由原独立窗口管理，C16保持冻结。

**历史不改写：** A46及此前完整导航保存在[CURRENT_STATE@e4bf84ff](https://github.com/swayhrl/accel-sim-framework/blob/e4bf84ff414c84576bd7dc1078d145910617b0f6/docs/ai_workload_research/CURRENT_STATE.md)。该快照中的“尚未授权”是A46时点，不能覆盖用户随后批准的A47；所有原报告、Goal、原始结果和commit仍按自身合同有效。

## 0. 唯一新任务：A47／109 CAGRA真实GPU发现

**状态：AUTHORIZED_READY_FOR_CODEX / EXECUTION_NOT_OBSERVED。** 完整Goal已发布并回读；还没有109执行回执。发布Goal不表示已启动GPU、已下载数据或已完成canary。本ChatGPT未连接109/174/164、操作GPU锁或运行实验。

- Branch：`hrl/aiarch-a47-cagra-glove100-native-109-v1`。
- **固定启动commit：`26ef7b20172495f26ed53248bfab792ae8af9040`**。
- [**A47完整连续Goal**](https://github.com/swayhrl/accel-sim-framework/blob/26ef7b20172495f26ed53248bfab792ae8af9040/docs/ai_workload_research/goals/AI_ARCH_A47_CAGRA_GLOVE100_BOUNDED_NATIVE_109_V1.md)。Goal blob：`c9dbb7905fec3473c40c2c564ae6e6dfe6c03245`。
- 创建parent为`e4bf84ff414c84576bd7dc1078d145910617b0f6`，parent→任务branch仅新增一份Goal、ahead1/behind0。执行者使用含Goal的启动commit，不回退到parent，不merge其它执行分支。
- 执行窗口：109 Codex；可复用已STOP的Lane M对话，但新建独立worktree、环境、输出及预算账。174不新增任务；不能为填满并行窗口另开副实验。

### 已批准范围与资源

只做GloVe-100-angular／cuVS CAGRA，同一个完整FP32 base与索引、同recall要求下，B1/B256×官方AUTO/一条校准后的SINGLE_CTA+SMALL：**四个正式点**。功能与校准最多8个配置检查，总≤12；三fresh process与有限ABBA配对重复。环境、数据身份、唯一完整构图、索引save/load及dataset附着、功能／recall、四点未插桩计时、归档和STOP在一条Goal中连续完成。

| 资源 | 累计上限 |
|---|---:|
| GPU | node109单RTX4080 |
| GPU共享锁 | 45分钟，包含canary、必要运行库JIT、构图、加载、质量、计时、失败尝试 |
| 总下载 | 6GiB，其中科学数据≤0.6GiB |
| 新盘 | 12GiB，保留同文件系统空闲≥64GiB |
| CPU／RAM | ≤4有效workers／任务进程树RSS≤8GiB |
| 显存 | 本任务进程≤12GiB，含上下文和临时分配 |

锁使用既有`/data/c16/locks/c16_gpu_campaign.lock`，非阻塞申请，锁忙/有其它GPU任务则STOP，不抢占、不改锁；父监督进程在所有自身GPU子进程结束后释放。允许有限CPU数据准备与独立环境准备并行，但计时阶段停止这些后台负载。禁止改驱动／系统CUDA／时钟／功率，不修改任何旧环境或旧实验资产。

### 科学边界

目标发行`cuvs-cu12==26.10.0`及A46核验的固定源码在G0/G2重新建立实装身份；源码存在不等于wheel/ABI已资格通过。数据没有发布方预先SHA时，允许完整获取后计算并绑定来源，而不是凭不存在的metadata要求提前STOP。

2000校准query与8000独立报告query分离；2048不同report query作计时集合。每个batch分别满足recall@10≥0.95且A/B差异≤0.005。校准h仅在9/11择一，报告后不改参数；质量失败正常NO_GO。GPU search时间与CPU query就绪到CPU结果可用wall分列，不将异步返回当完成、不把两者相加。

AUTO是官方启发式，不是全参数最优。SMALL优于AUTO首先是软件配置/状态策略现象；本轮不证明物理SMEM或硬件headroom。有效路径相同、AUTO充分和无显著差异都允许正常收口。缺扩展telemetry不强制先建tracer，普通包装问题同Goal有界修复；科学输入、精度、算法或资源边界改变才停止。

**不授权：** 新3DGS训练／15k重跑、Spira部署、第二数据集、NCU/NSYS/NVBit、模拟器、硬件机制、独立新holdout或自动续Goal。原生事件用于合格stream计时不等于完整profiler。完成后独立commit/push/fetch-back提交完整raw、资源账和终态，再由本窗口审查。

## 1. 已完成并接受：A45H与A45S

[A46独立审查](reviews/AI_ARCH_A46_A45H_A45S_INDEPENDENT_SCIENTIFIC_REVIEW_2026-10-14_V1.md)保持。

- **A45H／109：** `1936dffd204043a1ab6c0fad5e7aebf565497c1a`，CPU合成组件软件敏感性完成STOP。OMP8在两种Adam合成shape中优于16，扫描偏好不同；不能换算真实late训练wall或新硬件收益。原C++请求64与OMP_THREAD_LIMIT实际限制、终态torch_threads读数需区分。
- **A45S／174：** `e0236f9e34f25dc7c96d048b31754bcb74e05764`，源审择一完成STOP。选Q-A作为低增量发现对象；其proposal身份不回写为已经执行。此次用户批准的新执行是A47独立Goal，不是恢复A45S。

## 2. 3DGS真实原生证据：A26GR1与A44

[A44独立审查](reviews/AI_ARCH_A44_A26GR1_NATIVE_THREAD_ATTRIBUTION_REVIEW_2026-10-14_V1.md)及原执行`cf80f6ec07a31eccdaff264c3bce64e0511179f8`保持STOP。真实连续训练到15200步，后期未插桩均值132.480/133.810ms；主线程阻塞并集14.084/14.746ms，不是原跨线程30–32ms全部可恢复。CPUAdam结束常晚于GPU工作子线程，仍有OMP/软件/自然输入混杂；无长期收敛、后期GPU-only或硬件因果资格。A47不使用这些数字为ANNS背书。

## 3. Discovery储备与更早冻结结果

[A34—A43十轮日志](literature/AI_ARCH_A34_A43_TEN_ROUND_DISCOVERY_JOURNAL_2026-10-14_V1.md)：点云稀疏卷积结构准备—布局—消费有效期Q-S仍有直接神经网络研究价值，但本次不搭环境；TBE训练Q-E和[A31 CPU–GPU MoE](literature/AI_ARCH_A31_CPU_GPU_MOE_COEXECUTION_RESOURCE_FRONTIER_2026-10-14_V1.md)留储备。[A33 ANNS](literature/AI_ARCH_A33_GPU_ANNS_SEARCH_STATE_RESOURCE_DISCOVERY_2026-10-14_V1.md)是源级前导，不能以其main快照字节账代替26.10运行结果。

[A32对A30T/N的审查](reviews/AI_ARCH_A32_A30T_A30N_INDEPENDENT_SCIENTIFIC_CLOSEOUT_2026-10-14_V1.md)维持：T仅H200/SM90a条件性候选，N当前DiT具体问题证据不足，都STOP，不自动恢复。A28/A29、原A26G STOP、C16 Stage A、NequIP/Green Context及AWMA各独立authority不变。

发现允许合理强对照下的小预算观察，不要求提前完成全部oracle；机制贡献仍需完整时间、因果和有限实现成本。当前只批准一个A47原生发现Goal，没有新的硬件机制准入。
