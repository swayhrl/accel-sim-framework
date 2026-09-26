# 论文实验观察账本（不是AWMA结果）

Round 02首次建立。记录单位是“论文版本 × 实验组 × 工作负载/输入 × 配置 × 指标”，不是单独的benchmark名字。

## 入口

`ROUND02_DATA.json`包含配置、34条原表workload行（LATPC 24、Valkyrie 10）、17条数字/定性观察及来源限制。不是34个已复现实验，也不是所有论文图表的数据全集。LATPC和Memento对应用户提供正文；Valkyrie对应作者PDF关键章节；NeuMMU对应2019预印本v1。

## 阅读与取数双层标记

论文阅读深度与每条数据的取数方式分开。使用 `TABLE_VISUAL_CHECKED`、`TABLE_PARSED_TEXT_CROSSCHECKED`、`EXPLICIT_PROSE_NUMBER`、`QUALITATIVE_PROSE`、`AUTHOR_AGGREGATE`。本轮没有估读柱高，没有把作者均值填到每个workload上。

配置和实验对象缺失用null及解释：原文相应位置未披露，与我们尚未核实不同；数值0只能用于原文明确为0。输入只给footprint时不补造矩阵形状、模型revision或上下文长度。

## 不可直接比较的情况

- 名字一样但suite、实现、输入或平台不同，不合并成同一workload趋势。
- MPKI需记录L1/L2及每千何种instruction；原文未区分warp/thread计数时保持未知。一个miss除以小分母也能很大。
- 页数、共享集合比例、同时驻留命中概率、物理服务量不是同一指标。
- 参考原文MB/KB，不自动改成MiB/KiB；IPC倍数、cycle reduction百分比、等待占比、dynamic energy不可相加。
- 同一配置内对照优于跨论文横比。变更页大小同时扩footprint，不能称单变量页大小实验。
- hardware model不是已知真实芯片实现；model energy不是实测功耗；存储比不是面积比。
- 本账本只为选择问题和对照提供经验，不按这些数字替换AWMA配置、校准结果或实验权威。

## 更新规则

每条观察保留source_locator、baseline/treatment、scope及limitations。新的观察可提出“在什么条件下值得检查什么”，不能直接变成“必然发生的硬件规律”。有矛盾时保留版本/位置，不静默调和。所有研究想法与作者报告分栏。
