# Policy B 合同：DESIGN_ONLY_NOT_SAFE_FOR_PRODUCTION

本合同只授权纯 CPU/offline 原型语义审查。没有生产默认参数、dispatcher、预算分配、进程访问或信号。旧 AG6 STOP 永久不变；PolicyB 的任何输出均 `allocation=false, performance_pass=false`。通过原型测试也不等于通过真实保护器、遥测或性能验收。

## 严格准入与不可省略的安全条件

Preflight 仍须两次完整 host+cgroup R2，间隔≥10s：两范围 I/O full avg10均≤25%、memory full avg10均≤1%、host available和cgroup headroom均≥32GiB、原174/uid身份、精确当前角色与authority、OOM无新增。实际输出挂载 free必须严格>5GiB，预计写入后仍须严格>5GiB；输出device一致。原型不能仅凭一组当前PSI替代完整配对，`paired_r2`是独立可信适配器的完整证明。本轮真实 CPU 入口也使用冻结 CPUAdmission与只读authority回调，不以该原型给自身发准入。

| 冻结条件 | 保留方式与原阈值 | 原型责任边界 |
|---|---|---|
| 输出/预计增长 | free≤5GiB立即停止；预计增长后≤5GiB保守拒绝；旧64MiB expected、原stdout/stderr/evidence总量上界不隐式增加 | 原型独立检查free和expected数字，其余`disk_growth`由可信上游提供 |
| OOM | host oom_kill、cgroup oom/oom_kill变化立即停止 | `oom`谓词，缺失不是通过 |
| 内存/交换 | host或cg headroom<8GiB停止；cg swap相对baseline增长≥16MiB，三个≥10s资格点停止；host全局单页swap只作上下文 | `memory/swap`冻结状态机由上游保留，不由原型重新实现 |
| 内存 PSI | host/cg full avg10>10%，三个≥30s资格点停止 | `memory_psi_persistence`；不可把它随I/O告警一起去掉 |
| 身份/所有权/authority | PID/start_ticks/generation、完整映射/loaded-image、已证明的helpers、未知authority及异常要闭合 | `identity/authority`来自完整现行guard；sample身份连续性另检查；没有替代现行生产审计 |
| deadline/abort | 原7200s上界不增加；显式停止、信号、监控异常及非自然结束不得成为成功 | `deadline/explicit_abort`；纯函数不发信号，真实动作仍属BA dispatcher/guard |
| output device/输出限额 | 保留现行device稳定、stdout/stderr/总证据上界与预计写入检查 | `outdevice/disk_growth`，新数值不在本包定义 |

以上谓词必须全部存在且为严格bool。原型接受这些结果以验证新决策组合，**不宣称自己已经实现或验证上游安全适配器**。原生产规则未改；不能用本原型调用旧guard放行。

## Runtime I/O：替代措施而非无限告警

拟将 runtime cgroup I/O full avg10>25%作为压力告警；host I/O同样记录并保守告警。两个范围不可互换，低host读数不能覆盖cg失败。语义进展不是共享存储无害的证据。

原型明确定义三层替代：任何实测`io_impact=false`立即 `RUNTIME_STOP_SAFETY`；即使有合格进展，连续高PSI episode达到显式caller给定`max_io_warning_s`仍停止；原7200s总deadline独立保留。任一观察≤25%恢复会重置该episode，但不会重置无进展时钟或全局deadline。该保守有界fallback验证了“不是无限继续”的组合语义，**没有证据支持其生产时长或共享公平性度量**。`io_impact`目前没有真实适配器与接受阈值，因此不能生产晋升。

所有新时长均必须caller显式传入、正且有限、`illustrative=true`；代码没有生产默认。测试/回放用40/3/20/40/60秒仅为声明合成场景参数，分别对应sample gap、progress age、no-progress watchdog、long-phase grace、high-PSI episode上界，绝不构成未来运行合同或阈值放宽。

## 状态与恢复责任

| 前态/观察 | 输出 | 动作语义 |
|---|---|---|
| 未准入，任一R2/身份/预计增长/authority失败或缺失 | PRELAUNCH_HOLD | 不准启动，不消耗或创建预算；将来新鲜完整准入可重查 |
| 完整可信配对满足冻结条件 | PRELAUNCH_READY | 仅离线中间态，没有launch能力 |
| 连续、同scope的合格完成计数，PSI低且无安全问题 | RUNTIME_OBSERVING | 仅记录离线观察 |
| PSI高而语义证据有效，或已绑定合法有界phase grace未耗尽 | RUNTIME_WARNING | 受I/O fallback、no-progress和deadline同时约束 |
| 任何冻结安全失败、实际STOP/非自然结束、I/O有界fallback耗尽 | RUNTIME_STOP_SAFETY | 终态吸收；真实停机动作本轮未实现 |
| 新鲜同scope完成计数长期不变，预先批准的phase上界处理后watchdog耗尽 | RUNTIME_STOP_NOPROGRESS | 仅验证计数语义，不声称历史AE_GEMM如此 |
| 缺失/陈旧/倒退时间戳、计数重置、metric/scope不连续、identity变更、缺样、未知安全谓词 | RUNTIME_INSUFFICIENT_EVIDENCE（已知身份安全失败则STOP_SAFETY） | 保守闭合，不能把未知认作进展；已终止运行不能因后续恢复复活 |
| 自然结束且strict/runtime/input/ROI/identity/safety/no-prior-stop全部闭合 | COMPLETE_CANDIDATE | 仅候选，外部科学验收仍必需；晚到actual STOP使候选失效 |

可信语义是已完成活动lane模拟指令的coherent累计量，或同一进程下已完成CTA/唯一自然完成kernel的累计量；必须绑定启动实例、输入/ROI、metric/epoch与单调采样时间。裸cycle、OS ticks、trace消费、日志增长、已发射CTA均不可替代。原型只检查已传入record的一致性；真实producer/consumer身份桥接、序列号、epoch转换与可靠发布需要下一轮集成。

长且合法的无退休phase必须有预先审查的phase合同和有限grace。原型仅接受绑定`long_phase_contract_id`的声明场景，grace不从每次声明续租，而是从最后真实进展时刻计算。真实初始化、长kernel/内存等待phase界限尚未证明；不能因为CPU活跃无限豁免。无法界定时仍是生产阻碍，不给新数值。

## A/C对照、公平性与资格边界

A保持原三资格点STOP，保守且已实际触发，但不专属于模拟器无进展。C可以每次恢复reset和迟滞，不能解决共享scope误归因；原28条触发后全部高，不能据此发明新阈值。B将进展与安全分开，但必须实际测量共享影响并冻结所有时长/缺样动作；新cohort全臂用同一源码、同一输入/ROI与插桩，固定资源合同，禁止只接受幸存臂。

本轮不可关闭的缺口：实时进展协议、计数跨reset与取消原因、真实io_impact/fairness适配器、合法phase界限、原guard完整hook与失败动作、真实开销、一次端到端资格。下一步可推荐**另行授权opt-in源码/遥测集成和针对资格计划**；尚不能建议立即生产放行新AG6 cohort。若用户未来批准一次有界端到端运行，必须明确新预算和新UUID、执行权仍归BA，不能使用封存三个UUID，不能把资格运行伪装成不计预算canary。
