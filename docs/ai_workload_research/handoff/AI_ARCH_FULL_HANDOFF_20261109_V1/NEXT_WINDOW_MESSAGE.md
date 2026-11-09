请接续AI-ARCH项目，使用109节点，但本次先做CPU-only接班、独立审查和研究决策，不启动GPU或恢复旧Goal。

仓库swayhrl/accel-sim-framework。先SSH huangrulin@10.156.120.109，进入/home/huangrulin/workspace。只读fetch交接分支hrl/aiarch-new-window-handoff-109-20261109-v1，固定实际commit/tree，然后阅读：
docs/ai_workload_research/handoff/AI_ARCH_FULL_HANDOFF_20261109_V1/README.md
docs/ai_workload_research/handoff/AI_ARCH_FULL_HANDOFF_20261109_V1/AI_ARCH_FULL_HANDOFF.md
及同目录OPERATIONS_AND_ASSETS.md、AUTHORITY_INDEX.json。

最新Q1已经完整完成并STOP：
5787826ca21f7af958e6e1c1f828d62fd58a1ec4，
tree a070243a93fee5594dd88d515f08e228677ebf75。
实际完整状态、20formal、T8/T16、OFF/ON、独立camera和末态恢复都完成；当前没有GPU半成品要续跑。旧V1/R1/R2的STOP保持只读，不重新训练或重跑整个Q1。

协调分支hrl/ai-workload-research-coordination当前交接核实66b2dffc6141edf1c9f9f089091b3922556583f1，仍是Q1前快照；重新fetch核实际最新，不强行reset。先用固定结果独立复算/审查Q1的时延、输入/状态、数值边界、Host并集与GPU时钟及资源协议，再给协调更新提案和下一阶段组合决策。Q1执行侧结果待独立review，不能自动称科学审查已接受。

现有组合：Qwen成熟基点PARKED；Hybrid/KV为下一资格调查优先方向；MoE仅自然route/强软件/H200条件候选；Low-bit缺真实tensor；其它STOP不自动重开。完整资料和固定trees见交接包。

新建独立branch/worktree，不改协调分支或旧实验，不merge历史执行HEAD。普通工程问题有界连续解决，负结果保留，不放宽数值/质量门。本次允许CPU只读整理与独审提案；GPU新科学任务、下载、Profiler、模拟器、RTL及跨节点操作另需明确任务/当前资源授权。历史“资源解除”不当永久无限授权。109 GPU若未来获批仍必须原Image-Lab共同flock、预约、loaded gate和实时身份验收；不干预其它项目、不访问164。

交付独立review、协调更新提案、下一研究方向及最小可证伪合同，完成Git发布/远端commit-tree-blob核验后STOP。先报告接班核验结果和计划，不用等待我逐阶段批准已经授权的CPU整理；不要自动启动下一GPU Goal。
