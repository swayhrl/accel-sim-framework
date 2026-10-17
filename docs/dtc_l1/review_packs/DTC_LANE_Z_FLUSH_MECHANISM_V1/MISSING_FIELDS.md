# Missing fields / review boundaries

| 缺口 | 当前状态 | 不允许的替代 / 后续门槛 |
|---|---|---|
| 四格新 K0/K1 结果、strict/运行身份 | NOT_CONSUMED | 不执行新sim；不读U进度/partial BICG；只在整个组自然终态+strict+正式发布后消费 |
| 终端可查mapping、lost-but-resident count、kernel边界失效事件 | UNAVAILABLE | 不用 physical积分/Tag eviction/map-loss completed count 充当；需 X 独立发布直接字段与 boundary/reset 合同 |
| X 观测开关、有效默认值、事件hooks、开销和 source/build绑定 | UNAVAILABLE_PENDING_X_PUBLISHED_CONTRACT | 不虚构开关名；插桩前后周期不可直接混比，四格同观测合同 |
| T Gaussian 510个独立kernel cycles | UNAVAILABLE_IN_ACCEPTED_SMALL_EVIDENCE | 原序/名称/指令可由T ORDERED_KERNELS核；strict只存逐kernel布尔检查。此轮不重读旧raw，不平均分摊总周期；GEMM单kernel可由完整总周期确定 |
| A除M已封存scope之外的逐kernel cycles | UNAVAILABLE_IN_ACCEPTED_SMALL_EVIDENCE | A的kernel数/总周期不提供每核数值；本轮不重扫旧raw |
| C+统一DTC ready/pending、post-ready与map-loss区间 | UNAVAILABLE / UNCOMPARABLE | 普通cache coalesced lookup outcomes独立保留，不能接入DTC128B分母 |
| OO完整Tag/pool/PIB拒绝、重复在途地址关联 | UNAVAILABLE | 不因IO为0、low平均占用或cap-full=0而填0；eviction≠duplicate |
| kernel独立reset的DTC/cache/DRAM counter | UNAVAILABLE作为统一旧合同 | 重复累计快照只取终值；不把所有打印相加。差分需边界/reset/单调性证明 |
| active-only occupancy、分位数、互斥stall cycles、完整issue到retire | UNAVAILABLE | all64SM样本与post-ready区间不能外推 |
| retained mapping跨kernel逐地址复用关联 | UNAVAILABLE | K0/K1×Tag交互与lower/ready共变只能作有界机制证据，不给精确周期分摊 |
| T点DRAM/L2完整计数 | UNAVAILABLE_IN_SELECTED_T_MECHANISM_TABLE | T的credits×128不是DRAM；本轮只在M已有issued command/sector证据上报告相应计数 |
| 真实硬件PPA/频率、数值load correctness/native DTC效益 | UNAVAILABLE | 1cycle Tag和等物理容量不证明等面积/时序；不自动写v0.13 |

A与M的BICG IO分别为 `aec8c80b-1d77-4301-8314-fb98c5d95058` 与 `87c9040b-1ce7-4166-b68e-38da9bceb1d6`。M的后者是独立matched128证据；即使两者总周期相同也不跨UUID拼接。A原41PASS/3HOLD与全部原输入保留，不删负结果；原 GM12 未定义且此包不生成它。

本轮使用固定 Git blob 的小证据，无174旧raw/trace读取，因此未触发旧raw资源准入。未来确需补读旧raw时须先按当时174共享资源准入合同取得CPU/RSS/I/O/存储余量和限流边界，固定accepted UUID/完整终态/SHA再只读；不得借补字段去探测U或启动模拟。当前缺口不冒充已验证字段。
