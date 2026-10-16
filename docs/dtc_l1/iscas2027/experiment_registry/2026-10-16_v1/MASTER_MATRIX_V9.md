# DTC-L1 实验台账 V9：2026-10-16已发布最新检查点

**证据来源**：Lane A `b7444fe6bfe453cfe33ee815f2bfb02afad133ea`，其最后可复核的完整性能检查点`checkpoint_20261016T1325Z`（UTC13:24:28）；Lane B `d46cce269b88055decc2ca052dcb9baae0efee7e`；实验授权与派生Hotspot A审阅包沿用上一版V8。这是已推送GitHub的**状态快照**，不是通过实时读取174进程所得的新运行状态。

## 完成与剩余

| 项目 | 本次发布状态 |
|---|---|
| 原44行R2 | **33 terminal/invariant PASS，8 RUNNING，3 admission HOLD，0合法未启动**。33中原Hotspot2行为执行合格、科学采纳HOLD |
| 完整三设计主实验 | Btree、2DConvolution、GEMM、DWT2D、Gaussian、LUD、NN、MRI-Q **8个原输入负载**数值闭合 |
| 运行中的8行 | BICG IO256/IO128/WAIT128；ATAX IO256/OO128；GESUMMV IO256/OO128/TRAD96 |
| 派生Hotspot V2 | 新身份、独立5/5 strict PASS：B16 152914；TC80 107774；TRAD96 82873；IO256 85718；OO128 84456 cycles。此处TRAD96最快；未混合旧输入 |
| Btree/2D/LUD | Lane B已结束有界来源调查，均`UNRESOLVED_FORMAT_APPLICABILITY`；原数值terminal PASS保留，科学适用性待审 |
| 现代4080 DTC | 固定128KiB data/shared与端口协议不合法，HOLD；原生109和baseline-only证据分别按原范围保留 |
| 实施成本 | 统一RTL/DC/存储宏/时序评估尚待实际硬件材料；不能写等面积优势 |
| 总性能 | **GM12不可计算/不可刊出**：原义Hotspot及另外3个输入的捕获语义仍未全闭合；不能为了得到平均值挑选或剔除负载 |

## 科学判断

这轮执行流程已经实现“独立行尽早启动、terminal后严格验收、旧结果复用、失败不覆盖”。主实验接下来的等待时间主要由剩余8条自然完成决定，无需增加独立仿真矩阵或重新建立runner。

当前重要效应的双向性：
- 原BICG OO128为47,533,116 cycles，增强传统TRAD96为25,353,488，OO/传统加速仅0.533×；负结果不能隐去。
- 新派生Hotspot IO/OO均优于小传统和80KiB传统，却均略慢于增强传统（相对TRAD96分别0.967×/0.981×）。
- Btree/2D曾给出有利DTC数字，但原trace实际producer未绑定；只可报告为**固定已解码历史输入的有条件模拟观察**，需科学来源/稳健性证据后才可升级真实应用趋势。
- LUD global source model支持冻结地址、但仍未绑定原SASS/producer；同样不是native/全输入确认。

**优先行动：**(1) Lane A原任务保持活跃，8行自然完成且strict验收，不重发Goal；(2) 暂不重启Lane B无限溯源，若用户明确授权再做限界的Btree/2D双解释稳健性，而非盲重抓全部trace；(3) 并行补硬件面积、关键时序和论文有效方法/图表，任何缺项不填假数字。下一轮对比状态须fetch最新严格commit和失败收据，不能用本文件冒充机器实时状态。

所有先前V1–V8版本保留。本次仅变更独立文档branch，不改模拟器Core、配置、运行分支、调度器、原trace或科学HOLD。
