# EP-L2 / ISCAS2027 r13：用户明确批准两条PolyBench closeout源目录有条件分阶段释放

日期：2026-10-17（北京时间）。**已获用户明确授权。** 用户答复：“我同意。只要164上有了，能找到就问题不大。”此答复针对r12中列出的**两条明确的PolyBench `closeout.stage`目录**，并接受**不先在旧174本地完整物化66GB数据**的剩余恢复风险，以尽快为ISCAS EP-L2/DTC-L1恢复旧174真实可用空间。该授权是准确scope的一次性、条件性源释放许可，**不是**笼统清理/迁移权限、Git对象删除许可、或正式科学实验/低空间工程编译准入。

原文上下文：r12 `cc53f9085442a4c08e4cc11c4e979168c3b15369`，配合r10/r11已冻结的Storage-Ops V5–V7双端职责、164归档根、研究科学准入。**只用旧174原Storage-Ops源侧窗口执行本机文件释放；174-new目标侧只负责164证据、恢复指针与接收端确认。** 不重新开原Goal、不重启Storage-Ops任务、不操作其它Lane进程。

## 一、精确的允许释放对象（仅两条目录）

父目录：
`/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-extract`

允许目录A（优先）：
`/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-extract/polybench.correlation.closeout.stage`

允许目录B（次之、在第一阶段实测后酌需处理）：
`/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-extract/polybench.covariance.closeout.stage`

授权文件**严格取交付于源侧第三仓库** `swayhrl/gpu-l2-cache-verilog` 的 `docs/ep_l2/operations/174new_to_164_archive_v1/source_receipts/20261016_storageops_02/POLYBENCH_STAGE_HASHES.tsv`中对应两条顶层前缀的**13个精确普通文件**（11个有内容和2个0B完成标记）及 `POLYBENCH_STAGE_DIRECTORY_METADATA_V2.jsonl`中的**14个指定目录**，不删除清单以外文件、不越过顶层路径。清单SHA256 `bca6dfc2b43f4715ce0c6e55d4faa8ae11f3f4c7be7b96279e5671489004f274`；源侧数字文件元数据清单SHA256 `50c22e05d5550a5f3a8d80e45baf9b13e34beadfa01f5d6a333e914894753a80`；目录元数据清单SHA256 `d0f8ea5d069e370a045f9834cb21799d8fffa341c62285a39b00bec33ddbb3e9`。冻结目录含块空间约`66,331,324,416B`（61.77GiB），**只是预期释放上界而非实测df增量**。

### 永久不属于本次许可

不得删除或重命名原 `/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz`、默认的 `polybench.stage`、其余trace/raw、M5 GESU、R1/R1R/R2任何原始build、Git/`tmp_pack_*`、DTC-L1/EP-L2/C16当前输入/输出/进程、未知owner的文件。若任何路径存在非清单额外文件、软链、硬链接、多挂载点或活跃引用则对该目录HOLD，不递归通配删除。暂停状态的state-T进程不能kill/resume；原tgz是其可能的输入，必须原位保留。

## 二、可用的164归档与选择的简化证据层级

- **目标完整性已完成而非仅计划**：PolyBench压缩档 `17,943,970,556B`；在旧174源及174-new经164 SSHFS close/reopen读回，SHA256均为`9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca`；35/35 ranges收到DEST_VERIFIED、SOURCE_KEEP和closeout。164独立gzip/tar CRC/EOF及11个成员共`66,331,215,249B`逐项内容流式SHA256与源侧冻结stage manifest一致。额外2个空标记与13文件/14目录元数据sidecars已在164保存并读回。相关事实见174-new `20261016_storageops_06/STATUS.md`、PolyBench最终证据及164 project index；源侧 `POLYBENCH_STAGE_ARCHIVE_EQUIVALENCE.json`、`POLYBENCH_STAGE_METADATA_V2_SCOPE.json`。
- 目标压缩档应在经认证的164专属归档根之下，原始规划全路径为 `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/Decoupled-L2/old174/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/polybench.tgz`（**以目标真实close/reopen locator再确认**）。原件在旧174继续保留。
- 用户接受以“**内容逐项可还原＋空标记和数值元数据独立保存＋小范围真实还原证明**”替代本轮在旧174上完整展开全部66GB。允许通过现有冻结证据、一次全量归档URI/manifest核验和小规模non-overwrite恢复脚本测试建立release gate；**不强制重新全量读取66GB源stage SHA或在旧174物化66GB副本**。若已冻结source inode/size/mtime/ctime发生变化，才对受影响文件精确重新哈希与对比。目标端不得把SSHFS投影UID/GID/mode当作原生元数据；ctime记录以便追踪但不虚构能够原值恢复。
- **目标侧先在164授权根发布人可查找的 `POLYBENCH_RECOVERY_POINTER_R13.md` 与机器可读路径映射**：包括精确归档真实路径、整体SHA256、原两条stage路径、13个文件与两0B标记、原UID/GID/mode/mtime、目录权限/布局、如何从164的tar选择性恢复到旧174 **新的不存在路径**（不直接覆盖活跃路径）、如何按13文件SHA256验证，源/目标证据Git commit和后续原目录状态。该文件应同时提交目标侧执行分支并保存到164归档根，目标窗口自己close/reopen验证其所在路径和SHA并在桥接给旧174发只读证明。
- 若164归档/标记/sidecars目前不存在、不完整、不可定位、hash不一致、恢复脚本不能完成小文件和2个空标记的独立路径/权限恢复校验，则**HOLD全部源释放**，不能仅以之前口头报告断言已经备份。

## 三、一次快速源端核验与逐组释放

旧174源Ops先独立消费用户明确授权及目标 `RECOVERY_POINTER`，从**真实旧174 source mount namespace**完成不阻断项目的有界preflight：清单路径全覆盖/无其它对象、逐文件lstat(真实path、dev/inode/nlink/size/mtime/ctime/mode/UID/GID)、目录身份/符号链接/挂载隔离；与源冻结清单一致；已冻结全量SHA证据有效；当前/proc PID/cwd/fd/命令行、项目脚本和运行registry没有**现在正在实际读取或确定马上重用**这两条准确closeout目录。对source文件元数据变化或新写者，只暂停受影响目录，不触碰它。未来人工按原路径访问的风险已经由用户接受，须写入恢复说明而非无限期要求证明“未来永无读者”。

完成唯一一份准确preflight/manifest授权receipt并GitHub回读后，按顺序处理：

1. **第一阶段仅目录A correlation**：用manifest驱动单文件精确检查并unlink（关闭文件和目录、no-follow、无通配rm、无`rm -rf`、不追踪软链接），最后仅清掉manifest列出的空目录。删除前后`df -B1 -P /workspace`以及实际f_bavail，记录每项size/allocated、inode/hash证据与`df`净差，检查是否存在仍占用删除文件FD、overlay白化/硬链接导致实际回收偏低。用户明确批准了本目录，即使不做完整66GB旧174恢复也可在满足上述轻量可靠验证后执行；**不必再次请求用户一般性同意**。
2. 立刻向Lane1/5通知**真实**空间变化并要求他们在自己容器/registry/lease下独立复测，尤其Lane1正式build当前应有原48GiB floor+2GiB增长余量，DTC-L1/C16仍有写入；**不得将release前估计量当作准入证明**。若第一阶段后50GiB真实准入已稳定、有合法任务准备编译，先避免不必要的第2阶段磁盘高I/O；优先让正式R0.1推进。
3. **第二阶段目录B covariance已在用户本次授权内**，只有在第1阶段实测后正式构建仍未安全解锁、空间马上被其它活跃写入吞掉、或需要更充足的持续空间余量时才继续；执行前再次检查目标归档仍可定位和新鲜源/消费者状态，按相同清单逐文件释放，不把第1阶段PASS继承为第2阶段实时PASS。若已足够且正式编译正在使用，先HOLD第2阶段以保护共享IO。
4. 若任何目录在执行中出现身份不匹配、活跃依赖或不正常回收，**停止受影响目录**、保留尚未处理文件、记录精确异常和补救建议，不能顺手删其余科学数据凑数。即使overlay或外部写入使增量不明显，也不能调低正式实验门槛。

**最短交付**：目标侧 `RECOVERY_POINTER`+独立164定位/恢复证明；源侧 `POLYBENCH_R13_PRE_RELEASE_PASS/HOLD`、`A_RELEASED/HOLD`、可选`B_RELEASED/HOLD`与分目录真实df delta；两个原窗口各自只stage本仓自己负责的文件，commit/push/fetch/readback。不要为这件事设计新长期平台或反复全量归档；若存在已阻塞的其他临时reverse试验，先安全closeout/释放唯一bridge并保持原R1 source，不得重传/删除非本次两路径资产。

## 四、保持原科学合同与编译解锁

- Lane1原单例GateWaiter真实PID与锁必须独立验证，以新实际空间决定正式入口；Lane5拥有独立resource/11-gate/current scientific acceptance否决权。没有新合法编译不要声称已经可以开跑；不得切换模型/branch/config/trace/oracle、借机扩大TVD/RO/Ideal资源或自动解除旧R0/R1撤回。
- 两Ops本次优先目标是实际旧174空间回收，当前已完整的R1/R1R/R2/PB copy不再用第二传输流/反复复制；其它长周期归档/额外PPA可以留待源盘恢复之后。
- 不要将r13授权理解为“用户允许释放所有164上能找到的文件”。**只限这两条顶层目录的13个manifest文件及14个空目录；禁止源外任意删除。**

**用户授权已明确，不再卡在等待同一许可；如所有必要安全检查均通过，按双端职责执行并回报真实结果。**
