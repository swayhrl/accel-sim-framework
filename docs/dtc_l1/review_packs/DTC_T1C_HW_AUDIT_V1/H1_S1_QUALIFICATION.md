# 硬件成本与同频资格

本文件只审查硬件成本完整性与同频证据，不改写其它 Goal 的 H1/S1 科学假设或准入合同。没有产生新的综合、STA、网表或物理实现结果。四类来源等级严格为 `MEASURED_MATCHED`、`MEASURED_HISTORICAL_NOT_MATCHED`、`ESTIMATED_ONLY`、`UNAVAILABLE`。

|核对项|结果|等级及依据|
|---|---|---|
|Lane T 锚点和四份指定文档|PASS|逐字节对应 f520a445；T_RESOURCE / T_SCOPE / T_LEGALITY / T_REPORT，SHA 在 provenance 表|
|结构算术与 bank 映射|PASS，仅限模型|ESTIMATED_ONLY；8,864→35,840 bit，增加26,976 bit；bank 恒等式覆盖整个64-line周期|
|A 的匹配 RTL/top/参数/端口|UNAVAILABLE|没有当前32×4 finite OO128 的完整实现与报告绑定|
|B 的匹配 RTL/top/参数/端口|T1C_RTL_NOT_AVAILABLE|仅限 BOUNDED_SEARCH_SCOPE.tsv 所列来源；不宣称服务器其它位置或用户持有材料不存在|
|匹配标准单元库、PVT、电压、DC版本和正式 SDC|UNAVAILABLE|L2_DC 是占位路径的 elaboration 模板；R8 的既有审计也记录未闭合；未新探测工具或 license|
|完整 data/ordinary/PIB/metadata/外围面积|NOT_QUALIFIED|UNAVAILABLE；blackbox 或行为 RAM 不能当零面积，也不能以 flop 逻辑面积冒充 SRAM 总面积|
|匹配 setup/hold、WNS/TNS、实际 RAM 端口合同|NOT_QUALIFIED|UNAVAILABLE；没有当前 A/B 的真实映射网表与 STA|
|相同频率资格|NOT_QUALIFIED|模型1cycle不是测量；没有 SAME_FREQUENCY_PASS|
|完整面积资格|NOT_QUALIFIED|没有 TOTAL_AREA_PASS；无 MEASURED_MATCHED 指标|
|来源核对边界与 CPU-only 操作|PASS|只读命名的来源、Git 元数据及算术；不接触 Lane U 的运行状态、raw 或锁；无 EDA/GPU/模拟器调用|

Lane T 的示例必须单列：每 mapping 的57-bit aligned-address identity（保留 set 信息，非最小 tag）、10-bit physical ID、1 valid bit，加每 set `ceil(log2(ways!))` 的精确 LRU **信息量下界**。A 的 LRU 部分为160 bit，B 为1,024 bit。总量增加26,976 bit（3,372 byte）。它排除了 generation 副本、更新逻辑、比较器、decoder、mux、pending、端口、宏外围、时钟和布线；不进入实测面积合计。分解及条件见 [TAG_SCALING_COST.tsv](TAG_SCALING_COST.tsv)。

物理池固定只使物理槽计数不变。13-bit RefCnt 配置、640份 physical generation/TagValid、128 PIB 与至多4096 reference associations 的容量合同不随 Tag 数变化；实际 generation 位宽、waiter 的 dense/sparse 编码、RMW 端口与 bypass 仍未给出。当前软件 per-Tag generation64 的直译副本会额外增加24,576 bit；该数为**条件估算**，不是必需的最小实现，也不能自动加到另一种编码的“总成本”。软件64-bit LRU 时间戳与信息量下界是两种不同描述，不能同时相加。

最值得先检验的时序路径是 `bank/set decode → Tag RAM read → 8-way equality → hit/way select → physical identity/generation/state read → ref/waiter attach 或 victim/LRU update`。这是基于结构的风险推断（ESTIMATED_ONLY），不是 STA 的最差路径排名。每 bank 的 row 数翻倍、way 数翻倍、读行变宽、选择/fanout 增长；写入、命中 replacement 更新与 eviction 可能争用同一宏端口。同 bank 同 set 的 hit/read/write、late merge/return、allocation/reclaim 相遇时，必须有可验证的仲裁、stall 或 bypass 周期语义；不能借未冻结的额外 pipeline 将模型的1cycle假设悄悄改掉。

T_PREREG 的 core1410MHz 对应纯算术周期709.219858ps（ESTIMATED_ONLY，未扣 setup、uncertainty、clock skew 或 IO 预算）。当前没有库/PVT/电压、匹配 SRAM 的 access time/clock-to-Q、实际比较器/选择逻辑延时，也没有 formal SDC，因此既不能断言达到，也不能断言一定达不到。L2 文档中的其它时钟目标与默认 open-synthesis 约束不属于本合同。

不应遗漏 Tag 后面的服务路径：

|有限服务|直接源码证据（均为软件合同）|需要而未取得的硬件证据|
|---|---|---|
|ready selection / ordering|CORE_COMMON:690 的 oldest-ready 扫描；CORE_SHADER 的 eligibility/fence 过滤|128-entry 就绪/次序选择、物理 ready/generation 检查、fence 资格扇出与时序；不能拿软件循环作为组合延时|
|consumer wakeup|CORE_COMMON:660，4 waiter updates/core cycle；全部 waiter 完成后 physical 才 ready；late merge 加入同一 generation 队列|4路 PIB pending-dependency 更新、同 owner 多命中合并、slot generation 验证、返回仲裁、端口和逐周期一致性|
|collection / refill|CORE_SHADER:2961、4946以后；CORE_SHADER_H:2145，collection4 sectors/core cycle，refill quota1；32B/sector|数据宏 bank/端口、读写冲突与4-sector collect、1-sector refill 的仲裁、返回及消费者接口时序|
|reference attach / retirement|CORE_COMMON:882 和690以后，per-owner 去重；一次退休可释放该 owner 的全部引用|多引用 RefCnt RMW、同 physical 多次更新合并、13-bit溢出保护；内部串行化是否仍满足外部1-retire/cycle合同|
|reclaim / allocation|CORE_COMMON:567、940；TagValid=false 且 RefCnt=0 才 release，generation 匹配|最后引用减计数到回收再分配的旁路/优先级、旧 return 屏蔽、free-list 搜索实现及多 bank 一致性|

这些结构的容量大多是公共项，但它们是否已经支付了面积和周期成本，仍须完整 RTL 与真实报告回答。新几何可能改变并发活动和冲突频率；这也不允许据模拟性能变化倒推电路成本或合理端口。

现有 v3 L2 RAM 合同（L2_RAM_CONTRACT）使用 full-rate 接受、half-rate P/N bank 以及 N→N+1结果→N+2消费者捕获的不同接口。它只能说明不能偷换合同；不能证明 finite L1 的1cycle Tag lookup 或 collection/wakeup/refcount 同频。
