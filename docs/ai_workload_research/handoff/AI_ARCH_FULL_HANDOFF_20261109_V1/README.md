[Single complete handoff document](AI_ARCH_COMPLETE_HANDOFF_SINGLE_DOCUMENT.md): includes research handoff, full operations/assets, 42 authorities, new-window message and coordination proposal. Other files provide the same material in smaller sections.

# AI-ARCH 全项目交接入口｜2026-11-09 V1

适用对象：完全没有本聊天上下文的新窗口。交接时没有本窗口仍在执行的Goal、GPU任务或待接管后台进程。不要恢复旧进程。

**先读 [AI_ARCH_FULL_HANDOFF.md](AI_ARCH_FULL_HANDOFF.md)**。这是完整主文档，包含项目目标、研究组合、最新结论、历史边界与首次接班任务。

随后按需读：
1. [OPERATIONS_AND_ASSETS.md](OPERATIONS_AND_ASSETS.md)：109、Git、私有状态、工具与安全运行要求。
2. [AUTHORITY_INDEX.json](AUTHORITY_INDEX.json)：42个固定commit/tree；Git身份已核实，存在不等于独立科学审查通过。
3. [Q1_FIXED_FILE_INDEX.json](Q1_FIXED_FILE_INDEX.json)：最新Q1的90个公开文件精确入口。
4. [CURRENT_STATE_UPDATE_PROPOSAL.md](CURRENT_STATE_UPDATE_PROPOSAL.md)：协调层滞后修正提案；本交接未修改协调分支。
5. [NEXT_WINDOW_MESSAGE.md](NEXT_WINDOW_MESSAGE.md)：可直接派发的新窗口消息模板。

本包基于最新Q1 5787826ca21f7af958e6e1c1f828d62fd58a1ec4，tree a070243a93fee5594dd88d515f08e228677ebf75。
只读fetch核实协调HEAD仍66b2dffc6141edf1c9f9f089091b3922556583f1，tree c9491cbc37d41c2155218763bf215615ef72b39b。

交接分支hrl/aiarch-new-window-handoff-109-20261109-v1；最终本包commit/tree由发布收据和交接消息提供，避免文档自引用hash循环。新窗口fetch时重新记录实际HEAD，发生变化先读diff，不强行reset。

本包不复制数百份历史raw或19.5GB私有状态，不包含admin token、凭据或私有环境变量。原始资料通过固定commit和SHA索引定位。本次没有GPU/CUDA初始化、取锁、Profiler、模型推理/训练、下载依赖或访问164。
