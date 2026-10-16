# LUD 两kernel的global路径与执行锚点核查

结论：**UNRESOLVED_FORMAT_APPLICABILITY**。新增源码条件下的正面一致性证据支持冻结消费者现有global地址；没有建立原producer/ELF/predicate/control-flow绑定，不能把这种一致性升级为原采集语义闭合，也没有认定旧结果错误或不受影响。

## 精确来源与限定模型

保留包 `lud/cuda/lud_kernel.cu` 与GPU-app-collection commit `40e0052cebd3f98006190ed09e78f4981ef1a41b` 的同路径源码字节一致，SHA `fe3d0a5f06c82947f54cbf6fd9a75342b61263808a1587ead929fc3f8763fdc0`。源码既含两个kernel，也含 `lud_cuda` launch循环：默认BLOCK_SIZE=16，每个offset发射diagonal/perimeter/internal，最后一次只发diagonal。来源验证见 [APPLICATION_SOURCE_RECEIPT.json](APPLICATION_SOURCE_RECEIPT.json)。

本轮明确使用以下**未绑定原编译物的源码模型假设**：BLOCK_SIZE=16、matrix_dim=512、memcpy基址 `0x7fd9eb500000`、第 `2+3s` 个成员的perimeter offset为 `16s`。它们由默认源码、既有header/list及94成员顺序支持，但不证明原编译宏、数据字节或机器码相同。没有编译或执行新LUD程序。

## 两个kernel的global范围

在已登记57536条非零锚点风险中，`lud_diagonal`的13888条全部为shared访问；其global路径没有进入这个风险集合。原block16从lane0开始，源码global搬运位于每个有效thread都执行的循环中。这里只确认**既有该机制风险集合**没有diagonal global项，不宣称对整个kernel作了新的native/ISA资格认证。PC0540等7个shared风险PC保持旧报告范围。

`lud_perimeter`的global风险共19840条：24个LDG.E.SYS PC、11904条cacheable load；16个STG.E.SYS PC、7936条store。所有这些记录已按旧索引字节偏移稀疏重读并核原行SHA，未顺序重扫63/94个成员。其mask均为 `ffff0000`、stride4。见 [LUD_GLOBAL_PC_MODEL_CHECK.tsv](LUD_GLOBAL_PC_MODEL_CHECK.tsv)。

源码else分支令 `idx=threadIdx.x-16`：8个dia load分别读取row8..15；16个peri_col load与16个peri_col store分别读取/写入row0..15。每个PC仅用第一条记录在这些源码操作中识别标签；其余19800条作为后续独立记录核对，没有逐记录改拟源码操作。

40个PC的全部19840条记录都满足该源码模型，且在枚举first(E)=0..16时，唯一模型兼容锚点为16，恰与冻结first(P)消费相同。例：PC0140对应peri_col row0，第一阶段CTA0的lane16为 `0x7fd9eb508000`；把锚点强设为0会得到 `0x7fd9eb508040`，不符合该明确的idx映射。24个load/16个store的完整标签、各496条计数及代表地址收据见 [INDEX_AND_SOURCE_MODEL_RECEIPT.json](INDEX_AND_SOURCE_MODEL_RECEIPT.json)。

这是一项有界源码一致性检验，不是原capture证明：PC到源码操作标签来自首样本、没有SASS及predicate映射。若实际编译源码/宏/控制流不同，不能直接移植模型结论。没有以地址是否在数组内或性能好坏选择新解释。

## 保留的0x80/0x40歧义及来源

原diagonal第1成员第104行、PC0540/LDS.U、P=`0000fffe`、base0x40、stride64：已验证的旧producer源码按连续E压缩。E=`0000ffff`给lane1地址 **0x80**，E=`0000fffe`给 **0x40**，两者均能编码同一记录。该例属于shared，不把它误计到global；原行/索引身份及来源仍由上一包绑定。本轮不重做shared几何扫描；原37696条shared风险在明确参考几何下单条服务数相同，也仍不证明完整地址或所有配置时序等价。

## producer绑定、最小缺口与停止范围

旧traceall launcher、无version字段header、mode0/mode1混合形态与2020年3月E-mask源码家族相容；可验证的2021年version3 fork不能在固定TOOL_COMPRESS下生成同样混合模式，且header不同，不能用它认领原LUD采集。精确原library/ELF路径当前不可用；已检查validation包成员名中没有LUD目标，没有遍历无关ELF的符号。

最小后续来源是能把固定成员与实际producer合同及这40个global PC的编译/predicate/执行区间绑定的证据，不要求某一个特定hash。可优先验证实际BLOCK_SIZE、launch schedule和原SASS轮廓，或取得带E/lane的原始记录；无需先重建全部LUD、再扫629或再次计算shared bank投影。

本项在此停止，保留UNRESOLVED与原terminal PASS/科学待审状态。本轮没有把source-model一致性当作准入，也没有生成LUD新输入、修改地址、变更Lane A调度或发起配对性能实验。
