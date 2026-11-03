# 统计、比较集合与硬件成本边界

## 每输入六格与科学身份

逐输入记录CH-P0/CH-F128/CH-F256及DH-P0/DH-F128/DH-F256，详见SIX_CELL_PAIRING_PLAN.json。CH-F128/F256全部是未测量null；不可用0或1填补，亦不可从旧EP、PQ/PS、IR或R2回填。原始331包含6个原已批准的P0无新启动引用，其角色与证据逐项保留，不能把这些6个等同IR/R2。

四方定义（每个完整输入i、同一F）用实际cycles C计算：

- `S_CH(F,i) = C_CH,P0(i) / C_CH,F(i)`。
- `S_DH(F,i) = C_DH,P0(i) / C_DH,F(i)`。
- `R(F,i) = C_CH,F(i) / C_DH,F(i)`；大于1表示DH周期更少。
- `I(F,i) = S_DH(F,i) / S_CH(F,i) = R(F,i) / R(P0,i)`；大于1只表示DH按比例受益更多，不自动表示DH已整体超过CH，也不证明等面积。

每个GM必须附精确输入digest集合、n/目标n、套件覆盖率、缺失ID、正/负/相等数量和逐程序值。直接比较F128/F256时，必须在双方同一接受交集重算；不能比两个各33项但人群不同的GM。比值/交互必须逐输入计算后取同集合GM，禁止各自挑选最佳F拼接“统一配置”。

## 已有与未来集合

- 原CH-P0与DH-P0都有有效证据：33程序（缺SYRK、lavamd）。
- 原DH自身F128：33（缺SYRK、hybridsort）；原DH自身F256：33（缺SYRK、lavamd）。这些33不是同一集合。
- 同时有两个原DH F及两个P0：固定32程序，是64个核心CH候选共同目标。未来每个F四方实际n受新CH严格结果约束，失败不删除而是报告。
- 原F128四方前置集合32；原F256四方前置集合33（可附hybridsort）；两F共同四方集合32。
- lavamd-F128补充缺CH-P0，只有同F绝对R可在新CH严格通过后报告；S_CH和I保持UNKNOWN。恢复基线须另授权新身份，绝不改原失败。
- 原所有8个DH单因素共同集合31与本次32核心集合不同；勿把31的GM和33/32当同分母进展。
- 首批8/16是执行批次，不是重新选论文套件；只可标“首批子集”，不能标核心32或全35结论。

## 硬件差异必须披露

下游固定10MiB、40个subpartitions、MSHR192×merge4、miss queue32、850MHz DRAM及其余映射/时钟/时序。F仅改变 `-gpgpu_frfcfs_dram_sched_queue_size` 的配置字节，却通过实际Core源码同时改变共享credit：`F + 192 - (2 - 1)`，得到255/319/447；每subpartition private limit=1、每controller两private slots。不能称为纯队列容量或L2数据容量扩容。

CH/DH恰7项有效选项不同，详见Agent A与C：`dl1`组织、unified声明、DTC mode、Tag hash flag、DTC PIB/MSHR字段和有限完成服务。CH配置数据阵列96KiB；DH physical pool80KiB、logical tags512、unified声明128KiB。CH mode1的某些DTC参数不活跃，不能把惯性配置字段当真实CH结构资源。各设计内的P0/F128/F256保持自身L1/Hash/Tag/PIB和有限服务不变，跨设计实现与成本差异仍存在。

没有RTL面积/时序/能耗或关键路径测量，不能宣称等面积、等物理容量、等成本/免费扩容或物理性能上界。Hash沿用阶段I冻结设计，不按程序挑Hash。不改DRAM频率、L2容量或DTC架构来制造收益。

## 机制与组合边界

源码推导、trace元数据和运行时实测各自保留身份。静态重复地址不能证明cache hit/MSHR merge；cache总miss、DRAM原子数、L2扇区数及kernel末端打印量不能直接等同关键路径排队/带宽瓶颈。未知字段为UNKNOWN/null。

本Goal不启动组合。后续只有CH公平比较和机制证据审查完成，才按既有V2规则提出有限组合：全35性能证据，或预先固定套件至少3成员、GM≥1.01且正收益多数的方向才可候选；按既有V2，统一候选最终仍须覆盖原冻结35；现有缺口/HOLD保留并报告，未完成者不得宣称全35通过，不能临时缩成受益程序或其他“适用子集”。SYRK等未恢复前不能宣称全35通过。M8×F128/F256仅为未来提案；正式组合收益必须真实模拟取得，不得相乘两个单参数加速比当测量。
