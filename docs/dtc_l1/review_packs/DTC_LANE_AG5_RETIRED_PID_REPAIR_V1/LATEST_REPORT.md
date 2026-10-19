# AG5 CPU repair result

**PASS_BOUNDED_CPU_RETIRED_PID_REPAIR。实际新增模拟启动0；新性能UUID 0；AE/AD性能结果仍为UNAVAILABLE。**

AG4后三点没有启动，是因为其第2节要求的PID复用负控没有覆盖实际wait分派路径。复查发现退出PID仍保留在`owned`与`states`中，新实例可能在父级事件证实前被resume。第4、5、7节冻结规则要求科学资格出现缺口时整批STOP、不重试，所以不能修复后恢复旧UUID。不是AE/AD性能差，也没有证明真实模拟曾发生PID复用。

现在已在独立工作树修复：移除永久PID集合；唯一分派资格来自当前未reap的已证实实例。退出同时撤销归属、image和待继承状态；stop与resume都重新核PID/start_ticks/tracer/Tgid，image绑定对应generation。父级fork事件发生时复制受验证的继承信息，避免父进程退出后依赖其PID状态。退出记录另按PID/start_ticks保存，防止历史同PID记录互相覆盖。

CPU验收53项通过：14项真实生命周期、4项原有身份/外部负控、6项完整guard入口generation测试、8项mapping角色、10项原R2资源逻辑、3项模拟启动策略拒绝、8项外部锁精确绑定。长fixture至少3次真实10秒周期采样；实际采样数见最终裁决JSON。合法的“父先reap、子后首次stop”也通过。

完整分派复现使用真实CPU fork/exec/exit，再注入明确声明的同PID新generation停止状态。旧分派代码尝试`PTRACE_CONT`，测试适配器在系统调用前阻断；新代码维持PENDING且authority不得PASS。**没有强制Linux实际复用PID**，不能把这项覆盖写成内核端到端复用实测。真实事件重排、pending确认超时和STOP清理由另组真实CPU测试覆盖。

运行期间新增EP-L2离线锁曾触发STOP。只读检查证明是独立离线分析，随后增加精确PID/start_ticks/argv/cwd/脚本SHA/锁路径绑定，7种身份或路径变更仍拒绝。没有按目录通配放行，所有项目仍计入资源；没有操作外部进程或锁。另保留CPU测试锁竞争、测试适配器栈定位错误、Python环境污染的原失败记录，未把这些失败改写为PASS。

**现在仍不能启动新模拟。** 现场磁盘低于原10GiB准入线，具体时点及字节数见`FINAL_AUTHORITY_AND_RESOURCES.json`。没有执行两次正式性能准入，也没有设置新的模拟预算。旧AG4 UUID已封存；未来运行需要用户明确新批次范围/预算、BASE复用资格以及新的完整预注册和发布回读。本包禁用SIMULATION用途，只允许固定CPU fixture；未提供性能dispatcher。

收口复查曾另观察到独立DTC closure lane的CPU资格脚本，其执行权不在本包已固定的审查集合中。当时的`STOP_AUTHORITY_NOT_CLOSED`原样保存在`INTERIM_AUTHORITY_STOP.json`；没有添加例外或操作其进程。随后最新快照已无这些临时控制器，authority为PASS，详见终态JSON。当前现场authority与此前通过的有界CPU测试是不同时间/不同裁决：后者PASS不覆盖未来的执行权变化。未来启动前仍须重核。

历史不变：AG4为2/5实际启动、1项完整strict观测、0项有效优化结果；Gaussian 3,278,356 cycles保留为原观测，不能自动成为下一批资格控制。AG3为2/6启动、1项完整PASS；旧AG为1/8启动、0项完整PASS；AA5为1/4启动、0项完整PASS。Core、模拟二进制、trace、旧raw、论文未修改。旧AG4 142个发布blob及81项冻结执行文件逐项核对；最终CPU进程和自身FLOCK退出证据见`NO_SIMULATOR_STARTS.json`。
