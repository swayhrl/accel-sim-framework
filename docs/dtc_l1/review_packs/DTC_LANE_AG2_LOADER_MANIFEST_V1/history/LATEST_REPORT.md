# AG DISCOVERY_OPT — STOP

唯一BASE_GEMM在启动身份检查时因预冻结清单遗漏非ELF的 `/etc/ld.so.cache` 被SIGTERM。已观察ELF SHA均匹配，整体身份仍失败，不追认PASS。无完成kernel，完整BASE校准未发生；后续所有格未发射，cycles/ratio均UNAVAILABLE。根因及仅CPU重放修复原型见 [ROOT_CAUSE_AND_FOLLOWUP.md](ROOT_CAUSE_AND_FOLLOWUP.md)。


新模拟实际Popen child 1；保守启动预算消耗 1/8；完整strict PASS 0。固定八格，AD两格HOLD_UNQUALIFIED，不替换、不补跑。

| 点 | 状态 | 整数cycles | arm / 本轮同输入BASE |
|---|---|---:|---:|
| BASE_GEMM | HOLD_STRICT_FAILED | UNAVAILABLE | UNAVAILABLE |
| BASE_Gaussian | NOT_STARTED_COHORT_STOP | UNAVAILABLE | UNAVAILABLE |
| AC_GEMM | NOT_STARTED_COHORT_STOP | UNAVAILABLE | UNAVAILABLE |
| AC_Gaussian | NOT_STARTED_COHORT_STOP | UNAVAILABLE | UNAVAILABLE |
| AD_GEMM | HOLD_UNQUALIFIED | UNAVAILABLE | UNAVAILABLE |
| AD_Gaussian | HOLD_UNQUALIFIED | UNAVAILABLE | UNAVAILABLE |
| AE_GEMM | NOT_STARTED_COHORT_STOP | UNAVAILABLE | UNAVAILABLE |
| AE_Gaussian | NOT_STARTED_COHORT_STOP | UNAVAILABLE | UNAVAILABLE |

Core `965dffe04366e665626de4afeb7ffebca8622b5f`；固定X2上只合入AC83aca449与AEae83cc51，AD未资格、AF排除。15/15 CTest、AE137、AC80、68个AC×AE实际LDST CPU交错、正常导出/OFF差分/全echo资格见QUALIFICATION_DECISION.json。AC额外160KiB/SM明确收费，不是equal-area。

BASE仅以本轮全输入自然exit0+strict及旧完整K0共同定义指标严格校准成立；旧T数值只作参照，不能填本轮表。两输入是发现集，不能声称独立验证或计算原GM12；host wall不推GPU性能。

AA5历史保持1/4实际启动、0/4完整strict；旧UUID d0a29a82-c171-46e4-b077-d7ccfd2c4b7a在451.4s按冻结合同因host pswpin+1page STOP，仅67/510，own majorfault0。原STOP/raw/UUID未修改、未重启，不作校准。

共同计数、PIB/physical积分、lower/L2/DRAM实际单位见COMMON_METRICS.tsv；AC真实collection/WB重叠等只列AC_ON_DIAGNOSTICS.tsv。OFF未打印、K1-only、hash set/bank直方图及逐消费者时序均UNAVAILABLE，不补零。无native值正确性结论。

资源合同AG_DISCOVERY_RESOURCE_R2_V1：单sim；孤立host-global页变化WARN并加密采样；新增OOM、最低线、持续swap/PSI仍STOP。每次新准入/全FLOCK与真实loader库身份、监测和原始失败日志保存在独立AG raw。

终态原因：`ValueError('STOP_AFTER_FAILED_ATTEMPT_STRICT_OR_BASE_CALIBRATION:BASE_GEMM')`。无重试、retune、补格或后续自动派发。

收尾：自有协调器与sim实例均不存在，AG FLOCK为0，原输出收集器保持不动；FINAL_AUTHORITY_RELEASE.json证明本轮无剩余派发。收尾IO-full30.20%/23.06%不满足下一次双样本准入，与先前身份STOP区分记录。
