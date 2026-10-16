# EP-L2 review_r3｜六个原Codex窗口的统一续行

**仅执行本文件，不再重做review_r2的初始“R0已合格可直接跑”步骤。** 当前任务以Lane5科学资格撤回为准，原合同6c136e2a与WBUF16/8预算不变。Lane1/4/5已有新报告；开始前有界fetch本lane最新SHA、实际运行registry，确认无重复任务。所有历史结果保留，不覆盖、不force push，使用独立worktrees/result roots，生成新SHA/receipt。普通工程问题自行修复并继续；涉及科学协议变更才停受影响部分。

## Lane 5（第一优先）：解除磁盘hold＋独立修复资格

1. 回读本目录REVIEW.md、自己Framework b134f76d8f4cd759c0852b68edf922ecbd445ea9。科学撤回文件APPLICATION_ACCEPTANCE.json/VALIDATION_MATRIX.json及两份修复包是当前权威，旧R0/R1资格文件保持历史归档。不得让原R0六次数据再被runner/paper默认接收。补显式supersession门槛，旧run即使COMPLETE_VALID也拒作正式图。
2. 在共享registry锁下重新量测workspace free、其它活跃任务与构建所需增长；48GiB磁盘下限和64GiB可用内存下限不变。当前报告workspace free约47.313GiB、差约0.687GiB。仅对自己的**无活动、可重建的临时build/scratch**做有界空间审计，安全迁移到确实可用的另一个文件系统或重建后清理；保留原raw、trace、唯一binary、配置、CSV和他人数据。记录df前后、路径、hash及实际物理字节释放；不可恢复则保持RESOURCE_HOLD报告具体 blocker，不降阈值，不循环重试。若构建需更多空间，应保证足够编译峰值余量，而非刚过48就开大构建。
3. 向Lane1交付并协助测试clock-only已通过增量(Core1565f1f04978f12e51a29fcbf9dab9a3c61b5c4e)与尚未编译warmup candidate Core832d986b03dc3c940eb99a1ae6845dd07297f4ed的准确最小patch；优先由Lane1冻结官方新R0.1源码并生产一次新binary，你负责独立validation，避免同节点两个窗口重复全量编译。不要把未编译warmup candidate写PASS。
4. 新R0.1独立门槛至少新增两个显式production-driven gate：physical_bank_clock（nonzero memcpy offset下B16/U_WB16以及8敏感代表、每bank每物理周期grant<=1）与memcpy_payload_identity（真实force_tag_access与warm hit、sector/evict、WB和response/drain）。旧nine gates可做源差分审计＋必要重新测试；不得继承旧bank_service PASS而忽略新反例。对SASS数值不可验证维持当前scope，不要求无源数据的numerical输出。
5. 新R0.1冻结source/Framework/binary/config后发布真正新版INDEPENDENTLY_QUALIFIED gate，再滚动五开发负载B16/U_WB16（两运行上限、8CPU、32GiB reservation、48GiB disk/64GiB memory floor与其他项目保护）。旧3个pair原raw保留但新run_key必须重跑，另两个未跑继续新身份。获得首个合格pair就及时发布给Lane6；低效/退化同样保留。
6. R1.1、R2/TVD、R3/RO的独立资格和正式运行另排队，不把它们的binary与R0.1混合。协同Lane6升级图表消费者使撤回有否决权，不能只依赖旧immutable qualification证书。

## Lane 1（同一最高优先级）：唯一官方Core修复发布与版本隔离

1. 读取Lane5 b134f76d撤回材料，明确标记你此前R0独立资格声明已被后来实测supersede。R0 Core126394be.../binary0b504f55及R1 Corebe651cc.../binary2d2fb082...只读保留，不修改历史receipt/二进制、旧结果或registry。
2. 和Lane5协调workspace磁盘空间，只有安全admission允许后才构建。通过准确R0父提交应用clock+warmup最小补丁；若与R1诊断模块冲突，用单独R1.1 worktree调解，不用一个巨型merge混合历史Lane2/3。
3. 优先构建并冻结R0.1独立Core/Framework/binary身份；在真实生产分区运行非零memcpy offset bank grant<=1、直接预热读、反复预热不同sector、预热脏victim替换、后续写回/eviction/set_done与正常响应退尽；检查warmup reserve/Tag index原子一致性、不能删除未完成WB数据或把Host prefill当GPU物理bank操作。保持native Tag时间顺序不变。旧all-OFF等价只做受变更影响范围的增量校验，并由Lane5独立确认。
4. 尽快交付R0.1给Lane5正式独立资格与新五点比较；不等R1.1/TVD/RO。随后将同修复合入单独R1.1理想诊断，独立build/qualification，和Lane4形成同R1.1二进制B16/ideal配对。
5. Lane2/3给出针对R0.1的最小patch、精确冲突及回归，由你最后合入新R2/R3，不覆盖R0.1冻结binary。统一量测physical GPU bank clock的来源，RO/TVD新bank calls不可重引memcpy_offset。

## Lane 2：预适配修复基线，不空等但不抢主编译配额

1. 你已完成Core c197c14d8292e8c2aa522711f4125ed5624b5549的真实clean/dirty TVD生产接线和12组定向，保留review pack。以Lane1修复后的R0.1源码准确父提交为目标，在独立worktree做最小rebase/patch apply/check，优先静态检查clock/pin/force_tag_access与TVD victim保留冲突；在disk hold时不要抢占完整编译预算。
2. 针对host预热resident旧victim、partial-sector、TVD dirty read-forward、lower_accept/set_done、flush与bank-clock补必要定向测试，producer PASS与应用独立PASS仍分离。TVD served-sectors/bytes与匹配OFF/ON lower+DRAM delta保持分开，不能将定向2->1称应用/DRAM收益。
3. 向Lane1交可直接应用于精确修复父版本的最小patch和真实冲突清单。Lane5独立验证新集成binary并获准后才开始正式TVD对照；不打断R0.1主实验。

## Lane 3：RO生产接线适配R0.1，保留证书

1. 保留Core ac3028b00aa37c08b2210b1c9a1fe8444060c0f9和r4生产者定向结果、5个已绑定whole-commandlist oracle输入，不重新抓trace或放宽closed-world作用域。
2. 对Lane1修复后的准确R0.1最小rebase，审核RO接入Tag generation与新host预热句柄的关系、physical bank calls时钟、late detached sector Fill、shared D512 descriptor、实际lower返回与ICNT背压。保证两个开关默认OFF和四模式正确性。
3. 输出精确production适配补丁/测试/新增字段成本给Lane1/6。Lane5独立合格新版本前不开RO正式应用，不影响R0.1主实验。

## Lane 4：保留理想化成果，等待匹配的修复R1.1

1. Framework be21c95d9c846c9af0904d24c78c10c3243dc64b和Core b8b3d55b392fcff793d0aec684bddb73ba3065a9的原r2+19绑定测试保留，不重跑OLD vectorAdd 1.721259x历史诊断。
2. 在自己的分支检查Lane1 R1.1 repaired release的准确SHA/ideal注册与原r2 patch一致性，协助无冲突最小修复；disk hold时只执行无需大构建的源审计/runner检查，不强占lane5恢复工作。
3. 只有Lane5独立验证新R1.1时钟/预热＋理想开关并提供同一R1.1 binary的B16 spec，才按中央registry配额跑新身份的4工作负载I_WB/I_META/I_READ_HIT及两个I_WB_META。18格原NOT_RUN保持原状态，不用旧R1/R0/OLD静态点充填。
4. 研究headroom不是补救错误模型的替代品，不额外展开I_BANK/full矩阵直到已有机制证据需要。

## Lane 6（不用GPU或build即可先完成）：撤回不合格科学结果与fail-closed intake

1. 当前r2 Framework6a3c00cb17aaff2a2c23c5990e7ef90f294aa8df和全部PPA/13行历史图保留不可变。立即发布r3 paper修订：原r2 §5.1关于B16/U_WB16“已独立合格”的句子和§6旧sad 110593→110573性能与formal_sad/WB_PAIRS图全部标**SUSPENDED/RETRACTED_AS_SCIENTIFIC_RESULT**，不能作为当前投稿正文的正式结果。原数值可在撤回附录保留hash和原因，但主图、图表清单与平均值不得使用。
2. 修补native_pair_intake.py/result_intake.py/plot_qualified_pairs.py：仅历史R0_INDEPENDENTLY_QUALIFIED.json和run COMPLETE_VALID不足以接收；需要额外绑定Lane5最新有权威的APPLICATION_ACCEPTANCE.json及完整supersession证据（原run_key与binary/trace/config匹配、status确为CURRENT_ACCEPTED）。默认缺省、匹配失败、SUSPENDED、NOT_RUN都fail closed。不能靠用户手工禁用某张图；添加负测试保证旧sad/其它5行不能再重现为正式accepted图。
3. 科研叙述继续保留EP-L2架构、成本146/145KiB、双方共同128B copy latch、模型限制和历史旧静态理想读1.721259x（明显标为独立历史诊断）。TVD定向lower reads2->1不是应用/DRAM节省。
4. 新R0.1合格配对提交后，按准确新source/binary/资格+supersession manifest入图；新R1.1 ideal另用匹配binary。不可将旧r2 SAD图从文件系统删除或悄然覆盖，生成新revision并在STATUS指明旧图的撤回归属。

## 结束标准

每条Lane以自己的执行分支交付新revision、STATUS/RECEIPT、真正受检的source/binary/config/trace/run-key以及raw hash索引，push并回读。发布本handoff本身不在服务器开始任何任务，不推定已经清盘或恢复quota。旧质量审计PASS保留其局部范围，新的R0.1/R1.1科学资格须逐源重新签发。
