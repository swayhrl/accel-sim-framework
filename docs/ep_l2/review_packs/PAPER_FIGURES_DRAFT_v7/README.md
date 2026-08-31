# 非零阻塞工作负载的结构阻塞图

此图使用与 v6 相同的 7 个非零阻塞 workload：`dwt2d`、`convolutionSeparable`、`spmv`、`scan`、`FWT_7_21`、`cfd_097k`、`btree`。

不同于 100% 阻塞组成图，本图每个指标均除以 eligible miss-admission cycles；因此总柱高和柱顶数字是整体 L2 准入阻塞率。仅读取冻结 v3 绘图表，未重跑模拟器或修改科学数据。
