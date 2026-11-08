# Q1 CPU修复与资源边界审查

本次为CPU-only工程修复，不启动新GPU Goal，不取共同锁，不调用Image-Lab API，不改V1/R1原始结果。基线为R1最终39e129a6db5236f7acc595b5abaef14331df8ac9。候选代码位于util/ai_workload_research/q1_3dgs_cpu_hardening，旧工具与raw保持只读。

## 修复了什么

1. R1保存函数的semantic赋值修复已经保留；本次再发现端点after路径同样缺赋值。现显式计算并保存final_semantic_fingerprint，覆盖有/无checkpoint及EXACT/NOT_ESTABLISHED分支。
2. 取消保存最终状态前删除C_D。发现阶段的canonical checkpoint必须保留，不能用先删旧态的方式腾空间；因此晚期多状态实际磁盘需求需要重新核算，见RESOURCE_LIMITS.md。
3. supervisor在launch前登记job与源码SHA，启动、identity绑定及后续监控均处于try/finally保护内。即使启动失败、极快退出或真实监控STOP，也保存实际可取得的PID、OS退出码、ERROR/RESULT与异常原因，关闭日志。无法取得的退出码仍为null，不补造。
4. 未放宽VmSwap、未知PID、AccessDenied、PID复用、worker健康、共享GPU或资源上限规则。非正常退出恰逢监控缺口时仍STOP；本次没有把R1历史STOP改为PASS。

## 验证方式

通过的是CPU控制链路，不是GS-Scale原生GPU科学实验。

- 真实CPU Tensor、真实state_store、实际Controller.capture/save/restore_runner/assert_restored/before/after，走通保存→恢复→模拟数值更新→续行→再保存→再次恢复。
- 端点无保存路径、完整semantic精确相等/不等、sidecar写入失败不产生成功收据、最终保存保留C_D，均实际执行。
- 使用真实CPU子进程进入实际supervisor.run/run_job，串行成功→exit7错误→下一任务→最终清理。另注入启动失败、身份读取竞态、独立监控缺口，检查错误和退出码持久化。
- GPU、NVML、服务和共同flock边界均为mock；CPU tiny Runner不代表GS-Scale算子、质量或性能。真实CPU子进程都结束，CUDA保持未初始化。
- 在隔离副本上使用旧R1 worker实际调用同一个端点，稳定复现NameError；修复后相同调用通过。旧authority未改写。

最终235个不同适用CPU测试通过，另2项Qwen专属测试明确skip。重复执行的测试不重复计数。证据与计数在CPU_TEST_SUMMARY.json。原有AST数学顺序测试、loader、store、资源越界与监控安全测试同时保留。初次测试夹具问题与原缺陷复现日志保留。

## 能否说已修干净

已修复本次定位到的代码缺陷，并把此前漏测的跨函数执行链补进CPU回归；候选源码冻结。不能宣称所有GPU分支都已验证。后续若获独立授权，仍需在同一合法窗口先用真实GPU验收当前候选，而不能把这里的235项CPU测试当作GPU PASS。

本次没有新增晚期训练、性能样本或硬件归因，不改变R1的INCONCLUSIVE。

## 资源判断

V1/R1均未观测到用户批准资源容量超限；实际中断来自工程错误及其触发的监控安全条件。当前无证据要求扩大显存、RSS、charged-memory或8h/3h预算。

真正需要提前处理的是：唯一窗口释放后不能再次取锁；实际训练分配仅14logical而非16；完整晚期checkpoint的大小与恢复峰值尚未实测；代码存在额外保守准入和实现上限。详见RESOURCE_LIMITS.md，逐项区分用户合同、实现阈值和未知容量，未静默调整。

本次仅发布修复与审查，完成Git回读后结束，不启动GPU或R2。
