# AWMA R20R1｜真实solver入口的局部数值合同

日期：2026-10-01。用户已批准。状态：AUTHORIZED_NOT_STARTED_BY_CHATGPT。

## 执行边界

Lane F / node109 / RTX4080复用原窗口，为唯一执行者。Lane E与Lane G继续STOP。174-new不启动新任务；Accel-Sim、NVBit、SASS、硬件设计均未授权。

Handoff branch：`hrl/awma-r20r1-solver-entry-local-contract-handoff-v1`
Execution branch：`hrl/awma-r20r1-solver-entry-local-contract-109-v1`
Stage：`AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1`
Scientific parent：`50f8608898ec37a7e265bf3761d7bb236cdb3e88`
Parent tree：`9807e998d9d868c283fe42b825cbce74fd6c494d`
Review/design authority：`4adb3b95039c8a8851f69ec1be944315d301e962`中的`docs/vm_tlb/chatgpt_handoff/awma/r20_active_world_native_v1/STATUS_AFTER_R20_NUMERICAL_STOP.md`。

本轮新授权覆盖上述status中的“尚未授权”，但不改写R20原32步数值gate失败，不恢复原32步B0/S1性能合同。

## 只回答一个问题

固定真实G1回放生成的完整solver-entry，保留其真实contact/EFC顺序和数值，能否建立有判别力的单次solver数值合同？先做这一资格；失败即STOP，不写candidate。通过后才允许一个局部、在线active-world软件诊断，计时边界仍为完整`solver.solve(m,d)`，不是物理step或RL训练。

数值资格前不需要候选，不重新构造确定性碰撞管线，不以更宽的32步误差容差绕过原STOP。

## 阅读顺序

1. 本文件。
2. Parent review pack中的`FINAL_DECISION.md`、`STATE_AND_NUMERICAL_QUALIFICATION.md`、`BASELINE_ONE_STEP_CAUSAL_DIAGNOSTIC.json`、`RUN_COMMANDS.md`。
3. 本目录`LANE_F_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_GOAL.md`。

复用parent的`util/vm_tlb/awma/r20_active_world/`工具、隔离环境、scene、控制、状态文件和publisher。无需重新读所有历史轮次或重做平台/大传输canary。

## 核查依据与新增设计分开

**Parent观测：**32步B0轨迹不可重复；单步的语义contact/constraint多重集合相同、池化顺序不同。该多重集合检查不等于所有contact浮点参数、稀疏Jacobian和solver输入逐bit相同，也未排除graph-local scratch影响。0.3733是观察轨迹上根据solver_niter推导的结构量，不是利用率或加速上界。

**本次固定源码核读：**`google-deepmind/mujoco_warp@3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`，`mujoco_warp/_src/solver.py` blob `090061796792f4d11408eaa69b4ef3c44465c705`。`solve`依据实际SLEEP/compact等状态分支；正常路径创建SolverContext后调用`_solve`；`_solve`包含warmstart初始化、条件迭代和迭代后的约束力恢复。`solve_compact`还有gather/scatter和供integrator使用的Ma刷新。这些不能从测量边界中遗漏。

**外部一般背景：**MuJoCo官方MJWarp文档FAQ明确说明GPU执行可能因非确定性原子操作产生顺序和小数值差异，见https://mujoco.readthedocs.io/en/latest/mjwarp/ （2026-10-01查询）。这不是本轮漂移根因已证明，也不保证固定输入后的solver一定确定。

**本轮设计：**从真实调用边界保存输入，而不排序或重新计算一个更方便的问题；检验完整solver重复性，再决定是否值得实施一个在线诊断。

## 资源与发布

所有CUDA初始化、JIT、capture、replay与profiling须持有`/data/c16/locks/c16_gpu_campaign.lock`。CPU准备/分析可以并行，GPU计时串行，不抢占其它campaign。

164保留authority；109保留活跃副本；不在174本地stage大状态。只发布新状态/差分，parent已有哈希证据按引用复用，不重新建设data-plane。

最终commit/push/fetch-back与tree核验，退出本轮GPU进程、释放锁、worktree clean后STOP。Git通道失败按既有HTTPS→HTTP/1.1→SSH→API备用链发布同一个commit，不重跑科学实验。
