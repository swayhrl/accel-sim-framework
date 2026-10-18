# AG DISCOVERY_OPT — CPU_QUALIFIED_PREREGISTRATION_NOT_YET_EXECUTED

新模拟实际Popen child 0；保守启动预算消耗 0/8；完整strict PASS 0。固定八格，AD两格HOLD_UNQUALIFIED，不替换、不补跑。

| 点 | 状态 | 整数cycles | arm / 本轮同输入BASE |
|---|---|---:|---:|
| BASE_GEMM | NOT_STARTED | UNAVAILABLE | UNAVAILABLE |
| BASE_Gaussian | NOT_STARTED | UNAVAILABLE | UNAVAILABLE |
| AC_GEMM | NOT_STARTED | UNAVAILABLE | UNAVAILABLE |
| AC_Gaussian | NOT_STARTED | UNAVAILABLE | UNAVAILABLE |
| AD_GEMM | HOLD_UNQUALIFIED | UNAVAILABLE | UNAVAILABLE |
| AD_Gaussian | HOLD_UNQUALIFIED | UNAVAILABLE | UNAVAILABLE |
| AE_GEMM | NOT_STARTED | UNAVAILABLE | UNAVAILABLE |
| AE_Gaussian | NOT_STARTED | UNAVAILABLE | UNAVAILABLE |

Core `965dffe04366e665626de4afeb7ffebca8622b5f`；固定X2上只合入AC83aca449与AEae83cc51，AD未资格、AF排除。15/15 CTest、AE137、AC80、68个AC×AE实际LDST CPU交错、正常导出/OFF差分/全echo资格见QUALIFICATION_DECISION.json。AC额外160KiB/SM明确收费，不是equal-area。

BASE仅以本轮全输入自然exit0+strict及旧完整K0共同定义指标严格校准成立；旧T数值只作参照，不能填本轮表。两输入是发现集，不能声称独立验证或计算原GM12；host wall不推GPU性能。

AA5历史保持1/4实际启动、0/4完整strict；旧UUID d0a29a82-c171-46e4-b077-d7ccfd2c4b7a在451.4s按冻结合同因host pswpin+1page STOP，仅67/510，own majorfault0。原STOP/raw/UUID未修改、未重启，不作校准。

共同计数、PIB/physical积分、lower/L2/DRAM实际单位见COMMON_METRICS.tsv；AC真实collection/WB重叠等只列AC_ON_DIAGNOSTICS.tsv。OFF未打印、K1-only、hash set/bank直方图及逐消费者时序均UNAVAILABLE，不补零。无native值正确性结论。

资源合同AG_DISCOVERY_RESOURCE_R2_V1：单sim；孤立host-global页变化WARN并加密采样；新增OOM、最低线、持续swap/PSI仍STOP。每次新准入/全FLOCK与真实loader库身份、监测和原始失败日志保存在独立AG raw。

完整预注册push/fetch-back及每次新准入是发射前提；本CPU审查状态本身不表示已执行性能。
