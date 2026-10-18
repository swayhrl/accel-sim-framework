# AG 独立 DISCOVERY_OPT 资源合同差异与裁决

适用范围仅为本次AG新8个UUID；不修改AA5、历史raw、STOP或任何其他项目合同。默认并发严格为1，不启用双worker。

权威旧证据为AA5固定提交 `2d740ece2f5dbb6d99040a64f421e940687a48fa` 的 RESOURCE_CONTRACT.json 及续轮 run_matrix.py。该cohort实际1/4启动、0/4完整strict；451.4s时host pswpin单页增加触发其已冻结STOP。own ru_majflt=0、峰值RSS626688KiB，故该host-global事件不能归因于sim。原停止合法且保持；AG新规则不追溯改变它。

| 项目 | AA5冻结实现/文字 | AG R2 V1明确规则 |
|---|---|---|
| host-global pswpin/pswpout | 任意较起点增加即STOP | 逐采样记录；孤立小增加为WARN，完整采样提高至5秒；不从单页delta发送SIGTERM |
| 准入 | 两次相隔至少10s；host与cgroup余量≥32GiB，disk≥10GiB，memory-full avg10≤1%，io-full avg10≤25%，无新增OOM | 全部保留；删除的只有孤立host-global swap零增量否决，其他项目全部计入 |
| OOM/最低线 | 新OOM；host/cgroup余量<8GiB；disk<2GiB | 保留；cgroup oom/oom_kill新增在下一次≤1s轻量轮询中立即作STOP决策并记录，不声称零检测延时 |
| memory PSI持续紧急线 | >10%，连续3个30s采样 | 保留严格大于10、三次且间隔≥30s；第一次运行时观测立即有资格计数，无额外初始30s等待；WARN的5s采样不缩短后续观察间隔 |
| IO PSI持续紧急线 | 指定AA5合同与执行代码没有独立IO运行时紧急字段，只有准入≤25% | 披露原缺口；本AG明确新增保护：io-full avg10>25%，连续3次且间隔≥30s则STOP。不是声称原代码已有该规则，也不是放宽历史合同 |
| cgroup swap持续增长 | 无本项独立规则 | 相对本run起点≥16MiB，在连续3次间隔≥10s的合格采样均保持≥16MiB时STOP；任一次低于16MiB重置计数。仍高于阈值的部分回落不重置 |
| 关联压力与major fault | 原host-global变化直接STOP | 报告host page delta、cgroup swap/memory PSI、own majorfault增量与采样时间；增加采样。触及明确紧急条件则STOP，未触及则WARN，绝不把major fault等同于本进程swap或用它声称全局事件归因 |
| 超时/失败 | 7200s、单UUID单次实际启动、无失败重试 | 保留；失败、timeout、错配或资源STOP完整保存并停止后续筛选，不补格 |

裁决依据是用户明确批准的独立AG资源版本和保留持续紧急保护的要求。原AA5没有IO运行时字段这一事实公开列出，不能私下按想象声称继承；AG增加同准入上界25%的持续STOP保护。上述阈值、连续样本数、比较符号、观察间隔、采样加密与STOP目标在首个新性能前随完整科学预注册commit/push/fetch-back，之后不因性能或告警调整。

只允许对本次新AG runner直接创建并用PID/start_ticks/pidfd固定的子进程发SIGTERM；不按名称、进程组或session发信号，不SIGKILL，不碰其它项目/旧锁/旧进程。未回收自己的child前不释放本AG执行authority。采样与决策日志必须保留，WARN不是免监控。本文件单独不构成性能启动登记；只有完整EXECUTABLE_PREREGISTRATION.json及全部绑定文件已commit/push/fetch-back，且每次最新准入通过，才能执行。独立owned-child OOM watchdog实际以0.25s轻量轮询，在hash和全量/proc审计期间仍有效；所有full资源采样记录host-global swap，轻量watchdog仅监测cgroup OOM事件。
