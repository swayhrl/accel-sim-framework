
新Goal：ORIGINAL174_RESEARCH_ASSET_ARCHIVE_EXECUTION_V1

执行者：Lane T
执行环境：原174、174-new、真164
任务：已审计科研资产的分批COPY_ONLY归档
模式：一个连续Goal，solve-and-continue，有限清单，不重复全盘扫描

一、已完成的基线

只读盘点：
6a1a86ce3626bcd89274af071c4f4c5064ad607d

证据闭环：
9a34666c025474367b9176764d2ae67e03b22b49

原20套Trace归档：
b93fc0dbac79d6f9c5ca027baa2d2e1cf371455b

必须读取最新闭环包：
docs/ep_l2/operations/original174_trace_evidence_closure_20261024_v1/

重点使用：
- ARCHIVE_ACTION_QUEUE.csv
- LARGE_TRACE_CLOSURE_MATRIX.csv
- POLYBENCH_FULL_COVERAGE.csv
- RAW_RESULTS_RESTORABILITY.csv
- SOURCE_TO_TRUE164_RECOVERY_MAP.json
- PROJECT_CLOSURE_SUMMARY.csv
- CLOSURE_TOTALS_AND_NONADDITIVE_COUNTS.json
- RESOURCE_AND_ACTIVE_SCIENCE_AUDIT.json
- FINAL_STATUS_AND_RECEIPT.md

不重启此前任何已完成的Goal，不重新进行大范围盘点。

二、本次复制授权范围

授权对现有冻结行动队列中已明确列出、且通过下述所有准入门禁的对象进行COPY_ONLY归档：

A. 大型Trace候选
51个已规划资产根，约185.715GiB、24,378个去重文件身份。

其中应优先处理原174 SSD上的大Trace：
- Rodinia srad
- Rodinia lavaMD
- Rodinia hybridsort
- Parboil cutcp
- CUDA SDK scan
- DTC M5 ATAX/MVT
- 其他P0 SSD-backed对象

随后处理MD127上的CUTLASS、PolyBench及Parboil等大型Trace。

B. DTC科研原始结果
63个已完成Source全文件SHA的结果目录，
774个文件，222,915,898B。

包含原44行41个真实执行结果目录和独立SG3的22个目录。
原3个ADMISSION_HOLD不得补造raw结果。

C. 原20套Trace的补充文件
14,040个未包含在原冻结selector中的Source文件，
277,152,797B。

这些文件可能已经包含在上述185.715GiB候选计划中，必须按文件身份去重，不得重复计算或上传。

尤其注意CFD原始.trace和已处理.traceg不能假定等价。

D. 小型独立缺口
AWMA Q05固定窗口223,499B：
先寻找已有真164精确副本；确实缺失且身份、资源准入全部通过时，允许COPY_ONLY补归档。

不自动补传TLS P9，不接管旧事务。
不复制或退役C16受保护模型。
不扩展到冻结清单之外的新资产。

本次授权仅涵盖数据复制及恢复证据，不涵盖任何Source释放。

三、执行优先级

P0：高价值大型Trace归档，原174 SSD来源优先。
P1：其他可准入的大型Trace、PolyBench及MD127来源。
P2：DTC 63个原始结果目录。
P3：精确目录补充文件和Q05微小缺口。

允许先用一个已冻结、容量小的DTC结果目录验证端到端复制协议，再立即进入P0。

P0阶段不必等待所有资产的SHA准备完成才开始：
可对不同资产并行进行轻量元数据准备和复用查询，但实际大型数据传输严格使用单发送端、单接收端。

某个资产因资格或资源HOLD无法复制时，记录原因，并继续其他完全独立且安全准入的资产，不让单点问题长期阻塞整个Goal。

四、每项复制前的强制门禁

1. 重新确认真实Source端点、mount namespace、realpath及文件身份。
2. 必须是非空绝对路径，严格限制在注册的科研资产命名空间。
3. 确认没有活动writer、正在使用的未闭合输入或不允许冻结的科学任务。
4. 核对owner证据、命令清单、成员顺序、科学输入身份。
5. 优先检查现有164是否已有完全相同的可信内容。
6. 能复用既有完整SHA证据时复用；否则执行单流、低优先级的Source全文件SHA。
7. SHA前后核对Source identity，确保复制对象未发生变化。
8. 真164目标必须ABSENT或属于本任务合法可恢复的同一身份事务；禁止覆盖其他归档。
9. 同时验证目标容量、源端资源、接收端资源、当前科研活动及传输预算。
10. 任一强制门禁失败，则对该资产fail-closed，登记HOLD，不伪造PASS。

Copy Plan Ready不等于资源或身份已获准。

五、真164与资源限制

原174：
/root/share/mnt164 是本地MD127 shadow。

174-new：
/root/share/mnt164 才是真164 SSHFS入口。

真实远端：
admin-wcx@10.208.130.164:/home/shared

不得混淆。

沿用已验证协议：
- 一个Source sender
- 一个Target receiver
- 原始分块≤128MiB
- 单任务暂存≤256MiB
- 总传输速率≤30MiB/s
- Source不产生完整额外副本
- 不使用整个/workspace的NAS替换映射
- 低优先级CPU/IO
- 单资产可恢复断点与不可变提交
- COMMIT-last
- 所有已存在数据不得静默覆盖

特别处理Share低于40GiB的问题：

不得简单下调旧40GiB安全门槛。

本Goal允许在独立工作区资格认证一条zero-Share-staging路径：
Source直接流式读取，接收端将数据写入真164，不在原174的Share/MD127创建中转副本。

必须独立证明：
- Share新增payload写入为0
- 不改变旧资源门槛及既有科学流程
- 本次路径使用独立且完整的资源准入
- 原174 SSD剩余空间和外部任务预留受保护
- 真164可用空间及真实持久化能力满足要求
- raw tree、retained chunks、metadata、临时暂存和并发预留全部计入容量
- 不依赖未确认的压缩或去重节省

独立zero-Share路径资格通过后，可在本次授权范围内使用。
若需要修改原有全局资源合同、降低已冻结门槛或无法证明新路径安全，则停止受影响的复制，记录HOLD并等待用户审批。

不得因为用户授权COPY_ONLY就自动免除资源门禁。

六、传输与验证

每项资产：

1. 冻结精确manifest及Source身份。
2. 建立新归档事务，记录唯一资产ID和不可变目标。
3. 按既有分块协议COPY_ONLY。
4. 断点续传只能恢复相同Source身份和同一事务。
5. 完成后逐文件全量SHA、字节数及成员顺序验证。
6. 真164关闭并重新打开文件后校验。
7. 正确生成Source→164映射、恢复入口、目录元数据和COMMIT。
8. 通过独立验证后才标记ARCHIVED_CONTENT_VERIFIED。
9. 对容量允许的隔离小资产做真实native恢复验证。
10. 大资产即使完整内容归档，也不能因为未克隆整个Target就判为迁移失败；恢复验证状态单独保留。

归档必须保留完整科研输入和必要的恢复证据。

原始采集Trace、processed Trace、压缩包及展开目录需要分别记录，不凭名称推断等价。

不将数据归档PASS升级为科学实验PASS。

七、科研任务保护

原174的AEFAIR和其他真实活动科学任务优先级高于本次归档。

持续验证：
- 实际PID/start_ticks
- CPU和IO压力
- SSD剩余空间
- cgroup内存
- 外部任务资源预留
- 当前科研owner/controller状态

若发生资源竞争、IO压力持续超限或出现源端活动writer：
暂停受影响的数据传输，保留可恢复状态；
继续其他低资源工作或安全等待独立资源条件；
不得停止或重启科学进程。

不能按旧PID或旧controller快照误判当前活动。

不触发任何新实验，不改变AEFAIR或其他科学预算、T0、旧HOLD和accepted evidence。

八、并行与效率

允许在不冲突的不同工作区并行：
- Source身份与SHA准备
- 164重复内容查询
- 恢复入口准备
- DTC小结果manifest审核
- 已完成资产回执校验

但只允许一个大型数据传输流。

优先复用历史SHA和已有164内容，避免重复传输。

不为完成任务而全部重新哈希已确认不变的大型数据。
需要新哈希的对象按实际安全IO预算滚动执行。

对科学身份明确且已具备完整前置条件的资产，连续推进，不要求用户逐项确认。

普通脚本、路径、manifest及网络恢复问题自行修复并继续。
涉及科学合同、原资源门槛、数据删除或Source身份冲突时必须HOLD。

九、范围和禁止事项

绝对禁止：
- 删除、移动、覆盖Source数据
- 自动清理已归档的旧174数据
- 修改或重写历史科学结果
- 重新运行科学任务
- 擅自复制未获授权的模型或数据
- 使用未经证实的同名对象替代原数据
- 修改旧迁移事务或接管其锁
- 把MD127 shadow冒充真164
- 在失败后以不完整对象发布完成标记
- 向GitHub提交Trace主体、模型或敏感数据

可以在独立操作分支提交小型manifest、脚本、报告及校验回执。

十、交付与结束

使用新的独立操作分支。

最终至少提交：

- ARCHIVE_EXECUTION_LEDGER.jsonl
- FINAL_ARCHIVED_ASSETS.csv
- SOURCE_TO_TRUE164_RECOVERY_MAP.json
- FULL_SHA_AND_COMMIT_RECEIPTS.json
- NATIVE_RESTORE_VERIFICATION.json
- REMAINING_HOLD_AND_COPY_QUEUE.csv
- RESOURCE_AND_ACTIVE_SCIENCE_AUDIT.json
- FINAL_STATUS_AND_RECEIPT.md

每个资产必须独立标明：
- Source当前身份
- 原始大小
- 是否复用已有164内容
- 实际新传输字节
- 内容归档状态
- 完整SHA状态
- 恢复入口状态
- 完整native恢复状态
- 科学资格状态
- Source是否仍保留
- HOLD原因和下一步要求

最后统计：
1. 本轮新增真164归档的独立资产数与字节。
2. P0/P1大型Trace完成数量和剩余数量。
3. PolyBench各变体的归档覆盖。
4. DTC 63个结果目录的完成情况。
5. 节省的重复传输量。
6. 因资源或科学身份问题留下的HOLD。
7. 实际Source释放字节（必须为0）。
8. 真164可恢复资产的精确入口与SHA证据。

所有报告推送GitHub并进行远端逐文件回读。

Goal在已授权清单处理完毕或剩余全部为明确HOLD时正常结束。
不因HOLD存在而重复扫描、不断重试或无限运行。
完成后不自动启动下一轮迁移，也不删除任何数据。
