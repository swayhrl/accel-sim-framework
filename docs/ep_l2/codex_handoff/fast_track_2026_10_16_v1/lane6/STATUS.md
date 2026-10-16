# Lane 6 — r7 English manuscript / evidence / PPA

延续原 Goal、执行分支 `hrl/ep-l2-ft20261016-lane6-v1`，未新建工作树或重启任务。完整读取 r7 `99e7515f81b0038ac49d274b73f774e8ea801e46`，新产物包 `docs/ep_l2/review_packs/FT20261017_LANE6_PAPER_PPA_r5/`。文稿/工具 producer commit `24eb77812a649b30b1a63f307be6caa1927b36fb` 已 push、fetch、ls-remote 及46个精确blob回读一致；当前回执所属外层Git commit是本次报告发布HEAD，最终push后再次回读。

吸收英文编辑分支精确 `2d7091bf54f4aa77aca5f44e3005166dce8f7ae7`：原三文件逐字节保留，EN-v3完整正文、真实架构TikZ、Fig2–4待测图位和10条有用途引用。修订了PPA比较/选择/仲裁说明及受控结果状态输入，没有填性能数字。实际本地IEEEtran Letter编译4技术页＋1参考文献页，229503B，12个嵌入Type1字体，无Type3/undefined/overfull/警告；五页与放大架构目视通过。TableI实际在page3，以本次验证为准。官方会议格式已复核，作者和真实结果仍待补，非最终投稿稿。

PPA重绑定官方Core `c948184504d82b80e23eb3f4ff6cdfd328ba9355`（publication `57e1c363aede1a7790bdf94136d832d35ee7b34b` 同tree），生产Framework `3ab150b3e99ff3ed759b8cdc5154cfb5744042a7`。三份字段blob与62dc相等，故保留九字段账/六N-G场景并更新准确源身份；原getter和fixture-clock修复已存在，不重复patch或旧测试。146KiB/slice数据＋共同128B latch；G/K/Qb/E等硬件边界与比较/选择/rollback/端口/RTL/STA仍明确未知，不提供mm²/mW/频率或sizeof面积。

最新依赖读到Lane1 `248c93acc611679afe42590760481f451773003d`、Lane5 `300c1010161b270ae73414b8146d238c961f0cd0`。Lane1仅发布ENGINEERING_ONLY请求，正式binary仍null、runtime_ready=false；Lane5报告无安全pilot envelope且早于该新请求。两者都是依赖事实，不是本Lane取得或激活例外。Lane5当前V2 generation2，manifest `eccaa5bd0f24849dc4ae1c63754785a1cba29eefe23103491013088088ced37a` 未变，CURRENT_ACCEPTED行0、配对0、geomean=null。旧R0/R1与sad继续撤回；历史completed_pairs=3不能当接受数。

已交付claim-evidence map、逐panel证据/单位/归因合同、十行不可执行原输入图位清单和one-shot dependency_probe。probe复用已冻结r4原生V2/current-authority/proof/withdrawal/eleven-gate桥；有合格配对时用准确native adapter接收，候选行自身不出数值，未知schema仍fail-closed。以后每次接收和发图前重新fetch及最终ref检查，后续撤回会拒绝受影响结果；五对全接受才出geomean。没有重跑已通过的旧cost/bridge/oracle/calibration测试。

实际范围：0生产C++构建、0模拟、0run-key/lease、0registry写、0原始科学CSV修改、0Storage-Ops或其他项目动作。153份旧r1–r4文件与旧HEAD逐blob一致。启动资源读数只是快照，48+2GiB/正式政策未改；排版临时宏包约41.3MB，未系统安装。关闭registry0 active run/lease；2个DTC simulator及C16 PID280466仍存活，仅观察。

本Lane没有GateWaiter/release listener/后台进程，PID/锁/截止均null。Lane1最新回执称等待器prepared/not-started，现场定向扫描未观察到；唯一磁盘等待器仍属Lane1。后续触发是Lane5正式binary独立资格与首个CURRENT_ACCEPTED原生配对，在有效turn或用户/协调续行中继续，不伪称turn结束后无人值守。物理PPA与独立ideal/TVD/RO各按自己的资格并行等待，不阻塞主配对。
