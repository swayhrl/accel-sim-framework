# Optional paper revision notes — review only

这些是供后续人工审查的可选修订建议；未修改v0.13，不把T1-C晋升论文主配置，也不重算原GM12。T的GEMM/Gaussian是发现输入；U的DWT2D/BICG是预先固定的两个holdout。四输入分别描述，不合并为新总体GM，也不按负载挑选Tag。

可选表述：固定物理池80KiB、OO128、lower cap32768及冻结有限服务模型时，从32×4增至64×8逻辑Tag，在四个已完成输入上分别观察到whole-run周期下降。应紧接列出各自cohort与完整数值，不写成普适机制定律或等面积比较。

| 输入 / cohort | oldOO→T1-C cycles | cycle变化 | lower创建变化 | DRAM read bytes变化 | ready-to-complete均值变化 |
|---|---:|---:|---:|---:|---:|
| GEMM / discovery | 1,377,919→1,071,405 | −22.245% | −47.620% | UNAVAILABLE于本次T机制证据 | +71.723% |
| Gaussian / discovery | 3,798,174→3,278,356 | −13.686% | −54.110% | UNAVAILABLE于本次T机制证据 | +26.417% |
| DWT2D / fixed holdout | 237,887→236,447 | −0.605% | −5.778% | −0.232% | +0.686% |
| BICG / fixed holdout | 47,533,116→41,157,397 | −13.413% | −0.148% | −18.652% | +2.821% |

以上百分比一律(new/old−1)×100，负值为该量下降；表中不同人群的指标不可相加。`FOUR_INPUT_DESCRIPTIVE_COMPARISON.tsv`保留原整数与40位Decimal计算结果，不能用显示舍入参与判定。

BICG应独立讨论：lower创建仅17,814,872→17,788,475（减少26,397，约0.148%），L2 read sectors也仅71,259,488→71,153,900；DRAM read bytes却为943,113,728→767,204,608（减少175,909,120，约18.652%），whole-run减少6,375,719 cycles（约13.413%）。L2结果桶、retry及下层流量变化是另一个可观察层级，不能把DRAM变化直接称为“Tag减少了同等比例的新lower请求”，也不能据此将cycle改善归为单一原因。队列/时序/服务重叠和缓存状态反馈没有逐周期因果干预分解。

必须保留的负例：**BICG的T1-C仍为41,157,397 cycles，C+为25,353,488，较C+慢62.334%**。这与相对oldOO改善13.413%同时成立。DWT2D仅0.605%的描述性周期改善，没有重复估计就不能宣称显著。四输入ready-to-complete均值均上升，不能写“所有阶段都改善”；PIB/physical的all64SM平均值不能证明不存在短时饱和。

GEMM只有一个kernel，扩大Tag的旧收益不能解释成跨kernel retained-mapping复用。其余多kernel输入也缺逐地址/代际跨边界直接复用关联，相关结果只能与保留映射假设相容，不能给精确因果份额。新K1 V2选择的是source-defined invalidate请求，不是每kernel统一清空；配置变化、普通MEMBAR和重复idle事件要与实际kernel-done分开解释。未来K0/K1×Tag交互仍须报告源事件集合、各指标人群与post-ready退化。

C+与DTC的whole-run周期，以及U已闭合的同路径L2 sector/DRAM atom和successful injection边界可分别比较；DTC accepted128B ready/pending/new、PIB/physical与服务区间不能与C+普通cache同名字段拼成统一命中率或统一延迟分解。sector32B、line128B、creation、successful injection、retry与issued DRAM command各自保留单位。

原输入capture/format、modern容量HOLD、数值load正确性和真实PPA资格仍沿原审查边界。64×8最大way比较与metadata量增加，冻结1cycle lookup不证明等频或等面积；不能自动替换主图/主配置。任何实际论文修订、额外实验或晋升须有独立授权；此包只给证据与可选措辞。
