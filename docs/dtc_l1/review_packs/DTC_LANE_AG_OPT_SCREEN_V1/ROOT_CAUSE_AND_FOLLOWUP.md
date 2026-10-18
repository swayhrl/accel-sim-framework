# 本轮 STOP：启动映射预冻结漏项

实际启动1/8，完整strict0。唯一BASE_GEMM UUID5de274d3-f296-4ee8-a577-17cc661e718e，PID3740731/start_ticks905152384，按冻结身份失败规则由自有pidfd发送SIGTERM，exit=-15。协调器PID3739908/start_ticks905150778已退出，AG FLOCK已释放，无后续派发。原八格和UUID不更换、不重试；AD两格仍HOLD_UNQUALIFIED。

我的执行器封存遗漏了启动时映射的`/etc/ld.so.cache`。freeze_runtime.py用loader的`--list`固定ELF/依赖/loader及已知helper；run_screen.py的mapped_files()却接收所有filesystem-backed映射。第一次看到libcudart映射时，`/etc/ld.so.cache`仍在该快照中，其SHA026c6716eea796297e7da1e0f63c3439bfa47108cf8a22fae80c59b22e9ec1ff不在预注册清单，因此整体身份检查失败。文件为非ELF loader数据；已观察到的ELF SHA均匹配冻结值。这解释了清单与分类边界不一致，不能追认该attempt合格。

“暂态”是对loader行为的解释；本次停止前没有观测到该映射解除，不把解释当实测。CPU wrapper正例使用的Python入口属于OSS工具链wrapper，其实际argv有`--inhibit-cache`，且测试等待后才采样；未覆盖本轮系统loader的第一次C++启动映射。原7/15 CTests、正常打印与机制CPU证明保持其有界资格，但不能代替完整运行身份准入。

本次stdout28672B、stderr0，原样保存在独立raw并有完整SHA索引。观测到的完成kernel header为0，完整BASE校准未发生；GPU整数cycles、各arm比值、实际应用重叠/流量/收益全为UNAVAILABLE。约0.706s wall仅为生命周期诊断，绝不转换为GPU性能。

停止不是AG换页或OOM规则触发：运行首尾host pswpin/pswpout增量0，cgroup swap增长0、OOM/oom_kill新增0，own ru_majflt0，峰值RSS180224KiB（176MiB），最终资源决策CONTINUE。之后收尾审计IO-full为30.20%/23.06%，双样本不满足新准入；它晚于身份STOP，不倒写为停止原因。只读审计helper的CPU阶段固定0计数另有明确correction；启动预算以RUN_START/POPEN_CHILD/MATRIX_TERMINAL为准，原始审计未重写。

全部197生效文件、11个冻结运行文件、Core965dffe0、两原list及511成员stat身份在停止后复核不变。原AA5历史1/4启动、0/4完整strict、451.4s单页STOP与67/510 prefix保持，不重启、不补入新BASE。没有候选应用性能结论、论文晋升或独立验证结论。

后续修复建议是预先声明并固定loader数据输入的角色、SHA及文件身份，在实际映射可见时严格核对；保留对其它未知文件或ELF错配的拒绝。不能简单忽略全部非ELF映射，也不能把本次事后看到的cache SHA当作事前身份。还需用实际系统loader/早期C++映射CPU fixture补资格。

postmortem/replay_mapping_roles_cpu.py给出独立、只读、无loader/模拟器调用的九项CPU重放原型：原清单仍拒绝；反事实显式cache角色能解释已保存快照；改动ELF/cache digest、未知ELF/数据、角色缺失/错分均拒绝。它没有更改冻结runner或原失败状态，不构成已发布可执行修复。任何新性能需新用户审查、新cohort/UUID预算与完整预注册，不在本轮自动继续，也不启动其它输入、K1、组合或新Tag候选。
