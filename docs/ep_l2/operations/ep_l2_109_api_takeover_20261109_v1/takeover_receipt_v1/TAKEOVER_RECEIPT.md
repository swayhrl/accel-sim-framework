# EP_L2_NODE109_READONLY_TAKEOVER_V1 接管回执

结论：**COMPLETE（109侧只读接入与知识交接）**。观察日为2026-11-09，以下时间均为 Asia/Shanghai。交付不代表历史队列全闭合、GPU可使用、资产可删除或五点在Main侧已运行。

## 职责与连接

本窗口实际工作区为 `D:/Codex/Token-API/workspaces/EP-L2/109-EP-L2`，在独立仓库文档工作树写本回执，并维护本地 `CONTEXT.md`。EP-L2 Main仍是174-new的本机API会话“EP-L2交接-1”，独占科学调度、预算、验收和科研集成。109窗口只负责历史采集/工具/资产知识及以后明确授权的109侧联络。DTC、C16、AWMA、AI-ARCH及共享资产owner不因本次接入变更。

21:32:40 通过既有SSH连接109，实际主机名`PC`、账户`huangrulin`/UID1004、boot ID `35425a62-1268-4560-a3cb-b674371cd7aa`。只读设备查询显示 NVIDIA GeForce RTX 4080，UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`，driver `580.178.04`，与历史记录相符。21:37左右经既有 `hrl-174-new` 连接，`findmnt` 显示 `/root/share/mnt164` 的真实源为 `admin-wcx@10.208.130.164:/home/shared`，类型 `fuse.sshfs`；109的 `nas_rtx4080` 与 `nas_fast_sc_copy_st_20261029_v2` 均经174-new指向同一个164 bulk目录，不是109两份物理副本。本轮未新建或修改挂载。

## 当前进程与共享owner

21:33:02 的109一次观察中，共享锁 `/data/c16/locks/c16_gpu_campaign.lock` 由AI-ARCH supervisor PID480098/start_ticks485140027持有；GPU计算列表有AI-ARCH PID504807及ComfyUI。这是合法其他owner的活动，不对其发信号、改锁或读取活动raw。21:40:51 的定向复核显示该AI-ARCH supervisor及GPU进程已自然退出，锁未见持有者，GPU计算列表仅见ComfyUI。锁空闲快照不等于本窗口获得GPU使用权。

21:40:51，限定项目路径匹配到的进程只有109侧SSHFS PID426875/start_ticks345266062、PID1470456/start_ticks379699610，以及桥接PID3398091/start_ticks437957991；未见本共享RTX有限dispatcher、worker或EP GPU producer。10月26历史PID1219372与1362061在本轮 `/proc` 中不存在，不能用旧PID认领当前进程。174-new公共catalog publisher PID951008/root 仍在，只是指针维护进程，不能当109采集活动或EP科学Main。22:43:59+08:00又做一次限定路径的109 `/proc` 定向核查，仍只匹配到上述两处SSHFS和同一桥接PID/start_ticks；旧dispatcher/控制器/新dispatcher历史PID 1219372、1362061、1376608均不在，未见本项目GPU producer。该观察不重新判断锁或其他GPU owner；不建立轮询。

## 有限批次最后可证明状态

固定包E16是10月26日09:40–09:48的非原子快照：38已提交、1运行、36待处理、161专项、4失败保留、2被替代。现场沿指定control和真164小记录查到更晚证据：174-new控制文件 `QUEUE.json` 最后mtime为**10月27日06:15:24**，242行分别为41 `COMMITTED_VERIFIED`、33 `PENDING`、161 `PENDING_SPECIALIST_EXTENSION`、5 `FAILED_RETAINED`、2种 `SUPERSEDED` 各1；其中 `ORD_CUDA_SDK_transpose_636b2ab3ab5e_A001`、`ORD_EXT_transpose_32c9f7dc72fe_A001`、`ORD_EXT_transpose_cab8f027e949_A001` 已COMMIT，`ORD_Rodinia_streamcluster_1be5fda1aa60_A001` 的失败原件保留。旧有限dispatcher的已封stdout记录截至三项transpose提交，109旧PID已不存在。后续定向补核找到私有目录中的控制器与dispatcher终态；36项全部完成仍未获证实，详见下节。

21:39左右经已核源的真164挂载读到公共catalog：普通 `ASSETS.json` 82个 `FULL_APPLICATION_TRACE` 版本、派生 `DERIVED_ASSETS.json` 82个 `DERIVED_COMPLETE_CTA_TRACE` 版本，均为 `COMMITTED_VERIFIED`。普通指针所指小版本SHA `88ee027f8c2ecfc4058f9884f566a3a03e1bbe78c79b89849d1b711bed385364`、派生指针所指小版本SHA `ab4ab8b05dc91a299bfcd354f5c9e799c252f995ea241944ace705966b09765b` 均与实际小版本文件匹配。普通指针11月9日仍刷新；catalog增加可能来自独立后续任务，**82+82不是242队列终态，也不是164个独立程序或应用科学PASS**。未运行公共 `verify --all` 或 `restore`。

## exact36尾部定向补核（2026-11-09 22:40–22:41）

沿固定E16控制器源码及 `ROOT_PHASE_LAUNCH_V1.json` 指向的真164私有目录 `bulk_20261024_v1/private_candidates/cpu_post_parallel_20261026_v1/` 读取已封小收据。`phase_run/SWITCH_CLOSED.json` 证明原transpose发布关闭、36行切换及旧STOP退役；`phase_run/STATE.json` 记载 `EXACT36_BATCH_STARTED_CONTROLLER_COMPLETE`，表示控制器完成切换，不表示新批次完成。新dispatcher `run_1792982115925796665/STATE.json` 于**2026-10-27 06:15:24+08:00**记录 `FAILED_STOP`，第三项 `ORD_Rodinia_streamcluster_1be5fda1aa60_A001` 因 `worker/guard exit 75` 失败；同目录 `_FAILURE.json` 记录 `FAILED_RETAINED`。按 `NEW_BATCH_STARTED.json` 的冻结36个ID对照同一末次 `QUEUE.json`：2项 `COMMITTED_VERIFIED`、1项 `FAILED_RETAINED`、33项 `PENDING`。已封dispatcher stdout只列前两项COMMIT。控制器切换和有限dispatcher失败停机均可证明；33项后续合法处置与36项全完成仍为 `UNKNOWN`，不续跑或重试。上述小文件SHA256及时间见 `CURRENT_STATE.json`。

## 资产与资格继承

109的suite、pilot、Ada7、Ada8/C8、CUDA/SDK准备目录及旧AWMA tracer工具路径均实见为目录；未见这些根本身redirect。109冻结Ada7 `producer.so` 实见，历史SHA `55c6f482...147ee68b73`；冻结C8目录实见，历史producer SHA `c8cfa41f...159ad1352`；本轮没有重算二进制SHA。CUDA/SDK `manifests/` 内完整205/82原生路线表及小型 `FINITE_NATIVE_SUPERVISOR_CLOSEOUT_V1.json` 可定位，该子Lane terminal，不等于生产trace资格。

真164 `pilot_20261024_v1` 的COMMIT和174-new `READBACK_174NEW.json`可读，pilot归档SHA沿用历史 `17e4fa4b...7bf4dea94dcac3`，本轮未重hash tar。Ada7、C8、Ada9 engineering对象及Stencil full/derived对象的COMMIT也可定位。Stencil的100-kernel原采集及retained-byte恢复、COPY、108成员Native cold和目录关闭直接继承E17；原stride40 exit1保留，derived的consumer/timing为 `NOT_GRANTED`，不得替换Main当前冻结Stencil输入。Vector试点前两次capture exit0却无trace；E05明确SM70 cubin不能直接跨major。Ada7的symbolic constant、C8的有限HtoD观察及runtime-random `INPUT_DIFF`、CALL旧 `issued0` 等反例均保留。原生exit、数值、实际输入字节、全记录producer、特定consumer、硬件timing、归档/恢复分别判断；任何一项不因另一项PASS自动晋升。详见 `ASSET_INDEX.json`。

11月4存储E18/E22对suite的 `ACTIVE_PROTECTED` 与Ada/native准备的 `TARGET_UNVERIFIED` 只是当日范围；E19实际清理白名单仅R26九份、R27三份、Qwen3二十六份，不包含RTX/EP/Ada。本轮所有EP/共享Trace源继续KEEP，未移动、删除或恢复。

## 判定与动作

已完成固定包阅读、109账户/设备/进程/锁一次现场对齐、限定小证据及真164源核验、历史资格与反例索引、本地上下文和远端小报告交付。主要资产可定位；exact36剩余33项的后续处置和早期EP producer链仍按 `OPEN_ITEMS.md` 明确列为UNKNOWN，不阻塞此次固定接入完成。Main五点在174-new的实际运行/结果未由109窗口核查或改写。

本轮实际动作：GPU/native/NVBit/NCU采集 **0**，模拟器 **0**，科学预算登记 **0**、消费 **0**，锁变更 **0**，服务重启 **0**，资产迁移 **0**、删除 **0**，旧queue续跑/重试 **0**。只读 `nvidia-smi` 查询不计采集。发布回读后本轮结束，不启动后台轮询。

固定包：`420c84671579a80ee0a8cc696f0e8db7bcaf9a86` 下同目录的README、Goal、EVIDENCE_INDEX、ASSET_AND_ROLE_LEDGER；历史来源号E01/E02/E04/E05/E06/E08/E09/E10/E15/E16/E17/E18/E19/E22按该索引的固定commit/blob定位。现场路径、时点和证据分类见 `CURRENT_STATE.json`。
