# GO / NO_GO for a future AF arm

**当前：GO_CPU_CANDIDATE_REVIEW；NO_GO_REAL_INPUT_PERFORMANCE。** 原因：源码与synthetic可达性可核，但真实输入同定义窗口未观测，硬件时间/端口成本未闭合，AG尚无本包可核的性能前AF-arm/新增预算预注册。AF不加入AG既定8点主矩阵，本包不启动任何模拟。

只有下列条件**全部**满足才建议另行批准性能运行：

1. 在独立新候选binary中用已固定输入/source/config/observer采集精确事件，证明AF窗口可达；原LRU live、同set安全候选和实际commit处无free同时成立，不能用全SM平均occupancy、Tag eviction或generic NO_FREE_LINE总量代替。
2. 单列一次access尝试、逻辑reference和cycle去重规则，保留“原LRU拒绝且无候选”等反向/零机会证据；不得依据发现的性能挑输入、Tag或阈值。
3. CPU生命周期、default-OFF、真实option parser及构建检查通过；任何PARTIAL项与未覆盖模式明确。候选event出口若需修改共用stats合同，先单独请求审查，不改冻结AA5库或旧stdout补机会计数。
4. AG在新性能开始前，预注册不可变AF Core/Framework/source/config、AF-arm/输入/cohort、比较方向、停止/失败处理及**新增**运行/资源预算。未注册不替换8点，不自动重跑或扩矩阵。
5. 硬件门槛固定：same-set way-state/Ref/readiness/owner读取、最老安全选择、端口/扇出/仲裁与回收同步所需时延/面积有独立证据或明确限定模型研究。若需要新增扫描延迟/服务宽度/候选缓存等自由变量，先请求而不在AF V1自动引入。

即使GO条件满足，也只代表值得有界实验，**不预言真实加速**。可能不存在机会，或避免一次NO_FREE_LINE却增加其它Tag miss/下行压力；比较必须保留负结果及额外查找/选择成本。new request creation、successful injection、retry和DRAM字节分开，不做单一周期因果分摊。

本包的候选局部计数 `oo_frontend::reclaimable_victim_fallbacks()` 仅计ON分支成功选择替代victim的access事件；只读getter，无周期去重，不是唯一地址数、stall cycles或真实输入机会率。OFF不扫描、不产生这个观测值的机会测量；OFF getter的0不证明真实窗口不存在。该计数**未接入共用normal stdout/stats schema**，实际输入终态导出目前UNAVAILABLE，后续出口属于需审查的请求。
