# RO策略跨输入收敛：本轮停止扩扫，保留有限可选候选

依据最高科学authority **eae40596cb9a550785a50a3d64617686a6daa160** 的UMT1最终4/4接受、两个预算关闭、8次独立恢复，以及V5已关闭的Vector两点。此项仅做小型已发布metadata总结和有限计算，不启动模型、不改Source或历史。

**结论：一位压力epoch策略可显著避开Vector上的非必要RO服务开销，但真实触发的Conv/Scan完整应用收益分别仅0.388%/0.540%。当前证据足够结束这一轮阈值、频率和输入扩扫；没有新的完整模型申请。** 保留候选及所有小收益、零激活和负向计数，不能提前改为普适默认策略。

## 配对与完整周期

六点均为Core812fe1e / ELFa60600a4 / archive a7e9c8ce、Framework9dd1ee57、vendor f90c430c。每对严格同Source5、输入、clock、G32×8、完整命令人口和其他282项配置，唯一差异为pressure_epoch 0/1。

| 输入/背景 | 原始F完整cycles | 压力策略完整cycles | 减少cycles | cycles减少 | 策略开启后激活slice |
|---|---:|---:|---:|---:|---:|
| Vector1700 | 55,925 | 45,425 | 10,500 | 18.775145% | 0/64 |
| Conv850 | 335,088 | 333,789 | 1,299 | 0.387659% | 61/64 |
| Scan850 | 2,224,142 | 2,212,128 | 12,014 | 0.540163% | 4/64 |

Vector为DRAM1700MHz；Conv和Scan为850MHz，均为L100及冻结资源。**850与1700只作不同背景的context，不跨背景拼参考，不算合并加速比或GM。** 也不把旧Core862 S/W/WV或旧Source78结果混入任何一对。

完整输入身份：

- Vector4M：ddf26d4f6b4b672de3c5f6d1ab633cc44d3d9ef8023b87ae9a10760f3f4057dc，3命令、1 kernel、15625 CTA、56000000 instructions。
- Conv3072：438eefd67b073f1ca0e2c08be6aa99b3b9b9619d7832cc6cad9cc4467e63654e，4命令、2 kernel、27648 CTA、714547200 instructions。
- Scan：cf8d1c4d8e4956779ee5dbe0e836c6c77b595cb86cd2dc731e9897dd75504690，34命令、33 kernel、166608 CTA、1963460720 instructions。

每点均已正式接受、硬件排空、真164归档和两目标独立Native恢复。此处只核对这些小型回执与最终审计，不重读归档正文、不再次恢复。三对实测cycles均为正收益；不存在本项已测负/零cycles结果，不能编造。Vector零激活、Vector/Scan零detach及负向服务计数另行保留，不能把这些零值当成零性能收益。

## 三种不同证据

**Vector：无压力时的额外RO开销回避。** 策略开关确实开启，0/64激活，激活前Native接纳1000000、RO接纳0；原始F接纳RO1000000。它是额外RO服务开销的负对照，收益不证明“激活后的RO更快”。基线的activation0是POLICY_DISABLED，与开启策略后NO_ACTIVATION不同。

**Conv：实际触发可达，但端到端小收益。** 优化点61次激活、61/64 slice，激活前Native接纳229273；未激活slice为3、42、63。首次触发证明当时满足真实timed frontend、directory-ready、合格RO候选、非HIT及Tag全reserved或普通Line达到128的联合条件。不能由61/64推算全部联合事件频率或机会分母。

**Scan：少数slice激活，查询减少不等于关键路径改善。** 优化点4次激活、4/64，slice为25、27、36、62，激活前Native接纳13928689。RO查询14,536,577→607,828，减少95.818630%，完整cycles仅减少0.540163%。这是停止用查询数量代替应用性能的直接证据。

Conv查询1,322,161→1,111,583，减少15.926805%。普通Line-full事件2986→5649、bank-wait累计801419→803718是负向计数；完整应用仍略快。保留这些反向变化，不按单个机制计数给结构排序。

目前比较的是“条件RO策略相对eager Full-F”的整体差异。没有同输入独立分离触发前回避和触发后RO贡献的测量，不能将小收益全部归给触发后的RO、T或某一等待类别。

## 原样保留的RO人口

以下为64 slice最终累计记录各取一次，不能把192/2176个重复打印人口全部相加。

| 输入 | RO接纳 | transactions | merges | duplicate原计数 | detach |
|---|---:|---:|---:|---:|---:|
| Vector1700 | 1,000,000 → 0 | 250,849 → 0 | 749,151 → 0 | 0 → 0 | 0 → 0 |
| Conv850 | 1,322,070 → 1,111,555 | 376,204 → 306,537 | 945,866 → 805,018 | 1 → 1 | 14 → 15 |
| Scan850 | 14,536,577 → 607,828 | 3,721,306 → 156,327 | 10,815,271 → 451,501 | 0 → 0 | 0 → 0 |

六点均满足RO接纳=transaction+merge=responses、最终live0。transaction不是独立地址数。激活前Native接纳与RO接纳不是完整互斥分区：激活后仍有Native命中等路径，不能强凑成候选总分母。

Vector的小型V5 collector未导出RO query总数，因此此总结明确标NOT_EXPORTED，不将RO请求数冒充实测query总数。RO专属bank fill/response操作降为0也不等于全部Native数据访问或所有Bank成本被免费消除。

### Conv duplicate1的准确边界

Conv两点原计数均为1，**不改写为0**。复用已发布DUPLICATE_COUNTER_SEMANTICS_REVIEW：

- lower_accepted时比较同line另一个live RO entry的issued mask，未从另一entry的issued mask扣除ready位。
- 真正pending/lower-concurrency逻辑另用issued & ~ready。
- 因而1本身不能证明同时存在尚未返回的DRAM重复请求。
- 这也不证明实际事件只发生在ready/draining阶段，更不证明无害或全部同址所有权正确；事件级原因仍UNKNOWN。

此项不修改计数或Source，不为它追加raw大归因或模型。详细源SHA及定义保留于机器JSON和证据清单。

## 成本与资格

仍是一位运行时pressure epoch状态/每slice，加策略配置选择位、已有indexed Tag/MSHR压力结果的比较与选择逻辑。原Tag、Payload1168、四Bank/P1、WAD/TVD、descriptor、队列、查询端口及有限RO查询周期保留；没有新增隐藏CAM、Victim Data Array、Payload或免费更新周期。SET在真实frontend事件，CLEAR仅在新cache/完整命令epoch初始化，不偷偷加入动态回切或无限缓冲。

物理PPA、比较/选择组合路径时序尚未证明，完整epoch oracle仍是已声明的模型输入条件。1700MHz为服务敏感诊断背景，不等于真实GPU校准。应用NI未测、B0/M0a本项未证明、程序数值输出UNKNOWN，均不因本次归档接受或小型算术检查而改变。

等待类别非独占，跨slice累计不能相加成GPU关键路径cycles；边际峰值不还原联合触发，issued lower bytes不等于完成带宽。两个压力输入是有意选出的既有输入，不能称盲测总体。

## 收敛决定

1. 保留已有可选候选和三对精确结果；不改默认Source、不改历史，不把Vector18.775%推广为普遍收益。
2. 本轮停止阈值/回切、频率、为增加激活或merge人口而追加输入，以及没有具体性能机会的第二套B2查询重叠实现。
3. 仅当出现新的可实现服务结构、明确metadata/端口/ticket/周期成本和端到端性能机会时，先做该变更的有限生产CPU，再提交新Source匹配对照的独立精确科学申请。
4. 若未来确有新结构，Vector可作短无压力开销控制、Conv作已激活压力检查；长Scan仅在新结构确实针对其服务路径时再考虑。这是条件化顺序，不是本轮新实验申请。

机器结果：RO_STRATEGY_CONVERGENCE.json。计算及拒绝混参考检查：FINITE_CALCULATION_CHECKS.json。35份小型metadata的路径、字节数与SHA见SMALL_EVIDENCE_INPUT_MANIFEST.json。未读Trace/raw、未重跑原124/loader/生产parser资格，新增模型0。
