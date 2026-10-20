# EN-v20之外的论文措辞修订建议

本文件供作者审阅，**没有修改EN-v20原母稿**。原七输入与旧H0的身份/分母保持。

## 可直接使用的结果描述（英文）

> On the four currently accepted full-application pairs using the same main61 binary, the complete design achieves speedups of 0.502% for Conv and 0.928% for SAD, while CFD changes by −0.081% and DWT2D by −0.670%. The geometric mean over this interim four-input subset is 1.001679; the original seven-input campaign remains incomplete.

> Service reduction does not directly determine program latency. DWT2D reduces physical bank services by 13.845% and lower-read bytes by 5.575%, yet executes 1,124 GPU cycles longer. Most additional landing-wait observations occur in a kernel that becomes faster; the two main regressing kernels issue no new read-only lookups. These observations motivate controlled tests of victim lookup, retention, landing constraints, and state carried across kernels, rather than an additive stall-time explanation.

> Victim storage serves 49,962 reads in CFD and 23,305 reads in DWT2D. The read-only path avoids 51,678 and 9,965 conventional line-MSHR allocations, respectively. Neither baseline records line-MSHR-full blocking, and the corresponding application times remain nearly unchanged or regress. Activation counts establish execution of a mechanism, not its marginal critical-path benefit.

> All four complete-design runs enable tag detachment, but record zero successful detach events. Consequently, these application results do not establish a performance benefit from successful tag detachment. Read-only admission, merging, and line-MSHR bypass must be distinguished from tag detachment.

> SAD issues no victim read response and admits no read-only transaction. Its largest timing improvement precedes all counted copy operations, ruling out an explanation that attributes the entire improvement to dynamic copy elimination. W-only and victim-control comparisons are needed to distinguish organizational and timing effects.

## 条件式审校清单

以下是应避免的科学说法示例，不声称EN-v20已经包含这些原句；本文件不充当母稿逐行diff。

- “T为四应用释放Tag并获得收益” → 当前没有成功detach事件，不作此因果归因。
- “RO节省433138个MSHR，因此减少433138周期stall” → 三应用避免的line分配是事件计数；阻塞、描述符、请求、GPU时间分母不同。
- “DWT新增148372周期bank stall导致退化” → 这是非互斥请求等待和，98.9%在较快K1；landing槽位兼容性也不同于bank服务端口忙。
- “SAD的0.93%全来自copy消除” → 主要989cycles收益在零copy prefix，强于仅看总服务下降的反证。
- “四对GM代表七应用/替代旧0.16%” → 只报告明确成员的临时四对GM，七输入GM UNKNOWN；旧H0五输入另有source/问题范围。

没有重复运行或误差条数据，不使用“统计显著”“稳定加速”措辞。待E接受控制后，按准确背景报告边际差异，不把S→W→WV→F阶梯当无交互、唯一的模块分摊。
