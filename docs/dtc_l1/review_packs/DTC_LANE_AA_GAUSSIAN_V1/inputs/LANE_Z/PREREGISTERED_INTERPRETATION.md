# K0/K1 × logical Tag — preregistered interpretation V1

此文件冻结结果解释规则，不授予新 sim 执行权。Z 只消费 A/M/T 固定提交；没有读取 U 的状态、进度、partial BICG cycles 或新结果。U 必须在整个授权组自然终态、strict 完整通过、正式审查包发布且身份/SHA可核之后，才可在后续消费阶段读取。缺任何门槛不探测、不排序、不选择性读取；失败或缺失最终也须完整保留。此合同的 commit 与 push/fetch-back 回执是将来的消费前屏障；不得声称早于已经完成的 T 探索。

这里 `C(K,Tag)` 表示完整输入的 cycle 数，不是传统 C+ 设计。K0 预定义为旧语义：kernel 边界沿用既有普通 L1 flush/invalidate 行为，DTC 可查询 retained mappings 不新增边界清除。K1 预定义为 opt-in DTC kernel-boundary invalidation，在正式实现所声明且已验证的无 live Ref/pending/ownership 的安全边界清除映射。K1 具体 hook、开关、回收/计数与 drain 次序须由 X 正式 source/strict 合同绑定；不自动把 flush、invalidate、kernel launch 与 kernel complete 当同一事件。合同不符先登记偏差，不重命名 K 以迁就结果。

每个预先固定输入须完整展示四格；新结果当前一律 `NOT_CONSUMED`。K0 新 anchor 也不能直接用旧 Core/observer 的 T 周期替代。必须同 source/build/runtime/clock/observer、同完整有序 trace、同 effective options，除策略和 Tag 外匹配：OO128、physical640×128B、side16KiB、shared96KiB、cap32768、64SM、4 Tag banks及既有 finite 服务参数。exact config echo、源码及四格身份将来逐项封存。设计与 Tag 的硬件成本和时序不由此验证。

| cell | Tag sets×ways | 失效策略 | cycles / strict / UUID |
|---|---|---|---|
| C(K0,32×4) | 32×4 | retain legacy DTC mapping | NOT_CONSUMED |
| C(K0,64×8) | 64×8 | retain legacy DTC mapping | NOT_CONSUMED |
| C(K1,32×4) | 32×4 | opt-in boundary invalidate | NOT_CONSUMED |
| C(K1,64×8) | 64×8 | opt-in boundary invalidate | NOT_CONSUMED |

固定比率方向如下，均为 cycles quotient，>1 表示分子设计周期更长，不混用 speedup 的倒数。

| 比较 | 预注册表达式 | 判读 |
|---|---|---|
| 同Tag K1/K0，小Tag | Q32=C(K1,32×4)/C(K0,32×4) | >1表示 K1 较慢；<1表示 K1 较快 |
| 同Tag K1/K0，大Tag | Q64=C(K1,64×8)/C(K0,64×8) | 同上 |
| 同K0 大/小Tag | T0=C(K0,64×8)/C(K0,32×4) | <1表示扩大Tag降低周期 |
| 同K1 大/小Tag | T1=C(K1,64×8)/C(K1,32×4) | 同上 |
| 交互 | I=Q64/Q32=T1/T0；同时报 log(I) | I>1表示 K1 在大Tag下的相对周期惩罚更大（等价于大Tag收益在 K1 下减弱）；I<1相反；I=1无乘法交互 |
| 加性交互，描述性辅项 | Δ=[C(K1,64×8)−C(K0,64×8)]−[C(K1,32×4)−C(K0,32×4)] | GPU cycles；不命名 retained-mapping 的精确因果周期份额 |

无有效四格时只报有身份的原值，交互 `UNAVAILABLE_INCOMPLETE_FACTORIAL`。不按完成顺序计算中间排行榜；strict 失败不填周期零，不以别的 Tag/输入补格。无重复运行估计时不声称统计显著；不按结果调门槛或删除负收益。使用未舍入整数计算；零周期/分母不合法，记录失败。

固定报告模板（逐输入和每个原 kernel ordinal）：四格 cycles、UUID/strict/hash、Q32/Q64/T0/T1/I/logI/Δ；随后报告 ready/pending/new 的原 count 与 D、lower-created/injected 的独立值、Tag eviction、mapping 可查/失效计数及可用性、PIB/physical 积分与 samples、四项 post-ready sum/retired、map-loss sum/count、L2 sector/retry 及分母、DRAM issued commands/atom 与字节。缺字段原样列出；不得只展示显著下降的一项。kernel 保留原顺序、名称、stream、active instructions、ROI 与完整数目，不按 kernel 另挑 Tag。

解释预承诺：

1. **单 kernel 受限收益。** GEMM 原输入只有一个 kernel；扩大 Tag 的旧收益不能解释成跨 kernel retained reuse。若新 K0/K1 单 kernel 周期有差，先查实际 hook 是否只在末尾、安全边界是否不同、clock/observer/初始状态是否匹配，不能归为跨 kernel 复用。
2. **跨 kernel retained-mapping 收益。** 多 kernel 输入若 K1 相对 K0 变慢，且 ready 降低、lower 创建/注入增多、后继 kernel 周期恶化，可说与保留映射收益一致；没有 line+generation 跨边界关联、直接映射计数和统一事件边界时仍不能确证哪条映射被复用。K1 反而更快或扩大Tag在K1仍有收益时完整保留，并收缩旧解释；不能把全段差额都命名跨kernel因果收益。
3. **post-ready 退化。** whole-run 降低同时 ready-to-complete、ready-to-collect 或 collection 均值上升，明确并列报告：总吞吐与条件服务区间可以反向。失效策略改变样本人群，map-loss 的均值/计数也必须并列，不由均值推额外miss或瓶颈消失。
4. **相反或不闭合结果。** K1改善、I反向、Tag收益消失、DRAM增多、kernel异质性、结果与T相反，均按同一模板报告；不能在看到结果后改组、选Tag或挑kernel。机制相关性不能升级为逐周期精确因果分解。

发现集 GEMM/Gaussian 单列；原 BICG/DWT2D accepted 旧证据也不等于任何新 holdout。条件派生 Hotspot/Btree 使用自己的 lineage/基线，原输入格式及 capture applicability HOLD 不被数值 PASS 解除。新结果、发现集、条件派生输入都不灌入原 GM12，不重算原主图或选择每负载最佳 Tag。若未来需要任何新汇总，须另行先固定 cohort/分母，使用新名字、完整 paired coverage 并保留逐输入结果。本任务不写 v0.13 论文。
