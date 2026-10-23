# Lane T / 174-new — EP-L2 + DTC-L1 历史trace自主批量迁移 V1

状态：用户已明确授权本Goal范围内的COPY_ONLY资产迁移及连续批次操作，不必对每个trace或每个批次重复请示。此Git提交只是执行合同，不是服务器上迁移已发生的证据。

**目标**：174-new成为EP/DTC实验的长期直接执行入口；旧174原有trace逐步变成真164上带原始身份、可直接打开的只读输入；已迁移/已验证输入直接复用；本轮不启动科研模拟，不拷贝整个旧174工作区，不释放任何旧原件。Lane T一次性从现有科研证据生成有界清单、完成尽可能多的合法迁移、适配asset ensure/兼容路径、发布完整恢复与HOLD清单。

## 0. 起点、现有权威与实时变动

- 已验证native epoch2科研执行及真164输出归档：Framework 4a4931b2ac798c870df5b4661702dfec4900b331，docs/ep_l2/operations/174new_direct_native_takeover_20261023_v2/。174-new真实工作根 /root/data/ep_l2_dtc_l1_native_v2；source /root/data/ep_l2_dtc_l1_native_v2/activate.sh。旧174官方科研新启动已行政退休。
- 真164只能由174-new当前已核实SSHFS /root/share/mnt164 访问，映射164的 /home/shared；原174同名挂载是本地shadow，不得用作164。
- 已完成输入并避免重传：EP_VECTORADD_S、DTC_AD_GEMM及另行资格化的DTC legacy NN输入；旧E057/AD_GEMM结果、近期原生迁移与EP Vector r5结果也有164恢复证据，但**输出结果不是trace输入**，不能混用资产类型。
- EP-MAIN：hrl/ep-l2-main-native-174new-20261023-v1，准备Goal时Git HEAD 9993437fce9f21504b891fd25883aca631f7786a；docs/ep_l2/operations/ep_main_native_takeover_20261023_v1/INPUT_ASSET_REQUIREMENTS.json 有8个未登记的草案输入selector。CURRENT_SCIENTIFIC_STATE.md已更新2026-10-24 Vector r5诊断：75039 cycles，真实250118 RO事务，TagFAIL/relieve/detach=0，真164归档和两次native恢复完成。**绝不能使用仅接管、无新实验的旧EP快照覆盖它**。旧174 EP57/44/T0/25 accepted pair仍不变，迁移和Vector新epoch启动分别计费。
- DTC-MAIN：hrl/dtc-main-native-onboarding-20261023-v1，准备Goal时Git HEAD b2d6121e169dd0605d3e3c51cd010e7e77effd49。DTC_MAIN_NATIVE_ONBOARDING_20261023_V1/ORIGINAL44_ROW_INTAKE.json 是原44执行结果索引（41 PASS、3 Hotspot HOLD），其中raw_dir一般是结果目录，**不是输入trace路径**，必须回溯run spec/config/accepted input provenance。该分支已有E2-AEFAIR-DM活动进程的配置观测以及匹配hash矩阵消费者准备，启动本Goal时必须重新核实时运行/lease/IO余量，不假定没有活动科研。原AG8R1 2/2、1accepted/0本批剩余额度和其它历史科学证据保持不变。
- 原迁移工具、唯一receiver、真实164输出/trace迁移、分块SHA和COMMIT-last均已资格验证。复用FUTURE_ASSET_COPY_ONLY.md、164 native V2 input recovery、outbox工具；不要重做39项管理、15项合成、8423文件完整结果验证。
- 本Goal只消耗Git和旧资产只读权限，不授予新的science attempts。每组迁移前均刷新两MAIN的实际HEAD，核实际174-new科研活动、资源和真实输入身份。

## 1. 用户单次委托的实际权限

授权Lane T**独立选择、排序、分组、冻结清单、复制、恢复、校验、登记和生成路径映射**，对象限于有可靠旧owner输入证据、内容闭合且属于EP-L2或DTC-L1的历史trace输入（kernelslist.g、按序kernel-*.traceg、实际命令列表、相关目录/符号链接及input sidecar）。来源可为已接受实验、正式元数据绑定或通过当前已冻结来源核验的8项EP输入草案。每组不再向用户、E2或BA请求COPY_ONLY许可；T记录自己为USER_DELEGATED_ASSET_COPY_VERIFIER，但**不能冒充E2/BA的科研验收签名**。

同一授权包括：仅只读访问原174私有overlay的准确源文件、为精确文件做SHA/stat；经已有可信SSH通道读取/传输源字节；新真164根目录和immutable对象；174-new独立有界控制、分块staging、恢复抽检/完整复原（仅容量允许时）、路径兼容链接、既有asset目录与查询工具的数据化更新；已验证任务专属未提交临时文件的受控清理；小型工具修复、测试与Git证据发布。全部由Lane T一轮solve-and-continue完成。

不授权：删除/移动/覆写原174任何trace、raw、代码、科学结果；改变旧科学registry、T0、控制器、预算或科研接受；在旧174通过SSH运行新科学模拟；重启/追加任何付费实验或工程fixture里的完整科学应用；调低资源/安全水位；触碰C16/TLS/AWMA/其他项目资产；全盘遍历Docker overlay或整个NAS；把科学HOLD因归档成功改为PASS；常驻后台扫描/第二receiver；复制root密钥到Git。原174历史资产永久默认SOURCE_KEEP。只读COPY_ONLY任务授权不代表源文件删除授权。

## 2. 由科学证据生成去重的迁移清单，不做全盘扫描

P0 直接复用：EP_VECTORADD_S、DTC_AD_GEMM、已验证legacy NN及任何已在164且含精确全文件/有序成员SHA的trace，已有对象验证成功就只增加索引，不重传；当前DTC AEFAIR使用原GEMM资产，绝不能因本Goal重置其输入或覆盖其路径。

P1 EP-L2：原MAIN有效S/F集合对应的Conv、CFD、DWT2D、SAD、Vector（已存在）、已接受FWT恢复、独立SGEMM探索及有明确使用目的的E59/r5诊断输入；以INPUT_ASSET_REQUIREMENTS.json的8条草案为候选，不盲目认为每条都有完整验证资格。已知SGEMM单member在草案中约2.216GB，必须offset流式传输；FWT含19个kernels，不可只搬kernelslist或截断后段。Btree原有科学input/HOLD单列，不因传输改变科学地位。

P1 DTC-L1：从原44行的真实run/trace配置提取独立输入集合，跨C+/IO/OO按字节和有序成员去重；补入已接受AG/SG/FAST64及近期有明确科研使用计划的trace。不能将44个结果目录误认为44套trace；不能将独立Hotspot/Btree输入或HOLD提升为原44可接受科学数据。当前及即将运行的科学队列优先使用**已有或静态验证过的输入**，重资产读流不能干扰其活动运行。

P2 保留选择：其他已收录且输入SHA与成员均可靠的历史trace、原格式/HOLD或探索输入，若其科研场景确有后续用处则也迁移并在资产状态中注明科学HOLD；否则记录HOLD/NOT_IN_SCOPE，不为了表面完成率重复搜寻海量无关数据。

每个候选的清单必须有：原source绝对路径、原实验/项目/共用引用、科学资格和输入来源commit/path/SHA、原有完整commandlist、每个实际trace member的名称/大小/fullSHA（如旧证据缺少，针对选定文件重新流式计算）、目录及link语义、是否当前写入中、现有164对象与新的目标、目标可读树和原路径映射。记录唯一集合数量与跨项目复用。旧run raw目录绝不能代替输入root。任何缺失/变化/活跃写入/内容不符仅HOLD这组并继续其他组。

## 3. 自主有界分批传输（源原件始终KEEP）

一轮Goal内执行连续有限批次，按P0已验证复用→P1高优先级和小资产→P1大型输入→P2可用输入推进。批量按约1–8GiB逻辑字节组织；超过8GiB的单文件按offset分块断点续传，不因组织批次上限申请新许可。每次快照真实f_bavail、目标磁盘及其他科研项目当前剩余写预算，保留物理资源预留。不可用的候选写明精确HOLD，转做其他组，不无限轮询。

传输在唯一receiver及source sender资源锁之内：并发传输流=1、上限30MiB/s、raw chunk<=128MiB、task staging<=256MiB。优先零新增Share数据/control写入；本地原生/root/data的temp/control空间与原174/174-new overlay共用SSD底层，不能双重计算free。应用已有EP native V2 5GiB残余+2GiB监测等适用规则和当前DTC/其它项目reservation，host MemAvailable>=64GiB及当前cgroup/IO策略。真164检查足额空闲和目标准入；目标必须为新ABSENT路径，严禁覆写已提交对象。

建议根仅作为候选，先核确实不存在：
/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_ep_dtc_trace_inputs_v1/{EP,DTC,SHARED}/
174-new路径前缀对应 /root/share/mnt164/。

已经完成、闭合且SHA匹配的先查existing索引并直接reuse。新大文件边传边分块校验、受控部分续传、全范围闭合、关闭重开真164原始整文件SHA；一个范围失败不得使整个资产COMMIT成功。完整成员/目录/tree manifest、不可覆盖提交、COMMIT最后发布；错误数据保留HOLD证明，绝不能以重新生成trace伪造一致性。压缩或内容地址去重仅在已有机制资格和完整原始内容回读成立时使用，不凭工业Yosys JSON压缩比推断trace收益。

**活动科研优先**。尤其DTC最新E2-AEFAIR-DM已发布活动观测，需实时检查是否仍运行。若源端或174-new本地模拟器受IO/SSD/内存竞争威胁，暂停大型复制、先完成已有164对象复用/索引/无害metadata；允许有真实剩余I/O headroom的低优先级单流受限传输，不允许为抢进度影响科研运行。无独立resource许可才HOLD某批，不重启旧Goals或要求用户逐条作决策。

## 4. 真164直接可读目录、无感路径和性能边界

仅有chunk/tar归档不等于可以直接驱动SASS模拟；每个READY输入必须有**真正能从174-new open/seek/reopen的有序文件树**：原内容kernelslist.g和其所有必需trace成员、名称、相对路径/目录/link不变，immutable完整SHA/manifest和可靠恢复入口。可以沿用已验证native V2 true164 tree材料化机制；引入新包装器时先做有界合成故障/碰撞/恢复测试而不是借旧不同协议的PASS。

只在174-new自身兼容目录下创建需要的精确旧绝对trace路径到对应真164文件树的link/path-map，保留EP_VECTORADD_S和DTC_AD_GEMM既有映射不动；不允许将整个/workspace链接到NAS。旧科学二进制与科研主worktree保持原样，任何活动result/log/cache/registry/lock都在174-new native ext4，不能直接写164 SSHFS。

逐组验证：原source全SHA与真164全SHA/有序members一致；kernelslist实际字节原封不动；174-new本地真实realpath、stat、open、seek/reopen、最小header/decoder语义符合既有格式；执行asset ensure的dry-run/只读查询成功；不启动模拟器、不访问SSH科学执行。若真实随机读取速度对后续有风险，可用低干扰的有界读压测记录warm/cold条件，不清空共享page cache、不影响正在运行的科学进程；只在独立SSD余量和owner策略允许时创建有界hot cache。必须区分TRUE164_DIRECT_READ_READY与RESTORE_VERIFIED_NATIVE_TARGET（后者需要真的完整恢复到新ABSENT本地目录，容量不够就如实NOT_PERFORMED）。由于旧Source保留，完整本地恢复不是COPY_ONLY READY的必然前置，但要保留可复原脚本/原始bytes校验。

将新增asset ID写入174-new已验证的asset catalog，保持旧ID兼容；尽量数据驱动更新有限asset ensure目录，不修改原科学输入内容或运行中配置。EP-MAIN/DTC-MAIN仅收到资产发布索引，不自动修改科研分支或启动任何实验。迁移READY只证明数据可用，**不是新模拟器、正确性、性能、科学HOLD或预算资格**。

## 5. 一轮结束时的具体交付（Git小证据，不传trace到Git）

- CURRENT_ASSET_COVERAGE.csv：给每个已接受/拟运行的cohort及唯一trace集合明确denominator、P0/P1/P2、来源、大小、已在164/新增/暂缓/HOLD原因；不要宣称覆盖了整个old174所有trace。
- SOURCE_SELECTOR_MANIFESTS/：逐资产冻结完整source+ordered members+每文件SHA及目录/link语义，保留owner scientific binding和T代管COPY_ONLY身份。
- SOURCE_TO_TRUE164_PATH_MAP.json与TRUE164_TRACE_RECOVERY_INDEX.json：真164完整文件树、提交SHA、精准174-new compatibility路径、恢复工具及原路径。
- MIGRATION_BATCH_LEDGER.jsonl：分块事务、重传/复用/新复制字节数、出错恢复、完成/HOLD、资源门禁和物理测量；不能将NAS logical加到Source f_bavail。
- NATIVE_ASSET_ENSURE_VERIFICATION.json：真正从174-new只读打开新旧trace的独立证据，zero old174 simulator launches。
- EP_MAIN_ASSET_DELIVERY.md及DTC_MAIN_ASSET_DELIVERY.md：附准备时及最终owner Git HEAD、可直接使用asset IDs、需研究者单独批准的未来科学实验输入范围。
- SOURCE_KEEP_AND_RESOURCE_ACCOUNTING.json：旧source一字节不删、没有科研新启动、无预算和T0变动；logical/allocated/SSD/NAS/Share分开记账。
- REMAINING_HOLDS_AND_NEXT_ACTIONS.md：仅客观无法判定的科学来源、写入活跃、资源不足或格式问题和后续最小动作；**不得把普通工程问题当人工审批事项**。
- 原T-OPS独立分支发布全部有界文字/工具，Git远端HEAD和所有引用文件回读，保留历史旧记录和新恢复入口。所有未使用的P2和HOLD均有准确状态，不无限续行。

**闭合标准**：可证明范围内所有旧trace要么READY/ALREADY_VERIFIED，要么精确原因HOLD/NOT_IN_SCOPE；有效的已完成资产在174-new能按原路径正确定位并直接打开；不存在重新传旧bytes、错误科学资格/重复启动/自动删除；确实资源或输入身份无法通过时只HOLD特定项，推进其余合法工作后带证据结束本Goal。

本合同覆盖后续选定批次的COPY_ONLY与必要工程操作，不授权旧source释放、科学新应用、修改E2/BA科研记录。普通问题solve-and-continue，所有有资格资产在同一个Goal里持续处理，不要为每个batch建立新Goal或向用户问许可。