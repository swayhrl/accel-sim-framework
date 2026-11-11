# 私有人工审查协议

## 访问与隔离

仅在 109 本地、经确认有 WildChat 原文处理权限的审查者可查看 `/data/c16/aiarch_hybrid_four_session_g0_private_20261111_v1/review_cases.json`。该文件包含固定 S01–S04 的 user₁、原 GPT assistant₁、user₂、来源与原始身份；目录 0700、文件 0600。读取前应确认审查者身份、数据访问授权及用途允许范围。Git、聊天、Codex 工具日志、174、第三方 LLM 和云评测器均不得接收原文、原始 ID、局部摘录或可识别 PII。

原 GPT assistant₁ 只供判断 user₂ 对原历史的依赖。不得送入 Qwen 第二轮、作为参考答案，或交给未来独立质量盲评者。本轮没有执行人工内容审查；文件准备不代表授权或批准。

## 逐条判据

对每条固定会话独立记录：

1. **原 GPT 依赖**：user₂ 在未知原 GPT 回答时能否理解？仅用通用上下文是否足够？是否指向原 GPT 独有的列表、数字、建议、措辞、链接或承诺？如果 Qwen assistant₁ 不同，是否仍有合理回答空间？一般“继续”不得按关键词自动判定。
2. **隐私与权利**：是否有潜在 PII、敏感或不适用内容？数据库 ODC-BY 许可是否覆盖本次受限本地处理；单条内容和人员访问是否另需授权？若必须查看更多私人信息才能判断且无权限，记阻断。
3. **纯文本完整性**：是否缺少必需的附件、图片、工具结果或外部网页？是否要求当前纯文本模式不能满足的条件？短上下文资格是否受结构性问题妨碍？

须在私有记录中保存审查者身份、授权依据、审查时间、每项判断及理由；公开只发布去内容类别和状态。无法合法查看时不打开私有文件，记 `CONTENT_REVIEW_BLOCKED` 或在授权状态尚待核实时记 `PENDING_HUMAN_REVIEW`，不得推断 PASS。

## 分类与出口

每条使用 `SOURCE_COUNTERFACTUAL_ADMISSIBLE`、`ORIGINAL_GPT_DEPENDENT`、`CONTENT_REVIEW_BLOCKED`、`INDETERMINATE`；仅机械完成且缺人工审查则单独用 `PENDING_HUMAN_REVIEW`。四条全获合法审查且全部 admissible 才能 `G0_PASS`。任一明确不适合或权利/隐私不可接受则 `G0_NO_GO`。其余机械已完成但人工门未闭合为 `G0_PARTIAL_PENDING_REVIEW`。任何结果都不自动授权 GPU。
