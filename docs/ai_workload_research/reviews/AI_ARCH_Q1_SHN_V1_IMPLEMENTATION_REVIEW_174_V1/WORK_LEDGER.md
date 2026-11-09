# shN V1 额外工作账（源码推导）

固定输入：`2838e93cfc129183d7d727e80eccc1b2f577a82d` 的 `FORMAL_SAMPLES.tsv`、`shn_candidate.py`；推导脚本为本目录的 `derive_work.py`。以下是逻辑操作数和调用次数的界，不是实测 PCIe/DRAM 流量、kernel 数或耗时。每个正式样本有 51 个自然 step，`shN` 每行 45 个 FP32 元素，块长 32768。

| ON 样本（同窗各5个近似相同） | U 更新行总数 | 下一camera可见行总数 | 更新+预测分块迭代界 | ID/年龄 H2D 操作数 | 四份状态 gather 操作数 | 预测 cat 输出复制操作数 |
|---|---:|---:|---:|---:|---:|---:|
| 发现窗 pair1 | 47,090,821 | 39,624,309 | 2,648–2,748 | 1,387,442,080 B | 62,434,893,600 B | 7,132,375,620 B |
| 验证窗 pair1 | 48,612,391 | 41,888,784 | 2,763–2,863 | 1,448,018,800 B | 65,160,846,000 B | 7,539,981,120 B |

`_rows` 每次被 `update(U)` 和 `forward(visible)` 调用。每步各建 `correction/p1/p2` 三张16项FP32表，即每正式样本306次小表构造、19,584 B表载荷；这不等于306次独立物理传输。每个分块做 CPU `part.long()`、counter `index_select`、年龄范围检查；更新块还做 CPU `part.unique()`。随后传 `idx` 与 `age` 两个 int64 数组，故 ID/年龄上传的逻辑操作数为 `16×(U+visible)` B。GPU 端每块有3次表 `index_select`、4次45维状态 `index_select`，再由逐元素Torch表达式创建 `m,v,restored,result` 及中间项；更新块各有3次 `index_copy_`。预测块保留结果，最后一次 `torch.cat` 复制 `visible×45×4` B。四份状态 gather 的**源码级操作数**为 `4×45×4×(U+visible)` B，表 gather 为 `12×(U+visible)` B；缓存命中、融合、临时张量复用及真实设备流量均未知。

每步的分块迭代数未在固定Git逐步公开；总行数给出的界是 `ceil(U/32768)+ceil(visible/32768)` 到该值加100。`visible` 可含重复ID；更新U需要唯一。CPU `valid` 梯度清零的索引形态及由此产生的CPU/GPU搬运量，固定源码片段无法定量；不能把它算成零。

已有诊断只在OFF报告51次CPU Adam区间、299/303次全部CPU参数forwarding和逻辑copy operand bytes。ON关闭报告明示无逐操作transfer/region observer，ON新增更新、预测、索引、等待成本均为 `unknown`。`gpu_forward_backward` 的CUDA event不覆盖这些在train变换中新增的调用，且event span包含launch间隙。Host与设备时钟区间不可相减作因果分解。
