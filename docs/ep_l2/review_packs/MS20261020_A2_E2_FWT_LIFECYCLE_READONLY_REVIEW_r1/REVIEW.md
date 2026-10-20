# A2对E2 FWT执行生命周期的独立只读审查

审查固定于E HEAD `7ca11b7b698fa7c7eeaf602101a31153c13125bd`。结论：**缺少的是原生进程真实OS退出状态的持久回执；正式全输入与硬件drain闭合验证随后未执行。E011/E012保持INCOMPLETE，不具备成对性能验收条件。** 这不是已经证明的main61生产语义错误，也不能据此宣称原生应用正常完成。

本次仅静态读代码、回执、保存的进程快照及raw文件。未执行E parser、runner、registry API或任何原生实验；未构建、启动应用、重放实验或修改E文件。累计实际启动观测为12/40，本次新增0；T0和所有原预算不变。源码、回执SHA及物理观测在`FINDINGS.json`，固定E版本快照在`E_snapshots/`。

## 已证实的调用链与进程关系

所有下列行号均针对上述固定E HEAD；本目录快照保留原始行号。

1. `run_fwt_pair.py:15`调用`controller.step()`；`controller.py:53–64`用线程池运行`runner.execute()`。线程池不是额外的父进程，原生应用的直接父进程仍是controller PID **1665599**。
2. `runner.py:142–148`调用`Coordinator.start_application()`；`coordinator.py:553–565`执行`Popen(..., start_new_session=True)`并登记真实PID/start/boot。`start_new_session`创建原生应用独立session/进程组，**不改变其父子关系，也不保存退出码**。
3. 原执行会话记录退出143。它与128+SIGTERM相容，但现有记录没有信号发送者或原controller的wait回执；不能进一步断言具体外部工具杀进程的原因/方式。`runner.py:184–208`的`except BaseException/finally`不等于SIGTERM处理器：在没有Python处理器的默认SIGTERM终止路径中，不能依靠这些块回收孩子并落盘。
4. `recover_fwt.py:90–100`确认原controller消失，获得同一个`CONTROLLER.lock`，并在**第96行确认两个应用PPID均为1**，之后登记恢复controller PID **1733310**。取得单例锁恢复的是调度权限与资源观测，不能将已有孤儿重新变成新controller的孩子。
5. 保存的末次恢复heartbeat进一步记录：S PID/PGID/SID均为**1665796**，F均为**1665810**；两者PPID均为1、状态R。原生应用独立进程组确实存活过原supervisor退出，但新supervisor没有取得它们的`waitpid`所有权。`/proc/1/cmdline`当前为`/bin/bash`；本次未对PID1采取任何操作。

## 具体缺口与终验判定

正常路径在`runner.py:148,168–183`通过原父进程的`Popen.poll()/returncode`先要求真实exit0，随后才执行native计数、独立parser、全输入指令闭合和`validate_summary()`。但exit状态只保存在父进程内存中，到最终`run_status.json`写入前没有单独的持久OS退出回执（第188–197行）。

恢复路径`recover_fwt.py:14–19,55–71`只能轮询`/proc/PID/stat`，期望抓到短暂的Z状态并读取field52。**第32–34行“PID1 bash retains zombies”的假设没有成立为可靠契约**：一个非子进程的zombie可能在两次0.2秒观测间被真正的父/reaper收走。增加轮询频率不能保证取到wait状态；pidfd可提供身份/退出通知，也不会自动赋予对非子进程的wait权限。

两份最终回执走了`recover_fwt.py:57–58`的进程已消失分支，缺少`exit_code/kernel_exit`，保留`execution_stage=NATIVE_EXECUTION`、`complete_input_verified=false`、`independent_acceptance=NOT_ACCEPTED`。第73–80行正式终验没有进入；物理结果目录中也没有`parser.log`或`terminal_summary.json`。第83–85行落盘INCOMPLETE，随后第107–112行正确拒绝pair与后续主矩阵推进。

| 层次 | 本次实际证据 | 可得结论 |
| --- | --- | --- |
| 身份与运行存在性 | 原PID/start/boot、保存的PPID/PGID/SID、raw SHA | 原应用确曾运行；恢复期未重新启动 |
| 原生OS退出状态 | 原父退出，应用随后被reap；没有持久wait回执 | 不能证明exit0，也不知道真实最终信号/退出码 |
| raw文本 | 两份raw SHA与固定E回执一致；均有791609344指令的最终计数、exit文本及drain相关记录 | 仅保留待核验的应用自述；不能替代OS退出与全64slice闭合验收 |
| 正式终验 | parser/summary/validation未产生 | drain/所有权/全输入正式资格未判定；不是已经证明drain失败 |
| 成对结果 | 两端INCOMPLETE，pair=null | 不生成PASS、性能比或预算退款 |

另有同源竞态：`recover_fwt.py:65`在owned stop后要求进程仍为Z；`finish_zombie():39`再次断言已观察的Z仍存在。两处都可能遇到真正父进程已reap，导致恢复器断言退出。这不是本次已证明的实际失败分支，但应随同修复。第19行`f[49]`正确对应stat field52，**不是下标偏移问题**；heartbeat中R状态的field52=0尤其不能作为exit0使用。

## 交E独立实施的最小工程建议

1. **保住既有controller的wait父进程。** 在主线程安装有界SIGTERM处理，先停新派发，让已入场runner继续按原timeout/资源策略收尾并wait/reap后退出。若E要求立即停止，应显式对自有原生进程组执行已有TERM/3秒/KILL/wait路径并记录中断；不要只让supervisor退出。不能在signal处理器里直接阻塞wait，也不能创建第二个E controller。
2. **将真实wait结果在parser之前独立持久化。** 在`runner.py:168`附近增加原父采集的`NATIVE_EXIT.json`，绑定attempt/run_key、native PID/start/boot、wait_owner、source/main身份、退出码、raw SHA和采集时间。复用现有`write_json`的fsync+atomic replace。这是执行回执，不是科学PASS；真实exit0之后仍需所有原终验门。
3. **重连先消费已有真实回执，不再依赖“迟早会抓到zombie”。** 若未来已有上述回执，E独立校验完全一致的身份、raw hash与退出状态后再进入原终验；若非子进程已reap且没有真实回执，明确INCOMPLETE。处理第65/39行的消失竞态，不能用running field52、进程消失或raw尾部填退出码。E011/E012不能事后制造这种回执。

`PROPOSED_ONLY_NOT_APPLIED.patch`给出第1/2项的两文件小补丁草案，针对固定HEAD，**没有应用**。仅做了内存hunk/context核对和AST语法检查，没有runtime测试。草案采用延后普通SIGTERM、停止新增派发并保留原父直到已入场runner结束的策略；原native资源终止宽限和超时没有改变。E应在实施时核对主线程调用、信号到达与入场竞态、外部执行器退出契约，并独立发布、重绑现有tooling/API哈希，不能绕过冻结绑定。

该草案不保证抵抗SIGKILL、宿主崩溃或外部执行器随后强杀整棵树。若原工具不能允许bounded drain，应将**同一个单例controller**放在受保护的持久执行会话，或预先建立可靠wait owner；单对已经孤儿化的PID调用setsid/nohup/重新加锁，不能追回已丢失退出码。未证实外部143来源前，不宣称某一种会话配置已经解决该问题。

无需为本审查重跑FWT，也不扩大到生产main或控制器重构。E独立选择工程修复与后续授权；本审查保持FWT INCOMPLETE、历史证据及预算计数不变。
