# AG5 CPU repair: retired PID dispatch

本包响应“其他为什么不启动，能启动吗？有问题能修复就修复”。结论见 [LATEST_REPORT.md](LATEST_REPORT.md)。这是独立CPU修复工作，不增加模拟预算，不恢复任何旧Goal、UUID或dispatcher。

Framework分支：`hrl/iscas2027-dtc-lane-ag5-retired-pid-repair-174-v1`，固定父提交 `d8d0401dab0a1d9cb949302bcc05148328421cc2`。

原174独立根：`/workspace/dtc-lane-ag5-retired-pid-repair-174-v1/`。原始CPU maps和日志留本地；Git只发布源码、小型收据和索引。Core只读，无GPU/完整模拟/trace replay。

入口：`FINAL_CPU_QUALIFICATION_DECISION.json`、`ROOT_CAUSE_FIXED_BOUNDARY.md`、`PRODUCTION_DISPATCH_GENERATION_TESTS.json`、`SOURCE_AND_SHA_BINDING.json`、`NO_SIMULATOR_STARTS.json`、`NEW_COHORT_PRE_REG_PREREQUISITES.md`。
