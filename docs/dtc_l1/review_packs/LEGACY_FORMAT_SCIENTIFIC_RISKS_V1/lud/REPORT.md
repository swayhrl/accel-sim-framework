# LUD：执行地址锚点的独立科学风险

风险 ID：`LUD_LEGACY_EXECUTION_ANCHOR_V1`。级别：**高优先级科学适用性风险，OPEN**。没有认定现有结果错误，也没有认定输入已证明不受影响。没有选择新的地址解释。

## 已确认范围、PC 与 opcode

既有94成员中，本轮只读取先前已标记的63个成员；31个没有非零锚点风险指标的成员未重读。与旧筛查匹配：57536条 mode1 记录具有非零 first(P)、非零 stride 和连续 P，涉及787296个活动 lane 地址。它们分属两个 kernel 的95个 `(kernel,PC,opcode)` 项、93个不同 PC 数字。**PC必须连同kernel标识**，不能跨kernel按PC数字套用规则。

| 范围 | 记录数 | PC/opcode 范围 |
|---|---:|---|
| `lud_diagonal` | 13888 | 0540/LDS.U、05a0/LDS.U、05f0/STS、0640/STS、0740/LDS.U、0750/LDS.U、07c0/STS |
| `lud_perimeter` cacheable global loads | 11904 | 24个 LDG.E.SYS PC，各496条 |
| `lud_perimeter` global stores | 7936 | 16个 STG.E.SYS PC，各496条 |
| `lud_perimeter` shared loads/stores | 23808 | 48个 LDS.U、STS、LDS.U.128、STS.128 PC，各496条 |

逐项完整PC、opcode、真实宽度、数量及原始代表行见 [PC_OPCODE_RISK_COUNTS.tsv](PC_OPCODE_RISK_COUNTS.tsv)。shared合计37696条；global合计19840条，其中11904条为可缓存global load。没有把STG误计为可缓存load。旧筛查另外发现的26560条 first(P)非零但stride0记录，地址不随锚点改变；本轮不把它们算入57536条风险记录。

## 保留的具体歧义及来源

原第1成员第104行：kernel `lud_diagonal`，PC0540，`LDS.U`，P=`0000fffe`、base=`0x40`、stride=`64`。历史源代码打印P=E&predicate，却以E进行base_stride压缩，并要求E连续且至少两lane。

- 若 E=`0000ffff`，base属于lane0，活动lane1地址为 **0x80**。
- 若 E=`0000fffe`，base属于lane1，活动lane1地址为 **0x40**。

两种E都满足该历史编码合同，序列化字段相同。源码依据是已保留的2020年3月/8月 producer，哈希及版本由公共来源表绑定；11月修复改为按P编码。原行路径、偏移、原始行SHA和完整前后假设向量在PC表及索引中保留。没有用地址合法性或较少bank冲突来选择一个解释。

仅凭这个局部反例不能证明两种执行历史都匹配完整原二进制。连续的半warp P既可能来自真正的半warp执行区间，也可能来自全warp执行中的predicate；缺少采集绑定的SASS/control-flow/predicate证据，不能选定动态E。

## 可能影响的模拟行为

对每条风险记录枚举全部兼容 first(E)=0..min(first(P),30)，不选择一个锚点。global的19840条在至少一种解释下改变32B sector身份及数量，其中9600条也改变128B line身份及数量；按路径细分，cacheable LDG有11904条可能改变sector数量、5760条可能改变line数量，STG对应7936/3840条。可能改变访存合并、cache/sector行为、下游流量、资源等待及调度。它们是CPU footprint投影，不是已运行的事务或时序结果。

37696条shared风险记录在32bank、4B word、单warp分区、unlimited broadcast的明确参考几何下，**所有枚举锚点的单条bank服务数都与冻结消费相同**。这里的统一字对齐平移保留了每bank不同word数量的最大值。冻结Core只用每lane第一个起始地址作该服务计算，包括16B LDS/STS形式。因此这个单条服务投影不能判定地址正确，也不能作为整个LUD或所有历史配置时序等价的证明。其他配置、跨记录依赖和native功能语义没有在此被认证。

## 缺失证据与最小处理建议

缺少与固定输入绑定的原 producer/ELF/JIT、完整SASS predicate/control-flow及动态执行区间证据。建议下一轮如需深入，另交独立窗口仅研究上述两个kernel/95项轮廓，优先闭合11904条cacheable-load和7936条store的锚点，而非重建全部LUD或重复629审计。shared可保留服务投影不变这一有界证据，但不据此标为“不受影响”。

本轮到独立风险登记及具体地址备选为止；不生成LUD新trace，不要求恢复某个特定hash才能继续讨论，也不将Hotspot源码模型迁移到LUD。任何新的输入解释、结果外推范围或后续配对实验均需另审，Lane A状态及原结果保持原样。全量风险索引见 [RISK_DETAIL_RECEIPT.json](../RISK_DETAIL_RECEIPT.json)，按 `workload=lud` 筛选57536条。
