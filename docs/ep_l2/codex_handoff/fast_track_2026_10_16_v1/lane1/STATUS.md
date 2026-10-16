# Lane 1 review_r5 — 独立静态缺陷已修复，R0.1仍未编译

状态 `INDEPENDENT_STATIC_BLOCKER_FIXED_R0_1_UNCOMPILED_RESOURCE_HOLD`。节点huangrulin-174；同Lane1继续原两个执行分支 `hrl/ep-l2-ft20261016-lane1-v1`，未重启Goal。已依次完整消费r4/r5，最新协调77a9fbe937ea23465cf0d0076d2df1909f52d055；原6c136e2a科学合同、资源/配置/旧结果撤回边界不变。

最新未编译Core候选 **c948184504d82b80e23eb3f4ff6cdfd328ba9355**，直接父62dc1d179b5516e68b21b695c7a9c5d0667e9671；Core执行分支发布 **57e1c363aede1a7790bdf94136d832d35ee7b34b**，tree与候选完全相同，保留原R1发布祖先但不混入其机制。最新Framework冻结build输入 **3ab150b3e99ff3ed759b8cdc5154cfb5744042a7**。准确新source覆盖此前53a/62计划身份；旧候选、旧review pack保持可回读，未覆盖旧runtime数据。

生产source/build worktree仍 `/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-r0-1`；Core仍 `/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane1-r0-1`；发布仍 `/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-r1`；正式build仍 `/workspace/build/ep-l2-ft20261016-lane1-r0-1`，不存在。没有变更生产路径/机器、降低48GiB+2GiB/64GiB/配额，也未访问164。

已交付首个r5 build入口/两修复测试/21条生产定向与发布检查审核；修复工具准确source/vendor pin、失败日志身份、floor/lease竞态等。13项最终工具检查PASS；随后只对新Core pin重验1项受影响入口测试PASS，均使用假registry/resource及小Python子进程，没有实际准入、lease或CMake。所有C++修复/回归仍NOT_COMPILED_NOT_RUN；binary=null，独立资格=false，当前正式pair=0。

首个pack推送回读时发现Lane5刚发布e8f701995a27154ffcc54cc38245dde8cd7f9bdf：20项静态审核保留19PASS/1FAIL，确定原62候选l2cache.h observer重复定义。已逐字接入其最小删除patch，结果header hash匹配；另修旧directed fixture的time比GPU clock领先一周期问题，所有直接fill/response/access与cache周期同步。新Core只改这两个文件，无生产机制/预算/config变化。Lane5原审核不是新候选资格；11门槛及五pair准备仍需重绑定准确新source/binary。later-quiescent clean prefill scope维持原62候选，不能继承早期initial-only候选PASS。

BUILD_ADMISSION_ALTERNATIVES.md r2完成Lane1/Lane5独立证据对账，精确解释历史du与文件块之和的目录块差额。历史静态分配不能证明新编译/链接/并发峰值，当前其它文件系统亦未合格；全部替代方案只供审查、没有采纳。两个已有Storage-Ops窗口继续负责空间恢复；研究Lane未删除/传输Ops或DTC-L1资产。

最近有界收尾观测UTC14:23:13：workspace38,312,300,544B（35.68GiB）、距50GiB缺15,374,790,656B；RAM159,818,186,752B，中央EP-L2活跃run/build lease0/0，7个DTC simulator只读观察。此为快照，不是未来准入许可；本revision编译/应用/实际准入尝试/源清理0，没有后台worker。

新follow-up pack `docs/ep_l2/review_packs/FT20261016_LANE1_REVIEW_R5_INDEPENDENT_FOLLOWUP_r1/` 包含最小新Core差分、完整R0→当前候选patch、准确更新计划身份、原Lane5审核及空间对账。首份 `FT20261016_LANE1_REVIEW_R5_BUILD_READINESS_r1` 保持冻结；先前回执存新pack，当前RECEIPT/RECEIPT_REVIEW_R5同步。

下一步：现有Ops真正释放且Lane5独立复测后，重新检查live资源、真实进程/registry与配额，由Lane1通过原build_r0_1.py唯一正式构建R0.1、运行21条producer定向、冻结新binary，再交Lane5独立11门槛。首批五B16/U_WB16新pair不等TVD/RO/ideal。旧六条R0应用科学SUSPENDED及旧R1撤回仍有效，不得计算正式速度/均值或复用旧key。
