# AI-ARCH｜当前科研协调状态

**快照：2026-10-15，A47R1已授权发布、尚无实际运行回执。维护者：ChatGPT／AI-ARCH Discovery。**

本页是研究导航，不是节点实时监控。原A47已执行并STOP；A47R1依据用户随后对A48具体双canary建议的同意单独授权，不能自动延伸至完整GloVe构图/性能实验。遵循[协调协议](COORDINATION_PROTOCOL.md)、[问题图谱](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)及[证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。AWMA由原独立窗口管理，C16保持冻结。

**历史不改写：** A46及此前完整导航保存在[CURRENT_STATE@e4bf84ff](https://github.com/swayhrl/accel-sim-framework/blob/e4bf84ff414c84576bd7dc1078d145910617b0f6/docs/ai_workload_research/CURRENT_STATE.md)。该快照中的“尚未授权”是A46时点，本页优先记录A47实际STOP；所有原报告、Goal、原始结果和commit仍按自身合同有效。

## 最新执行准入：A47R1｜两项小型CAGRA stream/RMM隔离canary

**授权状态：`A47R1_AUTHORIZED_READY_FOR_CODEX / EXECUTION_NOT_OBSERVED`。** 用户在A48建议的两项1024×100合成最小GPU canary方案后明确同意“好的，排查”。**本ChatGPT已发布并远端核验Goal，但未SSH/操作109或GPU锁，不能称实际已启动/完成。**

- **109 Codex独立新任务：** [A47R1固定Goal](https://github.com/swayhrl/accel-sim-framework/blob/25b04ce3bc00f82d684de905870fd93c8942830d/docs/ai_workload_research/goals/AI_ARCH_A47R1_CAGRA_STREAM_RMM_TWO_MINICANARY_109_V1.md)。分支`hrl/aiarch-a47r1-cagra-stream-mr-minicanary-109-v1`，含Goal启动HEAD`25b04ce3bc00f82d684de905870fd93c8942830d`，Goal blob`356d9b026cca48394780aa1b2173f957e5eed21b`；从A48协调提交`ebbb9f8e60a9b8a3afe6d644289f9f4eb70ebf8f`独立分出，未merge A47执行branch。
- **C0：** 相同原26.10环境，1024×100固定合成FP32，默认RMM/CuPy allocator＋默认cuVS Resources stream，尝试至多一次CAGRA IVF-PQ小构图。**C0失败则直接STOP**。
- **C1（只有C0 PASS）：** 仅把cuVS Resources改为显式非默认CuPy stream，其他输入、版本、allocator、参数及wrapper相同；新鲜进程、至多一次小构图。两项都通过也不代表原显式RMM pool＋stream组合通过。
- **本次新预算：** 109原共享锁非阻塞累计≤300秒；CPU准备≤30min、CPU≤2 workers、进程树RSS≤2GiB、GPU显存≤2GiB、新文件≤128MiB；下载/包安装/核心版本更改=0。旧A47环境/数据/source只读，绝不重跑完整GloVe索引、recall、四点测时，也不开额外profiling、模拟器或机制。
- 这次只能确定默认API或**配置敏感性**，不能定性哪个vendor组件有缺陷。结果独立提交/fetch-back后再进入科学审查；A47原`PLATFORM_OR_ASSET_NO_GO / STOP`仍是冻结历史结论。

## 0. 最新独立审查：A48｜A47已执行并合法STOP

用户提供109 A47实际终态，**`PLATFORM_OR_ASSET_NO_GO / STOP`**。本窗口已从GitHub固定commit读取FINAL_REPORT、GATES、ENV_LOCK、DATA、RESOURCE_RECEIPT、GDB和执行代码，核对39新增文件、Git tree及执行branch HEAD，并补读官方CUDA/cuVS/RMM固定源码。见[**A48完整独立审查与stream分配源码解释**](reviews/AI_ARCH_A48_A47_CAGRA_PLATFORM_NO_GO_STREAM_RESOURCE_AUDIT_2026-10-14_V1.md)。

- **最终Git：** [`ce92807ca80e1a694e41376eab3dd6b146824fd8`](https://github.com/swayhrl/accel-sim-framework/commit/ce92807ca80e1a694e41376eab3dd6b146824fd8)，tree`40e873ed2ff07359d54ce75d2440ee1f789beadc`，report blob`d3f8a6b6831235225452d7872a9f1e8ead30a595`，原A47独立branch仍`hrl/aiarch-a47-cagra-glove100-native-109-v1`。
- **G0 PASS：** 24个官方wheel与锁定cuVS26.10.0、Python3.12.3、RMM/RAFT与设备标识已核，**不代表实际构图API资格已过**。
- **G1 PASS：** 完整官方GloVe100 HDF5字节SHA绑定、实际shape/字段、32查询×全部base的CPU精确cosine参考与GT第10距离误差约1.55e-8；不是CAGRA GPU数值或recall。
- **G2 STOP：** 原完整GloVe图构建调用发生SIGSEGV(-11)，未产出索引；许可内1024×100小API诊断在输入和`make_device_padded_dataset`通过后同样在IVF-PQ→RMM分配→`libcuda cuStreamGetId`崩溃。**根因UNKNOWN**，只说明此固定安装/资源/stream调用路径未合格，不是输入资产失败或目标工作负载有负性能。
- **G3 NOT_RUN：** 索引、AUTO/SMALL、recall、B1/B256正式4点全部为零，**AI-ARCH ANNS硬件问题没有被真实验证或否定**。
- **G4 PASS：** 归档/39文件Git核验。下载≈2.914GiB（数据0.452GiB）、新盘≈7.354GiB、RSS采样峰≈1.393GiB、GPU共享锁合计4.115s、显存采样峰752MiB（短诊断峰值未采样完整），CPU准备约60min，资源账未发现越界。执行侧报告共享锁已释放、旧资产无改动。

**新的独立source线索：** RMM v26.10.00 `stream_ordered_memory_resource::get_event`中确实调用`cudaStreamGetId`；cuVS26.10 changelog记录`cuda::stream_ref`迁移；GDB在Python RMM bridge/driver符号处SIGSEGV。此线索只**收窄到stream/RMM/cuvs资源交互**，未证明invalid stream或driver/vendor bug，不能以driver13000、runtime12090数字不同直接断言ABI冲突。

**下一步：** 原A47合同已经STOP，A48时点还未授权新的GPU执行；现在用户已另行授权上节A47R1的两项小型API canary。除其固定边界外，仍无完整GloVe构图、驱动/核心版本更改、模拟器、数据下载或新机制授权；即使小canary通过，也不能自动继续原完整构图和性能矩阵。可同时选择不追修vendor栈，回到A43点云稀疏卷积Q-S或别的真实GPU负载。**当前所有M/T/N/H/S/A47执行Lane均STOP。**

## 1. 已完成并接受：A45H与A45S

[A46独立审查](reviews/AI_ARCH_A46_A45H_A45S_INDEPENDENT_SCIENTIFIC_REVIEW_2026-10-14_V1.md)保持。

- **A45H／109：** `1936dffd204043a1ab6c0fad5e7aebf565497c1a`，CPU合成组件软件敏感性完成STOP。OMP8在两种Adam合成shape中优于16，扫描偏好不同；不能换算真实late训练wall或新硬件收益。原C++请求64与OMP_THREAD_LIMIT实际限制、终态torch_threads读数需区分。
- **A45S／174：** `e0236f9e34f25dc7c96d048b31754bcb74e05764`，源审择一完成STOP。选Q-A作为低增量发现对象；其proposal身份不回写为已经执行。此次用户批准的新执行是A47独立Goal，不是恢复A45S。

## 2. 3DGS真实原生证据：A26GR1与A44

[A44独立审查](reviews/AI_ARCH_A44_A26GR1_NATIVE_THREAD_ATTRIBUTION_REVIEW_2026-10-14_V1.md)及原执行`cf80f6ec07a31eccdaff264c3bce64e0511179f8`保持STOP。真实连续训练到15200步，后期未插桩均值132.480/133.810ms；主线程阻塞并集14.084/14.746ms，不是原跨线程30–32ms全部可恢复。CPUAdam结束常晚于GPU工作子线程，仍有OMP/软件/自然输入混杂；无长期收敛、后期GPU-only或硬件因果资格。A47不使用这些数字为ANNS背书。

## 3. Discovery储备与更早冻结结果

[A34—A43十轮日志](literature/AI_ARCH_A34_A43_TEN_ROUND_DISCOVERY_JOURNAL_2026-10-14_V1.md)：点云稀疏卷积结构准备—布局—消费有效期Q-S仍有直接神经网络研究价值，但本次不搭环境；TBE训练Q-E和[A31 CPU–GPU MoE](literature/AI_ARCH_A31_CPU_GPU_MOE_COEXECUTION_RESOURCE_FRONTIER_2026-10-14_V1.md)留储备。[A33 ANNS](literature/AI_ARCH_A33_GPU_ANNS_SEARCH_STATE_RESOURCE_DISCOVERY_2026-10-14_V1.md)是源级前导，不能以其main快照字节账代替26.10运行结果。

[A32对A30T/N的审查](reviews/AI_ARCH_A32_A30T_A30N_INDEPENDENT_SCIENTIFIC_CLOSEOUT_2026-10-14_V1.md)维持：T仅H200/SM90a条件性候选，N当前DiT具体问题证据不足，都STOP，不自动恢复。A28/A29、原A26G STOP、C16 Stage A、NequIP/Green Context及AWMA各独立authority不变。

发现允许合理强对照下的小预算观察，不要求提前完成全部oracle；机制贡献仍需完整时间、因果和有限实现成本。A47原Goal已完成且STOP，当前没有新的GPU执行或硬件机制准入。
