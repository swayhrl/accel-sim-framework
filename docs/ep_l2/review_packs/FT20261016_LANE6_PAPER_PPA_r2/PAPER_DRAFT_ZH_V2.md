# EP-L2：通过原位写回与共享数据池分离缓存驻留和写回暂存

## 摘要

GPU L2 的逻辑替换、数据转交和事务完成发生在不同时间。脏 line 退出缓存后，其数据仍需暂存，直至下层真正接收；地址顺序状态则可能继续保留到写回完成。静态划分 resident、bypass 和写回数据空间，会限制不同角色之间的容量复用，并引入 resident 到写回缓冲的搬运。EP-L2 通过带代际的 payload 句柄分离地址可见性与数据归属，使脏数据能够原位转为写回暂存，而新驻留数据获得独立落点。本文以相同数据容量、相同四 Bank 服务能力比较静态分区与共享写回池，分别考察数据搬运、实际借用和系统性能，避免将某一局部计数器改善等同于加速。瞬态受害者目录与只读 pending 事务作为独立扩展，分别受到有效 sector、排序和 oracle 作用域的约束。本文给出生产实现的资源与生命周期模型、验证范围和参数化成本分析；预算内应用性能结论以配对执行证据为依据。

## 1. 引言

缓存替换并不意味着数据可以立即释放。对于写回式 L2，一个 dirty victim 至少涉及三种不同责任：Tag 决定该地址是否仍作为 resident 可见，数据存储保存尚未交出的内容，写回控制状态维护与后续访问的顺序关系。这些责任具有不同的结束时间。如果按同一个事件管理它们，可能过早释放数据，也可能将仍有用的存储长期固定给一种角色。

传统静态方案为 resident、bypass 和写回暂存分别保留容量。当 dirty victim 需要搬入独立写回缓冲时，源读取、目的写入及向下层发送的再次读取均消耗阵列服务。共享池允许改变数据归属而保留原物理位置，可以避免前一次拷贝，并在合法空闲容量存在时接纳额外写回。然而，可用总容量不代表可用 Bank 服务；更大的写回并发也可能只增加下层排队。因此，共享容量、拷贝消除和端到端性能必须分别验证。

EP-L2 首先研究真实写回消费者驱动的共享。Resident Tag 通过句柄关联数据；脏受害者的数据可从 resident 转为 WB_STAGED，由有限控制状态保持到实际下层接收，而新 resident 使用另一个满足 Bank 类别约束的落点。该机制保持静态与共享模式的总数据容量及 Bank 服务一致。后续可组合的 TVD 和只读 pending 路径改变数据保留或地址合并语义，因而需要额外的正确性和成本证据。

本文围绕三个问题展开：共享写回是否减少有限暂存造成的有效阻塞；数据搬运减少能否独立解释收益；局部效果在固定下层系统中能否转化为应用性能。相应地，评估保留低效和退化负载，采用强静态重分区与等拷贝服务对照，并将理想化诊断与可实现机制分开。

## 2. 生命周期与问题定义

设 t_r 为 dirty victim 实际读出或原位写回提交时刻，t_a 为下层真正接收数据时刻，t_d 为写回完成时刻。WB staging 承担 [t_r,t_a] 的数据保存责任，WAD 则跟踪地址顺序直到 t_d。预留还可能早于 t_r，因此预留槽占用与已创建写回包数量分别统计。只有接收方拥有已计账的数据承载，t_a 才能成为源 payload 的释放边界；仅向软件队列压入指针不满足这一条件。

历史静态模型中的观察不能替代新有限 WBUF 的实测。特别地，WAD 活跃不意味着旧 resident payload 同时保持存活，line 级重用也不意味着同一 sector 的时间重用。在已核验的 13 个历史 locality checkpoint 中，vectorAdd_4M 的 line 重用率为 75%，同一 sector 时间重用率为零；scan 则分别约为 78.82% 和 16.04%。前者主要反映对同一 128B line 中不同 32B sector 的访问。该结果用于区分流式与复用行为，不能换算成 TVD 命中率或共享池加速。[1]

## 3. 等预算写回池

### 3.1 数据组织与比较对象

每个 slice 有 1024 个 Resident Tag，line 为 128B、含四个 32B sector。描述符池为 512 项，Line-MSHR 与 WAD 各为 128 项，每地址请求上限为 32。全芯片采用 64 slices、32 memory channels；主 DRAM 频率为 850MHz，L1 保持校准后的基准配置。

| 组织 | 数据项/slice | 静态角色或共享方式 | Bank 服务 |
|---|---:|---|---|
| B16_BANKED | 1168 | 1024 resident＋128 bypass＋16 WBUF | 4×292，每 Bank 每周期 1 次 line-sized 操作 |
| U_WB16 | 1168 | 同总容量，按实际 owner 分配 | 同上 |
| B8_BANKED / U_WB8 | 1160 | 静态 1024/128/8 或共享 | 4×290，同服务上限 |

16 项 WBUF 是预先固定的主配置，8 项是敏感性配置。两侧另有相同的单个 128B copy pipeline latch，用于连接源读取与目的写入；它不属于可借用的 1168/1160 项。因而主数据阵列为 146KiB/slice，两侧共同的数据阵列加 latch 为 146.125KiB/slice；下层队列数据承载另计。

### 3.2 静态拷贝与原位转交

静态模式在破坏 dirty victim 前同时预留 WAD、有限 staging 落点和必要发行容量。拷贝执行 resident source read 与 WBUF destination write，之后执行 WBUF lower-send read；源和目的在同 Bank 时按不同周期服务。共享模式将旧 resident 句柄原位转为 WB_STAGED，避免这次源到目的拷贝，但保留 lower-send read。两种模式的 absorbed write、fill 和真实响应读取均支付同一 Bank 仲裁成本。[2]

共享池不保留原先 C 项 WB 数据配额，也不赠送无限 WB 控制状态。WAD、issue queue 和物理 payload 共同约束在途工作。新 resident 尽量保持 payload_id mod 4 等于 tag_index mod 4，以避免将 placement 改变混入共享收益。预留失败需要完整回滚，已接受返回必须始终拥有落点；旧 WB 排空不依赖新的 resident 分配。

### 3.3 身份与数据转交

一个物理项在任意时刻只有一个主 owner；pin、pending sector 和读取引用是附属状态。句柄由 payload ID 和 generation 组成，晚到 fill 或已复用 Tag 只有在身份匹配时才能修改当前状态。WB 数据在 lower-send 获准前由 staging payload 承载，实际下层 push 之后才释放；WAD 继续到 set_done。若 TVD 延长保留，这段额外驻留必须归入独立角色和占用统计。

## 4. TVD 与只读事务扩展

TVD 在 Tag miss 后增加一拍目录查询，并与其他角色竞争 Bank。读服务要求请求的所有 sector 都有效；缺 sector 不能按整 line 命中处理。clean write/atomic 先原子 promote 到 resident，dirty inflight write/atomic 等待写回完成；dirty read-forward 必须先于一般 WAD 拒绝条件判断。响应所服务的 sector bytes 与实际避免的 lower/DRAM bytes 分开统计，后者由同输入 OFF/ON 事务和字节对照确定。

只读路径使用 whole-commandlist、line 粒度的 closed-world oracle：在覆盖范围内排除写、atomic、写分配伪读、别名冲突及无法证明安全的外部或并发写。Attached 请求由实际 Tag pointer 合并；detach 后同地址可出现独立 {id,generation} 事务，不能使用未计费的全 completion 地址扫描。Detach 与 Line-MSHR bypass 分别控制、分别验证；空证书是有效的负覆盖结果。事务仍需完成对象、共享描述符、sector masks、返回落点和响应背压状态，不声称完全没有 tracking 成本。

## 5. 实验方法

### 5.1 配对与正确性范围

首批比较固定五个开发负载：convolutionSeparable、FWT_7_21、cfd_097k、vectorAdd_4M、sad。btree 和 dwt2d 用于策略冻结后的验证，scan 独立处理。主比较在同一生产版本和 binary 中切换 B16 与 U_WB16；新诊断版本则在其自身 binary 中比较 B16 与 ideal。跨 binary 的全关一致性仅作为回归证据。

SASS trace 不携带完整数值 payload，故应用执行不能证明全字节或数值 atomic 输出。验证范围明确为模型内的独立 sector version reference、实际 requester 恰好一次响应、句柄/返回身份、WB 创建—接收—完成关系，以及终态退尽；有真实字节的定向测试单独报告。周期和指令数相同本身不构成数据正确性证明。

静态 B16 与共享 U_WB16 生产版本已通过这一限定范围的独立资格，包括有限暂存、实际 Bank 服务、旧全关行为、sector reference、requester identity 与资源退尽。该资格只覆盖上述写回模式，不自动覆盖 TVD 或 detached RO。

每条结果绑定源码、binary、ordered config/aux、trace 内容、epoch 和显式 feature/ideal 向量。只有独立资格通过的完整 pair 用于机制 speedup。已完成 pair 可增量报告，完整预定集合到齐前不计算全组均值；失败与未完成项保留状态，不填零或按性能删样本。

### 5.2 归因指标与强对照

除 cycles 和 instructions 外，报告 WB-data-full、WAD-full、真实 WB 创建/下层接收/完成、staged occupancy、借用来源及拒绝、copy 读写服务、Bank wait、lower queue 和 DRAM 读写字节。若只有 copy 减少而未触发真实借用，结论限定为搬运及 Bank 服务优化。若观察到局部共享效果，再选择代表点比较同 1168 项的 1024/112/32 静态分区，并以等 copy 服务代价隔离容量因素。compute-only 的 1024/0/144 对照明确放弃 bypass 能力。

### 5.3 理想化参考

历史旧静态 vectorAdd 的独立乐观读参考从 73,873 变为 42,918 cycles，指令数均为 56,000,000，比例为 1.721259×。该参考移除真实读 DRAM 流量及相关排队，写流量也随时序交错改变。它只解释这个历史模型和负载的读路径敏感性，既不是预算内 EP-L2 性能，也不是严格数学上界或其他负载的平均收益。[3]

I_WB 保留实际 copy/Bank 和 WAD 约束；I_META 保留排序、fill 与真实响应；I_READ_HIT 单独报告。有限扩大后仍有容量阻塞时只称 sensitivity。诊断、shadow 和 oracle 辅助实现分别标注，不混入预算内实现的主图。

## 6. 硬件成本

主配置原始数据 RAM 为 1168×128B=146KiB/slice、全芯片 9.125MiB；C8 为 145KiB/slice、9.0625MiB/chip。共同 copy latch 再计 128B/slice、8KiB/chip；其空闲不表示可被共享分配。静态与共享数据 bit 数相等，不推出相同面积、能量或频率。

1168/1160 项寻址均需 11-bit payload ID；1024 个 Tag 的该指针字段为 1408B/slice。WB 控制句柄还包含 generation、packet binding 和状态；复用 WAD 地址字段不代表这些增量免费。完整成本表区分当前代码字段、位宽/编码假设和未知物理实现，保留数据队列、分配器、Bank 仲裁与目录查找成本。Completion 对象的实际配置与最大同时存活数分别计账，不将一个 128 项算例当成 RO 实现容量。

当前 generation 实现拒绝 wrap，但未确定硬件最小位宽。TVD 的额外一拍是架构时序模型，尚非 STA 结论。工艺、SRAM 宏和匹配模块 RTL 缺失时，只报告参数化 bits 与事件成本，不输出由 C++ 容器大小换算的面积、功耗或最高频率。

## 7. 讨论

共享写回的价值必须由真实消费者、局部服务效果和配对应用结果共同解释。TVD 服务可能降低下层流量，RO detach 也可能增加重复读取；这些方向都不预设为正收益。本文的最终论点可以收敛到写回搬运、容量共享或经验证的扩展组合，并保留系统下游限制和负结果。

## 证据引用

[1] 已核验的 13 行历史 Streaming checkpoint；[2] 有限 WBUF / Unified WB 生产实现与存储端口账；[3] 旧静态单点乐观读参考。精确来源、manifest、正确性范围、当前资格和应用结果覆盖见补充材料 `EVIDENCE_SUPPLEMENT.md`、`SOURCE_EVIDENCE_MANIFEST.json`、`RESULT_COVERAGE.json`。
