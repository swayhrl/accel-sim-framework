# DQ4a：dense producer→consumer handoff

历史 MP01 在其合法 Graph-OFF scope 内观测到相邻 producer→consumer 次序与正 gap；这只是时间线现象，不是 cache handoff 的可节省时间或硬件因果证明。MP05 是 AWQ 表示 control，不能代替 BF16 decode 的 DQ4a 证据。

MP02/MP03 的 compiled path 没有可用的模块 hook 时间线。Lane7 虽在已有 FX 图中看到静态 gate/up→activation→down 依赖，但 runtime kernel inventory 只有名字，没有逐次 launch、layer、decode step 的无歧义关联；通用 GEMM/GEMV 名与融合 kernel 使边界不能从静态 DAG 推回。既有 `LEVEL_0_UNRESOLVED` 更达不到本问题原则上要求的 `LEVEL_2_EXACT`。

终态：`DQ4a = QUESTION_INCOMPLETE / NOT_IDENTIFIABLE_UNDER_CURRENT_COMPILED_PATH`；机制状态保留 `DQ4A_COMPILED_ATTRIBUTION_UNRESOLVED`。不按 FLOPs、操作数或静态调用顺序分摊 runtime 时间。
