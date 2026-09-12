# C14 acceptance and handoff

## 1. Branch/worktree isolation

PASS only if：

- Framework changes only on `hrl/vm-m4b-c14-dual-path-explore-v0`；
- Path P Core changes only on `hrl/vm-m4b-c14-segment-positive-v0`；
- Path N Core changes only on `hrl/vm-m4b-c14-criticality-v0`；
- C13/C12/operator-aware worktrees remain read-only；
- no C13 raw log/output directory is reused。

## 2. Instrumentation acceptance

Path P / N instrumentation均必须：

- default-off；
- default-off build能通过；
- instrumentation-on有明确enable option；
- deterministic test证明开启instrumentation不改变模拟cycles/timing；
- counter定义、unit、scope写清；
- cumulative/gauge分开；
- per-kernel累计字段若用于归因必须连续且守恒。

若无法证明non-perturbing，不得把该instrumentation用于机制结论。

## 3. Prototype acceptance

Path P最多两个prototype。一个prototype只有同时满足：

- config-gated/default-off；
- correctness fallback完整；
- unit/deterministic tests PASS；
- no stale completion / duplicate completion；
- translation/PTE conservation PASS；
- microdiagnostic输出独立；

才可标`PROTOTYPE_READY_FOR_MICRODIAGNOSTIC`。

Prototype micro performance只能标`EXPLORATORY_MICRODIAGNOSTIC`。

## 4. Microdiagnostic provenance

每个micro point必须保存轻量receipt：

- source branch/commit；
- binary SHA；
- config SHA；
- trace list/window SHA；
- original trace source；
- resolved compute indices；
- effective geometry；
- raw log SHA；
- terminal status；
- marker count；
- evidence label。

如果单kernel/window replay改变了原full-ROI warm state，必须在结果里显式写：

`STATE_CONTEXT_NOT_FULL_ROI_EQUIVALENT`

不得用micro speedup预测full-ROI加速比。

## 5. C13 dependency classification

C14 final报告必须给出一个二维矩阵：

- corrected C13 Segment：SUPPORTED / FRAGILE / NEGATIVE / PENDING
- Path P：GO / CONDITIONAL / NO_GO
- Path N：GO / CONDITIONAL / NO_GO

并给出四种组合下的下一步：

1. C13支持Segment + P GO：优先正式评估P prototype；
2. C13支持Segment + P NO_GO：保留Segment baseline，转N解释criticality；
3. C13 fragile/negative + N GO：转criticality-aware主线；
4. 两边都NO_GO：停止扩机制，回到characterization/其他translation方向。

## 6. Required final synthesis

`FINAL_REPORT.md`必须回答：

- 当前Segment path上是否存在可消除的冗余translation工作；
- 当前requester latency中有多少是可能隐藏的、多少有暴露stall信号；
- 哪条路线更有机会解释C12“slow-path大幅减少但speedup很小”；
- 哪个prototype/instrumentation已经做到代码级可验证；
- C13最新checkpoint是否改变判断；
- 下一步最多3个full-ROI实验，各自要回答什么、需要哪些arms、预计时间/资源。

## 7. Git discipline

禁止：

- `git add .`
- `git add -A`
- commit trace/raw log/build products

只stage明确的source/test/script/lightweight docs/results。

三个branch分别commit/push。handoff必须写明各branch最终SHA。

## 8. Final status

成功：

`C14_DUAL_PATH_EXPLORATION_COMPLETE_READY_FOR_REVIEW`

允许单Path：

`PATH_P_NO_GO_WITH_EVIDENCE`

或

`PATH_N_NO_GO_WITH_EVIDENCE`

但另一个Path应继续。

用户约4小时不在线；普通问题自行解决并继续，阶段性checkpoint可以commit/push，不等待确认。