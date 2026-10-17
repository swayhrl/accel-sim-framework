# RTL / finite-service variant crosswalk

审查对象是当前 finite DTC-L1，不能用文件名中的 OO、IO、classic 或 C+ 自动建立实现等价。路径、commit 与逐文件 SHA 见 [HARDWARE_PROVENANCE.tsv](HARDWARE_PROVENANCE.tsv)；下文 source ID 均指该表。审查锚点为 Lane T `f520a445436b57c0a0f2494fb858a1636f04d2bc`，Core `6fba0136f8465b59fe5858a950fa39efb265f654`。

|对象|可验证配置与来源|硬件绑定|可作出的结论|
|---|---|---|---|
|A：原 OO128|T_RESOURCE：32 sets × 4 ways、128 mappings、16 KiB logical coverage；CORE_COMMON 构造相同数量的逻辑 Tag|未取得对应 L1 RTL/top/filelist/完整 SRAM manifest|结构合同可核；实际总面积、延时与完整实现成本 UNAVAILABLE|
|B：T1-C OO128|T_RESOURCE：64 × 8、512 mappings、64 KiB logical coverage；同一 Core 的 sets/ways 参数|`T1C_RTL_NOT_AVAILABLE`，范围限于本包列明的已知来源|不能把参数化 C++ 当成已实现 RTL；额外位数可作估算，额外面积和时序不可确定|
|当前 IO|T_RESOURCE：IO256；与 OO128 的顺序、等待/唤醒/退休机制不同|没有与 finite IO256 绑定的综合报告|UNAVAILABLE；不能直接套用历史 IO 面积|
|当前 C+ / Base|Core 的常规缓存路径与 finite IO/OO 为不同组织|没有当前目标配置的 RTL 及完整面积/时序报告|UNAVAILABLE；不从名称推断等价或补造面积|
|博士论文第4章 IO / OO|THESIS_CH4，PDF 第82页／印刷第64页 §4.5.3，及第79页／印刷第61页 §4.3.3|论文称做过综合，但原 RTL commit、top、PVT、DC 版本与 raw reports 未绑定|OO 相对 IO 面积 +4.7% 为 `MEASURED_HISTORICAL_NOT_MATCHED`；仅保留历史结果|
|本地 classic L2|L2_CLASSIC，默认地址40位、64 sets、16 ways、128B line|行为数组和 L2 接口；不是已证实的当前 C+|不能充作当前 Base/OO128 面积基线|
|旧 decouple L2|L2_OLD_IOOO：地址49位、64 sets、16 ways、1024 data slots、2 data banks、epoch3、MSHR64|L2 的 IO/OO 组织开关不能建立当前有限服务合同|不是 A、B 或论文原物的已证实现；UNAVAILABLE current PPA|
|v3 L2|L2_PARAMS / L2_TOP：top `gsgpu_l2cache`，默认 Tag256 ×16，43-bit Tag +3-bit ZINF +12-bit pointer；4 ×1024 data slots；请求缓冲512|L2 DC elaboration 模板、blackbox/行为 RAM；与目标 L1 几何和服务不同|不能用作任何 `MEASURED_MATCHED` 行|
|SG0 引用的 v3 L2 `69cd5b608424568caaceff7c60ae591530629487`|SG0_RTL 明确说明论文来源关系未建立|不是论文原始 RTL 的收据，更不是新 finite L1 的收据|保留来源断点；不因同属 DTC 就搬运 PPA|

A、B 的公共合同：physical pool `640 ×128B =80KiB`，ordinary side `16KiB`，shared `96KiB` **单独列出**，OO PIB128，4 Tag banks，每 bank 每 core cycle 最多1次 Tag grant、合计4次，allocation width4，全局 lower cap32768；其余 finite service 和公共配置保持 T 的冻结合同。以上都是 `ESTIMATED_ONLY` 的配置/结构证据，并非实测面积或宏端口证明。T_PREREG 中模型 core clock1410MHz 对两者相同；不等于已经取得相同 ASIC Fmax。

`CORE_COMMON:490` 的 `m_tags(sets*ways)`、`m_phys(physical_lines)` 与 `m_slots(oo_pib_entries)` 直接支持“逻辑 Tag 数变化，物理槽与 PIB 条目数不变”。它们不支持 SRAM 宏个数、面积、端口和外围电路不变。软件 `uint64_t`、vector/list/map、主机对象布局、统计用 map 与断言扫描不能直接变成硬件存储位数或关键路径。

最低实现差异不能只写成 sets/ways 两个参数：需实现并验证每 bank 从8 rows ×4 ways 到16 rows ×8 ways；比较/命中选择/无效优先与 replacement 更新；Tag 中 physical-ID 和 generation 的一致性；allocation、eviction、refcount/TagValid、pending waiter 与 late merge 的冲突仲裁；读写端口及同地址 bypass；跨 bank 的全局额度；ready、collection、retire/reclaim 的周期合同。公共模块可以共享设计，但共享必须有 source binding 和验证收据。

当前 C++ 每 Tag 携带 `physical_identity {id, generation}`，generation 为64位（CORE_COMMON:153、849），因此 Tag 数增加还可能扩大 generation 副本。若 RTL 省去或缩窄它，需给出在 reuse、late return、PIB slot reuse、wrap 下仍不误唤醒/不回收错误对象的证明，不能默认免费。实际 replacement 在软件里使用每 Tag 64-bit 时间戳（:854、908），Lane T 的 exact-LRU 信息量下界并不是已有硬件实现。
