# DTC-L1 evidence closure / 2026-10-19 V1

## Authority and entry

用户已批准：除DC综合外，由ChatGPT规划后续实验，以高效率并行完成，保证重要的科学与运行正确性，不为不重要的细节反复开轮。本包把该授权落实为三个独立准备工作包和一个统一执行/科学收敛入口。它不是AG4的新指令，也不修改AG4的五次上限。

**新协调Codex只读完 `START_HERE_GOAL.md` 后行动。** 并行工作包是 `COV1_GOAL.md`、`SEM1_GOAL.md`、`ROB1_GOAL.md`；共同科学与预算合同见 `MASTER_PLAN.md` 和 `PLAN_CONTRACT.json`。该计划不是已经完成的可执行预注册：精确输入、代码、有效选项、UUID和派发顺序必须在对应批次首次运行前固定。

本协调分支：`hrl/iscas2027-dtc-evidence-closure-20261019-v1`。
Framework父提交：`2f3a8c4b27780e2bf3818949a6e5356d9fd62327`。
生产Core锚点：`c8090115bd57512b1b23fca7d925301fa620c751`。
当前英文稿：本会话正式v0.17；不是本分支继承README中的v0.14-R1。本包不修改稿件，不假定v0.17已发布在某个远端论文分支。

## 当前发布快照，不是现场运行状态

本次只读取得AG4 Framework `9ece18f6fdb6de16ee95f35caa6fad1fec765fc9`。其LATEST_REPORT报告CPU归属修复与GEMM复用资格通过、五点已冻结，记录当时0/5实际启动，发布回读待完成。**不能把这条快照当作当前仍0/5，也不能因此启动或重发AG4。** 不读活动raw，不轮询活动输出。

静态发现一个直接的并行风险：该提交的 `tools/review_authority.py` 会把argv中指向其他 `/dtc_l1/` 目录的新.py/.sh脚本判为UNKNOWN_DTC_CONTROL_STOP，也会审查名字包含dtc/fast64/lane的FLOCK。CPU-only不自动等于可与冻结AG4同容器并行执行。

因此：AG4可能活动时，当前允许GitHub文档/代码准备、低压只读源码审查；不得在其可见进程命名空间启动未被原合同识别的测试、脚本调度器、full simulator或执行锁。不改名、不搬脚本路径、不修改原checker来逃避分类。已存在且明确独立的CPU环境可并行测试，但不猜连接、不迁移正式DTC执行。否则等AG4自然结束后，三个CPU工作包并行运行，新执行器统一登记其角色。**保护AG4比虚假的并行更有效率。**

## 新预算与启动状态

AG4以外，本计划设置最多32次新增完整模拟器实际启动的内部上限：主体覆盖最多16、新输入最多6、稳健性/公平对照最多6、校准或受限工程替换最多4。复用的旧完整结果不计新启动；失败/超时计数，不通过换Lane名称重置。不是要求跑满32次。新模拟仅由协调者在AG4终态、来源资格和相应预注册成立后派发。

本计划发布不等于远端Codex已启动。三个新worker和执行协调者尚无START收据；必须有实际ACK/START后才能报告RUNNING。

最终DC、工艺宏/面积/时序由用户提供；不启动EDA、不搜索旧硬件材料到无限循环。不新增K2/一般coherence、AC/AC2/AF、AE+AD、现代DTC或旧Goal重启。

## 固定来源

- AG3终态：Framework `2f3a8c4b27780e2bf3818949a6e5356d9fd62327`，`docs/dtc_l1/review_packs/DTC_LANE_AG3_AE_AD_SCREEN_V1/`。
- AG4本次只读快照：Framework `9ece18f6fdb6de16ee95f35caa6fad1fec765fc9`，`docs/dtc_l1/review_packs/DTC_LANE_AG4_AUTHORITY_AE_AD_V1/`。最终结果以以后独立读取的不可变终态提交为准。
- T发现：`f520a445436b57c0a0f2494fb858a1636f04d2bc`，`docs/dtc_l1/review_packs/DTC_TAG_PILOT_V1/`。
- U验证：`16e56912cfd02f2311a1603a29415dee829fd495`，`docs/dtc_l1/review_packs/DTC_T1C_HOLDOUT_V1/`。
- A原有限服务：`f5c37d6edcce832a72cb0830021bffa78df6cc13`，`docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/final_closure_v1/`。
- M机制：`d723784a8b897566b63113f95972f7a8d12a01ce`，`docs/dtc_l1/review_packs/DTC_MECHANISM_CPU_CONSUMER_V1/`。
- V2值层边界：`59db64ce6af73c9585e0588723325d97975c23dc`，`docs/dtc_l1/review_packs/DTC_LANE_V2_VALUE_SCOPE_V1/`。
- Y2组件资格：`d085f98c10010d641ba4cfffa1f58fb8db3b56ee`；Z2解释：`2b633a616dc59efb99973e94bdfa421e28c33fab`。这两包不自动成为新应用值验证。

所有旧成绩、失败、输入风险和原IO/OO与赵皓宇论文第4章归属保持；源资料中的历史状态不覆盖当前计划或后来正式稿。
