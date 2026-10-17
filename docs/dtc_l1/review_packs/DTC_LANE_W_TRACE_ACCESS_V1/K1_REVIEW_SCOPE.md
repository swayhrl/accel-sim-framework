# W 对固定 K1 科学合同的只读映射

合同已知且固定：Lane V `26abd496417d9392245052e54fbd9ba27c6ffd96`。逐字节副本、来源及SHA分别见 `inputs/LANE_V_K1_SEMANTIC_CONTRACT.md`、`inputs/LANE_V_SOURCE_EVENT_MAP.md`、`PROVENANCE_SHA256.tsv`。本Lane不等待Lane X，不实现K1、不做K1性能外推。

K1事件是source-defined invalidate请求到达 `ldst_unit::invalidate()` 的边界；它继承上游选择的SM集合，撤销DTC lookup-visible映射并保留所有已接纳消费者的physical identity/generation和未完成生命周期。ordinary的pending invalidate可能稍后才真正提交Tag失效，不能把该commit时间当作K1边界。

| 事件或候选 | W可支持的分析 | W不能支持的结论 |
|---|---|---|
| idle-cluster/config-change/regular-membar请求 | 固定源码条件、SM作用域与请求入口已审查；见SOURCE_DEFINED_INVALIDATE.tsv | 仅凭kernel list或kernel-done不能给出动态E的cycle/phase、受影响SM或每个kernel必有E |
| 跨kernel相同128B line的R∩R | 资源准入后可计算地址相交；当前未扫描，UNAVAILABLE | 地址相交不证明同SM、实际Tag驻留、可查询命中或K1前后性能差 |
| 前一kernel W∩后续R | byte重叠是比line alias更强的潜在写读候选；当前均UNAVAILABLE | 不能由list顺序造真实happens-before，也不能推断load实际返回值 |
| 同warp L→S→L且没有选中E | 若得到原地址/PC可筛查旧映射候选；当前PC不可点名 | K1没有额外的store自动invalidate，不能称一般写后可见性已被K1解决 |
| E前已接纳consumer在E后完成 | K1允许其继续依原physical generation完成 | 这本身不是旧lookup误命中，也不证明某ISA的值正确性 |
| E后新lookup | K1要求撤销的旧映射不可见 | 本包没有动态lookup/refill/retire事件，无法证明具体旧Tag暴露或实现通过K1 |

冻结Core `6fba0136…` 未把source-defined ordinary invalidate传入独立DTC映射；这项源码事实保持。OO retained Tag跨退休可保留提供结构性研究理由，但当前Gaussian是否具有真正跨kernel可查询Tag复用仍未证实。完整指令数、load/store次数、重复kernel名或同一PC均不能替代原地址证据。

四个指定原输入既有opcode目录没有atomic/bypass load/fence记录。这不使idle/config失效请求自动为零，也不能恢复动态事件时间戳。BAR.SYNC不是regular MEMBAR或PROXY_FENCE；source scoreboard条件也不等于所有store ACK完成。

原输入当前仅作冻结consumer模型下的风险筛查：不允许K1性能外推，是本Lane明确的科学/执行边界，不再以“K1合同未知”为理由。Hotspot原HOLD、旧/新2D身份及新输入STOP、LUD不追加继续保留；Lane U完成不授权读取其旧raw或重启任何工作负载。
