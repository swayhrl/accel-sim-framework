# 174-AI-ARCH 长期上下文

更新：2026-11-09。实际本机项目根：`D:/Codex/Token-API/workspaces/174-AI-ARCH/`；本文件由174-AI-ARCH独立维护。Main的`D:/Codex/Token-API/workspaces/AI-ARCH/CONTEXT.md`由Main维护，两端聊天不会自动同步。

## 当前分工与状态

本窗口负责174-new历史AI-ARCH工作与以后用户明确指派的174节点CPU资料/源码任务。Main＝API会话`AI-ARCH交接-1`，仍负责109主线和总协调；用户已确认其正在执行`AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1`。实际启动HEAD、GPU准入、进度和formal数量未回报，不查询109或推测。Q1执行authority固定为`5787826ca21f7af958e6e1c1f828d62fd58a1ec4`，已接受独审`06355f73caaa6f38697d9acac94ac81a47c27e62`，shN CPU反事实`be7fe374c1402498eeab3d3f3be97a9eb01667ab`。shN参数与两份moments的3.379784GiB是静态内容量，不是实际峰值；没有新硬件候选已晋升。

本轮Goal `AI_ARCH_174NEW_API_TAKEOVER_CPU_ONLY_V1` 已完成节点资料核对与独立交付，结束后STOP。交接基点`308d97d76ca557d1e9750c8bb0f56aeef90cbee3`，tree`b594e1d3f42dffe8bb5b8d16160c673ec7c3ca20`；结果分支`hrl/aiarch-174new-api-takeover-receipt-20261109-v1`，报告目录`docs/ai_workload_research/handoff/AI_ARCH_174NEW_API_TAKEOVER_RESULT_20261109_V1/`。具体结果commit见本机发布回读与最终交付，不把自身commit递归嵌入Git文件。

## 节点身份与路径

受信SSH alias `hrl-174-new`实际连接`root@10.208.130.174:2239`；现场hostname`huangrulin-sshfs-174`，mount namespace`mnt:[4026535153]`。主仓库`/root/workspace/accel-sim-framework`当前是C16历史线，不能作为AI-ARCH最新科学HEAD，也不在其中checkout/reset/stash/clean。15个历史AI-ARCH独立worktree实际存在，HEAD均等于固定发布，检查时各自`git status`为空。原报告在对应工作树物化，节点对象库有15个固定tree；五项后期任务的Git receipt也在。完整逐项路径、原branch/commit/tree、审查和节点可读性见本轮`NODE_TASK_ASSET_INDEX.json`。

2026-11-09轻量资源快照：MemAvailable约205GB，2GiB swap仅余528kB，I/O pressure full avg10约14.83%，根工作盘约20.5GB可用但df百分比显示100%。这些仅为瞬时观察，不是未来任务准入预算。新任务仍从单个轻量worker起步，不复制模型、trace或raw。

## 已承接的固定证据与科学边界

固定索引共15项174-new科研任务：A4-T、A4-N、A10-T、A21、A22、A23、A30-T、A30-N、A45-S、A58、A70-N、A70-P、A73-H、A75-D、A77-S；另有`WORKFLOW_BOOTSTRAP`工作流验证。台账精确路径在交接`EVIDENCE_INDEX.json@308d97d7`与结果资产索引。早期T/N/S/H/D仅是历史逻辑Lane，不再开启竞争窗口。

- A21旧`PENDING_ASSETS`已由109 A26GR1/Q1后续证据更新；A22状态寿命映射仍是源码证据而非等待/传输实测。A45-S CAGRA仅历史提案，109后续质量NO_GO；A58的GNN条件提案经109执行后PARKED。A30-T只保留H200/SM90a条件路线，A30-N仍source-only STOP。
- A70-N/P和A75-D的零候选属于已审源范围，不能当native性能负例；A73-H待同面积功耗/PPA模型资格而PARKED。A77-S为`MODEL_AUTHORITY_NO_GO / PAIRING_NOT_ESTABLISHED`，0准入轴、0pilot，不能恢复六点扫描。AWMA仅有自身范围内翻译资格；其外部performance core完整source/binary链和与自然强native配对仍缺。
- A4-N原报告固定10,477字节全ASCII、2,334个字面问号，SHA-256`26ce76b3d1ba5beeb03ddf3439c33f96ee65282313097a8db1b050f6562ebdf3`。本轮有界查找未见可读原件/V2。保留`PARTIAL_DOCUMENT_INTEGRITY`，只使用A5独审独立可核的Si输入、NequIP配置、Sobek兼容性有限结论；不得按语境补文。
- 工作流验证记录在GitHub固定`1a7f8d5d6f01326da161f52447eee013d1a630ec`，手动模板有范围可用，旧CLI自动Skill发现未验证。174现场未定位该commit对象/工作树，不因此修CLI认证、部署hooks或长canary。

## 节点非Git原件与开放项

A70-N、A73-H、A75-D、A77-S的私有`FINAL_READBACK.json`仍在各自输出根；本轮结果Git目录`NODE_READBACKS/`保存原样小文件副本并绑定路径、字节/SHA。A75-D两份小manifest在原位且SHA匹配旧receipt；A77-S两个小manifest在原位，只作索引。A70-P`/tmp/aiarch-a70p-vlm-pipeline-174new-v1`现为空，私有readback未找到，固定Git report/receipt可用。15个历史工作树无未提交改动；一次进程cwd抽样无绑定进程，不等于证明整机无活动任务。

开放项：A4-N真实中文原件若将来有可信来源，应原样另存、绑定bytes/SHA与来源，不能覆盖损坏commit；A70-P readback缺失仅是包装证据缺口；A77实际外部core与binary现场身份仍未闭合。当前无已确认需本窗口接续的174 AI-ARCH活动任务。AWMA、C16、EP-L2、DTC-L1、VM/TLB和Image-Lab各自权限不变。

## 下次动作

收到用户/科学窗口新的具体任务后，先读本文件、本轮固定报告与资产索引，再定点读取对应原报告和最新同范围证据；确认实际工作树和未提交修改后才写新独立路径。109活动Goal与资源由Main保持唯一owner；本窗口不自动启动GPU、模拟器、模型或下一科研Goal。总协调只提交建议，由用户带回Main/科学窗口审查后选择性采纳。
