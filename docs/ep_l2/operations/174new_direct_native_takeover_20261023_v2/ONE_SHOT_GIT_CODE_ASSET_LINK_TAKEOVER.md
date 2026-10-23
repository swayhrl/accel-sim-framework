# EP-L2 + DTC-L1: 174-new不依赖宿主bind mount的直接原生接管（V2一次收敛Goal）

**本V2明确取代旧V1的“没有宿主bind mount即STOP”前置门槛。**
用户最终目标：今后只登录174-new，在174-new的本地PID/namespace运行EP-L2与DTC-L1；科研源码和实际运行入口在174-new；历史大体量trace/旧结果不全量复制到本地SSD，确切需要的资产通过真164按需提供；结果结案后长期归档真164；原174私有overlay仅作为待迁移的旧资产来源。**不可用SSH远程在原174启动模拟器冒充完成。**

这是独立迁移工作，不重复既有T的39项控制、15项合成、8423文件完整恢复、环境普查、现有管理epoch1。允许一轮内solve-and-continue；权限/科学身份/预算/资源真实阻塞要HOLD，不能伪造PASS。

## 已接受且不得改写的背景

- 原174与174-new同物理主机、不同mount/PID namespace；两overlay和共享/root/data均消耗同一SSD池，旧快照可用约7.5–10GiB，**不是两块SSD**。164在174-new的`/root/share/mnt164`，对应真正164 `/home/shared`，容量很大，但SSHFS高频trace性能尚未验证。
- 原174私有`/workspace`和`/scratch`的旧输入、CUDA11.8、部分Python3.11/ELF依赖在174-new并不存在；**软链接本身不能让不存在的旧文件变得可访问**。
- T epoch1统一管理正式PASS `361ad4f6dcf60bfe7ff8594c5c994bff5a2ef1b1`，新科学启动尚未启用。两个完整结果在164持久化并于174-new恢复验证PASS `c02fbf9f554b6287151ae50666889ff3aac4eebc`，不重新上传。历史科研状态最近确认EP57次/44接受、DTC当前AG8R1批2/2、1接受/0额度；在本Goal开始时必须读取真正owner最新权威再核一次。
- EP旧main61 Core `d010911e3174a3764791183cd108fe4664ba8731`、Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`；诊断E057 Core `1093d2629e3d6a9130ba25b9dd119b6f3e16c092`。DTC AG8R1 Core `c8090115bd57512b1b23fca7d925301fa620c751`、Framework `8e43c75a5e2eb60a8466084602b7df8117111e89`。这三个Core Git commit已从`swayhrl/gpgpu-sim`远端证实存在；不是允许混用不同科研lineage的授权。
- 旧main61 EP binary SHA256 `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`；E057 binary SHA256 `e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33`；DTC AG8R1 binary SHA256 `1004880fd7f01f815eb55d3e23fee451d95bb90eef7ecfb19ec8fd9531b9bd6c`及custom libcudart SHA `aee7c03cf30c2e9c2c9577165e019ce1dde929a668ca84882b5286415989cec2`。可按精确身份一次性只读拷贝可执行程序与所需库；不改写二进制伪装为原SHA。
- 无任何旧历史文件删除许可。原174原实验controller/ledger和科学结果不可reset、退款、旧失败重试。旧A–F、DTC其它正在执行活动及C16/TLS不得被打断。

基线先读：
1. `docs/ep_l2/operations/174new_execution_takeover_feasibility_20261022_v1/{README.md,PROJECT_FEASIBILITY.md,ENVIRONMENT.md,HANDOFF_AND_QUALIFICATION.md}`，commit `13b30fa613b55eb929785a5dfc015aae95a17a37`
2. `docs/ep_l2/operations/unified_management_20261023_v1/{README.md,FUNCTION_READINESS.json,NEXT_ACTIONS.json,EXECUTION_FENCING_PROTOCOL.json}`，commit `361ad4f6dcf60bfe7ff8594c5c994bff5a2ef1b1`
3. `docs/ep_l2/operations/full_result_offload_20261023_v1/{README.md,FINITE_BATCH_WORKFLOW.md}`，commit `c02fbf9f554b6287151ae50666889ff3aac4eebc`

## A. 代码、脚本与运行库在174-new本地落地（优先完成，不等待宿主挂载）

1. 创建**独立、定额**的174-new原生`/root/data/ep_l2_dtc_l1_native_v2/`，内部分EP/DTC `src,env,bin,run,hot-cache,control`。先核SSD共池真实当前可用、全部其他项目写入/监测预留、inode/RAM，禁止为了凑路径在原容器overlay大范围写入。容量不足只HOLD超预算部分；Git源码可选部分克隆/sparse checkout、只取必要子模块和工具。
2. **核心代码以Git为权威**：根据每个当前owner选定的精确Framework/Core/vendor提交，在174-new`git clone/fetch/worktree`到专属目录，保留原commit、dirty补丁、submodules、生成脚本与环境lock；**禁止**把C16现有`/root/workspace/accel-sim-framework`硬切分支/覆盖。将已收录Git的源码、Python脚本/启动配置直接获取，不需要复制原174整个项目树。
3. 对未入Git的**真正运行必需**的脚本、配置、编译二进制和库，旧174只读枚举成精确小清单，使用已有可信通道**只做一次性文件传输**到174-new（不是SSH启动科学进程）；两端closed-file SHA、mode和软链接审计。不要包括raw、GB级trace、活动结果、旧构建缓存或整个旧`/workspace`。
4. 优先尝试完整保留原二进制字节与ELF依赖闭包：`readelf -l/-d`、解释器、RUNPATH、`libcudart.so`、`libzstd`、libstdc++、必要Python脚本/解释器、vendor版本。仅在隔离运行包装脚本中设置依赖库路径或保留合法兼容路径；不修改旧binary的RPATH破坏SHA，也不全局替换174-new系统库。CUDA11.8若仅构建阶段需要，可以先避开新安装，优先验证CPU SASS trace replay。
5. 对两项目分别产出本地`env.sh`、`run.sh`、源Git和二进制/库/脚本SHA清单；不改变原科研机制默认开关。静态/工程环境PASS是独立于正式科学资格的状态。

## B. 大型历史trace和其它资产：164按需导入 + 兼容路径（不是“只改链接”）

1. 先做**轻量资产目录**：沿用epoch1 index、原trace`kernelslist.g`、完整有序member manifest及其原有组合身份；确认项目owner已认可其内容。已在可读共享存储/164且SHA匹配者**只建立引用，不重传**。
2. 对没有共享后端的原174私有overlay资产，优先选定EP一个最小正式trace目录（建议vectorAdd_4M S）和DTC一个已接受的最小正式trace目录（建议AD_GEMM），且只对**实际需用的成员集合**做一次受控原174→174-new→真164 COPY_ONLY。旧174原件SOURCE_KEEP、不更改。旧174传输期间允许从它**只读提取原始字节**；严格禁止SSH启动原174模拟器。
3. 复用已验证的单receiver/分块SHA/COMMIT-last/断点续传、无覆盖、源端原始member全SHA/有序目录及links；`/root/share`现已接近/低于旧40GiB水位，尽量ZERO新增Share写入。164新目标须真实fuse.sshfs、独占ABSENT路径、范围预算/资源准入。非普通结果的trace输入须有**独立输入身份/目录/缓存协议**，不借已验收outbox结果类型冒用trace资格。
4. 174-new本地创建新`/workspace`兼容视图，**只在174-new namespace**和新可写目录建立精确path-map/symlink：
   - Git代码路径→174-new本地`src`；
   - 原路径中的只读trace目录→真164新冻结trace树（或者按需预取到174-new本机有界hot-cache）；
   - runtime/依赖→174-new隔离`env/bin`；
   - 任何**可写**`results,tmp,cache,log,registry,locks`必须显式指向174-new的私有本地目录；绝不可误写只读trace源或164 SSHFS。
   不能整个`/workspace`符号链接至164，更不能在旧原174路径上挂可写目录。每个旧绝对路径的`realpath`、打开权限和实际读写落点都需机器可检查。
5. `kernelslist.g`引用与member相对路径、软链接拓扑、源manifest/composite trace hash与文件sha各按其原定义校验；不把一个kernelslist小文件hash当全trace身份。入库后先试`174-new本地open/seek/reopen`，并证明仿真I/O时没有旧174 SSH连接。
6. **性能策略**：不默认把SSD可用空间耗尽来缓存trace。输入集合小且资源预算足够时按需预取到原生SSD；若164直接read延迟太大，尝试经独立权限授权、RAM/cgroup水位批准的有界tmpfs/cache；常用大文件可优先导入true164并评价FUSE热点。不得擅自借用已有TLS tmpfs，不假设新挂载权限或达到原174读取速度。
7. 未导入/未具稳定只读后端的冷资产可留原174，标`REMOTE_SOURCE_KEEP_NOT_DIRECTLY_AVAILABLE`；**不能**用空symlink冒充全量资产无感可用。支持174-new上的显式`asset ensure NAME`按需迁移已经owner批准的资产，再映射；不得无权限全盘扫描/拷贝。

## C. 真正的174-new本地执行验证（科学进程绝不SSH落在旧174）

1. 为每项目生成一个唯一的`run native`入口，进程从174-new本地`fork/exec`，PID/mnt namespace证据、二进制字节、环境变量、trace realpath、完整退出/指令/CTA/64slice/strict、写入的本地真实目录均保存。启动时`strace`或受控open清单检查实际读取来自允许的174-new本地/真164输入视图，**没有到原174的远程执行或隐式SSHFS读旧raw**。
2. 先最小无论文资格工程fixture验证动态库/脚本/本地热写/解析。再只对owner批准的独立迁移资格cohort使用EP vectorAdd S和DTC AD_GEMM等**精确已接受原输入/config**（不要求重抓trace）。任何完成程序的实际仿真都是一次新启动，必须单独真实计费，不能暗记免费fixture。
3. 本Goal只允许在owner确切spec、可用资源、科研预算和用户精确科学启动许可同时满足时最多各1次全应用资格点，分别建立`EP_NATIVE_MIGRATION_Q1`和`DTC_NATIVE_MIGRATION_Q1`的**独立尝试号与预算**；0自动重试，不退款；旧EP57和旧DTC AG8R1 2/2、旧失败HOLD不变。若没有完整授权/预算，环境工程PASS但`SCIENCE_QUALIFICATION_PENDING_APPROVAL`，不得自行发起运行。
4. 新环境资格需比较：真实输入member SHA/ordered kernelslist、binary/dependency SHA、实际指令/CTA/kernel/epoch、模拟cycles和关键统计、终态/queue/drain/ownership，差异均明示，不用旧程序恰好exit0代替科学正确。短样本不能宣称全部trace场景性能无损；记录实际wall time和SSD/NAS读压力。

## D. 简化且可靠地切换科学权，再把新结果落164

1. 旧epoch1管理入口保留。确认旧E/E2、BA没有活动科学dispatch/未决旧intents；在原owner确认旧活动安全闭合后，冻结旧source原科研ledger快照（不可回写、退款或重置），在174-new本地只建立一个新的当前科研执行入口/ledger/锁（可以是现有管理CLI演进，不要另造一套复杂平台）。
2. 以精确用户/owner授权、request-id唯一消费、owner accepted source/config/trace身份、容量预算、进程本地PID为最小强制门禁。正式科学owner、用户和新接管epoch单次核验后，旧原174官方新dispatch路径行政退休；运行中旧进程自然完成。旧ledger继续作为历史权威，迁移开始后的新ledger绑定其不可变preimage与新单调科学epoch，不能同时存在两个可写科研入口。
3. **只有EP与DTC分别实际通过科学迁移资格、资源和权威切换门禁才标`NATIVE_SCIENCE_ACTIVE`；未通过的项目仍是174-new本地`ENGINEERING_READY`而科研启动禁用，不用SSH替代启动。**
4. 新结果先本地hot写入，结束且科学owner验收后复用现有164 outbox精确`COPY_READY → ARCHIVE_VERIFIED → RESTORE_VERIFIED`，旧结果E057/AD_GEMM及9个sidecars不重传。可以降低本地持久空间保留，但**原文件释放**必须独立明确授权；本Goal所有旧新原件默认SOURCE_KEEP。
5. 成功路径保留一键CLI（示例语义，不可用则标明）：
   `project status`、`project assets`、`asset ensure INPUT_ID`、`experiment prepare SPEC`、`experiment run-native SPEC`、`result archive ID`、`result restore ID`。
   无法实际本地执行的命令必须FAIL-CLOSED、不能包装成SSH启动旧模拟器。

## E. 许可、成本和Stop条件

**本Goal默认授权**：174-new独立代码checkout/小脚本和准确ELF库的有界只读复制、合法小工程配置/非科研fixture、对一项EP与一项DTC指定历史trace按需COPY_ONLY到真164（实际输入传输须先owner完整范围与资源准入），部署受控symlink/path-view、迁移相关纯工程修复，以及工具和Git审计文件。这些不允许改动原实验科学接受结果或旧原件。

**不自动授权**：任意未知/大规模输入迁移、超过当前底层SSD/RAM/164资源保留、全量历史资产复制、变更现有科学机制/源码语义、宿主机权限提升/挂载、任何旧source原件删除、旧科研attempt重启；新的各1次真实应用迁移资格运行仍需符合C.3的精确科学授权/预算。若现有空间确实不足，给出最小缺口，不允许用旧TLS特例；必要的旧归档数据释放另行报批。

普通Git/path/ELF/runner/兼容链接/脚本问题solve-and-continue；科学身份、资源、权限、预算、input content或控制权发生实质变化则HOLD对应子项。不要再无限重做旧审计；同一Goal在可推进步骤中并行EP/DTC两个静态准备，真正大型数据流仍单receiver。

## 最终交付与PASS定义

分层发布**证据**，不能一行PASS覆盖：
- `EP_NATIVE_CODE_AND_RUNTIME_READY`、`DTC_NATIVE_CODE_AND_RUNTIME_READY`；
- `EP_APPROVED_TRACE_AVAILABLE_164`、`DTC_APPROVED_TRACE_AVAILABLE_164`及按需缓存/兼容路径map（可标单输入/部分可用）；
- `EP_TARGET_NATIVE_PROCESS_PROOF`、`DTC_TARGET_NATIVE_PROCESS_PROOF`（真实174-new PID、无旧174 SSH科研进程）；
- `EP_SCIENCE_QUALIFIED`、`DTC_SCIENCE_QUALIFIED`（分别需独立真实计费完整应用，不由fixture冒充）；
- `SCIENCE_DISPATCH_EPOCH_SWITCHED`（单调且单一新科学ledger，旧历史原样冻结）；
- `NEW_RESULT_164_OFFLOAD_READY`，原历史资产始终`SOURCE_KEEP`。

GitHub独立分支、小型工具与恢复方法、源/输入/脚本/库精确身份、174-new直接调用命令、资源峰值/耗时以及确切未解决阻塞均远端回读。若任何项目需要下一授权，只提交**一个具体、最小、可一次批准的请求**，而不是发散出多条长期研究线。

**成功最终验收：** 用户只在174-new打开一个窗口，新EP/DTC实验由174-new本地模拟器进程运行，旧输入透过已迁到164的只读兼容视图访问，结案后结果真164归档；原174只承担暂未导入的旧资产冷库角色，不执行新实验。