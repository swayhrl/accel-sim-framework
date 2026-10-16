# EP-L2 / ISCAS2027 review_r9 | pilot请求晚于拒绝、Lane3/4交付和冷归档衔接
2026-10-17。**协调审查与有界CONTINUE，不是初始Goal、正式性能授权或删除批准。** 当前六Lane、双Storage-Ops已各自工作；只推荐**原Lane5窗口**消费一个新依赖事件，其他窗口不重新派发。

## 0. 准确时序及最新远端身份（下述只是已读Git快照）
- Lane5 Framework `hrl/ep-l2-ft20261016-lane5-v1` 提交 `300c1010161b270ae73414b8146d238c961f0cd0` 于 2026-10-16 17:14:48 UTC（北京时间10月17日01:14:48）发布 `NO_SAFE_PILOT_ENVELOPE`。其 `LOW_SPACE_PILOT_REQUEST_BINDING.json`查的是Lane1旧发布 `85534de235345292a153d9983cfd0d24d8033bb2`，因此request_commit/pilot_id均null；并非已经独立拒绝后续提交的具体申请。测试39项新+10项受影响原registry PASS只证明工具层，未创建token/lease，未编译。
- Lane1 Framework `hrl/ep-l2-ft20261016-lane1-v1` 在 2026-10-16 17:16:35 UTC才发布申请 `248c93acc611679afe42590760481f451773003d`；`docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1/LOW_SPACE_PILOT_REQUEST.json`，`pilot_id=EP_L2_R0_1_ENGINEERING_20261017_L1_P01`，请求文件内容SHA256 `3f4dfd9618602dfd3f2dc5d92d0d497987f9c6ea53088a6409648506f1c10dcb`，准确Core `c948184504d82b80e23eb3f4ff6cdfd328ba9355`、Framework `3ab150b3e99ff3ed759b8cdc5154cfb5744042a7`、vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`、独立工程root和最多-j2/3600s/21定向。
- Lane1真实dry-run与工具检查有效但仅 `REQUESTED_INDEPENDENT_LANE5_REVIEW_REQUIRED`，无真实lease/CMake/C++，工程与正式binary均null。用户截图晚于其GitHub状态报告称**唯一10分钟/48小时GateWaiter已经启动**；此为窗口可见报告、尚非本协调者登录进程实时证据。不能再命令启动第二等待器。
- 当前正式R0.1仍为无编译版本：原48GiB/额外2GiB建造余量、64GiB available RAM、共享registry/CPU/scan保护、Lane5独立11 gates/current V2 acceptance不变，旧R0/R1六条应用SUSPENDED，0 accepted pairs。

## 1. 对新请求具体预算的独立审查要求
申请两种写域的提出值（不是已批准安全数）：
- `/workspace`、`/tmp`同一预算：申请entry 26GiB，独立增长cap4GiB，其他写入reserve8GiB，监测/终止超调2GiB，应急保留10GiB，合计24GiB，仅有**2GiB算术余量**，hard-stop12GiB。
- `/root/share`独立预算：申请entry43GiB，增长0.5GiB、其他写入2GiB、超调0.5GiB、底线40GiB，合计**43GiB整，无额外算术余量**，hard-stop40.5GiB。
- 最新提交前Lane5自身30秒实测`/root/share`总free降343,343,104B，一段10秒net下降速率约17.61MB/s。它**不是未来最大写入率**，不能用短样本推导1小时安全或归责到DTC/C16；按此也不能认为43GiB的边界保留已得到证明。申请的4/8/2/10和0.5/2/0.5/40都是待Lane5独立核实、约束或拒绝的保守建议，不是测得的峰值或外部写入可执行上界。
- Lane5在原分支重新读取准确`248c93ac...`申请与`65500bb9...`独立工程runner、当前正式driver、现有pilot registry实现及其回归证据；按r8只读刷新现场`f_bavail`、两实际文件系统、DTC/C16/Storage-Ops活动、boot/registry身份、共享配额。先更新原拒绝的缺失request字段，**不能因为现在有request便直接签发token**。
- 若Lane5在用户既有**条件性一次**授权和不缩减其它项目保护下能证明并实测/强制执行一组合理的per-FS硬性预算，则发布**新的**准确、带精确request SHA、pilot_id、有效期、host/boot、STOP/lease的一次性`LOW_SPACE_PILOT_AUTHORIZATION`并回读后通知Lane1；普通r8工程问题可自行解决。若外部burst/终止超调或Share守护仍不能可靠界定，独立再出`NO_SAFE_PILOT_ENVELOPE_AFTER_REQUEST`，清楚区分已解决的请求身份与仍阻塞的资源项，不换成猜测的小GiB常数、不中途改正式policy、不启动CMake。
- 如果始终无法闭合，下一步选择**经证据批准的已停用目录精确迁出以恢复可用空间**，或准备需用户另批的独立主机/编译盘方案；不能无限等待/重复静态审计，更不能使用f_bfree-f_bavail保留块或假装在`/tmp`获得新盘。

## 2. Lane4科学审查（只接收源码准备）
- Framework `4a55269d5a4f1e11b93e67e9d4eadebe8b3b3493`，Core `8ff56eb0804a027f1e253e629dd2915b02bc03b5`，准确review pack `FT20261017_LANE4_REFERENCE_SYNC_r1`。源码补丁在成功clean/quiescent host prefill之后、memcpy offset++之前，对I_READ_HIT的ReferenceMemory按被接受的32B sector展开到字节做unknown version0/known标签清除，其它字节、已有response snapshots、monotonic producer counter不受影响；拒绝路径不修改reference。静态设计方向和原共同prefill语义一致。
- 该包附一条经历GPU写、dirty refusal、真实WB驱逐、稍后prefill、已保持sector读响应的**未执行**针对性反例，另有header回归；C++构建与两个新回归均NOT_RUN。此交付**接受为R1.1源码候选而非科学正确性证明**；等待正式R1.1生产实现/同binary B16和Lane5独立资格，原18格NOT_RUN、不能用于R0.1资格。
- Lane4 `VALIDATION.json`独立记录当前`CLIENT_CONTRACT`预期hash `8b4e820b9fcc...` 与现场 `6b20231ef33...` 不匹配，fail-closed正确。Lane5新工程pilot registry工具与原生产consumer的当前contract须按实际实时identity协调；不得由Lane4擅自覆盖旧hash或宽松跳过验签。该待修仅影响下一轮Ideal/独立认证，不阻塞Lane1工程R0.1静态准备。

## 3. Lane3（和Lane2）状态
- Lane3 Framework `e8d6f9671da0748b5f4eb780d6cdf163e91b58d1`、Core `5ae8b06d58b61189140f571ab37b5f6d51228632`，c948准确静态RO接线30源检查/10工具PASS；19 C++执行NOT_RUN。626秒依赖等待的`RESOURCE_WAIT_EXPIRED`仅指这个read-only监听子任务到期，不是RO项目失败；不再开额外等待器，等独立正式producer/qualification事件。
- Lane2后续Framework `dc21af497c319672c30752ed2192a2a8cc937bab`，TVD c948适配已完成；补充真实read-version presence guard源码候选，尚未编译。它的10分钟listener已结束，未来listener已加ENGINEERING_ONLY不能被误报成official release的守卫；无需重开轮询器。
- Lane2/3/4不借用户工程pilot来启动各自C++大编译、RO/TVD应用或ideal 18格；第一次有资格的性能仍依赖**官方**R0.1 producer并被Lane5独立接受。

## 4. Storage-Ops和交付门槛
- 双Ops在进行R1全14批归档及164全文件4,737,658,722B的独立内容恢复。旧174源侧已经完成B001 **1,269文件+123目录**原生权限/hash恢复演练，并精确清理**只有演练创建的副本**；原R1始终`SOURCE_KEEP`，没有任何R1历史build原始字节获准删除。
- 原Ops源侧目前为R1冻结精确197个`.vvp`、约4.46GB allocated的**待审源释放候选**，此外全build更高风险。未来若证据完整，优先让原Ops提交精确目录、原身份/恢复证明/项目owner无活跃依赖和需用户明确批准的manifest，不通过本r9直接授权删除。对于大PolyBench阶段当前仍是planning-only，不因配对赶期放开trace。
- Lane1只维护原来**一个**GateWaiter、可接受的工程pilot独立runner，无新全量CMake；Lane5本轮只新增一次**对最新申请的独立复核**，旧否决回执原样保留、另发新revision。其余Lane和Storage-Ops仍按原合同正常执行。

**审核结论**：Lane4修复候选与Lane3静态RO交付按scope接受；Lane5的早期`NO_SAFE_PILOT_ENVELOPE`是当时正确的，现有Lane1新申请应触发一次独立更新，但是否能够安全构建仍未知。没有给出降低正式48GiB、科学接受或源文件删除的额外批准。
