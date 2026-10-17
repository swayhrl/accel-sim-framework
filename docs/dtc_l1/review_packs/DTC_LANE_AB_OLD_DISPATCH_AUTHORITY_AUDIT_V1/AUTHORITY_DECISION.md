# 旧 FAST64/Core41 自动派发器审查裁决

**SAFE_TO_RETIRE_DISPATCHER_CANDIDATE**。这是“可以提交用户审批的单个派发器退役候选”，**不是锁已释放，不是可以忽略该authority，也不是本Goal已停用它**。本次只读审查；信号（含signal 0）、加/解锁、删锁、脚本修改、模拟器执行或接管次数均为0。

原174主机 `huangrulin-174`、root账户/原容器。目标仅限 PID **1425986**、start_ticks **584741606**。实例、脚本、等待条件、已有工作与冻结2D边界已分别核对。实际观察收据见 `OBSERVATION_INITIAL.json` 与 `OBSERVATION_FINAL.json`，最终进程分类以前者的更正说明和后者为准。

## 为什么是退役候选

1. PID/start_ticks与AA2固定发布证据一致，当前cmdline仍为旧 `auto_dispatch_fast64_4_2d_core41_v1.sh --watch --poll-seconds 120`。fd9与原路径的device/inode匹配；`fdinfo/9`明确 **FLOCK ADVISORY WRITE**。不是PID复用、锁文件残留或仅用 `/proc/locks` 阴性推断。全局 `/proc/locks` 本轮也未列出它，不能据此说已释放。
2. 当前脚本磁盘、进程打开的fd255、冻结Framework `18a68dcc…` Git blob三者内容一致，SHA256均为：

   `6521332b1bf6814cc165a5dce1150d82eee50813ec363e4d271224d8f123728b`

   这是本轮所读脚本字节身份，不伪称已恢复任意历史launch-time文件快照。三个pinned helper当前SHA也与脚本硬编码一致。
3. Base summary与structural companion两个指定文件均不存在，故脚本停在 `WAIT_BASE_STRICT_GATE`，每120秒重查。所读日志完整前缀只有该事件；没有IO/OO_DISPATCHED、MONITOR_STARTED或DISPATCH_AND_CLOSEOUT_ARMED记录。预定两臂run目录、launcher/supervisor/closeout文件及结果JSON均未出现。
4. 可见 `/proc` 中未发现目标Core41 IO/OO runtime、runner或该两臂monitor。目标本身只有sleep子进程，没有正在执行resource auditor或dispatch helper。另一个Core41 candidate collector **PID1482676/start_ticks585007227** 实际存在，但不是目标子进程，也不在退役批准范围；其它FAST64 controls与独立EP-L2模拟器均保留。
5. 该dispatcher唯一候选future work仍是**2DConvolution IO、OO**。冻结科学边界为原2D `FORMAT_APPLICABILITY_REVIEW_PENDING / UNRESOLVED_FORMAT_APPLICABILITY`，本轮2D任何arm/新派生trace均STOP；不是Gaussian AA2缺的四点，也没有当前2D新启动授权。维持自动续发已经不是当前科学计划所需工作。

因此没有发现需要由目标继续保护的已启动IO/OO任务，而其latent自动发射能力与当前2D“不追加执行”边界不兼容。当前Base文件缺失只是临时技术gate，并非科学禁发开关；保留进程不等于它永久不能发射。

## 它仍能做什么

旧auto脚本（对应冻结Framework源码）第52–69、93–133行：每轮先核3个helper SHA；两个Base文件出现且JSON身份匹配后，执行两worker资源审计；须safe=YES、authorized_workers≥2、candidate_cpus含36和37。随后若目标run目录不存在，分别调用dispatcher发IO/CPU36和OO/CPU37，再启动各自closeout monitor，最后退出。

下层dispatch脚本还检查旧Core **41d740e862a6ad89ab0fc32b7b927ec787752862** 的HEAD/clean、runtime、readonly runner、config与trace-list hash、Base JSON、target路径和独立dispatch锁。当前旧Core仍为该SHA且clean；runtime和runner都存在且与脚本pin相同。**未执行任何helper或dry-run，未读trace list/body，未重新做资源准入**；不能断言所有下层gate现在或未来都会通过，也不能断言它永远不会再发射。

另发现第73行 `local mode=$1 lower=$2 ... run=...${lower}...` 的同语句展开问题：`run`读取的是此前的lower，并非同语句新赋的参数。独立最小Bash fixture在未定义lower、set-u时预期退出127，见 `FUTURE_BRANCH_FIXTURE.json`；只检查目标初始环境中lower/BASH_ENV均缺席，未窥探私有Bash变量存储、未执行原未来分支。按所审脚本无先前lower赋值的路径，**IO dispatch先发生，随后start_monitor预期在此失败，OO后续文本路径未必可达**。因此“两臂+monitor”是配置意图，不是已证明会全部启动；至少IO的前置派发风险不能用这个bug排除。本Goal不修脚本，也不把偶发工程失败当科学STOP机制。

该旧脚本没有读取当前2D科学STOP、AA2的执行合同或其HOLD状态。Base provenance的历史 `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` 分类也不是当前新执行权限。因此技术gate未来变true并不提供科学授权。

## 最小停用方案——只供用户批准后另行执行

**本Goal不执行以下步骤。停用属于状态改变，必须按用户本轮明确要求等待单独批准；不能由本包的候选裁决自动执行。**

1. 执行前重新核 `PID=1425986/start_ticks=584741606`、cmdline、脚本SHA、lock device/inode、Base gate、全部直接/间接子进程及目标run artifacts。若出现simulator、runner、auditor/dispatcher、monitor或新任务，停止该方案并重审，不能沿用本次静态候选。通过pidfd固定该实例后再核start_ticks，避免只凭数值PID的复用竞态。
2. 仅向**该父shell实例**发送一次默认终止信号 **SIGTERM**，使用pidfd的单进程目标语义。脚本没有安装TERM trap；这是拟议的单进程退役，不是进程组/session终止，也不按模糊进程名批量操作。此处只描述方法，没有交付或执行可自动发送信号的脚本。[pidfd_send_signal(2)](https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html)
3. 不给sleep、collector、monitor或模拟器发送信号。当前sleep继承同一fd9/FLOCK，因此父进程退出后锁**未必马上释放**；让该sleep自然结束，逐次只读复核目标消失与原inode所有fdinfo锁持有者消失。当前poll为120秒，预计等其剩余sleep时长，但不把120秒当强制完成保证；若仍有holder，停止于只读复核，不能自行扩大信号范围。
4. **保留原锁文件、脚本、日志、Base/结果/raw及原Goal状态。** 不主动解锁，不删文件，不更新旧PID文件。锁释放以真实fdinfo/holder变化为证，不用文件存在/不存在代替。Linux FLOCK关联open-file description，fork/dup的继承fd全部关闭前可继续保锁，与实测sleep holder一致。[flock(2)](https://man7.org/linux/man-pages/man2/flock.2.html)
5. 保存停用前后小型收据。如果将来需要新authority或重启该脚本，必须另行科学准入；本方案不改脚本，因此也不声称永久禁止其它人重启。AA2仍保持其原STOP/HOLD，不能因本锁将来释放自动派发或重启原Goal。

## 对已有任务的影响和保留边界

按本轮观察，目标没有已启动Core41 IO/OO消费者；停用将取消**这一个watch loop的未来自动启动能力**。仅终止该父shell不会向独立session的既有runner/monitor发送信号；若执行前出现任何任务，必须先重审，不能把“不发送信号”扩大为对任意新任务零影响保证。sleep自然退出期间仅延后FLOCK释放。

PID1482676的Core41 candidate collector、BICG validator、早期qualification/deferred controls以及其它FAST64 collector不属于本批准对象。它们存在不证明目标应继续发射2D；它们也不会因本次候选而被停止、解锁或自动认定安全。初次观察还有独立EP-L2 simulator PID2938324，最终观察已不再可见；没有向它发送信号，也不从消失推断其终态。它不属于该旧DTC authority。删除某个锁文件或只检查全局 `/proc/locks` 都不能代替上述核对。

“没有发现已派发”仅限当前完整日志前缀、已列artifact路径及可见PID namespace。不能证明从未有过已删除的历史任务或不可见namespace/其它主机的作业；也未用日志行数推真实poll次数——`emit | tee -a`与stdout指向同一日志造成成对重复记录。
