# Lane7排队Handoff：split-K × execution memory-state诊断

执行节点：**109**；Lane：**7，复用现有RTX4080窗口**。
角色：native GPU producer；GPU锁：必须持有`/data/c16/locks/c16_gpu_campaign.lock`。
Goal：`C16_SPLITK_MEMORY_STATE_INTERACTION_109_V1`
状态：**QUEUED_NOT_STARTED**。

## 0. 先完成当前任务，不能插队

当前任务是`C16_OLMOE_ROUTING_PROVENANCE_MULTIROUND_109_V1`，协调合同commit：
`378df585cba4c21ac5864c374976e271ae44e9a3`。

本新Goal只在以下条件满足后执行：当前OLMoE Goal到达合法终止状态，raw/报告已妥善保留，Git交付完成或阻塞已明确记录，CUDA上下文卸载、GPU锁正常释放。当前任务的未解决GPU/runtime/correctness问题不能由本队列绕过。普通科学无信号或EOS正常结束不属于设备阻塞。

如果Lane7仍在执行原Goal，只把本文记入队列，不改变其runner、session矩阵、锁周期或STOP规则。不要将本诊断塞进OLMoE的模型驻留周期。本实验单独获取下一次锁。

可以并行：Lane4/Lane8@174-new。不得读取Lane4 partial结果。

## 1. 研究问题及旧结论

既有split8→split1全局H1失败：up M256改善，down M256近乎不变，两M1退化；`OPERATOR_SPECIFIC_SPLIT_POLICY_ONLY`仍冻结。

本轮不是扫描split参数，也不是再测同样A/B求一个更好数字。新增唯一实验维度是目标执行前的访存状态准备：

> 相同split8/split1实现的相对收益，是否依赖重复同arm预热，还是在独立大缓冲区访问之后仍然存在？GEMM本体与reduction的变化分别是什么？

已有NCU中up M256的GEMM自身计数已变化，故不能把全部收益简化为删除reduction。本轮最多建立state-conditioned implementation结果，不证明唯一L2容量因果，也不改变E1/Lane4结论。

## 2. Read first / source authority

repo：`swayhrl/accel-sim-framework`。

文献：`hrl/c16-chatgpt-literature-notes-v1@b0533583a6207a48cd4fa309e8dc4d925f20adce`，LR07。

原A/B producer：
`hrl/c16-lowbit-splitk-native-ab-109-v1@0e88faa28c9066b48e394dce657d7a16e6332a32`

完整读取`docs/vm_tlb/review_packs/C16_LOWBIT_SPLITK_NATIVE_AB_109_V1/`中的：
`SOURCE_AUTHORITY.json`、`BUILD_AND_BINARY_RECEIPT.json`、`INPUT_AND_WEIGHT_BINDINGS.tsv`、`A_AUTHORITY_REPRODUCTION.tsv`、`CORRECTNESS.tsv`、`LAUNCH_AUDIT.tsv`、`NCU_UP_M256_KERNEL_ROWS.tsv`、`FINAL_DECISION.json`及实际runner。

只复用已接受A/B extension和原模型/输入/weight bytes，不重新编译AWQ、不装后端、不重新量化。

B binary已报告SHA：
`1aa8db13f5fd10651aa4241f58200e3a7075214d34cca4d70fbcbe7cbbc07887`

A的binary/path及所有输入hash从上述immutable pack重新读取，不凭当前环境同名文件代替。A输出仍必须对原accepted SHA exact；B数值门槛沿用原`rtol=1e-2, atol=5e-2`。若本地B不在，先按已发布raw/build索引恢复相同binary；不得悄悄用新编译结果冒充。

## 3. 隔离与唯一矩阵

从`0e88faa28c9066b48e394dce657d7a16e6332a32`建独立branch/worktree：
`hrl/c16-splitk-memory-state-interaction-109-v1`

raw新目录：`/data/c16/splitk_memory_state_interaction_v1/<RUN_ID>/`。

模型/Layer0语义沿用原实验；仅两个点：**up_proj M256、down_proj M256**。不重测M1、不添加其他operator/model/M/split。

| Cell | 实现 | 执行前状态 |
|---|---|---|
| A_W | accepted split8 | WARM_SAME_ARM |
| B_W | accepted split1 direct output | WARM_SAME_ARM |
| A_E | accepted split8 | EVICT_CONDITIONED |
| B_E | accepted split1 direct output | EVICT_CONDITIONED |

每个operator四cell，总计八cell。A有独立reduction，B没有；grid/寄存器/shared/scratch保持旧合同。此处allocation bytes不是驻留bytes。

## 4. 访存状态准备合同

每个目标sample之前，先执行**该sample同一个arm两次不计时预热**，避免上一个cell替代本cell状态。

WARM_SAME_ARM：两次预热完成并同步 → 目标module测量。

EVICT_CONDITIONED：相同两次预热 → 一次固定大缓冲区访存conditioner → 同步 → 目标module测量。

### Conditioner

优先复用C16已accepted controlled-memory-state代码中的确定性、独立缓冲区遍历helper，只抽取必要函数，不重新跑旧矩阵。如果没有可复用实现，可用最小的独立缓冲区顺序读取/读改写实现；源代码和参数必须在本轮目标计时前commit冻结。

- 缓冲区大小固定为当前GPU已核实L2容量的4倍，所有cell都提前分配同一份；
- 与目标input/weight/output/scratch地址区间不重叠；
- 实际遍历全缓冲区，不用allocator empty_cache、CPU操作或无效/可消除代码冒充GPU cache-conditioning；
- 保留可核的访问步长、覆盖字节数、返回校验/副作用；
- 不在测量scope内分配conditioner，不把其GPU时间或流量计入目标module；
- W/E使用相同input/weights，conditioner不得改动目标数据；
- 不使用CUDA persisting set-aside或priority hint来制造结果。

只称`EVICT_CONDITIONED`，**不声称所有cache一定冷**。此处理也可能影响TLB、调频、调度或其它状态；本轮不据单一控制证明唯一cache因果。GPU属性/缓冲区覆盖资格不足则记录`CONDITIONER_QUALIFICATION_INCOMPLETE`并停止该科学比较，不试更多buffer尺寸。

## 5. 计时前资格，一次闭合

CPU阶段先核旧A/B binary/source/input/weight，冻结RUN_MANIFEST、八cell和conditioner参数。

GPU锁阶段只加载需要的相同projection资产；不下载/整套加载不必要的模型。

对两operator的四cell：
- A输入/output SHA复现旧authority；
- B输入/weights及数值比较通过；
- 目标shape/dtype/finite保持；
- 旧GEMM grid/block与A reduction/B absent保持；
- 未出现backend fallback或把conditioner包含进目标scope。

因为改变的只是准备状态，不允许新的数学/权重/precision改动。缺失包装可确定性恢复，真实identity冲突需停。

## 6. Bounded timing：全部cell一次完成

每operator先做A/B各10次不计时运行，随后25个镜像block：

`A_W, B_W, A_E, B_E, B_E, A_E, B_W, A_W`

因此每cell50个目标CUDA-event samples。每次sample都重新按§4准备状态，准备不在event范围内。同步边界一致，避免旧output tensor无限积累改变footprint；保持同一输入/权重，记录allocator/backend而不更换。

输出全量raw样本、median/mean/min/max/CV、每block配对差。新协议不能直接把旧ABBA中位数当作同一baseline拼接。

定义：
`gain_W = 1 - median(B_W)/median(A_W)`；
`gain_E = 1 - median(B_E)/median(A_E)`；
`state_interaction = gain_W - gain_E`（百分点）。

报告点估计和样本离散，不把50个同进程样本当独立应用样本。可以预先固定seed=20260928、1000次按完整镜像block重采样，提供描述性区间；不将区间当预注册因果显著性。

## 7. 限定NCU：八cell，与相同状态准备绑定

正确性/launch通过后，对两个operator的全部四cell各做一个profile，共八个semantic-range profile；不再另开后续小轮。

使用本项目已接受模式，不升级环境：
- NVTX选择只围住目标module；
- application replay；cache-control none；
- metrics仅`l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum`；
- 每次replay都执行相同两次同arm预热和W/E准备，且在NVTX外；
- A分别保留GEMM与reduction rows；B确认只有目标GEMM路径；
- raw计数保留单位，时长只在当前tool自然导出时保留，不加大metric sweep。

预热/conditioner若误入NVTX是工程selector问题，可修复后重跑受影响profile；不得按结果方向筛profile。NCU时长不替代主CUDA-event timing。所有计数都是kernel/semantic范围总量，不是tensor-level attribution。

## 8. 解释与决策

本轮不改旧H1门槛、不回写旧OPERATOR_SPECIFIC结论；新问题是独立定义的state interaction。

必须回答：
1. warm同arm下A/B方向是否与旧观察一致（协议不同，不能要求数值exact）？
2. E条件是否实际上扰动目标traffic或timing？若未可辨认，不能据此声称cache-state无关。
3. A/B相对收益随W/E怎样变化？如离散覆盖差异，标`UNRESOLVED_AT_BOUNDED_RESOLUTION`。
4. 分开列GEMM本体与reduction；不将GEMM计数变化全部归为某一种tensor。
5. up/down差异是否仍存在？这一步仍不建立通用预测器。

允许标签：
- `SPLIT_POLICY_BENEFIT_STATE_CONDITIONED_SCOPED`；
- `SPLIT_POLICY_DIRECTION_PERSISTS_ACROSS_TESTED_STATES`；
- `MEMORY_STATE_INTERACTION_UNRESOLVED`；
- `CONDITIONER_NO_RESOLVED_EFFECT`；
- typed authority/correctness/profile failure。

这些是限定解释，不是新cache机制、全模型加速或capacity-cliff证明。最多提出一项后继诊断；不自动做。

## 9. GPU锁与合并执行

CPU准备先完成 → 取得一次GPU lock → 资格/八cell计时/八cell NCU顺序执行 → 释放GPU资源及锁 → CPU统一分析与发布。

不抢锁、不删锁、不kill其他任务、不改时钟/功耗/driver。锁忙时继续安全CPU准备或等待；`WAIT_GPU_LOCK`不是科学失败。记录实际UUID、driver、pre/post状态及锁起止。

当前OLMoE任务优先。不能为本实验打断它，也不能改变Lane4任何状态。

## 10. 输出与发布

目录：`docs/vm_tlb/review_packs/C16_SPLITK_MEMORY_STATE_INTERACTION_109_V1/`

建议紧凑输出：README、SOURCE_AND_RUN_MANIFEST.json、CORRECTNESS_AND_LAUNCH.tsv、TIMING_SAMPLES.tsv、TIMING_SUMMARY.tsv、NCU_KERNEL_ROWS.tsv、INTERPRETATION.md、FINAL_DECISION.json、GPU_LOCK_RECEIPT.json、RAW_INDEX.tsv、SHA256SUMS。runner/conditioner源代码committed，小raw CSV/TSV直接保留。

最后：validate → commit → push → fetch-back exact commit/tree → clean → 报告 → STOP。需要独立consumer时交174-new，不由本窗口自行启动。

## 11. 禁止自动扩展

不准增加split=2/4/16、buffer sweep、M1、q_proj、更多模型、更多backend、newquant、D1-D3 trace、NVBit、cache/timing simulation、full-model性能测量或L2替换机制。原始A/B数值与实现不改。

普通工程问题solve-and-continue；source/数值/身份/lock边界变化才停，完整保留negative receipt。任务完成后Lane7继续作为109 GPU窗口，不自动开启下一项。
