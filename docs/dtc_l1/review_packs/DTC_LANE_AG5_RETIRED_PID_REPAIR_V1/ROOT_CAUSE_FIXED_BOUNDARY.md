# Fixed boundary and source review

旧源：AG4 `d8d0401dab0a1d9cb949302bcc05148328421cc2`；原冻结复现和最终STOP收据在继承的AG4包，保持原blob。`HISTORY_PRESERVATION.json`逐项绑定。

| 旧行为 | 新行为 | 验证 |
|---|---|---|
| terminal只pop confirmed，保留owned/states | 统一retire，清除当前归属、image、继承和隔离队列项 | 完整guard退出→同PID停止负控 |
| owned集合允许历史PID直接进入分派 | confirmed仅保存当前未reap实例，未知stop先quarantine | 子进程、线程、root三类注入 |
| 普通SIGSTOP可不重新核身份就resume | stop与resume核start_ticks/tracer/Tgid，image核generation | current identity及stale-image负控 |
| 首次child stop查父PID的当前image | 真实父fork事件时复制继承快照，绑定父/子ticks | 真实子stop延迟到父reap之后仍自然exit0 |
| exits按PID存储 | 兼容旧诊断，另附逐PID/ticks退出历史 | 最终实例退出审计 |
| 单个历史EP-L2锁绑定 | 保留原精确绑定，另加本次逐项审查的离线controller | 7种变异拒绝及当前正例 |
| guard可接SIMULATION capability | 本CPU修复包明确拒绝SIMULATION，仅固定CPU ELF路径 | fork前3项拒绝 |

`SOURCE_DIFF.patch`包含同名源的逐行差异；新测试和闭合工具直接提交完整源码。白名单仅本新review pack。Core及实际模拟二进制没有变化；mapping_roles、resource_policy、freeze_static、OOM watchdog均保持原字节。没有修改任何额度、时钟、K0/K1、AE/AD、Tag、输入、统计、loader白名单或科学超时。

受控路径：x86_64、TRACEME、自身ptrace fork/vfork/clone/exec/exit事件、主线程reader-helper、CPU线程创建退出。未资格泛化为任意Linux进程监督器；非leader exec等未测试路径不得推定支持。只有当前未reap子进程的terminal wait能够retire；不能对已经消失的/proc再推测新实例身份。

未确认的停止仍只能PENDING，有限确认窗口2秒，最多256事件后observer采样；父事件必须来自已确认父实例的真实GETEVENTMSG。每次exec仍完整验证冻结ELF、interpreter、依赖与cache映射/消失。未知exec、文件、可写cache和无法闭合的身份继续STOP。没有PPID/argv相同即放行或永久树白名单。
