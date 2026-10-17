# M：原174既有日志CPU机制补证

**状态：PASS_READONLY_MECHANISM_CONSUMPTION_WITH_DISCLOSED_GAPS。** 文档远端HEAD=`103c12ca28e0b5fb66f45b905a04108b501f8ec7`；只读受理Lane A最终HEAD=`f5c37d6edcce832a72cb0830021bffa78df6cc13` 的固定GEMM三臂、BICG六臂。九个raw stdout、strong/canonical strict、spec/config、binary、完整ordered kernel/指令与终端性能CSV全部闭合。GEMM full739,246,080活动线程指令，BICG full145,666,048。未读新candidate性能、未运行模拟器/GPU、未重启A或改变输入/冻结合同。

| 原输入 / arm | cycles | 成功下行读request | 实际DRAM读payload B | ready→collect平均core-cycle/cacheable warp |
|---|---:|---:|---:|---:|
| GEMM C+ | 1,511,333 | 2,603,998 | 0 | UNAVAILABLE |
| GEMM IO256 | 1,457,468 | 4,144,708 | 0 | 842.6816 |
| GEMM OO128 | 1,377,919 | 3,993,335 | 0 | 6.0614 |
| BICG C+ | 25,353,488 | 17,602,331 | 468,501,632 | UNAVAILABLE |
| BICG IO128 | 93,312,525 | 17,826,128 | 1,841,007,744 | 3557.9500 |
| BICG OO128 | 47,533,116 | 17,814,872 | 943,113,728 | 1.1590 |
| BICG C16 | 79,721,847 | 17,635,339 | 624,048,384 | UNAVAILABLE |
| BICG C80 | 26,555,809 | 17,603,205 | 431,602,688 | UNAVAILABLE |
| BICG WAIT128 | 84,049,733 | 17,639,045 | 731,557,120 | UNAVAILABLE |

**EVIDENCE_SUPPORTED：** GEMM OO128比C+少8.83%cycles，却多约53.35%成功下行读；三臂实际DRAM传输均0。因此“更快来自更少下行/DRAM请求”不成立。GEMM IO256/OO128的mean PIB181.05/79.19是全64SM全周期均值，而且深度不同。OO的post-ready等待明显更短，collection两者均1cycle；不把这当已完成的同深度纯组织因果证明。

**EVIDENCE_SUPPORTED：** BICG合法matched128下，OO比IO约1.9631×更快，新下行读仅减少0.063%；DRAM实际读payload约减48.77%，L2 reservation retry事件也减少。OO仍比C+慢约1.875×、DRAM读payload约为C+的2.013×。旧C16/C80/WAIT128均如表保留；WAIT128是传统16KiB/PIB128/MSHR32，C80是80KiB/PIB8/MSHR32，不冒充同机制因果控制。

**CORRELATION_ONLY：** OO较短的fully-ready后等待及下层访问时序/复用，是正例和回退的可证伪解释候选。高Tag替换数、mapping丢失后仍占用物理池、IO在途重复请求，使Tag覆盖探索有价值，但不能从credit变化直接推出Tag命中或单一瓶颈改善。区间总和并行重叠，事件可重试，不能把它们与GPU cycles相减做“贡献”分解。

**UNAVAILABLE / UNCOMPARABLE：** C+缺少DTC11同义阶段分解；OO缺完整Tag/pool拒绝、重复在途地址及可比PIB-full周期；CSV没有DTC字段。常规HIT/HIT_RESERVED原值保留在CONVENTIONAL_LOOKUP_CONTEXT.tsv，但粒度/路径不同，不与DTC128B reference强造命中率。低平均占用及cap-full=0不能排除其它瓶颈。

两个机制假设及预留检查规则已在读取旧DWT2D raw之前按SHA封存。随后独立核对：DWT2D C+247,588 / OO237,887cycles，成功下行读219,173 /232,173，实际DRAM读11,268,992 /11,307,264B。这个“略快但读量略增”的旧例没有反驳非单调关系，也不能证明Tag新candidate成功。没有把它加入发现集/均值，没有展开任何新candidate。

**建议T0继续，T1有条件继续：** M先行的原始身份与统计语义门槛已通过。T0补GEMM同128深度缺口；T1只能按原GEMM/Gaussian三Tag候选共六attempt及固定选择门槛做有界干预，当前证据不保证晋升。仍须T独立CPU合法性/资源/authority检查、immutable manifest提交并fetch-back后才能运行；M不给启动权。不建议据这些旧计数直接开T2或改服务宽度，更不改变原主实验、HOLD或GM12。

当前现场PID520970/433763/469026均已不存在；历史最终收据仍保留其当时状态，四个原锁文件inode保留且本窗口只stat、未flock。没有重建dispatcher、停止watcher或改A manifest。执行worktree/分支及前后SHA见PRECHECK_RECEIPT和POSTCHECK_RECEIPT；大stdout、trace、binary、CSV仍在原只读位置，不进Git。

审阅顺序：[指标定义](METRIC_DEFINITIONS.md) → [九臂原值表](EXISTING_RUN_MECHANISM.tsv) → [结论支持](CLAIM_SUPPORT.md) → [缺失字段](MISSING_FIELDS.md) → [身份链](INPUT_RUN_IDENTITIES.json) → [预留假设封存](HYPOTHESIS_FREEZE.json)及[DWT2D独立核对](DWT2D_READONLY_CHECK.json)。复核步骤见REPRODUCE.md。
