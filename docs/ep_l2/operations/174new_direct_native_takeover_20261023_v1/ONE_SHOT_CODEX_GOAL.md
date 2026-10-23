# 174-new 直接原生接管 EP-L2 + DTC-L1（一次收敛 Goal）

**状态：已准备、尚未执行；本文件的提交不是服务器迁移完成证明。** 执行场所为 **174-new** 独立Codex窗口。目标是**后续科研进程直接在174-new容器运行**，不是174-new通过SSH在原174容器运行，也不是简单将SSH命令包装为本地CLI。原174保留历史资产，不进行批量归档/删除。164保存以后完成的结果。

## 0. 既有事实和优先级

- 原174与174-new是**同一物理宿主机、不同Docker容器和mount/PID namespace**；共享SSD(/dev/sdf；Docker overlay也用同一SSD)、共享/root/data；/root/share为近满水位的独立机械/RAID池；**仅174-new**的/root/share/mnt164指向真164 SSHFS。
- 原174的/workspace、DWT/Gaussian/GEMM trace、CUDA11.8及/scratch内部分运行库位于**原174私有overlay**；174-new当前无这些路径。切容器不会新增SSD容量。历史可用空间曾约7.52GiB，后续量化约10GiB，必须重新测。
- 已有174-new统一管理epoch1（**仅管理权**，科学启动禁用）：
  Framework \`361ad4f6dcf60bfe7ff8594c5c994bff5a2ef1b1\`
  原管理入口 \`/root/data/ep_l2_dtc_l1_management_20261023_v1/bin\`。39项控制测试通过，但**原科学controller consume/fork门禁尚未绑定新执行环境**。
- 现有完整结果归档和恢复均PASS：
  Framework \`c02fbf9f554b6287151ae50666889ff3aac4eebc\`
  E057/AD_GEMM总8423files/513,220,893B，真实164完整SHA＋174-new native恢复；SOURCE_KEEP、零科研新启动、零释放。不可再次搬运作为环境资格替代。
- 原EP-L2已观测57 actual starts /44 COMPLETE_VALID，T0=1792414193，原控制器STOPPED，科学最大值null**不是**无限次授权；当前owner E/E2。
- DTC-L1当前AG8R1 route-repair cohort已2/2实际fork、1 accepted、0剩余，原终态HOLD/STOP。旧初始0只是过时快照；其他AG/BA历史队列独立保留。owner BA。
- EP旧main61/Core \`d010911e3174a3764791183cd108fe4664ba8731\`/binary SHA \`61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5\`，新诊断E057/Core \`1093d2629e3d6a9130ba25b9dd119b6f3e16c092\`/binary SHA \`e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33\`，不能混用科学身份。
- DTC AG8R1例子 Framework \`8e43c75a5e2eb60a8466084602b7df8117111e89\`/Core \`c8090115bd57512b1b23fca7d925301fa620c751\`/binary SHA \`1004880fd7f01f815eb55d3e23fee451d95bb90eef7ecfb19ec8fd9531b9bd6c\`/custom libcudart SHA \`aee7c03cf30c2e9c2c9577165e019ce1dde929a668ca84882b5286415989cec2\`；其RUNPATH依赖原174 \`combined-final\`目录。检查实际选定cohort而不硬套历史头。
- 系统目标优先：**少拷资产、少耗SSD、无SSH科学执行、复用既有164 outbox、一次完成**。不得以再做一轮分析/搭建复杂多agent框架替代实质接管。

完整先读：
- \`docs/ep_l2/operations/174new_execution_takeover_feasibility_20261022_v1/{README.md,ENVIRONMENT.md,PROJECT_FEASIBILITY.md,HANDOFF_AND_QUALIFICATION.md}\` @ \`13b30fa613b55eb929785a5dfc015aae95a17a37\`
- \`docs/ep_l2/operations/unified_management_20261023_v1/{README.md,NEXT_ACTIONS.json,FUNCTION_READINESS.json,EXECUTION_FENCING_PROTOCOL.json}\` @ \`361ad4f6dcf60bfe7ff8594c5c994bff5a2ef1b1\`
- \`docs/ep_l2/operations/full_result_offload_20261023_v1/{README.md,FINITE_BATCH_WORKFLOW.md}\` @ \`c02fbf9f554b6287151ae50666889ff3aac4eebc\`

## 1. 最优先排除真正的硬阻塞：直接只读共享原174 overlay

### 1.1 先做高价值、有限的宿主权限预检（只读）

确认174-new是否有**正规宿主机管理员权限**、可否在不停止现有容器与C16/其它任务的前提下，将**原174运行容器当前完整merged挂载视图中的/workspace**以及必要的运行库/工具路径，以稳定的**只读bind mount**暴露到174-new的mount namespace。

- 只允许经宿主机管理员**明确授权并可审计**的Docker/容器挂载配置。严禁把root@container当host root、直接进入Docker \`overlay2/*/diff\`/upperdir、未授权\`nsenter\`、/proc跨namespace伪挂载、绕开原174隔离或修改宿主Docker内部数据。
- 必须验证挂载对象是**原174实际merged视图**而非上层增量目录；确认文件SHA、设备、inode、link/symlink语义、容器启动/销毁期间有效期和**重启后持久配置**。不能仅凭宿主路径存在宣称可访问。
- 174-new当前没有/workspace，可考虑受控RO导出到\`/workspace\`以维持旧绝对trace路径，但**不能**在其上写入新实验结果。也可在\`/mnt/legacy174/workspace\`暴露后显式重绑定配置；不得用字符串替换假装等价。
- 对Source的\`/scratch\`工具链、\`/usr/local/cuda-11.8\`和其他必需ELF解释器/so目录，优先只读复用精确依赖闭包，不覆盖174-new现有C16/Python/系统库。具体绝对路径需求由\`readelf\`/运行配置确认。
- **不得**仅使用 \`docker --volumes-from\` 就宣称可以共享原容器私有overlay的/workspace；也不应把SSHFS原174挂载伪装成“本地直接执行”。
- 一个初始只读canary必须由**174-new的本地进程**，无SSH，独立\`open/read/seek/reopen\`已知DWT、Gaussian、GEMM trace成员以及旧小身份文件，并与原owner记录的SHA匹配。
- 如果合法的host挂载权限或稳定性不存在：状态\`BLOCKED_NO_HOST_BIND_OR_EQUIVALENT\`，不要切科学权、不要偷改旧容器。不允许SSH转发方案充当通过。允许只就所需热输入提出“一次性拷至164 + 174-new直接读”候选，但仅标\`PARTIAL_SELECTED_INPUTS\`，绝不冒称掌握所有旧资产或全量接管。

### 1.2 宿主挂载不能破坏其他任务

不重启/重建已在使用的174-new容器，不停止原174容器；若只能通过重建容器挂载，应在本Goal内发布**精确宿主权限/重启依赖与影响范围**，保留现有epoch1并停止破坏性阶段。除非有独立当前用户授权并且所有受影响任务均可安全排空，不做该变更。

## 2. 一次性准备174-new真正可直接运行的环境（仅挂载条件PASS时）

- 用原174现有完整二进制、trace、配置和必要动态库的**只读可访问副本**尽量免编译；不碰174-new既有C16 checkout。
- 通过\`file/readelf/sha256/ldd/解释器模块导入\`建立EP-L2 main61及必要新诊断、DTC选定当前cohort各自的runtime closure。缺少CUDA11.8/自定义libcudart/Python3.11时优先采用受控、精确、只读运行时闭包；必要新安装仅在隔离任务本地目录、按资源准入，不动系统全局库或旧文件。
- 创建174-new私有可写工作树/结果/缓存目录（首选经验证的/root/data专属小目录）；写入**独立于只读旧/workspace**。源码从精确Git SHA/小patch起步，数据/trace通过受控RO挂载或内容地址路径只读引用。
- 新模拟器/控制器不得写旧/workspace或旧接受结果；文件全路径、环境变量/LD_LIBRARY_PATH/RPATH/动态加载依赖必须被审计。必要path-map以opt-in、source/config身份注明，禁止默改其他模拟器科研语义。
- 現有SSD与Docker overlay共用底层池，\`/root/data\`不是额外容量。编译缓存、临时输出、完整恢复副本均严格计入当前EP/DTC原有或新批准的空间/CPU/RAM/IO保留，不能因为挂载RO而跳过。
- 旧164是真SSHFS；新实验hot writes只能用174-new本地原生目录，并在关闭+owner接受后交给已验收164 outbox。不可直接把活动raw、锁/SQLite或运行中checkpoint写在SSHFS。

## 3. 简单且可靠的一次性科学执行权切换（不要大规模重造fence平台）

正式权限目标：174-new**本地PID/mount namespace中的唯一项目科学执行入口**；旧174容器未来不再启动新EP/DTC实验，只作为原资产只读遗留承载。此前epoch1仅管理；不要将它当科学权已切换。

- 在源端自然停止/无活动进程/无未决lease-intent的前提下，读取E2和BA真正current owner身份/ledger/每批预算和原始T0，明确旧57、旧AG8R1 2/2、所有失败、HOLD等不重置、不退款。
- 先通过精确备份与hash/old authority closure，在174-new本地建立**新的唯一、持久性科学执行ledger/锁/控制器入口**。保留Source原canonical文件冻结可追溯；设新的单调cutover epoch2（如旧Source当前状态仍epoch1且无其他owner变更），真实状态源只能有一个。不要在Source和Target保持两个独立可写的科研controller/registry。
- 原管理epoch1保留为完整证据；有必要在已有共享管理授权文件里追加最小epoch2接管回执，行政退休原174**官方**新任务入口。无需开发庞大的分布式双边fencing框架；但至少保证**同一个实验request_id在当前唯一ledger里只会消耗/启动一次**，失联只能查原生durable intent而非盲重试。
- 原174旧科研数据/源码/binary和已经完成的results全部SOURCE_KEEP，不删除、不移动、不在其上就地继续实验；保留旧控制器、注册簿原件供审计，但官方新启动入口只指向174-new。
- DTC仍有旧AG8R1 0剩余，因此禁止在旧cohort里偷偷增加名额；EP \`maximum_actual_starts=null\`亦不表示无限授权。新授权的迁移资格/正式研究实验必须逐项有自己的精确规格和预算。
- **不得**让上一轮仅为管理而签发的T委托自动代签新的科学资格；保持owner科学身份与签字边界。

## 4. 同一Goal内部完成最小原生可执行性验证（无重复耗时大矩阵）

顺序：先EP-L2、后DTC-L1，两条项目资料准备可并行。不要为模拟器环境验证重抓trace、不迁移全部旧资产、不大规模重编译。现有64-slice/源码identity全数保留。

- 静态: 真实Target PID namespace/非SSH进程树、真实ELF依赖、旧trace opened directly、source/config/input/binary hash、目录权限及本地结果写入。
- 工程: 已冻结最小fixture，验证命令行、解析、终态退出/正确性、数据和必需历史统计；不把fixture当成科学应用PASS。
- **真实跨容器科学资格**：如本Goal连同用户精确新预算授权允许，可各选**最多1个**owner确认的已经接受、短小、能与旧精确配对的完整输入/配置：EP首选旧main61 \`vectorAdd_4M S\`；DTC首选旧accepted \`AD_GEMM\`。新迁移资格cohort独立登记真实启动/失败成本，各至多一次自然启动、0自动重试，不能冲减旧57或DTC旧2/2；全部实际成本按当前owner/用户新批准资源政策处理。此行仅为**资格候选**，若未发布精确冻结spec、预算或当前owner资格，**不可**自行启动，不得宣称全部科学执行资格PASS。
- 完整资格至少保真指令数、kernel/CTA、GPU cycles（需要决定是否与旧可精确确定性相等）、64slice和相关FIFO/控制器终态、输出完整SHA/科学语义；任何trace路径重绑定和运行库变化按不同环境记录而非冒用旧科学源身份。
- 评估至少一组新环境trace读取热点的壁钟时间，明确短小资格样本无法推出整体性能无损。无需重复原本全套实验矩阵。

## 5. 用164作为后续新结果权威长期库

复用 \`c02fbf9f554b6287151ae50666889ff3aac4eebc\` 完整结果归档、\`361ad4f6dcf60bfe7ff8594c5c994bff5a2ef1b1\` epoch1统一管理outbox与V9单receiver。切换174-new native时Source就变成174-new本地，不再需要源端SSH；仍保持独立科学接受、归档SHA、真实native恢复或明示的证据等级和retention/reclaim四条状态链。

- 本地只存活跃hot数据与有界不可中断控制；结案后尽快按已批准outbox送真164，确认COMMIT/fullSHA、RESTORE与完整恢复脚本/索引；已归档历史E057/AD_GEMM不重传。
- SSD若不足以同时容纳新结果＋全量Target-native restore，不能冒称完成恢复。允许先归档并readback校验、\`RESTORE_PENDING_RESOURCE\`；要真正释放本地原始数据仍需相应project owner/用户对当前确切原件、可恢复证明和读者依赖单独授权。
- 旧174所有文件默认SOURCE_KEEP；新174-new结果可以设计未来专用、显式授权的自动滚动冷归档和局部释放，但本Goal绝不删除任何科研数据。
- 不以SSH远程运行原174 app、不用SSHFS当hot IO、不复制海量旧trace、不执行未知管理员权限/容器root绕过；这样运行后用户只需登录174-new工作。

## 6. 本Goal的许可/工作顺序和结束标准

用户把这份完整Goal明确交给Lane T，表示批准：限定目录/资源内的只读审计、经过**合法宿主管理员授权**的非破坏性RO挂载、174-new独立环境配置、小型工程fixture以及**在明确单独冻结spec/预算/资格后**的最多各一项迁移资格运行。该授权**不等于**无条件准许宿主容器重启、绕过存储门槛、任意补科学预算或批量源文件释放。

先做A（合法RO挂载）。A阻塞则不再反复做前几轮报告，不走伪直连方案，给用户一页精确“需要哪项宿主管理员动作/权限、当前可做的备选路径”并STOP。A通过时继续B→C→D→E，一轮处理所有普通工程问题，不把轻微PATH/依赖/工具问题升级成频繁人工请示。只在宿主权限、科学身份、预算、资源安全、真实执行资格或所有者边界有实质改变时报告HOLD。

在最终产物中必须**分层给出不可混淆的状态**：

- \`DIRECT_FS_ACCESS_PASS\`（174-new本地RO读原174历史资产与依赖、无SSH）
- \`EP_NATIVE_RUNTIME_PASS\` / \`DTC_NATIVE_RUNTIME_PASS\`（本地能启动旧科学二进制并完成精确工程资格）
- \`EP_SCIENCE_QUALIFIED\` / \`DTC_SCIENCE_QUALIFIED\`（若有独立授权的真实完成配对；不能由工程smoke代替）
- \`EPOCH2_SCIENCE_DISPATCH_OWNER_SWITCHED\`（只有科学真实接口、单一ledger和新旧owner协议合格才允许）
- \`NEW_RESULT_164_PATH_READY\`（当前输出hot/write与164长期数据生命周期可用）
- \`NO_LEGACY_SOURCE_DELETE\`（历史资产全保留）

最终提供：174-new本地独立\`project status/assets/experiment prepare/run/result archive/restore\`操作入口（不可执行的命令明确DISABLED）；**实际Target本地科学进程PID/namespace证明**，依赖图、冻结本机/远端身份、持久宿主挂载办法、原文件只读/结果路径、两项目资格证据、单一新权限切换收据、失败恢复与最少后续动作。小型Git审计产物远端回读；不把原始科研数据提交Git。

**关键验收：** 用户在174-new的一个窗口中、**不通过SSH进入原174**，能直接启动174-new本地的受控模拟器读取旧trace、写174-new本地临时结果、再经已验证通道归档164。任何一步未实际测试即不能宣布“完全接管”。

### 限制性默认

- 无宿主管理员挂载权限 => BLOCKED而非SSH fallback冒充通过；
- 不重启旧科学Goal，不代替owner实际科学资格，不退款、不reset、不自动再次启动旧失败任务；
- 不触碰当前其他项目的容器和mount命名空间，不在旧原始/workspace上写数据；
- 不删除、不归档/迁移完整旧trace源树；部署使用最少新SSD且严守物理共享容量；
- ordinary bug solve-and-continue；scientific / authority / host privilege / resource contract changed => HOLD。
