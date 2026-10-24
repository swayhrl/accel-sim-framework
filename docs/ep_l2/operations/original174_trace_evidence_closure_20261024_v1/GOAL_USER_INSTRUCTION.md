
新Goal：
ORIGINAL174_LARGE_TRACE_AND_RESEARCH_EVIDENCE_CLOSURE_V1

执行者：Lane T
执行位置：服务器端，原174 + 174-new + 真164
任务类型：连续执行、证据核验、恢复闭环
优先级：P0大型Trace > P1 PolyBench > P2实验原始记录 > P3 AWMA/C16

一、起点与总体目标

上一轮只读盘点已完成，禁止重复从零进行全盘扫描。

盘点基准：
commit 6a1a86ce3626bcd89274af071c4f4c5064ad607d

目录：
docs/ep_l2/operations/original174_remaining_asset_inventory_20261024_v1/

此前20套Trace迁移基准：
commit b93fc0dbac79d6f9c5ca027baa2d2e1cf371455b

必须先读取：
- STORAGE_SUMMARY.md
- LARGE_ASSETS_TOP30.csv
- LARGE_ASSET_EVIDENCE_GAP_QUEUE.csv
- POLYBENCH_TRACE_INVENTORY.csv
- ARCHIVE_COVERAGE.csv
- RAW_EXPERIMENT_RECORDS.csv
- AWMA_C16_ASSET_AUDIT.md
- UNKNOWN_AND_HOLDS.md
- 164现有恢复索引与不可变校验证据

目标是将现有资产盘点提升为可用于实际恢复和后续存储决策的可信证据体系。

本Goal以完整科研资产为对象，不以提高已归档百分比为目的，不为了PASS而改变科学输入、接受资格或既有证据。

二、P0：大型Trace全面闭环（最高优先级）

优先处理Top30大型Trace和已知大型压缩包。

重点包括但不限于：
- CUTLASS大型Trace及1/40变体
- Rodinia srad、lavaMD、hybridsort
- polybench.tgz（已有历史归档证据）
- rodina-3.1.tgz、parboil.tgz
- Parboil cutcp、MRI-gridding、stencil
- CUDA SDK scan
- PolyBench syrk、correlation、covariance、fdtd2d
- DTC m5-trace-immutable中的ATAX、MVT等
- 其他Top30和缺口队列中的大型输入

请按现有清单全部处理，不限于以上例子。

对每个资产必须回答：

1. 源文件是否完整存在？位于哪个真实物理端点？
2. 有哪些目录别名、同inode引用、历史压缩包或重复副本？
3. 精确文件成员、字节数、原始commandlist和顺序是什么？
4. 是否有足够的科研owner证据确定当前输入身份？
5. 真164上是否存在对应的完整原始内容？
6. 现有SHA、manifest、COMMIT和历史恢复证据是否足以证明内容相同？
7. 如已有内容但证据不完整，能否通过服务器端补充核验完成闭环？
8. 是否有有效恢复入口，以及是否完成过真实恢复验证？
9. 尚缺什么才能成为可信的可恢复归档？

特别要求：

A. 已有完整、可信且当前仍有效的SHA和恢复证据时，直接复用，不机械重算几十GB数据。

B. 如果缺少必要的内容证明，允许在真实服务器端进行受控全文件流式SHA校验。保持单流、有界内存、低优先级IO，不产生第二份大文件。

C. 校验Source与真164不能混淆端点。原174的/root/share/mnt164是MD127本地shadow；174-new对应路径才是真164 SSHFS。必须记录mount namespace、realpath和实际远端身份。

D. 压缩包与解压后的Trace分别建立身份关系。不得因为polybench.tgz整体归档，就把所有独立fraction/full/trim Trace自动列为已归档。

E. 此前20套Trace只证明精确冻结成员，不证明Source同目录所有额外文件已归档。应核对差集。

F. 真164存在完整可读raw树但未做完整native Target恢复的资产，要准确写成CONTENT_ARCHIVED_RESTORE_NOT_FULLY_TESTED，不误标成内容缺失。

G. 对资源允许的小样本，可以验证实际恢复；大输入不为了追求形式上的完整native恢复而额外复制数十GB。需要完整本地恢复才能证明的部分如实保留HOLD。

H. 仍然没有真164内容证据的资产，列为REQUIRES_ARCHIVE_ACTION，保留准确的输入、字节、目标位置、传输资源要求与必要权限。不得假装已经归档。

处理顺序：
先复用现有证据关闭容易核准的项目，再补最有价值的缺失证据，最后整理真正需要新增传输的对象。

三、P1：PolyBench所有已发现变体

以现有28项PolyBench Trace/Package变体为初始集合。

逐项核对：
- 程序名称
- 输入规模
- 原始Trace版本
- full / fraction / trim
- commandlist及kernel成员
- 真实Source端点
- 真164对应副本
- 完整内容校验证据
- 恢复范围
- 科学输入资格

必须区分：
1. 整个Trace目录完整归档
2. 仅某个冻结selector完整归档
3. 仅历史压缩包完整归档
4. 仅部分成员或片段归档
5. 归档内容未知

R13历史归档原样保留，不重复计数此前已释放的展开数据。

如果发现现有28项之外的明确重要变体，可补充登记，但不进行新的无界全盘扫描。

四、P2：实验原始记录的可恢复性

复用RAW_EXPERIMENT_RECORDS.csv及各科学owner的accepted evidence。

按项目核对：
- EP-L2
- DTC-L1
- C2P/M2D/TLS
- AWMA
- C16

区分：
- 完整原始模拟器输出
- 接受结果的CSV/JSON/日志
- 输入配置和命令
- 源码及二进制身份
- 正确性与性能统计证据
- 中间构建和重复生成文件

重点确认历史已接受结果能否从现有164归档恢复，而不是只保留论文中的最终数字。

已证实的E057和AD_GEMM结果不要重复做无意义的传输或验证。

输出不同项目的raw结果规模、归档覆盖、缺失证据、真实恢复范围和优先级。

不能因为文件扩展名是JSON、log或CSV就认定其为完整科研原始记录。

五、P3：AWMA/C16未闭合证据

AWMA：
- 复核164中96个run catalog及其声明的114.173GiB逻辑数据。
- 对90份manifest匹配保留既有证明。
- 重点核对剩余6份digest不匹配的具体原因，区分摘要定义差异、文件变动、缺失或真正损坏。
- 调查Q05 accepted SIM_EVIDENCE恢复locator缺口。
- 已知V4部分矩阵仍为PARTIAL，不得升级科学结果。
- 不自动触发109上的新GPU任务或采集。

C16：
- 保留原164六份模型完整SHA证据。
- 原174规范六份模型继续ACTIVE_KEEP。
- 核对当前恢复入口、模型身份及历史回执。
- SSHFS inode变化不能直接解释为数据变化。
- 不执行新的模型退役、迁移或删除。

TLS：
- 核对P9正式归档缺口391,334,023B及相关恢复状态。
- 不重启原P9事务、不接管旧lock/controller。
- 对其余未完成的planned groups只做状态和证据核对。

本阶段主要解决证据和恢复定位问题；无法通过只读核验解决的对象形成后续动作清单。

六、资源与操作边界

本Goal允许：
- 精确范围内的只读目录和元数据调查
- 必要的服务器端流式内容SHA
- 校验已有164归档和恢复索引
- 小规模、隔离的恢复验证（须符合资源预算）
- 在独立审计工作区生成脚本、报告和回执

本Goal不允许：
- 新的大Trace批量搬运
- 删除、移动、覆盖任何Source
- 清理历史实验结果、模型或缓存
- 重启旧迁移Goal或旧科学Goal
- 修改AEFAIR及其他正在执行的科学任务
- 改动科研预算、controller、accepted结果或原始实验身份
- 向GitHub上传原始大型Trace、模型或敏感配置

如发现确实需要新增归档，先完成COPY_PLAN_READY证据，明确所需源端、真164目标、字节数、空间与IO预算，再等待独立授权。

优先复用既有单sender/receiver、≤128MiB分块和≤256MiB暂存的成熟方案，但本轮不擅自启动新的数据复制。

必须持续检查AEFAIR及其他实际运行任务的PID/start_ticks、资源余量和IO压力。遇到资源冲突优先暂停重IO验证，切换其他低成本工作。

严格防止空Source路径解析为cwd/home；所有Source根必须非空、绝对路径、限定科研命名空间。不得读取或发布无关账户秘密。

七、执行策略

这是一个连续Goal，不拆成多个需要人工反复启动的Goal。

P0优先执行，尽量完成Top30逐项闭环；之后自动推进P1、P2和P3。

普通脚本、路径、manifest解析及工程问题自行解决并继续。

遇到缺少科学owner资格、重要数据身份冲突、无法满足的资源约束或必须新增数据传输时，保留明确HOLD及下一步要求，不擅自假设。

对每个处理对象给出：
- ARCHIVED_CONTENT_VERIFIED
- ARCHIVED_RESTORE_VERIFIED
- PARTIAL_ARCHIVE
- NOT_ARCHIVED_CONFIRMED
- DUPLICATE_OR_REUSABLE
- UNKNOWN/HOLD
- REQUIRES_COPY_AUTHORIZATION

内容归档状态、恢复验证状态、科学接受状态必须是独立字段，不得用一个PASS混合表达。

八、最终交付

请在独立审计分支提交：

1. LARGE_TRACE_CLOSURE_MATRIX.csv
   Top30及补充大Trace逐项完整状态。

2. POLYBENCH_FULL_COVERAGE.csv
   28项及新确认变体的完整关系与归档结果。

3. RAW_RESULTS_RESTORABILITY.csv
   各项目原始科学记录的保存和恢复覆盖。

4. AWMA_C16_RECOVERY_GAP_CLOSURE.md
   六个manifest差异、Q05、C16及相关缺口。

5. SOURCE_TO_TRUE164_RECOVERY_MAP.json
   已证实内容的精确恢复定位和证据引用。

6. ARCHIVE_ACTION_QUEUE.csv
   尚需补归档的内容、大小、优先级及资源要求。

7. RESOURCE_AND_ACTIVE_SCIENCE_AUDIT.json
   服务器端IO、空间、身份与活跃任务保护回执。

8. FINAL_STATUS_AND_RECEIPT.md
   完成数量、剩余HOLD、总字节及结论边界。

额外提供按项目汇总：
- 已证明归档的独立资产数量和逻辑字节
- 已证明可恢复的数量和字节
- 仅有部分归档的数量和缺口
- 证据不足的数量与缺口原因
- 待授权复制的独立数据量
- 可能复用的已有副本及节省传输量

所有统计要去重，明确Source、MD127、174-new SSD、真164之间的物理归属；不能把路径别名当独立数据，也不能把逻辑字节相加冒充物理空间。

九、结束条件

必须处理完当前Top30和28项PolyBench清单，对每项给出可信状态或明确、不可自行解决的HOLD。

其后完成P2/P3中已有证据可解决的缺口。

不要求通过伪造或强推PASS消除所有HOLD。

输出下一轮真实需要复制或恢复的最小集合，按价值、字节和风险排序。

完成后提交GitHub，并对报告和关键回执进行远端回读核验。

最后汇报：
- 哪些大型Trace现在已可以放心从164恢复
- 哪些还缺真正的数据副本
- 哪些仅缺恢复验证
- 哪些可以通过现有归档直接复用
- 多少实验原始记录已完整保留
- AWMA/C16还有哪些关键风险

不得在本Goal结束时自动执行迁移、清理或释放Source。
