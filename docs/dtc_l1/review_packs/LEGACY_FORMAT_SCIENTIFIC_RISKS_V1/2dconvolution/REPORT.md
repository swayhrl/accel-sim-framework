# 2DConvolution：version3 历史编码约定与锚点风险

风险 ID：`2DCONV_V3_PRODUCER_EXECUTION_ANCHOR_V1`。级别：**高优先级科学适用性风险，OPEN**。这不是历史结果错误判定，也不是输入不受影响证明。

## 历史约定与已确认事实

固定成员header声明 tracer version3，但这个标签不能判定predicate/mask修复状态：

| 来源 | TRACER_VERSION | 打印mask | 地址压缩/列表mask |
|---|---|---|---|
| `475a282dd5baabfc481b3be44963e92fc3df34cc`，修复前 | 3 | P=active&predicate | E=active |
| `756ed33d503704b4faf97bb3a051792f0450d14c`，修复后 | 3 | P=active&predicate | P=active&predicate |

两份完整源码的SHA、行号依据及冻结consumer身份保存在 [CONSUMER_AND_ENCODING_SOURCES.json](../CONSUMER_AND_ENCODING_SOURCES.json)。修复前源码sha=`d9a7995178e95db6ebf467625036c805ad784d43ece233f6277c6ab217db318f`；修复后sha=`4f5aa97ac05c6d01ad9885c0bb51848483b9f1fad4153324dad49ae47a7fb639`。该版本同时存在两套地址mask合同；不能把正文布局version3与地址语义修复等同。

保留的launcher使用CUDA11.0并命名外部tracer_tool.so和postprocessor路径，没有其不可变二进制/source/JIT身份。路径中的20260821是本地输入整理标记，不是采集producer修复收据。header中的NVBit1.4也不是producer commit绑定。详细原始小文件收据见 [CAPTURE_FAMILY_METADATA.json](../CAPTURE_FAMILY_METADATA.json)。

## 有界正文审查

只读取先前标记出的同一个成员，复核40940条连续P、非零first(P)/stride的mode1记录，涉及1269140个活动lane地址。全部位于kernel `Convolution2D_kernel`，10个PC各4094条：

| PC | Opcode | 路径 | 记录数 |
|---|---|---|---:|
| 0120、0130、0140、0150、0160、0170、0180、0190、01a0 | LDG.E.SYS | 可缓存global load | 各4094，共36846 |
| 0250 | STG.E.SYS | global store | 4094 |

宽度均为4。完整逐PC计数及原始代表行见 [PC_OPCODE_RISK_COUNTS.tsv](PC_OPCODE_RISK_COUNTS.tsv)。没有重做几何/ISA/指令总量/完整输入身份审计，没有读取其他未标记成员。

原第1成员第58行：PC0120/LDG.E.SYS、P=`fffffffe`、base=`0x7fdc00000004`、stride=`4`。旧E-mask合同下 E=`ffffffff` 给活动lane1地址 `0x7fdc00000008`；E=`fffffffe`给 `0x7fdc00000004`。修复后的P-mask合同则把base绑定first(P)，符合后一种消费。**没有producer绑定就不能由version3选择这些合同或动态E。** 该反例的原行SHA、完整向量与路径已保留。

## 可能影响的模拟行为

40940条都存在条件性的活动地址差异。其中PC0120/0160/0190/0250的16376条，在兼容锚点解释之间改变32B sector及128B line的footprint身份和数量：可缓存load12282条，store4094条。举例，0120所涉31个lane的相对起始地址为4..124或8..128，4B宽度分别覆盖4或5个sector、1或2个128B line。cache/coalescing、下游请求、资源占用、写流量、等待和调度因而可能变化。

其余24564条在这个两锚点比较下地址不同而sector/line footprint相同。这是当前几何投影的事实，不是native地址语义或完整程序时序不受影响证明。没有运行模拟、比较cache状态或预测加速比。

## 尚缺证据与最小处理建议

缺少绑定该成员的tracer_tool.so/source构建收据，及在需要时用于判定旧E区间的原ELF/SASS/predicate/control-flow证据。优先做**单producer合同的取证**：若能证明实际producer使用修复后P-mask约定，可排除这里的旧E-mask锚点机制；若只能绑定修复前约定，则需针对这10个PC研究动态E。版本字符串、CUDA版本或现有运行PASS不能替代此证明。

如确需source reconstruction，可另交独立窗口研究这个单kernel/单成员；不要默认采用Hotspot模型或宣布原trace“应统一lane0”。在新解释获审之前，保留既有结果和状态，只登记风险及证据缺口。任何候选、输入替换、支持域调整或独立配对范围另审。完整风险索引见 [RISK_DETAIL_RECEIPT.json](../RISK_DETAIL_RECEIPT.json)，按 `workload=2DConvolution` 筛选40940条。
