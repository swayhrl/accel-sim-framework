# AG7 Policy B integrated：最终STOP

第三个正式点 AD_GEMM 因预注册的 `TIMEOUT_7200` 停止，实际 wall receipt 为 7200.609 秒；其周期和速度结果不接受。控制器随即停止整个 cohort，AD_Gaussian 的新 UUID 未启动并封存。没有重试或延长时限。

原huangrulin-174，BA `/root` 唯一派发。AG7确认实际启动 3/4，接受 2/4；消耗槽位 3/4，无重试、替代、免费canary或预算返还。

F=null，O仍为临时候选；未完成4/4，不作最终AE/AD选择。

| Qualified point | Whole-input cycles | BASE/ON |
|---|---:|---:|
| AE_GEMM | 826089 | 1071405/826089 |
| AE_Gaussian | 3242397 | 3278356/3242397 |

停止原因：`TIMEOUT_7200`。

Policy B仅显式opt-in，默认OFF。原host全局I/O三资格点保护保留；cgroup压力为有界告警。采样约10秒（最大间隔30秒），进展新鲜度30秒、无退休上限600秒、连续cgroup高压上限1800秒及总期限7200秒均保持预注册值。完成指令来自同线程coherent计数；不以CPU活动、trace消费或日志增长冒充语义进展。

W1 实际执行 9 个 unittest 方法，0 failures / 0 errors；包含原八组及声明为 synthetic 的父进程到 fork 后模拟器身份交接用例。W2 实际执行 9 个协议方法、native producer header probe，以及真实 guard 的自然 exit0 和受控停止/回收资格；接收时钟工程修复后在新的严格 R2 下实际重跑 9 个协议方法并通过。W1 的限定 host I/O 例外没有转移到 W2 或模拟器。CPU 合成计数不构成模拟科学结果，旧 BB2 未执行的测试没有被回填为 PASS。

比较资格为 `PASS_BA_NEWLY_SCOPED_AG7_COMPARATOR_ELIGIBILITY_CONDITIONAL_ON_EACH_RUN_CLOSURE`：原 Core `c8090115bd57512b1b23fca7d925301fa620c751` 与原 Core 库字节保持一致；Framework 仅增加经独立审查的观察性 producer。来源、输入/ROI、270 选项、加载器与实际运行时闭合共同构成新限定比较桥，并非仅凭 source diff 继承旧 BASE。两条接受结果均自然 exit0 且完整 strict 闭合；首 AE_GEMM 同时完成真实端到端资格并计入正式预算。历史 AG3/AG4 executor 限制没有升级。详见 [BA comparability decision](AG7_BASE_AND_SOURCE_COMPARABILITY.json)、[W1 receipts](W1_CPU_TEST_RECEIPTS.json)、[W2 qualification](W2_POLICY_PROFILE_AND_QUALIFICATION.json)。

以下是全部已关闭自有 resource log 的一次流式摘要；PSI 均为 full avg10 百分比，属于共享作用域观测，不能独占归因给模拟器。

| Point | Resource samples | Host I/O peak | Cgroup I/O peak | Resource STOP samples |
|---|---:|---:|---:|---:|
| AE_GEMM | 674 | 25.29 | 4.17 | 0 |
| AE_Gaussian | 89 | 29.84 | 0.47 | 0 |
| AD_GEMM | 682 | 21.28 | 0.16 | 0 |

AE 两点曾有短暂 host I/O 高值及 host/global swap 告警，保留原持续性保护规则，未达到 STOP 条件。三个点均无未知 I/O scope 或运行时 authority 失败；未观察到 cgroup I/O >25 的真实高压 episode。因此本轮不能实证宣称 Policy B 在共享 cgroup 持续高压下的公平性或生产级安全性。AD_GEMM 有 719 条连续、计数单调且无超过 30 秒 producer gap 的进展记录，但没有 NATURAL 终态；这些计数仅用于保护诊断，不转换为周期、完成时间预测或 AD 性能估计。Engine 的 terminal failure/identity_pass=false 是超时强制停止后的未闭合状态，不是另一个已证明的身份漂移根因。

推荐保持 Policy B 默认 OFF，将本轮作为有限 pilot 证据交统一科学裁决。当前唯一阻碍完整 AE/AD 筛选的是 AD_GEMM 超时及其导致的 AD_Gaussian 未启动；不能据此断言 AD 无效、AE 胜出或旧 AG6 的 I/O STOP 是误报。若裁决要求补齐筛选，需单独批准未来每点 wall-time 合同及新启动预算；在科学裁决明确接受本轮 AE pair 和限定 BASE 继续适用、且来源/输入/选项/运行时仍可闭合的前提下，最小补齐对象是两个全新 AD 点。该路径须新注册、重新准入，不复用本轮封存 UUID，不退还已消耗启动，也不自动动用 BA32；本报告不预选新的时间阈值或启动次数授权。

已完成自有精确controller/guard实例只读存活检查：活动自有实例0；没有借此重新授予派发权限或宣称审计全部外部任务。旧AG6仍1/4消耗、0接受、三个UUID封存；BA原0/32独立。原selection/44行/GM12/T7/U2及Hotspot/Btree边界不变。

证据入口：[cohort terminal](AG7_COHORT_TERMINAL.json)、[ledger](AG7_BUDGET_LEDGER.json)、[per-start references](PER_START_EVIDENCE.json)、[accepted metrics](ACCEPTED_METRICS.json)。无raw stdout/maps/jsonl/trace/二进制进入Git。远端最终HEAD/tree/blob回读由root在提交后另行记录。
