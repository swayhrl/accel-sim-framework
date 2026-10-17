# DTC_LANE_V_SEMANTIC_AND_INVALIDATION_CONTRACT_174_V1

**只读审计已交付；当前 DTC 写后数值可见性 UNPROVEN，K1 尚未实现；全 ISA 正确性与“一键清空”主张 STOP。** 普通 L1 invalidate/flush 没有传到独立 DTC Tag/physical；ordinary store、atomic、bypass 的完成观察不会自动撤销 DTC 映射。PROXY_FENCE不能充当数据一致性。

执行环境为原174主机 `huangrulin-174`、原容器root账户。独立 Framework 分支 `hrl/iscas2027-dtc-lane-v-semantic-audit-174-v1`，worktree `/workspace/worktrees/accel-sim-iscas2027-dtc-lane-v-semantic-audit-174-v1`，从冻结 **build** `18a68dcccd795f1b6cda75504e9450d00c9cee02` 创建。Core `6fba0136f8465b59fe5858a950fa39efb265f654`逐文件匹配Git对象且clean；未改Core、build或其它Lane目录，未运行完整模拟器，没有新增observer/dispatcher。

审查先核Core/build及A/T/U已提交发布证据。A固定 `f5c37d6edcce832a72cb0830021bffa78df6cc13`、T固定 `f520a445436b57c0a0f2494fb858a1636f04d2bc`，U正常fetch后固定 `16e56912cfd02f2311a1603a29415dee829fd495`。U真实后台准入及后续终态报告均保留，只读Git对象，没有接管、重启或重做其终态验收；Git内容发布回执与另存raw root的最终回执明确分开。移动中的U远端读数差异已记入事件图。

最关键的语义结论：

* **kernel-done与source invalidate不同**。默认flush_l1=0；开关开启后，cycle按每个cluster的not_completed==0选择SM集合，可反复触发；并发kernel/cluster状态可阻止对应集合，不能称每个实际kernel边界统一失效。cache配置变化、普通membar另有自己的条件。
* ordinary invalidate请求等待其miss queue/owner/MSHR排空后执行；这不是DTC drain。`flush()`只处理ordinary modified tags，不能拿它证明DTC失效或真实writeback。
* IO/OO独立Tag+physical，返回按保存的UID/physical/generation，Tag victim不取消旧消费者。OO最后Ref才可回收；IO靠替换者FIFO release依赖，source invalidate无天然替换者，需单列orphan生命周期证明。
* store sidecar可在dispatch退出时完成观察，WRITE_ACK计数是另一条路径。proxy只提供source async规则及OO同warp younger-retire过滤，不建立一般全局内存ordering/coherence。

给Lane X的K1：**仅在source-defined L1 invalidate请求中撤销DTC地址查找可见性；已接纳消费者和在途返回继续用旧physical+generation，最后owner结束才可回收。** 不清PIB/Ref/waiter/inflight，不统一增加generation，不复活旧Tag。IO缺乏等价最后owner证明时 `STOP-IO-IMPLEMENTATION`。K1不声称解决无失效事件的写后同址读取。

交付入口：

|文件|内容|
|---|---|
|[SOURCE_EVENT_MAP.md](SOURCE_EVENT_MAP.md)|逐调用链、源码行号、A/T/U发布身份、真实kernel与条件source事件、三个结论层级|
|[WRITE_VISIBILITY_RISK_MATRIX.tsv](WRITE_VISIBILITY_RISK_MATRIX.tsv)|load/store/atomic/bypass/fence/kernel/invalidate/return/victim/reclaim的五状态变化与前后次序；CURRENT和K1_REQUIRED明确分开|
|[K1_SEMANTIC_CONTRACT.md](K1_SEMANTIC_CONTRACT.md)|最小合同、线性化点、IO缺口、一键清空裁决、8项实现验收要求|
|[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md)|STOP等级、可验证缺口、支持域与X/Y/W/AA共同审查边界|
|[SOURCE_SHA256.tsv](SOURCE_SHA256.tsv)|冻结source与A/T/U证据的commit/blob/SHA256/bytes身份；不复制其它Lane工作目录|
|[CPU_CHECKS.json](CPU_CHECKS.json)|小型只读源码/header检查结果、编译器与负测stderr；完整模拟器运行数=0|

复核命令：在本worktree执行 `python3 -E docs/dtc_l1/review_packs/DTC_LANE_V_SEMANTIC_V1/scripts/audit_readonly.py`。只在本包写SHA表/小型收据，临时编译生产header与5个小程序后清理临时目录；不调用模拟器。PASS限结构/源码谓词，**architectural value tests=0，K1 implementation tests=0**。旧generation负测的子进程assert为预期结果。

Git交付以本分支最终HEAD/tree为准；提交后必须push、fetch-back、逐blob匹配全部本包文件并核worktree clean。最终外部回执写 `/workspace/dtc-lane-v-semantic-audit-174-v1/FINAL_FETCH_BACK.json`，绑定最终提交而不制造自引用commit。报告不伪造自身HEAD。科学STOP不妨碍本只读审计交付完成，也不授权突破缺口或启动新实验。
