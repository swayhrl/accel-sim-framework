# r5：重绑定c948的静态字段、比较逻辑与关键路径成本账

精确目标Core `c948184504d82b80e23eb3f4ff6cdfd328ba9355`，与publication
`57e1c363aede1a7790bdf94136d832d35ee7b34b` tree相等。它尚未编译，binary=null；
source字段存在不代表生产门槛PASS。FIELD_COST_LEDGER.csv给逐项原文件／行锚点，
SOURCE_MANIFEST给完整blob hash。r3成本与撤回附录保留不变。

| 代码／资源事实 | 可审查的表示假设 | 物理未知与差分责任 |
|---|---|---|
| N=1168/1160，4 bank，bank class分别292/290；line128B | data RAM146/145KiB；同一latch128B，两侧阵列+latch146.125/145.125KiB，chip9.1328125/9.0703125MiB | ECC／macro外围／控制／线网另计，不等于面积相等 |
| slot.role三种、state八种，owner/generation/pending/ready/pins | 若独立编码：2+3+(A−7)+G+4+4+K bits/slot；A48/G16/K6时76bits，N1168为88768bits=11096B | 这是gross字段表示，不是全部增量；role/state相关可压缩但需真实编码；K6/G16不是已证安全最小值 |
| PayloadHandle为ID+generation，1024个Tag关联 | P11；若显式保存G，则1024(P+G)；G16=3456B/slice | 只存ID为1408B，不可忽略generation所存位置；若B/U均pointerized则共同，非全部共享增量 |
| ft_wb_record含handle、born、expected，WAD最多128 | 128(P+G)，G16=432B/slice；另加packet binding J、state／valid | born是年龄统计，expected是reference sidecar，不能把software map或mem_fetch*大小当SRAM面积 |
| ft_replacement三handle、landing_id、Tag index、phase、四flags | 已知字段3(P+G)+P+10+2+4，G16=108bits；地址key／packet引用／saved rollback状态另计 | 若landing_id与handle可合并，需证明生命周期一致；saved slot不赠送免费shadow副本 |
| slot.versions、copy_versions、WB expected | 验证sidecar，不能代替128B data RAM；共同copy latch仍计1024bits | 不直接合成软件reference版本数组；如真正采用版本硬件需另设计并计费 |
| source以physical GPU cycle仲裁，保留Tag timestamp顺序 | 单周期bank busy至少4位；selected token、retry state需明确有界 | m_cycle软件64位时钟／monotonic assert不是必需的64位硬件时间寄存器；未编译候选不能宣称实际一op/cycle合格 |
| allocator扫描role/state/owner/pin并选择bank-compatible落点 | eligible bitmap N位或free-list NP位+控制为替代方案；每bank选择292/290候选 | 选择/priority encode、端口、扇出与critical path需RTL，不能把软件扫描变成免费组合逻辑 |
| 每Bank pending/granted按oldest-ready处理 | 若Q_b项、age E位，token宽需P+G+op+E+valid；二叉选择Q_b−1个E-bit比较节点、深ceil(log2 Q_b) | 未把vector长度当硬件队列深度；Q_b/E边界、wrap、tie-break、mux/线网均待证明，不能额外偷加queue预算 |
| handle_live和handle_owner_matches索引验证 | occupied与G位相等比较，owner再加A−7位相等比较；bank class取低2位 | 并发读取端口／复用与阶段划分待RTL，不因非CAM就“零成本” |
| WAD128，TVD另有查找 | 若全并行，128组A−7位equality，A48共5248个bit比较位置 | 非门数或延迟数字；串行／分级lookup需说明是否改变时序合同，TVD+1cycle不等于STA达标 |
| D512／native128／每地址32，RO已有N配置completion | descriptor ID9位，0..32 count6位；RO配置N与live bound分开，r3 N成本修订沿用 | 新RO/TVD适配不意味着已应用资格；新字段须按最终官方repair-base与实际接线复核，oracle不免费 |

COST_MODEL.json列六个N/G场景，A48/K6均明确是假设；不提供总metadata上限、
mm²、mW或STA数字。该JSON/CSV是本Lane新派生成本资产，绝非原始科学CSV的修改。

关键路径审查：

1. hit：Tag→句柄存活／generation／owner→Bank授权→RAM→response。pointer化与
   generation是否同阶段可读尚未证明，不把全部比较放进一个“免费命中周期”。
2. replacement：WAD及控制预留→eligible/free-slot选择→旧owner/pin复核→commit；
   失败保持Tag和payload原子不变，rollback保存/读端口的代价另计。
3. WB send：handle／reference→bank read→下层实际接收→释放。WAD继续到set_done；
   发出指针不构成数据交接。copy路径额外read/write与共同latch均按真实服务计。
4. TVD/RO：TVD独立lookup建模+1cycle；RO late fill的generation／sector及ICNT
   backpressure各有控制路径；不以软件函数调用数换算逻辑级数。

能量只保留方程：E_dyn=Σbank read/write事件×匹配宏能量+线网/latch+控制活动；
已计RAM读写时，copy附加项不重复计阵列。匹配工艺、频率、泄漏和执行时间缺失，
不填节能比例。代码修复不扩大payload预算，host prefill复用唯一allocator。

c948已移除先前重复getter并同步测试时钟；这两个源差分不改变本账的payload字段。
三份字段源blob与62dc逐字节相同，因此重绑定新SHA，未重复旧bits计算或测试。
未编译候选仍不构成运行／PPA资格，不能再叠加旧getter删除patch。
