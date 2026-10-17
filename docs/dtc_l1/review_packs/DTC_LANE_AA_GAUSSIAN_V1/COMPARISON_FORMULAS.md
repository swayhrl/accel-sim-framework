# Fixed factorial comparisons

令 y00=K0_32x4，y01=K0_64x8，y10=K1_32x4，y11=K1_64x8。主指标 y 为自然完成的 total GPU cycles；active-thread instructions 和 CTA 必须一致。主效应以同单位的差值报告，同时提供两个 Tag 内的 K 配对周期比。

| Quantity | Fixed formula |
| --- | --- |
| K main effect / cycles | ((y10−y00)+(y11−y01))/2 |
| Tag main effect / cycles | ((y01−y00)+(y11−y10))/2 |
| K×Tag interaction / cycles | (y11−y01)−(y10−y00) |
| K simple effect at32x4 / cycles | y10−y00 |
| K simple effect at64x8 / cycles | y11−y01 |
| Tag simple effect atK0 / cycles | y01−y00 |
| Tag simple effect atK1 / cycles | y11−y10 |
| K speed ratio at32x4 | y00/y10 |
| K speed ratio at64x8 | y01/y11 |
| K cycle change at32x4 / % | 100×(y10/y00−1) |
| K cycle change at64x8 / % | 100×(y11/y01−1) |
| Q32: K1/K0 cycle quotient at32x4 | y10/y00 |
| Q64: K1/K0 cycle quotient at64x8 | y11/y01 |
| T0: large/small Tag cycle quotient atK0 | y01/y00 |
| T1: large/small Tag cycle quotient atK1 | y11/y10 |
| multiplicative interaction I | Q64/Q32=T1/T0 |
| interaction on log-cycle scale | log(y11/y01)−log(y10/y00) |

周期差为负代表周期减少；speed ratio大于1代表加速。这里交互采用完整 difference-of-differences，不额外除2；不能与采用其他编码的回归系数混淆。四点各一次确定性模拟，无重复样本、无置信区间或显著性结论。不得仅报告有利的 Tag 层级或把历史控制当新配对。

Q/T周期quotient大于1表示分子较慢，I大于1表示K1在大Tag下相对周期惩罚更大。它们与上表speed ratio的方向不同，均保留整数原值计算。对可比的终态 count 或已定义 conditional mean，采用相同的主效应/交互公式，保留各自单位与分母，不混用计数、扇区、字节及周期。比例、条件均值与总体周期之间不建立可加归因。任一必要点非 strict PASS或字段缺失，对应比较为 UNAVAILABLE；分母为0标UNDEFINED_ZERO_DENOMINATOR，跨单位/人群不可比为UNCOMPARABLE。不插值、不以0填充、不剔除失败后另选点。
