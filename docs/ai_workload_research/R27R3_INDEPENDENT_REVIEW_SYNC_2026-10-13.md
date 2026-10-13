# AWMA R27R3 独立审阅结果｜协调层同步记录

**同步日期：**2026-10-13  
**性质：**研究证据导航更新，不是AWMA或C16的实验授权，也不修改任何历史结果。

## 固定权威

- AWMA R27R3执行commit：[`7bd31fae4c54e121d54743a803d978ee02a64959`](https://github.com/swayhrl/accel-sim-framework/commit/7bd31fae4c54e121d54743a803d978ee02a64959)。
- 执行tree：`bcd3a9ab5890a946d03a49b46df4434abff4238c`；直接父提交为冻结handoff `29ce051f982f3854bd4392a94e4195c59340123b`。
- 独立AWMA科学审阅：[`R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md`](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md)，审阅commit `d6e9bbfb562814bcd5dc5adb444d3c572e7f446b`。
- AWMA当前科学状态快照：[`STATUS_AFTER_R27R3_REVIEW_2026-10-13.md`](https://github.com/swayhrl/accel-sim-framework/blob/f0a6ec310c09cd011fffbe8a5ca22d6effacdf6b/docs/vm_tlb/literature_notes/awma/plans/STATUS_AFTER_R27R3_REVIEW_2026-10-13.md)，提交 `f0a6ec310c09cd011fffbe8a5ca22d6effacdf6b`。
- 原始证据入口：[`R27R3 review pack`](https://github.com/swayhrl/accel-sim-framework/tree/7bd31fae4c54e121d54743a803d978ee02a64959/docs/vm_tlb/review_packs/AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1)；node164 raw按执行收据引用。

## 已接受的事实与证据级别

- **研究对象：**meta-llama/Llama-3.2-1B固定revision、RTX4080/SM89、BF16 tied embedding/lm_head W、FP32 AdamW优化器状态；只有tied-W训练，其他backbone权重冻结但参与forward/dH backward。
- **输入与阶段：**已资格化WikiText-2 raw train parquet、确定性bank `[33,128,128]`；固定bank k=0、物理B1，训练完整梯度及一步更新。
- **控制变量：**B0-vs-B0两个fresh process；同一R26 common CPU checkpoint/RNG、同一输入、同一冻结PyTorch/CUDA/CCE后端。没有C1/S2候选对比，也没有capacity。
- **原始观测指标：**BF16完整总梯度 `[128256,2048]` 共262,668,288元素，原逐元素门限 `|x_2-x_1| ≤ 0.01 + 0.01|x_1|`；25元素超限（行198有12处、行284有13处）。最大超限坐标(198,604)，5.40625 vs 5.3125，绝对差0.09375，允许0.0640625；其余loss、next-loss、dH、W、FP32 m/v、step、cursor均通过。
- **接受结论：**`R27R3_B0_REFERENCE_NOT_REPEATABLE`，只表示这个冻结输入/硬件/软件和判据下B0跨进程重复性未资格化；STOP正确。源代码归因、修正、容量、32-step均未执行。
- **独立核查：**reviewer从Git精确commit/tree/ref核验，独立重新计算20/20 Git review-pack文件SHA256并复核25坐标计算/阈值、源码控制顺序；node164的21项及两份各3,152,550,620-byte raw张量由执行侧回读，本次审阅未直接SSH重读/重新运行。
- **禁止外推：**不证明B0数学错误、不证明C1/S2错误或正确、不解释kernel级根因、不否定R26单重复序列一physical-batch容量发现、不声称 varied-input capacity/训练收敛/性能或硬件headroom。

## 对统一问题图谱的贡献

- **P08**：梯度/优化器状态研究不仅是内存物化成本，还必须建立跨运行的合法数值参考和状态可比性。
- **P09**：浮点归约顺序与数值门限可能限制等价实现的可鉴定性；本次是“参考重复性门槛未过”的本机实测，**不是**数值归约kernel根因已确认。
- 对应跨项目证据条目：**E-A13**；本同步仅将`REPORTED_PENDING_REVIEW`提升为“独立审阅接受的有限STOP”，不改变任何其他E-Axx/E-Cxx科学结论。

## 执行权限边界

协调分支不产生R27R4、不授予GPU/模拟器/Profiler/模型下载/holdout/硬件任务。若要开展新的native BF16确定性/数值参考研究，必须由AWMA项目独立制定新合同、预算、合法对照和STOP门槛。C16 Stage A仍关闭；109锁、174/164职责按原项目执行合同保持不变。
