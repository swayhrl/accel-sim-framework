# 实验台账更新协议

用户要求“完成后更新”。维护者分工：174 Codex在其**执行分支**上维护每个immutable attempt及R2注册行的机器状态；ChatGPT在收到新报告、读到对应remote commit/strict evidence后更新**本论文总表**。两者不互相覆盖，不靠历史聊天截图推导最新terminal。

## 验收后才算完成

**事件驱动：**每个自然terminal后立刻执行strict validator；验证Core/runtime/config/trace/program/input/ROI及source-specific counters/exit、重复记账/漏响应/最终drain。通过者标`STRICT_PASS`并登记commit、receipt及exact row identity；失败标`FAILED_PRESERVED`并保存旧attempt UUID/日志，不重命名为成功。运行中记`RUNNING`且不出数值。未核查的用户口头进度标`REPORTED_RUNNING_UNVERIFIED`；已登记但不确定实时状态标`PREREGISTERED_STATUS_UNVERIFIED`。

**每个里程碑**（先试点结果，之后机制控制/慢行/12项收口，最后容量gate）在执行分支提交小型snapshot，并更新`codex_handoff/LATEST_REPORT.md`，push+fetch-back HEAD/tree。无新科学问题时自动补位，不为等用户阅读报告而停止已授权独立实验。

**总表更新由ChatGPT完成**：收到commit或在新对话中明确要求同步时，直接读取GitHub新HEAD与receipts，再提交新的`V2`快照或更新同一表的状态（保留旧提交）。不把summary等同原始记录。不会声称在本次聊天结束后仍在后台自动观察GitHub。

## 明确界限

- 不能用`REGISTERED_ROWS_V2.tsv`的`NOT_YET_LAUNCHED`描述当前实时进度；它是当时的注册快照。新attempt状态要看新提交。
- 174源Core6fba... R1 V2覆盖此前789...V1计时缺陷；旧gate保留superseeded，已停止的旧finite attempts记录invalidated。
- E14 modern baseline可以做；E15 modern capacity尚未通过，E16 modern DTC不能“为了利用空闲计算资源”偷跑208KiB数据/共享预算。
- 109固定12的producer在109未发现，是**本机不可用**而非不可恢复；SpMV格式通过≠simulator admission；LayerNorm trace不准入。
- 逐程序输入若缺编译期尺寸或完整前序状态，不能猜测或直接报“已验证完整应用”。
