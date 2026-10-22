# 四组已接受点的detach=0归因

范围：SGEMM E051、CFD E052、DWT E053、Vector E054，同r4 binary、各自完整输入与原RO证书。Conv在本次取数中尚未独立接受，不填数。

四组共同闭合：**实际production Tag探测未产生一次RESERVATION_FAIL，因此进入relieve/detach的必要分支没有发生。** 这只说明已测路径的触发缺失，不能写成“Tag总是充足”。

| workload | RO事务 | RO接收请求 | 已探测head-cycle | 跳过head-cycle | production Tag探测次数 | production FAIL | detach |
|---|---:|---:|---:|---:|---:|---:|---:|
| sgemm | 0 | 0 | 2566806 | 105742 | 2566806 | 0 | 0 |
| cfd_097k | 51678 | 206448 | 1524394 | 218239 | 1163176 | 0 | 0 |
| dwt2d | 9965 | 39836 | 1863454 | 335584 | 1793713 | 0 | 0 |
| vectorAdd_4M | 250118 | 1000000 | 3400296 | 375000 | 831673 | 0 | 0 |

Vector新增：250,118个RO事务、749,882个合并请求、1,000,000个RO响应；831,673次production Tag探测中FAIL为0，relieve/detach均0。与CFD/DWT一样，实际RO活动存在但必要production失败触发未发生。

SGEMM另有上游闭合：RO事务为0，已观察的2,282,704个认证候选head-cycle全部为resident hit。该head域不同于2,317,312个已接受认证候选请求，二者不要求相等。

CFD/DWT分别产生51,678/9,965个RO事务。它们的零detach不是“没有RO”；实际production FAIL仍为0。两者首次sticky-reuse转移分别51,617/9,960次，但pressure-way扫描为0，不能据此把sticky reuse或no-missing写成零detach的原因。相关条件比例均NA。

容量检查：CFD在412,896个候选head中咨询206,448次；DWT在156,210个中咨询67,090次。已检查descriptor/address均无失败；未咨询部分保持NA，不解释成容量有余或阻塞。M1下传统line检查为NA，不与unobserved重复相加。

CFD的RO创建事件在物理kernel4/5阶段分别3,036/48,642；DWT的9,965个创建事件在kernel1阶段。该阶段归属是事件发生时的active-kernel状态，不是请求/被detach事务的因果kernel。SGEMM缺少已发布的逐phase数值投影，本报告保持UNKNOWN，没有重扫raw。

论文表建议采用PAPER_TABLE.csv；COUNTER_METRICS_LONG.csv保留全部212项计数的准确单位/分母/NA，PHASE_EVENT_TABLE.csv提供已发布逐phase事件。所有RO数字属于当前r4的legacy格式摘要，**不回填旧main61动态原因，不构造新S/F加速比**。

- Only four accepted newr4 fullF diagnostic points are included at this intake. Conv remains blank/pending; no unaccepted raw or process state is used.
- These are finite1168/P1 W1V1T1M1 diagnostics under exact Core9243/main d99 and each own frozen input/certificate, not newS/F performance pairs.
- The RO counts labelled legacy/oldmodel are authoritative legacy-FORMAT counters of these CURRENT r4 runs, never oldmain61 dynamic data.
- Production Tag probe invocations, observed/probed/skipped headcycles, accepted requests, transactions, mergedrequesters, wayexposures and transition counts have distinct units. Do not merge populations or force acceptedrequests=headexposures.
- Observed zero rawpressure applies to covered heads and zero productionFAIL applies to actual productionprobes; skippedfrontend rawstatus isNA. Neither proves globally abundant Tags or a hardware upper bound.
- No eligibilityway population was scanned: reuse/no_missing/eligible zeros have NA ratios, not empirical absence of those victim properties under hypothetical pressure.
- High firstreuse transitions among transaction creations are lifecycle context only, not an identified causal barrier without pressure-conditioned observations.
- Capacity notconsulted is not noeligible/full/free; lineNA is subset of unobserved. Zero failures apply only to checked predicates and exact scope.
- Physical phase is activekernel state, not requester/victim causal owner. Crossphase detach/retire counts are events, and phase livepopulation isNA. SGEMM phase numeric counts are not fabricated from singlekernel or global totals.
- No historical counters, failure/HOLD states, source qualification or campaign count is changed. E051 originalFAILED remains alongside accepted supplemental revalidation; no refund/restart.
- No capturednumeric application-output guarantee, general workload prevalence, isolatedT speedup or oldS/newF ratio follows. Original model/certificate closedworld/noaliases/nohiddenwriters/drain assumptions remain.
- Analysis is metadata-only, does not wait for D, and does not assert D consumption/ACK or schedulingGoal state.
