# Btree：mode0 full32 地址列表的独立科学风险

风险 ID：`BTREE_LEGACY_MODE0_LIST_ASSOCIATION_V1`。级别：**高优先级科学适用性风险，OPEN**。这里的级别表示需要审查输入来源和地址解释，不等于宣布历史结果错误，也不等于已证明不受影响。没有修改任何准入状态。

## 已确认事实

既有11负载格式筛查在 Btree 的第1成员找到6000条 mode0 额外地址记录。本轮只读取这一已标记成员，复核数量与旧筛查完全一致；第2成员未重读。6000条都在 kernel `findRangeK`、PC `1c40`、opcode `LDG.E.SYS`、实际宽度4，全部只有一个活动 lane，列表却有32个原始地址字。

冻结 parser 用列表前 popcount(P) 项填活动 lane。历史 E-list 编码约定则把这32个字对应 lane0到31。因此，这一**来源约定下**5792条记录各有一个活动地址不同，其余208条在这个比较下相同。完整逐 PC 数量及代表记录见 [PC_OPCODE_RISK_COUNTS.tsv](PC_OPCODE_RISK_COUNTS.tsv)，机器摘要见 [RISK_SUMMARY.json](RISK_SUMMARY.json)。

原始第1成员第691行，P=`10000000`，活动 lane28：word0=`0x7f8eed50bc04`，word28=`0x7f8ef0d10f88`。冻结消费给 lane28 前者，历史 full32 关联给它后者。原始行 SHA 是 `1a796138e666ecfb5b7ae812ad5a9f275b0c1225ed501d96c60d6976c51eedf8`。地址值及顺序是原 trace 字节事实；历史 source-family 合同对本次采集的适用性仍需独立确认。

## 可能影响的模拟行为

`LDG.E.SYS` 在冻结 consumer 中属于可缓存 global load（CACHE_ALL，没有 STRONG.GPU/BYPASS 修饰）。5792个不同地址也分别落在不同的32B sector和128B line。每条仍只有一个活动 lane，单条 footprint 数量仍是1；变化的是 line/sector 身份，而不是该条访问数量。可能影响 cache/tag/sector 命中、合并对象、DTC/PIB/MSHR 压力、下游流量、等待和调度；没有运行 cache 状态或时序模拟，不能推断影响方向或加速比大小。

删除额外地址项还可能改变 parser 随后读取的未使用 `imm` 字段；冻结 consumer 对 LDG 不使用该字段。这里没有创建候选 trace 或规范化器，因此没有作任何删除。该细节也不能替代地址解释审查。

## 尚缺证据与最小处理建议

缺少与固定成员绑定的原 tracer/library、采集可执行文件及其不可变构建/JIT 收据。header/launcher、原始 full32 列表及历史源代码是强烈的来源家族证据，但本报告没有恢复精确采集身份或验证 native 数据/输出。

建议先审查这个**单成员、单 kernel、单 PC** 的 E-list 适用性与现有结果的科学外推边界。若之后决定采用新的派生解释，可另设独立窗口制作只针对该成员和PC的白名单候选，登记新输入身份，再由 Lane A 审查最小匹配比较；不把 Hotspot 的已接受研究路线自动推广到 Btree。当前不补丁主 parser，不覆盖已有结果，不新增 HOLD、不改变接受状态，也不自动启动或登记重跑。

原输入的历史 receipt、原行身份和全部104476条跨程序风险索引的 SHA 见 [公共证据收据](../RISK_DETAIL_RECEIPT.json)。筛选 index 的 `workload=btree` 得到全部6000条；该索引是诊断表，不是派生科学输入。
