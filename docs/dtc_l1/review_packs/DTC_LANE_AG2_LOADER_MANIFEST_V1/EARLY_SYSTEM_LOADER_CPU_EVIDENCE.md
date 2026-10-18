# 真实早期系统loader CPU证据

固定C probe只调用私有CPU函数返回174并write成功标记，自然exit0。编译仅gcc，无CUDA或模拟器；依赖libag2_cpu_fixture.so与libc.so.6，PT_INTERP=/lib64/ld-linux-x86-64.so.2，canonical为/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2。静态readelf与构建完整命令/编译器SHA见CPU_BUILD_RECEIPT.json，不以运行目标的--list推导资格。

证据根：evidence/cpu-final/。CPU_MAPPING_PREREGISTRATION.json在fork前新采集cache与全部ELF；PRE_FORK.json绑定manifest SHA及精确argv/env。冻结monotonic_ns=9057974715440291，fork_ns=9057974721329606；自有PID3813999/start_ticks905797472。此前独立首次CPU正例也保留于cpu-initial/，之后因Python兼容修正对最终源码重新冻结、CPU复核；两次都不属于模拟attempt。

| 时点 | 停顿与实测 | 证明 |
|---|---|---|
| 0 | kernel exec SIGTRAP，loader尚未执行 | 完整初始maps已含主ELF、系统interpreter |
| 72 | syscall9 mmap出口 | cache实际映射首次出现，SHA/dev/inode及非ELF角色通过 |
| 72至123 | 多次完整快照 | cache与ELF共同被确认，全部5个注册文件真实覆盖 |
| 123 | syscall11 munmap入口 | cache仍实际存在，地址/长度及maps保留 |
| 124 | 同munmap出口，return0 | cache不再映射；确认后消失被允许 |
| 127后自然退出 | exit0，成功标记 | 128快照、全部角色/注册文件、最终SHA及闭合通过 |

cache当前SHA026c6716eea796297e7da1e0f63c3439bfa47108cf8a22fae80c59b22e9ec1ff；dev major0/minor156，inode33906366，46232B。完整stat及时点见manifest。该本轮事前身份与旧事后观察巧合相等，不补旧清单。

机制是自有child PTRACE_TRACEME，exec后第一次SIGTRAP开始PTRACE_SYSCALL，EXITKILL保护协调器意外死亡；无attach、LD_AUDIT、LD_PRELOAD、inhibit-cache或GPU。所有maps从真实/proc取得；没有靠sleep等待cache消失。CPU库validate_manifest → Sequence.observe → parse_maps/validate_snapshot → verify_file/file_record → Sequence.close均用于真实数据及负例。

覆盖边界：这是新候选解析器的实际系统loader路径资格，不是旧run_screen.py的修复发射测试；旧生产脚本未改、未运行。未覆盖大型C++模拟器、libcudart/GPU、trace helper子进程、线程间映射修改、异步监测漏窗、其它架构/namespace、无cache系统正例或模拟全生命周期。这些均UNQUALIFIED，不能由当前PASS推定正式runner已经可发射。
