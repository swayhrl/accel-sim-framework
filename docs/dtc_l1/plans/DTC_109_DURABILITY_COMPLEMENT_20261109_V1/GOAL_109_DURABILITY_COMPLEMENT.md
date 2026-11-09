# 109-DTC-L1 Durability Complement V1｜一次有界保全任务

## 0. 任务身份与授权
执行窗口：本机API独立窗口 **109-DTC-L1**。科学唯一Main **174-DTC** 正在执行另一个已授权的有限服务/完成机制Goal（固定规划 `32cbe43f6975ff6a11cfd1210f88026771656b48`）；本任务不得读取/修改174 Main活动raw、锁、registry、进程、CONTEXT，也不得经174活动环境中转资料。
本文件是下一任务合同；**只有用户转交固定GitHub提交并明确要求执行时才授权本合同**。发布本文件本身不触发任务。授权仅包括限定范围内的109 CPU-only源文件内容身份、专属小型清单与独立真实true164路线存在时的条件性保全复制；没有合格路线则产出source SHA与目标HOLD后结束。
本轮新增native运行、GPU/NCU/nsys、SASS capture、模型、科学request、预算、GPU锁获取和HOLD释放全部为0。历史SOURCE_KEEP、英文v0.23及赵皓宇博士论文第4章原IO/OO归属不变。

## 1. 科学背景与现有证据
109生产者2026-10-16完成12诊断＋SpMV small1138_bus＋LayerNorm主输入及敏感性，共15个native条件；SpMV已生产4条kernel trace，LayerNorm主输入6条。后续SpMV cubin89 consumer NOT_ADMITTED、SM89 CPU评审 NO_GO/HOLD，LayerNorm实际cubin86且跳过CALL.REL.NOINC仍NOT_ADMITTED；该保全任务不改变准入。与SM70/V100-derived64SM Oracle CORE32独立，Oracle128格已在固定trace范围内审查接受，109不是其全体输入生产者。
首次只读接手的固定真实观察：`2e009bb7a360054dcebe47c680d64aa16d4a8b88`，目录 `docs/dtc_l1/handoffs/DTC_109_READONLY_INTAKE_20261109_V1/`。native根586文件：固定285成员历史164逐成员SHA于10月16日PASS、今天109路径和大小285/285 METADATA_MATCH；额外301文件总263,676,362B；11月4日整树true164映射仍TARGET_UNVERIFIED。285成员总174,081,218B，整树逻辑字节437,757,580B。SM89 CPU根48文件：原45成员本地归档历史PASS、当前metadata 45/45，额外3文件583,932B；CPU归档true164副本未知。
301额外文件类别：INDEX_OR_RECEIPT 5/50,965B、LAYERNORM_MATERIALIZED_INPUT 2/37,748,736B、LOCAL_ARCHIVE_OR_GIT_CLOSEOUT 2/85,573,289B、PARBOIL_GIT_METADATA_OR_OBJECT 99/61,787,618B、PARBOIL_UPSTREAM_SOURCE_OR_INPUT 182/78,467,893B、SPMV_BUILD_SOURCE_OR_OUTPUT 11/47,861B。其中原本地285成员tar.gz本身占85,512,354B，属于extra301之一，不是第286个原科学payload。CPU额外3为2个小型索引/回执7,640B＋一个本地CPU45成员tar.gz576,292B。
不能因为extra不在原归档中就认为可删除。已有285目的端历史PASS与整个586树TARGET_UNVERIFIED同时成立，不能从metadata推出现今归档内容PASS或整树可恢复。

## 2. 固定输入、目录与单写规则
主精确白名单以此次 `2e009...` 包内 `METADATA_MEMBER_MAP.json` 的 native `extra_files.native_285.files` 301项、CPU `extra_files.cpu_45.files` 3项为准；不按名称重建名单或增添未知对象。根仅：`/data/c16/dtc_native_coverage_109_v1`、`/data/c16/dtc_sm89_admission_feasibility_109_v1`。原285/45索引与SHA回执来自原producer提交 `890fb0be7e681a60419c49ca0a7aa85731d8c164`、SM89 CPU提交 `d58e75ce32845a281692f19aeb4057b4c9822a3f`。存储整树旧状态来自 `b290790401e248a19427c26c0dde51e6b55ded67`；详细固定链接见 `SOURCE_INDEX.json`。
本机独占根建议 `D:/Codex/Token-API/workspaces/109-DTC-L1/`，先确认实际存在/独占；只修改自己的 `CONTEXT.md`、新交付目录及独立GitHub文档分支，不改原109历史worktree或两个source根。不得自行访问主Main CONTEXT；用小型 `MAIN_INCREMENT_NOTE.md` 等待174-DTC自然checkpoint消费。

## 3. Gate A：一次内容身份和风险分级
1. 复用首次盘点元数据而不重扫全/data。经既有109入口确认实际观察节点、namespace与专属source根一次；不查询GPU/锁/进程、不猜网络或SSH配置。
2. 仅对冻结304个额外文件依相对路径做有界 SHA256，记录当前byte数、metadata读前/后、SHA、类别和状态。拒绝越界路径、symlink跳转、权限异常、读前后状态变化；异常按项 `UNSTABLE_SOURCE/INACCESSIBLE`，不按0或凭原尺寸代替内容。不得重hash旧285/45内部payload、重新解压或重做native数值/trace解析。
3. native额外301中包含旧本地285成员tar.gz，只核该压缩包当前SHA与原历史 `af5c6ec76179f881f689f486829c025055764bd9e564e598c0dc18560865f984` 是否一致，不再核压缩成员；CPU额外3中本地45成员tar.gz仅核当前SHA是否与历史 `95f3e6d6e3a986bdc7d9d2468374275e2e008b81cbd88d0ec026315117a6f28f` 一致。二者如不符保留冲突，不改旧receipt。
4. 仅对source身份通过者标记 `SOURCE_SHA_PINNED`；列出实际完整304的通过/错误/未核；旧historic true164验收继续单列。不要因同样的文件大小/mtime称为SHA PASS。对与其他项目共享的Git对象、source和工具只做DTC专属快照身份，不修改所有权。

## 4. Gate B：条件性的真实true164备份（若路线不合格则HOLD）
只有109已经具有**用户此前授权的独立直达true164**的现存路线（真实挂载或直接配置的存储接收端），并能证明实际真实164宿主/namespace、接收权限、可用空间、目标为专属新目录时，才可以继续。不得因历史 `109→hrl174new→mounted164` 字符串擅自跳板至174-DTC、旧174或其他服务，不能配置新凭据/代理、尝试提权或反复重连。
Gate B PASS后，只在真164经批准的用户专属新目录完成 native301 和 CPU3 **COPY+SOURCE_KEEP**；source原件、旧archive、历史source和原target均保持不动。允许在独立staging以精确白名单流式打包，禁止自包含递归、跟随根外symlink、覆盖目标已有资产。独立接收方实际重新读取target文件或archive stream，对304目标成员的size/SHA/manifest和无目录穿越逐项核验，归档只报所证明的子集。
如果路由/存储/权限/receiver核验不符合门槛，停止数据传输并返回 `SOURCE_SHA_PINNED_TARGET_ROUTE_HOLD`，不为了凑完成而尝试原174生产主机。只在安全隔离空间许可且不影响其他项目时做刚生成补集的非破坏性恢复测试；否则 `RESTORE_NOT_TESTED`。补集成功也**不能**把whole native586宣称现在RESTORE_PASS：还须证明原285包今日target身份与联合586完整恢复；本Goal不主动重验旧285成员。若唯一已知路径需要174授权，将所需最小存储接收条件写入报告，停下等待后续独立许可。
Gate B只提供数据耐久性，不解封SpMV/LayerNorm SM89/HOLD，不授权任何SASS或GPU任务。不得清理、移动、压缩原source、删git目录或改变旧SOURCE_KEEP。

## 5. 交付与停止
在独占项目 `deliveries/DTC_109_DURABILITY_COMPLEMENT_V1/` 交付：`REPORT.md`、`EXTRA301_CPU3_SHA.json`（304项真实内容身份及失败）、`ROUTE_GATE_AND_TARGET_RECEIPT.json`、`WHOLE_TREE_SCOPE.md`、`MAIN_INCREMENT_NOTE.md`、`SOURCE_INDEX.json`、`MANIFEST.json`；如有真实复制另附接收端独立SHA/stream/restore限定回执。对于有泄露风险的本地config或凭据，只公开脱敏路径、大小、SHA与状态，**不得把payload、trace、archive、源码Git对象或凭据上传GitHub**。
发布在新独立文档分支唯一新目录 `docs/dtc_l1/handoffs/DTC_109_DURABILITY_COMPLEMENT_20261109_V1/`，不修改旧 `2e009...` 包或174新机制Goal；GitHub固定提交后远端回读manifest成员、bytes、Git blob/SHA。实际更新109自己的 `CONTEXT.md`，不假定174同步；给Main短增量而非新的Main任务。
回传固定commit、实际109源SHA数量、两个历史归档今天本地包SHA结果、true164路由/目标范围与未决项、实际独占CONTEXT位置，所有新native/NCU/capture/模拟/request/预算/GPU锁计数为0。完成后 `STOP_PENDING_EXPLICIT_TASK`；若只有source PIN而无独立target，仍为合格有界完成，绝不谎称已保全到true164。
