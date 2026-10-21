# E2五组同新binary容量诊断：最终回执

五组全部CURRENT_ACCEPTED，十端真实native exit/wait0、完整输入指令、64slice与资源退尽通过独立终验；原唯一控制器STOPPED，原PID/collector/native均已退出。新增完整应用严格10次，历史累计46次，未退款或自动追加。原T0、36次历史、32行及各桶、contingency8/8与FAILED/INCOMPLETE/HOLD完整保留。

|Workload|OFF cycles|ON cycles|OFF/ON|状态|
|---|---:|---:|---:|---|
|convolutionSeparable|292,932|268,117|1.092553×|CURRENT_ACCEPTED|
|cfd_097k|79,093|79,742|0.991861×|CURRENT_ACCEPTED|
|dwt2d|166,519|157,034|1.060401×|CURRENT_ACCEPTED|
|sad|110,773|110,634|1.001256×|CURRENT_ACCEPTED|
|vectorAdd_4M|73,696|42,788|1.722352×|CURRENT_ACCEPTED|

冻结main SHA256：`93a9f28ddb9c0c9ceb93409764a5664666589477778fe5d41d90a179704706eb`；Core `fe7e1fc1e8f40b5c4c6d0f232a528483891389c5`。全部OFF/ON由该新binary实际运行，没有借旧main61 S锚或继承其runtime资格。source/build/archive/native/input/配置链详见FINAL_RECEIPT和完成审查。

累计结果生成：new 6,899,258,320B / 10,737,418,240B；old+new 21,208,834,704B / 25,769,803,776B。迁移未重置历史生成量。最终workspace可用 18,959,142,912B，保留5GiB底线和2GiB监控余量；E active runs/leases均0。数值次数/时间上限此前按用户批准取消，但不授权任何未登记新科学条件或自动重试。

本组是联合大容量+L2 data-service诊断，原MAIN分母不变。所有ON的MissQ完整full-check覆盖缺口仍使分类为UNKNOWN，不标near-unbounded、无限容量或硬件P1吞吐上界。CFD变慢649cycles保留；不能把效果拆成capacity-only因果。

各对已在接收后立即推送/远端回读并投D原三通道；Conv接收提交6a6fd10a，控制器最终提交4146ea83。D下一步只增量Conv并汇总五组，复用已消费四组缓存；没有把投递冒充D已消费。

[独立完成审查](completion_audit_r1/AUDIT.json)、[完整最终回执](FINAL_RECEIPT.json)、[资源账](FINAL_RESOURCE_LEDGER.json)、[配对CSV](FINAL_ACCEPTED_PAIRS.csv)。后续FWT/SGEMM只完成准备交付，仍需E2准确资格/范围与单独运行批准；BFS缺件、Hotspot备用，不自动启动。
