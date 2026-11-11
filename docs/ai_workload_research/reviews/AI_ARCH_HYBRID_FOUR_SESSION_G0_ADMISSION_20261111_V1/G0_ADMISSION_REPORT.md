# 109-AI-ARCH｜四会话 G0 来源适配审查 V1

**判决：`G0_PARTIAL_PENDING_REVIEW`。实际取得 `SOURCE_COUNTERFACTUAL_ADMISSIBLE` 的会话为 0/4。GPU 输入前提未满足，维持 `NO_GPU_PROBE_READY / STOP`。**

## 固定来源与范围

科学合同为 `d058d4faf2d93e31976888808a608c4a8fa46714`（tree `fd6085fe75179143a764ed8aa050ef10a37112eb`）的 V2 `REVISED_CONTRACT.md`、`SCIENCE_REVIEW.md` 和 `QUALITY_GATE_SPEC.json`。资产资格为 `8e836c7bb0b0428fe2c04630ef21ddf6b9d3269f`，环境安装为 `e82218cd73240ee4307603daa18390d3af7197d0`，原四条选择为 `d750e4a7d3477f93198f419b7682756ab661c88f`。本轮没有修改 Draft PR #2 的科学合同。

只读使用 109 固定 WildChat 分片和 Qwen tokenizer。分片为 231,061,961 字节，SHA-256 `2023b66a16cf095fcd3686e10259dc089eca95f739fa1c863b07af56029f9f00`；Qwen 修订 `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`。脚本复用原严格过滤及探索池完整 SHA-256 最小四条规则，得到 27,628 候选、22,079 探索、5,549 保留，四条 digest 列表承诺 `a5f4cfb551054561d6353d096143679bb8603c7ab0a2831d5f409ea86feee701`。过滤阶段扫描固定分片的消息字段，但没有选用、输出或审查保留池会话；未增补或替换样本。

## 四条机械结果

| 匿名引用 | 结构及标记 | user₁ / user₂ 原始 token | 首轮模板输入 | 空 assistant₁ 的第二轮模板输入 | 含两次 256 输出与 32 余量的估算 | 当前分类 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| S01 | 通过 | 33 / 4 | 42 | 55 | 599 | `PENDING_HUMAN_REVIEW` |
| S02 | 通过 | 6 / 41 | 15 | 66 | 610 | `PENDING_HUMAN_REVIEW` |
| S03 | 通过 | 2 / 2 | 12 | 24 | 568 | `PENDING_HUMAN_REVIEW` |
| S04 | 通过 | 846 / 8 | 855 | 873 | 1417 | `PENDING_HUMAN_REVIEW` |

四条的角色交替、完整会话消息数、前两条 user 非空以及现有 row/message `redacted/toxic` 标记均满足机械门。首轮输入 42/15/12/855 与原 V1 一致；以原 GPT 历史构造的第二轮诊断 212/85/33/1095 也一致。后者**不是**未来 Qwen 自续历史的长度。第二轮估算以空 assistant 模板加 256、32 余量及新输出 256 计算，均低于 8192；这是无已知必然超限的 CPU 检查，不是实际生成后长度保证。

来源语言字段分别为 Russian、Czech、Chinese、English；S03 两条 user 的语言字段为 Tagalog 与 Chinese。简单的去内容结构信号扫描未标出明确附件/网页/历史指代信号；该规则不覆盖所有语言表达，也无法判断暗含的原 GPT 回答依赖或文本是否缺失。逐条格式与信号类别见 `SESSION_ADMISSION_LEDGER.json`。

## 尚未闭合

四条的原 GPT 特定回答依赖、潜在 PII/敏感内容、单条文本的处理权限，以及缺失附件或纯文本强制条件，均未由合法授权的人审查。WildChat ODC-BY 数据库许可和 `redacted/toxic=false` 不能代替逐条权利与隐私判断。本轮没有把原文、ID 或局部摘录交给 Codex API、云评测器或 Git；也没有把执行者的机械检查当人工判断。原 GPT assistant₁ 只在 109 私有审阅材料内供依赖判定，绝不进入未来 Qwen 输入或质量 gold。

私有审阅材料位于 `/data/c16/aiarch_hybrid_four_session_g0_private_20261111_v1/review_cases.json`，目录权限 0700、文件 0600；仅可由被明确授予该数据处理权限的本地审查者查看。需要人工逐条记录 A/B/C 判据、身份与授权依据。没有已知可合法承担此项审查的人员确认，因此四条均保持 pending。若任何一条明确不适用，应保持固定样本并将本组判为 `G0_NO_GO`；不得临时替换。

## 执行边界

本轮运行 DuckDB 1.4.1、Transformers 5.22.2 与 `Qwen3_5Tokenizer` 的 CPU 脚本；未初始化 CUDA，未加载完整模型、运行 vLLM/Runner、下载或调用 GPU。现阶段不建议进入 30 分钟 GPU 动态资格窗口。
