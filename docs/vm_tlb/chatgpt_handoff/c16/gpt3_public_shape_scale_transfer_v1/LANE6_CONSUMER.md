# Lane 6 — GPT-3公开尺寸规模外推 Independent Consumer

执行节点：174-new  
Lane：6  
角色：CPU-only independent consumer / cross-experiment comparator  
GPU：禁止  
GPU lock：禁止  
允许并行：Lane4、Lane7、Lane8

任务：`C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_CONSUMER_174NEW_V1`

## 1. 可以立即做的CPU-only准备

在新producer尚未完成时即可：
- 读MASTER_PIPELINE；
- 读Lane8 prep合同；
- 读取旧Qwen A/B与split-state结果；
- 建立consumer scaffold；
- 独立复算旧Qwen的shape、qweight/L2、grid、timing与state interaction字段；
- 冻结跨实验比较公式和输出schema。

禁止：
- 读取Lane4 partial；
- GPU/CUDA；
- 将未来producer summary预填成结果；
- 修改旧packs。

## 2. 等待producer的方式

Producer branch预期：

`hrl/c16-gpt3-public-shape-scale-transfer-109-v1`

可以每180秒检查一次remote branch，最长120分钟。

正式重算的开始条件：
- producer final commit已push；
- review pack存在且SHA闭合；
- producer合同绑定Lane8 PRE_GPU_READY；
- GPU lock receipt显示合法释放；
- correctness/launch gate状态明确。

如果producer只完成部分point，consumer照实消费合法部分，不要求109补跑以凑表。

## 3. 独立重算

不要把producer的derived summary当计算authority。

从raw samples/rows重算：

### Dense
- 每point n/min/median/max/mean/CV；
- launch inventory与shape；
- M256 NCU frozen metrics；
- 只说明GPT-3公开尺寸的实际Dense anchor，不与W4数值结果直接等同。

### W4
每point / arm / state：
- timing分布；
- gain_W = 1 - B_W/A_W；
- gain_E = 1 - B_E/A_E；
- state_interaction = gain_W - gain_E；
- complete-mirror-block bootstrap，seed 20260928，1000重采样，q05/q50/q95；
- correctness；
- grid/reduction/scratch；
- M256 NCU source rows。

## 4. 与旧Qwen进行严格匹配比较

旧authority：
`3aad5887b9b4c5bec801962bf8035fed9d485f47`

只比较同一accepted split8/split1 implementation family和相同W/E protocol。

构造：

`SCALE_TRANSFER_COMPARISON.tsv`

至少包含：
- model_shape_class：Qwen7B accepted / GPT3-public-shape proxy
- role：EXPAND-like / CONTRACT-like
- M：1/256
- K/N
- split1 GEMM grid
- split8 GEMM grid
- qweight bytes
- qweight/L2
- A/B warm gain
- A/B disturbed gain
- state interaction
- bootstrap区间
- DRAM change where NCU exists

重要：Qwen的up/down与GPT-3的expand/contract只是形状方向类比，不是模型语义完全相同。

## 5. 主要科学问题

### 5.1 M1并行度规模效应

旧Qwen：
- up M1 split1 grid 148
- down M1 split1 grid 28

GPT-3 proxy预期：
- expand M1 grid 384
- contract M1 grid 96

分析：
- split1在更大N下是否因CTA数量增加而减少M1退化？
- 若方向改变，是否与grid供给一致？

不能仅凭grid宣布因果；需要timing/launch共同支持。

### 5.2 工作集跨L2尺度变化

旧Qwen qweight约32.4MiB < 64MiB L2。
GPT-3 proxy qweight 288MiB ≈4.5×L2。

分析：
- W/E state interaction的绝对值和方向是否系统变化；
- warm状态下DRAM是否明显比旧Qwen更难降到极低；
- 若state interaction缩小，不直接说“因为权重放不下L2”，只能说与规模关系一致；
- 若interaction仍大，说明还有值得定位的状态变量。

### 5.3 EXPAND/CONTRACT差异

判断是否仍存在：
- EXPAND更受减少reduction/workspace收益驱动；
- CONTRACT更受并行度供给约束。

只用已测数据，不抽象成普遍定律。

## 6. 解释门槛

这次允许的结论强度：

### 强规模转移证据
满足：
- correctness/launch闭合；
- 至少一个对应point的split方向或state interaction相对旧Qwen出现清晰变化；
- 变化大于各自测量离散度，且bootstrap interaction区间支持；
- 形状/grid/workset变化给出一致但非唯一解释。

### 方向保持但幅度改变
如果所有sign相同、只interaction magnitude变化，就写成“规模改变了敏感度，但未改变策略方向”。

### 无明显规模效应
如果timing/interaction都在原有离散范围内，就关闭，不继续SASS。

不要为了得到“强结果”事后改变阈值。

## 7. 是否授权后续trace/simulator

Consumer只能**建议**，不能自动执行。

若确实出现有解释力的scale crossover，最多提出：
- 一个Qwen旧point
- 一个GPT-3 proxy新point

做后续bounded SASS/Accel-Sim的paired design。

否则：
- 不抓trace；
- 不跑full timing；
- 不把GPT-3加入模型列表只为数量。

## 8. 输出

Review pack：
`docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_CONSUMER_174NEW_V1/`

至少：
- `AUTHORITY_AUDIT.json`
- `OLD_QWEN_RECOMPUTE.tsv`
- `NEW_DENSE_RECOMPUTE.tsv`
- `NEW_W4_RECOMPUTE.tsv`
- `SCALE_TRANSFER_COMPARISON.tsv`
- `GRID_AND_WORKSET_INTERPRETATION.md`
- `NCU_COMPARISON.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

用户汇报必须中文清楚写：
- GPT-3公开尺寸改变了什么；
- split策略方向是否变化；
- 驻留状态敏感性是否变化；
- 这是不是值得做后续机制/模拟。

不要用机器标签代替主结论。

## 9. Git

建议branch：
`hrl/c16-gpt3-public-shape-scale-transfer-consumer-174new-v1`

普通工程问题solve-and-continue。
最终：
tests -> diff-check -> SHA256SUMS -> commit -> push -> fetch-back -> clean -> STOP。
