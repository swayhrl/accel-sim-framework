# 工作负荷重复次数缩减方法

优先保留原空间工作集、路径、数据类型、算法阶段和warmup，只缩减源码证明可单独控制的重复。每个缩减版本建立新binary、argv、input与profile身份，原资产和失败现场保留。2不是通用稳态保证，体积小也不等于模拟快。

## 1 固定身份与研究问题

填写[审查模板](WORKLOAD_REPETITION_REDUCTION_REVIEW_TEMPLATE_V1.json)：程序与源码版本、原命令、输入或seed和ABI、binary SHA、producer以及目标consumer。先说明研究缓存、并行度、依赖、吞吐还是算法结果，再按实际加载顺序解析模拟器配置。

当前一个已消费EP REF32x8_L100实例的有效L2为2MiB、SM数80；后加载的config-2覆盖早先值，[配置证明](evidence_v12/E114_ACTUAL_CONSUMED_EP_EFFECTIVE2MIB80SM_CONFIG_PROOF.json)不代表物理4080或所有DTC。保留原工作集相对有效L2的比例、CTA数量与波次；波次使用实际资源限制下的resident CTA，而非盲用上限32。

## 2 逐源码循环分类

| 循环类别 | 默认处理 |
|---|---|
| 冗余计时重复 | 可作为首选缩减轴，但先检查每轮状态与warmup |
| 内核微基准重复 | 单独分析；减少会改变单次kernel的指令与访存轨迹 |
| 独立batch | 是覆盖范围，只有明确用途才减少 |
| 数据遍历或grid-stride | 保留，删除会漏算元素 |
| 算法stage或网络merge | 保留完整依赖链 |
| 时间步 | 保留原时间跨度；改变属于另一个问题 |
| 搜索与收敛 | 保留终止准则和必要迭代，不能当计时冗余 |

每个loop记录源码行、控制变量和调用传播。分别查host launch外循环、device内循环、库内部循环；同一个NUM_REPS可能进入多个位置，不能全局替换。

## 3 写出每轮状态流

逐项列出读写buffer、RNG及seed、重置位置、是否覆盖全部输出、是否读取上一轮结果、地址顺序与输入分配是否稳定。画出或列出launch依赖，以及stream、event、同步和queue次序。检查warmup是否触达同一数据、cache或分配，减少测量重复时保留原warmup策略。

数学结果可相同而跨轮cache状态不同；host循环独立也不能证明device工作可删。没有源码闭合的loop保持UNKNOWN，不凭变量名或运行耗时猜测。

## 4 做最小修改并声明保留与丢弃

只改已定位的重复控制，记录diff、原值与候选值。支持CLI的用参数，不支持时显式修改review过的常量，不编造选项。新构建绑定完整source、flags、binary与输入；不把小版本标为旧大版本完成。

| 信息层 | 需要评估的证据 |
|---|---|
| 数学与bitwise输出 | 给定输入和重复数下按原gold／QA规则验收；容差通过不等于逐位相同，相同公式不自动等于原最终输出 |
| 单轮SASS与地址 | kernel代码、参数、grid/block、访问范围及顺序是否保留 |
| 跨轮cache和稳态 | cold／warm状态、上一轮遗留、轮次依赖是否仍代表目标 |
| 长期计数与代表性 | 丢掉的总访存、稀有路径、频次分布或收敛行为逐项声明 |
| 计时统计 | 重复样本减少会损失均值／方差精度，不能继承原计时结论 |

## 5 必要时用2或4或8轮校准

先固定空间工作集和算法覆盖，再选一个最小候选；只有研究结论依赖稳态、cache延续或稀有事件时，才追加必要的2／4／8轮对照。事先给出记录量、原生时间、插桩时间和模拟指令／周期预算及停止条件。校准不足时收窄用途或保留更多轮次，不以“2轮已跑完”推导代表性。

GPU原生耗时、插桩采集耗时和模拟器耗时分别记录。压缩GB受格式、重复性及压缩器影响，不能直接换算模拟时间。

## 6 沿现有QA和轻量consumer链验收

按新身份依次取得原native gold QA、受限trace中完整launch／record覆盖和数据校验，再复用适用的轻量decoder／launch／retire路线并声明用途。ROI前缀只用于成本观察，不能充当完整资产。producer声明计数、全量记录验证和consumer退休指令分别记录。

不默认遍历全部配置、完整模型回放、重写独立数值oracle或保存所有host数组。原gold不适用时先说明变化原因和必要补充；不能跳过算法正确性。

## 7 scan与其他程序的复用例子

原scan为N6815744、17种长度、100轮。外循环每轮读取固定d_Input并完整重写d_Output，没有跨round算法反馈；large每轮的3个stage仍必须全部保留。保持原N与17种长度、改2轮，预期完整66个kernel，仍可能达到1e8级记录；这不是模拟快或cache等价的承诺。

已执行的scan小版是engineering_smoke：N262144为原N的1／26，选2／17长度、repeat1。两主数组总工作集由52MiB变为2MiB，hier中间grid由26变为1，空间与并行信息明显改变。short／hier原gold QA及完整1／3kernel采集已分别留证：[native QA2](evidence_v12/E116_ROOT_SMALLSCAN_NATIVE_QA2_ACCEPTANCE.json)、[capture2](evidence_v12/E117_ROOT_SMALLSCAN_CAPTURE2_ACCEPTANCE.json)。声明229376／272200条记录还不是F9验证或模拟器资格；这些通过仅证明该smoke自身，不证明原研究代表性。

simpleStreams的累加值和correct_data公式随nreps变化，host重复与kernel内部迭代需分开；stencil时间递推、streamcluster收敛、sortingNetworks stage和grid-stride必须保留。transpose不同源码版本的NUM_REPS传播不同，先读[版本绑定建议与源码引用](RESEARCH_SCALE_PROPOSALS_V12.json)，再决定只改哪一层host重复。

## 8 可复用交付与退出清单

- 原身份、研究问题、有效配置及loop分类齐全，读写／反馈／同步／RNG／warmup已说明。
- 最小diff、新身份、保留与丢弃矩阵及必要校准范围已审；没有把空间缩减混成repeat-only。
- 记录／wall／存储预算与失败停止条件先冻结，QA、完整采集、数据和轻量consumer证据分别闭合。
- 原资产KEEP；中断、超预算或不完整结果明确归档为gap，不拼接不同进程前缀充当原完整trace。
- 能完成SHA与轻量检查的大raw可先归档，昂贵POST／裁剪按用途延期；发布时写清工程smoke、repeat-only研究候选或另行授权的空间规模轴。

模板只是审查记录。每个资格必须引用真实回执，任何空栏、建议值或批准状态文字都不能替代实际验收。
