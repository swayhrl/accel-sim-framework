# 本Goal无模拟器启动

本Goal完整模拟器/Accel-Sim/GPU/canary/trace replay启动数0，新性能attempt0，新UUID0，模拟器lock获取0。实际目标只包括两个工程CPU正例的固定小C probe；二者均exit0并reaped。case子进程只运行有限列表的固定CPU Python测试，另有gcc/readelf工程工具。没有启动旧AG的正式run_screen.py，没有调用accel-sim.out，也没有打开trace body。

源码审计见evidence/PROCESS_API_AUDIT.json：

- mapping_roles.py只做文件校验，没有fork/Popen/exec/shell接口。
- early_system_loader_cpu.py唯一fork/exec目标为编译的固定ag2-cpu-system-loader-probe常量，没有任意可执行路径、参数、shell或dispatch模式。launch_gate在fork前核固定目标、C源码与build receipt SHA、PT_INTERP和DT_NEEDED；manifest在fork前写出。
- qualify_mapping_cpu.py只运行固定/usr/bin/python3 -B test_mapping_roles_cpu.py和有限CASES枚举，负例中所谓simulator目标仅为拒绝launch_gate的字符串，绝未执行。
- replay_legacy_nine.py及其最小common模块没有进程创建；只读保存的旧映射证据，输出AG2 raw。
- ptrace仅由自己的fork子进程TRACEME及父进程固定child PID使用，永不attach。唯一kill只用于自有未回收CPU child的异常清理；本轮两个CPU目标均自然退出，没有向其它项目发信号。

旧AG的launcher源码仅history/scripts/run_screen.py.txt不可导入文本，未纳入任何可调用工具路径；原worktree中旧脚本保持原冻结内容。本包没有发布完整模拟runner，也没有配置任何后台派发、恢复、自动重试或预算表。

evidence/CPU_AUTHORITY_TERMINAL.json记录两个自有PID/start_ticks均不存在、所有owned child已回收、无派发余留。只读site快照用于CPU工作记录，不是新性能准入或运行授权；旧AG/AA5资源合同没有变更。

本证明来自明确执行清单、代码允许的启动路径和自有child收据，不把整个host其它项目的进程计为本Lane的启动或声称它们已停止。
