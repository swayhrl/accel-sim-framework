# DTC-L1 Main：科学审查接受与上下文同步

## 1. 本次任务

作为唯一的 **DTC-L1 Main**（本机 API 会话“DTC-L1交接-1”），接收科学窗口对本轮 CORE32 Controlled Oracle 的正式审查意见，前向更新项目上下文，并给出一次简短接收回执。

本次是已完成审查的接收和文档同步，不是新一轮Main收尾，也不是结构实现或科学执行Goal。用户已同意科学审查意见，并要求通过固定GitHub资料交互；按用户转交的完整commit SHA读取本目录。

## 2. 固定资料与目录

- Repository：`swayhrl/accel-sim-framework`。
- 接受包路径：`docs/dtc_l1/review_packs/CORE32_ORACLE_SCIENTIFIC_ACCEPTANCE_20261109_V1/`。
- 接受包固定commit：采用用户本次转交指令中明确给出的完整SHA。不要自行用分支HEAD替换。
- 正式科学包基线：`b9ff89f00ea8ff889e4189136501c714c5d7e345`。
- 运行结果固定提交：`7ffcca7f908a21f45ba1a6ebb3b335ff962f97df`。
- 完整工程交接：`3f0036f2868e20a8d9a4b6244c7c74d940954188`。
- 项目目录：`D:/Codex/Token-API/workspaces/DTC-L1/`。
- 应更新文件：`D:/Codex/Token-API/workspaces/DTC-L1/CONTEXT.md`。
- 本次本地接收回执：项目 `deliveries/CORE32_ORACLE_SCIENTIFIC_ACCEPTANCE_20261109_V1/MAIN_ACCEPTANCE_RECEIPT.md`。

若本机已有上述项目上下文，读取后合并，保留无关内容和历史来源。若实际工作区入口不同，使用已确认的本项目入口并在回执说明；不要创建第二份互相竞争的项目上下文。

## 3. 执行步骤

1. 从用户给定的固定commit读取本目录 `MANIFEST.json`、`README.md`、本指令、`CONTEXT_INCREMENT.md`、`REVIEW_DECISION.json`和完整 `SCIENTIFIC_REVIEW_RECEIPT.txt`。
2. 对本目录manifest列出的九个小型成员核bytes/SHA256。其余JSON作为已有审查回执保存或引用即可，不重新运行128格连接、GM复算或D级raw审计。manifest自身以本次固定Git commit/blob身份绑定。
3. 接收 `ACCEPT_SCOPED_CLOSEOUT` / `CLOSED_ACCEPTED_WITHIN_DECLARED_TRACE_SCOPE`：只关闭本轮Controlled Oracle Goal，不表示DTC-L1研究结束。接受Main总签署与当前STOP。
4. 将 `CONTEXT_INCREMENT.md` 前向合并到项目 `CONTEXT.md`，记录本接受包的完整commit、固定路径及本次接收结果。默认执行端统一为DTC-L1 Main；旧账户Main只供历史查询。旧“独审待完成”“旧Main继续收尾”等当前状态应标为已被后续固定证据取代，历史记录本身保留。
5. 将结构排序、20格发现集的解释范围、有限机制准入要求和后续独立资格记录为 **待明确任务/授权**。此前机制选型文件和CPU原型建议不能因读取本包自动激活。
6. 写一份简短本地接收回执，并在当前API会话返回摘要，然后STOP。无需为这次接收再次合并整个审查分支、改写远端原包或开启新的发布循环。

## 4. 允许动作与停止边界

允许：只读GitHub固定小包、计算其manifest的bytes/SHA、合并本项目CONTEXT.md、保存本地接收回执、在当前API会话报告结果。普通本地读取、路径和文档合并问题可自行处理。

本条不授权：

- 新机制源码实现、编译资格、CPU原型或安全fixture执行；
- 任何新模拟、request、预算消费、GPU采集、新输入、20格或44格执行；
- 重跑128格、全量raw/trace/归档重审、为了换执行端重做已通过验证；
- 查询或干预174/164/109活动进程、raw、锁、registry、旧RUNNING/blocked字段、只读publisher或其他项目服务；
- 解除Tag/HOLD、覆盖历史失败/负例、修改D/M冻结回执、原RESULT或b9正式包；
- 改写生产Core、原Source或英文LaTeX v0.23。

若仅本次小包出现缺文件、SHA不一致或当前本地上下文存在直接冲突，在回执报告具体项并保留现状；不要自行升级成模型补跑或重新审计。

## 5. 接收回执要求

回执应简短列明：

1. `accepted_review_commit`：实际读取的本接受包完整SHA。
2. `review_manifest_check`：九个成员的核验结果，若失败列具体路径。
3. `scientific_goal_status`：本轮Controlled Oracle固定trace范围接受关闭；项目研究继续。
4. `main_route`：DTC-L1 Main为唯一后续执行端，旧账户Main仅历史查询。
5. `context_updated_path`及本次更新内容摘要；只有实际写入成功才称已更新。
6. `new_simulations=0`、`new_requests=0`、`budget_consumed=0`、`gpu_capture=0`、`candidate_implementation=0`。
7. `next_state=STOP_WAITING_FOR_EXPLICIT_NEXT_TASK`。

不重新报告所有32个应用的结果，不要求再写一份Main最终科学包。等待用户明确转交下一条任务。
