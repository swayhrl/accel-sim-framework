# EP-L2 / ISCAS2027 review_r12 | 先恢复空间、后补长期归档：快速回收审批方案

2026-10-17（北京时间，按最新GitHub HEAD回读得出，不能当作服务器实时状态）。**本文件是待用户明确批准的方案，不是删除授权、Goal重启或新的编译准入。** 两个Storage-Ops原窗口有各自的唯一源/目标权限；旧174是源侧，174-new只代表164 SSHFS读取与验证，不直接决定删除。当前Lane1正式48GiB+2GiB/64GiB/中央lease+Lane5科学资格不变。

## 0. 新的事实：先前“还在传PolyBench”已过期

- **PolyBench 35/35**已在164单流完成，整体压缩归档大小 **17,943,970,556B**，源/目标SHA256 `9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca`一致；164端完整gzip/tar CRC/EOF及**11个非空stage成员逐文件66,331,215,249B内容哈希匹配**，两个0字节标记和13文件/14目录的原生owner/mode/mtime侧清单均在164经过独立读取验证。**尚未**在旧174重新物化66GB原生stage，也未证明全部ACL/xattrs或未来消费者不再使用；原tgz与两stage一律SOURCE_KEEP。
- **R1/R1R/R2**均已完成164目标端全部文件归档与独立内容恢复，合计历史build分配上界11,839,741,952B；源原件保留、回收0。R1准确197项`.vvp`的有序TSV SHA256 `af1bf73951ab44258591afd625043c855e3a76bca67fb378abe8b226ee271c84`，allocated上界4,464,783,360B；现有B001 13-file/470,083,881B反向恢复bridge批次卡在旧174安全gate，不是源释放。它占的是bridge/Share，不是根源空间。
- 源端新增M5 GESU 两个不活动/tmp unpack-check目录，精确路径`/tmp/m5-gesu-unpack-check.FGnex7`及`/tmp/m5-gesu-unpack-check.F9XDGy`，各993,886,208B allocated，内容全和保留的canonical目录一致，另有`gesu.tar.zst` 59,339,020B；目标164对本专门archive的验证尚未建立，科学源release未授权。
- 最新目标记录旧174 `f_bavail≈21.32×10^9 B`（约19.9GiB）。原正式Lane1建造门槛50GiB约53.687×10^9B，因此差约32.37×10^9B。外部并发写入持续，不能将目录allocated上界相加后直接声称已解锁。

## 1. 最有效的释放对象：仅两条准确PolyBench closeout目录

源根目录：
`/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-extract/`

候选绝对路径：
1. `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-extract/polybench.correlation.closeout.stage`（当前冻结manifest内文件逻辑和33,273,281,470B，约30.99GiB，实际allocated需按该目录源端实测）。
2. `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-extract/polybench.covariance.closeout.stage`（逻辑和33,057,933,779B，约30.79GiB，实际allocated需按该目录源端实测）。

总体13文件/14目录分配空间冻结 **66,331,324,416B≈61.77GiB**，清单SHA256 `bca6dfc2b43f4715ce0c6e55d4faa8ae11f3f4c7be7b96279e5671489004f274`；原始metadata侧清单 `POLYBENCH_STAGE_FILE_METADATA_V2.jsonl` SHA256 `50c22e05d5550a5f3a8d80e45baf9b13e34beadfa01f5d6a333e914894753a80`，目录清单SHA256 `d0f8ea5d069e370a045f9834cb21799d8fffa341c62285a39b00bec33ddbb3e9`。原`polybench.tgz`仍保留在旧174且164；**不授权删tgz**、实际默认`polybench.stage`、任何其它trace、成果与Git资产。

**可供用户考虑的快速释放标准，与旧V7“先全量在旧174原路径物化66GB”不同：** 将已有的tar-to-stage逐文件内容对照、164 gzip/tar全成员stream验证、metadata/零字节标记校验视为充分的内容可恢复性基础，仅再做一个有界、无覆盖、小文件+原UID/GID/mode/mtime/目录/0B marker恢复脚本演练，并检查能否在原路径建立独立`absent` staging再按需restore；不强制当下写回旧174全部66GB。这个放宽的前提是**用户对这个准确范围和恢复证据等级单独明确批准**，并接受完整原生物化/ACL/xattrs未全面验证、未来手工指定stage可能需要重建的剩余风险。ctime无法原值恢复，应存档而不承诺复原。
- 用户如果批准，源侧必须在删除前**新鲜**检验：源码/manifest/文件path/hash/size/dev/inode/nlink/owner/permission/st_dev/实际allocated与已冻结一致，符号链接/mount/硬链接异常则HOLD；读者包含活动/stopped进程的cwd/cmdline/FD、DTC-L1/Decoupled-L2项目owner和未来计划脚本registry，任何受影响的未来引用必须排除或有可执行恢复处理方案，否则仍SOURCE_KEEP。
- 旧174源侧**唯一释放者**先对correlation一组冻结文件逐项安全释放（不通配递归删除、不触碰其它目录），立即测量`df -B1 -P /workspace`前后和open-deleted FD；若已经合法达到正式50GiB+增长且Lane1正在准备构建，则通知Lane5独立复测，按原构建独占/资源门槛优先让路。若未获得足够稳定余量，按同一精准批准与最新源审计释放covariance组；任何unlinked但lower-overlay/仍FD打开而无df提升，停止并报告，绝不把逻辑GB当实际回收。
- 不将“完整164归档副本存在”当作未来一定能直接跑原stage路径；须记录准确从`polybench.tgz`恢复13成员(含2独立零标记)到两原路径的无覆盖recipe、数字权限/mtime回填、全量SHA检验方法和内存/临时盘需求。可以在空间恢复后完成额外大规模演练和长期归档索引，但**不要把未完成的审计冒称已完成**。
- 未收到用户对上面两个绝对路径的**确切批准**，两个源Ops窗口继续当前r10 copy-only/安全准备，无任何此范围删除。

## 2. 更小备选与避免无效工作

- **R1 197 .vvp**：即使164内容已完整恢复，原release scope仍需用户另批准；有已知精确TSV；任何单一反向演练仅用于验证恢复方式，不能反复占用唯一bridge、写入源root大副本。若合理地解除卡住的13-file B001批次，必须源旧174与目标164通过既有GitHub-pinnedSOURCE_ACK正式关闭/取消，不删除stage以外内容；已经完成的B001哈希不能重传。
- **M5 GESU**：两份/tmp与canonical完整同SHA，各约0.93GiB；需要小`gesu.tar.zst`备份若已经有164备份则只检验，不重复复制。它是DTC/M5源科学副本，不得在用户的泛化“腾空间”话语下自动删除；只有以后对两绝对路径另签准确释放批准后才释放。
- **资源效率**：当前唯一bridge一次一批，优先终止无收益的重恢复复制；对已完整归档对象不反复做35chunk上传、原始66GB文件全量重hash或第二套回执平台。SHA凭现有完整证据与一次release前抽样+关键文件稳定性校验；如果实际source身份变化，必须增量证明准确影响，不允许略过目标保护。保持正常V5/V7单流和40GiB Share底线。
- 用户希望后续工作后台推进，指的是两个已存在的Codex/Ops窗口在现有任务边界做不争用的文档/冷归档索引；本合同不创建自动化、不会在模型后台自行操作旧174或164。任何永久daemon、额外资源writer、Git/prune、科学原件释放均另审。

## 3. 成功的指标

**实测**`df /workspace`连续净增长、Lane5独立准入以及首个R0.1生产编译优于归档量和receipt数量。保持官方50GiB/内存/CPU/lease、科学V2撤回和旧结果冻结；工程pilot没有有效Lane5安全token就不得CMake。正常调度不得为了归档成果让Lane1/5忙轮询重试。

**执行状态**：当前方案本身`PROPOSED_ONLY_AWAIT_EXACT_USER_RELEASE_APPROVAL`。若用户批准，需要旧174与174-new各自在自己原窗口消化对同一准确manifest的精确条件；所有源释放后必须有原始per-file receipt与真实df回收记录及远端readback。
