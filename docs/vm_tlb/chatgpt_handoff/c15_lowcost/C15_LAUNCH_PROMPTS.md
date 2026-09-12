# C15 三窗口Goal启动指令

请在三个独立Codex窗口的Goal模式分别发送下面一段。已有旧Goal仍运行时不要混入；已完成的旧窗口可以复用会话，但必须进入新的独立worktree。三条指令只写自己的分支。

## 窗口A

```text
使用Goal模式启动 C15_A_STATIC_FINGERPRINT_AND_INTEGRATION。
仓库 swayhrl/accel-sim-framework；自己的远端分支 hrl/vm-c15-static-v0；建议worktree /workspace/worktrees/accel-sim-vm-c15-static。
先只读定位已有clone，fetch自己的分支，安全建立或复用non-detached独立worktree。不要reset/stash/切换其他窗口worktree。记录planning_sha和当前HEAD；规划来源是 hrl/vm-c15-lowcost-plan-v0。
完整阅读 docs/vm_tlb/chatgpt_handoff/c15_lowcost/ 下的 START_HERE.md、C15_AUTHORITY_AND_SCOPE.md、C15_DATA_CONTRACT.md、C15_RESOURCE_AND_RECOVERY.md、C15_STAGE_ACCEPTANCE.tsv、C15_VALIDATION_TEST_CATALOG.md、C15_BUDGET_MATRIX.tsv、C15_REFERENCE_ANCHORS.tsv，随后完整阅读 C15_LANE_A_GOAL.md。
连续执行自己的C15-0/C15-1小阶段，先发布资产和bootstrap清单，再完成8–12配置的有来源静态表征；配置数不是模型数。读取config/index/Safetensors header，不下载完整权重、不启动GPU或模拟器。
自己工作完成后只读fetch B分支 hrl/vm-c15-native-capture-v0 和 C分支 hrl/vm-c15-sampling-validation-v0 的已提交发布manifest，核SHA并在A自己的integration目录完成C15-5汇总。不修改或merge其他窗口分支，不消费live partial。
每阶段按stage/test合同出receipt；未知字段不补0；能力缺口继续独立工作；普通路径/解析/依赖问题主动解决。元数据不足不虚构模型，动态缺口不伪装跨模型验证。工具完成和科学准确性通过分开。
不必各阶段等用户确认，不新增完整SASS/Accel-Sim/Core改动/租机/权重下载。按预算和resource policy执行，合理权限需平台批准，不能绕过。
及时commit/push自己的分支；最后给来源、阶段状态、主要结论、费用和缺口。目标 C15_A_STATIC_AND_INTEGRATION_READY_FOR_REVIEW；能力不足用明确的CAPABILITY_LIMITED或PARTIAL状态，不假装整体通过。
```

## 窗口B

```text
使用Goal模式启动 C15_B_NATIVE_CENSUS_AND_BOUNDED_CAPTURE。
仓库 swayhrl/accel-sim-framework；自己的远端分支 hrl/vm-c15-native-capture-v0；建议worktree /workspace/worktrees/accel-sim-vm-c15-native。
先只读定位clone，fetch自己的分支，安全建立或续用独立non-detached worktree，记录planning_sha/HEAD。不得进入A/C或旧C12–C14 worktree修改文件。
完整阅读 docs/vm_tlb/chatgpt_handoff/c15_lowcost/ 下的 START_HERE.md、C15_AUTHORITY_AND_SCOPE.md、C15_DATA_CONTRACT.md、C15_RESOURCE_AND_RECOVERY.md、C15_STAGE_ACCEPTANCE.tsv、C15_VALIDATION_TEST_CATALOG.md、C15_BUDGET_MATRIX.tsv、C15_REFERENCE_ANCHORS.tsv，再读 C15_LANE_B_GOAL.md 和 fixtures/contract_examples.json。
立即做真实GPU/模型/工具能力盘点，不等A/C全部完成。先小canary，再原生无profile重复、轻量目录和storage/generation寿命V2；只有可访问且已授权GPU、本地完整模型和后端支持时运行真实native。无GPU时完成importer、fixture、dry-run和历史header-only目录，不把合成/CPU结果当native。
最多3个真实部署，每部署最多8个轻量scenario，先一个短scenario验证。profiling开销单独测；shape/stack只在独立标记pass。原生目录可完整列kernel，但不生成全模型SASS。
使用C已发布selector；未发布时按handoff规定先2–4个bootstrap窗口。capture必须两遍身份核验，过滤canary通过后才运行；最多12窗口/部署、单次4GiB/20min、总trace/profile32GiB、累计4 GPU-active hours；每GPU一个采集器且C15总GPU并发1。到限保留partial，不自行扩预算。
不启动任何Accel-Sim/GPGPU-Sim replay或新Core build，不下载完整权重、不租机、不动共享环境、不接受新条款。普通错误主动修复，资源缺口不终止可行离线工作。
提前发布目录checkpoint给C；每窗口保存hash/sidecar/terminal/cost和缺口。只commit/push B分支，目标 C15_B_NATIVE_CAPTURE_READY_FOR_REVIEW；缺GPU等用CAPABILITY_LIMITED_READY_FOR_REVIEW且明确实际新动态覆盖数。
```

## 窗口C

```text
使用Goal模式启动 C15_C_SAMPLING_AND_RETROSPECTIVE_VALIDATION。
仓库 swayhrl/accel-sim-framework；自己的远端分支 hrl/vm-c15-sampling-validation-v0；建议worktree /workspace/worktrees/accel-sim-vm-c15-sampling。
先定位clone，fetch自己的分支，安全建立或续用独立non-detached worktree，记录planning_sha/HEAD。旧C12/C13/C14/Operator-aware只读，不改变其代码、raw logs、trace、config、Core或已接受标签。
完整阅读 docs/vm_tlb/chatgpt_handoff/c15_lowcost/ 的 START_HERE.md、C15_AUTHORITY_AND_SCOPE.md、C15_DATA_CONTRACT.md、C15_RESOURCE_AND_RECOVERY.md、C15_STAGE_ACCEPTANCE.tsv、C15_VALIDATION_TEST_CATALOG.md、C15_REFERENCE_ANCHORS.tsv、C15_BUDGET_MATRIX.tsv，再读 C15_LANE_C_GOAL.md 和 fixtures/contract_examples.json。
不要等待新模型或GPU。从固定C12/Operator-aware/corrected C13/C14资料开始，复用既有scan和精确per-kernel解析器，但所有派生结果写C15私有目录。先无采样守恒control，再建立cheap-feature选择器与页/行指纹；提前发布selector接口给B。
执行已规定三类分层策略和virtual budgets，freeze seed/split/指标/阈值。不能用候选机制speedup挑primary样本；使用完整模拟/完整trace特征的策略单列oracle并计成本。C13已被分析过，只称回溯跨配置测试，不称新盲测。
区分represented与actually sampled覆盖；unique页用并集，rate先聚合分子分母，CTA文件顺序不当全GPU访存顺序。累计translation等待不称隐藏率或全局critical path。
完成C15-4全部回测：原始计数和率误差、机制成对delta/sign、小收益INCONCLUSIVE、cold/context偏差、sketch精度、完整费用。没有新模拟授权，不为补context表启动simulator。未达精度保留SAMPLER_NOT_QUALIFIED，不调整阈值凑PASS。
在B发布后只读导入少量新真实目录/窗口；没有则明确动态跨模型待补，不阻塞历史校准。最后最多提出3个未来高保真申请，不执行。
所有小阶段有test receipt和明确状态，普通工程问题主动解决并连续推进。只commit/push C分支，目标 C15_C_SAMPLING_VALIDATION_READY_FOR_REVIEW；能力缺口/未知数据真实报告。
```
