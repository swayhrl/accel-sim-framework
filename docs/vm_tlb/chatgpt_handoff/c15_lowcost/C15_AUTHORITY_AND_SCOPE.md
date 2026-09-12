# C15 authority, scope and workflow

Version: `C15_LOWCOST_V1`.

## 1. Authority and motivation

用户批准的设计顺序保持不变：

`元数据普查 → 原生执行轻量目录 → 语义/形状分层选样 → 有上下文的选择性采集 → 页/Cache行双尺度分析 → 误差及新颖性门控 → 少量详细模拟`。

本轮只实施到低成本表征/既有数据校准；最后一项详细模拟是未来升级能力，不在本Goal授权中。旧C14建议的5个full-ROI exposure点不自动继承到C15。

研究单位是`模型revision × 实现 × Weight/Activation/KV精度 × phase/context/batch × TP/PP/EP/rank × 数据布局`。不能把同一模型的多个配置冒充多个模型，也不能凭DeepSeek/GLM系列名推断MoE或MLA。

本包新增的是执行分工、预算、验收和失败处理，不改变已审定研究范围。参考论文只提供方法动机，其误差和加速比不成为C15已实现保证。

## 2. Frozen input roots

- Framework执行/采集代码基线：`a268aba0d01310294074ded5bb8017e2092394c0`。
- C12正式22-arm数据：同上提交中的`C12_C5_FULL_ROI_FAIR_PERFORMANCE`。
- Operator-aware及Deep Dive：`8801f2e9fea4e0df1d79853a5e4440c4da463486`。其`util/vm_tlb/analyze_c12_operator_aware.py`具有explicit-cycle和累计counter闭合检查，可在C15私有输出目录复用。
- corrected C13：`9ab1e0708af66a533d9327f35f1a3e63a34c4285`，只用`C13_EFFECTIVE_CONFIG_AUDIT`中mode=0、EQ gate后的10个accepted identities。
- C14：`d3ac4c7b12f8e9253e6d14f34e58dbf484b39a05`，只作cold-context和局部proxy边界参考。
- C12 Core参考：`swayhrl/gpgpu-sim@57bb71ecd015b6ec0ab32e45b0815e5beaf69172`，只读。

本轮不创建或修改Core分支。读其他source时记录实际commit和blob/hash，禁止把分支显示名当冻结身份。历史模式错误的C13九行全部排除；异常计入排除清单。

历史trace-list身份：Prefill 692项、SHA256 `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`；Decode1 740项、SHA256 `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`。这是列表hash，不等于所有trace文件内容hash。

## 3. Ownership

每lane仅写以下自己的namespace（小写a/b/c）：

- 代码：`util/vm_tlb/c15/lane_a/`、`lane_b/`、`lane_c/`。
- 测试：`tests/vm_tlb/c15/lane_a/`等。
- 轻量结果：`docs/vm_tlb/review_packs/C15_LOWCOST_MULTIMODEL/lane_a/`等。
- 回报：`docs/vm_tlb/codex_handoff/c15/lane_a/LATEST_REPORT.md`等。
- 大文件/缓存：私有scratch，优先`/workspace/c15-lowcost/<lane>/<run_uuid>/`。

三个lane均不得写`chatgpt_handoff/c15_lowcost/`；发现合同问题先记录`CONTRACT_ISSUES.md`，按较窄安全解释继续不受影响的工作。不要并行改公共库；需要另一lane函数时导出固定commit文件到自己的vendor目录，保留许可证/来源/hash，不在来源worktree调用会写默认输出的脚本。

A兼任只读整合者：仅写A分支的`.../lane_a/integration/`。没有第四个并行协调窗口，也不能在同一A分支开两个写者。

## 4. Publish/consume protocol

每个可消费checkpoint含：

- `PUBLISH_MANIFEST.json`：schema、planning_sha、lane、run_id、producer文件hash、输入source提交、ready stage IDs、全部发布文件SHA256及大小、证据范围、缺口。
- `STAGE_STATUS.tsv`：每个小阶段的执行状态、科学验收状态、test receipt、artifact manifest、失败/降级原因。
- `COST_LEDGER.tsv`：完整成本，不能漏掉重试、加载、预热和解析。
- `LATEST_REPORT.md`：做了什么、没做什么、最重要发现、下一依赖。

manifest不包含自身hash或未知的未来commit，避免自引用；consumer将fetch到的准确commit写入自己的`CONSUMED_INPUTS.tsv`。完成temp文件后在自己的filesystem原子rename为发布文件，commit后才允许其他lane消费。

fetch失败时可用已在本地且身份验证过的git对象先工作。禁止以未提交live partial作为正式cross-lane输入。禁止`git add .`/`git add -A`/force push；只stage明确自有路径，push自己分支，最后核验远端HEAD。

## 5. Stage semantics

`C15_STAGE_ACCEPTANCE.tsv`是小阶段清单；各lane Goal给出具体算法和测试。每阶段分开记录：

- execution：`NOT_STARTED/RUNNING/COMPLETE/WAITING_INPUT/CAPABILITY_LIMITED/FAILED`。
- validation：`PASS/FAIL/INCONCLUSIVE/NOT_APPLICABLE/NOT_EXECUTED`。

`COMPLETE + FAIL`合法：表示已完成一项证伪或准确性不达标实验。不得把不理想科学结果视为工程失败而丢弃，也不得把工具测试通过视为采样准确性通过。

缺模型、缺GPU、缺已测形状或失效权限只限制对应阶段；完成所有不依赖它的工作。单个新模型无法适配不终止整个Goal。只有关键冻结来源损坏、身份不一致无法隔离或平台明确拒绝全部必要读取，才是整体hard blocker。

## 6. Hard scientific invariants

1. 不缩hidden/head/vocab/grid冒充原模型；不同层的独立Weight不替换为反复访问同一小buffer。
2. native GPU warmup不等于simulator Cache/TLB warmup；当前没有授权状态checkpoint实现。
3. `.traceg`的CTA文件顺序不代表真实全GPU顺序；无SM映射时不能声称私有L1准确性。
4. virtual contiguous、disk offsets、modeled PA、真实物理地址分开；解析页数不是TLB working set或miss。
5. unknown保持unknown；历史KV runtime-range数据不得重标为真实语义KV访问。
6. sum kernel duration不是并发makespan；sum unique pages不是并集；rate先加分子分母。
7. requester累计等待或LDST-head proxy不是global critical path，不能计算“隐藏率”。
8. 选样不得用待测试机制收益挑点；C13已被团队分析过，称`RETROSPECTIVE_CROSS_CONFIG_TEST`而非全新盲测。
9. 首次新部署的prospective holdout先固定再查看目标结果；数据不够时明确不声称跨模型有效。
10. 所有预算、代表性误差、capture开销必须实测或明确为估计，不承诺固定几分钟或10倍加速。

## 7. Completion scope

各lane正常终态：

- `C15_A_STATIC_AND_INTEGRATION_READY_FOR_REVIEW`
- `C15_B_NATIVE_CAPTURE_READY_FOR_REVIEW`
- `C15_C_SAMPLING_VALIDATION_READY_FOR_REVIEW`

有能力缺口使用对应`..._CAPABILITY_LIMITED_READY_FOR_REVIEW`；已尽力完成主体但仅等其他lane时提交`..._INTERIM_READY_WAITING_INPUT`，不冒称整体完成。

A的集成终态：`C15_LOWCOST_FOUNDATION_READY_FOR_REVIEW`或`C15_LOWCOST_FOUNDATION_PARTIAL_READY_FOR_REVIEW`。前者要求合同/单测/资产/静态库/至少一个真实动态目录/历史校准均有可复核结果；跨模型动态结论只对真实可比的部署成立。若科学精度不达标，可完整报告为`SAMPLER_NOT_QUALIFIED`，不得把ready-for-review写成全方法已通过。

下一阶段详细回放只能输出申请：指定问题、窗口上下文、设备结构、expected information、成本上限和接受/否定准则；不得自行启动。
