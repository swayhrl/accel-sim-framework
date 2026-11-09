# Gate审阅清单与不可穿越的安全/工程边界

## A：候选可实现性与反例
[ ] 实际source callsite、选择规则和输出状态稳定，已证明≥2个独立合法候选同一周期竞争；旧规则与新规则在CPU fixture中选不同合法对象。
[ ] 修改只限一个已冻结有限调度/返回/完成机制，没有同时附带queue扩容、Tag/physical/PIB改变、clock/L2/DRAM改变或无限服务。
[ ] 既有下游queue/credit满0的证据被纳入反证，不仅用平均等待或重试次数证明critical path。
[ ] 资源规格有entry、bits、max comparisons/tick、真实bank/端口、pipeline latency、per-cycle grant、backpressure、bounded fairness以及时序/面积风险。
[ ] 负控制、邻近强CH、历史不利结构结果和缺失计数器都进入候选决策；没有source-backed witness则NO_GO，不启动。

## B：局部CPU资格和独审
[ ] 冻结Baseline Source/isolated Candidate Source、Framework、binary/lib与完整effective options；同新binary的OFF与ON仅候选策略位不同。
[ ] 32/64/128B、partial/unaligned mask、multi-sector/parent、重复/迟到response、old generation、credit/ref/waiter exactly once。
[ ] notify/collect/WB grant denied、retirement/physical释放仅在合法时点、完成fairness、队列满反压/终止drain。
[ ] atomics、stores、fence、I-cache/texture/constant/bypass/noneligible负控制；原完成值路径不造假。
[ ] fixture故意破坏服务配额/选项回显/所有权，独立审查能拒绝；所有CPU脚本只作用新隔离树，复用旧已验收资格。
[ ] 纯增加观察计数的OFF运行必须经过CPU telemetry-neutral证明；不得因观测方便改服务顺序。

## C1：首4格严格资格
[ ] 新完整科学request，一次性UUID仅首次使用；选定W在4强目标内，vectorAdd作负控制，固定输入sha来源。
[ ] 从本次新冻结binary真实OFF、ON自然完整终态，不借旧DH-P0或Oracle OFF。
[ ] 新候选的有效决策变化/正曝光真实来自ON事件，而非配置echo或统计采样伪影。
[ ] 同一输入、kernel ordinals、name、CTA、active instruction与命令/初态/ROI等价，非候选选项一致。
[ ] 实际PID/start/maps/loader/libs/argv/cwd/resource guard、端口/周期配额，原strict不能削弱。
[ ] 源/归档chunk与whole stream/commit/index/typed native restore全部PASS、SOURCE_KEEP。
[ ] 独立安全与科学review明确允许下一16；若失败/HOLD/NO_EXPOSURE，其他16不注册。

## C2：剩余16格与终结
[ ] 只用预登记剩余8输入各OFF/ON，另一个精确request；不补跑已消费点。
[ ] 所有性能回退/精确零完整纳入；失败不能填zero or speedup1，也不得算作工程性能负例。
[ ] 完整10 GM仅在10配对accepted时报告；否则给实际接受交集和无法概括全10的限制。
[ ] 真实线程/资源/归档边界受控，未为可用性杀健康任务，归档恢复完成且只读publisher不受干预。
[ ] 最终report、固定SHA源索引、独立审查、GitHub回读、CONTEXT增量完成后STOP。
[ ] 未授权的22/44、CH、额外candidate/消融、Tag HOLD恢复、109 GPU工作均为0。

## 证据单位与声明
- 128B line、32B L2 sector、32B DRAM atom、request object和warp指令并非同一单位；不能将不同人口直接相除作因果份额。
- 计数器的cumulative/kernel reset/mean/occupancy/gauge/峰值分别标出；null/missing保持UNKNOWN，只有有源码证明的稀疏零才可派生。
- 真实选择改变和周期改善能支持“相关观察”；没有反事实事务时间线及其他解释排除前，不宣称唯一critical-path因果。
- 全部固定trace结果均不证明原生应用数值、capture ELF/内容、跨kernel coherence、RTL面积/功耗或等面积。
- 旧已封包不重写、旧HOLD不因新CPU PASS自动解除，合法性能负例与工程失败分别保留。