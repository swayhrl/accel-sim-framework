# 174-AI-ARCH｜CPU-only历史承接与节点核对Goal

Goal：`AI_ARCH_174NEW_API_TAKEOVER_CPU_ONLY_V1`。

用户将本Goal转交给API会话 `174-AI-ARCH` 后，授权在**174-new**完成本文件界定的接班。不是科研GPU/模拟任务。请在同一Goal中连续完成资料阅读、必要节点自查、遗留差异整理、知识维护与发布，不每完成一个小步骤就等待确认。

## 1. 必读和当前事实

首先完整阅读本目录README、CONTEXT_174.md和EVIDENCE_INDEX.json，再按台账读取15项科研任务的原报告及相关独审。先关注各任务的科学问题、实际做过什么、固定终态和不能外推的范围；不重审全部外部论文或大raw。

主线在109：Main（API“AI-ARCH交接-1”）的 `AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1` 已被用户确认执行，结果未回报。你不登录109、不查其活动分支进度/raw、进程、GPU锁/预约，也不改Image-Lab或重发该Goal。科学窗口负责审结果，Main继续原合同。

历史资料不等于当前任务。A77-S是模型/配对资格NO_GO而不是待继续模拟；A70等源范围零候选不是GPU性能负例。旧C16/AWMA/EP-L2/DTC-L1等不属于本次接管。

## 2. 本机工作入口与上下文隔离

建议API本机目录：`D:/Codex/Token-API/workspaces/174-AI-ARCH/`。

若尚无目录，可新建并维护该目录的 `CONTEXT.md` 与 `deliveries/AI_ARCH_174NEW_API_TAKEOVER_CPU_ONLY_V1/`。若API环境已有明确项目工作根，记录实际路径并使用它；不得把路径是否存在当作既定事实。

不要并发写Main的 `D:/Codex/Token-API/workspaces/AI-ARCH/CONTEXT.md`。无法访问D盘时，在自己的174独立工作区维护CONTEXT.md，并将其去除敏感信息后的快照发布Git，说明实际位置。不假定两端聊天、文件或上下文自动同步。

## 3. 确认174-new而非原174

使用本机现有受信SSH配置，历史alias为`hrl-174-new`，旧端口2239仅作线索。可先用 `ssh -G hrl-174-new` 检查hostname/user/port等非敏感字段，随后单次连接确认用户、hostname、容器/namespace线索、工作目录与repo/worktree。

不要打印完整SSH配置、私钥、token、环境变量值或可能含凭据的ProxyCommand。不要关闭host-key校验。相同`huangrulin-sshfs-174` hostname不能单独证明是目标容器；身份有矛盾就停止节点侧动作，用Git固定资料继续可独立部分并报告，不尝试切换其它账户碰运气。

历史主repo为 `/root/workspace/accel-sim-framework`。只读查看其remote URL、worktree登记和AI-ARCH相关refs；不在共享主工作树checkout/reset/stash/clean，不改变既有remote或全局Git/SSH/Codex配置。

先读取适用AGENTS。旧AGENTS若仅限定VM/TLB某分支，不把它当当前AI-ARCH科研Goal；有实质权限冲突时明确报告，不能默默忽略。

## 4. 轻量资源与安全边界

以现有Git对象、固定路径和小型文本为主。单个轻量解析worker起步，控制Git线程和并行下载；不要因机器有很多核就启动大批后台任务。当前load、MemAvailable、swap、I/O pressure及本工作区所在文件系统余量只做必要只读快照，不把历史14/38/71/79GiB或swap记录当当前资源。

不全盘find/du，不穿越 `/root/share/mnt164` 或其它大型挂载，不复制模型/场景/trace/checkpoint。新增资料应保持小型；不为接班做完整repo重新clone、历史全量fetch或大对象哈希。只有缺少本表明确固定对象时，才针对命名ref/commit有界获取；若传输会大量拉取，改用GitHub逐文件固定读取并报告本地对象缺口。

不运行CUDA/NVML/JIT、模型、Profiler、Accel-Sim或RTL，不编译模拟器，不安装依赖或下载模型/数据，不更改时钟/功率/驱动。旧worker/supervisor/launcher可能带副作用，禁止为了查看状态而import或执行。

不删除任何旧worktree、cache、失败输出或正式证据。不绕过自动审批/安全策略完成删除；不影响接班的临时副本可保留，并标明来源与派生属性。

## 5. 节点侧核对：把Git历史落实为可持续入口

### A. Git与worktree登记

在已确认的repo中只读运行等价于 `git worktree list --porcelain`、限定AI-ARCH前缀的 `git for-each-ref` 和 `git cat-file -e` 的检查。用台账的固定commit/report定位，不按worktree名字补猜路径。

逐项记录：任务ID、原branch、固定published commit/tree、当前本地HEAD、相关远端HEAD（必要时单次读取）、实际worktree/output、报告和receipt可读性、是否有本地差异、是否有新提交/未跟踪文件。

分清：
- Git报告可读；
- 节点原输出仍存在；
- 大payload资格/科学结果已经接受。

三者不同。小报告在Git可恢复，不因为tmp缓存不见就重做研究。旧分支比已知commit更新时，先只读看具体变化，再判断是receipt补交、文档修订还是新科学工作；不reset到旧SHA。

### B. 有界检查自身未发布内容

只查看已定位的AI-ARCH任务路径。优先 `STATUS/RECEIPT/FINAL_REPORT/FINAL_READBACK`、少量Git log/diff和小型索引。不能扫描其它项目活动raw、读取所有进程环境或将大日志复制进入本轮包。

发现自身未发布文件时保留原件；可在本轮独立目录保存必要的小型快照、bytes/SHA和来源，不自动变更旧分支或将未验收结果写成PASS。可确定性重建的索引/manifest标为DERIVED或RECONSTRUCTED，绑定生成规则和原固定输入。

若有疑似仍活动的AI-ARCH任务，只在能绑定工作目录、用户、进程启动身份和任务收据时做一次被动核对；不kill、不attach调试、不重启、不继续dispatch。状态未知就写未知。其它项目进程不属于接班范围。

### C. 本轮重点缺口

- A4-N：查是否存在可读原件或后续V2。找不到则保留A5限定结论，不从问号文本猜回中文。
- A70N/P、A73H、A75D、A77S：核CONTEXT所列精确历史worktree和输出入口；找到private FINAL_READBACK则作小文件证据，缺失则使用固定Git事实。
- A77-S：只登记既有外部core/config/binary源码身份和索引入口，明确其所属项目。没有readiness升级，不运行六点pilot，不读取大型trace或访问164。
- 工作流bootstrap：仅继承可用手动模板与边界，不修旧CLI认证、不部署hooks、不升级Codex。
- Git台账之外的新发现：只有能通过任务内容/Goal/用户归属确认属于AI-ARCH，才进入补充表；不要因路径同在accel-sim-framework或包含174就接管。

## 6. 隔离写入与发布

建议新接班结果分支：`hrl/aiarch-174new-api-takeover-receipt-20261109-v1`；若名称已用，先核归属，选择不覆盖旧内容的新后缀。

从本交接固定提交建立自己的小型/sparse worktree，只写本轮结果目录，例如：
`docs/ai_workload_research/handoff/AI_ARCH_174NEW_API_TAKEOVER_RESULT_20261109_V1/`。

历史分支和执行原件全部只读；本轮不直接写科研协调分支，不合并历史实验HEAD。Main在109运行时，不要求它暂停来同步上下文。你的结果由用户带回科学窗口审查，再选择性纳入总导航。

允许必要的有界网络/API/解析和包装修补，使用现有认证及传输备用通道，不输出凭据。远端发布失败不重跑调查或改科学内容；保留exact本地commit，用已有合法通道发布同一对象。

## 7. 最低交付与知识落盘

1. `TAKEOVER_REPORT.md`：节点身份及读取范围、15项科研任务＋工作流的恢复结果、历史与当前差异、未发布材料、活动状态、未决项、可承担能力和明确不能做什么。
2. `NODE_TASK_ASSET_INDEX.tsv`或JSON：原固定来源与实际node路径一一对应；不存在/不可读/未核分开，不填造。
3. `CONTEXT_174_SNAPSHOT.md`：本机CONTEXT的可公开快照，包含当前109运行保护、节点分工、证据索引、科学边界、未决项和下一动作。小而可持续维护，旧历史用固定链接。
4. `RECEIPT.json`：本轮实际访问节点/路径、允许动作、未执行项目、必要资源快照、Git发布身份；记录未完整采样的范围，不冒称连续峰值。
5. `COORDINATION_UPDATE_PROPOSAL.md`：仅列建议Main将来采纳的174接班事实，不修改总协调和Main本机CONTEXT。

若发现真缺件或身份冲突，返回有界部分完成报告与具体缺口；不要为追求全绿重新开展旧科研、进入其它节点或大扫描。已经可恢复的部分继续完成。

在本机CONTEXT中记录本轮结果、固定来源和未决项。以后同一窗口按当前入口与任务增量工作，不重复全套接班。

## 8. 收口与判定

完成语法/路径/编码检查、显式staging、commit/push及单次fetch-back，核远端ref/commit/tree和本轮小文件blob/字节；无凭据/大payload入Git。只报告自己工作树clean，不声称其它项目也clean。

最终返回中文摘要：哪些历史工作已接上、哪些只剩Git、哪些节点资料新找到、是否有本地未完成/未发布事项、接班是否足以长期工作，以及固定报告链接。不要只给D盘链接。

资料与节点入口已闭合、没有需要干预的旧活动任务、边界和上下文可持续时，可报告本节点接班完成；有不可替代科学内容缺失则明确PARTIAL及其影响，不把缺普通tmp等同整体失败。

完成后STOP，不自动启动任何新科学实验或额外研究Goal。未来174的源码、独立分析或模拟器任务均由用户/科学窗口按具体问题另行确定。
