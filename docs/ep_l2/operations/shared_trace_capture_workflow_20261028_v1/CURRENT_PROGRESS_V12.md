# V12 研究规模优先的资产与采集计划

交接基线时间：2026-10-29T10:54:48.801281+08:00；新重复优先范围另见E118。用户已调整交付方向：优先复用规模可控的现有资产，新采集先逐源码评估重复次数缩减，空间缩放另作有明确用途的轴；alignedTypes、transpose及同类巨大默认输入的全量后处理和裁剪不再是本轮硬门槛。完整大raw仍需SHA归档和轻量检查，已有trace、F9校验、部分GROUP及失败现场全部保留。[生效范围](evidence_v12/E112_ROOT_USER_RESEARCH_SCALE_FIRST_SCOPE.json)覆盖V11及更早版本的规模安排，历史报告仍保留原时点。

## 全注册成本审计与优先顺序

| 单位 | 数量 | 解释 |
|---|---:|---|
| 已注册输入来源单位 | 243 | 关联历史队列与实际资产的来源身份 |
| 声明元数据成本组 | 240 | 只合并3组元数据相同候选，不证明运行时输入字节或consumer profile等价 |
| 历史队列行 | 242 | 原状态保留 |
| 公共常规对象与裁剪关联 | 71与71 | 裁剪关联父对象，不作为额外71个workload |
| 独立RAW对象 | 3 | 当前已发布数量 |
| typed专项 | 8完成、153延期 | 与公共对象数分开 |
| 记录规模UNKNOWN | 165行 | 不按小规模或不可运行处理 |

[243行瘦投影](REGISTERED_COST_THIN_V12.json)保存注册ID、程序版本、声明身份指纹、已知记录数、规模建议及资产关联。1,570,112B完整注册表保留在NAS，原路径、字节数和SHA见[索引](EVIDENCE_INDEX_V12.json)。Root已核过全量成本视图引用；重点源码绑定为37份匹配冻结job source SHA、6份build join仍UNKNOWN、0份不匹配。审计不会给未知输入授予运行或科学资格。

先使用规模可控的公共资产和当前EP／DTC精确SM70输入；对巨大默认版本避免继续付出长时间分组成本。四份已完整采集的大raw合计20,344,674,408B，约20.3447GB，下一步是SHA归档和轻量检查，当前仍待归档，不能写成已提交。旧scan及SDK42默认simpleStreams为不完整现场，继续留缺口；新小版本通过也不代表旧大版本完成。

## 重复次数优先的研究计划

用户进一步同意repeat-only-first：[新生效范围](evidence_v12/E118_ROOT_USER_REPEAT_ONLY_FIRST_SCOPE.json)要求保留原空间工作集、路径、类型与warmup，只先缩减源码证明可单独控制的重复。2轮只是候选，不能盲称保住cache或稳态。空间规模缩减作为另一条有明确用途的轴，不再是默认研究方案。

[可执行审查方法](WORKLOAD_REPETITION_REDUCTION_METHOD_V1.md)和[填写模板](WORKLOAD_REPETITION_REDUCTION_REVIEW_TEMPLATE_V1.json)分别覆盖身份／配置、loop分类、读写反馈与同步、最小diff、保留丢弃矩阵、必要的2／4／8校准，以及原QA到轻量consumer的验收链。[机器建议表](RESEARCH_SCALE_PROPOSALS_V12.json)已改为重复优先，旧空间建议仅保留NAS来源引用，全部仍待逐源码评估和新身份验收。

scan可先评估保留原N6815744及全部17长度、100轮降2轮；large每轮3阶段全保，预期66个kernel，但仍可能1e8级记录。alignedTypes保原50,000,000B和类型矩阵后评估host32→2；convolution保原3072×3072与row／column链后评估host16→2。transpose先拆清不同版本NUM_REPS的host与device传播；simpleStreams的累加和QA端点随重复变，不能称原数值等价。stencil时间步、streamcluster收敛、网络stage和grid-stride不当冗余删。

## 根据实际模型选择工作集与CTA波次

已消费并接受的一个EP配置REF32x8_L100，在实际命令按顺序加载的4份配置覆盖后，生效L2为2MiB、80个SM，几何为32 sets×8 ways×128B×64 slices。后加载的配置覆盖基础24 ways／6MiB；这是配置加载顺序的结果，不是直接CLI cache参数获胜。[实际配置证明](evidence_v12/E114_ACTUAL_CONSUMED_EP_EFFECTIVE2MIB80SM_CONFIG_PROOF.json)及[Root重新解析验收](evidence_v12/E113_ROOT_COST_VIEW_AND_EFFECTIVE_EP_CONFIG_ACCEPTANCE.json)仅支持这一条EP路线，不代表物理RTX4080或全部DTC配置。

先挑选1至2个工作集相对生效L2的比例点，再检查CTA波次：totalCTAs／(SM数×每SM实际可驻留CTA)。驻留CTA受线程、寄存器和共享内存共同限制，不能固定假设32。建议研究档完整采集约1至10M条warp records；超过100M条或1GB时先复核研究目的与规模。这些是成本建议，尚不是新硬门或采集资格，实际header、占用率和记录预算仍需核实。

## 已完成的scan小版定位为工程冒烟

原device、gold、header及host gold QA代码保持的离线ELF为0bcb102ac67c4402eafdb35aa19808cfc52e7a72a3737b06b67ff2f0a62fbc64，[源码验收](evidence_v12/E115_ROOT_SMALL_SCAN_SOURCE_AND_OFFLINE_ELF_ACCEPTANCE.json)之外，现已有[native QA2](evidence_v12/E116_ROOT_SMALLSCAN_NATIVE_QA2_ACCEPTANCE.json)和[capture2](evidence_v12/E117_ROOT_SMALLSCAN_CAPTURE2_ACCEPTANCE.json)真实闭合回执。short LEN1024和hier LEN16384在N262144、repeat1、seed2009下分别完整采集1／3个kernel；229376／272200条是producer声明记录，尚不是F9或consumer资格。

该版本仅为engineering_smoke。相对原N6815744，N缩为1／26且只选2／17种长度，两主数组总工作集52MiB→2MiB，hier中间grid26→1。输入seed／libc和FNV绑定服务于该smoke身份，FNV不充当SHA；通过不证明原版缓存、并行度或研究代表性。下一研究候选优先固定原工作集再评估重复，而非继续默认缩N。

## 当前执行与保留边界

旧五项资源停止和随后默认scan的用户停止均按其闭合时点保留；新小版QA2和capture2也已闭合。后续归档或执行状态应另按真实回执更新。旧五项因资源门停止、随后scan按用户要求停止，均保留闭合历史；已完成的F9及部分GROUP不重跑。conv a001在metadata owner JSON的tuple／list边界失败，未执行GROUP32正文；不启动a002大规模延续。本地work与大默认继续执行的候选只能保留为工程来源，不覆盖新的研究规模安排。

当前公共71常规、71裁剪、RAW3和SM70公共125输入保持。V10闭合的当前EP／DTC64绑定、64启动、63退休与61精确配置接受证据继续复用；三类科学限制仍按其原时点解释，不移植到新小profile。全量161适配和全库SM70正文恢复仍不作为本轮硬门槛。源KEEP、释放0，科学资格、预算和242条历史均不改，外部ChatGPT审稿尚未收到。
