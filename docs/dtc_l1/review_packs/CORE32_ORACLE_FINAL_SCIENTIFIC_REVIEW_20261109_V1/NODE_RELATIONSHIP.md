# DTC-L1 节点、资产与证据链

本轮 Main 接班从 Windows `D:/Codex/Token-API/workspaces/DTC-L1` 发起，通过既有 `ssh hrl-174-new` 到 `root@174-new` 的 `/root/workspace`。后者是登录入口；Oracle 的实际 Core/Framework、native execution、归档和 Git 审阅工作树在各自冻结路径，不以登录目录猜科研身份。

| 节点 | 本轮角色 | 主要入口与边界 |
|---|---|---|
| Windows | API 执行与本地交接、交叉核对 | `D:/repo/artifacts/DTC_MAIN_FULL_HANDOFF_20261109_V1/` 是固定交接包的本机副本；项目 `deliveries/` 存摘要及复算回执。它不是 raw 或实际运行源。 |
| 174-new | DTC-MAIN 的 Native CPU 模拟、科学登记与当前 Main 收尾 | `/root/data/dtc_controlled_oracle_20261106_v1/initial8` 和 `/root/data/dtc_oracle_clean_successor_20261107_v1/remaining24` 是两批结果源；native science registry 位于 `/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/`。旧科学 owner 已退出，现有只读 publisher 是另一进程。 |
| 164 | true164 大资产、冻结 Source、结果归档与恢复证据 | 从 174-new 已有 `/root/share/mnt164` SSHFS 访问，源为 `admin-wcx@10.208.130.164:/home/shared`；DTC 本轮归档根是 `.../huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/`。174 的 `target_mount_path` 与 164 的 `/home/shared/huangrulin/...` 是同一归档的两种路径，不是两份实验。 |
| 109 | 已有 RTX4080/SM89 GPU 原生采集与 AI-ARCH 等研究 | 可向 DTC 提供已经验收的历史 trace/输入，但本轮 CPU-only 收尾不在 109 启动采集、不取 GPU 锁；SM89 输入不能凭同名替换本轮 SM70 冻结输入。其部分 NAS 入口经 174-new 指向同一个 164 bulk，不是两份本地备份。 |

常见来源链为“109 原生采集/热资产 → 有单独证据的 164 归档 → 174-new 按固定输入身份消费”。这条链不自动证明每个输入均完整备份或原生应用数值；本轮固定 `input_digest`、spec、result SHA、archive/native restore 指针见 `FIXED32_INPUT_AND_RESULT_INDEX.json`。`input_digest` 也不自动等于某个 trace 文件的 SHA。

174-new 的 Oracle Core 工作树在 true164 根下 `source/integration-core/`，Framework 在 `source/framework-build/`，二者冻结为 `e6b41aba...` 与 `02775fd7...`。既有 `review-worktree/` 分支为 `DTC_CONTROLLED_ORACLE_IMPLEMENTATION_EXECUTION_V1`，默认 index 有预存 staged deletions；Main 新报告使用 `/root/data/dtc_core32_oracle_main_closeout_20261109_v1` 的独立分支 `dtc/core32-oracle-main-closeout-20261109-v1`。GitHub 固定 commit 保存小型审阅包，不能替代 164 上的 raw、Trace、build 或 source/native restore。

接班时现场核得 `/root/data` 可用约 20 GiB、164 挂载可用约 39 TiB；这是时间点观察，当前无新模拟准入。native registry 的两请求分别 32/32 和 96/96 已消费、remaining 都为 0，字段 `state=RUNNING` 是旧静态状态；`SHARED_POOL_EXECUTION_TERMINAL.json` 及 D 终审证明模型终结。PID 525725 不存在；PID 660465 对应原只读 publisher，原位保留。EP-L2 与 DTC 共享 174/164/native 设施但科学身份、预算和结果互不借用；109 的 AI-ARCH/采集资源也不因本接班转移。
