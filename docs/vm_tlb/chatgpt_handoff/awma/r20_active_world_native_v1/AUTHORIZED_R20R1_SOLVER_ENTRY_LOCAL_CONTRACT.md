# R20R1授权与续跑入口

日期：2026-10-01。用户已批准。状态：AUTHORIZED_NOT_STARTED_BY_CHATGPT。

本文件更新`STATUS_AFTER_R20_NUMERICAL_STOP.md`的“待授权”状态，不改写R20原始数值资格失败，也不恢复32步物理轨迹性能合同。

## 最新执行入口

- scientific parent：`50f8608898ec37a7e265bf3761d7bb236cdb3e88`
- parent tree：`9807e998d9d868c283fe42b825cbce74fd6c494d`
- handoff branch：`hrl/awma-r20r1-solver-entry-local-contract-handoff-v1`
- execution branch：`hrl/awma-r20r1-solver-entry-local-contract-109-v1`
- 起始HEAD：`72215894add10b96dc0274c98f6e8b265219eac3`
- 起始tree：`8ca907f253944a5e0ec3f0d251df06418be16e62`
- stage：`AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1`
- 目录：`docs/vm_tlb/chatgpt_handoff/awma/r20r1_solver_entry_local_contract_v1/`
- 必读：`START_HERE.md`及`LANE_F_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_GOAL.md`。

## 本轮范围

Lane F/109复用原窗口。先固定真实t128 solver-entry的完整数值、EFC/J/contact顺序与实际依赖，5次B0同入口重放并加一次独立图见证。graph-local上下文需要独立审计；恢复全部Data不是scratch已闭合的证明。

若这一局部合同仍不成立，停止，不写candidate。若通过，再在事前冻结的128/136/144/152四个入口完成B0-only资格，然后只允许一个在线active-world软件诊断；全部初始化/维护/输出收尾计入完整solver边界。发现有稳定响应后才使用原封存时间窗口的固定入口，不自动进行架构或完整step推断。

不改成确定性contact/EFC算法，不放宽旧32步阈值，不重建平台、不下载新scene、不改变B/solver/精度。大状态沿用164 authority、109活跃副本，174不stage大文件。

Lane E、Lane G、174/Accel-Sim仍STOP。没有后台自动启动或新任务调度；节点需要接收续跑指令后执行。
