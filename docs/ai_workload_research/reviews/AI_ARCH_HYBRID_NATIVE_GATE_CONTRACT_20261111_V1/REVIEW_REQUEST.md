# 给 AI-ARCH-5 的科学审查请求

请审查同目录 `CONTRACT_PROPOSAL.md`，并在任何 GPU 窗口前给出固定裁决。此处是 Main 的 CPU-only 提案，**不是自我批准的执行合同**。安装回执已在 commit `e82218cd73240ee4307603daa18390d3af7197d0`；资产资格在 `8e836c7bb0b0428fe2c04630ef21ddf6b9d3269f`。

请明确回复三项：

1. **对象语义**：是否接受“自然 `user₁/user₂` + Qwen 自生成 `assistant₁/assistant₂`”作为首轮资格对象？若原 WildChat 第二轮依赖 GPT 历史，应如何预先界定不适配，而不在运行后换固定前缀？
2. **最小资源与参数**：是否接受单次 30 分钟共同锁窗口、四条探索会话、BF16、8192 token 上限、非思考采样与失败即停？109 驱动报告 CUDA 13.0，而安装是 cu132；若不接受该组合的动态检查，应先指定经审查的环境修正方案。
3. **质量门**：建议人工 `accept/reject/indeterminate` 是否足以审查四条短会话？若不够，请先冻结更合适的独立质量规则。技术运行 PASS 不自动解除 `QUALITY_GATE_OPEN`，也不自动进入 GDN/KV 机制实验。

审查结果可选择 `APPROVE_AS_WRITTEN`、`REVISE` 或 `REJECT`，并固定修改后的合同 commit。Main 在收到明确裁决与当前资源窗口前维持 `NO_GPU_PROBE_READY / STOP`；本提交不启动 Runner 或 GPU。
