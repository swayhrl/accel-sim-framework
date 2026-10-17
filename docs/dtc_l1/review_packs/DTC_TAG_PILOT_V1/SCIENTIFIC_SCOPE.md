# 探索科学边界与资源计价

T0只补GEMM同实际PIB128的IO/OO组织对照；原IO256仍保留，不能把三者关系直接推广成与C+差额的单一因果贡献。T1只干预OO的Tag sets/ways，保持数据/共享容量、pool/PIB、finite服务及所有原有效选项，不能据新周期回写原44行或改变其科学HOLD。

数据/metadata分开：DTC物理80KiB＋普通side16KiB，另保留96KiB shared。Tag128/256/512是可查询映射数，对应16/32/64KiB地址覆盖，**不是增加数据阵列**。T1-A和B均256映射，但A是32sets×8ways，B为64×4；B不改变同地址Tag bank，改变的是set冲突。A/C比较路数从4升8。4banks每bank的映射数原32、A/B64、C128。物理ID需表示640槽，最少10bit；OO128×最多32引用仍为4096，13bit Ref宽度保持；waiter/generation、PIB、事务和唤醒结构保留，不能当作免费。

RESOURCE_OVERHEAD.tsv给出条目数、比较路数、data/shared和示例Tag存储位数。示例使用57bit aligned line identity＋10bit phys ID＋1 valid、再加每set准确LRU信息量下界ceil(log2(ways!))；这是一个显式packing示例，含可压缩set位，不是实现最小面积，也没有完整端口、fanout、generation、解码、ready选择、比较器、电线、时钟或时序成本。软件对象sizeof不当SRAM面积。1cycle查找与原配额仅为冻结模型条件；若不能以同频实现，就没有硬件加速资格。实际PPA全部UNAVAILABLE。

性能和机制字段分别报告。M发现GEMM OO比C+快时成功下行读反而更多、DRAM实际传输为0；因此本T不预设“更快一定来自少请求”。下行credit不乘128伪装DRAM量，PIB-full等重试事件不改称互斥stall cycles。T1若缺OO命中/拒绝/重复地址同义字段，仍只能验证周期与已输出资源变化，不能补造完整命中率或因果贡献。final累计量只取最后一次，不把跨kernel重复打印直接相加。

严格验证边界：

- 真实检查：完整原列表和511成员SHA、ordered names、活动线程指令、CTA计数、natural exit0、未触发limits/deadlock、runtime/config/Core/64SM/mode/Tag/PIB/pool/cap echo、输出SHA、credit/下行/依赖/ordinary/Ref/physical balance及11finite统计。
- physical drain指活Ref/在途/部分分配排空且allocated/reclaim守恒；原前端会保留tag-visible行，不能把合法retained mappings强制写成0。
- 独立逐sector返回计数未直接输出，标UNAVAILABLE；保留生产full-line四distinct-sector mask、generation/重复负测、inflight/credit守恒的既定资格，不能声称已经测到新的逐sector性能。
- ordinary内部MSHR/延迟队列占用缺少单独DTC终端字段，标UNAVAILABLE；检查既有自然终止、源completion及store/atomic/bypass sidecar守恒。不编造一个“queue=0”字段。
- SASS timing replay不能验证完整architectural load数值；原native/input语义资格沿用冻结边界，不升级为数值证明。没有改变原trace、parser、opcode或ordinary路由。

原C+比较保持独立传统Core身份，不把其缺少DTC11同义分解视为0；原OO是T1主要周期分母。所有C+跨机制归因受M披露缺口限制，任何不同trace/配置/ROI不得混除。探索结果不宣称native DTC、等总面积、完整平台支持或论文GM12。

本轮只允许2个发现输入、7个attempt。原Hotspot HOLD、modern128KiB HOLD、SM89/LayerNorm未准入、2D新输入STOP、LUD不追加均保留。T1结束后所有新holdout、T2服务点、source observer或新机制均需另行审查，不自动执行。
