# Non-executable next-cohort prerequisites

此文件是设计要求，没有命令、UUID或自动派发器。

1. 用户明确决定新的范围及实际启动预算。旧AG3/AG4等全部UUID、失败记录和封存剩余格不得恢复或挪用；新的用户答复到来前保持预算UNASSIGNED。
2. 单独审查修复后的CPU资格、生产启动策略接入和同一分派路径等价性。当前仅发布CPU guard；不得直接把CPU PASS说成已发布性能执行器。
3. 若选择复用AG3 GEMM和AG4 Gaussian，必须重新独立核定各BASE来源、完整strict、输入、Core、actual ELF/build-id/loader、全部effective options、公共统计及唯一外部runner差异。特别保留AG4资格失误及其观测边界。任何不能闭合时交用户决定完整配对范围，不能擅自追加BASE或预算。
4. 完整新cohort冻结：新UUID与顺序、一次机会、停止/失败/7200秒timeout、单worker、原K0/OO128/64×8开发stress及全部finite quota/clock；每点最多单AE或单AD；原输入完整成员SHA和命令窗口；实际运行库、loader/cache身份；runner/guard/strict SHA；统计字典/比较公式/不可用字段。Core保持`c8090115bd57512b1b23fca7d925301fa620c751`，除非用户另审。
5. 资源先恢复磁盘≥10GiB，并对所有项目重做两次≥10秒准入及PID/start_ticks、authority/FLOCK核对，保持原R2全部持续阈值。资源变化不授权删历史数据、操作外部进程或私下改门槛。
6. 科学预注册commit/push/fetch-back，核HEAD/tree/blob/clean后，才可实际启动。新的失败/STOP保留；不自动retry、不选择性补格。没有授权时不启动任何旧Goal、canary、GPU/native或trace replay。

本次询问提供的可选预算方案仍待用户明确答复；无默认选项被当作授权。磁盘当前也独立阻止完整模拟，即使之后预算获准仍须通过资源门槛。
