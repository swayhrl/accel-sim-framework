# EP-L2六Lane协调协议

本协议只具体化GitHub协作，不扩大COMMON_CONTRACT中的机制或实验授权。正式目录职责沿用`project_spec/WORKFLOW_GOVERNANCE.md`：ChatGPT发布任务和研究决策，Codex提交执行报告与证据；候选完成不等于独立审查通过。

## 1. 单一入口、独立写入

协调分支`hrl/ep-l2-ft20261016-coordination-v1`由ChatGPT维护。六个Codex不得向协调分支或旧冻结分支直接push，不修改本目录的任务合同；改变合同的需求先写入本lane报告。

Lane N独占两个仓库中自己的`hrl/ep-l2-ft20261016-laneN-v1`执行分支。Lane 6仅需Framework；Lane 5只有测试确实需要Core改动时才建立Core分支。创建前检查远端是否存在以及是否已有对应活跃任务；若存在，先读取并继续，不reset、不force-push、不覆盖。历史字母lane保持其原历史含义。

Framework代码lane不得从协调分支直接认领旧submodule指针为runtime。先读取Lane 1发布的父版本合同；未发布时可从共同集成点开展独立模块和测试，但报告为待集成候选。Lane 1使用README的Core/Framework候选，核实实际匹配和静态等价。Lane 6可从本次协调提交建立文档分支。

所有worktree、build目录、运行配置、结果根隔离。不得重编译仍服务活跃实验的binary。新增机制代码默认OFF；无关项目、trace、权重和历史结果只读。

## 2. 六Lane写入边界与依赖

| Lane | 自己负责的生产/证据 | 消费者 |
|---|---|---|
| 1 | 公共allocator/handle、preview/commit、WB路径、baseline与集成 | 2/3/4/5/6 |
| 2 | TVD独立模块、最小接入patch、定向验证 | 1集成，5独立验证，6写作 |
| 3 | RO认证、事务模块、最小接入patch、定向验证 | 1集成，5独立验证，6写作 |
| 4 | ideal模式、历史复用审计、诊断配置和结果 | 1接入公共变化，5运行去重，6写作 |
| 5 | 测试、runner、host配额、run-key registry、验证与实验表 | 1/2/3/4使用配额，6消费结果 |
| 6 | 论文、图表脚本、claim map、PPA账 | ChatGPT/用户审阅 |

Lane 1是公共生产接口与正式集成的唯一合入者；2/3/4可在自己的独立分支修改必要接入点并交付patch，但不得共用可写Core工作树。不要仅为搬运文件merge整个历史分支；依据准确提交取最小变更，并记录原始生产者与实际消费版本。

启动时Lane 1优先发布接口，Lane 5优先发布host budget/registry位置；其余lane先做无依赖任务。依赖在开始消费和阶段切换时有界fetch，不做高频空轮询。仍未就绪时完成可交付部分，报告`DEPENDENCY_PENDING`及准确所需产物；不要伪造ready，也不要承诺后台继续。

## 3. 每个Lane如何报告

在自己的Framework执行分支维护：

```text
docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/laneN/STATUS.md
docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/laneN/RECEIPT.json
docs/ep_l2/review_packs/FT20261016_LANE<N>_<STAGE>_r<REV>/
```

使用阶段revision创建新review pack，不覆盖已冻结的pack/CSV。STATUS是入口不是唯一证据；RECEIPT绑定准确的生产源码、配置、binary、trace和review pack。目录内具体产物见各Goal。

STATUS最少包含：lane编号、真实node/host、worktree、Framework/Core执行分支与生产SHA、任务状态、已完成内容、正在执行内容、依赖的已核实SHA、下一个可执行动作、review pack路径。首次状态与阶段完成时提交，运行中的状态仅在有实际变化时更新。

RECEIPT建议字段：`schema_version, lane_id, task_id, coordination_commit, status, framework_branch, framework_source_commit, core_branch, core_source_commit, binary_sha256, config_sha256, trace_identity, feature_vector, ideal_vector, dependency_receipts, artifacts, validation, active_runs, blockers`。未产生的值用null或明确NOT_RUN，不用零或虚构hash。`active_runs`必须来自真实runner记录；不能根据本次发布推定存在。

先freeze代码commit，再build/run；后续证据commit记录该生产commit。不要把即将包含RECEIPT本身的未来commit SHA写进它；证据发布SHA由远端分支/提交和最终报告给出，避免自引用。

## 4. 公共接口、版本和实验证据的发布位置

Lane 1在自己的分支发布：

```text
docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1/INTERFACE_CONTRACT_V1.md
docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1/BASELINE_CONTRACT_V1.json
```

接口变更先更新合同再通知消费者；不得让2/3各造一套allocator或descriptor池。2/3/4发布READY时列出匹配的接口版本、patch顺序、定向结果和仍未覆盖的路径，不能仅写完成。

Lane 5在自己的分支发布`lane5/HOST_BUDGET.md`和`lane5/RUN_REGISTRY_SNAPSHOT.json`。实际运行锁/registry放在该文件指定的共享主机目录，Git中的snapshot不是跨主机锁。每个host都有资源配额；跨host由Lane 5分派唯一run-key/owner，其他lane不能各自认领同一任务。

没有配额或依赖版本时可继续编辑、构建与轻量定向测试，但不得私自开展多任务长模拟。历史结果只有完整身份与本轮模式相符才复用；缺索引包装可确定性重建，缺科学输入不可猜补。

## 5. 提交与回读

只stage本lane明确路径，不用`git add .`/`git add -A`。每次发布至少：检查工作树、`git diff --check`、保存source/测试/输入身份、commit、普通push、重新fetch远端并确认发布SHA。出现并发更新先读取并合并自己的改动，不强推。

大型raw日志留在实际结果根；提交路径、hash、终态和必要紧凑证据，不上传巨量日志或模型资产。未具备写权限时保留本地commit/patch并如实报告；不称已推送。

完成后给用户/ChatGPT返回：Lane编号、Framework/Core分支与提交、STATUS/RECEIPT/review pack路径、测试及实验数量、当前阻塞和下一步。ChatGPT从这些分支回读证据后更新协调入口，六个窗口不抢写一个PARALLEL_WORKBOARD。

## 6. 本次发布与后续授权

发布时六lane均为`PLANNED_NOT_STARTED`，并未在服务器发起进程。用户把启动指令交给相应Codex窗口后，各窗口按实际执行更新自己的状态。能自行解决的普通工程问题修复后继续；只有已定语义/预算变更、无法恢复的科学输入缺失等问题停下相应受影响部分。不得重启已有任务、改动其它项目或扩展未经授权的实验维度。
