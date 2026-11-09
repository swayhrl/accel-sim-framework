# 给EP-L2 Main的109侧上下文增量

109-EP-L2已完成 `EP_L2_NODE109_READONLY_TAKEOVER_V1` 的一次只读接入。实际本机工作区为 `D:/Codex/Token-API/workspaces/EP-L2/109-EP-L2`，自身 `CONTEXT.md` 已更新；**没有改写Main的 `D:/Codex/Token-API/workspaces/EP-L2/CONTEXT.md`**。固定包源提交：`420c84671579a80ee0a8cc696f0e8db7bcaf9a86`。本交付目录：`docs/ep_l2/operations/ep_l2_109_api_takeover_20261109_v1/takeover_receipt_v1/`，包含回执、现场状态、资产索引和未决项；以本分支最终发布commit为固定阅读入口。

2026-11-09 21:32–21:41 Asia/Shanghai，109实连主机`PC`/用户`huangrulin`，RTX4080 UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`，driver580.178.04。21:33共享GPU锁由AI-ARCH supervisor占用，21:40定向复核见其自然退出；当时RTX相关进程仅余两个SSHFS与桥接；22:43:59定向109进程复核仍只见同一三进程身份，旧dispatcher/控制器/新dispatcher历史PID均不在，未见有限dispatcher或EP GPU producer。锁空闲的瞬时观察不授予下一次GPU运行。174-new公共catalog publisher仍在，属另一进程角色。

109 suite/pilot/Ada7/Ada8-C8/CUDA准备目录及冻结producer位置仍在。109两个NAS入口都经174-new指向同一个真164 bulk；174-new `findmnt` 的源为 `admin-wcx@10.208.130.164:/home/shared`。pilot、Ada7、C8、Ada9、Stencil的真164小COMMIT可定位。普通与派生catalog各82个已提交**版本**，不等于82个程序或当前五点输入资格。Stencil既有CPU恢复链按E17关闭，不需重做；derived仍无consumer/timing授权。

有限队列的最后可读小状态是10月27日06:15+08:00 `QUEUE.json`：242行中41已提交、33待处理、161专项待处理、5失败保留、2被替代；10月26的transpose三项后来已COMMIT。22:40–22:41补核真164私有控制目录：控制器 `EXACT36_BATCH_STARTED_CONTROLLER_COMPLETE`，新dispatcher于10月27日06:15:24+08:00因第三项streamcluster的 `worker/guard exit 75` 进入 `FAILED_STOP`。冻结36项末次状态为2已提交、1失败保留、33待处理；33项后续合法处置仍 `UNKNOWN`，旧PID不在，不能续跑或把pending改closed。Vector前两次capture exit0但无trace、C8随机输入 `INPUT_DIFF`、CALL旧issued0及Stencil原失败均保持反例。

Main仍是174-new唯一科学调度、预算、验收和集成owner。已转交的GEMM EXT0/1/2与Stencil EXT0/2五点，其登记/运行/结果仅以Main自身新回执为准；109窗口没有查询活动raw、改输入或提出额外前置条件。本轮GPU/native/NVBit/NCU 0、SIM 0、科学登记0、消费0、锁变更0、迁移0、删除0。需要33项后续处置或特定109资产时，请以精确asset ID和已封receipt给本窗口定向核对；不要将其作为当前五点的跨族阻塞门。
