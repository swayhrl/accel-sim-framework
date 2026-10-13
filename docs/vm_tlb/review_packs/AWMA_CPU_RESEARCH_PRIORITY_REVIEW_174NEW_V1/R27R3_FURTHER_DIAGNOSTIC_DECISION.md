# R27R3 是否值得再定位
建议：**暂存**。未建议立即另批数值 GPU 实验。

## 已知与未知
来源：执行 `7bd31fae4c54e121d54743a803d978ee02a64959`；独立审查 `d6e9bbfb562814bcd5dc5adb444d3c572e7f446b`。原冻结逐元素规则为 `|got-ref|<=0.01+0.01*|ref|`。本轮标准库脚本复核了 25 个唯一坐标（表中 first/top 各 25 行是同一集合）；198/284 行分别 12/13 处，输入总数及 label 总数均 127。最大超限 (198,604) 差 0.09375，double 重算门槛 0.0640625，与 published FP32 门槛微小舍入一致。

所有失败行都参与 lookup，但 198 只出现一次，所以 repeated-token collision 不是充分解释。总梯度是 classifier 与 lookup 两支合并的结果：旧 R26 `component.py:365–435` 明确 B0 先取得 CCE dH/dW，再 native backbone/embedding backward，BF16 `W.grad.add_(dc)`；C1/S2 用 compact lookup 与 full/tiled classifier gradient 合并。图中没有分量误差测量，R27R3 `NUMERIC_ATTRIBUTION.json` 明确 component comparison 未运行。dH 在门内但非 bitwise，也不能从参与行反推具体 kernel。

CPU_RECHECK 只证明 published 数值和频次内部一致；没有独立读取完整 raw、验证训练质量、定位根因或改写 R27R2 数值 STOP。mean/cosine 和本步 W/m/v 通过不覆盖原梯度门。

## 投入价值
R26 的重复序列 tied-W-only 五步数据为一物理 batch 边界移动；共同 B70 整步峰值 S2 高 3.828 MiB、三组正式时间 MIXED。R27R2/R3 尚无多样输入容量结果。当前没有训练损失/收敛质量异常，也没有性能或容量限制能独立支撑广泛 numerical-order 研究。先把排障做到完美再找课题的收益不明确。

若未来出现独立任务质量或容量动机，**最多一个**可区分设计是：原 Llama revision、R26 common state、WikiText bank k0/B1 下两 fresh processes，按原 B0 阶段同时保存 hidden/LSE/dH 摘要、classifier dW、native lookup dW 和合并结果的 198/284 行及事前控制行；先判断误差来自上游、某支或 BF16 merge。保持原门槛，记录插桩导致的同步/内存扰动，不能把 observed arm 当 unchanged timing baseline。若匹配上游不成立，分量对比保持 UNKNOWN；不得循环重采到过门，最多两控制步骤，禁止 C1/S2 修正、容量、32 步及性能测量。开发成本包括安全 observer 与阶段身份核验，结果最多是根因线索，不直接成为硬件 headroom。本设计未进入候选名单、没有运行授权。
