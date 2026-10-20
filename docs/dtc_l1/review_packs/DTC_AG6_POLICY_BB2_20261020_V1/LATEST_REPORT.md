# BB2：Policy B 源码与封存回放完成，CPU资格未放行

结论：`DESIGN_ONLY_NOT_SAFE_FOR_PRODUCTION`；实际 CPU 测试为 `NOT_EXECUTED_RESOURCE_HOLD`，不声称8组测试通过。已完成资源合同、最小语义进展接口设计、纯离线策略和8组针对性测试源码，以及原28条记录的旧I/O规则独立复算。B的历史结果列是明确标记的**未执行预期判定**，不是CPU执行证明，也没有预测AE_GEMM会完成。

原174环境、独立 worktree/output；Goal精确提交 e83156d8ff2620686ca1bea4bea3da94fb57079e，完整读取；BB锚点 ee61be47f5d2e6cbeaa028791f9674b8f092ee86。未重审原AG5/SEM/ROB资格，不读模型或trace，不改生产规则。

## 实际入口结果

2026-10-20 09:49:41 北京时间，冻结CPU准入回调的首样本：host IO full avg10 **28.90%>25%**、cgroup IO 0、两范围memory PSI 0；host available=335,113,572,352B、cgroup headroom=208,470,069,248B、disk=18,621,779,968B，空间与内存通过。首样本失败即停止，没有第二个样本、资源重试或等候轮询。

实际authority未闭合仅涉及本入口自身：调用使用相对脚本路径，与已注册绝对argv不相符；现存回执中的唯一unknown PID就是entry PID，不能据此指控其他窗口。入口已增加绝对argv检查，但遵守本次host资源HOLD，未再入场。之前一次入口在任何OS采样或测试前因归档`mapping_roles`依赖缺失退出，已补齐准确冻结依赖；失败回执保留。两次入口都未import测试/策略执行器，实际unittest=0、fixture=0、模拟=0。

因此，本包为**源码审阅 + 预期测试 + 真实准入拒绝 + 已执行旧规则算术回放**。不是CPU资格PASS。精确源码、入口提交、准入检查与执行数量见 [CPU_QUALIFICATION.json](CPU_QUALIFICATION.json)、[CPU_ADMISSION_SUMMARY.json](CPU_ADMISSION_SUMMARY.json)。归档准入源码与当前只读authority回调被单独隔离；纯PolicyB不import它们或任何生产BA/guard模块。

## 科学结果

- [28行比较](HISTORICAL_28_ROW_REPLAY.tsv)复算旧规则与原decision/资格计数全部一致：第22/25/28行三资格点26.50/60.09/56.22%，第28行STOP；旧STOP不变。
- 历史`semantic_progress=UNAVAILABLE`，替代I/O影响/运行期适配器证据同样缺失。B列全部保守不足证据，标有`proposal_evaluator_executed=False`与`UNDETERMINED_PROGRESS_NO_PRODUCTION_PROMOTION`；没有向历史插入合成计数、完成事件或速度。
- 精确c809源码已有完成active-lane模拟指令计数；CTA会重置，kernel done也用于强制停止。冻结62323c40 observer没有完整实时语义协议。优先方案是安全点coherent采样累积完成指令，绑定PID/start_ticks/generation、input/ROI、seq与monotonic时间。计数增长仍不证明数值正确或共享存储无害。
- B保留严格paired R2、>5GiB+预计写入、memory/swap/OOM/identity/deadline等保护。Runtime PSI拟作告警，但以实测I/O影响、显式有界高压episode fallback和原总deadline约束；新时长均caller显式的**合成示例参数**，无生产默认、未选择生产门槛。
- 重复mapping哈希减负仅提出审计保持的源码方案：没有可强制的文件不可变保证则仍逐次哈希。没有实施或声称节省百分比。纯策略测试与生产开销的实测数据均UNAVAILABLE。

## 阻碍与下一轮最小授权

暂不推荐立即放行新的生产AG6 cohort。先需在新鲜严格准入与正确绝对角色绑定下，完成已准备的8组纯CPU语义测试；随后才可另批 opt-in进展producer/consumer、安全与共享I/O公平性适配器、合法无退休phase界限、真实guard闭合与一次计划内端到端资格。任何真实模拟资格都要明确新的启动预算和新UUID，仍由BA唯一dispatcher执行，不是免费canary；不能使用封存三个UUID。

本轮没有生产IO gate变化，没有旧Goal重启或新实验预算。AG6仍1/4消耗、0有效、3封存；BA仍0/32；O provisional、F=null，旧selection/44/GM12/T/U/Core均未变。进程信号、锁获取、模型/trace读取、编译、模拟、fixture和性能UUID创建均为0。

发布完整证据与精确远端回读后STOP，不自动补跑CPU测试或启动任何模拟。审阅入口：[合同](POLICY_B_CONTRACT.md)、[进展可行性](PROGRESS_SIGNAL_FEASIBILITY.md)、[证据索引](EVIDENCE_INDEX.md)、[预算边界](SCIENCE_AND_BUDGET_BOUNDARY.json)。
