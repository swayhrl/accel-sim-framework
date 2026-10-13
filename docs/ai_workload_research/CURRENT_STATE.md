# AI负载体系结构研究｜当前协调状态

> **快照日期：2026-10-13。只读科研导航；不是实时任务看板，不授予执行权限。**

| 主线 | 最新证据入口 | 当前科学状态 | 后续操作边界 |
|---|---|---|---|
| C16 | [`635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f`](https://github.com/swayhrl/accel-sim-framework/commit/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f) | Stage A停止；10候选中0正式准入，2个未准入问题保留 | 无新C16 GPU/holdout/机制授权；研究目标保留 |
| AWMA·地址翻译/Pre-L1 | [机制资格化记录](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_PREL1_COALESCER_PAPER_QUALIFICATION_V1/FINAL_QUALIFICATION.md) | 模拟器与独立样本支持有范围的翻译服务抑制；运行加速有正/零/负 | 保留独立论文证据，不推断真实4080整模型加速 |
| AWMA·在线稀疏分派 | [`99d05f0ad221a1d44dd11bac0ed83965bb2c0942`](https://github.com/swayhrl/accel-sim-framework/commit/99d05f0ad221a1d44dd11bac0ed83965bb2c0942) | 固定公开批次的局部在线净时间正结果；非稳定普遍端到端提升 | 不自动推硬件 |
| AWMA·训练梯度容量 | [R26审查](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/R26_TIED_WEIGHT_CAPACITY_REVIEW_2026-10-02.md)；[R27R2审查](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/R27R2_VARIED_BATCH_CAPACITY_REVIEW_2026-10-13.md) | R26重复输入条件下增加1个物理Batch；R27R2不同输入数值未资格化 | 不改原合同，不声称真实多样batch容量效果 |
| AWMA·R27R3 | [execution](https://github.com/swayhrl/accel-sim-framework/commit/7bd31fae4c54e121d54743a803d978ee02a64959)；[独立审阅](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md) | **接受**`R27R3_B0_REFERENCE_NOT_REPEATABLE`；同样起点/B1/固定bank k0两次B0，25/262,668,288 BF16总梯度元素超过原容差；内核归因未知 | R27R3 COMPLETE/STOP；未运行C1/S2组件归因、容量或32步；**无新AWMA GPU授权** |

## 下一步的科研组织

- 统一问题图谱和证据索引已发布为V1；训练与推理、LLM与非LLM均在研究范围。
- R27R3证据按[独立审阅接受后的E-A13](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)归档；协调分支不把该B0重复性失败升级为硬件瓶颈，也不以此重启旧实验。
- 后续文献阅读与各项目既有实验并行，先查已解决的软件能力、观测范围和剩余约束。
- 实验只由具体可证伪问题触发；发现性小实验与正式机制验证分开。
- 共享资源不变：109 GPU按既有锁串行；174-new科研分析和模拟按原授权；164负责大文件的长期保存。
- 本文件不安排新Goal，不判定尚待审查的AWMA执行结果为accepted。
