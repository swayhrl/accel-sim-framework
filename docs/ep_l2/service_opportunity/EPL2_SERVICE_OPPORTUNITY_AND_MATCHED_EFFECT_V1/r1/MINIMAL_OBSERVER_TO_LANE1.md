# Lane1最小观测接口：MQ2 / RG1

Authority: Framework `c8aa87bdbe220853eb2d27d8babd448cff02a66e` §2–4. 本文件是接口请求，不是已实现observer、producer资格或新增实验授权。仅复用Lane1生产小case；Lane3未创建新C++构建、应用或观察框架。不交给Lane2插入performance任务。

现有 `bank_block` 混合frontend/copy/lower-WB拒绝；`bank_wait_cycles` 是各logical op首次conflict至消费的间隔之和，`bank_retry_attempts` 是调用次数。它们既没有消费者ready原因，也没有MissQ第二项身份。`EPL2B0V1` 5000-cycle窗口只有占用均值与bank累计差，不能复原同周期的机会。代表raw未输出M0/L2CHAR专用frontend/lower-drain记录，缺失字段为null。

## MQ2：复用真实队头尝试的结果，不多调用一次bank request

在 `baseline_cache::cycle` 的原head决策处，提供只读二项窗口视图；在 `l2_cache::lower_ready` 的真实WB bank尝试返回后关联其拒绝原因。observer不能为看计数额外调用 `lower_ready/request`，不能消费或撤销物理服务。

每slice按physical GPU cycle去重的计数：

| 字段 | 定义/单位 |
|---|---|
| `mq2_head_wb_lower_open_bank_denied` | 实际head是L2_WRBK、相应packet下游可接收、此次真实bank请求被拒绝的slice-cycles |
| `mq2_safe_second_opportunity` | 上述条件且第二项普通demand read、不同128B line、packet下游可接收、原请求/输入足以证明无atomic/fence/volatile/acquire/release等顺序限制；计slice-cycles |
| `mq2_second_exclusion[reason]` | 同line、非普通read、未知/不安全顺序、第二项下游full、无第二项；互斥首因编码，合计分母明确 |
| `mq2_bypass_issued` | 第二项真实lower enqueue次数；OFF必须0，ON≤safe opportunity；slice/cycle总lower enqueue仍≤1 |
| `mq2_head_recovery_wait_max` | 从原head实际恢复全部就绪到head真实enqueue的最大间隔；区分head持续不ready时间 |

最小见证只保留小case全部事件，应用最多每slice首16条；超出只计 `witness_truncated`。字段：physical_cycle、slice、head/second request UID、line、type、order-proof classification、真实lower full、head bank结果、选中项、实际enqueue。被越过WB的handle/generation/WAD/原sequence不能变化，exact-once enqueue和set_done/drain仍用现有检查。producer未定义可证明order信息时，safe机会为UNKNOWN/拒绝，不能把`!is_write()`当充分证明。

## RG1：四类真实client状态，UNKNOWN不是not-ready

只覆盖response、fill、lower-WB、frontend实际队头及其当前phase。由各真实队列/控制器提供有界的 `present, readiness={READY,BLOCKED,UNKNOWN}, block_reason, token, payload_id, generation, bank, read/write, phase, sequence`。response的ICNT full、lower-WB的实际packet memport full等非bank约束必须来自同一决策时点的真实状态。frontend需要其当前可执行copy-read/copy-write/landing-write阶段；fill不能用不存在的buffer替代真实返回队头。

`token`应是producer审定的有限client/transaction/phase身份；不能使用host pointer充当可综合硬件身份。现有(r,id,write)潜在同slot/跨generation/多client别名须由Lane1审计并计费。Lane3不在此规定超预算宽度，也不改公共arbiter。

| 字段 | 定义/单位 |
|---|---|
| `services[bank]` / `physical_cycles[bank]` | 已实际consume的RAM操作数 / 实际计时physical cycles；P1峰值≤1；host prefill不产生service；selection不等于consume |
| `held_not_ready[bank]` | 本cycle有保留身份，实际ready信息明确BLOCKED的bank-cycles |
| `held_not_ready_another_ready[bank]` | 上述同一决策时点另有同bank、全部非bank条件就绪的真实请求；UNKNOWN不计 |
| `held_not_ready_another_ready_zero_service[bank]` | 上述存在可审计见证，且完成本physical cycle全部合法phase后该bank实际services=0；这是OFF空转见证，不能用中途sample代替 |
| `recovered_grants[bank,client]` | RG1实际让其它READY请求consume、同时老请求明确BLOCKED的次数；不宣称因果上节省多少GPU cycle |
| `client_first_ready_to_consume_max`、`client_first_attempt_to_consume_max` | 按稳定token生命周期测量，单位physical cycles；ready起伏与首次attempt分别记录，不能相加为独占stall |
| `client_cancel[reason]`、`pending_token_peak/final` | 只计合法cancel/rollback、释放/复用前审计；终态pending=0，不能timeout抛弃数据 |

事件最少为 `READY_CHANGE / SELECT / CONSUME / CANCEL`，附cycle、slice、bank、client/token、generation、phase、sequence、非bank block_reason。小case记录全部；应用只保留首16个empty-service/recovered见证与每client最长等待见证，截断显式计数；不做全trace日志。

采样必须覆盖cycle首、调用前状态变化与cycle末consume结果。若真实ready同cycle改变，要在consume处重验并记录；不能把“C++尚未调用”视作BLOCKED，不逐周期清空m_granted。若需collect/arbitrate分阶段或增加register/latency，必须披露到candidate时序和成本合同。非bank资源的probe必须无副作用，未知条件保守保持原策略。

## 仅需Lane1原小case返回的核对表

| case | OFF见证 / ON检查 | 当前Lane3状态 |
|---|---|---|
| M1真实队列WB bank-denial+安全异line demand第二项 | OFF不能发第二项；MQ2准确发一次，head恢复优先、WB原年龄/handle/WAD不丢 | AWAITING_PRODUCER_CASE |
| M2同line/atomic/控制/未知ordering/第二项lower-full | 不越过、OFF/ON顺序相同；不能撤销已consume服务 | AWAITING_PRODUCER_CASE |
| G1 response被真实ICNT full挡住且held，同bank另一真实client ready | OFF完整cycle zero-service见证；RG1回收真实service，response unblocks后保留年龄 | LEGAL_PRODUCTION_WITNESS_NOT_YET_RECEIVED |
| G2 lower-WB真实lower-full；fill/frontend晚到与同cycleready变化 | 不使用调用顺序猜ready；consume≤1；无free response buffer | LEGAL_PRODUCTION_WITNESS_NOT_YET_RECEIVED |
| G3 oldREADY持续就绪、同bank竞争、partial fill/rollback/cancel/复用 | oldREADY liveness保留；request exact-once、pending drain、pin/generation正确 | AWAITING_AFFECTED_REGRESSIONS |

这些接口使“结构可能”升级为“合法生产小case已测”，仍不能直接升级为“代表应用已触发/有性能收益”。后者只由Lane5同源接受端点及同cycle见证更新。本轮RO/TVD/Ideals/atomic不继承资格。
