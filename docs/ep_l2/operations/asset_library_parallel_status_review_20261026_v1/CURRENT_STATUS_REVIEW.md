# 资产库与RTX4080补齐：当前情况与审阅入口

本材料是2026-10-26北京时间约09:40–09:48的冻结快照，不是实时仪表盘。各证据文件独立采样，不能视为跨服务器原子快照。工作树父提交为 `708d4e7029012d7f87a0b5c4b6bcc2bc0590151d`；接管基线为 `564808e166ca4bde2201dec6bc7a4d6e50c47c48`。本次提交只新增报告、代码副本和证据，不修改正在执行的代码、队列、科学账本或历史结果。

## 先读结论

- RTX4080已发布38份常规完整应用trace和38份既定CTA-stride40派生版本。新增13份派生已经全数COMMIT、回读并加入派生目录，两个有限控制进程自然退出。这些是精确输入/版本计数，不代表38个benchmark程序，更不代表全套测试集覆盖。
- 现有4080批次仍在处理CUDA Samples v11.8的transpose：GPU采集已exit0，808次kernel launch的完整记录校验通过，当前在CPU分组后处理。36项PENDING的CPU2边界切换已批准并启动等待，尚未发生切换，不能宣称当前项已双路运行。
- SM70精确归档接续已经恢复，当前仍在重读、整SHA核验原有611,552,641,085字节分块。约09:48观测到扫描位置约162.85GB；这是重复核验进度，不是新增资产量。树中仍为944/5606个整文件、317,055,807,712字节；目标COMMIT和本轮EXACT_BATCH_COMPLETE仍不存在。
- 所有新trace、分块、派生结果、运行日志及临时文件均写真164。174-new的两个既有资产控制根合计约0.82GB，本轮并行启动主要只新增一个463字节的Native STOP控制文件及极少量分配块。
- 统一SM70公共库的正式激活与全成员Native窗口验收尚未执行。已有代码资格和模板，不等于125份输入已经获得公共入口与恢复的最终验收。
- 另有161项队列行需要专项适配；它们不是已就绪36项的一部分。完整补齐所有4080缺口没有可靠结束日期。
- 资产库Goal UI仍为PAUSED。后续直接用户授权的数据工程任务已经在后台运行；没有把Goal伪称为恢复或完成。

机器可读快照见 [LIVE_STATE.json](LIVE_STATE.json)。证据索引见 [EVIDENCE_INDEX.json](EVIDENCE_INDEX.json)，所有提交成员及SHA见 [REVIEW_PACKAGE_MANIFEST.json](REVIEW_PACKAGE_MANIFEST.json)。给ChatGPT的审阅要求见 [CHATGPT_REVIEW_REQUEST.md](CHATGPT_REVIEW_REQUEST.md)。

## 1. 范围和分母

### SM70公共库冻结范围

| 维度 | 数量及含义 |
|---|---|
| 精确输入变体 | 125 |
| 无fraction路径标签 | 100；原始标签是NO_FRACTION_LABEL_NOT_FULL_CAPTURE_CERTIFIED，不能自动称为完整应用采集认证 |
| 既有fraction/trim路径 | 25；各自保持原输入与裁剪身份 |
| 去重逻辑对象 | 22,769 |
| 资产到成员引用 | 25,149 |
| 去重逻辑字节 | 972,603,859,656，约972.60GB |
| suite/program字符串键 | 56，未跨版本、别名归并，不能直接与旧53家族口径比较 |
| 分suite输入变体 | Rodinia64、PolyBench/GPU29、CUDA Samples18、Parboil14 |

依据：[FROZEN_SCOPE_PROJECTION.json](evidence/sm70/FROZEN_SCOPE_PROJECTION.json)，其原始ALL_BUNDLES SHA为 `7ebb0949d9f81cd47d1d0cc4abab0596318babd6eafb2fb3295e8b0325182cc6`。架构header、源版本、输入变体、历史科学接受和当前模拟器可用性分别记录。

### RTX4080范围

现有队列242行：38 COMMITTED_VERIFIED、1 RUNNING、36 PENDING、161 PENDING_SPECIALIST_EXTENSION、4 FAILED_RETAINED、两个不同的SUPERSEDED各1。失败及被替代记录均保留；不能相加为待采workload数量。

普通目录38份，派生目录38份；普通目录按suite标签的输入数为CUDA SDK11、CUDA Samples9、Parboil9、Rodinia8、PolyBench/GPU1。这里仍是精确输入，不是程序家族数。38个派生父ID与38个普通ID的集合关系由 [VALIDATION_REPORT.json](VALIDATION_REPORT.json) 核对。

源码目录分母包含现代CUDA Samples v11.8的205项、官方SDK4.2.9的82项、另一个研究快照的73个源码目录、Rodinia3.1的23家族、Rodinia2.0-ft的11家族、Parboil11、PolyBench15。版本重叠和实现差异必须保留，不能直接求和为唯一可采程序数量。

[源码范围投影](evidence/rtx4080/SOURCE_SCOPE_BASE_PROJECTION.json) 的逻辑身份分类和 [当前QUEUE](evidence/rtx4080/QUEUE.json)、[普通目录](evidence/rtx4080/ORDINARY_CATALOG.json)、[派生目录](evidence/rtx4080/DERIVED_CATALOG.json) 是不同口径；源码投影计数不是当前采集完成数。

## 2. 当前后台执行图

| 任务 | 精确身份 | 当前状态、结束条件 |
|---|---|---|
| SM70 V12R2监督 | PID1361521 / ticks972665970 | RUNNING_COPY_ONLY；等待精确目标COMMIT、EXACT_BATCH_COMPLETE及自然结束 |
| SM70 driver | PID1361524 / ticks972666019 | 已有分块全SHA重读阶段；随后仍有Source全SHA、树装配与整文件关闭重开SHA |
| 旧RTX有限dispatcher | PID1219372 / ticks967383986 | 当前transpose后处理及发布完成后，按自有STOP自然退出 |
| CPU2 exact36切换控制器 | PID1362061 / ticks972688413 | WAIT_CURRENT_OR_OLD_DISPATCHER；未修改当前RUNNING项 |
| 精确13派生prepare/publish | PID1361779、1361780 / ticks972675628 | 两者已退出；13项全部COMMITTED_VERIFIED |

CPU2切换必须同时满足：当前项COMMIT、接收端回读、普通catalog都闭合；旧dispatcher自然STOP并退出；原Native和109租约空闲；36项身份、job哈希和自有STOP均精确匹配。仅替换这36项的worker路径和SHA，不更改argv、输入或源码身份。新批GPU采集并发仍1，kernel后处理并发2；任一不确定清理、非COMMIT或身份漂移会保留证据并停止，不自动重启。

对应代码、Root批准和测试在 [code/cpu2_phase](code/cpu2_phase)、[evidence/cpu2_phase](evidence/cpu2_phase)。生产算法仍为冻结POST `5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d`，原发布/更新函数与远端心跳watchdog保持原协议。微型等价与负例测试已通过；阶段切换的完整状态机测试采用模拟进程，真实阶段切换尚未发生，应继续观察首个真实结果。

## 3. SM70故障、修复及当前资格

旧V3最初因共享SSD预留保护停止；空间条件变化后，其preflight发现Source的FUSE inode变化并自然退出。源归档路径、大小17,943,970,556字节、mtime、ctime、uid/gid、mode等都相同，唯一变化为inode85202680→96999419。独立完整读取源归档后，SHA仍精确等于：

`9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca`

V12R2仅对本输入清单SHA `4f2e611e7b1a2e599005fc2160122eaf0f975c66a45757b0a1f7730713d630ba` 提供显式Root批准的内存别名绑定，旧manifest和Source原件均不修改。原Source归档/member全SHA、已关闭chunk全SHA、树整文件关闭重开SHA及COMMIT链保持。

只有一个143,654,912字节的未完成派生tree文件，在旧进程完全退出、四个原SM70租约独占下，前后全SHA相等地移到同一164目标的ROOT_RETAINED_UNCOMMITTED_PARTIALS_20261026_v1。该文件未删除、未截断，保留路径与完整SHA回执在 [ROOT_PARTIAL_PRESERVED_V1.json](evidence/sm70/ROOT_PARTIAL_PRESERVED_V1.json)。

第一次V12启动的Python写边界误拒真实/dev/null，尚未启动driver就退出。失败证据保留；R2仅允许真实major1/minor3字符设备的open，新增实际gated子进程生命周期测试，普通Native写、symlink伪装和/dev/zero仍拒绝。当前运行的是R2，不能把历史启动失败误报为当前状态。

当前engine SHA：`53ca6aedea4f11f2e45fcf9bdd8f33ec5ecd5437af0e5e3ca286458c7cd01b1e`。代码和批准见 [code/sm70](code/sm70)，独立源全SHA结果见 [SOURCE_WHOLE_SHA_RESULT.json](evidence/sm70/SOURCE_WHOLE_SHA_RESULT.json)。

### 资源口径发生了显式变更，需重点审查

当前任务是精确NAS-only入口：所有payload、日志、临时文件均在164；Native仅打开四个既有租约，不另写大文件。它检查Native真实5GiB余量及64MiB自身控制上限，完整报告所有foreign注册预留，但不再为自己的零Native写入再次背负整个foreign pool ceiling。没有修改或排除任何foreign registry项目、科学预算或科学启动。

这是新的Root工程决策，不是旧V10的“所有预留相加”门槛仍然通过。Python写路径audit是固定程序路径约束，不是对恶意native代码的系统级沙箱。默认restore入口仍保留旧严格预留门；NAS复制通过不自动授予Native恢复资格。

hash/装配的每调用上限为64MiB/s，只有Native块设备健康、NAS健康且压力低才走快档，否则回落30/10/4/1。它不是跨进程聚合硬限速；实际受NAS及读写、节流开销限制。09:19 driver rchar约101.08GB，09:48约163.89GB，仅支持当前在推进，不能当作新增目标字节。

## 4. 13份派生补齐已闭合

原generator `0f2a6d35e5f2547aa284a075a02fae1b981483d9b10614f6275697368ef513a4` 和BoundIO `19a5274933da2ec0c83852ac7d87bddcff3b3fdd70d47d0d51769266fe93116e` 原字节复用。精确13个普通父对象约8.34GB逻辑文件量。

生成并发2、发布并发1，共用受计量数据读的10MiB/s节流；该数字不是整个系统所有元数据、网络和文件写入的硬速率保证。各worker/publisher AS上限1536MiB，控制器soft256MiB/hard1536MiB。R1父进程hard256MiB会妨碍子进程提高上限的问题已在启动真实scope前修复，并以UID65534实际子进程测试验证。

发布先独占新对象目录，严格比较PREPARED精确成员集合、大小和全SHA，关闭重开检查后不可覆盖安装COMMIT，最后更新独立派生catalog。失败前缀不入catalog；不持4080采集SOURCE/TARGET租约；已有对象不覆盖、失败不自动重试。

证据：[PUBLISH_TERMINAL.json](evidence/derived13/PUBLISH_TERMINAL.json)、[TERMINAL.json](evidence/derived13/TERMINAL.json)、[冻结代码与全部pins](evidence/derived13/FINAL_REVIEW_PACKAGE_R2.json)、[代码](code/derived13)。

## 5. 公共入口和“全量读取、恢复验收”尚未执行

候选公共代码版本为 `e2b1a814a201f7f5dd95c55c61a94f04069690dd18ecfabd89c9f88dc7ae19c7`，代码副本在 [code/public_suite_not_activated](code/public_suite_not_activated)。完整验收边界详见 [PUBLIC_ACCEPTANCE_BOUNDARY.md](PUBLIC_ACCEPTANCE_BOUNDARY.md)。

1. 三个项目cwd各自调用公共CLI，检查全125输入、全部成员、别名和入口解析，复用已绑定历史完整SHA证据；返回值明确NOT_FRESH_SHA。
2. 三个小型完整输入分别实际materialize并重开全SHA。
3. 独立全对象阶段对22,769个去重逻辑对象各做一轮完整Source读取→Native小窗口写入→关闭重开回读SHA。全部972.60GB逻辑字节都覆盖，活跃窗口≤64MiB、任务总Native占用≤256MiB；依精确context和持久化回执复用已完成项。
4. 最终确认125输入、25,149引用、全部commandlist顺序/SHA、442别名、20份既有资产、四个archive审计和受保护科学工具前后快照。

全量窗口恢复不是整库同时物化；目前也不能声称全量大文件在Native按原uid/gid/mtime完整重建。口头说明中的“恢复原始文件及属性”应按本文件精确收紧。

三倍计量I/O主要来自读、写、回读，不是三个cwd各刷完整库。按冻结公共profile约30MiB/s聚合计量，972.60GB×3约2.92TB的理论下限约25.8小时，另有元数据、校验、压力降速和有限窗口回执开销；26–78小时只是工作量估算。

当前V5 bootstrap仍缺Source2最终闭合后的绑定、protected-after、最终spec和Root批准；新的V12R2 EXACT_BATCH_COMPLETE和新的engine pins须显式接入后续生产闭合，不能借用旧V10 BATCH记录或把代码资格说成生产验收完成。

## 6. 科学资格与保留边界

- 仅EP-MAIN常驻；临时Lane已经结束准备。本报告不启动新模拟、GPU采集、验证、清理或旧Goal。
- 原A2/B/C/D/E2/F成果、original57/T0、main61、r4/E59、r5/E057身份保持分离。精确历史依据见本分支既有接管文件，不能把此工程提交当新的科学结果。
- EP研究配置仍保留其Volta基础身份；4080上新采SM89资产不自动意味着EP已改为4080配置。
- producer/完整记录校验PASS、归档PASS、派生字节等价、Native恢复PASS和应用/消费者模拟器资格是不同结论。当前这些4080目录不自动授予各模拟器profile语义或性能接受；硬件timing校准也没有授予。
- Source KEEP、释放0。近期使用、近期计划复用、复用情况未知的缓存继续保留；未按旧估算清掉最近资格缓存。
- 其它项目的科学请求在变化，注册表投影仅为带时间戳观察；本报告没有改写它们。

## 7. 时间预估及下一步

09:20给用户的粗估：当前transpose约1–2小时；SM70当前归档阶段约12–18小时；36项已就绪4080粗估24–72小时；公共库激活后全范围验收另需约1–3天。已就绪范围总体2–4天、约10月28–30日收尾是有条件估计，不是验收完成日期承诺。

这些不是相互独立的纯算力任务，受NAS、序列化GPU、逐应用完整闭合及可能的兼容失败影响；72小时有限批次上限也不等于72小时所有输入必然通过。161项专项适配不在此工期内。

下一步按证据推进：观察当前transpose发布→exact36真实CPU2首项；SM70形成精确COMMIT和完成回执→独立Root闭合登记、公共绑定和最终spec审查→公共入口与全范围Native窗口验收；单列161项适配路线。不能跳过失败和未覆盖输入，也不能仅为缩短估计改成抽样验收。
