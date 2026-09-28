# Lane 8 — GPT-3公开尺寸实验准备与冻结

执行节点：174-new  
Lane：8  
角色：CPU-only prep / contract freeze / static validator  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4、Lane6、Lane7

任务：`C16_GPT3_PUBLIC_SHAPE_PREP_174NEW_V1`

## 1. 目标

把MASTER_PIPELINE中的实验合同变成109可直接执行的冻结资产，使Lane7不需要在GPU窗口里临时决定shape、tensor布局、计时协议或分析规则。

本Lane不运行GPU、不构造大GPU tensor、不做native timing。

## 2. 必读authority

- `docs/vm_tlb/chatgpt_handoff/c16/gpt3_public_shape_scale_transfer_v1/MASTER_PIPELINE.md`
- LR08 GPT-3笔记
- `3aad5887b9b4c5bec801962bf8035fed9d485f47`
  - split-state最终pack
- `0e88faa28c9066b48e394dce657d7a16e6332a32`
  - 原A/B pack与runner
- `INPUT_AND_WEIGHT_BINDINGS.tsv`
- `SOURCE_PATCH.diff`

## 3. 第一阶段：尽快冻结接口，允许Lane7流水启动

先完成最小静态审计并立即push一个中间commit，包含：

`docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_PREP_174NEW_V1/PRE_GPU_CONTRACT_FROZEN.json`

至少冻结：
- 四个M/K/N；
- evidence class命名；
- FP16 Dense与W4代理严格分开；
- group_size=128；
- A/B binary authority SHA；
- grid/scratch公式；
- state protocol；
- timing block协议；
- NCU scope；
- correctness tolerance；
- synthetic tensor公式的版本号；
- 禁止项。

状态必须明确：

`CONTRACT_FROZEN_CPU_PREP_CONTINUES`

这个commit push后，Lane7可以开始CPU-only bootstrap，但仍禁止CUDA/GPU lock。

不要为了等所有review pack文件完成而延迟该第一commit。

## 4. 第二阶段：并行完成全部CPU准备

第一commit发布后继续完成：

### 4.1 独立复算静态数学

不能只复制master表。用独立脚本复算并单元测试：
- dense parameter count/bytes；
- W4 qweight/qzeros/scales shapes与bytes；
- M1/M256 input/output bytes；
- split1/split8 scratch；
- 预计grid；
- qweight/L2比例；
- 16GB峰值上界预算。

输出：
- `SHAPE_AND_MEMORY_BUDGET.tsv`
- `EXPECTED_LAUNCH_AND_SCRATCH.tsv`

### 4.2 冻结合成tensor算法

实现一个纯函数规范，不生成巨大文件。

建议版本 `GPT3_SHAPE_SYNTH_V1`：

Dense FP16：
- weight每次只生成当前operator；
- 固定小非零值/简单可审计模式；
- input固定有限模式；
- 不研究数值分布。

W4：
- qweight int32 packed fixed nondegenerate nibble pattern；
- qzeros fixed legal packed pattern；
- scales FP16固定小正数；
- input与Dense独立、固定小幅模式。

要求：
- 不依赖Python hash/random全局状态；
- 公式可以在CPU tiny-shape上单测；
- 给出tiny reference hash；
- 大tensor只由109在GPU锁内按同公式生成。

如果packed zero-point编码从现有AutoAWQ source无法静态闭合，STOP，不猜。

### 4.3 生成109 runner骨架

在`util/vm_tlb/c16/`准备：
- producer prepare脚本；
- locked runner；
- launch validator；
- analyzer；
- raw reseal/hash脚本。

runner必须：
- 不加载任何完整模型；
- 直接使用accepted A/B extension binary；
- 只生成当前operator所需tensor，完成后释放，控制峰值；
- conditioner只分配一次并复用；
- CUDA相关import/调用必须只发生在GPU锁内阶段；
- Dense和W4结果目录分开。

### 4.4 旧结果比较contract

生成：
`OLD_QWEN_COMPARISON_CONTRACT.json`

绑定旧Qwen：
- qweight bytes；
- L2；
- 四point grid；
- M1/M256旧timing；
- M256 state interaction。

只冻结读取来源和比较字段，不预写新结论。

## 5. PRE_GPU_READY gate

最终只有以下均通过才能写：

`PRE_GPU_READY.json`

内容包括：
- prep branch + HEAD + tree；
- master coordination SHA；
- A/B binary SHA；
- synthetic formula SHA/version；
- expected shape/grid/scratch表SHA；
- runner source SHA；
- memory peak bound；
- unit tests PASS；
- no GPU used；
- Lane4 partial not accessed。

如果静态估算显示任一operator在“当前operator + conditioner +最大scratch + Dense/W4必要tensor +合理workspace裕量”下可能超过16GB，禁止109直接尝试，先收紧执行顺序/内存生命周期；不能靠OOM试错。

## 6. Git

从coordination branch建立：
`hrl/c16-gpt3-public-shape-prep-174new-v1`

中间contract commit和最终READY commit都必须push。

最终：
validate -> tests -> git diff --check -> SHA256SUMS -> push -> fetch-back commit/tree -> clean -> STOP

汇报必须用中文说明：
- GPT-3尺寸是什么；
- 哪部分是真正FP16 Dense shape anchor；
- 哪部分只是W4机制代理；
- 预计是否适配16GB；
- Lane7现在是否可合法启动GPU。
