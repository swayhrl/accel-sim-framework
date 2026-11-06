# AI-ARCH｜研究组合状态台账 V1

日期：2026-11-06（Asia/Shanghai）。本轮只有CPU/原文/Git证据审查，没有新native测量。协调分支实际fetch后仍为 ed365741b230718f6ffc1ccbed125fc2566aac15，tree e2f3c9d2d4485b0d41db6c6ceec33af0d8e35304；没有更晚协调HEAD。其CURRENT_STATE仍是A80快照，不能代表后续Qwen结果，也不能据其中“正在执行”判断今天的进程。

## 证据层级与生命周期

SOURCE_ONLY、作者实验、我方native、CPU复算、条件性设计分开。STOP表示那份Goal已结束，不是整类负载没有问题。远端ref存在只证明归档入口；本轮不查询GPU、锁owner、其它项目的进程或活动raw。下表的“状态”是科学记录和研究决策，不是实时作业清单。

| 研究线 | 固定执行authority与审查链 | 真实证据／当前终态 | 本组合决定 |
|---|---|---|---|
| Qwen BF16 Decode V8–V11 | V11 339559f6972f25ac1aec78fb3577b7bd2640410e，tree c8c8391a6a0c83294ae4b6441e8c8d130180ffd2；V8 b3e0adf450a563997717126fd1c1985e884855a3、V9 b8456ce48d8ac4939a8586bc1450239cf4d344fc、V10 94cbc8197cc3a5ec22669a55e7ccfb1a3df16962 | 已完成STOP。V9有18点90个formal；V10/V11有对应节点计数和局部对照；NO_HARDWARE_CANDIDATE_PROMOTED | 成熟负载分析基点，PARKED，不重跑 |
| 3DGS GS-Scale | A26GR1 cf80f6ec07a31eccdaff264c3bce64e0511179f8，tree c66008a9da553d06a00195c8c133c3e7ec16692d；协调固定HEAD中的A44/A28/A46；A45H 1936dffd204043a1ab6c0fad5e7aebf565497c1a | 真实Rubble两次从零到15200步；有晚窗主机等待，但限OMP16、非完整收敛。A45H是CPU合成fixture／源码反证，不是自然late训练加速 | PRIMARY问题，但缺完整late-state与强软件配对，当前不准入GPU |
| Hybrid GDN／KV | A70N 5076223db5db0256fd0ccacec50b5347a0cab8c5，tree 592e12903c8fa029fb5108a967f8a00bb9cb9458；A71/A72独审 | SOURCE_SCOPE_ACCEPTED_NOT_NATIVE_NEGATIVE；NO_SURVIVOR_IN_SEARCH_SCOPE／STOP，0候选；没有我方native state-copy／迁移结论 | SECONDARY，需真实模型、自然会话和兼容软件身份 |
| MoE执行 | A70O 94ca01df352cf4cf707cd35e5f9f63d4eff014c6，tree b5b3d7f8f925c50aa845cebec2cb3057fe91b261；A71/A72独审 | SOURCE_ONLY限定0候选／STOP，不是MoE性能负例 | 不恢复旧Goal；Q3只保留具体残余问题 |
| MoE Hopper条件设计 | A30T 1a8b9317de4c16e3dd19018f7f42cae1ebf5750e，tree 11ce04902cc3b5abcda7c5c07722a898e2ec221f；A32独审 | SOURCE_QUALIFIED_PROBE_CANDIDATE／H200_SM90A_CONDITIONAL，未获设备、未运行；不是硬件候选已成立 | CONDITIONAL；109 SM89不能替代 |
| Group-wise W4 | A81 492c7c79e130d60cb344d723c15751afe81a5a82 | NO_REAL_TENSOR_AUTHORITY，G0 STOP，G1未取得真实tensor-pair证据。SHA不等于可读合法权重／activation | PARKED，不造热点／借旧activation补权重 |
| VLM视觉—语言交接 | A70P f2399777a30f4fdafa26858b3cd418e497538db2，tree 811616c50e4594e1884d4ee4e4c622a72fb953d1；A71 | SOURCE_ONLY／STOP。缓存、encoder Graph、分离已有软件；作者GB200的mm-processor数字不是我方8B完整请求 | PARKED；自然媒体／质量／完整wall未闭合 |
| 视频DiT | A30N 6f78a2e1e9a2fdb04bc9468f4b2d5594bc3229a6 + A32；A75D 6421e6768ff3df2ec20cddd87b3aa28b932c113a + A76 | A30N EVIDENCE_INSUFFICIENT；A75D SOFTWARE_NEARBY_NO_SURVIVOR／STOP。近似cache、稀疏、offload不等于同质量硬件收益 | PARKED；不能把Wan官方完整设置缩小塞入16GB后称同对象 |
| GNN | A67 c425819d1f41e0cbd3053315cd5590697e808a3c + A68；后续技术储备 4c1ba2c544a0f8ba309efa6f57eadfe248b98454 | 真实IGB-small eager短窗FULL驻留软件替代成立；A61数值STOP、A65 compiled非对齐保留。medium仅准入测算 | PARKED_BY_USER；不是所有GNN已解决，也不自动下载medium |
| 自然serving／Agent输入 | A70M f2d6324da298be26f39cda427f3e7db1a7e7031d + A72；A73W e7f2438aec9ee5c3ab677027c48a08dcd40c75b0 + A74 | 前者SOURCE_SCOPE STOP；后者SOURCE_INCOMPLETE／PARKED，公开usage／shape不能还原真实model-facing token | PARKED，不把合成trace replay当原自然请求 |
| 非矩阵资源iso-PPA | A73H 06b17a72f683316a4088292a4b424c9d97c7437c；A74C d2530b3bb8a2743b716ec58e6a3113d18b66c71f | PARKED_FOR_PPA_OR_SIM_MODEL／STOP；原生机会门不等于TC↔SFU物理交换；SM100模型与边际PPA缺失 | PARKED，不启动模拟器／RTL |
| RL后训练 | A75R 8e53641295068cdef653362d0f8d7f441c636b11 + A76 | SOURCE_SCOPE STOP。作者rollout／trainer等待与spec软件近邻不是我方GPU资源饱和证据 | PARKED；不因主流模型而自动恢复 |

这些执行SHA与复核的文件blob/SHA见本目录evidence索引。独立审查commit与执行commit严格分列；没有把一次source审查变成新native authority。本次最新ref元数据核验未建立更晚、可替代上述主要结论的已接受native结果；不声称所有远端分支都经过内容审查。

## 必须保留的范围

Qwen：B1约10.125、B2约10.448ms/额外token是固定短上下文完整generate的经验斜率。主导节点读量接近一份BF16权重，B2未翻倍；不等于实测全应用DRAM或全机memory-bound。只读驱逐对照只部分归因局部B2数据状态；B1复用条件失败、早先写驱逐混杂、desktop遥测边界、原数值FAIL均保留。altered eager的layer0首个已观察差异不能转换为native首差。


V8还保留150个formal／五个独立配置的真实性能与软件对照：logprobs=None减少约4.2–4.5ms的32-minus-1差值，R仍约1.033；不能把返回开销算成硬件冗余。其正式计时后的native端点观测中，A00选中raw logit相同（27.25），CPU FP64 logsumexp变化预测首token logprob差异至约2.5e-7；这解释该端点分数的归一化贡献，不定位native最早前向分歧层。V10 altered eager边界不能补足这个映射。LP_NONE的数值不可观测范围也不是旧阈值PASS。

3DGS：A44已把跨线程30.871/32.128ms并集纠正为主线程候选14.084/14.746ms。本轮复核不是新发现。GPU worker同步有大量CPUAdam重叠，不能把它们相加。原、修observer虽camera顺序一致，Gaussian轨迹不同；不是配对速度试验。自然U、实际SH字节和完整late checkpoint仍缺。

MoE／Hybrid：旧Q30 Layer24 prefill expert-loop与新的自然decode fused路径不同；逻辑padding、expert频数、state内容字节都不是实际DRAM或延迟。库API存在不等于本机启用、合格或最优。

## 独立项目边界

EP-L2、DTC-L1、AWMA、C16的当前活动状态均为NOT_QUERIED，本包不作运行判断。只读取固定历史引用，不查看或干预它们的活动GPU raw。没有访问164，没有恢复任何已STOP Goal。
