# C16 GPT-3公开尺寸规模外推实验 — Master Pipeline V1

日期：2026-09-28。

## 0. 目标

回答一个已经由Lane7现有结果提出、但尚未做规模外推的问题：

> 当规则Dense层从7B级低比特形状扩大到GPT-3-175B公开FFN尺寸后，split-K的并行度收益与执行前数据驻留状态之间的权衡是否发生系统性变化？

这不是GPT-3原始权重实验。证据分两层：

1. **GPT-3公开尺寸FP16 Dense基线**：只使用原论文公开的FFN尺寸，合成固定数值，真实RTX4080执行；用于确认大Dense形状在本机上的实际kernel/时间/流量量级。
2. **GPT-3公开尺寸W4代理**：把同样的K/N尺寸映射到已经接受的AutoAWQ 4-bit split8/split1内核，只用于检验现有“并行度—驻留状态”机制是否随规模改变。它不是GPT-3量化checkpoint，也不是原始GPT-3精度/数值行为。

不下载175B，不生成完整96层，不声称自然GPT-3端到端性能。

---

## 1. 节点与流水线

### Lane8 — 174-new
- 角色：CPU-only prep / contract freeze / static validation
- GPU：禁止
- GPU lock：禁止
- 可与Lane4并行
- 第一产物：`PRE_GPU_CONTRACT_FROZEN.json`
- 最终产物：`PRE_GPU_READY.json`

### Lane7 — 109
- 角色：唯一RTX4080 native producer
- GPU：RTX4080 / SM89
- GPU lock：所有CUDA动作必须持有
- 允许在Lane8执行时先做CPU-only source/hash/worktree准备
- **只有看到Lane8的PRE_GPU_READY且commit/hash完全匹配后才能获取GPU锁**

### Lane6 — 174-new
- 角色：CPU-only independent consumer
- GPU：禁止
- GPU lock：禁止
- 可以提前建立consumer scaffold并读取旧Qwen/Lane7 authority
- 只有新producer final commit + raw manifest/pack就绪后才做正式结果重算

### Lane4
保持原R0/M1/diagnostic长跑；所有Lane禁止读取partial或修改其worktree/binary/config/output。

---

## 2. 效率原则

同一大任务按“准备—执行—消费”流水：

1. Lane8先冻结实验数学合同、shape、内存预算、预期grid/scratch和runner接口。
2. Lane7可同时完成：新worktree、旧A/B binary SHA复核、环境/工具检查、脚本静态阅读。不得import CUDA extension、不得初始化CUDA。
3. Lane8发布PRE_GPU_READY后，Lane7一次外层GPU lock内完成：
   - GPU身份/内存资格；
   - 合成tensor生成；
   - correctness + launch audit；
   - FP16 Dense基线；
   - W4代理所有timing；
   - 限定NCU；
   - 释放锁。
4. Lane7释放GPU后在CPU上统一分析并push science commit/pack。
5. Lane6可在Lane7 CPU后处理/164封装阶段并行准备解析；正式consumer只读取final/accepted raw或pack，不使用partial。
6. 不逐cell回来请求批准；普通工程问题solve-and-continue。只有科学合同、authority、correctness、GPU锁、OOM/shape unsupported才STOP。

---

## 3. 冻结公开尺寸

GPT-3-175B公开FFN：
- hidden H = 12288
- FFN = 4H = 49152
- 原模型为两层GELU FFN，不使用Qwen式gate/up/down语义。

本任务命名：

| point | M | K | N | 含义 |
|---|---:|---:|---:|---|
| EXPAND_M1 | 1 | 12288 | 49152 | FFN升维，M=1形状控制 |
| EXPAND_M256 | 256 | 12288 | 49152 | FFN升维，M=256形状控制 |
| CONTRACT_M1 | 1 | 49152 | 12288 | FFN降维，M=1形状控制 |
| CONTRACT_M256 | 256 | 49152 | 12288 | FFN降维，M=256形状控制 |

M=1/256是局部shape实验，不自动等于自然decode/prefill。

---

## 4. 静态容量与W4布局

### FP16 Dense
每个主FFN矩阵：
- 参数量：603,979,776
- FP16 bytes：1,207,959,552 = 1152 MiB

### W4代理，group_size=128
对两个方向参数量相同：

- qweight shape = `[K, N/8]` int32
- qzeros shape = `[K/128, N/8]` int32
- scales shape = `[K/128, N]` FP16

每矩阵：
- qweight = 301,989,888 B = 288 MiB
- qzeros = 2,359,296 B = 2.25 MiB
- scales = 9,437,184 B = 9 MiB
- 合计 = 313,786,368 B ≈ 299.25 MiB

RTX4080 accepted L2 = 67,108,864 B = 64 MiB。

关键规模关系：
- 旧Qwen2.5 AWQ qweight约32.4MiB，可整体小于L2；
- GPT-3尺寸W4 qweight 288MiB，约4.5×L2，不能整体驻留。

这正是本轮规模外推的核心变量之一。

---

## 5. 复用的split策略

Arm A：
- accepted AutoAWQ kernel
- split_k_iters=8
- 8-plane FP16 scratch
- 独立sum(0) reduction

Arm B：
- accepted split1 direct-output binary
- split_k_iters=1
- 同一GEMM内核家族/布局/反量化数学
- 无独立reduction

不得新增split2/4/16。

预测grid（m16n128，M256含16个M tiles）：

| point | B split1 GEMM grid | A split8 GEMM grid |
|---|---:|---:|
| EXPAND_M1 | 384 | 3072 |
| EXPAND_M256 | 6144 | 49152 |
| CONTRACT_M1 | 96 | 768 |
| CONTRACT_M256 | 1536 | 12288 |

预测scratch（FP16 `[split,M,N]`）：

| point | B bytes | A bytes |
|---|---:|---:|
| EXPAND_M1 | 98,304 | 786,432 |
| EXPAND_M256 | 25,165,824 | 201,326,592 |
| CONTRACT_M1 | 24,576 | 196,608 |
| CONTRACT_M256 | 6,291,456 | 50,331,648 |

Lane8必须独立复算，不只复制本表。Lane7动态launch audit必须验证后才能解释timing。

---

## 6. 合成数值合同

### FP16 Dense基线
只做shape/kernel anchor，不研究训练权重分布。

- dtype：FP16
- weight：固定有限非零小值，避免溢出；精确公式由Lane8冻结并写入manifest
- input：固定可复现有限模式；精确公式同样冻结
- 不使用原始GPT-3权重
- 不比较模型质量

### W4代理
不声称GPT-3量化模型。

- group_size=128
- qweight/qzeros/scales采用固定、非退化、可重复的合法packed模式
- 输入采用固定小幅FP16模式
- A/B必须对同一bit-exact tensor运行
- A/B elementwise `rtol=1e-2, atol=5e-2`
- 全finite
- 不要求与FP16 Dense基线数值相等

---

## 7. 访存状态

沿用Lane7已经资格化的两种准备：

### WARM_SAME_ARM
每个timed sample前，同一arm做2次untimed warmup，然后测目标。

### EVICT_CONDITIONED
同样2次same-arm warmup后，完整遍历同一块独立256MiB int32 buffer一次，再测目标。

- conditioner = 268,435,456 B = 4×L2
- 与目标input/weight/scratch地址区间必须不重叠
- 不使用empty_cache
- 不使用persisting hint
- conditioner在timed event/NVTX target之外

只能称“独立大buffer扰动后的状态”，不能称所有cache完全cold，也不能唯一归因L2。

---

## 8. GPU执行矩阵

### Track A：FP16 Dense shape anchor
四点：
- EXPAND_M1
- EXPAND_M256
- CONTRACT_M1
- CONTRACT_M256

只做warm基线：
- 10 warmups
- 50 CUDA-event samples
- 记录min/median/max/mean/CV
- launch inventory
- M256两个方向各一个限定NCU profile

### Track B：W4 split/state proxy
四point × 2 arms × 2 states = 16 cells。

每cell 50 samples，25个complete mirror blocks。
每point mirror order：

`A_W, B_W, A_E, B_E, B_E, A_E, B_W, A_W`

这会给每cell每block 2个样本，总50。

NCU只对M256：
- 2 operators × 4 cells = 8 profiles
- application replay
- cache-control none
- metrics：
  - `l1tex__t_bytes.sum`
  - `lts__t_bytes.sum`
  - `dram__bytes.sum`
  - kernel duration
- A的GEMM和reduction分列
- B只有GEMM
- 不做tensor-level attribution

总计NCU 10份（2 Dense + 8 W4）。

---

## 9. 预注册解释问题

新实验完成后只回答：

1. GPT-3尺寸下，M1是否因为N更大而减少对split8提供额外CTA的依赖？
2. M256下，split1与split8的方向是否与旧7B up/down一致？
3. qweight从<L2变成约4.5×L2后，W/E状态交互是否减弱、增强或改变方向？
4. EXPAND与CONTRACT是否仍表现不同，能否由grid供给与workspace/reduction差异共同解释？
5. FP16 Dense anchor的kernel/traffic量级是否支持“这是一个真正的大Dense工作集”这一规模定位？

不得从本实验推出：
- GPT-3原始checkpoint性能；
- 完整96层端到端收益；
- 原始GPT-3自然激活分布；
- GPT-3量化效果；
- 唯一L2/cache因果；
- 多GPU TP/PP系统性能。

---

## 10. 何时值得后续SASS/模拟

本轮不自动抓trace，不运行Accel-Sim。

只有当：
- 至少一个关键point出现相对旧7B清晰的方向变化/交互变化；
- correctness与launch identity闭合；
- native结果提出明确的可模拟机制问题；

才单独设计1–2个代表point做bounded SASS capture。

否则native screen关闭即可。

---

## 11. Git / authority

Coordination branch：
`hrl/c16-gpt3-public-shape-scale-transfer-v1-coordination`

Coordination base：
`3aad5887b9b4c5bec801962bf8035fed9d485f47`

旧split/state authority：
`C16_SPLITK_MEMORY_STATE_INTERACTION_109_V1`

旧A/B authority：
`C16_LOWBIT_SPLITK_NATIVE_AB_109_V1`

GPT-3公开尺寸与文献边界：
`docs/vm_tlb/chatgpt_handoff/c16/gpt3_public_shape_scale_transfer_v1/GPT3_PUBLIC_SHAPE_AUTHORITY.md`

对应完整LR08阅读记录固定于commit `139135231fb30b4981eedb031da9c7e182269652`，如需全文用该commit读取，不依赖当前coordination branch是否包含literature历史。

本任务不修改历史packs。
