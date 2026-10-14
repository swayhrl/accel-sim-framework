# AI-ARCH｜当前科研协调状态

**快照：2026-10-15，A47R2已获授权发布、等待109执行回执。维护者：ChatGPT／AI-ARCH Discovery。**

本页是研究导航，不是节点实时监控。原A47与A47R1已各自STOP；用户随后对A49纠偏批准了独立A47R2小型复验，本次仍不授权完整GloVe构图或正式性能矩阵。遵循[协调协议](COORDINATION_PROTOCOL.md)、[问题图谱](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)及[证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。AWMA由原独立窗口管理，C16保持冻结。

**历史不改写：** A46及此前完整导航保存在[CURRENT_STATE@e4bf84ff](https://github.com/swayhrl/accel-sim-framework/blob/e4bf84ff414c84576bd7dc1078d145910617b0f6/docs/ai_workload_research/CURRENT_STATE.md)。该快照中的“尚未授权”是A46时点，本页优先记录A47实际STOP；所有原报告、Goal、原始结果和commit仍按自身合同有效。

## 最新执行准入：Round A47R2｜修正index资格、条件stream对照与下一步裁决合并

**当前：`A47R2_AUTHORIZED_READY_FOR_CODEX / EXECUTION_NOT_OBSERVED`。** 用户2026-10-15在A49确认`str(idx.dtype)=="float32"`的确定性错误后回复“继续吧”，并要求今后将建议、具体做法与可合并步骤放入同一轮。本窗口据此发布[**A47R2连续Goal**](https://github.com/swayhrl/accel-sim-framework/blob/bbbe9d89d05e268f7dc958886a571fb327c44584/docs/ai_workload_research/goals/AI_ARCH_A47R2_CAGRA_INDEX_FIELDS_AND_STREAM_CANARY_109_V1.md)，本窗口**未实际连接109或启动GPU**。

- Git：branch `hrl/aiarch-a47r2-cagra-index-fields-stream-109-v1`，完整启动HEAD `bbbe9d89d05e268f7dc958886a571fb327c44584`；从A49协调parent `c3d235cd99f2698672dd40094fcd4502e397b055`独立分出，branch相对parent ahead1，唯一新增Goal。
- 唯一科研目的：对固定26.10源码和1024×100 seed20261014合成FP32输入，仅重新资格确认**C0默认RMM/默认cuVS Resources**；在合取assert前逐项记录`trained/size/dim/degree/dtype`，改用`np.dtype(idx.dtype)==np.dtype('float32')`。C0合法PASS后**同Goal连续执行C1**，只将Resources改为显式非默认CuPy stream；C0失败立即停止。
- 预检脚本语法/类型/元数据格式，防止旧R1的`None.__module__`等小包装错误再次消耗GPU进程。C0/C1两种科学配置分别最多一次build，不试完整GloVe，不重跑旧pool+stream失败配置。所有异常原样记录，`new dataset dimension100 vs old0`警告不得自动当索引错误。
- **本次新且独立预算：** node109原锁非阻塞累计≤300秒，显存≤2GiB，进程树RAM≤2GiB，CPU≤2有效workers／准备≤30min，新文件≤128MiB，下载/安装/驱动与系统更动=0，旧A47/A47R1资产完全只读。
- **合并收口：** 本Goal内同步完成CPU预检、至多两个tiny canary、证据与资源归档、结果分岔和**下一步明确建议/最小新合同草案**，commit/push/fetch-back后STOP。不能因C0 PASS另开C1 Goal；也不能顺手晋升原118万GloVe构图、四点GPU正式实验或额外机制。本轮成果只支持API资格或软件配置敏感性，硬件headroom仍未知。
- A47 `PLATFORM_OR_ASSET_NO_GO`、A47R1执行`DEFAULT_API_STILL_FAILS`为冻结历史原始终态，A49给出独立测试断言纠偏；后续不能覆盖旧Git数据来“修改”其判决。T/N/H/S/旧M/C16/AWMA全部已接受STOP。

## 0. 最新独立审查：A49｜A47R1已执行STOP，C0断言存在确定性缺陷

用户送达[**A47R1报告@13ea8acc**](https://github.com/swayhrl/accel-sim-framework/blob/13ea8acc7f19d13eca0aa3c049984db5c4256e83/docs/ai_workload_research/runs/AI_ARCH_A47R1_CAGRA_STREAM_RMM_MINICANARY_109_V1/FINAL_REPORT.md)，其状态为执行侧`DEFAULT_API_STILL_FAILS/STOP`。本窗口读取15个新增文件、raw C0.log/事件、supervisor及冻结cuVS v26.10.00 Python/C++源码，发布[**A49独立纠偏**](reviews/AI_ARCH_A49_A47R1_C0_PREDICATE_SOURCE_AUDIT_2026-10-15_V1.md)。

**实际执行：** G0 PASS，123冻结hash/mtime一致；两个GPU子进程（一次metadata formatter未构图；一次C0真实1024×100 IVF-PQ tiny构图API）；**C0 API已返回、完成同步、未SIGSEGV**，但随后Python合取assert失败；C1未运行、没有GPU搜索/recall或性能；GPU锁累计1.590秒，GPU样本峰286MiB，RSS样本峰约0.844GiB，下载=0、新文件约5.34MiB；执行工作区clean、锁已释放属于Codex回执。

**新关键源码结论：** 原`minicanary.py`使用`str(idx.dtype)=="float32"`，但固定`cagra.pyx`通过`cydlpack.pyx`的FP32分支返回的是`np.float32`**类型对象**，其字符串形式为`"<class 'numpy.float32'>"`。**即使有效的FP32索引也不能通过这个表达式**。另一方面C++ graph-only首次`update_dataset`前维度可为0，并会记录`new dimension 100 vs old index 0`的warning；这不是后置index字段错误的证明。由于原程序没有分别打印`trained,len,dim,degree,dtype`，C0是否有其它真实失败字段仍然UNKNOWN。

**科研裁决：`A47R1_SCOPED_EXECUTION_STOP_ACCEPTED / C0_BUILD_RETURNED / INDEX_QUALIFICATION_ASSERT_DEFECT / ACTUAL_INDEX_VALIDITY_UNRESOLVED / C1_NOT_RUN`。** 不改写执行原报告，独立解释不能把`DEFAULT_API_STILL_FAILS`当原生cuVS默认构图再次失败。旧A47带显式pool/stream配置的SIGSEGV仍有效，两维配置同时改变，stream或pool因果未确定。

**下一步仅建议，不授权：** 如果需要，可另审极小`A47R2`——事前纯CPU验证wrapper；C0依原配置一次tiny build并**先分字段记录**，正确用`np.dtype(idx.dtype)==np.dtype("float32")`核，再在C0真正PASS时C1仅改显式cuVS stream。两次fresh process、既有锁非阻塞、新GPU≤300秒、不安装下载/修改系统、不完整GloVe构图、无性能点。**A47R1已STOP且本页不自动授权R2；所有旧M/T/N/H/S/A47执行任务仍停止。**

## 1. A47R1历史授权入口（已结束）

**历史准入状态：A47R1当时已获授权、Goal已就绪；现在已实际执行并STOP，以上第0节及A49独立审查为最新科研状态。** 原授权不能自动延伸到A47R2。

- **109 Codex独立新任务：** [A47R1固定Goal](https://github.com/swayhrl/accel-sim-framework/blob/25b04ce3bc00f82d684de905870fd93c8942830d/docs/ai_workload_research/goals/AI_ARCH_A47R1_CAGRA_STREAM_RMM_TWO_MINICANARY_109_V1.md)。分支`hrl/aiarch-a47r1-cagra-stream-mr-minicanary-109-v1`，含Goal启动HEAD`25b04ce3bc00f82d684de905870fd93c8942830d`，Goal blob`356d9b026cca48394780aa1b2173f957e5eed21b`；从A48协调提交`ebbb9f8e60a9b8a3afe6d644289f9f4eb70ebf8f`独立分出，未merge A47执行branch。
- **C0：** 相同原26.10环境，1024×100固定合成FP32，默认RMM/CuPy allocator＋默认cuVS Resources stream，尝试至多一次CAGRA IVF-PQ小构图。**C0失败则直接STOP**。
- **C1（只有C0 PASS）：** 仅把cuVS Resources改为显式非默认CuPy stream，其他输入、版本、allocator、参数及wrapper相同；新鲜进程、至多一次小构图。两项都通过也不代表原显式RMM pool＋stream组合通过。
- **原A47R1批准的预算（已结束、不可重复使用）：** 109原共享锁非阻塞累计≤300秒；CPU准备≤30min、CPU≤2 workers、进程树RSS≤2GiB、GPU显存≤2GiB、新文件≤128MiB；下载/包安装/核心版本更改=0。旧A47环境/数据/source只读，绝不重跑完整GloVe索引、recall、四点测时，也不开额外profiling、模拟器或机制。
- 该方案当时旨在测试默认API和可能的配置敏感性；其实际结果与断言缺陷见第0节。A47原`PLATFORM_OR_ASSET_NO_GO / STOP`及A47R1执行侧STOP均为冻结历史结论，A49只增加独立纠偏。

## 2. 历史独立审查：A48｜A47已执行并合法STOP

用户提供109 A47实际终态，**`PLATFORM_OR_ASSET_NO_GO / STOP`**。本窗口已从GitHub固定commit读取FINAL_REPORT、GATES、ENV_LOCK、DATA、RESOURCE_RECEIPT、GDB和执行代码，核对39新增文件、Git tree及执行branch HEAD，并补读官方CUDA/cuVS/RMM固定源码。见[**A48完整独立审查与stream分配源码解释**](reviews/AI_ARCH_A48_A47_CAGRA_PLATFORM_NO_GO_STREAM_RESOURCE_AUDIT_2026-10-14_V1.md)。

- **最终Git：** [`ce92807ca80e1a694e41376eab3dd6b146824fd8`](https://github.com/swayhrl/accel-sim-framework/commit/ce92807ca80e1a694e41376eab3dd6b146824fd8)，tree`40e873ed2ff07359d54ce75d2440ee1f789beadc`，report blob`d3f8a6b6831235225452d7872a9f1e8ead30a595`，原A47独立branch仍`hrl/aiarch-a47-cagra-glove100-native-109-v1`。
- **G0 PASS：** 24个官方wheel与锁定cuVS26.10.0、Python3.12.3、RMM/RAFT与设备标识已核，**不代表实际构图API资格已过**。
- **G1 PASS：** 完整官方GloVe100 HDF5字节SHA绑定、实际shape/字段、32查询×全部base的CPU精确cosine参考与GT第10距离误差约1.55e-8；不是CAGRA GPU数值或recall。
- **G2 STOP：** 原完整GloVe图构建调用发生SIGSEGV(-11)，未产出索引；许可内1024×100小API诊断在输入和`make_device_padded_dataset`通过后同样在IVF-PQ→RMM分配→`libcuda cuStreamGetId`崩溃。**根因UNKNOWN**，只说明此固定安装/资源/stream调用路径未合格，不是输入资产失败或目标工作负载有负性能。
- **G3 NOT_RUN：** 索引、AUTO/SMALL、recall、B1/B256正式4点全部为零，**AI-ARCH ANNS硬件问题没有被真实验证或否定**。
- **G4 PASS：** 归档/39文件Git核验。下载≈2.914GiB（数据0.452GiB）、新盘≈7.354GiB、RSS采样峰≈1.393GiB、GPU共享锁合计4.115s、显存采样峰752MiB（短诊断峰值未采样完整），CPU准备约60min，资源账未发现越界。执行侧报告共享锁已释放、旧资产无改动。

**新的独立source线索：** RMM v26.10.00 `stream_ordered_memory_resource::get_event`中确实调用`cudaStreamGetId`；cuVS26.10 changelog记录`cuda::stream_ref`迁移；GDB在Python RMM bridge/driver符号处SIGSEGV。此线索只**收窄到stream/RMM/cuvs资源交互**，未证明invalid stream或driver/vendor bug，不能以driver13000、runtime12090数字不同直接断言ABI冲突。

**下一步：** 原A47合同已经STOP，A48时点还未授权新的GPU执行；现在用户已另行授权上节A47R1的两项小型API canary。除其固定边界外，仍无完整GloVe构图、驱动/核心版本更改、模拟器、数据下载或新机制授权；即使小canary通过，也不能自动继续原完整构图和性能矩阵。可同时选择不追修vendor栈，回到A43点云稀疏卷积Q-S或别的真实GPU负载。**当前所有M/T/N/H/S/A47执行Lane均STOP。**

## 3. 已完成并接受：A45H与A45S

[A46独立审查](reviews/AI_ARCH_A46_A45H_A45S_INDEPENDENT_SCIENTIFIC_REVIEW_2026-10-14_V1.md)保持。

- **A45H／109：** `1936dffd204043a1ab6c0fad5e7aebf565497c1a`，CPU合成组件软件敏感性完成STOP。OMP8在两种Adam合成shape中优于16，扫描偏好不同；不能换算真实late训练wall或新硬件收益。原C++请求64与OMP_THREAD_LIMIT实际限制、终态torch_threads读数需区分。
- **A45S／174：** `e0236f9e34f25dc7c96d048b31754bcb74e05764`，源审择一完成STOP。选Q-A作为低增量发现对象；其proposal身份不回写为已经执行。此次用户批准的新执行是A47独立Goal，不是恢复A45S。

## 4. 3DGS真实原生证据：A26GR1与A44

[A44独立审查](reviews/AI_ARCH_A44_A26GR1_NATIVE_THREAD_ATTRIBUTION_REVIEW_2026-10-14_V1.md)及原执行`cf80f6ec07a31eccdaff264c3bce64e0511179f8`保持STOP。真实连续训练到15200步，后期未插桩均值132.480/133.810ms；主线程阻塞并集14.084/14.746ms，不是原跨线程30–32ms全部可恢复。CPUAdam结束常晚于GPU工作子线程，仍有OMP/软件/自然输入混杂；无长期收敛、后期GPU-only或硬件因果资格。A47不使用这些数字为ANNS背书。

## 5. Discovery储备与更早冻结结果

[A34—A43十轮日志](literature/AI_ARCH_A34_A43_TEN_ROUND_DISCOVERY_JOURNAL_2026-10-14_V1.md)：点云稀疏卷积结构准备—布局—消费有效期Q-S仍有直接神经网络研究价值，但本次不搭环境；TBE训练Q-E和[A31 CPU–GPU MoE](literature/AI_ARCH_A31_CPU_GPU_MOE_COEXECUTION_RESOURCE_FRONTIER_2026-10-14_V1.md)留储备。[A33 ANNS](literature/AI_ARCH_A33_GPU_ANNS_SEARCH_STATE_RESOURCE_DISCOVERY_2026-10-14_V1.md)是源级前导，不能以其main快照字节账代替26.10运行结果。

[A32对A30T/N的审查](reviews/AI_ARCH_A32_A30T_A30N_INDEPENDENT_SCIENTIFIC_CLOSEOUT_2026-10-14_V1.md)维持：T仅H200/SM90a条件性候选，N当前DiT具体问题证据不足，都STOP，不自动恢复。A28/A29、原A26G STOP、C16 Stage A、NequIP/Green Context及AWMA各独立authority不变。

发现允许合理强对照下的小预算观察，不要求提前完成全部oracle；机制贡献仍需完整时间、因果和有限实现成本。A47原Goal已完成且STOP，当前没有新的GPU执行或硬件机制准入。
