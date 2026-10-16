# Lane 6 r5 — EN-v3 working paper and source-bound PPA

本 revision 执行 review_r7 `99e7515f81b0038ac49d274b73f774e8ea801e46`；延续原 Goal、worktree、执行分支。旧 r1–r4 与英文编辑分支原稿均保留。

- `EP_L2_EN_v3.pdf` / `.tex`：完整引言、问题、架构、方法、结果解释框架、相关工作和结论；4 页技术正文＋第 5 页纯参考文献。Fig.1 是声明的机制图，Fig.2–4 明确等待实测。
- `EDITORIAL_ADOPTION.md`：EN-v2 精确来源、吸收差分、引用核查层次与实际会议格式复核。
- `CLAIM_EVIDENCE_MAP.md`、`FIGURE_EVIDENCE_CONTRACT.md`：正文论点与精确资格、归因、面板的连接；不把历史终态当科学接受。
- `PPA_LEDGER.md`、`COST_MODEL.json`、`FIELD_COST_LEDGER.csv`、`COST_REBIND.json`：官方 c948 静态字段与比较／选择逻辑账。146 KiB 数据／slice、共同 128 B latch；metadata 场景有假设，物理面积／功耗／频率未知。
- `dependency_probe.py`：一次依赖事件读取，复用 r4 已冻结 V2 bridge。可带显式 native pair adapter 做原生验证；无 adapter 不输出数值结果。它不是后台等待器，不创建 lease。

本次收到 Lane5 新 publication `300c1010161b270ae73414b8146d238c961f0cd0`：当前 V2 generation 2、manifest hash `eccaa5bd0f24849dc4ae1c63754785a1cba29eefe23103491013088088ced37a` 未变，CURRENT_ACCEPTED 行和配对均为 0。其工程 pilot 工具与拒绝意见不构成正式 binary 或科学资格；本 Lane 不激活任何工程例外。旧 R0/R1 与三组旧应用仍撤回，旧 sad 不进入图表。PPA 无物理数字，五组均值为 null。

官方静态目标 Core `c948184504d82b80e23eb3f4ff6cdfd328ba9355` / publication `57e1c363aede1a7790bdf94136d832d35ee7b34b` 同 tree；生产 Framework `3ab150b3e99ff3ed759b8cdc5154cfb5744042a7`。binary 为 null；表中输入配置只作冻结研究设定。运行 source/config/binary/trace/key 需要随后由 Lane5 逐对发布，不借用静态候选来补空字段。

实际范围：仅文稿、派生成本资产、只读依赖和临时 LaTeX typesetting。0 次生产 C++ 构建、0 次模拟、0 次 registry/lease 写入、0 次 Storage-Ops／其他项目动作。本 Lane 无 GateWaiter、PID／锁／截止均不适用；未建立 release listener。后续依赖读取由当前有效 turn 或用户／协调窗口续行触发，不宣称 turn 结束后有自动常驻服务。

验证入口见 `VALIDATION.md`。字体/宏包只在任务临时目录，未纳入仓库或修改系统安装。PDF 尚缺作者信息、正式实测和最终投稿检查，是可审阅工作稿。

关闭前另收到 Lane1 `248c93acc611679afe42590760481f451773003d` 的 ENGINEERING_ONLY 请求；正式源未变，binary 仍 null。请求、工具测试、尚未启动的 GateWaiter 都不增加接受配对。本 Lane 只消费依赖事实。
